import os
import re
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import sys

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.qa_model import QAModel
from processors.document_processor import DocumentProcessor

# Load environment variables
load_dotenv()

# Define models
class QuestionRequest(BaseModel):
    text: str
    cdp: Optional[str] = None

class SourceItem(BaseModel):
    url: str
    title: str

class AnswerResponse(BaseModel):
    answer: str
    sources: List[str] = []

# Create FastAPI app
app = FastAPI(title="CDP Support Chatbot API")

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
qa_models = {}
supported_cdps = ["segment", "mparticle", "lytics", "zeotap"]

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
VECTORSTORE_DIR = os.path.join(BASE_DIR, "vectorstores")

# Initialize document processor
document_processor = DocumentProcessor(DATA_DIR, VECTORSTORE_DIR)

# Cross-CDP Comparison Function
def handle_cross_cdp_comparison(question):
    """Handle cross-CDP comparison questions"""
    comparison_details = {
        "audience creation": {
            "summary": "Comparing Audience Creation Approaches:",
            "details": {
                "Segment": "Uses behavioral events and SQL-like syntax in Personas. Focuses on event-based segmentation.",
                "mParticle": "Provides drag-and-drop interface with real-time updates. Emphasizes mobile and app data segmentation.",
                "Lytics": "Utilizes machine learning for predictive audiences. Offers boolean logic and visual audience builder.",
                "Zeotap": "Specializes in third-party data enrichment and lookalike modeling for audience creation."
            }
        },
        "data integration": {
            "summary": "Comparing Data Integration Capabilities:",
            "details": {
                "Segment": "Extensive integration library. Strong focus on routing data between platforms.",
                "mParticle": "Robust mobile SDK. Emphasizes cross-platform identity resolution.",
                "Lytics": "Advanced machine learning for data enrichment and prediction.",
                "Zeotap": "Specializes in identity resolution and third-party data integration."
            }
        }
    }
    
    # Determine comparison type
    comparison_type = next(
        (key for key in comparison_details if key in question.lower()), 
        "general"
    )
    
    if comparison_type == "general":
        # Generic comparison if no specific type detected
        return AnswerResponse(
            answer="CDP Comparison Overview:\n\n" + 
            "\n".join([f"{cdp}: {details}" for cdp, details in comparison_details['data integration']['details'].items()]),
            sources=[]
        )
    
    # Specific comparison
    comparison = comparison_details[comparison_type]
    formatted_comparison = f"{comparison['summary']}\n\n" + \
        "\n".join([f"{cdp}: {detail}" for cdp, detail in comparison['details'].items()])
    
    return AnswerResponse(
        answer=formatted_comparison,
        sources=[]
    )

@app.on_event("startup")
async def startup_event():
    """Load QA models on startup"""
    global qa_models
    
    print(f"Looking for vector stores in: {VECTORSTORE_DIR}")
    # Check if directory exists
    if os.path.exists(VECTORSTORE_DIR):
        print(f"Vector store directory exists: {os.listdir(VECTORSTORE_DIR)}")
    else:
        print(f"Vector store directory does not exist")
    
    for cdp in supported_cdps:
        try:
            print(f"Trying to load vector store for {cdp}...")
            vectorstore = document_processor.load_vectorstore(cdp)
            if vectorstore:
                qa_models[cdp] = QAModel(vectorstore, cdp)
                print(f"Loaded QA model for {cdp}")
            else:
                print(f"No vectorstore found for {cdp}")
        except Exception as e:
            print(f"Error loading QA model for {cdp}: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "CDP Support Chatbot API"}

@app.get("/cdps")
async def get_cdps():
    """Get list of supported CDPs"""
    return {"cdps": supported_cdps}

@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """Advanced question handling for CDP support"""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    # Preprocessing the question
    question = request.text.strip()
    
    # Irrelevant question filter
    irrelevant_keywords = ["movie", "weather", "sports", "food", "restaurant"]
    if any(keyword in question.lower() for keyword in irrelevant_keywords):
        return AnswerResponse(
            answer="I'm a CDP support specialist focused on Customer Data Platforms like Segment, mParticle, Lytics, and Zeotap. Please ask me about CDP-related tasks or comparisons."
        )
    
    # Cross-CDP Comparison Detection
    comparison_keywords = ["compare", "difference", "vs", "versus", "better"]
    cdp_names = ["segment", "mparticle", "lytics", "zeotap"]
    
    cdp_mentions = [cdp for cdp in cdp_names if cdp in question.lower()]
    is_comparison = (any(comp in question.lower() for comp in comparison_keywords) and len(cdp_mentions) > 1)
    
    if is_comparison:
        return handle_cross_cdp_comparison(question)
    
    # Check if user specified a CDP in the dropdown
    if request.cdp and request.cdp != "all" and request.cdp in qa_models:
        # User selected a specific CDP
        model = qa_models[request.cdp]
        result = model.answer_question(question)
        return AnswerResponse(
            answer=result["answer"],
            sources=result["sources"]
        )
    
    # Check if question mentions a specific CDP
    mentioned_cdp = next((cdp for cdp in supported_cdps if cdp in question.lower()), None)
    
    if mentioned_cdp and mentioned_cdp in qa_models:
        model = qa_models[mentioned_cdp]
        result = model.answer_question(question)
        return AnswerResponse(
            answer=result["answer"],
            sources=result["sources"]
        )
    
    # If no specific CDP is mentioned or selected, query all CDPs
    answers = []
    all_sources = []
    
    # We'll query all models but only include relevant responses
    for cdp, model in qa_models.items():
        try:
            result = model.answer_question(question)
            
            # Only include answers that aren't generic "couldn't find" responses
            if "I couldn't find specific information" not in result["answer"]:
                answers.append(f"From {cdp.capitalize()}:\n{result['answer']}")
                all_sources.extend(result["sources"])
        except Exception as e:
            print(f"Error getting answer from {cdp}: {e}")
    
    if not answers:
        return AnswerResponse(
            answer="I'm sorry, I couldn't find specific information about that in any of the CDP documentation. Could you rephrase your question or ask something more specific about Segment, mParticle, Lytics, or Zeotap?"
        )
    
    # Limit the number of responses to show (to avoid overwhelming the user)
    if len(answers) > 2:
        answers = answers[:2]
    
    return AnswerResponse(
        answer="\n\n".join(answers),
        sources=all_sources[:5]  # Limit to 5 sources to keep the response clean
    )