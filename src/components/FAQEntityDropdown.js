import React, { useState, useRef } from "react";

function FAQEntityDropdown({ template, onChange }) {
  const initialValues = Object.fromEntries(
    template.filter(part => typeof part === "object").map(e => [e.key, e.options[0]])
  );
  const [entityValues, setEntityValues] = useState(initialValues);
  const [hoveredEntity, setHoveredEntity] = useState(null);

  const entityRefs = useRef({});
  const dropdownRefs = useRef({});

  const buildQuestion = () =>
    template.map(part =>
      typeof part === "object" ? entityValues[part.key] : part
    ).join("");

  React.useEffect(() => {
    onChange(buildQuestion());
  }, [entityValues, onChange]);

  // Keep dropdown open if mouse is over either entity or dropdown
  const handleMouseLeave = (key) => {
    setTimeout(() => {
      const entityHovered = entityRefs.current[key]?.matches(':hover');
      const dropdownHovered = dropdownRefs.current[key]?.matches(':hover');
      if (!entityHovered && !dropdownHovered) {
        setHoveredEntity(null);
      }
    }, 140); // short delay for smoother user experience
  };

  return (
    <span className="faq-entity-inline">
      {template.map((part, idx) =>
        typeof part === "object" ? (
          <span
            key={part.key}
            className="entity-bold-container"
            style={{ position: "relative", display: "inline-block" }}
            ref={el => (entityRefs.current[part.key] = el)}
            onMouseEnter={() => setHoveredEntity(part.key)}
            onMouseLeave={() => handleMouseLeave(part.key)}
          >
            <span className="entity-bold">
              {entityValues[part.key]}
            </span>
            {hoveredEntity === part.key && (
              <div
                ref={el => (dropdownRefs.current[part.key] = el)}
                className="entity-popup-hover"
                onMouseEnter={() => setHoveredEntity(part.key)}
                onMouseLeave={() => handleMouseLeave(part.key)}
              >
                {part.options.map(option => (
                  <div
                    key={option}
                    className={`entity-option-hover${entityValues[part.key] === option ? " selected" : ""}`}
                    onClick={() => {
                      setEntityValues(v => ({ ...v, [part.key]: option }));
                      setHoveredEntity(null);
                    }}
                  >
                    {option}
                  </div>
                ))}
              </div>
            )}
          </span>
        ) : (
          <span key={idx}>{part}</span>
        )
      )}
    </span>
  );
}

export default FAQEntityDropdown;
