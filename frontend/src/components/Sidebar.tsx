import React, { useState, useEffect, useRef } from 'react';
import { 
  FiMenu, 
  FiEdit3, 
  FiSearch, 
  FiImage, 
  FiGrid, 
  FiHexagon, 
  FiPlus, 
  FiFileText, 
  FiMoreHorizontal,
  FiSun,
  FiMoon
} from 'react-icons/fi';
import gsap from 'gsap';
import LogSearchModal from './LogSearchModal';

interface SidebarProps {
  isLightMode?: boolean;
  toggleTheme?: () => void;
  onSelectAction?: (action: string) => void;
  onNewChat?: () => void;
}

export default function Sidebar({ 
  isLightMode = false, 
  toggleTheme = () => {},
  onSelectAction = () => {},
  onNewChat = () => {}
}: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [activeRecent, setActiveRecent] = useState<string>('Friendly Greeting');
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [isSearchModalOpen, setIsSearchModalOpen] = useState(false);
  const sidebarRef = useRef<HTMLDivElement>(null);
  const profileMenuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (profileMenuRef.current && !profileMenuRef.current.contains(event.target as Node)) {
        setShowProfileMenu(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    if (sidebarRef.current) {
      gsap.fromTo(
        sidebarRef.current.querySelectorAll('.nav-item, .brand, .user-profile, .sidebar-section-title'),
        { opacity: 0, x: -10 },
        { opacity: 1, x: 0, duration: 0.3, stagger: 0.03, ease: 'power1.out', clearProps: 'opacity,transform' }
      );
    }
  }, [isCollapsed]);

  const recentChats = [
    'TechCrunch AI Startups Scrape',
    'Fact Check Global News Stream',
    'Amazon Electronics Price Monitor',
    'Reddit Developer Sentiment Feed',
    'Self-Healing DOM Anchor Replay',
    'HackerNews Trending Intelligence',
    'GitHub Repository Crawler Setup',
    'Bloomberg Geopolitics Fact Check',
    'E-commerce Catalog Drift Fix',
    'Bright Data Scraper Studio Job',
    'NeuroAnchor Semantic Recovery'
  ];

  const filteredRecents = recentChats.filter(chat => 
    chat.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div ref={sidebarRef} className={`sidebar ${isCollapsed ? 'collapsed' : 'expanded'}`} style={{ display: 'flex', flexDirection: 'column', height: '100vh', justifyContent: 'space-between', padding: isCollapsed ? '16px 8px' : '16px 12px', background: isCollapsed ? 'transparent' : 'var(--color-surface-base)' }}>
      {/* Top Header & Brand */}
      <div className="sidebar-top-section" style={{ display: 'flex', flexDirection: 'column', width: '100%', flexShrink: 0 }}>
        <div className="brand-header" style={{ display: 'flex', alignItems: 'center', justifyContent: isCollapsed ? 'center' : 'flex-start', gap: '12px', padding: isCollapsed ? '0 0 16px' : '0 8px 16px' }}>
          <button className="icon-btn sidebar-icon" onClick={() => setIsCollapsed(!isCollapsed)} style={{ width: '40px', height: '40px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'transparent', border: 'none', color: 'var(--color-text-primary)', cursor: 'pointer', borderRadius: '50%' }}>
            <FiMenu size={20} />
          </button>
          {!isCollapsed && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer' }} onClick={onNewChat}>
              {/* SaMp Official Brand Logo */}
              <img 
                src={isLightMode ? '/samp_black.png' : '/samp_white.png'} 
                alt="SaMp Logo" 
                style={{ width: '26px', height: '26px', objectFit: 'contain' }}
              />
              <span style={{ fontSize: '18px', fontWeight: '600', letterSpacing: '-0.02em', color: 'var(--color-text-primary)' }}>Samp</span>
            </div>
          )}
        </div>

        {/* Primary Action Buttons */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', width: '100%' }}>
          <button 
            className="nav-item" 
            onClick={onNewChat}
            style={{ padding: isCollapsed ? '0' : '10px 14px', justifyContent: isCollapsed ? 'center' : 'flex-start', width: isCollapsed ? '44px' : '100%', height: isCollapsed ? '44px' : 'auto', margin: isCollapsed ? '0 auto 4px' : '0' }}
          >
            <FiEdit3 size={18} style={{ flexShrink: 0 }} />
            {!isCollapsed && <span className="nav-label">New session</span>}
          </button>

          <button 
            className="nav-item" 
            onClick={() => {
              setIsSearchModalOpen(true);
            }}
            style={{ padding: isCollapsed ? '0' : '10px 14px', justifyContent: isCollapsed ? 'center' : 'flex-start', width: isCollapsed ? '44px' : '100%', height: isCollapsed ? '44px' : 'auto', margin: isCollapsed ? '0 auto 4px' : '0' }}
          >
            <FiSearch size={18} style={{ flexShrink: 0 }} />
            {!isCollapsed && <span className="nav-label">Search logs</span>}
          </button>

          <button 
            className="nav-item" 
            onClick={() => onSelectAction('Scrape Website')}
            style={{ padding: isCollapsed ? '0' : '10px 14px', justifyContent: isCollapsed ? 'center' : 'flex-start', width: isCollapsed ? '44px' : '100%', height: isCollapsed ? '44px' : 'auto', margin: isCollapsed ? '0 auto 4px' : '0' }}
          >
            <FiImage size={18} style={{ flexShrink: 0 }} />
            {!isCollapsed && <span className="nav-label">Scraper Studio</span>}
          </button>

          <button 
            className="nav-item" 
            onClick={() => onSelectAction('/memory')}
            style={{ padding: isCollapsed ? '0' : '10px 14px', justifyContent: isCollapsed ? 'center' : 'flex-start', width: isCollapsed ? '44px' : '100%', height: isCollapsed ? '44px' : 'auto', margin: isCollapsed ? '0 auto 4px' : '0' }}
          >
            <FiGrid size={18} style={{ flexShrink: 0 }} />
            {!isCollapsed && <span className="nav-label">Collective Memory</span>}
          </button>

          <button 
            className="nav-item" 
            onClick={() => onSelectAction('/health')}
            style={{ padding: isCollapsed ? '0' : '10px 14px', justifyContent: isCollapsed ? 'center' : 'flex-start', width: isCollapsed ? '44px' : '100%', height: isCollapsed ? '44px' : 'auto', margin: isCollapsed ? '0 auto 4px' : '0' }}
          >
            <FiHexagon size={18} style={{ flexShrink: 0 }} />
            {!isCollapsed && <span className="nav-label">Fleet Health</span>}
          </button>
        </div>
      </div>

      {/* Middle Scrollable Section: Watch Missions & Recent Scrapes */}
      {!isCollapsed && (
        <div className="sidebar-middle-scroll" style={{ flex: 1, overflowY: 'auto', marginTop: '16px', marginBottom: '16px', display: 'flex', flexDirection: 'column', gap: '16px', paddingRight: '4px' }}>
          {/* Active Missions Group */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <div className="sidebar-section-title" style={{ padding: '0 12px', fontSize: '12px', color: 'var(--glass-text-muted)', fontWeight: '600' }}>
              Missions
            </div>

            <button 
              className="nav-item" 
              onClick={() => onSelectAction('Automate Tracking')}
              style={{ padding: '8px 14px', fontSize: '13.5px' }}
            >
              <FiPlus size={16} style={{ flexShrink: 0 }} />
              <span className="nav-label">New watch mission</span>
            </button>

            <button 
              className="nav-item" 
              onClick={() => onSelectAction('Fact Check News')}
              style={{ padding: '8px 14px', fontSize: '13.5px' }}
            >
              <FiFileText size={16} style={{ flexShrink: 0 }} />
              <span className="nav-label">Fact Check News Feed</span>
            </button>

            <button 
              className="nav-item" 
              onClick={() => onSelectAction('/heal')}
              style={{ padding: '8px 14px', fontSize: '13.5px' }}
            >
              <FiFileText size={16} style={{ flexShrink: 0 }} />
              <span className="nav-label">Self-Healing DOM Replay</span>
            </button>

            <button 
              className="nav-item" 
              onClick={() => onSelectAction('/watch')}
              style={{ padding: '8px 14px', fontSize: '13.5px', color: 'var(--glass-text-muted)' }}
            >
              <FiMoreHorizontal size={16} style={{ flexShrink: 0 }} />
              <span className="nav-label">All watch missions</span>
            </button>
          </div>

          {/* Recent Scrapes Group */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
            <div className="sidebar-section-title" style={{ padding: '0 12px', fontSize: '12px', color: 'var(--glass-text-muted)', fontWeight: '600', marginBottom: '4px' }}>
              Recent Extractions
            </div>

            {filteredRecents.map((item, idx) => (
              <button 
                key={idx}
                className={`nav-item ${activeRecent === item ? 'active' : ''}`}
                onClick={() => {
                  setActiveRecent(item);
                  onSelectAction(item);
                }}
                style={{ 
                  padding: '8px 14px', 
                  fontSize: '13.5px',
                  backgroundColor: activeRecent === item ? 'rgba(255, 255, 255, 0.08)' : 'transparent',
                  fontWeight: activeRecent === item ? '600' : '400',
                  borderRadius: '8px'
                }}
              >
                <span className="nav-label">{item}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Bottom User Profile & Theme Toggle Section */}
      <div className="sidebar-bottom-section" style={{ flexShrink: 0, borderTop: isCollapsed ? 'none' : '1px solid var(--glass-border)', paddingTop: '12px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
        {/* Direct Theme Toggle Button */}
        <button 
          className="nav-item" 
          onClick={toggleTheme}
          title={isLightMode ? 'Switch to Dark Mode' : 'Switch to Light Mode'}
          style={{ 
            padding: isCollapsed ? '0' : '10px 12px', 
            justifyContent: isCollapsed ? 'center' : 'flex-start', 
            width: isCollapsed ? '44px' : '100%', 
            height: isCollapsed ? '44px' : 'auto', 
            margin: isCollapsed ? '0 auto 4px' : '0',
            borderRadius: isCollapsed ? '50%' : '12px',
            background: 'transparent'
          }}
        >
          {isLightMode ? <FiMoon size={18} style={{ flexShrink: 0 }} /> : <FiSun size={18} style={{ flexShrink: 0 }} />}
          {!isCollapsed && <span className="nav-label">{isLightMode ? 'Dark mode' : 'Light mode'}</span>}
        </button>

        <div 
          ref={profileMenuRef}
          style={{ position: 'relative', width: '100%', display: 'flex', justifyContent: 'center' }}
        >
          <div 
            className="user-profile"
            onClick={() => setShowProfileMenu(!showProfileMenu)}
            style={{ 
              width: isCollapsed ? '44px' : '100%', 
              height: isCollapsed ? '44px' : 'auto', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: isCollapsed ? 'center' : 'flex-start', 
              cursor: 'pointer', 
              padding: isCollapsed ? '0' : '8px 10px', 
              borderRadius: isCollapsed ? '50%' : '12px',
              transition: 'background-color 0.2s'
            }}
          >
            <div className="avatar" style={{backgroundColor: 'var(--color-accent)', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '50%', width: '28px', height: '28px', fontSize: '13px', flexShrink: 0, fontWeight: '600'}}>S</div>
            {!isCollapsed && <span className="nav-label" style={{ fontWeight: '500', fontSize: '14px', marginLeft: '10px' }}>Samp AI Studio</span>}
          </div>

          {showProfileMenu && (
            <div 
              style={{
                position: 'absolute',
                bottom: '100%',
                left: isCollapsed ? '54px' : '0',
                marginBottom: '12px',
                width: '230px',
                backgroundColor: 'var(--color-surface-elevated)',
                backdropFilter: 'blur(20px)',
                WebkitBackdropFilter: 'blur(20px)',
                border: '1px solid var(--glass-border)',
                borderRadius: '16px',
                padding: '8px',
                boxShadow: '0 12px 32px rgba(0, 0, 0, 0.4)',
                display: 'flex',
                flexDirection: 'column',
                gap: '4px',
                zIndex: 9999
              }}
            >
              <div style={{ padding: '8px 12px', borderBottom: '1px solid var(--glass-border)', marginBottom: '4px' }}>
                <div style={{ fontSize: '13px', fontWeight: '600', color: 'var(--color-text-primary)' }}>Samp AI Studio</div>
                <div style={{ fontSize: '11px', color: 'var(--glass-text-muted)', marginTop: '2px' }}>Autonomous Workspace • v1.0</div>
              </div>
              <button 
                onClick={() => { setShowProfileMenu(false); toggleTheme(); }}
                style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px', background: 'transparent', border: 'none', color: 'var(--color-text-primary)', fontSize: '13px', borderRadius: '8px', cursor: 'pointer', textAlign: 'left' }}
                onMouseEnter={e => e.currentTarget.style.backgroundColor='var(--glass-bg-hover)'}
                onMouseLeave={e => e.currentTarget.style.backgroundColor='transparent'}
              >
                <span>Appearance</span>
                <span style={{ fontSize: '11px', color: 'var(--color-accent)' }}>{isLightMode ? 'Light' : 'Dark'}</span>
              </button>
              <button 
                onClick={() => { setShowProfileMenu(false); onSelectAction('/health'); }}
                style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px', background: 'transparent', border: 'none', color: 'var(--color-text-primary)', fontSize: '13px', borderRadius: '8px', cursor: 'pointer', textAlign: 'left' }}
                onMouseEnter={e => e.currentTarget.style.backgroundColor='var(--glass-bg-hover)'}
                onMouseLeave={e => e.currentTarget.style.backgroundColor='transparent'}
              >
                <span>Worker Health</span>
                <span style={{ fontSize: '11px', color: '#10b981' }}>Connected</span>
              </button>
              <button 
                onClick={() => { setShowProfileMenu(false); onSelectAction('/memory'); }}
                style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px', background: 'transparent', border: 'none', color: 'var(--color-text-primary)', fontSize: '13px', borderRadius: '8px', cursor: 'pointer', textAlign: 'left' }}
                onMouseEnter={e => e.currentTarget.style.backgroundColor='var(--glass-bg-hover)'}
                onMouseLeave={e => e.currentTarget.style.backgroundColor='transparent'}
              >
                <span>Immune Memory</span>
                <span style={{ fontSize: '11px', color: 'var(--color-accent)' }}>Live</span>
              </button>
              <div style={{ borderTop: '1px solid var(--glass-border)', marginTop: '4px', paddingTop: '4px' }}>
                <button 
                  onClick={() => { setShowProfileMenu(false); onNewChat(); }}
                  style={{ width: '100%', padding: '8px 12px', background: 'transparent', border: 'none', color: '#ef4444', fontSize: '13px', borderRadius: '8px', cursor: 'pointer', textAlign: 'left' }}
                  onMouseEnter={e => e.currentTarget.style.backgroundColor='rgba(239, 68, 68, 0.1)'}
                  onMouseLeave={e => e.currentTarget.style.backgroundColor='transparent'}
                >
                  Clear Session
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
      {/* Search Logs Comprehensive Modal */}
      <LogSearchModal 
        isOpen={isSearchModalOpen}
        onClose={() => setIsSearchModalOpen(false)}
        onSelectJob={(jobId, url) => {
          onSelectAction(`job_inspect_${jobId}`);
        }}
      />
    </div>
  );
}
