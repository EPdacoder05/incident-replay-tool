import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';

function IncidentDetail() {
  const { id } = useParams();
  const [incident, setIncident] = useState(null);

  useEffect(() => {
    fetch('/mockData.json') // Same JSON file
      .then((res) => res.json())
      .then((data) => {
        const selected = data.find((item) => item.id === parseInt(id));
        setIncident(selected);
      })
      .catch(console.error);
  }, [id]);

  if (!incident) return <p className="text-center mt-10">Loading...</p>;

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <Link to="/" className="text-blue-600 underline mb-4 inline-block">&larr; Back</Link>
      <h1 className="text-2xl font-bold text-blue-700 mb-4">{incident.title}</h1>
      <p className="text-gray-600 mb-6">{incident.description}</p>

      <ul className="space-y-4">
        {incident.events.map((event, idx) => (
          <li key={idx} className="border-l-4 border-blue-500 pl-4">
            <p className="text-sm text-gray-500">{new Date(event.timestamp).toLocaleString()}</p>
            <h2 className="text-lg font-semibold">{event.type}</h2>
            <p className="text-sm text-gray-600">
              <span className="font-semibold">Source:</span> {event.source}
            </p>
            <p className="text-gray-800">{event.description}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default IncidentDetail;
