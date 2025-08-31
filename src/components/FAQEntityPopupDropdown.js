import React, { useState, useRef, useEffect } from "react";

function FAQEntityPopupDropdown({ template, onChange }) {
  // Prep initial selected values for each entity
  const initialValues = Object.fromEntries(
    template
      .filter(part => typeof part === "object")
      .map(e => [e.key, e.options[0]])
  );
  const [entityValues, setEntityValues] = useState(initialValues);
  const [openDropdown, setOpenDropdown] = useState(null);
  const dropdownRefs = useRef({});

  // Build full question from selected values
  const buildQuestion = () =>
    template.map((part) =>
      typeof part === "object" ? entityValues[part.key] : part
    ).join("");

  useEffect(() => {
    onChange(buildQuestion());
  }, [entityValues]);

  // Close the dropdown when clicking outside
  useEffect(() => {
    function handleClick(e) {
      if (
        openDropdown &&
        dropdownRefs.current[openDropdown] &&
        !dropdownRefs.current[openDropdown].contains(e.target)
      ) {
        setOpenDropdown(null);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [openDropdown]);

  // Render only **one pill per entity**, and open dropdown on click
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
      {template.map((part, idx) =>
        typeof part === "object" ? (
          <span
            key={part.key}
            style={{ position: "relative", display: "inline-block" }}
            ref={el => (dropdownRefs.current[part.key] = el)}
          >
            <span
              style={{
                background: "#d7c4ef",
                borderRadius: "8px",
                padding: "5px 18px",
                color: "#694673",
                cursor: "pointer",
                border: openDropdown === part.key ? "1.6px solid #6c3f99" : "1.6px solid transparent",
                fontWeight: "bold",
                margin: "0 2px",
                boxShadow: openDropdown === part.key ? "0 2px 10px #e4d5fa" : undefined,
                display: "inline-block",
                transition: "background 0.25s"
              }}
              onClick={() => setOpenDropdown(openDropdown === part.key ? null : part.key)}
            >
              {entityValues[part.key]} 
              <span style={{
                marginLeft: 7,
                fontWeight: 900,
                color: "#7f39b0",
                fontSize: "0.98em"
              }}>▼</span>
            </span>
            {openDropdown === part.key && (
              <div
                style={{
                  position: "absolute",
                  top: "118%",
                  left: 0,
                  zIndex: 100,
                  background: "#fff",
                  boxShadow: "0 6px 28px #cabbf6",
                  borderRadius: 10,
                  padding: "7px 2px",
                  minWidth: 132,
                  marginTop: 7,
                  border: "1.5px solid #ba9ce5",
                }}
              >
                {part.options.map(option => (
                  <div
                    key={option}
                    style={{
                      padding: "10px 22px",
                      cursor: "pointer",
                      color: "#6c3f99",
                      fontWeight: 500,
                      background: entityValues[part.key] === option ? "#f4eefb" : "#fff",
                      borderRadius: 6,
                      marginBottom: 1,
                      textAlign: "left",
                    }}
                    onClick={() => {
                      setEntityValues(v => ({ ...v, [part.key]: option }));
                      setOpenDropdown(null);
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

export default FAQEntityPopupDropdown;
