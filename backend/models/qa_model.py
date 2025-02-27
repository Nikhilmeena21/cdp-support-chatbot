from sentence_transformers import SentenceTransformer
import numpy as np
import re
import groq
import os
from dotenv import load_dotenv

class QAModel:
    def __init__(self, collection, cdp_name):
        self.collection = collection
        self.cdp_name = cdp_name
        
        # Use the same embedding model
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load Groq API key from environment variables
        load_dotenv()
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if self.groq_api_key:
            self.groq_client = groq.Client(api_key=self.groq_api_key)
        else:
            print("Warning: GROQ_API_KEY not found in environment variables")
            self.groq_client = None
    
    def answer_question(self, question):
        """Answer a question using the vector store and Groq"""
        # Clean and process the question
        clean_question = question.strip()
        
        # Generate embedding for the question
        question_embedding = self.embedder.encode(clean_question).tolist()
        
        # Perform similarity search
        results = self.collection.query(
            query_embeddings=[question_embedding],
            n_results=5
        )
        
        # Get documents
        context_docs = results['documents'][0] if results['documents'] else []
        
        # Combine context documents
        if context_docs:
            context = "\n\n".join(context_docs)
        else:
            context = ""
        
        # Generate answer
        if self.groq_client:
            answer = self.generate_groq_answer(clean_question, context)
        else:
            answer = self.generate_simple_answer(clean_question, context)
        
        # Extract sources
        sources = list(set([
            metadata.get('url', '') 
            for metadata in (results['metadatas'][0] if results['metadatas'] else [])
            if metadata and 'url' in metadata
        ]))
        
        return {
            "answer": answer,
            "sources": sources
        }
    
    def generate_groq_answer(self, question, context):
        """Generate an answer using Groq's LLM"""
        if not context:
            return f"I couldn't find specific information about {question} in the {self.cdp_name} documentation."
        
        # Create a prompt for Groq
        prompt = f"""You are a helpful CDP (Customer Data Platform) support specialist for {self.cdp_name}.
Answer the following question based on the provided context from the {self.cdp_name} documentation.
Your answer should be clear, concise, and directly address the question.
Format any steps or instructions in a numbered list.
If the information is not in the context, say you don't have that specific information.

Context:
{context}

Question:
{question}

Answer:"""
        
        try:
            # Get completion from Groq
            completion = self.groq_client.chat.completions.create(
                model="llama3-8b-8192",  # You can use "mixtral-8x7b-32768" for more complex queries
                messages=[
                    {"role": "system", "content": f"You are a helpful CDP support specialist for {self.cdp_name}."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for more focused answers
                max_tokens=800
            )
            
            # Extract the response
            answer = completion.choices[0].message.content
            return answer
        
        except Exception as e:
            print(f"Error generating response with Groq: {e}")
            # Fall back to simple answer
            return self.generate_simple_answer(question, context)
    
    def generate_simple_answer(self, question, context):
        """Generate a simple answer (fallback if Groq is unavailable)"""
        if not context:
            return f"I couldn't find specific information about {question} in the {self.cdp_name} documentation."
        
        # Identify if this is a "how-to" question
        how_to_keywords = ["how", "steps", "guide", "process", "way to", "setup", "configure", "implement"]
        is_how_to = any(keyword in question.lower() for keyword in how_to_keywords)
        
        if is_how_to:
            # Format as a step-by-step guide
            intro = f"Here's how to {question.lower().replace('how do i ', '').replace('how to ', '').replace('?', '')} in {self.cdp_name}:"
            return f"{intro}\n\n{context}"
        else:
            # Format as a general information response
            return f"Based on the {self.cdp_name} documentation, here's information about {question.replace('?', '')}:\n\n{context}"