import os
import json
import re
import chromadb
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

class DocumentProcessor:
    def __init__(self, data_dir, vectorstore_dir):
        self.data_dir = data_dir
        self.vectorstore_dir = vectorstore_dir
        
        # Create vectorstore directory if it doesn't exist
        if not os.path.exists(vectorstore_dir):
            os.makedirs(vectorstore_dir)
        
        # Use a free embedding model
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(path=self.vectorstore_dir)
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
    
    def process_cdp_docs(self, cdp_name):
        """Process documents for a specific CDP"""
        cdp_dir = os.path.join(self.data_dir, cdp_name)
        if not os.path.exists(cdp_dir):
            print(f"No data directory found for {cdp_name}")
            return None
            
        print(f"Processing documents for {cdp_name}...")
        
        # Create or get collection
        collection = self.chroma_client.get_or_create_collection(name=cdp_name)
        
        # Load all documents
        document_count = 0
        for filename in os.listdir(cdp_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(cdp_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        doc_data = json.load(f)
                        
                        # Use a smaller chunk size with smaller overlap for more precise retrieval
                        splitter = RecursiveCharacterTextSplitter(
                            chunk_size=500,  # Smaller chunks
                            chunk_overlap=50,
                            length_function=len,
                            separators=["\n\n", "\n", ". ", " ", ""]
                        )
                        
                        # Split document into chunks
                        splits = splitter.split_text(doc_data['content'])
                        
                        # Generate embeddings
                        embeddings = self.embedder.encode(splits).tolist()
                        
                        # Add each chunk to the collection with meaningful metadata
                        for i, (split, embedding) in enumerate(zip(splits, embeddings)):
                            collection.add(
                                documents=[split],
                                embeddings=[embedding],
                                metadatas=[{
                                    'source': doc_data['source'],
                                    'title': doc_data['title'],
                                    'url': doc_data['url'],
                                    'chunk_id': i,
                                    'total_chunks': len(splits),
                                    'doc_type': 'how_to' if any(keyword in split.lower() for keyword in 
                                               ['how to', 'steps', 'guide', 'tutorial', 'instructions']) else 'general'
                                }],
                                ids=[f"{cdp_name}_{document_count}_{i}"]
                            )
                        
                        document_count += 1
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON from {file_path}")
        
        print(f"Processed {document_count} documents for {cdp_name}")
        return collection
    
    def process_all_cdps(self):
        """Process documents for all CDPs"""
        results = {}
        
        for cdp_dir in os.listdir(self.data_dir):
            cdp_path = os.path.join(self.data_dir, cdp_dir)
            if os.path.isdir(cdp_path):
                collection = self.process_cdp_docs(cdp_dir)
                if collection:
                    results[cdp_dir] = collection
        
        return results
    
    def load_vectorstore(self, cdp_name):
        """Load a saved vector store"""
        try:
            return self.chroma_client.get_collection(name=cdp_name)
        except Exception as e:
            print(f"Error loading collection for {cdp_name}: {e}")
            return None