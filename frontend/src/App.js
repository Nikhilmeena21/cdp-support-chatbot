import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import ChatMessage from './components/ChatMessage';
import WelcomeMessage from './components/WelcomeMessage';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [selectedCDP, setSelectedCDP] = useState('all');
  const [isLoading, setIsLoading] = useState(false);
  const messageEndRef = useRef(null);

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messageEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (input.trim() === '' || isLoading) return;
    
    // Add user message
    const userMessage = {
      text: input,
      sender: 'user',
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    
    try {
      // Send request to API
      const response = await fetch('/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: input,
          cdp: selectedCDP === 'all' ? null : selectedCDP
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to get answer');
      }
      
      const data = await response.json();
      
      // Add bot message
      setMessages(prev => [...prev, {
        text: data.answer,
        sender: 'bot',
        sources: data.sources,
        timestamp: new Date().toISOString()
      }]);
    } catch (error) {
      console.error('Error getting answer:', error);
      
      // Add error message
      setMessages(prev => [...prev, {
        text: "Sorry, I encountered an error processing your question. Please try again.",
        sender: 'bot',
        error: true,
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>CDP Support Chatbot</h1>
        <div className="cdp-selector">
          <label htmlFor="cdp-select">Platform:</label>
          <select 
            id="cdp-select" 
            value={selectedCDP} 
            onChange={(e) => setSelectedCDP(e.target.value)}
          >
            <option value="all">All CDPs</option>
            <option value="segment">Segment</option>
            <option value="mparticle">mParticle</option>
            <option value="lytics">Lytics</option>
            <option value="zeotap">Zeotap</option>
          </select>
        </div>
      </header>
      
      <div className="message-container">
        {messages.length === 0 ? (
          <WelcomeMessage />
        ) : (
          messages.map((msg, index) => (
            <ChatMessage key={index} message={msg} />
          ))
        )}
        
        {isLoading && (
          <div className="message bot loading">
            <div className="message-content">
              <div className="loading-indicator">
                <div className="dot"></div>
                <div className="dot"></div>
                <div className="dot"></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messageEndRef} />
      </div>
      
      <div className="input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask a question about using CDPs..."
          disabled={isLoading}
        />
        <button onClick={handleSend} disabled={isLoading || !input.trim()}>
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M22 2L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
      </div>
    </div>
  );
}

export default App;