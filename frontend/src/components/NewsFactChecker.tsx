import React, { useState, useEffect, useRef } from 'react';
import { FiCheckSquare, FiSearch, FiAlertCircle, FiLoader } from 'react-icons/fi';
import gsap from 'gsap';

export default function NewsFactChecker() {
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState<any[]>([]);
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
    if (containerRef.current && results.length > 0) {
      gsap.fromTo(
        containerRef.current.querySelectorAll('.fact-check-result-item'),
        { opacity: 0, y: 15 },
        { opacity: 1, y: 0, duration: 0.4, stagger: 0.08, ease: 'power2.out' }
      );
    }
  }, [results]);

  const handleSearch = async () => {
    if (!query) return;
    setIsSearching(true);
    try {
      const res = await fetch('http://localhost:8000/api/news/fact-check', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query_or_url: query,
          user_region: 'India',
          max_sources: 4
        })
      });
      const data = await res.json();
      
      const isVerified = data.verification_status?.status_code === 'verified_true';
      
      const formattedResults = (data.sources || []).map((s: any) => ({
        source: s.source_name || 'News Outlet',
        headline: s.headline || query,
        confidence: (data.trust_percentage || 0) / 100,
        timestamp: 'Just now',
        verified: isVerified
      }));
      
      setResults(formattedResults);
    } catch (error) {
      console.error('Error fetching fact check:', error);
      setResults([{
        source: 'System',
        headline: 'Failed to connect to Fact-Checker backend.',
        confidence: 0,
        timestamp: 'Just now',
        verified: false
      }]);
    } finally {
      setIsSearching(false);
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
          News Fact Checker
        </h1>
        <p className="subtitle" style={{ fontSize: '16px', opacity: 0.7, marginTop: '6px' }}>Cross-verify breaking news against multi-source verified consensus.</p>
      </div>
      
      <div className="module-content" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        
        <div style={{ padding: '12px 16px', borderRadius: '9999px', display: 'flex', alignItems: 'center', backgroundColor: 'var(--glass-bg-heavy)', border: '1px solid var(--glass-border)' }}>
          <FiSearch style={{ marginRight: '12px', color: 'var(--glass-text-muted)' }} size={18} />
          <input 
            type="text" 
            placeholder="Enter claim or headline to cross-verify..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            style={{ flex: 1, background: 'transparent', border: 'none', color: 'var(--color-text-primary)', outline: 'none', fontSize: '15px' }}
          />
          <button 
            onClick={handleSearch}
            disabled={isSearching || !query}
            style={{ marginLeft: '12px', background: 'var(--color-accent)', color: '#000', border: 'none', borderRadius: '9999px', padding: '10px 24px', fontWeight: '500', cursor: (isSearching || !query) ? 'not-allowed' : 'pointer', fontSize: '14px' }}
          >
            {isSearching ? <FiLoader className="spin" size={16} /> : 'Verify'}
          </button>
        </div>

        {isSearching ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '16px' }}>
            <div className="skeleton-box" style={{ width: '100%', height: '74px', borderRadius: '16px' }} />
            <div className="skeleton-box" style={{ width: '100%', height: '74px', borderRadius: '16px' }} />
            <div className="skeleton-box" style={{ width: '100%', height: '74px', borderRadius: '16px' }} />
          </div>
        ) : results.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '8px' }}>
            {results.map((r, i) => (
              <div key={i} className="fact-check-result-item" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px', background: 'var(--glass-bg-hover)', border: '1px solid var(--glass-border)', borderRadius: '12px' }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <div style={{ fontWeight: '500', fontSize: 'var(--font-size-md)', color: 'var(--color-text-primary)' }}>{r.headline}</div>
                  <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--glass-text-muted)', display: 'flex', gap: '8px' }}>
                    <span>{r.source}</span> • <span>{r.timestamp}</span>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: r.verified ? '#10b981' : '#ef4444', fontSize: 'var(--font-size-sm)', fontWeight: '500', backgroundColor: r.verified ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)', padding: '6px 16px', borderRadius: '12px' }}>
                  {r.verified ? <FiCheckSquare size={18} /> : <FiAlertCircle size={18} />}
                  {r.verified ? 'Verified' : 'Unverified'}
                </div>
              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  );
}
