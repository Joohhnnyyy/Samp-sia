import React, { useState, useEffect, useRef } from 'react';
import { FiArrowUpRight, FiArrowDownRight, FiCheckCircle, FiAlertTriangle, FiRefreshCw } from 'react-icons/fi';
import { API_BASE_URL } from '../config';
import gsap from 'gsap';

interface CollectorHealth {
  collector_id: string;
  name: string;
  target_url: string;
  status: string;
  schema_version: number;
  total_runs: number;
  success_rate: number;
  avg_karma_score: number;
  last_updated: string;
}

export default function HealthMonitor() {
  const [collectors, setCollectors] = useState<CollectorHealth[]>([]);
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [runningDiag, setRunningDiag] = useState<string | null>(null);
  const [diagResult, setDiagResult] = useState<{ id: string, status: string, message: string } | null>(null);
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

  const fetchHealth = async () => {
    try {
      const [colRes, evtRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/health/collectors`),
        fetch(`${API_BASE_URL}/api/health/events?limit=10`)
      ]);
      const colData = await colRes.json();
      const evtData = await evtRes.json();
      setCollectors(colData.collectors || []);
      setEvents(evtData.events || []);
    } catch (err) {
      console.error('Failed to fetch health', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleRunDiagnostics = async (collector_id: string) => {
    setRunningDiag(collector_id);
    setDiagResult(null);
    try {
      const response = await fetch(`${API_BASE_URL}/api/health/check/${collector_id}`, { method: 'POST' });
      const data = await response.json();
      setDiagResult({ id: collector_id, status: data.status, message: data.message });
      await fetchHealth();
      
      // Clear the result after 5 seconds
      setTimeout(() => {
        setDiagResult(current => current?.id === collector_id ? null : current);
      }, 5000);
    } catch (err) {
      console.error('Diagnostics failed', err);
      setDiagResult({ id: collector_id, status: 'error', message: 'Diagnostics failed to run' });
      setTimeout(() => setDiagResult(null), 5000);
    } finally {
      setRunningDiag(null);
    }
  };

  // Compute aggregate stats
  const activeCount = collectors.length;
  const avgSuccess = activeCount > 0 
    ? (collectors.reduce((acc, c) => acc + c.success_rate, 0) / activeCount).toFixed(1) 
    : 0;
  const avgKarma = activeCount > 0 
    ? (collectors.reduce((acc, c) => acc + c.avg_karma_score, 0) / activeCount).toFixed(1) 
    : 0;
  const totalRuns = collectors.reduce((acc, c) => acc + c.total_runs, 0);

  const stats = [
    { label: 'Active Collectors', value: activeCount, trend: 'Live', positive: true },
    { label: 'Avg Success Rate', value: `${avgSuccess}%`, trend: '', positive: Number(avgSuccess) > 90 },
    { label: 'Avg Karma Score', value: `${avgKarma}/100`, trend: '', positive: Number(avgKarma) >= 70 },
    { label: 'Total Extractions', value: totalRuns, trend: '', positive: true }
  ];

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
          Fleet Health Monitor
        </h1>
        <p className="subtitle" style={{ fontSize: '16px', opacity: 0.7, marginTop: '6px' }}>Real-time telemetry and extraction drift alerts for all active scrapers.</p>
      </div>
      
      <div className="module-content" style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
        
        {/* Aggregate Stats */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
          {stats.map((stat, i) => (
            <div key={i} className="stat-card-item" style={{ padding: '16px 20px', background: 'var(--glass-bg-hover)', border: '1px solid var(--glass-border)', borderRadius: '24px', display: 'flex', flexDirection: 'column', gap: '12px', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--glass-text-muted)', fontSize: '11px', fontWeight: '600', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
                {stat.label}
              </div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '12px' }}>
                <span style={{ fontSize: '28px', fontWeight: '500', color: 'var(--color-text-primary)', letterSpacing: '-0.02em' }}>{loading ? '-' : stat.value}</span>
                {stat.trend && (
                  <span style={{ fontSize: '13px', display: 'flex', alignItems: 'center', color: stat.positive ? '#10b981' : '#ef4444' }}>
                    {stat.positive ? <FiArrowUpRight /> : <FiArrowDownRight />} {stat.trend}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Collector List */}
        <div>
          <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '12px', color: 'var(--color-text-primary)' }}>Active Scrapers</h3>
          {loading ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {[1, 2, 3].map(i => (
                <div key={i} style={{ padding: '20px', background: 'var(--glass-bg-hover)', border: '1px solid var(--glass-border)', borderRadius: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', flex: 1 }}>
                    <div className="skeleton-box" style={{ width: '180px', height: '18px' }} />
                    <div className="skeleton-box" style={{ width: '320px', height: '14px', opacity: 0.6 }} />
                  </div>
                  <div style={{ display: 'flex', gap: '24px', alignItems: 'center' }}>
                    <div className="skeleton-box" style={{ width: '60px', height: '24px' }} />
                    <div className="skeleton-box" style={{ width: '120px', height: '36px', borderRadius: '9999px' }} />
                  </div>
                </div>
              ))}
            </div>
          ) : collectors.length === 0 ? (
            <div style={{ padding: '24px', textAlign: 'center', color: 'var(--glass-text-muted)', background: 'var(--glass-bg-hover)', borderRadius: '16px' }}>
              No active collectors found.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {collectors.map(c => (
                <div 
                  key={c.collector_id} 
                  style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '16px 20px', background: 'var(--glass-bg-hover)', border: '1px solid var(--glass-border)', borderRadius: '24px', transition: 'all 0.2s ease', gap: '16px' }}
                  onMouseOver={(e) => { e.currentTarget.style.background = 'var(--glass-bg-active)'; e.currentTarget.style.transform = 'translateY(-1px)'; e.currentTarget.style.boxShadow = '0 4px 12px var(--glass-shadow)'; }}
                  onMouseOut={(e) => { e.currentTarget.style.background = 'var(--glass-bg-hover)'; e.currentTarget.style.transform = 'none'; e.currentTarget.style.boxShadow = 'none'; }}
                >
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <span style={{ fontWeight: '500', color: 'var(--color-text-primary)', fontSize: '15px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{c.name}</span>
                      <span style={{ flexShrink: 0, padding: '4px 10px', borderRadius: '12px', fontSize: '10px', fontWeight: '700', letterSpacing: '0.05em', textTransform: 'uppercase', background: c.status === 'active' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)', color: c.status === 'active' ? '#10b981' : '#ef4444' }}>
                        {c.status}
                      </span>
                    </div>
                    <div style={{ fontSize: '13px', color: 'var(--glass-text-muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      <a 
                        href={c.target_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        style={{ color: '#38bdf8', textDecoration: 'none', transition: 'opacity 0.2s' }}
                        onMouseOver={(e) => e.currentTarget.style.opacity = '0.8'}
                        onMouseOut={(e) => e.currentTarget.style.opacity = '1'}
                      >
                        {c.target_url}
                      </a> • {c.total_runs} runs • v{c.schema_version}
                    </div>
                  </div>
                  
                  <div style={{ display: 'flex', alignItems: 'center', gap: '32px', flexShrink: 0 }}>
                    <div style={{ textAlign: 'right', flexShrink: 0 }}>
                      <div style={{ fontSize: '11px', color: 'var(--glass-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '4px', whiteSpace: 'nowrap' }}>Karma Score</div>
                      <div style={{ fontSize: '18px', fontWeight: '500', color: c.avg_karma_score >= 70 ? '#10b981' : '#f59e0b', whiteSpace: 'nowrap' }}>
                        {c.avg_karma_score}<span style={{ fontSize: '13px', opacity: 0.5 }}>/100</span>
                      </div>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '8px', minWidth: '160px' }}>
                      <button 
                        onClick={() => handleRunDiagnostics(c.collector_id)}
                        disabled={runningDiag === c.collector_id}
                        style={{ 
                          padding: '10px 16px', 
                          fontSize: '13px', 
                          display: 'flex', 
                          alignItems: 'center', 
                          gap: '8px',
                          background: 'var(--glass-bg-hover)',
                          border: '1px solid var(--glass-border)',
                          color: 'var(--color-text-primary)',
                          borderRadius: '9999px',
                          cursor: runningDiag === c.collector_id ? 'not-allowed' : 'pointer',
                          transition: 'all 0.2s',
                          fontWeight: '500',
                          width: '100%',
                          justifyContent: 'center'
                        }}
                        onMouseOver={(e) => {
                          if (runningDiag !== c.collector_id) {
                            e.currentTarget.style.background = 'var(--glass-bg-active)';
                          }
                        }}
                        onMouseOut={(e) => {
                          if (runningDiag !== c.collector_id) {
                            e.currentTarget.style.background = 'var(--glass-bg-hover)';
                          }
                        }}
                      >
                        {runningDiag === c.collector_id ? (
                          <>
                            <FiRefreshCw className="spin" style={{ color: '#38bdf8' }} />
                            Checking...
                          </>
                        ) : diagResult?.id === c.collector_id ? (
                          diagResult.status === 'healthy' ? (
                            <>
                              <FiCheckCircle style={{ color: '#10b981' }} />
                              Healthy
                            </>
                          ) : (
                            <>
                              <FiAlertTriangle style={{ color: '#ef4444' }} />
                              {diagResult.status === 'warning' ? 'Warning' : 'Error'}
                            </>
                          )
                        ) : (
                          <>
                            Run Diagnostics
                          </>
                        )}
                      </button>
                      {diagResult?.id === c.collector_id && (
                        <div style={{ fontSize: '11px', color: diagResult.status === 'healthy' ? '#10b981' : '#ef4444', textAlign: 'right', maxWidth: '160px', lineHeight: '1.4' }}>
                          {diagResult.message}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Alert Feed */}
        <div style={{ marginTop: '8px' }}>
          <h1 style={{ display: 'flex', alignItems: 'center', gap: '16px', fontSize: '32px' }}>System Health Alerts</h1>
          <div style={{ maxHeight: '300px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '8px', paddingRight: '4px' }}>
            {events.length === 0 && !loading ? (
              <div style={{ padding: '24px', textAlign: 'center', color: 'var(--glass-text-muted)', background: 'var(--glass-bg-hover)', borderRadius: '16px' }}>
                No recent health events.
              </div>
            ) : (
              events.map((evt, idx) => {
                const isHealthy = evt.status === 'healthy';
                const isWarning = evt.status === 'warning';
                const colorHex = isHealthy ? '#10b981' : isWarning ? '#f59e0b' : '#ef4444';
                const colorRgbaBase = isHealthy ? '16, 185, 129' : isWarning ? '245, 158, 11' : '239, 68, 68';
                
                // Clean up redundant "Collector 'Collector for " from messages
                const cleanMessage = evt.message.replace(/Collector 'Collector for (.*?)'/, "Scraper for $1");

                return (
                  <div key={idx} style={{ 
                    padding: '16px', 
                    background: `rgba(${colorRgbaBase}, 0.05)`, 
                    border: `1px solid rgba(${colorRgbaBase}, 0.2)`, 
                    borderRadius: '24px', 
                    display: 'flex', 
                    alignItems: 'flex-start', 
                    gap: '16px',
                    transition: 'all 0.2s'
                  }}>
                    <div style={{ marginTop: '2px', color: colorHex, fontSize: '18px', filter: `drop-shadow(0 0 8px rgba(${colorRgbaBase}, 0.6))` }}>
                      {isHealthy ? <FiCheckCircle /> : <FiAlertTriangle />}
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: '14.5px', color: 'var(--color-text-primary)', marginBottom: '6px', fontWeight: '500', lineHeight: '1.4' }}>{cleanMessage}</div>
                      <div style={{ fontSize: '12px', color: 'var(--glass-text-muted)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span>{new Date(evt.timestamp).toLocaleString()}</span>
                        <span style={{ width: '4px', height: '4px', borderRadius: '50%', background: 'var(--glass-border-highlight)' }} />
                        <span style={{ fontFamily: 'monospace' }}>{evt.collector_id}</span>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
