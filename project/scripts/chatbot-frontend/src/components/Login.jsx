import React, { useState } from 'react';

const Login = ({ onLogin }) => {
  const [geminiApiKey, setGeminiApiKey] = useState('');
  const [mcpUser, setMcpUser] = useState('');
  const [mcpPassword, setMcpPassword] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (geminiApiKey.trim() && mcpUser.trim() && mcpPassword.trim()) {
      onLogin({
        gemini_api_key: geminiApiKey,
        mcp_user: mcpUser,
        mcp_password: mcpPassword,
      });
    } else {
      alert('Please fill in all fields.');
    }
  };

  return (
    <div className="flex items-center justify-center h-screen bg-background-light dark:bg-background-dark">
      <div className="w-full max-w-md p-8 space-y-8 bg-white rounded-lg shadow-lg dark:bg-gray-800">
        <div className="text-center">
            <div className="flex justify-center mb-4">
                 <div className="flex size-12 items-center justify-center rounded-full bg-primary text-white">
                    <span className="material-symbols-outlined text-3xl">smart_toy</span>
                </div>
            </div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Agent Credentials
          </h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Please enter your credentials to start the session.
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <input
                id="gemini-api-key"
                name="gemini-api-key"
                type="password"
                required
                className="relative block w-full px-3 py-2 text-gray-900 placeholder-gray-500 bg-gray-50 border border-gray-300 rounded-t-md focus:outline-none focus:ring-primary focus:border-primary focus:z-10 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white"
                placeholder="Gemini API Key"
                value={geminiApiKey}
                onChange={(e) => setGeminiApiKey(e.target.value)}
              />
            </div>
            <div>
              <input
                id="mcp-user"
                name="mcp-user"
                type="text"
                required
                className="relative block w-full px-3 py-2 text-gray-900 placeholder-gray-500 bg-gray-50 border border-gray-300 focus:outline-none focus:ring-primary focus:border-primary focus:z-10 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white"
                placeholder="MCP Username"
                value={mcpUser}
                onChange={(e) => setMcpUser(e.target.value)}
              />
            </div>
            <div>
              <input
                id="mcp-password"
                name="mcp-password"
                type="password"
                required
                className="relative block w-full px-3 py-2 text-gray-900 placeholder-gray-500 bg-gray-50 border border-gray-300 rounded-b-md focus:outline-none focus:ring-primary focus:border-primary focus:z-10 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white"
                placeholder="MCP Password"
                value={mcpPassword}
                onChange={(e) => setMcpPassword(e.target.value)}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              className="group relative flex justify-center w-full px-4 py-2 text-sm font-medium text-white bg-primary border border-transparent rounded-md hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
            >
              Start Chat
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Login;