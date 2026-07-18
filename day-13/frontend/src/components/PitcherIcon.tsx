/* The NimbusSupport lemonade pitcher — jug with a lemon slice. */
export function PitcherIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {/* jug body */}
      <path d="M7 3.5h10l-.9 14.2a2.4 2.4 0 0 1-2.4 2.3h-3.4a2.4 2.4 0 0 1-2.4-2.3L7 3.5Z" />
      {/* spout */}
      <path d="M7 3.5 5.2 6.2" />
      {/* handle */}
      <path d="M17 7.2c2.7.4 2.7 4.8 0 5.2" />
      {/* lemon slice */}
      <circle cx="11.9" cy="12.4" r="2.7" />
      <path d="M11.9 9.7v5.4M9.2 12.4h5.4" />
    </svg>
  );
}
