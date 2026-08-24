import React, { useState, useEffect, useRef } from 'react';
import gsap from 'gsap';
import { 
  FiPlus, 
  FiMic, 
  FiChevronDown,
  FiArrowUp,
  FiGlobe,
  FiCheckSquare,
  FiActivity,
  FiClock,
  FiCheck,
  FiDatabase,
  FiShield,
  FiList
} from 'react-icons/fi';

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading?: boolean;
}

export default function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [inputValue, setInputValue] = useState('');
  const [showMenu, setShowMenu] = useState(false);
  const [region, setRegion] = useState('Global');
  const [showRegionMenu, setShowRegionMenu] = useState(false);
  const [mousePos, setMousePos] = useState({ x: 50, y: 50 });
  const [isFocused, setIsFocused] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  const menuRef = useRef<HTMLDivElement>(null);
  const regionMenuRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const auraRef = useRef<HTMLDivElement>(null);
  const innerAuraRef = useRef<HTMLDivElement>(null);

  // GSAP smooth mouse tweening
  const mouseCoords = useRef({ x: 50, y: 50 });

  const handleContainerMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const targetX = ((e.clientX - rect.left) / rect.width) * 100;
    const targetY = ((e.clientY - rect.top) / rect.height) * 100;

    gsap.to(mouseCoords.current, {
      x: targetX,
      y: targetY,
      duration: 0.8,
      ease: 'power2.out',
      onUpdate: () => {
        setMousePos({ x: mouseCoords.current.x, y: mouseCoords.current.y });
      }
    });
  };

  const handleContainerMouseLeave = () => {
    setIsHovered(false);
    gsap.to(mouseCoords.current, {
      x: 50,
      y: 50,
      duration: 1.2,
      ease: 'power3.out',
      onUpdate: () => {
        setMousePos({ x: mouseCoords.current.x, y: mouseCoords.current.y });
      }
    });
  };

  // GSAP aura state tweens (subtle & refined)
  useEffect(() => {
    if (!auraRef.current) return;
    const targetOpacity = isFocused ? 0.65 : inputValue.trim() ? 0.55 : isHovered ? 0.4 : 0.22;
    const targetScale = isFocused ? 1.015 : inputValue.trim() ? 1.01 : 1.0;
    const targetBlur = isFocused ? 26 : inputValue.trim() ? 22 : 16;

    gsap.to(auraRef.current, {
      opacity: targetOpacity,
      scale: targetScale,
      filter: `blur(${targetBlur}px)`,
      duration: 0.7,
      ease: 'sine.out'
    });

    if (innerAuraRef.current) {
      gsap.to(innerAuraRef.current, {
        opacity: isFocused ? 0.45 : isHovered ? 0.3 : 0.15,
        duration: 0.7,
        ease: 'sine.out'
      });
    }
  }, [isFocused, isHovered, inputValue]);

  React.useEffect(() => {
    if (showRegionMenu && regionMenuRef.current) {
      const dropdown = regionMenuRef.current.querySelector('.region-dropdown');
      if (dropdown) {
        gsap.fromTo(dropdown, { opacity: 0 }, { opacity: 1, duration: 0.25, ease: 'power1.out', clearProps: 'opacity' });
      }
    }
  }, [showRegionMenu]);

  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setShowMenu(false);
      }
      if (regionMenuRef.current && !regionMenuRef.current.contains(event.target as Node)) {
        setShowRegionMenu(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleMenuClick = (command: string) => {
    onSend(command);
    setShowMenu(false);
  };

  const handleSubmit = () => {
    if (inputValue.trim() && !isLoading) {
      onSend(inputValue.trim());
      setInputValue('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div 
      ref={containerRef}
      onMouseMove={handleContainerMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={handleContainerMouseLeave}
      className="chat-input-container" 
      style={{ width: '100%', margin: '0 auto', display: 'flex', flexDirection: 'column', alignItems: 'center', position: 'relative' }}
    >
      {/* Siri Aura Ambient Glow - Controlled smoothly by GSAP */}
      <div 
        ref={auraRef}
        className="siri-input-aura"
        style={{
          position: 'absolute',
          inset: '-8px',
          borderRadius: '100px',
          background: `radial-gradient(circle at ${mousePos.x.toFixed(1)}% ${mousePos.y.toFixed(1)}%, oklch(72% 0.22 350 / 0.8), oklch(68% 0.20 285 / 0.75) 40%, oklch(65% 0.18 215 / 0.75) 75%, oklch(70% 0.20 330 / 0.8))`,
          filter: 'blur(18px)',
          opacity: 0.25,
          pointerEvents: 'none',
          zIndex: 0
        }}
      />
      {/* Secondary Inner Brightness Follower Ring */}
      <div 
        ref={innerAuraRef}
        style={{
          position: 'absolute',
          inset: '-2px',
          borderRadius: '100px',
          background: `linear-gradient(${mousePos.x * 3.6}deg, rgba(236, 72, 153, 0.6), rgba(168, 85, 247, 0.6), rgba(59, 130, 246, 0.6), rgba(236, 72, 153, 0.6))`,
          filter: 'blur(8px)',
          opacity: 0.2,
          pointerEvents: 'none',
          zIndex: 0
        }}
      />
      <div className="input-box" style={{ width: '100%', maxWidth: '800px', margin: '0 auto', backgroundColor: 'var(--color-surface-base)', borderRadius: '100px', padding: '12px 16px', border: isFocused ? '1px solid rgba(192, 132, 252, 0.5)' : '1px solid var(--glass-border-highlight)', boxShadow: isFocused ? '0 16px 44px rgba(168, 85, 247, 0.18)' : '0 12px 36px var(--glass-shadow)', position: 'relative', zIndex: 1, transition: 'border-color 0.4s ease, box-shadow 0.4s ease' }}>
        <div className="input-wrapper" style={{ display: 'flex', alignItems: 'center', width: '100%', padding: '0 8px' }}>
          <div style={{ position: 'relative' }} ref={menuRef}>
            <button className="icon-btn left-icon-btn" onClick={() => setShowMenu(!showMenu)} style={{ color: 'var(--color-text-primary)' }}><FiPlus size={32} /></button>
            {showMenu && (
              <div style={{ position: 'absolute', bottom: '100%', left: '0', marginBottom: '16px', backgroundColor: 'var(--color-surface-elevated)', backdropFilter: 'blur(20px)', WebkitBackdropFilter: 'blur(20px)', borderRadius: '16px', padding: '8px', display: 'flex', flexDirection: 'column', gap: '4px', minWidth: 'max-content', boxShadow: '0 12px 36px rgba(0, 0, 0, 0.4), 0 0 1px 1px rgba(255,255,255,0.1)', zIndex: 99999, border: '1px solid var(--glass-border-highlight)' }}>
                <button onPointerDown={(e) => { e.preventDefault(); handleMenuClick('/scrape '); }} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 16px', background: 'transparent', border: 'none', color: 'var(--color-text-primary)', textAlign: 'left', borderRadius: '8px', cursor: 'pointer', fontSize: 'var(--font-size-md)', whiteSpace: 'nowrap' }} onMouseEnter={e => e.currentTarget.style.backgroundColor='var(--glass-bg-hover)'} onMouseLeave={e => e.currentTarget.style.backgroundColor='transparent'}>
                  <FiGlobe /> Scrape Website
                </button>
                <button onPointerDown={(e) => { e.preventDefault(); handleMenuClick('/fact-check '); }} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 16px', background: 'transparent', border: 'none', color: 'var(--color-text-primary)', textAlign: 'left', borderRadius: '8px', cursor: 'pointer', fontSize: 'var(--font-size-md)', whiteSpace: 'nowrap' }} onMouseEnter={e => e.currentTarget.style.backgroundColor='var(--glass-bg-hover)'} onMouseLeave={e => e.currentTarget.style.backgroundColor='transparent'}>
                  <FiCheckSquare /> Fact Check News
                </button>
                <button onPointerDown={(e) => { e.preventDefault(); handleMenuClick('/health'); }} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 16px', background: 'transparent', border: 'none', color: 'var(--color-text-primary)', textAlign: 'left', borderRadius: '8px', cursor: 'pointer', fontSize: 'var(--font-size-md)', whiteSpace: 'nowrap' }} onMouseEnter={e => e.currentTarget.style.backgroundColor='var(--glass-bg-hover)'} onMouseLeave={e => e.currentTarget.style.backgroundColor='transparent'}>
                  <FiActivity /> Fleet Health
                </button>
                <button onPointerDown={(e) => { e.preventDefault(); handleMenuClick('/watch'); }} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 16px', background: 'transparent', border: 'none', color: 'var(--color-text-primary)', textAlign: 'left', borderRadius: '8px', cursor: 'pointer', fontSize: 'var(--font-size-md)', whiteSpace: 'nowrap' }} onMouseEnter={e => e.currentTarget.style.backgroundColor='var(--glass-bg-hover)'} onMouseLeave={e => e.currentTarget.style.backgroundColor='transparent'}>
                  <FiClock /> Automate Tracking
                </button>
                <button onPointerDown={(e) => { e.preventDefault(); handleMenuClick('/memory'); }} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 16px', background: 'transparent', border: 'none', color: 'var(--color-text-primary)', textAlign: 'left', borderRadius: '8px', cursor: 'pointer', fontSize: 'var(--font-size-md)', whiteSpace: 'nowrap' }} onMouseEnter={e => e.currentTarget.style.backgroundColor='var(--glass-bg-hover)'} onMouseLeave={e => e.currentTarget.style.backgroundColor='transparent'}>
                  <FiDatabase /> Collective Memory
                </button>
                <button onPointerDown={(e) => { e.preventDefault(); handleMenuClick('/heal'); }} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 16px', background: 'transparent', border: 'none', color: 'var(--color-text-primary)', textAlign: 'left', borderRadius: '8px', cursor: 'pointer', fontSize: 'var(--font-size-md)', whiteSpace: 'nowrap' }} onMouseEnter={e => e.currentTarget.style.backgroundColor='var(--glass-bg-hover)'} onMouseLeave={e => e.currentTarget.style.backgroundColor='transparent'}>
                  <FiShield /> Self-Healing Viewer
                </button>
                <button onPointerDown={(e) => { e.preventDefault(); handleMenuClick('/results'); }} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 16px', background: 'transparent', border: 'none', color: 'var(--color-text-primary)', textAlign: 'left', borderRadius: '8px', cursor: 'pointer', fontSize: 'var(--font-size-md)', whiteSpace: 'nowrap' }} onMouseEnter={e => e.currentTarget.style.backgroundColor='var(--glass-bg-hover)'} onMouseLeave={e => e.currentTarget.style.backgroundColor='transparent'}>
                  <FiList /> Scrape Results
                </button>
              </div>
            )}
          </div>
          
          <textarea 
            className="hidden-input" 
            placeholder="Ask Sia anything..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            rows={1}
            style={{flex: 1, resize: 'none', height: '56px', paddingTop: '15px', paddingLeft: '24px', paddingRight: '24px', border: 'none', background: 'transparent', color: 'var(--color-text-primary)', fontSize: 'var(--font-size-md)', outline: 'none'}}
            disabled={isLoading}
          />

          <div className="input-actions-right" style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            {!inputValue.trim() && (
              <div style={{ position: 'relative' }} ref={regionMenuRef}>
                <button 
                  onClick={(e) => { e.preventDefault(); setShowRegionMenu(!showRegionMenu); }} 
                  disabled={isLoading} 
                  style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 16px', borderRadius: '100px', cursor: 'pointer', backgroundColor: 'var(--glass-bg-hover)', border: '1px solid var(--glass-border)', color: 'var(--color-text-primary)', fontSize: 'var(--font-size-sm)', whiteSpace: 'nowrap', transition: 'all 0.2s' }}
                  onMouseEnter={e => e.currentTarget.style.backgroundColor='var(--glass-bg-active)'} 
                  onMouseLeave={e => e.currentTarget.style.backgroundColor='var(--glass-bg-hover)'}
                >
                  {region} <FiChevronDown />
                </button>
                {showRegionMenu && (
                  <div 
                    className="region-dropdown"
                    style={{ 
                      position: 'absolute', 
                      bottom: '100%', 
                      right: 0, 
                      marginBottom: '12px', 
                      width: '200px', 
                      backgroundColor: 'var(--color-surface-elevated)', 
                      backdropFilter: 'blur(20px)', 
                      WebkitBackdropFilter: 'blur(20px)', 
                      border: '1px solid var(--glass-border)', 
                      borderRadius: '16px', 
                      padding: '8px', 
                      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)', 
                      display: 'flex', 
                      flexDirection: 'column', 
                      gap: '4px', 
                      zIndex: 100 
                    }}
                  >
                    {[
                      { id: 'Global', label: 'Global', desc: 'Worldwide intelligence' },
                      { id: 'US', label: 'US', desc: 'United States focus' },
                      { id: 'India', label: 'India', desc: 'India focus' },
                      { id: 'UK', label: 'UK', desc: 'United Kingdom focus' },
                      { id: 'EU', label: 'EU', desc: 'European Union focus' }
                    ].map(opt => (
                      <button 
                        key={opt.id}
                        onPointerDown={(e) => { 
                          e.preventDefault(); 
                          setRegion(opt.id); 
                          setShowRegionMenu(false); 
                          onSend('/trending ' + opt.id); 
                        }} 
                        style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 16px', background: 'transparent', border: 'none', color: 'var(--color-text-primary)', textAlign: 'left', borderRadius: '8px', cursor: 'pointer', transition: 'all 0.2s' }} 
                        onMouseEnter={e => e.currentTarget.style.backgroundColor='var(--glass-bg-hover)'} 
                        onMouseLeave={e => e.currentTarget.style.backgroundColor='transparent'}
                      >
                        <div style={{ width: '20px', display: 'flex', justifyContent: 'center', flexShrink: 0 }}>
                          {region === opt.id && <FiCheck size={16} />}
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                          <span style={{ fontSize: '14px', fontWeight: 500 }}>{opt.label}</span>
                          <span style={{ fontSize: '12px', color: 'var(--glass-text-muted)' }}>{opt.desc}</span>
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
            {inputValue.trim() && (
              <button className="submit-btn" onClick={handleSubmit} disabled={isLoading} style={{ backgroundColor: 'var(--color-text-primary)', color: 'var(--color-bg-primary)', border: 'none', borderRadius: '50%', width: '56px', height: '56px', display: 'flex', justifyContent: 'center', alignItems: 'center', cursor: 'pointer' }}>
                <FiArrowUp size={32} />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
