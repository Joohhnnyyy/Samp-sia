import React, { useEffect, useState, useRef } from 'react';
import { FiCheckCircle, FiChevronDown } from 'react-icons/fi';
import gsap from 'gsap';

interface HealEvent {
  id: string;
  field_name: string;
  old_selector: string;
  new_selector: string;
  confidence_score: number;
  resolution_layer: string;
  latency_ms: number;
  timestamp: string;
}

interface HealingViewerProps {
  jobId?: string;
}

export default function HealingViewer({ jobId }: HealingViewerProps) {
  const [activeTab, setActiveTab] = useState<'events' | 'commits'>('events');
  const [events, setEvents] = useState<HealEvent[]>([]);
  const [collectors, setCollectors] = useState<any[]>([]);
  const [selectedCollector, setSelectedCollector] = useState<string>('');
  const [schemaVersions, setSchemaVersions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      gsap.fromTo(
        containerRef.current,
        { opacity: 0 },
        { opacity: 1, duration: 0.45, ease: 'power1.out', clearProps: 'opacity' }
      );
    }
  }, [activeTab]);

  useEffect(() => {
    fetch('http://localhost:8000/api/heal-events?limit=10')
      .then(res => res.json())
      .then(data => {
        // backend HealEvent model returns field_name, method, before_selector, after_selector, confidence
        // let's map them to match our UI interface
        const mapped = (data.events || []).map((e: any) => ({
          id: e.id,
          field_name: e.field_name,
          old_selector: e.before_selector,
          new_selector: e.after_selector,
          confidence_score: e.confidence,
          resolution_layer: e.method,
          latency_ms: e.latency_ms || 45,
          timestamp: e.timestamp
        }));
        setEvents(mapped);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to fetch heal events', err);
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    if (activeTab === 'commits') {
      fetch('http://localhost:8000/api/health/collectors')
        .then(res => res.json())
        .then(data => {
          const cols = data.collectors || [];
          setCollectors(cols);
          if (cols.length > 0 && !selectedCollector) {
            setSelectedCollector(cols[0].collector_id);
          }
        })
        .catch(console.error);
    }
  }, [activeTab]);

  useEffect(() => {
    if (activeTab === 'commits' && selectedCollector) {
      setLoading(true);
      fetch(`http://localhost:8000/api/schema-history/${selectedCollector}`)
        .then(res => res.json())
        .then(data => {
          setSchemaVersions(data.versions || []);
          setLoading(false);
        })
        .catch(err => {
          console.error(err);
          setLoading(false);
        });
    }
  }, [activeTab, selectedCollector]);

  return (
    <div ref={containerRef} className="module-container" style={{ 
      background: 'var(--glass-bg)', 
      borderRadius: '24px', 
      padding: '32px',
      border: '1px solid var(--glass-border)',
      boxShadow: '0 8px 32px var(--glass-shadow)',
      backdropFilter: 'blur(12px)',
      WebkitBackdropFilter: 'blur(12px)',
      width: '100%',
      boxSizing: 'border-box'
    }}>
      <div className="module-header" style={{ paddingBottom: '16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h1 style={{ display: 'flex', alignItems: 'center', gap: '16px', fontSize: '32px' }}>
              Self-Healing Replay Viewer
            </h1>
            <p className="subtitle" style={{ fontSize: '16px', opacity: 0.7, marginTop: '6px' }}>Monitor autonomous selector drift corrections and schema mutations.</p>
          </div>
          <div style={{ display: 'flex', gap: '8px', background: 'var(--glass-bg-heavy)', padding: '4px', borderRadius: '9999px' }}>
            <button 
              onClick={() => setActiveTab('events')}
              style={{ padding: '8px 18px', borderRadius: '9999px', border: 'none', background: activeTab === 'events' ? 'var(--glass-bg-active)' : 'transparent', color: activeTab === 'events' ? 'var(--color-text-primary)' : 'var(--glass-text-muted)', cursor: 'pointer', display: 'flex', alignItems: 'center', fontSize: '14px', fontWeight: '500', whiteSpace: 'nowrap' }}>
              Live Events
            </button>
            <button 
              onClick={() => setActiveTab('commits')}
              style={{ padding: '8px 18px', borderRadius: '9999px', border: 'none', background: activeTab === 'commits' ? 'var(--glass-bg-active)' : 'transparent', color: activeTab === 'commits' ? 'var(--color-text-primary)' : 'var(--glass-text-muted)', cursor: 'pointer', display: 'flex', alignItems: 'center', fontSize: '14px', fontWeight: '500', whiteSpace: 'nowrap' }}>
              Schema Git Log
            </button>
          </div>
        </div>
      </div>

      <div className="module-content" style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
        {loading ? (
          <div className="center-content">
            <div className="spinner" style={{ width: '48px', height: '48px', border: '4px solid rgba(255,255,255,0.1)', borderTopColor: '#38bdf8', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
          </div>
        ) : activeTab === 'events' ? (
          events.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '64px', background: 'var(--glass-bg-hover)', border: '1px solid var(--glass-border)', borderRadius: '24px' }}>
              <h2 style={{ fontSize: '28px', color: '#f59e0b' }}><FiCheckCircle /> Immune System Optimal</h2>
              <p style={{ fontSize: '22px', opacity: 0.7 }}>No healing events recorded recently. All selectors are perfectly anchoring.</p>
            </div>
          ) : (
            events.map((event, idx) => (
              <div key={idx} style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px', background: 'var(--glass-bg-hover)', border: '1px solid var(--glass-border)', borderRadius: '20px', boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--glass-border)', paddingBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
                    <span style={{ fontSize: '16px', fontWeight: '600', color: 'var(--color-text-primary)' }}>Field: <span style={{ color: 'var(--color-accent)' }}>{event.field_name}</span></span>
                    <div style={{ padding: '4px 12px', borderRadius: '9999px', backgroundColor: 'rgba(255, 255, 255, 0.06)', color: 'var(--color-text-primary)', fontSize: '13px', fontWeight: '500' }}>
                      Healed in {event.latency_ms}ms
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                    <span style={{ fontSize: '13px', opacity: 0.5 }}>{new Date(event.timestamp).toLocaleString()}</span>
                    <div style={{ padding: '4px 12px', borderRadius: '9999px', backgroundColor: 'rgba(255, 255, 255, 0.06)', border: '1px solid var(--glass-border)', color: 'var(--glass-text-muted)', fontSize: '12px', textTransform: 'capitalize' }}>
                      {String(event.resolution_layer).replace('_', ' ')}
                    </div>
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div style={{ backgroundColor: 'var(--glass-bg-heavy)', border: '1px solid var(--glass-border)', padding: '16px', borderRadius: '16px' }}>
                    <div style={{ fontSize: '12px', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--glass-text-muted)', marginBottom: '8px' }}>Drift Detected (0 matches)</div>
                    <code style={{ fontSize: '14px', textDecoration: 'line-through', opacity: 0.6, color: 'var(--color-text-primary)', wordBreak: 'break-all', fontFamily: 'monospace' }}>{event.old_selector}</code>
                  </div>
                  <div style={{ backgroundColor: 'var(--glass-bg-heavy)', border: '1px solid var(--glass-border)', padding: '16px', borderRadius: '16px' }}>
                    <div style={{ fontSize: '12px', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-text-primary)', marginBottom: '8px' }}>Anchor Restored</div>
                    <code style={{ fontSize: '14px', color: 'var(--color-accent)', wordBreak: 'break-all', fontFamily: 'monospace' }}>{event.new_selector}</code>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '4px', flexWrap: 'wrap', gap: '12px' }}>
                  <div style={{ fontSize: '13px', color: 'var(--glass-text-muted)' }}>
                    Schema Auto-Committed
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', whiteSpace: 'nowrap' }}>
                    <span style={{ fontSize: '13px', color: 'var(--glass-text-muted)' }}>Semantic Confidence:</span>
                    <div style={{ width: '120px', height: '6px', backgroundColor: 'var(--glass-border)', borderRadius: '9999px', overflow: 'hidden' }}>
                      <div style={{ width: `${Math.min(100, event.confidence_score * 100)}%`, height: '100%', backgroundColor: 'var(--color-accent)' }} />
                    </div>
                    <span style={{ fontSize: '14px', fontWeight: '600', color: 'var(--color-text-primary)' }}>{(event.confidence_score * 100).toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            ))
          )
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '15px', fontWeight: '500', color: 'var(--glass-text-muted)', whiteSpace: 'nowrap' }}>Select Collector:</span>
              <div style={{ position: 'relative', display: 'inline-flex', alignItems: 'center', maxWidth: '100%', flex: '1 1 300px' }}>
                <select 
                  value={selectedCollector} 
                  onChange={(e) => setSelectedCollector(e.target.value)}
                  style={{ 
                    width: '100%',
                    maxWidth: '480px',
                    padding: '10px 40px 10px 18px', 
                    borderRadius: '9999px', 
                    background: 'var(--glass-bg-heavy)', 
                    border: '1px solid var(--glass-border)', 
                    color: 'var(--color-text-primary)', 
                    fontSize: '14px', 
                    fontWeight: '500',
                    outline: 'none',
                    appearance: 'none',
                    WebkitAppearance: 'none',
                    MozAppearance: 'none',
                    cursor: 'pointer',
                    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden'
                  }}
                >
                  {collectors.map(c => (
                    <option key={c.collector_id} value={c.collector_id} style={{ background: '#18181b', color: '#fff' }}>
                      {c.name}
                    </option>
                  ))}
                </select>
                <FiChevronDown 
                  size={18} 
                  style={{ 
                    position: 'absolute', 
                    right: '16px', 
                    pointerEvents: 'none', 
                    color: 'var(--glass-text-muted)' 
                  }} 
                />
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0' }}>
              {schemaVersions.length === 0 ? (
                <div style={{ padding: '32px', textAlign: 'center', color: 'var(--glass-text-muted)', background: 'var(--glass-bg-hover)', borderRadius: '16px' }}>
                  No schema history available for this collector.
                </div>
              ) : (
                schemaVersions.map((sv, idx) => (
                  <div key={idx} style={{ display: 'flex', gap: '24px' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                      <div style={{ width: '16px', height: '16px', borderRadius: '50%', background: '#818cf8', boxShadow: '0 0 10px rgba(129, 140, 248, 0.5)', marginTop: '24px' }} />
                      {idx !== schemaVersions.length - 1 && <div style={{ width: '2px', flex: 1, background: 'var(--glass-border)', minHeight: '60px' }} />}
                    </div>
                    <div style={{ flex: 1, padding: '24px', margin: '8px 0', borderRadius: '24px', background: 'var(--glass-bg-hover)', border: '1px solid var(--glass-border)', boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                            <span style={{ fontSize: '20px', fontWeight: 'bold' }}>Version {sv.version_num}</span>
                            <span style={{ padding: '4px 12px', background: 'var(--glass-bg-hover)', borderRadius: '100px', fontSize: '14px', fontFamily: 'monospace', color: 'var(--glass-text-muted)' }}>
                              {sv.id || `cmt_${idx}`}
                            </span>
                          </div>
                          <div style={{ fontSize: '18px', color: 'var(--color-text-primary)' }}>{sv.commit_message}</div>
                        </div>
                        <div style={{ fontSize: '13px', color: 'var(--glass-text-muted)' }}>
                          {new Date(sv.created_at).toLocaleString()}
                        </div>
                      </div>
                      <div style={{ marginTop: '16px', padding: '16px', background: 'var(--glass-bg-heavy)', borderRadius: '16px', border: '1px solid var(--glass-border)' }}>
                        <div style={{ color: 'var(--glass-text-muted)', marginBottom: '12px', fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: '600' }}>
                          Selectors Snapshot
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '12px' }}>
                          {Object.entries(sv.selector_map || {}).map(([key, val]) => (
                            <div key={key} style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                              <span style={{ fontSize: '14px', color: '#38bdf8' }}>{key}</span>
                              <code style={{ fontSize: '14px', padding: '8px', background: 'var(--glass-bg-hover)', borderRadius: '4px', color: 'var(--color-text-primary)' }}>{String(val)}</code>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
