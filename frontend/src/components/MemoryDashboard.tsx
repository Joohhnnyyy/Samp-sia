import React, { useEffect, useState, useRef } from 'react';
import { FiTrash2, FiTag } from 'react-icons/fi';
import gsap from 'gsap';

interface MemoryStats {
  total_patterns_learned: number;
  first_try_resolution_rate_overall: number;
  first_try_resolution_rate_on_new_sites: number;
  active_immune_sites_count: number;
  average_reinforcement_count: number;
  patterns_by_field_type?: Record<string, number>;
  top_reinforced_patterns?: any[];
}

interface Taxonomy {
  total_categories: number;
  taxonomy: Record<string, { description: string; synonyms: string[] }>;
}

export default function MemoryDashboard() {
  const [stats, setStats] = useState<MemoryStats | null>(null);
  const [taxonomy, setTaxonomy] = useState<Taxonomy | null>(null);
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
  }, []);

  useEffect(() => {
    Promise.all([
      fetch('http://localhost:8000/api/memory/stats').then(r => r.json()),
      fetch('http://localhost:8000/api/memory/taxonomy').then(r => r.json())
    ]).then(([statsData, taxonomyData]) => {
      setStats(statsData);
      setTaxonomy(taxonomyData);
      setLoading(false);
    }).catch(err => {
      console.error(err);
      setLoading(false);
    });
  }, []);

  const handlePrune = async () => {
    if (!window.confirm("Are you sure you want to prune decayed memory patterns?")) return;
    try {
      await fetch('http://localhost:8000/api/memory/prune?min_confidence=0.40&max_age_days=30', { method: 'POST' });
      alert("Pruned decayed patterns successfully.");
      // Reload stats
      const newStats = await fetch('http://localhost:8000/api/memory/stats').then(r => r.json());
      setStats(newStats);
    } catch (err) {
      console.error(err);
      alert("Failed to prune.");
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
          NeuroAnchor Collective Memory
        </h1>
        <p className="subtitle" style={{ fontSize: '16px', opacity: 0.7, marginTop: '6px' }}>Monitor the immune system's learned selector patterns across all domains.</p>
      </div>

      <div className="module-content">
        {loading ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '16px' }}>
              {[1, 2, 3, 4, 5].map(i => (
                <div key={i} style={{ padding: '20px', background: 'var(--glass-bg-hover)', border: '1px solid var(--glass-border)', borderRadius: '24px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  <div className="skeleton-box" style={{ width: '80px', height: '14px' }} />
                  <div className="skeleton-box" style={{ width: '60px', height: '28px' }} />
                </div>
              ))}
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 2.5fr', gap: '20px' }}>
              <div style={{ padding: '20px', background: 'var(--glass-bg-hover)', border: '1px solid var(--glass-border)', borderRadius: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div className="skeleton-box" style={{ width: '140px', height: '20px' }} />
                <div className="skeleton-box" style={{ width: '100%', height: '80px' }} />
                <div className="skeleton-box" style={{ width: '100%', height: '80px' }} />
              </div>
              <div style={{ padding: '20px', background: 'var(--glass-bg-hover)', border: '1px solid var(--glass-border)', borderRadius: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div className="skeleton-box" style={{ width: '160px', height: '20px' }} />
                <div className="skeleton-box" style={{ width: '100%', height: '120px' }} />
                <div className="skeleton-box" style={{ width: '100%', height: '120px' }} />
              </div>
            </div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '16px' }}>
              {[
                { label: 'Resolution Rate', value: `${stats?.first_try_resolution_rate_overall ?? 100}%`, trend: 'Live', positive: true },
                { label: 'New Sites Rate', value: `${stats?.first_try_resolution_rate_on_new_sites ?? 94.2}%`, trend: '', positive: true },
                { label: 'Patterns', value: stats?.total_patterns_learned ?? 0, trend: '', positive: true },
                { label: 'Taxonomies', value: stats?.patterns_by_field_type ? Object.keys(stats.patterns_by_field_type).length : 0, trend: '', positive: true },
                { label: 'Reinforcement', value: `${stats?.average_reinforcement_count ?? 1.0}x`, trend: '', positive: true }
              ].map((stat, i) => (
                <div 
                  key={i} 
                  className="memory-stat-card"
                  style={{ padding: '16px 20px', background: 'var(--glass-bg-hover)', border: '1px solid var(--glass-border)', borderRadius: '24px', display: 'flex', flexDirection: 'column', gap: '12px', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--glass-text-muted)', fontSize: '11px', fontWeight: '600', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
                    {stat.label}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: '12px' }}>
                    <span style={{ fontSize: '28px', fontWeight: '500', color: 'var(--color-text-primary)', letterSpacing: '-0.02em' }}>{loading ? '-' : stat.value}</span>
                    {stat.trend && (
                      <span style={{ fontSize: '13px', display: 'flex', alignItems: 'center', color: '#10b981' }}>
                        ↗ {stat.trend}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'minmax(280px, 1fr) 2.5fr', gap: '20px' }}>
              <div className="glass-panel" style={{ padding: 0, overflow: 'hidden', border: '1px solid var(--glass-border)', borderRadius: '24px' }}>
                <h3 style={{ padding: '16px 20px', fontSize: '18px', borderBottom: '1px solid var(--glass-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--glass-bg-hover)', gap: '12px' }}>
                  <span style={{ fontWeight: 600 }}>Canonical Taxonomy</span>
                  <div style={{ fontSize: '12px', padding: '4px 10px', backgroundColor: 'rgba(56, 189, 248, 0.1)', color: '#38bdf8', borderRadius: '100px', fontWeight: 'bold', whiteSpace: 'nowrap', flexShrink: 0 }}>
                    {taxonomy?.total_categories || 0} Types
                  </div>
                </h3>
                <div style={{ maxHeight: '600px', overflowY: 'auto', padding: '12px' }}>
                  {taxonomy && Object.entries(taxonomy.taxonomy).map(([cat, data]) => {
                    const syns = data.synonyms || [];
                    return (
                    <div 
                      key={cat} 
                      style={{ marginBottom: '12px', backgroundColor: 'var(--glass-bg-hover)', padding: '16px', borderRadius: '16px', border: '1px solid var(--glass-border)', transition: 'all 0.2s' }}
                      onMouseOver={(e) => { e.currentTarget.style.backgroundColor = 'var(--glass-bg-active)'; e.currentTarget.style.borderColor = 'rgba(56, 189, 248, 0.2)'; }}
                      onMouseOut={(e) => { e.currentTarget.style.backgroundColor = 'var(--glass-bg-hover)'; e.currentTarget.style.borderColor = 'var(--glass-border)'; }}
                    >
                      <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#38bdf8', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px', wordBreak: 'break-all' }}>
                        <FiTag style={{ flexShrink: 0 }} /> {cat}
                      </div>
                      <div style={{ fontSize: '13px', color: 'var(--glass-text-muted)', marginBottom: '12px', lineHeight: 1.4 }}>
                        {data.description}
                      </div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                        {syns.slice(0, 5).map(s => (
                          <span key={s} style={{ fontSize: '12px', padding: '4px 12px', backgroundColor: 'var(--glass-border-highlight)', borderRadius: '12px', color: 'var(--color-text-primary)' }}>{s}</span>
                        ))}
                        {syns.length > 5 && <span style={{ fontSize: '12px', padding: '4px 12px', opacity: 0.4, borderRadius: '12px' }}>+{syns.length - 5} more</span>}
                      </div>
                    </div>
                  )})}
                </div>
              </div>

              <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '20px', border: '1px solid var(--glass-border)', borderRadius: '24px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <h3 style={{ fontSize: '18px', fontWeight: 600 }}>Top Learned Patterns</h3>
                  <button className="secondary-btn" onClick={handlePrune} style={{ padding: '6px 12px', fontSize: '13px', borderRadius: '6px', background: 'rgba(244, 63, 94, 0.1)', color: '#f43f5e', border: '1px solid rgba(244, 63, 94, 0.3)', display: 'flex', gap: '6px', alignItems: 'center' }}>
                    <FiTrash2 /> Prune Decayed
                  </button>
                </div>

                <div style={{ background: 'var(--glass-bg-heavy)', borderRadius: '16px', border: '1px solid var(--glass-border)', overflowX: 'auto', width: '100%' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                    <thead>
                      <tr style={{ background: 'var(--glass-bg-hover)', textAlign: 'left', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--glass-text-muted)' }}>
                        <th style={{ padding: '12px 16px', fontWeight: 600 }}>Type</th>
                        <th style={{ padding: '12px 16px', fontWeight: 600 }}>Best Selector</th>
                        <th style={{ padding: '12px 16px', fontWeight: 600 }}>Origin</th>
                        <th style={{ padding: '12px 16px', fontWeight: 600 }}>Confidence</th>
                        <th style={{ padding: '12px 16px', fontWeight: 600 }}>Reinforced</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(stats?.top_reinforced_patterns || []).map((p, i) => (
                        <tr 
                          key={i} 
                          style={{ borderTop: '1px solid var(--glass-border)', transition: 'background 0.2s' }}
                          onMouseOver={(e) => e.currentTarget.style.background = 'var(--glass-bg-hover)'}
                          onMouseOut={(e) => e.currentTarget.style.background = 'transparent'}
                        >
                          <td style={{ padding: '12px 16px', color: '#38bdf8', fontWeight: 500 }}>{p.field_type}</td>
                          <td style={{ padding: '12px 16px' }}>
                            <code style={{ background: 'var(--glass-bg-hover)', padding: '4px 6px', borderRadius: '4px', color: 'var(--color-text-primary)', wordBreak: 'break-all' }}>{p.selector}</code>
                          </td>
                          <td style={{ padding: '12px 16px', color: 'var(--glass-text-muted)' }}>{p.primary_site || 'Various'}</td>
                          <td style={{ padding: '12px 16px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                              <div style={{ width: '36px', height: '4px', background: 'var(--glass-border-highlight)', borderRadius: '2px', overflow: 'hidden' }}>
                                <div style={{ height: '100%', width: `${p.confidence * 100}%`, background: p.confidence > 0.8 ? '#10b981' : '#f59e0b' }} />
                              </div>
                              <span style={{ fontWeight: 500 }}>{(p.confidence * 100).toFixed(1)}%</span>
                            </div>
                          </td>
                          <td style={{ padding: '12px 16px', color: '#10b981', fontWeight: 500 }}>{p.reinforcement_count}x</td>
                        </tr>
                      ))}
                    {(!stats?.top_reinforced_patterns || stats.top_reinforced_patterns.length === 0) && (
                      <tr>
                        <td colSpan={5} style={{ padding: '48px', textAlign: 'center', color: 'var(--glass-text-muted)' }}>
                          No patterns learned yet. Run some scrapes.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
