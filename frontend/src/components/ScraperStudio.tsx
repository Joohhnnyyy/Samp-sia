import React, { useState, useEffect, useRef } from 'react';
import { FiPlus, FiTrash2, FiGlobe, FiLoader, FiSearch } from 'react-icons/fi';
import gsap from 'gsap';
import { API_BASE_URL } from '../config';

interface ScraperStudioProps {
  onJobStart?: (id: string) => void;
  presetData?: any;
}

export default function ScraperStudio({ onJobStart, presetData }: ScraperStudioProps) {
  const [targetUrl, setTargetUrl] = useState('');
  const [activeTab, setActiveTab] = useState('plain');
  const [isSubmitting, setIsSubmitting] = useState(false);
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

  const [fields, setFields] = useState([
    { id: 1, name: 'product_name', description: 'The title of the product' },
    { id: 2, name: 'price', description: 'The price of the product' },
    { id: 3, name: 'stock_status', description: 'In stock or out of stock' }
  ]);

  React.useEffect(() => {
    if (presetData) {
      setTargetUrl(presetData.example_url || '');
      if (presetData.fields && presetData.fields.length > 0) {
        setFields(presetData.fields.map((f: string, i: number) => ({
          id: i + 1,
          name: f,
          description: `Extract ${f}`
        })));
      }
    }
  }, [presetData]);

  const [exampleFields] = useState([
    { id: 1, label: 'Title', example: 'Sony WH-1000XM5' }
  ]);

  const [goal, setGoal] = useState('');
  const [maxSteps, setMaxSteps] = useState(5);

  const addField = () => setFields([...fields, { id: Date.now(), name: '', description: '' }]);
  const removeField = (id: number) => setFields(fields.filter(f => f.id !== id));
  const updateField = (id: number, key: 'name' | 'description', value: string) => 
    setFields(fields.map(f => f.id === id ? { ...f, [key]: value } : f));

  const handleRunScrape = async () => {
    if (!targetUrl) return alert("Please enter a Target URL");
    setIsSubmitting(true);
    
    try {
      let endpoint = '';
      let payload = {};

      if (activeTab === 'plain') {
        endpoint = '/api/scrape/run';
        payload = { url: targetUrl, fields: fields.map(f => f.name) };
      } else if (activeTab === 'example') {
        endpoint = '/api/scrape/teach';
        payload = { url: targetUrl, label: exampleFields[0].label, example: exampleFields[0].example };
      } else if (activeTab === 'agentic') {
        endpoint = '/api/scrape/agentic';
        payload = { url: targetUrl, goal: goal, max_steps: maxSteps };
      } else if (activeTab === 'search') {
        endpoint = '/api/scrape/search';
        payload = { query: targetUrl, fields: fields.map(f => f.name), max_sources: maxSteps };
      }

      const res = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        alert(`Error from backend: ${errorData.detail || res.statusText}`);
        return;
      }

      const data = await res.json();
      
      if (data.job_id) {
        if (onJobStart) onJobStart(data.job_id);
      } else {
        alert("Failed to start job: No job_id returned");
      }
    } catch (err) {
      console.error(err);
      alert("Error starting scrape job");
    } finally {
      setIsSubmitting(false);
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
          Scraper Studio
        </h1>
        <p className="subtitle" style={{ fontSize: '16px', opacity: 0.7, marginTop: '6px' }}>Configure extraction tasks and deploy autonomous scraping agents.</p>
      </div>
      
      <div className="module-content" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div className="url-bar" style={{ padding: '12px 16px', borderRadius: '9999px', display: 'flex', alignItems: 'center', backgroundColor: 'var(--glass-bg-heavy)' }}>
          {activeTab === 'search' ? <FiSearch className="url-icon" size={18} style={{ marginRight: '12px', opacity: 0.7 }} /> : <FiGlobe className="url-icon" size={18} style={{ marginRight: '12px', opacity: 0.7 }} />}
          <input 
            type="text" 
            placeholder={activeTab === 'search' ? "Enter search keywords (e.g. 'best budget laptops')" : "https://example.com"}
            value={targetUrl}
            onChange={(e) => setTargetUrl(e.target.value)}
            style={{ width: '100%', background: 'transparent', border: 'none', color: 'var(--color-text-primary)', outline: 'none', fontSize: '15px' }}
          />
        </div>

        <div className="tabs" style={{ display: 'flex', gap: '8px', padding: '4px', background: 'var(--glass-bg-hover)', borderRadius: '9999px', overflowX: 'auto' }}>
          <button className={`tab-btn ${activeTab === 'plain' ? 'active' : ''}`} onClick={() => setActiveTab('plain')} style={{
            background: activeTab === 'plain' ? 'var(--glass-bg-active)' : 'transparent',
            color: activeTab === 'plain' ? 'var(--color-text-primary)' : 'var(--glass-text-muted)',
            padding: '8px 18px', borderRadius: '9999px', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', fontSize: '14px', fontWeight: '500'
          }}>
            Schema
          </button>
          <button className={`tab-btn ${activeTab === 'example' ? 'active' : ''}`} onClick={() => setActiveTab('example')} style={{
            background: activeTab === 'example' ? 'var(--glass-bg-active)' : 'transparent',
            color: activeTab === 'example' ? 'var(--color-text-primary)' : 'var(--glass-text-muted)',
            padding: '8px 18px', borderRadius: '9999px', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', fontSize: '14px', fontWeight: '500'
          }}>
            Example
          </button>
          <button className={`tab-btn ${activeTab === 'agentic' ? 'active' : ''}`} onClick={() => setActiveTab('agentic')} style={{
            background: activeTab === 'agentic' ? 'var(--glass-bg-active)' : 'transparent',
            color: activeTab === 'agentic' ? 'var(--color-text-primary)' : 'var(--glass-text-muted)',
            padding: '8px 18px', borderRadius: '9999px', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', fontSize: '14px', fontWeight: '500'
          }}>
            Agentic
          </button>
          <button className={`tab-btn ${activeTab === 'search' ? 'active' : ''}`} onClick={() => setActiveTab('search')} style={{
            background: activeTab === 'search' ? 'var(--glass-bg-active)' : 'transparent',
            color: activeTab === 'search' ? 'var(--color-text-primary)' : 'var(--glass-text-muted)',
            padding: '8px 18px', borderRadius: '9999px', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', fontSize: '14px', fontWeight: '500'
          }}>
            Search
          </button>
        </div>

        <div className="tab-content" style={{ minHeight: '150px' }}>
          {(activeTab === 'plain' || activeTab === 'search') && (
            <div className="dynamic-rows">
              <div className="row-header" style={{ display: 'grid', gridTemplateColumns: '1fr 2fr 40px', gap: '12px', fontSize: '13px', textTransform: 'uppercase', letterSpacing: '0.05em', background: 'var(--glass-bg-hover)', color: 'var(--glass-text-muted)', padding: '10px 16px', borderRadius: '16px', marginBottom: '12px', fontWeight: '600' }}>
                <div>Field Name</div>
                <div>Semantic Description</div>
                <div></div>
              </div>
              {fields.map(f => (
                <div key={f.id} className="field-row" style={{ display: 'grid', gridTemplateColumns: '1fr 2fr 40px', gap: '12px', alignItems: 'center', marginBottom: '8px' }}>
                  <input type="text" value={f.name} onChange={(e) => updateField(f.id, 'name', e.target.value)} placeholder="e.g. price" style={{ padding: '10px 16px', background: 'var(--glass-bg-hover)', border: '1px solid var(--glass-border)', borderRadius: '9999px', color: 'var(--color-text-primary)', fontSize: '14px' }} />
                  <input type="text" value={f.description} onChange={(e) => updateField(f.id, 'description', e.target.value)} placeholder="e.g. The exact cost of the product" style={{ padding: '10px 16px', background: 'var(--glass-bg-hover)', border: '1px solid var(--glass-border)', borderRadius: '9999px', color: 'var(--color-text-primary)', fontSize: '14px' }} />
                  <button onClick={() => removeField(f.id)} style={{ background: 'transparent', border: 'none', color: '#ef4444', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><FiTrash2 size={18} /></button>
                </div>
              ))}
              <button onClick={addField} style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 16px', background: 'var(--glass-bg-hover)', border: '1px dashed var(--glass-border-highlight)', borderRadius: '9999px', color: 'var(--color-accent)', cursor: 'pointer', width: 'fit-content', fontWeight: '500', fontSize: '13px', marginTop: '4px' }}>
                <FiPlus size={14} /> Add Field
              </button>
              
              {activeTab === 'search' && (
                <div style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <label style={{ fontSize: 'var(--font-size-sm)', color: 'var(--glass-text-muted)' }}>Max Sources (URLs to discover and scrape)</label>
                  <input 
                    type="number" 
                    value={maxSteps}
                    onChange={(e) => setMaxSteps(parseInt(e.target.value) || 4)}
                    style={{ padding: '12px', background: 'var(--glass-bg-hover)', border: '1px solid var(--glass-border)', borderRadius: '9999px', color: 'var(--color-text-primary)', fontSize: 'var(--font-size-md)' }}
                  />
                </div>
              )}
            </div>
          )}

          {activeTab === 'example' && (
            <div className="tab-content" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div style={{ padding: '16px', background: 'rgba(245, 158, 11, 0.1)', borderRadius: '16px', border: '1px solid rgba(245, 158, 11, 0.2)', color: '#fcd34d', fontSize: '14px' }}>
                Provide 1-2 examples from the page. NeuroAnchor will find all similar elements automatically without CSS selectors.
              </div>
              <div className="dynamic-rows">
                <div className="row-header" style={{ display: 'grid', gridTemplateColumns: '1fr 2fr 40px', gap: '12px', fontSize: 'var(--font-size-sm)', background: 'var(--glass-bg-hover)', color: 'var(--glass-text-muted)', padding: '12px', borderRadius: '16px' }}>
                  <div>Label</div>
                  <div>Example Data</div>
                  <div></div>
                </div>
                <div className="field-row" style={{ display: 'grid', gridTemplateColumns: '1fr 2fr 40px', gap: '12px', alignItems: 'center', marginTop: '8px' }}>
                  <input type="text" value={exampleFields[0].label} readOnly style={{ padding: '12px 16px', background: 'var(--glass-bg-hover)', border: '1px solid var(--glass-border)', borderRadius: '9999px', color: 'var(--glass-text-muted)' }} />
                  <input type="text" value={exampleFields[0].example} readOnly style={{ padding: '12px 16px', background: 'var(--glass-bg-hover)', border: '1px solid var(--glass-border)', borderRadius: '9999px', color: 'var(--glass-text-muted)' }} />
                  <button disabled style={{ background: 'transparent', border: 'none', color: '#ef4444', opacity: 0.5, display: 'flex', justifyContent: 'center' }}><FiTrash2 /></button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'agentic' && (
            <div className="input-group" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <label style={{ fontSize: 'var(--font-size-sm)', color: 'var(--glass-text-muted)' }}>Agent Goal</label>
                <textarea 
                  value={goal}
                  onChange={(e) => setGoal(e.target.value)}
                  placeholder="e.g. Find all team members and their social links..."
                  style={{ width: '100%', padding: '16px', background: 'var(--glass-bg-hover)', border: '1px solid var(--glass-border)', borderRadius: '24px', color: 'var(--color-text-primary)', minHeight: '120px', resize: 'vertical' }}
                />
              </div>
              <div className="input-group">
                <label style={{ fontSize: 'var(--font-size-sm)', color: 'var(--glass-text-muted)' }}>Max Navigation Steps</label>
                <input 
                  type="number" 
                  value={maxSteps}
                  onChange={(e) => setMaxSteps(Number(e.target.value))}
                  style={{ width: '100%', padding: '16px', background: 'var(--glass-bg-hover)', border: '1px solid var(--glass-border)', borderRadius: '9999px', color: 'var(--color-text-primary)' }}
                />
              </div>
            </div>
          )}
        </div>

        <button 
          onClick={handleRunScrape} 
          disabled={isSubmitting}
          style={{ width: '100%', padding: '14px', background: 'var(--color-accent)', color: '#000', border: 'none', borderRadius: '9999px', fontWeight: '500', cursor: isSubmitting ? 'not-allowed' : 'pointer', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px', marginTop: '8px', fontSize: '15px' }}
        >
          {isSubmitting ? <><FiLoader size={18} className="spin" /> Starting...</> : <>Run Scrape</>}
        </button>
      </div>
    </div>
  );
}
