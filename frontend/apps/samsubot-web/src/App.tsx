import React, { useState } from 'react';

// Mock API functions for demonstration
const mockAPI = {
  login: async (username: string, password: string) => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    if (username && password) {
      return { data: { access_token: 'mock-token-123' } };
    }
    throw new Error('Invalid credentials');
  },
  
  getChatHistory: async (token: string) => {
    await new Promise(resolve => setTimeout(resolve, 500));
    return {
      data: [
        {
          user_message: "Hello",
          bot_response: "Hi there! How can I help you?",
          timestamp: new Date(Date.now() - 60000).toISOString()
        },
        {
          user_message: "What's the weather?",
          bot_response: "I'd need your location to check the weather for you.",
          timestamp: new Date(Date.now() - 30000).toISOString()
        }
      ]
    };
  },
  
  sendMessage: async (token: string, sessionId: string, message: string) => {
    await new Promise(resolve => setTimeout(resolve, 800));
    
    // Mock different response types
    const responses = [
      { message: "That's an interesting question! Let me help you with that." },
      { 
        message: { 
          query: message, 
          result: `I processed your message: "${message}". Here's my response!` 
        } 
      }
    ];
    
    return responses[Math.floor(Math.random() * responses.length)];
  }
};

type BotResponse = string | { query: string; result: string };

