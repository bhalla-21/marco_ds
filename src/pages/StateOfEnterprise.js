import React, { useState } from "react";
import TopNav from "../components/TopNav";
import FAQEntityDropdown from "../components/FAQEntityDropdown";
import SectionCard from "../components/SectionCard";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const API_URL = "https://marco-ds-1.onrender.com";
// UPDATED FAQS WITH BRAND DROPDOWNS AND NEW TEMPLATES
const faqs = [
  {
    template: [
      "What are the top ",
      { key: "metric", options: ["Net Revenue", "Gross Profit", "Operating Income", "Volume"], default: "Net Revenue" },
      " drivers in ",
      { key: "country", options: ["France", "United Kingdom", "Germany", "United States"], default: "France" },
      " for ",
      { key: "brand", options: ["Oreo", "Chips Ahoy!", "Milka", "Ritz"], default: "Oreo" },
      " in ",
      { key: "timePeriod", options: ["MTD", "QTD", "YTD", "Month"], default: "QTD" },
      "?"
    ]
  },
  {
    template: [
      "Which ",
      { key: "brand", options: ["Oreo", "Chips Ahoy!", "Milka", "Ritz"], default: "Oreo" },
      " sub-brand is driving ",
      { key: "metric", options: ["Net Revenue", "Gross Profit", "Operating Income", "Volume"], default: "Net Revenue" },
      " growth in ",
      { key: "timePeriod", options: ["MTD", "QTD", "YTD", "Month"], default: "QTD" },
      "?"
    ]
  },
  {
    template: [
      "What is the ",
      { key: "brand", options: ["Oreo", "Chips Ahoy!", "Milka", "Ritz"], default: "Oreo" },
      " ",
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
  },
  {
    template: [
      "Which ",
      { key: "brand", options: ["Oreo", "Chips Ahoy!", "Milka", "Ritz", "brands"], default: "brands" },
      " are driving growth in ",
      { key: "region", options: ["HQ", "LA", "AMEA", "EU", "All Regions"], default: "EU" },
      " region?"
    ]
  },
  {
    template: [
      "Analyze performance trends for ",
      { key: "brand", options: ["Oreo", "Chips Ahoy!", "Milka", "Ritz", "key brands"], default: "key brands" },
      " in the ",
      { key: "category", options: ["Chocolate", "Biscuits", "Cakes and Pastries", "Beverages", "Candy"], default: "Chocolate" },
      " category"
    ]
  },
  {
    template: [
      "Compare Q1 vs Q2 performance for ",
      { key: "brand", options: ["Oreo", "Chips Ahoy!", "Milka", "Ritz", "all brands"], default: "all brands" },
      " across ",
      { key: "region", options: ["HQ", "LA", "AMEA", "EU", "All Regions"], default: "All Regions" },
      " regions"
    ]
  },
  {
    template: [
      "Show me benchmark analysis for ",
      { key: "brand", options: ["Oreo", "Chips Ahoy!", "Milka", "Ritz", "Key Brands"], default: "Key Brands" }
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
    setLlmResponse(null);

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
      
      {/* HOMEPAGE SECTION - TOP PART */}
      <div className="intro-section" style={{ 
        textAlign: "center", 
        maxWidth: "1200px", 
        margin: "0 auto", 
        padding: "40px 20px 60px 20px" 
      }}>
        {/* MARCO-DEEPSEEK Header */}
        <div style={{ marginBottom: "30px" }}>
          <h1 className="marco-header" style={{
            fontSize: "2.8rem",
            fontWeight: "700",
            color: "#6f42c1",
            margin: "20px 0 15px 0"
          }}>
            MARCO<span className="gpt-accent" style={{ color: "#9a6fd6" }}>-DEEPSEEK</span>
            <span className="sparkle-icon" style={{ marginLeft: "8px" }}>✨</span>
          </h1>
          
          {/* Fixed "Powered by ARISE" positioning */}
          <div className="powered-by" style={{ 
            fontSize: "16px", 
            color: "#666", 
            marginBottom: "30px",
            textAlign: "left"
          }}>
            <span>Powered by <b style={{ color: "#6f42c1" }}>ARISE</b></span>
          </div>
        </div>

        {/* Introduction Text */}
        <p className="intro-text" style={{
          fontSize: "18px",
          lineHeight: "1.6",
          color: "#444",
          maxWidth: "800px",
          margin: "0 auto 50px auto"
        }}>
          I'm a GenAI knowledge tool to help you get deeper insights faster. I'm trained to answer What, Why and some diagnostic questions on Nielsen consumption and panel data and unstructured data sources.
        </p>

        {/* Skills Section */}
        <div className="skills-section">
          <p className="skills-title" style={{
            fontSize: "20px",
            fontWeight: "600",
            color: "#333",
            marginBottom: "30px"
          }}>
            Skills:<br />
            <span style={{ fontSize: "16px", fontWeight: "400", color: "#666" }}>
              Below are the skills I am trained on:
            </span>
          </p>
          <div className="card-row" style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
            gap: "20px",
            marginBottom: "40px"
          }}>
            <SectionCard 
              title="State of the Enterprise" 
              description="What are the Net Revenue drivers for Oreo in QTD?" 
            />
            <SectionCard 
              title="Customer" 
              description="What were the top selling products at Publix in January of 2025?" 
              disabled 
            />
            <SectionCard 
              title="Deep Research" 
              description="Please provide an overview of buyer preferences for the Cracker Category for Q1 of 2025." 
              comingSoon 
            />
          </div>
        </div>
      </div>

      {/* ENTERPRISE SECTION - BOTTOM PART */}
      <div className="enterprise-section" style={{
        borderTop: "2px solid #e9ecef",
        paddingTop: "60px",
        paddingBottom: "60px",
        textAlign: "center",
        maxWidth: "1400px",
        margin: "0 auto",
        padding: "60px 20px"
      }}>
        
        {/* Added FAQ Header */}
        <h2 style={{
          fontSize: "2.2rem",
          fontWeight: "600",
          color: "#6f42c1",
          marginBottom: "50px"
        }}>
          Frequently Asked Questions
        </h2>
        
        {/* EXPANDED FAQ GRID - Now with 8 FAQs in 3-column layout */}
        <div
          className="faq-grid"
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(350px, 1fr))",
            gap: "25px",
            marginBottom: "50px",
            maxWidth: "1300px",
            margin: "0 auto 50px auto",
            zIndex: 10,
            position: "relative"
          }}
        >
          {faqs.map((faq, idx) => (
            <div 
              className="faq-card" 
              key={idx}
              style={{
                padding: "25px",
                backgroundColor: "#f8f9fa",
                borderRadius: "15px",
                border: "1px solid #e9ecef",
                minHeight: "140px",
                display: "flex",
                alignItems: "center",
                boxShadow: "0 4px 12px rgba(111, 66, 193, 0.1)",
                transition: "transform 0.2s ease, box-shadow 0.2s ease",
                position: "relative",
                zIndex: 20
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = "translateY(-2px)";
                e.currentTarget.style.boxShadow = "0 6px 20px rgba(111, 66, 193, 0.15)";
                e.currentTarget.style.zIndex = "30";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = "translateY(0)";
                e.currentTarget.style.boxShadow = "0 4px 12px rgba(111, 66, 193, 0.1)";
                e.currentTarget.style.zIndex = "20";
              }}
            >
              <FAQEntityDropdown 
                template={faq.template} 
                onChange={setChatInput}
                key={`faq-${idx}`}
              />
            </div>
          ))}
        </div>

        {/* Chat Bar */}
        <div
          className="chat-bar"
          style={{ 
            display: "flex", 
            alignItems: "center",
            justifyContent: "center", 
            marginBottom: "50px",
            gap: "15px",
            flexWrap: "wrap",
            maxWidth: "700px",
            margin: "0 auto 50px auto"
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
              flex: "1 1 auto",
              minWidth: "300px",
              maxWidth: "500px",
              padding: "16px 20px",
              fontSize: "16px",
              borderRadius: "12px",
              border: "2px solid #6f42c1",
              outline: "none",
              boxShadow: "0 4px 12px rgba(111, 66, 193, 0.1)",
              boxSizing: "border-box"
            }}
          />
          <button 
            className="chat-bar-send" 
            onClick={handleSendRequest} 
            disabled={isLoading || !chatInput.trim()}
            style={{
              flex: "0 0 auto",
              padding: "16px 20px",
              fontSize: "16px",
              borderRadius: "12px",
              backgroundColor: (isLoading || !chatInput.trim()) ? "#ccc" : "#6f42c1",
              color: "white",
              border: "none",
              cursor: (isLoading || !chatInput.trim()) ? "not-allowed" : "pointer",
              boxShadow: "0 4px 12px rgba(111, 66, 193, 0.2)",
              transition: "all 0.2s ease",
              fontWeight: "600",
              minWidth: "120px",
              textAlign: "center",
              whiteSpace: "nowrap",
              overflow: "hidden"
            }}
            onMouseEnter={(e) => {
              if (!isLoading && chatInput.trim()) {
                e.target.style.backgroundColor = "#5a3698";
                e.target.style.transform = "translateY(-1px)";
              }
            }}
            onMouseLeave={(e) => {
              if (!isLoading && chatInput.trim()) {
                e.target.style.backgroundColor = "#6f42c1";
                e.target.style.transform = "translateY(0)";
              }
            }}
          >
            {isLoading ? 'Processing...' : '↩'}
          </button>
        </div>

        {/* RESPONSE CONTAINER */}
        {(isLoading || error || llmResponse) && (
          <div className="response-container" style={{ 
            textAlign: 'left', 
            background: '#fff', 
            padding: '40px', 
            borderRadius: '20px', 
            boxShadow: '0 8px 30px rgba(111, 66, 193, 0.15)',
            maxWidth: '1000px',
            margin: '0 auto'
          }}>
            {isLoading && (
              <div style={{ textAlign: 'center', padding: '40px' }}>
                <div style={{ 
                  fontSize: '18px', 
                  color: '#6f42c1',
                  marginBottom: '10px'
                }}>
                  Generating insights, please wait...
                </div>
              </div>
            )}
            
            {error && (
              <p style={{ 
                color: '#dc3545', 
                textAlign: 'center',
                fontSize: '16px',
                padding: '20px'
              }}>
                Error: {error}
              </p>
            )}
            
            {llmResponse && (
              <div>
                <div className="markdown-content" style={{
                  lineHeight: '1.6',
                  fontSize: '16px',
                  color: '#333'
                }}>
                  <ReactMarkdown 
                    remarkPlugins={[remarkGfm]}
                    components={{
                      table: ({node, ...props}) => (
                        <table style={{
                          borderCollapse: 'collapse', 
                          width: '100%', 
                          margin: '25px 0',
                          fontSize: '14px',
                          border: '1px solid #ddd',
                          borderRadius: '8px',
                          overflow: 'hidden'
                        }} {...props} />
                      ),
                      thead: ({node, ...props}) => (
                        <thead style={{backgroundColor: '#6f42c1', color: 'white'}} {...props} />
                      ),
                      th: ({node, ...props}) => (
                        <th style={{
                          border: '1px solid #ddd', 
                          padding: '15px 12px', 
                          fontWeight: '600',
                          textAlign: 'left'
                        }} {...props} />
                      ),
                      td: ({node, ...props}) => (
                        <td style={{
                          border: '1px solid #ddd', 
                          padding: '12px',
                          textAlign: 'left'
                        }} {...props} />
                      ),
                      h2: ({node, ...props}) => (
                        <h2 style={{color: '#6f42c1', marginTop: '30px'}} {...props} />
                      ),
                      h3: ({node, ...props}) => (
                        <h3 style={{color: '#6f42c1', marginTop: '25px'}} {...props} />
                      )
                    }}
                  >
                    {llmResponse.text_answer}
                  </ReactMarkdown>
                </div>
                
                {/* CHART CONTAINER - RESPONSIVE GRID LAYOUT */}
                {llmResponse.charts && llmResponse.charts.length > 0 && (
                  <div className="charts-container" style={{ marginTop: '40px' }}>
                    <h3 style={{ 
                      marginBottom: '25px', 
                      color: '#6f42c1',
                      fontSize: '24px',
                      fontWeight: '600',
                      textAlign: 'center'
                    }}>
                      Charts ({llmResponse.charts.length})
                    </h3>
                    <div style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
                      gap: '25px',
                      justifyItems: 'center'
                    }}>
                      {llmResponse.charts.map((chartSrc, index) => (
                        <div key={index} style={{ 
                          border: '2px solid #e9ecef', 
                          borderRadius: '15px', 
                          padding: '20px',
                          backgroundColor: '#fff',
                          boxShadow: '0 6px 20px rgba(0,0,0,0.1)',
                          maxWidth: '450px',
                          width: '100%'
                        }}>
                          <img 
                            src={chartSrc} 
                            alt={`Generated Chart ${index + 1}`} 
                            style={{ 
                              width: '100%',
                              height: 'auto',
                              maxHeight: '300px',
                              objectFit: 'contain',
                              borderRadius: '10px'
                            }}
                            onError={(e) => {
                              console.error(`Chart ${index} failed to load:`, chartSrc.substring(0, 100));
                              e.target.style.display = 'none';
                            }}
                            onLoad={() => console.log(`Chart ${index} loaded successfully`)}
                          />
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* CSS for responsive behavior */}
      <style jsx>{`
        @media (max-width: 768px) {
          .intro-section, .enterprise-section {
            padding: 30px 15px !important;
          }
          
          .faq-grid {
            grid-template-columns: 1fr !important;
          }
          
          .card-row {
            grid-template-columns: 1fr !important;
          }
          
          .chat-bar {
            flex-direction: column !important;
            align-items: stretch !important;
          }
          
          .chat-bar input {
            min-width: auto !important;
            max-width: 100% !important;
            margin-bottom: 10px !important;
          }
          
          .chat-bar button {
            min-width: auto !important;
            max-width: 100% !important;
          }
          
          .charts-container > div {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
}

export default StateOfEnterprise;
