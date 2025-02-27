# CDP Support Chatbot

A sophisticated chatbot that answers "how-to" questions related to Customer Data Platforms (CDPs): Segment, mParticle, Lytics, and Zeotap.

![CDP Support Chatbot Screenshot](https://i.imgur.com/YOUR_SCREENSHOT_ID.png)

## Features

* **Answer "How-to" Questions** : Provides detailed, step-by-step instructions for performing tasks within each CDP
* **Documentation-based Responses** : Extracts and processes information directly from official CDP documentation
* **Multiple CDP Support** : Covers four major CDPs - Segment, mParticle, Lytics, and Zeotap
* **Cross-CDP Comparisons** : Compare functionality across different platforms (e.g., "How does Segment's audience creation compare to Lytics?")
* **Intelligent Response Formatting** : Presents answers in clear, structured formats with proper organization
* **Source Attribution** : Includes references to source documentation

## Technical Architecture

### Overview

The CDP Support Chatbot uses a hybrid architecture that combines:

1. **Vector Search** : For efficient retrieval of relevant documentation chunks
2. **LLM Integration** : For high-quality response generation from retrieved context

This approach provides both the accuracy of retrieving real documentation and the natural language capabilities of modern LLMs.

### Data Flow

1. User submits a question through the frontend interface
2. Backend processes the question and determines intent
3. Vector search finds relevant documentation chunks
4. Retrieved context is sent to the LLM with the original question
5. LLM generates a coherent, structured response
6. Response is formatted and displayed to the user

### Tech Stack

#### Backend

* **FastAPI** : High-performance API framework
* **ChromaDB** : Vector database for document storage and retrieval
* **Sentence Transformers** : For creating text embeddings
* **Groq API** : LLM for generating high-quality responses
* **BeautifulSoup** : For documentation scraping
* **Python 3.x** : Core programming language

#### Frontend

* **React** : UI framework
* **CSS** : Styling with custom components

## Setup and Installation

### Prerequisites

* Python 3.9+ and pip
* Node.js and npm
* Groq API key (sign up at [console.groq.com](https://console.groq.com/))

### Backend Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/cdp-support-chatbot.git
cd cdp-support-chatbot
```

2. Set up Python virtual environment:

```bash
cd backend
python -m venv venv
venv\Scripts\activate.bat  # On Windows
source venv/bin/activate  # On Unix/MacOS
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the backend directory:

```
GROQ_API_KEY=your_groq_api_key_here
```

5. Run the documentation scraper and processor (optional, sample data included):

```bash
python run_scrapers.py
```

6. Start the backend server:

```bash
python run_api.py
```

### Frontend Setup

1. Navigate to the frontend directory:

```bash
cd ../frontend
```

2. Install dependencies:

```bash
npm install
```

3. Start the development server:

```bash
npm start
```

4. Open your browser to [http://localhost:3000](http://localhost:3000/)

## Usage

1. Select a specific CDP from the dropdown or keep "All CDPs" selected
2. Type your question in the input field
3. Review the response, which includes:
   * Structured answer
   * Steps (if applicable)
   * Code examples (if applicable)
   * Source references

### Example Questions

* "How do I set up a new source in Segment?"
* "How can I create a user profile in mParticle?"
* "How do I build an audience segment in Lytics?"
* "How can I integrate my data with Zeotap?"
* "How does Segment's audience creation process compare to Lytics?"

## Implementation Details

### Vector Database Architecture

The system uses a sparse vector representation of documentation chunks:

1. **Document Processing** :

* Documentation is split into small chunks (~500 tokens)
* Each chunk is embedded using Sentence Transformers
* Embeddings and metadata are stored in ChromaDB

1. **Retrieval** :

* User questions are embedded using the same model
* Vector similarity search finds the most relevant chunks
* Multiple chunks are combined to provide comprehensive context

### Response Generation

The system uses a two-stage approach:

1. **Retrieval** : Vector search finds relevant documentation chunks
2. **Generation** : Groq LLM generates coherent, well-structured responses

This "Retrieval-Augmented Generation" approach ensures responses are:

* Grounded in actual documentation
* Well-formatted and easy to understand
* Directly relevant to the user's question

### Cross-CDP Comparison

A specialized module handles comparison questions by:

1. Detecting comparison intent through keyword analysis
2. Identifying which CDPs are being compared
3. Retrieving comparison data from structured knowledge base
4. Formatting responses to highlight key differences

## Future Enhancements

* User feedback mechanism for response quality
* Expanded documentation coverage
* Multi-language support
* Voice interface integration
* Interactive code examples

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

* [Groq](https://groq.com/) for their powerful LLM API
* [ChromaDB](https://www.trychroma.com/) for the vector database
* Documentation from Segment, mParticle, Lytics, and Zeotap
