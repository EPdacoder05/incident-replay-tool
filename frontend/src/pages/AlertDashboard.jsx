import { useEffect, useState } from 'react';

function AlertDashboard() {
  const [alerts, setAlerts] = useState([]);
  const [logHistory, setLogHistory] = useState([]);

  // Simulate incoming error log data (normally from Dynatrace, Splunk, etc.)
  const generateMockLogs = () => {
    const services = ['AuthService', 'APIGateway', 'DBWriter', 'Emailer', 'CacheSync'];
    return Array.from({ length: 5 }, (_, i) => ({
      timestamp: new Date().toISOString(),
      source: ['Splunk', 'Dynatrace', 'OpenSearch'][Math.floor(Math.random() * 3)],
      service: services[i],
      errors: Math.floor(Math.random() * 50), // Random error count between 0-49
    }));
  };

  // Check for error spikes (you can adjust the logic here)
  const detectSpikes = (newLogs) => {
    const newAlerts = [];

    newLogs.forEach((log) => {
      const prev = logHistory.find(
        (h) => h.service === log.service && h.source === log.source
      );
      if (!prev || log.errors > prev.errors * 1.8 || log.errors > 40) {
        newAlerts.push(log);
      }
    });

    return newAlerts;
  };

  useEffect(() => {
    const interval = setInterval(() => {
      const newLogs = generateMockLogs();
      setLogHistory(newLogs);
      const spikes = detectSpikes(newLogs);

      if (spikes.length > 0) {
        setAlerts((prev) => [
          ...spikes.map((spike) => ({
            ...spike,
            id: `${spike.service}-${Date.now()}`
          })),
          ...prev,
        ]);
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [logHistory]);

  return (
    <div className="min-h-screen bg-gray-50 p-6 font-sans">
      <div className="w-full bg-gradient-to-r from-quantum-yellow via-quantum-green to-quantum-yellow py-3 mb-6 rounded shadow">
        <h1 className="text-2xl font-bold text-white text-center">Error Spike Monitor</h1>
      </div>

      <div className="max-w-5xl mx-auto">
        {alerts.length === 0 ? (
          <p className="text-center text-gray-500 text-sm">No spikes detected... yet. 🎯</p>
        ) : (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {alerts.map((alert) => (
              <div key={alert.id} className="bg-white border border-red-300 rounded shadow p-4">
                <h2 className="text-lg font-semibold text-red-600">
                  {alert.service}
                </h2>
                <p className="text-sm text-gray-500 italic">
                  {alert.source} · {new Date(alert.timestamp).toLocaleTimeString()}
                </p>
                <p className="text-sm mt-2 text-gray-700">
                  🚨 <strong>{alert.errors}</strong> errors detected
                </p>
                <button
                  className="mt-3 text-sm text-blue-600 hover:underline"
                  onClick={() => alert(`(Future) Pre-fill MI with ${alert.service}`)}
                >
                  Create MI from this
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default AlertDashboard;
