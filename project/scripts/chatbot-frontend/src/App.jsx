import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import MessageList from './components/MessageList';
import MessageInput from './components/MessageInput';
import Login from './components/Login';
import Instructions from './components/Instructions';

function App() {
  // 'login', 'instructions', 'chat' durumlarını yönetmek için
  const [appState, setAppState] = useState('login');
  const [credentials, setCredentials] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState('');

  useEffect(() => {
    setSessionId(Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15));
  }, []);

  // 1. Adım: Login bilgileri alındı, talimatlar ekranına geç
  const handleLogin = (creds) => {
    setCredentials(creds);
    setAppState('instructions');
  };

  // 2. Adım: Kullanıcı proxy'i başlattı, sohbet ekranına geç
  const handleInstructionsComplete = () => {
    setAppState('chat');
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
          // Backend'e sadece gemini api anahtarını gönderiyoruz
          gemini_api_key: credentials.gemini_api_key,
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

  // Hangi aşamada olduğumuza göre doğru ekranı göster
  if (appState === 'login') {
    return <Login onLogin={handleLogin} />;
  }

  if (appState === 'instructions') {
    return <Instructions credentials={credentials} onComplete={handleInstructionsComplete} />;
  }

  return (
    <div className="relative flex h-screen w-full flex-col overflow-hidden bg-background-light dark:bg-background-dark font-display">
      <Header />
      <MessageList messages={messages} isLoading={isLoading} />
      <MessageInput onSendMessage={handleSendMessage} isLoading={isLoading} />
    </div>
  );
}

export default App;
