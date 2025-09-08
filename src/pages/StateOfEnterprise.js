import React, { useState } from "react";
import TopNav from "../components/TopNav";
import FAQEntityDropdown from "../components/FAQEntityDropdown";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm'; // NEW IMPORT - Install with: npm install remark-gfm

const API_URL = "https://marco-ds-1.onrender.com";

// CORRECTED FAQS WITH PROPER TEMPLATE STRUCTURE
const faqs = [
  {
    template: [
      "What are the top ",
      { key: "metric", options: ["Net Revenue", "Gross Profit", "Operating Income", "Volume"], default: "Net Revenue" },
      " drivers in ",
      { key: "country", options: ["France", "United Kingdom", "Germany", "United States"], default: "France" },
      " for Oreo in ",
      { key: "timePeriod", options: ["MTD", "QTD", "YTD", "Month"], default: "QTD" },
      "?"
    ]
  },
  {
    template: [
      "Which ",
      { key: "subBrand", options: ["Oreo", "Chips Ahoy!", "Milka", "Ritz"], default: "Oreo" },
      " sub-brand is driving ",
      { key: "metric", options: ["Net Revenue", "Gross Profit", "Operating Income", "Volume"], default: "Net Revenue" },
      " growth in ",
      { key: "timePeriod", options: ["MTD", "QTD", "YTD", "Month"], default: "QTD" },
      "?"
    ]
  },
  {
    template: [
      "What is the Oreo ",
      { key: "metric", options: ["Net Revenue", "Gross Profit", "Operating Income", "Volume"], default: "Net Revenue" },
      " trend in ",
      { key: "timePeriod", options: ["MTD", "QTD", "YTD", "Month"], default: "QTD" },
      "?"
    ]
  },
  {
    template: [
      "Summarize MDLZ performance in ",
      { key: "region", options: ["HQ", "LA", "AMEA", "EU", "All Regions"], default: "HQ" },
      " for ",
      { key: "metric", options: ["Net Revenue", "Gross Profit", "Operating Income", "Volume", "All Metrics"], default: "Net Revenue" },
      " over ",
      { key: "timePeriod", options: ["MTD", "QTD", "YTD", "Month"], default: "MTD" },
      "."
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
      
      // ADD THIS DEBUG LOGGING - ONLY ADDITION
      console.log('Backend response:', data);
      console.log('Charts data:', data.charts);
      if (data.charts) {
        data.charts.forEach((chart, i) => {
          console.log(`Chart ${i}:`, typeof chart, chart?.substring(0, 50) + '...');
        });
      }
      
      if (data.error) {
        setError(data.error);
      } else {
        // PROCESS CHARTS TO ENSURE THEY ARE BASE64 STRINGS - ONLY ADDITION
        const processedData = { ...data };
        if (processedData.charts && processedData.charts.length > 0) {
          processedData.charts = processedData.charts.filter(chart => {
            return typeof chart === 'string' && chart.startsWith('data:image');
          });
        }
        setLlmResponse(processedData);
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
      <div className="header-section" style={{ textAlign: "center", maxWidth: "1400px", margin: "0 auto" }}>
        <h1 className="enterprise-title">State of the Enterprise</h1>
        
        {/* FAQ GRID WITH IMPROVED STYLING */}
        <div
          className="faq-grid"
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(2, 1fr)",
            gap: "20px",
            marginBottom: "36px",
            maxWidth: "1200px",
            margin: "0 auto 36px auto"
          }}
        >
          {faqs.map((faq, idx) => (
            <div 
              className="faq-card" 
              key={idx}
              style={{
                padding: "20px",
                backgroundColor: "#f8f9fa",
                borderRadius: "12px",
                border: "1px solid #e9ecef",
                minHeight: "120px",
                display: "flex",
                alignItems: "center"
              }}
            >
              <FAQEntityDropdown 
                template={faq.template} 
                onChange={setChatInput}
                key={`faq-${idx}`} // Force re-render when needed
              />
            </div>
          ))}
        </div>

        <div
          className="chat-bar"
          style={{ 
            marginTop: 20, 
            display: "flex", 
            alignItems: "center", 
            justifyContent: "center", 
            marginBottom: "40px",
            maxWidth: "800px",
            margin: "20px auto 40px auto"
          }}
        >
          <input
            type="text"
            className="chat-bar-input"
            value={chatInput}
            onChange={e => setChatInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendRequest()}
            placeholder="Your question will appear here..."
            style={{ 
              minWidth: "600px", 
              padding: "12px 16px",
              fontSize: "16px",
              borderRadius: "8px",
              border: "1px solid #ccc"
            }}
          />
          <button 
            className="chat-bar-send" 
            onClick={handleSendRequest} 
            disabled={isLoading}
            style={{
              marginLeft: "10px",
              padding: "12px 16px",
              fontSize: "16px",
              borderRadius: "8px",
              backgroundColor: "#6f42c1",
              color: "white",
              border: "none",
              cursor: isLoading ? "not-allowed" : "pointer"
            }}
          >
            {isLoading ? '...' : '↩'}
          </button>
        </div>

        {/* RESPONSE CONTAINER - UNCHANGED */}
        {(isLoading || error || llmResponse) && (
          <div className="response-container" style={{ textAlign: 'left', background: '#fff', padding: '30px', borderRadius: '15px', boxShadow: '0 4px 20px rgba(0,0,0,0.05)' }}>
            {isLoading && <p>Generating insights, please wait...</p>}
            {error && <p style={{ color: 'red' }}>Error: {error}</p>}
            
            {llmResponse && (
              <div>
                <div className="markdown-content">
                  {/* ENHANCED REACTMARKDOWN WITH TABLE SUPPORT - KEY CHANGE */}
                  <ReactMarkdown 
                    remarkPlugins={[remarkGfm]}
                    components={{
                      table: ({node, ...props}) => (
                        <table style={{
                          borderCollapse: 'collapse', 
                          width: '100%', 
                          margin: '20px 0',
                          fontSize: '14px',
                          border: '1px solid #ddd'
                        }} {...props} />
                      ),
                      thead: ({node, ...props}) => (
                        <thead style={{backgroundColor: '#f8f9fa'}} {...props} />
                      ),
                      th: ({node, ...props}) => (
                        <th style={{
                          border: '1px solid #ddd', 
                          padding: '12px 8px', 
                          backgroundColor: '#f8f9fa', 
                          fontWeight: '600',
                          color: '#495057',
                          textAlign: 'left'
                        }} {...props} />
                      ),
                      td: ({node, ...props}) => (
                        <td style={{
                          border: '1px solid #ddd', 
                          padding: '12px 8px',
                          textAlign: 'left'
                        }} {...props} />
                      ),
                      tr: ({node, ...props}) => (
                        <tr style={{
                          ':nth-child(even)': {backgroundColor: '#f8f9fa'},
                          ':hover': {backgroundColor: '#e9ecef'}
                        }} {...props} />
                      )
                    }}
                  >
                    {llmResponse.text_answer}
                  </ReactMarkdown>
                </div>
                
                {/* ENHANCED CHART RENDERING WITH DEBUG INFO - ONLY ADDITION */}
                {llmResponse.charts && llmResponse.charts.length > 0 ? (
                  <div className="charts-container" style={{ marginTop: '30px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <h3>Charts ({llmResponse.charts.length})</h3>
                    {llmResponse.charts.map((chartSrc, index) => (
                      <div key={index} style={{ border: '1px solid #eee', borderRadius: '10px', padding: '10px' }}>
                        <img 
                          src={chartSrc} 
                          alt={`Generated Chart ${index + 1}`} 
                          style={{ maxWidth: '100%', display: 'block' }}
                          onError={(e) => {
                            console.error(`Chart ${index} failed to load:`, chartSrc.substring(0, 100));
                            e.target.style.display = 'none';
                          }}
                          onLoad={() => console.log(`Chart ${index} loaded successfully`)}
                        />
                      </div>
                    ))}
                  </div>
                ) : (
                  <div style={{ marginTop: '30px', padding: '20px', background: '#f5f5f5', borderRadius: '10px' }}>
                    <p>No charts generated for this query.</p>
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
