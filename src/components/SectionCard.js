import React from "react";
import { useNavigate } from "react-router-dom";

function SectionCard({ title, description, route, disabled, comingSoon }) {
  const navigate = useNavigate();
  return (
    <div 
      className={`section-card${disabled ? " section-card-disabled" : ""}${comingSoon ? " section-card-comingsoon" : ""}`}
      onClick={() => { if (route && !disabled && !comingSoon) navigate(route); }}
      style={{ cursor: route && !disabled && !comingSoon ? "pointer" : "default" }}
    >
      <strong>{title}</strong>
      <div>{description}</div>
      {comingSoon && <span className="comingsoon-badge">Coming Soon</span>}
      {disabled && <span className="indev-badge">In development</span>}
    </div>
  );
}

export default SectionCard;
