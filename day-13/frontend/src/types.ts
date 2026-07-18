import type { Citation, ToolCallEvent } from "./api/chat";

export interface Message {
  id: string;
  role: "user" | "assistant";
  text: string;
  toolCalls: ToolCallEvent[];
  citations: Citation[];
  streaming: boolean;
  error?: string;
}
