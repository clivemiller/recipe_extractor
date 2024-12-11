import React, { useState, useEffect } from 'react';

const API_BASE_URL = 'https://recipe-extractor-backend.onrender.com'; // Backend base URL

function Account({ user, setUser }) {
  const [authMode, setAuthMode] = useState(user ? 'loggedIn' : 'login'); // 'login', 'signup', or 'loggedIn'
  const [formData, setFormData] = useState({ email: '', password: '', username: ''});
  const [updateData, setUpdateData] = useState({ username: '', currentPassword: '', newPassword: '' });
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    if (user) {
      setUpdateData({ username: user.username, currentPassword: '', newPassword: '' });
    }
  }, [user]);

  const handleLogout = () => {
    localStorage.removeItem('user');
    setUser(null);
    setAuthMode('login');
  };

  // Handle input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleUpdateInputChange = (e) => {
    const { name, value } = e.target;
    setUpdateData({ ...updateData, [name]: value });
  };

  // Handle form submission for login or signup
  const handleAuthSubmit = (e) => {
    e.preventDefault();
    const endpoint = authMode === 'login' ? '/api/login' : '/api/signup';

    fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          setError(data.error);
        } else {
          localStorage.setItem('user', JSON.stringify(data)); // Save user to localStorage
          setUser(data); // Update the user state
          setError('');
          setAuthMode('loggedIn');
        }
      })
      .catch(() => setError('Something went wrong. Please try again.'));
  };

  // Handle updating username or password
  const handleUpdateSubmit = (e) => {
    e.preventDefault();
    fetch(`${API_BASE_URL}/api/users/${user.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updateData),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          setError(data.error);
          setSuccessMessage('');
        } else {
          setUser(data);
          localStorage.setItem('user', JSON.stringify(data)); // Update localStorage
          setError('');
          setSuccessMessage('Account details updated successfully!');
        }
      })
      .catch(() => setError('Something went wrong. Please try again.'));
  };

  if (authMode === 'loggedIn' && user) {
    return (
      <div className="account-page">
        <h1>Welcome, {user.username}!</h1>
        <p>Email: {user.email}</p>
        <p>Subscription: {user.is_paying_member ? 'Premium' : 'Default'}</p>
        <button onClick={handleLogout}>Log Out</button>
        <h2>Update Account</h2>
        {error && <p className="error">{error}</p>}
        {successMessage && <p className="success">{successMessage}</p>}
        <form onSubmit={handleUpdateSubmit}>
          <div>
            <label>
              Username:
              <input
                type="text"
                name="username"
                value={updateData.username}
                onChange={handleUpdateInputChange}
                required
              />
            </label>
          </div>
          <div>
            <label>
              Current Password:
              <input
                type="password"
                name="currentPassword"
                value={updateData.currentPassword}
                onChange={handleUpdateInputChange}
                required
              />
            </label>
          </div>
          <div>
            <label>
              New Password:
              <input
                type="password"
                name="newPassword"
                value={updateData.newPassword}
                onChange={handleUpdateInputChange}
                required
              />
            </label>
          </div>
          <button type="submit">Update Account</button>
        </form>
      </div>
    );
  }

  return (
    <div className="auth-container">
      <h1>{authMode === 'login' ? 'Log In' : 'Sign Up'}</h1>
      {error && <p className="error">{error}</p>}
      <form onSubmit={handleAuthSubmit}>
        {authMode === 'signup' && (
          <div>
            <label>
              Username:
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                required
              />
            </label>
          </div>
        )}
        <div>
          <label>
            Email:
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              required
            />
          </label>
        </div>
        <div>
          <label>
            Password:
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              required
            />
          </label>
        </div>
        <button type="submit">{authMode === 'login' ? 'Log In' : 'Sign Up'}</button>
      </form>
      <p>
        {authMode === 'login' ? "Don't have an account?" : 'Already have an account?'}
        <button onClick={() => setAuthMode(authMode === 'login' ? 'signup' : 'login')}>
          {authMode === 'login' ? 'Sign Up' : 'Log In'}
        </button>
      </p>
    </div>
  );
}

export default Account;
