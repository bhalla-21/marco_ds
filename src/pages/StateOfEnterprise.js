import React, { useState } from "react";
import TopNav from "../components/TopNav";
import FAQEntityDropdown from "../components/FAQEntityDropdown";
import ReactMarkdown from 'react-markdown';

const API_URL = "https://marco-ds-1.onrender.com:8000";

const faqs = [
  {
    template: [
      "What are the top Net Revenue drivers in ",
      { key: "country", options: ["France", "United Kingdom", "Germany", "United States"] },
      " for Oreo in QTD?"
    ]
  },
  {
    template: [
      "Which ",
      { key: "subBrand", options: ["Oreo", "Chips Ahoy!", "Milka", "Ritz"] },
      " sub-brand is driving growth in QTD?"
    ]
  },
  {
    template: [
      "What is the Oreo net revenue trend in ",
      { key: "timePeriod", options: ["QTD", "YTD", "MTD", "Month"] },
      "?"
    ]
  }
];

function StateOfEnterprise() {
  const [chatInput, setChatInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [llmResponse, setLlmResponse] = useState(null);

  const handleSendRequest = async () => {
    if (!chatInput.trim()) return;

    setIsLoading(true);
    setError(null);
    setLlmResponse(null); // Clear previous response immediately

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: { text: chatInput, files: [] },
          history: [],
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.error) {
        setError(data.error);
      } else {
        setLlmResponse(data);
      }

    } catch (e) {
      setError(e.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="main-bg">
      <TopNav />
      <div className="header-section" style={{ textAlign: "center", maxWidth: "1200px", margin: "0 auto" }}>
        <h1 className="enterprise-title">State of the Enterprise</h1>
        <div
          className="faq-flex-row"
          style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "flex-start",
            gap: "28px",
            marginBottom: "36px"
          }}
        >
          {faqs.map((faq, idx) => (
            <div className="faq-card" key={idx}>
              <FAQEntityDropdown template={faq.template} onChange={setChatInput} />
            </div>
          ))}
        </div>
        <div
          className="chat-bar"
          style={{ marginTop: 20, display: "flex", alignItems: "center", justifyContent: "center", marginBottom: "40px" }}
        >
          <input
            type="text"
            className="chat-bar-input"
            value={chatInput}
            onChange={e => setChatInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendRequest()}
            placeholder="Your question will appear here..."
          />
          <button className="chat-bar-send" onClick={handleSendRequest} disabled={isLoading}>
            {isLoading ? '...' : '↩'}
          </button>
        </div>

        {/* --- THIS IS THE KEY CHANGE --- */}
        {/* We only render the response container IF there is a response, loading state, or error */}
        {(isLoading || error || llmResponse) && (
          <div className="response-container" style={{ textAlign: 'left', background: '#fff', padding: '30px', borderRadius: '15px', boxShadow: '0 4px 20px rgba(0,0,0,0.05)' }}>
            {isLoading && <p>Generating insights, please wait...</p>}
            {error && <p style={{ color: 'red' }}>Error: {error}</p>}
            
            {llmResponse && (
              <div>
                <div className="markdown-content">
                  <ReactMarkdown>{llmResponse.text_answer}</ReactMarkdown>
                </div>
                
                {llmResponse.charts && llmResponse.charts.length > 0 && (
                  <div className="charts-container" style={{ marginTop: '30px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    {llmResponse.charts.map((chartSrc, index) => (
                      <img 
                        key={index} 
                        src={chartSrc} 
                        alt={`Generated Chart ${index + 1}`} 
                        style={{ maxWidth: '100%', border: '1px solid #eee', borderRadius: '10px' }}
                      />
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default StateOfEnterprise;
