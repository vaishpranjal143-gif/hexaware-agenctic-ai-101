export interface ToolCallEvent {
  plugin: string;
  function: string;
  args: Record<string, string>;
  blocked: boolean;
}

export interface Citation {
  source: string;
  section: string;
}

export interface ChatHandlers {
  onToken: (text: string) => void;
  onToolCall: (call: ToolCallEvent) => void;
  onCitations: (citations: Citation[]) => void;
  onError: (message: string) => void;
  onDone: () => void;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

// The backend streams Server-Sent Events over a POST response.
// EventSource can't send a POST body, so we parse the SSE wire format
// (`event: <name>\ndata: <json>\n\n`) by hand from the fetch stream.
export async function streamChat(
  token: string,
  conversationId: string,
  message: string,
  handlers: ChatHandlers,
  signal?: AbortSignal
): Promise<void> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}/api/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ conversation_id: conversationId, message }),
      signal,
    });
  } catch {
    handlers.onError("Couldn't reach NimbusSupport. Is the backend running?");
    return;
  }

  if (response.status === 401) {
    handlers.onError("Your session expired — please log in again.");
    return;
  }
  if (!response.ok || !response.body) {
    handlers.onError(`Request failed (${response.status})`);
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const events = buffer.split("\n\n");
    buffer = events.pop() ?? "";

    for (const raw of events) {
      let eventName = "message";
      let data = "";
      for (const line of raw.split("\n")) {
        if (line.startsWith("event:")) eventName = line.slice(6).trim();
        else if (line.startsWith("data:")) data += line.slice(5).trim();
      }
      if (!data) continue;
      const payload = JSON.parse(data);

      switch (eventName) {
        case "token":
          handlers.onToken(payload.text);
          break;
        case "tool_call":
          handlers.onToolCall(payload as ToolCallEvent);
          break;
        case "citations":
          handlers.onCitations(payload.citations as Citation[]);
          break;
        case "error":
          handlers.onError(payload.message);
          break;
        case "done":
          handlers.onDone();
          break;
      }
    }
  }
}
