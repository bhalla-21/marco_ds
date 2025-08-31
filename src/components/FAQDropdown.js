import React, { useState } from "react";

function FAQDropdown({ question, options, onSelect }) {
  const [hover, setHover] = useState(false);

  return (
    <div
      className="faq-dropdown"
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{ position: "relative" }}
    >
      <div className="faq-main-question">{question}</div>
      {hover && (
        <div className="faq-dropdown-menu">
          {options.map((opt, idx) => (
            <div
              key={idx}
              className="faq-dropdown-item"
              onMouseDown={() => onSelect(question, opt)}
              style={{ cursor: "pointer" }}
            >
              {opt}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default FAQDropdown;
