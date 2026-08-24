import React, { useState } from 'react';
import { FiMessageSquare, FiSend, FiDatabase, FiLink } from 'react-icons/fi';
import { API_BASE_URL } from '../config';

interface RagQnAProps {
  jobId?: string;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  citations?: any[];
}

export default function RagQnA({ jobId }: RagQnAProps) {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: "I'm Sia. I have access to the knowledge base of your recent scrapes. Ask me anything about the data." }
  ]);
  const [input, setInput] = useState('');
  const [isIndexing, setIsIndexing] = useState(false);
  const [indexStatus, setIndexStatus] = useState<string | null>(null);
  const [collectionName, setCollectionName] = useState<string | null>(null);
  const [isAsking, setIsAsking] = useState(false);

  const handleIndex = async () => {
    if (!jobId) return;
    setIsIndexing(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/rag/index/${jobId}`, { method: 'POST' });
      const data = await res.json();
      setCollectionName(data.collection_name);
      setIndexStatus(`Indexed ${data.chunks_indexed} chunks successfully.`);
    } catch (err) {
      console.error(err);
      setIndexStatus('Failed to index data.');
    }
    setIsIndexing(false);
  };

  const handleSend = async () => {
    if (!input.trim() || !jobId) return;
    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsAsking(true);
    
    try {
      const res = await fetch(`${API_BASE_URL}/api/rag/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: userMessage.content,
          collection_name: collectionName || `job_${jobId.replace(/-/g, '_')}`,
          job_id: jobId,
          top_k: 5
        })
      });
      const data = await res.json();
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.answer || "I could not find an answer in the knowledge base.",
        citations: data.citations || []
      }]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "Error communicating with RAG engine."
      }]);
    } finally {
      setIsAsking(false);
    }
  };

  return (
    <div className="module-container" style={{ display: 'flex', flexDirection: 'column' }}>
      <div className="module-header" style={{ flexShrink: 0 }}>
        <h1 style={{ display: 'flex', alignItems: 'center', gap: '16px', fontSize: '32px' }}>
          <FiMessageSquare className="accent-text" /> Sia RAG Knowledge Base
        </h1>
        <p className="subtitle" style={{ fontSize: '22px' }}>Interactive AI Q&A grounded in your verified scraped data.</p>
        
        {jobId && (
          <div style={{ marginTop: '24px' }}>
            <button className="secondary-btn" onClick={handleIndex} disabled={isIndexing} style={{ fontSize: '18px', padding: '12px 24px' }}>
              <FiDatabase /> {isIndexing ? 'Indexing...' : 'Index to ChromaDB Vector Store'}
            </button>
            {indexStatus && <span style={{ marginLeft: '16px', fontSize: '18px', color: '#10b981' }}>{indexStatus}</span>}
          </div>
        )}
      </div>

      <div className="module-content" style={{ display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0, padding: 0 }}>
        <div style={{ flex: 1, overflowY: 'auto', padding: '32px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {!jobId && (
            <div className="glass-panel" style={{ textAlign: 'center', padding: '32px', color: '#f59e0b' }}>
              <h2>No active job context</h2>
              <p>Please run a scrape job first to enable semantic search on its data.</p>
            </div>
          )}
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
              <div style={{ fontSize: '20px', lineHeight: '1.5' }}>{msg.content}</div>
              {msg.citations && msg.citations.length > 0 && (
                <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                  <div style={{ fontSize: '16px', opacity: 0.6, marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <FiLink /> Source Citations
                  </div>
                  {msg.citations.map((c, i) => (
                    <div key={i} style={{ backgroundColor: 'rgba(0,0,0,0.2)', padding: '12px', borderRadius: '8px', fontSize: '16px' }}>
                      <div style={{ color: '#38bdf8', marginBottom: '4px' }}>Row Index: {c.row_index}</div>
                      <div style={{ opacity: 0.8 }}>"{c.text}"</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        <div style={{ padding: '24px', backgroundColor: 'rgba(0,0,0,0.2)', borderTop: '1px solid rgba(255,255,255,0.08)', flexShrink: 0 }}>
          <div className="input-group" style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
            <input 
              type="text" 
              className="glass-input" 
              style={{ flex: 1, padding: '20px', fontSize: '22px', borderRadius: '9999px' }}
              placeholder={isAsking ? "Sia is thinking..." : "Ask a question about your scraped data..."} 
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !isAsking && handleSend()}
              disabled={!jobId || isAsking}
            />
            <button 
              className="primary-btn" 
              onClick={handleSend} 
              disabled={!jobId || !input.trim() || isAsking} 
              style={{ width: '64px', height: '64px', padding: 0, display: 'flex', justifyContent: 'center', alignItems: 'center', borderRadius: '50%' }}
            >
              <FiSend size={28} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
