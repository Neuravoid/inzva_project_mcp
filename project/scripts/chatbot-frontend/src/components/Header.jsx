import React from 'react';

const Header = () => {
  return (
    <header className="flex items-center justify-between whitespace-nowrap border-b border-white/10 px-6 py-4">
      <div className="flex items-center gap-3">
        <div className="flex size-8 items-center justify-center rounded-full bg-primary text-white">
          <span className="material-symbols-outlined text-lg">
            smart_toy
          </span>
        </div>
        <h2 className="text-lg font-bold text-black dark:text-white">Intelligent Agent</h2>
      </div>
      <div className="flex items-center gap-4">
        <button className="flex h-10 w-10 items-center justify-center rounded-full text-black/60 hover:bg-black/5 dark:text-white/60 dark:hover:bg-white/5">
          <span className="material-symbols-outlined text-xl">
            settings
          </span>
        </button>
        <div 
          className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10" 
          style={{
            backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuC2yjX3_Lf2o5hbiwp1kASgGToA9ndbbzK0xIhU-ZrUoOzaovAR07KaT3ppCo2Wn2RuS5aUcdqprzqUVbpJ5KsS0U-wSezK7aCK64ywOaAwwtqdK0lQn55A2SA6ZrsY0AnkrTgfOcYC65Ge30TsVhpuaEdfLyM1LDojnEcUmKxJ2izY31gYrS9mmvD7108BTaesLq2vnRdDO0ME5oEuxKBRw3jehtT8XIrkWbDIjId3xHskHLhKpGv5Mimq5MFJ5f6k4IIQtxo7z5s")'
          }}
        />
      </div>
    </header>
  );
};

export default Header;