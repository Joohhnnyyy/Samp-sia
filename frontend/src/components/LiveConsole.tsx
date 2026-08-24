import React, { useEffect, useState, useRef } from 'react';
import gsap from 'gsap';

interface LiveConsoleProps {
  jobId: string | null;
  onComplete?: (data: any) => void;
}

export default function LiveConsole({ jobId, onComplete }: LiveConsoleProps) {
  const [logs, setLogs] = useState<string[]>([]);
  const [status, setStatus] = useState<string>('connecting');
  const logsEndRef = useRef<HTMLDivElement>(null);
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

  useEffect(() => {
    if (!jobId) return;

    setLogs([`[INFO] Initializing secure connection to Sia Telemetry...`, `[INFO] Connecting to ws://localhost:8000/ws/jobs/${jobId}...`]);
    setStatus('connecting');

    const ws = new WebSocket(`ws://localhost:8000/ws/jobs/${jobId}`);

    ws.onopen = () => {
      setStatus('connected');
      setLogs(prev => [...prev, `[INFO] WebSocket Connected.`]);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'log') {
          const level = (data.level || 'INFO').toUpperCase();
          setLogs(prev => [...prev, `[${level}] ${data.message}`]);
        } else if (data.type === 'progress') {
          setLogs(prev => [...prev, `[PROGRESS] ${data.percent}% - ${data.message}`]);
        } else if (data.type === 'done' || data.type === 'result') {
          setLogs(prev => [...prev, `[SUCCESS] ${data.message || 'Job completed successfully!'}`]);
          if (onComplete) onComplete(data);
        } else {
          setLogs(prev => [...prev, event.data]);
        }
      } catch (e) {
        setLogs(prev => [...prev, event.data]);
      }
    };

    ws.onerror = (error) => {
      setStatus('error');
      setLogs(prev => [...prev, `[ERROR] WebSocket error occurred.`]);
    };

    ws.onclose = () => {
      setStatus('closed');
      setLogs(prev => [...prev, `[INFO] WebSocket Connection Closed.`]);
    };

    return () => {
      ws.close();
    };
  }, [jobId]);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const getLogColor = (log: string) => {
    if (log.includes('[ERROR]')) return '#f43f5e';
    if (log.includes('[WARN]')) return '#f59e0b';
    if (log.includes('[HEAL]')) return '#38bdf8';
    if (log.includes('[SUCCESS]') || log.includes('successfully')) return '#10b981';
    return '#e2e8f0';
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
            Live Console
          </h1>
          <p className="subtitle" style={{ fontSize: '16px', opacity: 0.7, marginTop: '6px' }}>Real-time telemetry and execution logs for active worker jobs.</p>
        </div>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '8px', 
          padding: '8px 16px', 
          borderRadius: '9999px', 
          backgroundColor: status === 'connected' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(255, 255, 255, 0.05)',
          color: status === 'connected' ? '#10b981' : 'var(--glass-text-muted)',
          fontSize: '13px',
          fontWeight: '600',
          letterSpacing: '0.05em',
          textTransform: 'uppercase',
          border: '1px solid var(--glass-border)'
        }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: status === 'connected' ? '#10b981' : '#888' }}></span>
          {status}
        </div>
      </div>
      
      <div className="module-content" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ fontSize: '15px', color: 'var(--glass-text-muted)' }}>
            Job ID: <span style={{ color: 'var(--color-accent)', fontWeight: '600', fontFamily: 'monospace' }}>{jobId || 'No active job'}</span>
          </div>
        </div>
        
        <div style={{ 
          height: '320px', 
          backgroundColor: 'rgba(0, 0, 0, 0.4)', 
          borderRadius: '16px', 
          padding: '20px', 
          fontFamily: '"JetBrains Mono", SFMono-Regular, Menlo, Monaco, Consolas, monospace', 
          color: '#e2e8f0', 
          overflowY: 'auto',
          border: '1px solid var(--glass-border)',
          boxShadow: 'inset 0 4px 20px rgba(0,0,0,0.3)',
          fontSize: '14px',
          lineHeight: '1.6'
        }}>
          {logs.map((log, index) => (
            <div key={index} style={{ marginBottom: '6px', color: getLogColor(log) }}>
              {log}
            </div>
          ))}
          <div ref={logsEndRef} />
        </div>
      </div>
    </div>
  );
}
