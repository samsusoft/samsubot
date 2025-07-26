import React, { useState } from 'react';
import axios from 'axios';

function App() {
  // 🔐 Auth state
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [token, setToken] = useState<string | null>(null);

  // 💬 Chat state
  const [message, setMessage] = useState('');
  const [botResponse, setBotResponse] = useState('');

  // 🔓 Login handler
  const handleLogin = async () => {
    try {
      const response = await axios.post('http://localhost:8000/auth/login', {
        username,
        password,
      });

      setToken(response.data.access_token); // assuming JWT is returned as access_token
      alert('Login successful!');
    } catch (error) {
      console.error('Login failed:', error);
      alert('Login failed');
    }
  };

  // 📤 Send message to bot
  const handleSendMessage = async () => {
    if (!token) {
      alert('Please login first');
      return;
    }

    try {
      const response = await axios.post(
        'http://samsubot_backend:8000/chat',
        { message },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setBotResponse(response.data.reply || 'No response');
    } catch (error) {
      console.error('Message failed:', error);
      alert('Failed to send message');
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>🧠SamsuBot</h1>

      <div>
        <h2>🔐Login</h2>
        <input
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <br />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <br />
        <button onClick={handleLogin}>Login</button>
      </div>

      {token && (
        <div>
          <h2>💬 Chat with Bot</h2>
          <textarea
            placeholder="Type your message"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            rows={3}
            cols={40}
          />
          <br />
          <button onClick={handleSendMessage}>Send</button>
          <h3>🤖 Bot says:</h3>
          <p>{botResponse}</p>
        </div>
      )}
    </div>
  );
}

export default App;