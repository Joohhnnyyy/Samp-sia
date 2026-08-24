import React, { useEffect, useState } from 'react';
import { API_BASE_URL } from '../config';

interface Connector {
  id: string;
  name: string;
  category: string;
  description: string;
  example_url: string;
  fields: string[];
}

interface RecentChatsProps {
  onSelectPreset?: (preset: Connector) => void;
}

export default function RecentChats({ onSelectPreset }: RecentChatsProps) {
  const [connectors, setConnectors] = useState<Connector[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/connectors`)
      .then(res => res.json())
      .then(data => {
        setConnectors(data.connectors.slice(0, 4)); // Only grab first 4 as requested
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load connectors", err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="recent-chats">
      <h3>Executive Landing & Preset Idea Gallery</h3>
      <div className="cards-grid">
        {loading ? (
          <>
            <div className="chat-card skeleton"></div>
            <div className="chat-card skeleton"></div>
            <div className="chat-card skeleton"></div>
            <div className="chat-card skeleton"></div>
          </>
        ) : (
          connectors.map(conn => (
            <div 
              key={conn.id} 
              className="chat-card" 
              style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', gap: '8px' }}
              onClick={() => onSelectPreset?.(conn)}
            >
              <div style={{ color: 'var(--color-accent)', fontSize: '12px', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '1px' }}>
                {conn.category}
              </div>
              <h4>{conn.name}</h4>
              <p>{conn.description}</p>
              <span className="date" style={{ marginTop: 'auto', paddingTop: '8px', opacity: 0.7 }}>
                URL: {conn.example_url.split('/')[2]}...
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
