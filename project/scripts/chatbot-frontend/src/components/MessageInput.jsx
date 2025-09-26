import React, { useState } from 'react';

const MessageInput = ({ onSendMessage, isLoading }) => {
  const [inputText, setInputText] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputText.trim() && !isLoading) {
      onSendMessage(inputText);
      setInputText('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <footer className="border-t border-white/10 p-6">
      <div className="mx-auto flex max-w-4xl items-center gap-4">
        <form onSubmit={handleSubmit} className="relative flex-1">
          <input
            className="w-full rounded-lg border-transparent bg-black/5 py-3 pl-4 pr-12 text-black dark:bg-white/5 dark:text-white dark:placeholder:text-white/60"
            placeholder="Type your message..."
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !inputText.trim()}
            className="absolute inset-y-0 right-0 flex items-center pr-4 text-black/60 hover:text-primary dark:text-white/60 dark:hover:text-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span className="material-symbols-outlined">
              send
            </span>
          </button>
        </form>
        <button className="flex h-12 w-12 items-center justify-center rounded-lg bg-black/5 text-black/60 hover:text-primary dark:bg-white/5 dark:text-white/60 dark:hover:text-primary">
          <span className="material-symbols-outlined text-2xl">
            mic
          </span>
        </button>
      </div>
    </footer>
  );
};

export default MessageInput;