import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import StateOfEnterprise from "./pages/StateOfEnterprise";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/enterprise" element={<StateOfEnterprise />} />
      </Routes>
    </Router>
  );
}

export default App;
