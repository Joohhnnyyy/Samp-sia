import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import MainChatArea from './components/MainChatArea';
import './bones/registry';

function App() {
  const [isLightMode, setIsLightMode] = useState(false);
  const [activeAction, setActiveAction] = useState<string | null>(null);

  useEffect(() => {
    if (isLightMode) {
      document.body.setAttribute('data-theme', 'light');
    } else {
      document.body.removeAttribute('data-theme');
    }
  }, [isLightMode]);

  return (
    <div className="app-container" style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden' }}>
      <Sidebar 
        isLightMode={isLightMode} 
        toggleTheme={() => setIsLightMode(!isLightMode)} 
        onSelectAction={(action) => setActiveAction(action)}
        onNewChat={() => setActiveAction('new_chat_' + Date.now())}
      />
      <MainChatArea 
        isLightMode={isLightMode}
        triggeredAction={activeAction}
        onActionHandled={() => setActiveAction(null)}
      />
    </div>
  );
}

export default App;
