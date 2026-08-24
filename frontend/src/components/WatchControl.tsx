import React, { useEffect, useState, useRef } from 'react';
import { FiPlay, FiPause, FiTrash2, FiChevronDown, FiChevronUp } from 'react-icons/fi';
import gsap from 'gsap';

interface WatchJob {
  watch_job_id: string;
  mode: string;
  sources: any;
  status: string;
  interval_seconds: number;
  total_cycles: number;
  estimated_credits_per_hour: number;
  last_run_at: string | null;
  next_run_at: string | null;
  last_diff: string | null;
  last_avg_karma: number | null;
}

export default function WatchControl() {
  const [watches, setWatches] = useState<WatchJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [mode, setMode] = useState<'links' | 'keyword'>('links');
  const [input, setInput] = useState('');
  const [expandedJobId, setExpandedJobId] = useState<string | null>(null);
  const [jobDetails, setJobDetails] = useState<any>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      gsap.fromTo(
        containerRef.current,
        { opacity: 0 },
        { opacity: 1, duration: 0.45, ease: 'power1.out', clearProps: 'opacity' }
      );
    }
  }, []);

  const toggleExpand = async (id: string) => {
    if (expandedJobId === id) {
      setExpandedJobId(null);
      setJobDetails(null);
    } else {
      setExpandedJobId(id);
      setJobDetails(null);
      try {
        const res = await fetch(`http://localhost:8000/api/watch/${id}`);
        const data = await res.json();
        setJobDetails(data);
      } catch (err) {
        console.error(err);
      }
    }
  };

  const fetchWatches = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/watch');
      const data = await res.json();
      setWatches(data.watches || []);
      setLoading(false);
    } catch (err) {
      console.error(err);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWatches();
    const interval = setInterval(fetchWatches, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleCreate = async () => {
    if (!input.trim()) return;
    try {
      const payload = mode === 'links' ? { mode, urls: input.split(',').map(s => s.trim()) } : { mode, query: input };
      await fetch('http://localhost:8000/api/watch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      setInput('');
      fetchWatches();
    } catch (err) {
      console.error(err);
    }
  };

  const handleAction = async (id: string, action: 'pause' | 'resume' | 'delete') => {
    try {
      if (action === 'delete') {
        if (!window.confirm('Delete this watch job?')) return;
        await fetch(`http://localhost:8000/api/watch/${id}`, { method: 'DELETE' });
      } else {
        await fetch(`http://localhost:8000/api/watch/${id}/${action}`, { method: 'POST' });
      }
      fetchWatches();
    } catch (err) {
      console.error(err);
    }
  };

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
      <div className="module-header" style={{ marginBottom: '24px' }}>
        <h1 style={{ display: 'flex', alignItems: 'center', gap: '16px', fontSize: '32px' }}>
          Automate Tracking
        </h1>
        <p className="subtitle" style={{ fontSize: '16px', opacity: 0.7, marginTop: '6px' }}>Schedule automated monitors to watch target links and keyword topics.</p>
      </div>
      
      <div className="chat-widget-body" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', gap: '8px', padding: '4px', background: 'var(--glass-bg-heavy)', borderRadius: '9999px' }}>
          <button onClick={() => setMode('links')} style={{ flex: 1, padding: '10px', borderRadius: '9999px', border: 'none', background: mode === 'links' ? 'var(--glass-bg-active)' : 'transparent', color: mode === 'links' ? 'var(--color-text-primary)' : 'var(--glass-text-muted)', cursor: 'pointer', fontSize: 'var(--font-size-md)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
            Exact Links
          </button>
          <button onClick={() => setMode('keyword')} style={{ flex: 1, padding: '10px', borderRadius: '9999px', border: 'none', background: mode === 'keyword' ? 'var(--glass-bg-active)' : 'transparent', color: mode === 'keyword' ? 'var(--color-text-primary)' : 'var(--glass-text-muted)', cursor: 'pointer', fontSize: 'var(--font-size-md)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
            Keyword Query
          </button>
        </div>

        <div style={{ padding: '12px 16px', borderRadius: '9999px', display: 'flex', alignItems: 'center', backgroundColor: 'var(--glass-bg-heavy)', border: '1px solid var(--glass-border)' }}>
          <input 
            type="text" 
            placeholder={mode === 'links' ? "https://site1.com, https://site2.com" : "Enter topic to track (e.g. AI News)"}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            style={{ flex: 1, background: 'transparent', border: 'none', color: 'var(--color-text-primary)', outline: 'none', fontSize: 'var(--font-size-md)' }}
            onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
          />
          <button onClick={handleCreate} style={{ marginLeft: '16px', background: 'var(--color-accent)', color: '#000', border: 'none', borderRadius: '9999px', padding: '8px 24px', fontWeight: '500', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', fontSize: 'var(--font-size-md)' }}>
            Start
          </button>
        </div>

        {loading ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '16px' }}>
            <div className="skeleton-box" style={{ width: '100%', height: '64px', borderRadius: '20px' }} />
            <div className="skeleton-box" style={{ width: '100%', height: '64px', borderRadius: '20px' }} />
          </div>
        ) : watches.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '8px' }}>
            <div style={{ fontSize: 'var(--font-size-sm)', fontWeight: '600', color: 'var(--glass-text-muted)', paddingBottom: '8px', borderBottom: '1px solid var(--glass-border)' }}>Active Trackers</div>
            {watches.map(w => (
              <React.Fragment key={w.watch_job_id}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 16px', background: 'var(--glass-bg-hover)', border: '1px solid var(--glass-border)', borderRadius: '24px' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    <div style={{ fontWeight: '500', fontSize: 'var(--font-size-md)', color: 'var(--color-text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: w.status === 'running' ? '#10b981' : '#f59e0b' }} />
                      {w.mode === 'links' ? (w.sources?.[0] || 'Link Watcher') : (w.sources || 'Keyword Watcher')}
                    </div>
                    <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--glass-text-muted)', display: 'flex', gap: '12px' }}>
                      <span>{w.total_cycles} cycles</span>
                      <span>{w.interval_seconds}s int</span>
                      {w.last_diff && <span style={{ color: 'var(--color-accent)' }}>Changes detected</span>}
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button onClick={() => toggleExpand(w.watch_job_id)} style={{ background: 'transparent', border: 'none', color: '#c2e7ff', cursor: 'pointer', padding: '8px', borderRadius: '8px', backgroundColor: 'rgba(194,231,255,0.1)' }}>
                      {expandedJobId === w.watch_job_id ? <FiChevronUp size={24} /> : <FiChevronDown size={24} />}
                    </button>
                    {w.status === 'running' ? (
                      <button onClick={() => handleAction(w.watch_job_id, 'pause')} style={{ background: 'transparent', border: 'none', color: '#f59e0b', cursor: 'pointer', padding: '8px', borderRadius: '8px', backgroundColor: 'rgba(245,158,11,0.1)' }}><FiPause size={24} /></button>
                    ) : (
                      <button onClick={() => handleAction(w.watch_job_id, 'resume')} style={{ background: 'transparent', border: 'none', color: '#10b981', cursor: 'pointer', padding: '8px', borderRadius: '8px', backgroundColor: 'rgba(16,185,129,0.1)' }}><FiPlay size={24} /></button>
                    )}
                    <button onClick={() => handleAction(w.watch_job_id, 'delete')} style={{ background: 'transparent', border: 'none', color: '#ef4444', cursor: 'pointer', padding: '8px', borderRadius: '8px', backgroundColor: 'rgba(239,68,68,0.1)' }}><FiTrash2 size={24} /></button>
                  </div>
                </div>
                {expandedJobId === w.watch_job_id && (
                  <div style={{ padding: '16px', background: 'var(--glass-bg-heavy)', border: '1px solid var(--glass-border)', borderRadius: '24px', marginTop: '-8px' }}>
                    {jobDetails ? (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        <div style={{ fontSize: 'var(--font-size-md)', fontWeight: 'bold', color: 'var(--color-text-primary)' }}>Scrape Cycle History</div>
                        {jobDetails.cycles && jobDetails.cycles.length > 0 ? (
                          jobDetails.cycles.map((c: any) => (
                            <div key={c.cycle_number} style={{ padding: '12px', background: 'var(--glass-bg-hover)', borderRadius: '16px', borderLeft: '3px solid #10b981' }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                <span style={{ fontWeight: '500', color: 'var(--color-text-primary)', fontSize: 'var(--font-size-sm)' }}>Cycle {c.cycle_number}</span>
                                <span style={{ color: 'var(--glass-text-muted)', fontSize: 'var(--font-size-sm)' }}>{new Date(c.run_at).toLocaleTimeString()}</span>
                              </div>
                              <div style={{ color: 'var(--color-text-primary)', fontSize: 'var(--font-size-sm)' }}>
                                {c.diff_summary 
                                  ? (typeof c.diff_summary === 'object' 
                                      ? `Changes: ${c.diff_summary.new || 0} new, ${c.diff_summary.removed || 0} removed, ${c.diff_summary.changed || 0} changed.` 
                                      : c.diff_summary)
                                  : 'No new changes detected.'}
                              </div>
                            </div>
                          ))
                        ) : (
                          <div style={{ color: 'var(--glass-text-muted)', fontSize: 'var(--font-size-sm)' }}>No cycles completed yet...</div>
                        )}
                      </div>
                    ) : (
                      <div style={{ color: 'var(--glass-text-muted)', fontSize: 'var(--font-size-sm)' }}>Loading details...</div>
                    )}
                  </div>
                )}
              </React.Fragment>
            ))}
          </div>
        )}

      </div>
    </div>
  );
}
