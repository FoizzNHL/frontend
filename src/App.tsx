import { useState } from "react";
import { Link, Outlet, useLocation } from "react-router-dom";

function App() {
  const location = useLocation();
  const [open, setOpen] = useState(false);

  const navItems = [
    { path: "/", label: "NHL" },
    { path: "/tests", label: "LED Tests" },
    { path: "/bets-editor", label: "Bets editor" }
  ];

  const isActive = (p) => location.pathname === p;

  return (
    <div className="min-h-screen flex flex-col text-white relative">
      {/* Icey backdrop */}
      <div className="absolute inset-0 -z-10 bg-linear-to-br from-[#002f6c] via-[#0a2a57] to-[#8b0018]" />
      <div className="pointer-events-none absolute inset-0 -z-10 opacity-20
        bg-[radial-gradient(1000px_500px_at_50%_-10%,rgba(255,255,255,0.20),transparent_60%),radial-gradient(800px_400px_at_20%_80%,rgba(255,255,255,0.10),transparent_60%)]" />
      {/* Rink stripes */}
      <div className="absolute left-0 right-0 top-0 h-0.5 bg-white/70 -z-10" />
      <div className="absolute left-0 right-0 top-2 h-1.5 bg-[#af1e2d] -z-10" />
      <div className="absolute left-0 right-0 top-[18px] h-px bg-white/40 -z-10" />

      {/* NAVBAR */}
      <nav className="sticky top-0 z-20 backdrop-blur-xl border-b border-white/10 bg-white/5">
        <div className="max-w-6xl mx-auto px-4">
          <div className="h-16 flex items-center justify-between">
            {/* Brand */}
            <Link to="/" className="flex items-center gap-2">
              <span className="text-2xl">🏒</span>
              <span className="text-xl md:text-2xl font-extrabold tracking-wide">
                NHL Game Lights
              </span>
            </Link>

            {/* Desktop menu */}
            <ul className="hidden md:flex items-center gap-2">
              {navItems.map(({ path, label }) => (
                <li key={path}>
                  <Link
                    to={path}
                    className={[
                      "px-3 py-2 rounded-xl font-semibold transition shadow-sm",
                      "ring-1 ring-inset",
                      isActive(path)
                        ? "bg-gradient-to-r from-[#af1e2d] to-[#002f6c] ring-white/20"
                        : "bg-white/5 hover:bg-white/10 ring-white/10"
                    ].join(" ")}
                  >
                    {label}
                  </Link>
                </li>
              ))}
            </ul>

            {/* Mobile toggle */}
            <button
              onClick={() => setOpen((v) => !v)}
              className="md:hidden inline-flex items-center justify-center w-10 h-10 rounded-xl bg-white/10 ring-1 ring-white/15"
              aria-label="Toggle menu"
            >
              <svg viewBox="0 0 24 24" className="w-6 h-6">
                <path
                  d={open ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"}
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </button>
          </div>

          {/* Mobile drawer */}
          {open && (
            <ul className="md:hidden pb-4 space-y-2">
              {navItems.map(({ path, label }) => (
                <li key={path}>
                  <Link
                    to={path}
                    onClick={() => setOpen(false)}
                    className={[
                      "block px-3 py-2 rounded-xl font-semibold transition shadow-sm",
                      "ring-1 ring-inset",
                      isActive(path)
                        ? "bg-gradient-to-r from-[#af1e2d] to-[#002f6c] ring-white/20"
                        : "bg-white/5 hover:bg-white/10 ring-white/10"
                    ].join(" ")}
                  >
                    {label}
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </div>
      </nav>

      {/* MAIN */}
      <main className="flex-grow max-w-6xl mx-auto w-full px-4 py-8">
        <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl p-5 shadow-xl">
          <Outlet />
        </div>
      </main>

      {/* FOOTER stripes */}
      <footer className="px-4 pb-6">
        <div className="max-w-6xl mx-auto">
          <p className="mt-3 text-center text-sm text-white/70">
            © {new Date().getFullYear()} Goal Light
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
