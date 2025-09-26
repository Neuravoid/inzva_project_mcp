import React from 'react';

const Message = ({ message }) => {
  const { text, sender } = message;
  
  if (sender === 'user') {
    return (
      <div className="flex items-start justify-end gap-4">
        <div className="flex flex-col items-end gap-1.5">
          <p className="text-sm font-medium text-black/60 dark:text-white/60">User</p>
          <div className="max-w-md rounded-lg bg-primary p-3 text-white">
            <p className="text-base font-normal">{text}</p>
          </div>
        </div>
        <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-black/5 dark:bg-white/5">
          <span className="material-symbols-outlined text-lg text-black/60 dark:text-white/60">person</span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-start gap-4">
      <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary text-white">
        <span className="material-symbols-outlined text-lg">smart_toy</span>
      </div>
      <div className="flex flex-col gap-1.5">
        <p className="text-sm font-medium text-black/60 dark:text-white/60">Agent</p>
        <div className="max-w-md rounded-lg bg-black/5 p-3 dark:bg-white/5">
          <p className="text-base font-normal text-black dark:text-white">{text}</p>
        </div>
      </div>
    </div>
  );
};

export default Message;