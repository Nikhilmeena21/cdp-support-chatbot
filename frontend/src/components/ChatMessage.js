import React from 'react';
import './ChatMessage.css';

function ChatMessage({ message }) {
  const { text, sender, sources, error } = message;
  
  // Process the text to properly format numbered lists and sections
  const processText = (text) => {
    if (!text) return '';
    
    // Split by CDP sections if they exist
    const sections = text.split(/From [A-Za-z]+:/);
    
    if (sections.length > 1) {
      // There are multiple CDP sections
      let result = '';
      const cdpNames = text.match(/From [A-Za-z]+:/g) || [];
      
      for (let i = 0; i < cdpNames.length; i++) {
        const cdpName = cdpNames[i];
        const sectionContent = sections[i+1] || '';
        
        result += `<div class="cdp-section">
          <h4>${cdpName}</h4>
          ${formatSteps(sectionContent)}
        </div>`;
      }
      
      return result;
    } else {
      // Single content block
      return formatSteps(text);
    }
  };
  
  // Format steps and lists
  const formatSteps = (content) => {
    if (!content) return '';
    
    // Format numbered steps
    content = content.replace(/(\d+)\.\s+(.*?)(?=\n\d+\.|\n\n|$)/gs, '<li class="step">$1. $2</li>');
    
    // Format bullet points
    content = content.replace(/(?:^|\n)[-•]\s+(.*?)(?=\n[-•]|\n\n|$)/gs, '<li>$1</li>');
    
    // Wrap lists
    content = content.replace(/<li class="step">(.*?)<\/li>(\s*<li class="step">.*?<\/li>)+/gs, '<ol class="steps">$&</ol>');
    content = content.replace(/<li>(.*?)<\/li>(\s*<li>.*?<\/li>)+/gs, '<ul>$&</ul>');
    
    // Format paragraphs
    content = content.replace(/(?:^|\n\n)([^<\n].*?)(?=\n\n|$)/gs, '<p>$1</p>');
    
    return content;
  };
  
  return (
    <div className={`message ${sender} ${error ? 'error' : ''}`}>
      <div className="message-content">
        <div 
          dangerouslySetInnerHTML={{ 
            __html: processText(text) 
          }}
        />
        
        {sources && sources.length > 0 && (
          <div className="sources">
            <p className="sources-title">Sources:</p>
            <ul>
              {sources.map((source, index) => (
                <li key={index}>
                  <a 
                    href={source} 
                    target="_blank" 
                    rel="noopener noreferrer"
                  >
                    {source}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

export default ChatMessage;