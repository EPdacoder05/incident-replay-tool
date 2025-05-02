import { Link, useLocation } from 'react-router-dom';

function NavBar() {
  const location = useLocation();

  const linkStyle = (path) =>
    `text-sm font-semibold text-green-700 hover:underline ${
      location.pathname === path ? 'underline' : ''
    }`;

  return (
    <header className="bg-white shadow mb-6">
      <div className="max-w-6xl mx-auto flex items-center justify-between px-4 py-3">
        <a
          href="https://quantum-health.com"
          target="_blank"
          rel="noopener noreferrer"
        >
          <img
            src="/assets/quantum-logo.png"
            alt="Quantum Health Logo"
            className="h-8"
          />
        </a>

        <div className="flex items-center gap-6">
          <Link to="/" className={linkStyle('/')}>
            Incident Replay Tool
          </Link>
          <Link to="/alerts" className={linkStyle('/alerts')}>
            Error Monitor
          </Link>
          <Link to="/dashboard" className={linkStyle('/dashboard')}>
            Heatmap
          </Link>

        </div>
      </div>
    </header>
  );
}

export default NavBar;
