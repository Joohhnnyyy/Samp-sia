import React, { useState, useEffect, useRef, useMemo } from 'react';
import { FiCommand, FiSun, FiMoon } from 'react-icons/fi';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import ChatInput from './ChatInput';

// Import our "Tools" which we'll render inline
import ScraperStudio from './ScraperStudio';
import ResultsTable from './ResultsTable';
import HealthMonitor from './HealthMonitor';
import NewsFactChecker from './NewsFactChecker';
import WatchControl from './WatchControl';
import MemoryDashboard from './MemoryDashboard';
import LiveConsole from './LiveConsole';
import HealingViewer from './HealingViewer';
import BloubBot, { EYE_ONLY_SEQUENCE, PROCESSING_SEQUENCE } from './BloubBot';
import { Skeleton } from 'boneyard-js/react';
import gsap from 'gsap';

function formatMarkdownText(raw: string): string {
  if (!raw) return '';
  // Replace literal '\n' characters returned as text strings with real newlines
  let formatted = raw.replace(/\\n/g, '\n');
  return formatted;
}

const TypingEffect = ({ text, onType, onComplete }: { text: string, onType: () => void, onComplete?: () => void }) => {
  const cleanText = useMemo(() => formatMarkdownText(text), [text]);
  const [displayedText, setDisplayedText] = useState('');

  useEffect(() => {
    setDisplayedText(''); // Reset on new text
    let i = 0;
    const interval = setInterval(() => {
      setDisplayedText((prev) => prev + (cleanText[i] || '') + (cleanText[i+1] || '') + (cleanText[i+2] || ''));
      i += 3;
      onType();
      if (i >= cleanText.length) {
        clearInterval(interval);
        if (onComplete) onComplete();
      }
    }, 5);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cleanText]);

  return (
    <div className="markdown-content">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{displayedText}</ReactMarkdown>
    </div>
  );
};

interface Message {
  role: 'user' | 'assistant';
  content: string;
  tool?: 'scraper' | 'results' | 'health' | 'news' | 'assistant' | 'watch' | 'memory' | 'console' | 'heal';
  jobId?: string;
}

interface MainChatAreaProps {
  isLightMode?: boolean;
  triggeredAction?: string | null;
  onActionHandled?: () => void;
}

