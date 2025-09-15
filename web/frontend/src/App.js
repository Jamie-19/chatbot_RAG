import React, { useState, useEffect, useRef, useCallback } from 'react';
import './App.css';

// --- SVG Icons ---
const BotAvatar = () => (
  <div className="avatar bot-avatar">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="white" xmlns="http://www.w3.org/2000/svg"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zM8.5 12.5c-0.83 0-1.5-0.67-1.5-1.5s0.67-1.5 1.5-1.5 1.5 0.67 1.5 1.5-0.67 1.5-1.5 1.5zm7 0c-0.83 0-1.5-0.67-1.5-1.5s0.67-1.5 1.5-1.5 1.5 0.67 1.5 1.5-0.67 1.5-1.5 1.5zm-3.5 4c-2.33 0-4.31-1.46-5.11-3.5h10.22c-0.8 2.04-2.78 3.5-5.11 3.5z"/></svg>
  </div>
);

const UserAvatar = () => (
  <div className="avatar user-avatar">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="white" xmlns="http://www.w3.org/2000/svg"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
  </div>
);

const SendIcon = () => (
  <svg width="28" height="28" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
);

const TypingIndicator = () => (
  <div className="message-row bot-row">
    <BotAvatar />
    <div className="typing-indicator">
      <span>BOT is typing</span>
      <div className="dot"></div>
      <div className="dot"></div>
      <div className="dot"></div>
    </div>
  </div>
);

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isTyping, _setIsTyping] = useState(false);
  const isTypingRef = useRef(isTyping);
  const ws = useRef(null);
  const messagesEndRef = useRef(null);

  const setIsTyping = useCallback((value) => {
    isTypingRef.current = value;
    _setIsTyping(value);
  }, []);

  const connectWebSocket = useCallback(() => {
    if (ws.current && ws.current.readyState !== WebSocket.CLOSED) {
      ws.current.close();
    }

    ws.current = new WebSocket(`ws://${window.location.host}/chat`);

    ws.current.onopen = () => {
      console.log('WebSocket connection established.');
      setMessages(prevMessages => {
        if (prevMessages.length === 0) {
          return [{ sender: 'bot', text: 'Connected! How can I help you today?' }];
        }
        return prevMessages;
      });
    };

    ws.current.onclose = () => {
      console.log('WebSocket connection closed.');
    };

    ws.current.onmessage = (event) => {
      if (isTypingRef.current) {
        setIsTyping(false);
      }

      setMessages(prevMessages => {
        const lastMessage = prevMessages[prevMessages.length - 1];
        if (lastMessage && lastMessage.sender === 'bot') {
          return [
            ...prevMessages.slice(0, prevMessages.length - 1),
            { ...lastMessage, text: lastMessage.text + event.data },
          ];
        } else {
          return [...prevMessages, { sender: 'bot', text: event.data }];
        }
      });
    };
  }, [setIsTyping]);

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (ws.current) ws.current.close();
    };
  }, [connectWebSocket]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const sendMessage = (event) => {
    event.preventDefault();
    if (input.trim() && ws.current && ws.current.readyState === WebSocket.OPEN) {
      setMessages(prev => [...prev, { sender: 'user', text: input }]);
      ws.current.send(input);
      setIsTyping(true);
      setInput('');
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>RAG Chatbot</h1>
      </header>
      <div className="chat-window">
        {messages.map((msg, index) => (
          <div key={index} className={`message-row ${msg.sender}-row`}>
            {msg.sender === 'bot' ? <BotAvatar /> : <UserAvatar />}
            <div className={`message-bubble ${msg.sender}-bubble`}>
              {msg.text}
            </div>
          </div>
        ))}
        {isTyping && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>
      <form className="chat-form" onSubmit={sendMessage}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask me anything..."
          autoComplete="off"
        />
        <button type="submit">
          <SendIcon />
        </button>
      </form>
    </div>
  );
}

export default App;
