import { Link } from 'react-router-dom';

function NavBar() {
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
        <Link to="/" className="text-green-700 font-semibold hover:underline">
          Incident Replay Tool
        </Link>
      </div>
    </header>
  );
}

export default NavBar;
