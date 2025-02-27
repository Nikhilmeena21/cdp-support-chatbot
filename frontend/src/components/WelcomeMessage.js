import React from 'react';
import './WelcomeMessage.css';

function WelcomeMessage() {
  return (
    <div className="welcome-message">
      <h2>Welcome to the CDP Support Chatbot!</h2>
      <p>
        I'm here to help you with information about Customer Data Platforms (CDPs)
        including Segment, mParticle, Lytics, and Zeotap.
      </p>
      <div className="example-questions">
        <p>You can ask questions like:</p>
        <ul>
          <li>"How do I set up a new source in Segment?"</li>
          <li>"How can I create a user profile in mParticle?"</li>
          <li>"How do I build an audience segment in Lytics?"</li>
          <li>"How can I integrate my data with Zeotap?"</li>
          <li>"What's the difference between Segment and mParticle?"</li>
        </ul>
      </div>
      <p className="tip">
        <strong>Tip:</strong> You can select a specific CDP from the dropdown in the header
        or ask about all platforms at once.
      </p>
    </div>
  );
}

export default WelcomeMessage;