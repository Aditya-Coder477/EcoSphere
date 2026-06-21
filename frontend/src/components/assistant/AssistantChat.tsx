import React, { useState, useRef, useEffect } from 'react';
import { AssistantMessage } from '../../types';
import { assistantService } from '../../services/assistantService';
import { Send, User, Sparkles, Loader2, BookOpen } from 'lucide-react';
import { Button } from '../ui/Button';
import { getSimulatedAnswer, getWelcomeMessage, mockUserProfile } from '../../mocks';
import { useAppStore } from '../../store/useAppStore';

const QUICK_CHIPS = [
  'Why is my footprint high?',
  'What should I reduce first?',
  'How much can I save by using public transport?',
  'Which category is my biggest source?',
];

// Simple markdown-style bold renderer
const renderContent = (text: string) =>
  text.split(/(\*\*[^*]+\*\*)/).map((part, i) =>
    part.startsWith('**') && part.endsWith('**')
      ? <strong key={i} className="text-text-main font-semibold">{part.slice(2, -2)}</strong>
      : <span key={i}>{part}</span>
  );

export const AssistantChat: React.FC<{ userId: string }> = ({ userId }) => {
  const footprint = useAppStore((s) => s.footprint);
  const user = useAppStore((s) => s.user);
  const displayName = user?.name || mockUserProfile.name;

  const [messages, setMessages] = useState<AssistantMessage[]>(() => [
    getWelcomeMessage(user?.name || mockUserProfile.name)
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Update welcome message content reactively when displayName changes
  useEffect(() => {
    setMessages((prev) =>
      prev.map((msg) =>
        msg.id === 'welcome'
          ? { ...msg, content: getWelcomeMessage(displayName).content }
          : msg
      )
    );
  }, [displayName]);

  const addMessage = (msg: Omit<AssistantMessage, 'id' | 'timestamp'>) => {
    setMessages((prev) => [
      ...prev,
      { ...msg, id: Date.now().toString(), timestamp: Date.now() },
    ]);
  };

  const handleSend = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    addMessage({ role: 'user', content: trimmed });
    setInput('');
    setLoading(true);

    try {
      const res = await assistantService.queryAssistant(userId, trimmed);
      if (res?.data?.answer) {
        addMessage({
          role: 'assistant',
          content: res.data.answer,
          sources: res.data.sources,
          confidence: res.data.confidence,
          fallback_mode: res.data.fallback_mode,
          response_source: res.data.response_source,
          suggested_follow_up_questions: res.data.suggested_follow_up_questions,
          used_demo_data: res.data.used_demo_data,
          grounded_facts: res.data.grounded_facts,
        });
      } else {
        throw new Error('Empty response');
      }
    } catch {
      // Smart context-aware fallback instead of a generic error
      const simulatedAnswer = getSimulatedAnswer(trimmed);
      addMessage({
        role: 'assistant',
        content: simulatedAnswer,
        sources: ['EcoSphere Knowledge Base (simulated)'],
        confidence: 'low',
        fallback_mode: 'demo',
        response_source: 'demo',
        suggested_follow_up_questions: [
          'Why is my footprint high?',
          'What should I reduce first?',
        ],
        used_demo_data: true,
        grounded_facts: ['Dominant emission source is transport (simulated)'],
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[620px] glass-panel overflow-hidden" role="main" aria-label="AI Climate Coach chat">

      {/* Message list */}
      <div className="flex-1 overflow-y-auto p-6 space-y-5">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
            role={msg.role === 'assistant' ? 'status' : undefined}
          >
            {/* Avatar */}
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                msg.role === 'user'
                  ? 'bg-primary/20 text-primary'
                  : 'bg-accent/20 text-accent'
              }`}
              aria-hidden="true"
            >
              {msg.role === 'user'
                ? <User className="w-4 h-4" />
                : <Sparkles className="w-4 h-4" />
              }
            </div>

            {/* Bubble container */}
            <div className="flex flex-col gap-2 max-w-[80%]">
              {/* Bubble */}
              <div
                className={`rounded-2xl px-5 py-3 text-sm leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-primary text-white rounded-tr-none'
                    : 'bg-surface border border-border rounded-tl-none text-text-main'
                }`}
              >
                <div className="whitespace-pre-wrap">
                  {msg.role === 'assistant'
                    ? msg.content.split('\n').map((line, i) => (
                        <p key={i} className={line === '' ? 'h-2' : ''}>
                          {renderContent(line)}
                        </p>
                      ))
                    : msg.content
                  }
                </div>

                {/* Sources */}
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-border/50 text-xs text-text-muted">
                    <div className="flex items-center gap-1 mb-1">
                      <BookOpen className="w-3 h-3 text-accent" aria-hidden="true" />
                      <span className="font-semibold text-accent">Sources</span>
                    </div>
                    <ul className="list-disc pl-4 space-y-0.5">
                      {msg.sources.map((s, i) => <li key={i}>{s}</li>)}
                    </ul>
                  </div>
                )}
              </div>

              {msg.role === 'assistant' && msg.suggested_follow_up_questions && msg.suggested_follow_up_questions.length > 0 && (
                <div className="flex gap-2 flex-wrap mt-1">
                  {msg.suggested_follow_up_questions.map((q, i) => (
                    <button
                      key={i}
                      onClick={() => handleSend(q)}
                      aria-label={`Ask Climate Coach: "${q}"`}
                      className="text-xs text-left px-3 py-1.5 rounded bg-surface border border-border text-text-muted hover:text-text-main hover:border-accent/60 transition-colors"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Typing indicator */}
        {loading && (
          <div className="flex gap-3" aria-live="polite" aria-label="Assistant is typing">
            <div className="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center flex-shrink-0">
              <Sparkles className="w-4 h-4 text-accent" aria-hidden="true" />
            </div>
            <div className="bg-surface border border-border rounded-2xl rounded-tl-none px-5 py-4 flex gap-1.5 items-center">
              {[0, 0.15, 0.3].map((delay, i) => (
                <div
                  key={i}
                  className="w-2 h-2 bg-text-muted/60 rounded-full animate-bounce"
                  style={{ animationDelay: `${delay}s` }}
                />
              ))}
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* Input area */}
      <div className="p-4 bg-surface/50 border-t border-border">
        {/* Quick chips — shown when only the welcome message exists */}
        {messages.length === 1 && (
          <div className="flex gap-2 mb-3 overflow-x-auto pb-1 scrollbar-hide" aria-label="Quick question suggestions">
            {QUICK_CHIPS.map((chip, i) => (
              <button
                key={i}
                onClick={() => handleSend(chip)}
                className="whitespace-nowrap px-3 py-1.5 rounded-full bg-background border border-border text-xs text-text-muted hover:text-text-main hover:border-accent/60 transition-colors"
              >
                {chip}
              </button>
            ))}
          </div>
        )}

        <div className="flex gap-2">
          <label htmlFor="assistant-input" className="sr-only">Ask your climate coach</label>
          <input
            id="assistant-input"
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend(input)}
            placeholder="Ask your climate coach..."
            disabled={loading}
            className="flex-1 bg-background border border-border rounded-full px-5 py-3 text-sm focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent disabled:opacity-50"
          />
          <Button
            onClick={() => handleSend(input)}
            disabled={!input.trim() || loading}
            size="icon"
            aria-label="Send message"
            className="rounded-full w-11 h-11 bg-accent hover:bg-accent/90 text-white flex-shrink-0"
          >
            {loading
              ? <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
              : <Send className="w-4 h-4" aria-hidden="true" />
            }
          </Button>
        </div>
      </div>
    </div>
  );
};
