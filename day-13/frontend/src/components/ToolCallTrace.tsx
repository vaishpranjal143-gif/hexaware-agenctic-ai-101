import type { ToolCallEvent } from "../api/chat";

function formatArgs(args: Record<string, string>): string {
  const entries = Object.entries(args);
  if (entries.length === 0) return "";
  return entries.map(([k, v]) => `${k}=${v}`).join(", ");
}

export function ToolCallTrace({ calls }: { calls: ToolCallEvent[] }) {
  if (calls.length === 0) return null;
  return (
    <div className="trace" role="log" aria-label="Tools NimbusSupport used">
      <div className="trace-heading">Agent activity</div>
      <ul className="trace-list">
        {calls.map((call, i) => (
          <li key={i} className={`trace-row${call.blocked ? " trace-row-blocked" : ""}`}>
            <span className="trace-dot" aria-hidden="true" />
            <span className="trace-call">
              {call.plugin}.{call.function}({formatArgs(call.args)})
            </span>
            {call.blocked && <span className="trace-blocked-tag">blocked</span>}
          </li>
        ))}
      </ul>
    </div>
  );
}
