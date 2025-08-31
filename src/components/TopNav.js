// src/components/TopNav.js
import React from 'react';
import { NavLink } from 'react-router-dom'; // Use NavLink for active styling

function TopNav() {
  return (
    <nav className="top-nav">
      <div className="nav-left">
        <img 
          src="https://upload.wikimedia.org/wikipedia/commons/c/c7/Mondelez_international_2012_logo.svg" 
          alt="Mondelez Logo" 
          className="nav-logo" 
        />
        <div className="nav-links">
          <NavLink to="/" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
            <span className="icon-placeholder">🏠</span> Home Page
          </NavLink>
          <NavLink to="/enterprise" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
            <span className="icon-placeholder">📈</span> State of the Enterprise
          </NavLink>
          <NavLink to="/user-guide" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
            <span className="icon-placeholder">📖</span> User Guide
          </NavLink>
        </div>
      </div>
      <div className="nav-right">
        <span className="data-refresh-text">Data Refreshed Thru: 7/5/2025</span>
        <div className="user-profile">
          <span className="icon-placeholder-user">👤</span>
          <span>user@mdlz.com</span>
          <span className="chevron-down">▼</span>
        </div>
      </div>
    </nav>
  );
}

export default TopNav;
