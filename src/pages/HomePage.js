// src/pages/HomePage.js
import React from "react";
import { useNavigate } from "react-router-dom";
import TopNav from "../components/TopNav"; // Use the new component
import SectionCard from "../components/SectionCard";

function HomePage() {
  const navigate = useNavigate();

  const handleChatNavigation = () => {
    navigate("/enterprise");
  };

  return (
    <div className="main-bg">
      <TopNav /> {/* <-- This now contains your entire header */}
      <div className="header-section">
        {/* The Mondelez logo is now in TopNav, so it's removed from here */}
        <h1 className="marco-header">
          MARCO<span className="gpt-accent">-GPT</span>
          <span className="sparkle-icon">✨</span>
        </h1>
        <div className="powered-by">
          <span>Powered by <b>ARISE</b></span>
        </div>
        <p className="intro-text">
          I'm a GenAI knowledge tool to help you get deeper insights faster. I'm trained to answer What, Why and some diagnostic questions on Nielsen consumption and panel data and unstructured data sources.
        </p>
        <div className="chat-section">
          <input 
            type="text" 
            className="chat-box" 
            placeholder="How can I help?" 
            onFocus={handleChatNavigation}
          />
          <div className="chat-actions">
            <button className="chat-history-button">Show Chat History</button>
            <a href="/enterprise" className="chat-link">Go back to my chat</a>
          </div>
        </div>
        <div className="skills-section">
          <p className="skills-title">
            Skills:<br />
            Below are the skills I am trained on:
          </p>
          <div className="card-row">
            <SectionCard title="State of the Enterprise" description="What are the Net Revenue drivers for Oreo in QID?" route="/enterprise" />
            <SectionCard title="Customer" description="What were the top selling products at Publix in January of 2025?" disabled />
            <SectionCard title="Deep Research" description="Please provide an overview of buyer preferences for the Cracker Category for Q1 of 2025." comingSoon />
          </div>
        </div>
      </div>
    </div>
  );
}

export default HomePage;
