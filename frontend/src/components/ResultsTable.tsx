import React, { useEffect, useState, useRef } from 'react';
import { FiDownload, FiMessageSquare } from 'react-icons/fi';
import gsap from 'gsap';

interface ScrapedRow {
  data: Record<string, any>;
  karma_score: number;
}

interface JobData {
  id: string;
  url: string;
  status: string;
  avg_karma_score: number;
  extracted_rows: ScrapedRow[];
}

interface ResultsTableProps {
  jobId?: string;
}

export default function ResultsTable({ jobId }: ResultsTableProps) {
  const [job, setJob] = useState<JobData | null>(null);
  const [loading, setLoading] = useState(true);
  const [simulating, setSimulating] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      gsap.fromTo(
        containerRef.current,
        { opacity: 0 },
        { opacity: 1, duration: 0.45, ease: 'power1.out', clearProps: 'opacity' }
      );
    }
  }, [job]);

  useEffect(() => {
    const fetchJobData = async () => {
      try {
        let targetJobId = jobId;
        
        if (!targetJobId) {
          // Fetch the most recent job from the backend if none provided
          const listRes = await fetch('http://localhost:8000/api/scrape/jobs?limit=1');
          if (listRes.ok) {
            const list = await listRes.json();
            if (list && list.length > 0) {
              targetJobId = list[0].id;
            }
          }
        }
        
        if (!targetJobId) {
          setLoading(false);
          return;
        }

        const res = await fetch(`http://localhost:8000/api/jobs/${targetJobId}`);
        if (!res.ok) throw new Error('Not found');
        
        const data = await res.json();
        if (data && data.status) {
          // Backend returns "rows", map it to "extracted_rows" for our UI components
          data.extracted_rows = data.rows || [];
          setJob(data);
        }
        setLoading(false);
      } catch (err) {
        console.error('Failed to fetch job results', err);
        setLoading(false);
      }
    };

    fetchJobData();
  }, [jobId]);

  const handleExport = (format: string) => {
    if (!job) return;
    window.open(`http://localhost:8000/api/export/${job.id}?format=${format}`, '_blank');
  };

  const handleSimulateBreakage = async () => {
    if (!job) return;
    setSimulating(true);
    try {
      const res = await fetch(`http://localhost:8000/api/dev/simulate-site-change/${job.id}`, { method: 'POST' });
      if (!res.ok) throw new Error('Simulation failed');
      // The WebSocket will handle the streaming of the self-healing events
    } catch (err) {
      console.error(err);
      alert('Failed to simulate site change.');
    } finally {
      setSimulating(false);
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
      <div className="module-header" style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1 style={{ display: 'flex', alignItems: 'center', gap: '16px', fontSize: '32px' }}>
            Scrape Results
          </h1>
          <p className="subtitle" style={{ fontSize: '16px', opacity: 0.7, marginTop: '6px' }}>Extracted data payload and karma trust verification.</p>
        </div>
        {job && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--color-text-primary)', fontSize: '13px', fontWeight: '500', background: 'var(--glass-bg-hover)', border: '1px solid var(--glass-border)', padding: '6px 16px', borderRadius: '9999px' }}>
            Karma Trust: {job.avg_karma_score.toFixed(1)}
          </div>
        )}
      </div>

      <div className="module-content">
        {loading ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', padding: '16px 0' }}>
            <div className="skeleton-box" style={{ width: '100%', height: '40px', borderRadius: '12px' }} />
            <div className="skeleton-box" style={{ width: '100%', height: '52px', borderRadius: '12px' }} />
            <div className="skeleton-box" style={{ width: '100%', height: '52px', borderRadius: '12px' }} />
            <div className="skeleton-box" style={{ width: '100%', height: '52px', borderRadius: '12px' }} />
          </div>
        ) : !job ? (
          <div style={{ textAlign: 'center', padding: '48px 24px', background: 'var(--glass-bg-hover)', borderRadius: '20px', border: '1px dashed var(--glass-border)' }}>
            <div style={{ fontSize: '16px', fontWeight: '600', color: 'var(--color-text-primary)', marginBottom: '8px' }}>
              Awaiting Intelligence
            </div>
            <p style={{ fontSize: '14px', opacity: 0.6, margin: 0, color: 'var(--color-text-primary)' }}>No data payload available yet. Run an autonomous scrape job to begin.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              <button onClick={() => handleExport('json')} style={{ flex: 1, padding: '8px', background: 'var(--glass-bg-hover)', border: 'none', borderRadius: '9999px', color: 'var(--color-text-primary)', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', fontSize: '12px' }}>
                <FiDownload /> JSON
              </button>
              <button onClick={() => handleExport('csv')} style={{ flex: 1, padding: '8px', background: 'var(--glass-bg-hover)', border: 'none', borderRadius: '9999px', color: 'var(--color-text-primary)', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', fontSize: '12px' }}>
                <FiDownload /> CSV
              </button>
              <button onClick={() => handleExport('markdown')} style={{ flex: 1, padding: '8px', background: 'var(--glass-bg-hover)', border: 'none', borderRadius: '9999px', color: 'var(--color-text-primary)', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', fontSize: '12px' }}>
                <FiDownload /> Markdown
              </button>
            </div>

            <button 
              onClick={handleSimulateBreakage}
              disabled={simulating}
              style={{ width: '100%', padding: '10px', background: 'rgba(244, 63, 94, 0.1)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: '9999px', color: '#f43f5e', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', cursor: simulating ? 'not-allowed' : 'pointer', fontSize: '13px', fontWeight: '500' }}>
              {simulating ? <div className="spinner" style={{ width: '14px', height: '14px', border: '2px solid rgba(244, 63, 94, 0.1)', borderTopColor: '#f43f5e', borderRadius: '50%', animation: 'spin 1s linear infinite' }} /> : ' Simulate Site Breakage (Hero Feature)'}
            </button>

            <div style={{ maxHeight: '300px', overflowY: 'auto', background: 'var(--glass-bg-heavy)', borderRadius: '16px', border: '1px solid var(--glass-border)' }}>
              {job.extracted_rows.length === 0 ? (
                <div style={{ padding: '16px', textAlign: 'center', color: 'var(--glass-text-muted)' }}>No rows extracted.</div>
              ) : (
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                  <thead style={{ background: 'var(--glass-bg-hover)' }}>
                    <tr>
                      {Object.keys(job.extracted_rows[0].data).map((k) => (
                        <th key={k} style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid var(--glass-border)', color: 'var(--glass-text-muted)', fontWeight: '500' }}>{k}</th>
                      ))}
                      <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid var(--glass-border)', color: 'var(--glass-text-muted)', fontWeight: '500' }}>Karma</th>
                    </tr>
                  </thead>
                  <tbody>
                    {job.extracted_rows.map((row, i) => (
                      <tr key={i} style={{ borderBottom: '1px solid var(--glass-border)' }}>
                        {Object.values(row.data).map((val: any, j) => (
                          <td key={j} style={{ padding: '12px', color: 'var(--color-text-primary)' }}>
                            {typeof val === 'object' ? JSON.stringify(val) : String(val)}
                          </td>
                        ))}
                        <td style={{ padding: '12px', color: '#10b981', fontWeight: '500' }}>{row.karma_score}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
            
            <button style={{ width: '100%', padding: '10px', background: 'transparent', border: '1px solid var(--glass-border-highlight)', borderRadius: '9999px', color: 'var(--color-text-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', cursor: 'pointer', fontSize: '13px' }}>
              <FiMessageSquare /> Ask Sia About This Data
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
