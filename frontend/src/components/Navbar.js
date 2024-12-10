// Navbar.js
import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';

function Navbar({ user, onLogout }) {
  const [isActive, setIsActive] = useState(false);

  const toggleNavbar = () => {
    setIsActive(!isActive);
  };

  const closeNavbar = () => {
    setIsActive(false);
  };

  return (
    <nav className="navbar">
      {/* Brand/Logo Section */}
      <div className="navbar-left">
        <NavLink to="/" className="nav-brand" onClick={closeNavbar}>
          {/* Replace the src with your actual logo path or use text */}
          {/* <img src="/path-to-your-logo.png" alt="Brand Logo" className="navbar-logo" /> */}
          <span className="brand-name">The Recipe Fox</span>
        </NavLink>
      </div>
      <div
        className={`hamburger ${isActive ? 'open' : ''}`}
        onClick={toggleNavbar}
        aria-label="Toggle navigation"
        aria-expanded={isActive}
      >
        <div></div>
        <div></div>
        <div></div>
      </div>

      {/* Navigation Links */}
      <ul className={`navbar-links ${isActive ? 'active' : ''}`}>
        <li>
          <NavLink to="/" className="nav-link" onClick={closeNavbar}>
            Home
          </NavLink>
        </li>
        <li>
          <NavLink to="/recipe-box" className="nav-link" onClick={closeNavbar}>
            Recipe Box
          </NavLink>
        </li>
        {user ? (
            <li>
              <NavLink to="/account" className="nav-link" onClick={closeNavbar}>
                {user.username}
              </NavLink>
            </li>
        ) : (
          <li>
            <NavLink to="/account" className="nav-link" onClick={closeNavbar}>
              Account
            </NavLink>
          </li>
        )}
        {user ? (<div className="logout-nav-button" onClick={onLogout}>
                Log Out
          </div>) : (<div></div>)
          }
          
      </ul>
    </nav>
  );
}

export default Navbar;
