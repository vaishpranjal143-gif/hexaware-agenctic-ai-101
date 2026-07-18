import { useState } from "react";
import type { LoginResult } from "./api/auth";
import { streamChat } from "./api/chat";
import { ChatWindow } from "./components/ChatWindow";
import { PitcherIcon } from "./components/PitcherIcon";
import { Composer } from "./components/Composer";
import { Login } from "./components/Login";
import type { Message } from "./types";

function newId(): string {
  return crypto.randomUUID();
}

export default function App() {
  const [auth, setAuth] = useState<LoginResult | null>(null);
  const [conversationId, setConversationId] = useState(() => newId());
  const [messages, setMessages] = useState<Message[]>([]);
  const [busy, setBusy] = useState(false);

  function updateMessage(id: string, patch: Partial<Message>) {
    setMessages((prev) => prev.map((m) => (m.id === id ? { ...m, ...patch } : m)));
  }

  function handleLogin(result: LoginResult) {
    setAuth(result);
    setConversationId(newId()); // fresh thread per login, never shared across accounts
    setMessages([]);
  }

  function handleLogout() {
    setAuth(null);
    setMessages([]);
  }

  async function handleSend(text: string) {
    if (!auth) return;
    const userMessage: Message = {
      id: newId(),
      role: "user",
      text,
      toolCalls: [],
      citations: [],
      streaming: false,
    };
    const assistantId = newId();
    const assistantMessage: Message = {
      id: assistantId,
      role: "assistant",
      text: "",
      toolCalls: [],
      citations: [],
      streaming: true,
    };
    setMessages((prev) => [...prev, userMessage, assistantMessage]);
    setBusy(true);

    let text_ = "";
    const toolCalls: Message["toolCalls"] = [];

    await streamChat(auth.token, conversationId, text, {
      onToken: (chunk) => {
        text_ += chunk;
        updateMessage(assistantId, { text: text_ });
      },
      onToolCall: (call) => {
        toolCalls.push(call);
        updateMessage(assistantId, { toolCalls: [...toolCalls] });
      },
      onCitations: (citations) => updateMessage(assistantId, { citations }),
      onError: (message) => updateMessage(assistantId, { error: message, streaming: false }),
      onDone: () => updateMessage(assistantId, { streaming: false }),
    });

    updateMessage(assistantId, { streaming: false });
    setBusy(false);
  }

  if (!auth) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand">
          <span className="brand-mark">
            <PitcherIcon />
          </span>
          <div>
            <div className="brand-name">NimbusSupport</div>
            <div className="brand-sub">
              {auth.displayName} <span className="role-tag">{auth.role}</span>
            </div>
          </div>
        </div>
        <div className="header-actions">
          <div className="status-pill">
            <span className="status-dot" aria-hidden="true" />
            Online
          </div>
          <button className="logout-button" onClick={handleLogout}>
            Log out
          </button>
        </div>
      </header>

      <main className="app-main">
        <ChatWindow messages={messages} onSuggestion={busy ? undefined : handleSend} />
      </main>

      <footer className="app-footer">
        <Composer disabled={busy} onSend={handleSend} />
        <p className="footer-note">
          NimbusSupport answers from NimbusMart's policy library and order records — it will say
          when it doesn't know something rather than guess, and only shows orders you're allowed
          to see.
        </p>
      </footer>
    </div>
  );
}
