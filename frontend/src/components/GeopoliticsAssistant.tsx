import React, { useEffect, useState } from 'react';
import { FiGlobe, FiTrendingUp, FiSend, FiMessageSquare } from 'react-icons/fi';

interface TrendingTopic {
  title: string;
  category: string;
  summary: string;
  hot_badge: string;
  suggested_query: string;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export default function GeopoliticsAssistant() {
  const [region, setRegion] = useState('Global');
  const [trending, setTrending] = useState<TrendingTopic[]>([]);
  const [loadingTrending, setLoadingTrending] = useState(true);
  
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'assistant', content: "Hello. I am Sia, your geopolitical intelligence assistant. I am continuously monitoring global news wires. How can I help you analyze the current situation?" }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    setLoadingTrending(true);
    fetch(`http://localhost:8000/api/news/trending?location=${region}`)
      .then(r => r.json())
      .then(data => {
        setTrending(data.trending_topics || []);
        setLoadingTrending(false);
      })
      .catch(err => {
        console.error(err);
        setLoadingTrending(false);
      });
  }, [region]);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg: ChatMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);

    try {
      const res = await fetch('http://localhost:8000/api/assistant/geopolitical-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMsg.content,
          user_location: region,
          chat_history: messages.slice(1) // omit initial greeting
        })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.answer || "I am having trouble processing the intelligence right now." }]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { role: 'assistant', content: "I am having trouble connecting to my intelligence feeds right now." }]);
    }
    setIsTyping(false);
  };

  return (
    <div className="module-container" style={{ display: 'flex', flexDirection: 'column', height: '600px', borderRadius: '16px', overflow: 'hidden', border: '1px solid rgba(255,255,255,0.1)' }}>
      <div className="module-header" style={{ flexShrink: 0, padding: '24px', backgroundColor: 'rgba(0,0,0,0.4)', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
        <h1 style={{ display: 'flex', alignItems: 'center', gap: '16px', fontSize: '24px', margin: 0 }}>
          <FiGlobe className="accent-text" /> Sia Geopolitical Assistant
        </h1>
        <p className="subtitle" style={{ fontSize: '16px', margin: '8px 0 0 0', opacity: 0.7 }}>Conversational AI grounded in real-time global news streams.</p>
      </div>

      <div className="module-content" style={{ display: 'flex', flex: 1, minHeight: 0, padding: 0, backgroundColor: 'rgba(255,255,255,0.02)' }}>
        
        {/* Sidebar: Trending Themes */}
        <div style={{ width: '350px', backgroundColor: '#07090e', padding: '32px', display: 'flex', flexDirection: 'column', gap: '24px', flexShrink: 0, overflowY: 'auto' }}>
          <div>
            <label style={{ fontSize: '18px', opacity: 0.8, marginBottom: '8px', display: 'block' }}>Intelligence Region</label>
            <select className="glass-input" value={region} onChange={e => setRegion(e.target.value)} style={{ width: '100%', padding: '16px', fontSize: '20px' }}>
              <option value="Global">Global Context</option>
              <option value="India">India</option>
              <option value="US">United States</option>
              <option value="UK">United Kingdom</option>
              <option value="EU">European Union</option>
            </select>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '22px', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '16px', marginTop: '16px' }}>
            <FiTrendingUp color="#f59e0b" /> Trending Themes
          </div>

          {loadingTrending ? (
            <div className="center-content">
              <div className="spinner" style={{ width: '32px', height: '32px', border: '3px solid rgba(255,255,255,0.1)', borderTopColor: '#38bdf8', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
            </div>
          ) : trending.length === 0 ? (
            <div style={{ opacity: 0.6, fontSize: '18px' }}>No trending data available.</div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {trending.map((t, i) => (
                <div key={i} className="glass-panel" style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '8px', cursor: 'pointer' }} onClick={() => setInput(t.suggested_query || `Tell me more about the situation regarding: ${t.title}`)}>
                  <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#38bdf8' }}>{t.title}</div>
                  <div style={{ fontSize: '14px', opacity: 0.8 }}>{t.summary}</div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px', marginTop: '8px' }}>
                    <span style={{ opacity: 0.6 }}>{t.category}</span>
                    <span style={{ color: '#f59e0b', fontWeight: 'bold' }}>
                      {t.hot_badge}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Chat Area */}
        <div style={{ flex: 1, backgroundColor: '#07090e', display: 'flex', flexDirection: 'column' }}>
          <div style={{ flex: 1, overflowY: 'auto', padding: '48px', display: 'flex', flexDirection: 'column', gap: '32px' }}>
            {messages.map((msg, idx) => (
              <div key={idx} style={{ 
                alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '80%',
                backgroundColor: msg.role === 'user' ? 'rgba(56, 189, 248, 0.1)' : 'rgba(255,255,255,0.05)',
                border: `1px solid ${msg.role === 'user' ? 'rgba(56, 189, 248, 0.2)' : 'rgba(255,255,255,0.1)'}`,
                padding: '24px',
                borderRadius: '16px',
                borderBottomRightRadius: msg.role === 'user' ? '4px' : '16px',
                borderBottomLeftRadius: msg.role === 'assistant' ? '4px' : '16px',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px', opacity: 0.6, fontSize: '16px' }}>
                  {msg.role === 'user' ? 'You' : <><FiGlobe /> Sia Intelligence</>}
                </div>
                <div style={{ fontSize: '22px', lineHeight: '1.6', whiteSpace: 'pre-wrap' }}>{msg.content}</div>
              </div>
            ))}
            {isTyping && (
              <div style={{ alignSelf: 'flex-start', padding: '24px', opacity: 0.6, fontSize: '20px', display: 'flex', alignItems: 'center', gap: '12px' }}>
                <FiMessageSquare /> Sia is analyzing sources...
              </div>
            )}
          </div>

          <div style={{ padding: '32px', borderTop: '1px solid rgba(255,255,255,0.08)', flexShrink: 0 }}>
            <div className="input-group" style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
              <input 
                type="text" 
                className="glass-input" 
                style={{ flex: 1, padding: '24px', fontSize: '22px', borderRadius: '9999px' }}
                placeholder="Ask about global events, economic impacts, or regional stability..." 
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSend()}
                disabled={isTyping}
              />
              <button className="primary-btn" onClick={handleSend} disabled={!input.trim() || isTyping} style={{ width: '72px', height: '72px', padding: 0, display: 'flex', justifyContent: 'center', alignItems: 'center', borderRadius: '50%' }}>
                <FiSend size={32} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