export default function MainChatArea({ isLightMode = false, triggeredAction, onActionHandled }: MainChatAreaProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const heroRef = useRef<HTMLDivElement>(null);
  const chatHistoryRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (triggeredAction) {
      if (triggeredAction.startsWith('new_chat')) {
        setMessages([]);
      } else {
        handleSendMessage(triggeredAction);
      }
      if (onActionHandled) onActionHandled();
    }
  }, [triggeredAction]);

  useEffect(() => {
    if (heroRef.current && messages.length === 0) {
      gsap.fromTo(
        heroRef.current,
        { opacity: 0 },
        { opacity: 1, duration: 0.45, ease: 'power1.out', clearProps: 'opacity' }
      );
    }
  }, [messages.length]);

  useEffect(() => {
    if (chatHistoryRef.current) {
      const items = chatHistoryRef.current.querySelectorAll('.chat-msg-item:not(.animated)');
      if (items.length > 0) {
        gsap.fromTo(
          items,
          { opacity: 0 },
          { 
            opacity: 1, 
            duration: 0.4, 
            stagger: 0.06, 
            ease: 'power1.out',
            clearProps: 'opacity',
            onComplete: () => {
              items.forEach(el => el.classList.add('animated'));
            }
          }
        );
      }
    }
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSendMessage = async (message: string) => {
    const input = message.trim();
    if (!input) return;

    const newMessages: Message[] = [...messages, { role: 'user', content: input }];
    setMessages(newMessages);
    setIsLoading(true);

    let nextMessage: Message;

    setTimeout(() => {
      const lower = input.toLowerCase();
      if (lower.startsWith('job_inspect_')) {
        const jobId = input.replace('job_inspect_', '');
        nextMessage = { role: 'assistant', content: `Displaying logs & telemetry for Job \`${jobId}\`...`, tool: 'console', jobId };
        setMessages([...newMessages, nextMessage]);
        setIsLoading(false);
        setIsTyping(true);
      } else if (lower.startsWith('/scrape') || lower === 'scrape') {
        nextMessage = { role: 'assistant', content: 'I have opened the Scraper Studio for you. You can configure your extraction below.', tool: 'scraper' };
        setMessages([...newMessages, nextMessage]);
        setIsLoading(false);
        setIsTyping(true);
      } else if (lower.startsWith('/fact-check') || lower.includes('fact check')) {
        nextMessage = { role: 'assistant', content: 'Here is the NewsKeeper Fact-Checker interface.', tool: 'news' };
        setMessages([...newMessages, nextMessage]);
        setIsLoading(false);
        setIsTyping(true);
      } else if (lower.startsWith('/health') || lower === 'fleet health') {
        nextMessage = { role: 'assistant', content: 'Displaying live telemetry for the Scraper Fleet.', tool: 'health' };
        setMessages([...newMessages, nextMessage]);
        setIsLoading(false);
        setIsTyping(true);
      } else if (lower.startsWith('/watch') || lower === 'automate tracking') {
        nextMessage = { role: 'assistant', content: 'NeuroWatch Mission Control is ready. You can configure continuous tracking below.', tool: 'watch' };
        setMessages([...newMessages, nextMessage]);
        setIsLoading(false);
        setIsTyping(true);
      } else if (lower.startsWith('/memory')) {
        nextMessage = { role: 'assistant', content: 'Displaying Collective Memory and immune system stats.', tool: 'memory' };
        setMessages([...newMessages, nextMessage]);
        setIsLoading(false);
        setIsTyping(true);
      } else if (lower.startsWith('/results')) {
        nextMessage = { role: 'assistant', content: 'Here are the latest job results.', tool: 'results' };
        setMessages([...newMessages, nextMessage]);
        setIsLoading(false);
        setIsTyping(true);
      } else if (lower.startsWith('/heal')) {
        nextMessage = { role: 'assistant', content: 'Opening the Self-Healing Replay Viewer.', tool: 'heal' };
        setMessages([...newMessages, nextMessage]);
        setIsLoading(false);
        setIsTyping(true);
      } else if (lower.startsWith('/trending')) {
        const parts = input.split(' ');
        const location = parts.length > 1 ? parts.slice(1).join(' ') : 'Global';
        fetch(`http://localhost:8000/api/news/trending?location=${encodeURIComponent(location)}`)
          .then(res => res.json())
          .then(data => {
            let md = `**${location} Trending Intelligence**\n\n`;
            if (data.trending_topics) {
              data.trending_topics.forEach((t: any) => {
                const cleanBadge = t.hot_badge ? t.hot_badge.replace(/[^\w\s-]/g, '').trim() : '';
                md += `- **${t.title}**\n  *${t.summary}*\n  > **${t.category}** | \`${cleanBadge}\`\n\n`;
              });
            }
            setMessages([...newMessages, { role: 'assistant', content: md }]);
            setIsLoading(false);
            setIsTyping(true);
          }).catch(err => {
            setMessages([...newMessages, { role: 'assistant', content: 'Error loading trending intelligence.' }]);
            setIsLoading(false);
            setIsTyping(true);
          });
      } else {
        // Fallback to Native Sia LLM Chat
        const chatHistory = messages.map(m => ({ role: m.role, content: m.content }));
        fetch('http://localhost:8000/api/assistant/geopolitical-chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: input, user_location: 'Global', chat_history: chatHistory })
        })
        .then(res => res.json())
        .then(data => {
          let answer = data.answer || "I am having trouble processing the intelligence right now.";
          if (data.citations && data.citations.length > 0) {
            answer += '\n\n**Sources:**\n';
            data.citations.forEach((c: any) => {
              answer += `- [${c.source_title}](${c.source_url})\n`;
            });
          }
          setMessages([...newMessages, { role: 'assistant', content: answer }]);
          setIsLoading(false);
          setIsTyping(true);
        }).catch(err => {
          setMessages([...newMessages, { role: 'assistant', content: 'Error connecting to Sia backend.' }]);
          setIsLoading(false);
          setIsTyping(true);
        });
      }
    }, 100);
  };

  const renderTool = (message: Message) => {
    if (!message.tool) return null;
    switch (message.tool) {
      case 'scraper': return (
        <ScraperStudio 
          onJobStart={(jobId) => {
            setMessages(prev => [...prev, { role: 'assistant', content: `Started job ${jobId}. Monitoring logs...`, tool: 'console', jobId }]);
          }} 
        />
      );
      case 'results': return <ResultsTable />;
      case 'health': return <HealthMonitor />;
      case 'news': return <NewsFactChecker />;
      case 'watch': return <WatchControl />;
      case 'memory': return <MemoryDashboard />;
      case 'heal': return <HealingViewer />;
      case 'console': return (
        <LiveConsole 
          jobId={message.jobId || null} 
          onComplete={(data) => {
            // Format rows into a markdown table if they exist
            let resultTable = '';
            if (data.rows && data.rows.length > 0) {
              const headers = Object.keys(data.rows[0]);
              const headerRow = `| ${headers.join(' | ')} |`;
              const dividerRow = `| ${headers.map(() => '---').join(' | ')} |`;
              const bodyRows = data.rows.map((row: any) => `| ${headers.map(h => row[h]).join(' | ')} |`).join('\n');
              resultTable = `\n\n### Extracted Data\n${headerRow}\n${dividerRow}\n${bodyRows}`;
            }

            setMessages(prev => [...prev, { 
              role: 'assistant', 
              content: `**Scrape job completed successfully!**\n\n**Collector ID:** \`${data.collector_id || 'N/A'}\`${resultTable}` 
            }]);
          }}
        />
      );
      default: return null;
    }
  };

  return (
    <div className="main-content" style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      <div className="center-content" style={{ flex: 1, overflowY: 'auto', padding: '0 15%', scrollBehavior: 'smooth' }}>
        {messages.length === 0 ? (
          <div ref={heroRef} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', width: '100%', height: '100%', position: 'relative', minHeight: '70vh' }}>
            {/* Giant BloubBot Sitting in the Right Corner */}
            <div style={{
              position: 'fixed',
              right: '-8vw',
              top: '50%',
              transform: 'translateY(-50%)',
              zIndex: 2,
              filter: 'drop-shadow(0 36px 80px rgba(0,0,0,0.35))',
              pointerEvents: 'auto'
            }}>
              <BloubBot 
                size="clamp(500px, 46vw, 920px)" 
                follow={true} 
                expression="neutre" 
                shape={undefined}
                autoSequence={true}
                customSequence={EYE_ONLY_SEQUENCE}
              />
            </div>

            {/* Centered Welcome Hero & Input */}
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%', maxWidth: '800px', zIndex: 1, marginTop: '-18vh', textAlign: 'center' }}>
              <h1 style={{ 
                fontSize: 'clamp(36px, 3.8vw, 56px)', 
                fontWeight: '400', 
                color: 'var(--color-text-primary)', 
                marginBottom: '32px', 
                letterSpacing: '-0.025em', 
                lineHeight: '1.15',
                whiteSpace: 'nowrap'
              }}>
                How can I help you today?
              </h1>
              <div style={{ width: '100%' }}>
                <ChatInput onSend={handleSendMessage} isLoading={isLoading} />
              </div>
            </div>
          </div>
        ) : (
          <div ref={chatHistoryRef} className="chat-history" style={{ paddingBottom: '40px' }}>
            {messages.map((message, idx) => (
              <div key={idx} className="chat-msg-item" style={{ marginBottom: '32px', display: 'flex', flexDirection: 'column', alignItems: message.role === 'user' ? 'flex-end' : 'flex-start' }}>
                <div style={{
                  maxWidth: message.tool ? '100%' : '80%',
                  background: message.role === 'user' ? 'var(--color-user-msg-bg)' : 'transparent',
                  color: message.role === 'user' ? 'var(--color-user-msg-text)' : 'var(--color-text-primary)',
                  padding: message.role === 'user' ? '14px 28px' : '0',
                  borderRadius: message.role === 'user' ? '9999px' : '0',
                  fontSize: '18px',
                  fontWeight: message.role === 'user' ? '400' : 'normal',
                  lineHeight: '1.5',
                  boxShadow: message.role === 'user' ? '0 1px 4px rgba(0,0,0,0.08)' : 'none'
                }}>
                  {message.role === 'user' ? (
                    message.content
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', width: '100%' }}>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', flex: 1, minWidth: 0 }}>
                        {idx === messages.length - 1 && isTyping ? (
                          <TypingEffect text={message.content} onType={scrollToBottom} onComplete={() => setIsTyping(false)} />
                        ) : (
                          <div className="markdown-content">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>{formatMarkdownText(message.content)}</ReactMarkdown>
                          </div>
                        )}
                        {message.tool && (
                          <div className="tool-container" style={{ marginTop: '16px', width: '100%', maxWidth: message.tool === 'memory' || message.tool === 'health' || message.tool === 'watch' ? '1100px' : '900px' }}>
                            {renderTool(message)}
                          </div>
                        )}
                      </div>
                      {idx === messages.length - 1 && !isLoading && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '8px' }}>
                          <BloubBot 
                            size={72} 
                            follow={true} 
                            expression={isTyping ? "attentif" : "neutre"} 
                            state={isTyping ? "alert" : undefined}
                            autoSequence={!isTyping}
                            customSequence={EYE_ONLY_SEQUENCE}
                          />
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {isLoading && (
              <div style={{ marginBottom: '32px', width: '100%', maxWidth: '800px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <Skeleton name="chat-widget-skeleton" loading={true}>
                  <div style={{ padding: '16px 20px', color: 'var(--glass-text-muted)', fontSize: '15px' }}>Processing intelligence...</div>
                </Skeleton>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <BloubBot 
                    size={72} 
                    follow={false} 
                    expression="neutre" 
                    autoSequence={true}
                    customSequence={PROCESSING_SEQUENCE}
                  />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {messages.length > 0 && (
        <div style={{ flexShrink: 0, position: 'relative', zIndex: 9999, padding: '24px 15%', paddingBottom: '48px' }}>
          <ChatInput onSend={handleSendMessage} isLoading={isLoading} />
          <div style={{ textAlign: 'center', opacity: 0.5, marginTop: '16px', fontSize: '14px' }}>
            Powered by Samp Deep Scraper & Autonomous Intelligence
          </div>
        </div>
      )}
    </div>
  );
}
