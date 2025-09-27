import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import MessageList from './components/MessageList';
import MessageInput from './components/MessageInput';
import Login from './components/Login'; // Login komponentini import et

function App() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [credentials, setCredentials] = useState(null);

  useEffect(() => {
    // Benzersiz oturum kimliği oluştur
    setSessionId(Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15));
  }, []);

  const handleLogin = (creds) => {
    setCredentials(creds);
    setIsAuthenticated(true);
    // İlk karşılama mesajını ekle
    setMessages([
      {
        id: 1,
        text: "Hello! I am an intelligent agent. How can I assist you with your tasks today?",
        sender: 'bot'
      }
    ]);
  };

  const handleSendMessage = async (messageText) => {
    if (!messageText.trim() || !credentials) return;

    const userMessage = { id: Date.now(), text: messageText, sender: 'user' };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8080/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: messageText,
          session_id: sessionId,
          // Kimlik bilgilerini her istekte backend'e gönder
          gemini_api_key: credentials.gemini_api_key,
          mcp_user: credentials.mcp_user,
          mcp_password: credentials.mcp_password,
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      const botMessage = { id: Date.now() + 1, text: data.answer, sender: 'bot' };
      setMessages(prev => [...prev, botMessage]);

    } catch (error) {
      const errorMessage = { id: Date.now() + 1, text: `Sorry, there was an error: ${error.message}`, sender: 'bot' };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Eğer kullanıcı giriş yapmamışsa Login ekranını göster
  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />;
  }

  // Giriş yapılmışsa sohbet arayüzünü göster
  return (
    <div className="relative flex h-screen w-full flex-col overflow-hidden bg-background-light dark:bg-background-dark font-display">
      <Header />
      <MessageList messages={messages} isLoading={isLoading} />
      <MessageInput onSendMessage={handleSendMessage} isLoading={isLoading} />
    </div>
  );
}

export default App;
