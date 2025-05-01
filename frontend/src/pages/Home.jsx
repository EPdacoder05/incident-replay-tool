import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

function Home() {
  const [incidents, setIncidents] = useState([]);

  useEffect(() => {
    fetch('/mockData.json')
      .then((res) => res.json())
      .then((data) => setIncidents(data))
      .catch(console.error);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <h1 className="text-3xl font-bold text-center text-blue-700 mb-6">Major Incidents</h1>
      <div className="max-w-4xl mx-auto space-y-4">
        {incidents.map((incident) => (
          <Link
            to={`/incident/${incident.id}`}
            key={incident.id}
            className="block bg-white p-4 rounded shadow hover:bg-blue-50 transition"
          >
            <h2 className="text-lg font-semibold">{incident.title}</h2>
            <p className="text-sm text-gray-500">
              {new Date(incident.date).toLocaleDateString(undefined, {
                year: "numeric",
                month: "long",
                day: "numeric"
              })}
            </p>
          </Link>
        ))}
      </div>
    </div>
  );
}

export default Home;
