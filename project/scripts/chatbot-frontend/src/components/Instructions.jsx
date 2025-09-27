import React from 'react';

function Instructions({ credentials, onComplete }) {
  const proxyCommand = `npx -y mcp-remote https://mcp.turkishtechlab.com/mcp --username ${credentials.mcp_user} --password ${credentials.mcp_password} --stdio-host 0.0.0.0 --stdio-port 8088`;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full bg-white dark:bg-gray-800 rounded-lg shadow-xl p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            🚀 Almost Ready!
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            We need to start the MCP proxy server on your machine. Follow these steps:
          </p>
        </div>

        <div className="space-y-6">
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-3">
              Step 1: Open a New Terminal
            </h3>
            <p className="text-blue-800 dark:text-blue-200 mb-4">
              Open a new PowerShell or Command Prompt window (separate from the one running Docker).
            </p>
          </div>

          <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-green-900 dark:text-green-100 mb-3">
              Step 2: Run This Command
            </h3>
            <div className="bg-gray-900 rounded-lg p-4 mb-4">
              <code className="text-green-400 font-mono text-sm break-all">
                {proxyCommand}
              </code>
            </div>
            <p className="text-green-800 dark:text-green-200 text-sm">
              Copy and paste this command into your new terminal. It will start the MCP proxy server.
            </p>
          </div>

          <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-yellow-900 dark:text-yellow-100 mb-3">
              Step 3: Confirm Success
            </h3>
            <p className="text-yellow-800 dark:text-yellow-200 mb-2">
              You should see messages like:
            </p>
            <ul className="text-yellow-800 dark:text-yellow-200 text-sm space-y-1 ml-4">
              <li>• "Proxy established successfully"</li>
              <li>• "Listening on 0.0.0.0:8088"</li>
            </ul>
            <p className="text-yellow-800 dark:text-yellow-200 text-sm mt-2">
              <strong>Keep this terminal open</strong> - the proxy must remain running.
            </p>
          </div>
        </div>

        <div className="mt-8 text-center">
          <button
            onClick={onComplete}
            className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-8 rounded-lg transition duration-200 transform hover:scale-105"
          >
            ✅ I've Started the Proxy - Continue to Chat
          </button>
        </div>

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Having trouble? Check that your firewall/antivirus isn't blocking port 8088.
          </p>
        </div>
      </div>
    </div>
  );
}

export default Instructions;