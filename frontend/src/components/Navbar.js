import React from 'react';
import { NavLink } from 'react-router-dom';

function Navbar({ user, onLogout }) {
  return (
    <nav className="navbar">
      <ul className="navbar-links">
        <li>
          <NavLink to="/" className="nav-link">
            Home
          </NavLink>
        </li>
        <li>
          <NavLink to="/recipe-box" className="nav-link">
            Recipe Box
          </NavLink>
        </li>
        {user ? (
          <NavLink to="/account" className="nav-link">
          Welcome, {user.username}!
          </NavLink>
        ) : (
          <li>
            <NavLink to="/account" className="nav-link">
              Account
            </NavLink>
          </li>
        )}
      </ul>
      <div className="navbar-left">
        {user && (
          <button className="logout-button" onClick={onLogout}>
            Log Out
          </button>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
