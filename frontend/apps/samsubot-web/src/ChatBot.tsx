import React, { useState } from "react";

const ChatBot: React.FC = () => {
  const [userMessage, setUserMessage] = useState<string>("");
  const [botReply, setBotReply] = useState<string>("");

  const sendMessage = async () => {
    try {
      const response = await fetch("http://localhost:8080/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization:
            "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1MzMxMTI1Mn0.qIJffgPGYr5B-yCdQZaT5QWSA4z-U1vJnmcfyZhb6JE",
        },
        body: JSON.stringify({ message: userMessage }),
      });

      const data = await response.json();
      setBotReply(data.message);
    } catch (error) {
      console.error("Error:", error);
      setBotReply("Something went wrong");
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>SamsuBot</h2>
      <input
        type="text"
        value={userMessage}
        onChange={(e) => setUserMessage(e.target.value)}
        placeholder="Ask me anything..."
        style={{ width: "60%", padding: "8px" }}
      />
      <button onClick={sendMessage} style={{ marginLeft: 10, padding: "8px 16px" }}>
        Send
      </button>
      <div style={{ marginTop: 20 }}>
        <strong>Bot:</strong> {botReply}
      </div>
    </div>
  );
};

export default ChatBot;
