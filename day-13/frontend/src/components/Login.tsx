import { useState, type FormEvent } from "react";
import { login, type LoginResult } from "../api/auth";
import { PitcherIcon } from "./PitcherIcon";

const DEMO_ACCOUNTS = [
  { username: "riya", kind: "customer" as const, label: "sees own orders" },
  { username: "arjun", kind: "customer" as const, label: "sees own orders" },
  { username: "kavya", kind: "customer" as const, label: "sees own orders" },
  { username: "admin", kind: "staff" as const, label: "sees every order" },
  { username: "manager", kind: "staff" as const, label: "sees every order" },
  { username: "sales", kind: "staff" as const, label: "sees every order" },
];

export function Login({ onLogin }: { onLogin: (result: LoginResult) => void }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const result = await login(username.trim(), password);
      onLogin(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setBusy(false);
    }
  }

  function fillAccount(name: string) {
    setUsername(name);
    setPassword(`${name}123`);
    setError(null);
  }

  return (
    <div className="login-screen">
      <form className="login-card" onSubmit={handleSubmit}>
        <div className="brand-mark login-mark" aria-hidden="true">
          <PitcherIcon />
        </div>
        <h1 className="login-title">Sign in to NimbusSupport</h1>
        <p className="login-sub">Account access is role-based — customers see only their own orders.</p>

        <label className="login-label" htmlFor="username">
          Username
        </label>
        <input
          id="username"
          className="login-input"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          autoFocus
          autoComplete="username"
        />

        <label className="login-label" htmlFor="password">
          Password
        </label>
        <input
          id="password"
          type="password"
          className="login-input"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="current-password"
        />

        {error && <p className="login-error">{error}</p>}

        <button className="login-submit" type="submit" disabled={busy || !username || !password}>
          {busy ? "Signing in…" : "Sign in"}
        </button>

        <div className="login-demo">
          <p className="login-demo-heading">Demo accounts — click to fill</p>
          <div className="login-demo-grid">
            {DEMO_ACCOUNTS.map((a) => (
              <button
                key={a.username}
                type="button"
                className="demo-chip"
                onClick={() => fillAccount(a.username)}
              >
                <span className="demo-chip-name">{a.username}</span>
                <span className={`demo-chip-role is-${a.kind}`}>
                  {a.kind} · {a.label}
                </span>
              </button>
            ))}
          </div>
        </div>
      </form>
    </div>
  );
}
