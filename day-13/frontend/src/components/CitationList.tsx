import type { Citation } from "../api/chat";

export function CitationList({ citations }: { citations: Citation[] }) {
  if (citations.length === 0) return null;

  const unique = Array.from(new Map(citations.map((c) => [`${c.source}#${c.section}`, c])).values());

  return (
    <div className="citations" aria-label="Sources">
      <span className="citations-label">Sources</span>
      {unique.map((c) => (
        <span className="citation-chip" key={`${c.source}#${c.section}`} title={c.section}>
          {c.source}
        </span>
      ))}
    </div>
  );
}