function App() {
  // 🔐 Auth state
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // 💬 Chat state
  const [message, setMessage] = useState('');
  const [botResponse, setBotResponse] = useState<BotResponse>('');
  const [chatHistory, setChatHistory] = useState<
    { user_message: string; bot_response: string; timestamp: string }[]
  >([]);
  const [isSending, setIsSending] = useState(false);

  // 🔓 Login handler
  const handleLogin = async () => {
    if (!username || !password) {
      alert('Please enter both username and password');
      return;
    }

    setIsLoading(true);
    try {
      const response = await mockAPI.login(username, password);
      const accessToken = response.data.access_token;
      setToken(accessToken);
      alert('Login successful!');

      // ⏬ Load history after login
      await loadChatHistory(accessToken);
    } catch (error) {
      console.error('Login failed:', error);
      alert('Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  // 📜 Load chat history from backend
  const loadChatHistory = async (accessToken: string) => {
    try {
      const response = await mockAPI.getChatHistory(accessToken);
      setChatHistory(response.data);
    } catch (error) {
      console.error('Failed to load chat history:', error);
    }
  };

  // 📤 Send message to bot
  const handleSendMessage = async () => {
    if (!token) {
      alert('Please login first');
      return;
    }

    if (!message.trim()) {
      alert('Please enter a message');
      return;
    }

    setIsSending(true);
    try {
      const response = await mockAPI.sendMessage(token, 'user123', message);
      console.log('Bot response:', response);

      const raw = response.message;
      if (typeof raw === 'string') {
        setBotResponse(raw);
      } else if (raw && typeof raw === 'object' && 'result' in raw && 'query' in raw) {
        setBotResponse({
          query: raw.query,
          result: raw.result,
        });
      } else {
        setBotResponse('No valid response');
      }

      // Add to chat history immediately (simulate real-time update)
      const newHistoryItem = {
        user_message: message,
        bot_response: typeof raw === 'string' ? raw : raw.result || 'No response',
        timestamp: new Date().toISOString()
      };
      setChatHistory(prev => [...prev, newHistoryItem]);

      setMessage(''); // clear input
    } catch (error) {
      console.error('Message failed:', error);
      alert('Failed to send message');
    } finally {
      setIsSending(false);
    }
  };

  // Helper function to render bot response safely
  const renderBotResponse = () => {
    if (!botResponse) return <p>No response yet...</p>;
    
    if (typeof botResponse === 'string') {
      return <p>{botResponse}</p>;
    } else if (botResponse && typeof botResponse === 'object' && 'query' in botResponse && 'result' in botResponse) {
      return (
        <div>
          <p><strong>Query:</strong> {botResponse.query}</p>
          <p><strong>Result:</strong> {botResponse.result}</p>
        </div>
      );
    }
    return <p>No valid response</p>;
  };

  // Handle Enter key press in textarea
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div style={{ 
      padding: 20, 
      maxWidth: 800, 
      margin: '0 auto', 
      fontFamily: 'Arial, sans-serif' 
    }}>
      <h1>🧠 SamsuBot</h1>

      {/* 🔐 Login Section */}
      {!token && (
        <div style={{ 
          border: '1px solid #ddd', 
          padding: 20, 
          borderRadius: 8, 
          backgroundColor: '#f9f9f9' 
        }}>
          <h2>🔐 Login</h2>
          <div style={{ marginBottom: 10 }}>
            <input
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={{ 
                padding: 8, 
                marginRight: 10, 
                border: '1px solid #ccc', 
                borderRadius: 4,
                width: 150
              }}
            />
          </div>
          <div style={{ marginBottom: 15 }}>
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{ 
                padding: 8, 
                marginRight: 10, 
                border: '1px solid #ccc', 
                borderRadius: 4,
                width: 150
              }}
            />
          </div>
          <button 
            onClick={handleLogin}
            disabled={isLoading}
            style={{
              padding: '10px 20px',
              backgroundColor: isLoading ? '#ccc' : '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: 4,
              cursor: isLoading ? 'not-allowed' : 'pointer'
            }}
          >
            {isLoading ? 'Logging in...' : 'Login'}
          </button>
        </div>
      )}

      {/* 💬 Chat Section */}
      {token && (
        <div style={{ marginTop: 30 }}>
          <div style={{
            border: '1px solid #ddd',
            padding: 20,
            borderRadius: 8,
            backgroundColor: '#f9f9f9'
          }}>
            <h2>💬 Chat with Bot</h2>
            <textarea
              placeholder="Type your message (Press Enter to send, Shift+Enter for new line)"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              rows={3}
              style={{
                width: '100%',
                padding: 10,
                border: '1px solid #ccc',
                borderRadius: 4,
                resize: 'vertical',
                fontSize: 14
              }}
            />
            <br />
            <button 
              onClick={handleSendMessage}
              disabled={isSending || !message.trim()}
              style={{
                marginTop: 10,
                padding: '10px 20px',
                backgroundColor: (isSending || !message.trim()) ? '#ccc' : '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: 4,
                cursor: (isSending || !message.trim()) ? 'not-allowed' : 'pointer'
              }}
            >
              {isSending ? 'Sending...' : 'Send'}
            </button>
          </div>

          <div style={{ marginTop: 20 }}>
            <h3>🤖 Bot says:</h3>
            <div style={{
              border: '1px solid #ddd',
              padding: 15,
              borderRadius: 8,
              backgroundColor: '#fff',
              minHeight: 60
            }}>
              {renderBotResponse()}
            </div>
          </div>

          {/* 📜 History Section */}
          <div style={{ marginTop: 30 }}>
            <h3>🗂 Chat History:</h3>
            <div style={{ 
              maxHeight: 400, 
              overflowY: 'auto', 
              border: '1px solid #ccc', 
              padding: 15,
              borderRadius: 8,
              backgroundColor: '#fff'
            }}>
              {chatHistory.length === 0 ? (
                <p style={{ color: '#666', fontStyle: 'italic' }}>No chat history yet...</p>
              ) : (
                chatHistory.map((msg, index) => (
                  <div key={index} style={{ 
                    marginBottom: 15, 
                    paddingBottom: 15,
                    borderBottom: index < chatHistory.length - 1 ? '1px solid #eee' : 'none'
                  }}>
                    <div style={{ marginBottom: 5 }}>
                      <strong>🧑 You:</strong> {msg.user_message}
                    </div>
                    <div style={{ marginBottom: 5 }}>
                      <strong>🤖 Bot:</strong> {msg.bot_response}
                    </div>
                    <small style={{ color: '#666' }}>
                      {new Date(msg.timestamp).toLocaleString()}
                    </small>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;