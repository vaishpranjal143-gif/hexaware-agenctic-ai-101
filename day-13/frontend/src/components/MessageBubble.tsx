import type { ReactNode } from "react";
import type { Message } from "../types";
import { PitcherIcon } from "./PitcherIcon";
import { ToolCallTrace } from "./ToolCallTrace";
import { CitationList } from "./CitationList";

/* Render the light markdown the agent actually emits — **bold** and `code` —
   without pulling in a markdown library. Everything else stays plain text. */
function renderRich(text: string): ReactNode[] {
  return text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g).map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith("`") && part.endsWith("`")) {
      return <code key={i}>{part.slice(1, -1)}</code>;
    }
    return part;
  });
}

export function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";
  const thinking = message.streaming && !message.text && !message.error;

  return (
    <div className={`message-row ${isUser ? "message-row-user" : "message-row-assistant"}`}>
      {!isUser && (
        <div className="avatar" aria-hidden="true">
          <PitcherIcon />
        </div>
      )}
      <div className="message-col">
        {!isUser && message.toolCalls.length > 0 && <ToolCallTrace calls={message.toolCalls} />}
        <div className={`bubble ${isUser ? "bubble-user" : "bubble-assistant"}`}>
          {message.error ? (
            <span className="bubble-error">{message.error}</span>
          ) : thinking ? (
            <span className="typing" aria-label="NimbusSupport is typing">
              <span />
              <span />
              <span />
            </span>
          ) : (
            <>
              {renderRich(message.text)}
              {message.streaming && <span className="cursor" aria-hidden="true" />}
            </>
          )}
        </div>
        {!isUser && <CitationList citations={message.citations} />}
      </div>
    </div>
  );
}
