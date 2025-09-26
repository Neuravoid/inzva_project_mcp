import React from 'react';

const TypingIndicator = () => {
  return (
    <div className="flex items-start gap-4">
      <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary text-white">
        <span className="material-symbols-outlined text-lg">smart_toy</span>
      </div>
      <div className="flex flex-col gap-1.5">
        <p className="text-sm font-medium text-black/60 dark:text-white/60">Agent</p>
        <div className="flex items-center gap-2 max-w-md rounded-lg bg-black/5 p-3 dark:bg-white/5">
          <p className="text-base font-normal text-black dark:text-white">Agent is typing</p>
          <div className="flex gap-0.5">
            <span className="size-1 animate-[bounce_1s_infinite_0.1s] rounded-full bg-black/50 dark:bg-white/50"></span>
            <span className="size-1 animate-[bounce_1s_infinite_0.2s] rounded-full bg-black/50 dark:bg-white/50"></span>
            <span className="size-1 animate-[bounce_1s_infinite_0.3s] rounded-full bg-black/50 dark:bg-white/50"></span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;