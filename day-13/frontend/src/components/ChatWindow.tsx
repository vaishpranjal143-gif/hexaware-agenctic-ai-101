import { useEffect, useRef } from "react";
import type { Message } from "../types";
import { PitcherIcon } from "./PitcherIcon";
import { MessageBubble } from "./MessageBubble";

const SUGGESTIONS = [
  "What's the status of my order?",
  "Can I return opened earbuds?",
  "Do you store my credit card details?",
];

export function ChatWindow({
  messages,
  onSuggestion,
}: {
  messages: Message[];
  onSuggestion?: (text: string) => void;
}) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages]);

  return (
    <div className="chat-window">
      {messages.length === 0 && (
        <div className="empty-state">
          <div className="empty-cloud" aria-hidden="true">
            <PitcherIcon />
          </div>
          <p className="empty-title">How can we help today?</p>
          <p className="empty-hint">
            Ask about your orders, returns, warranties, or anything in NimbusMart's policies.
          </p>
          <div className="suggestions">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                className="suggestion-chip"
                onClick={() => onSuggestion?.(s)}
                disabled={!onSuggestion}
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}
      {messages.map((m) => (
        <MessageBubble key={m.id} message={m} />
      ))}
      <div ref={endRef} />
    </div>
  );
}
