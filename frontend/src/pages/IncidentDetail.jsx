import { useParams, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";

function IncidentDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [incident, setIncident] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/mockData.json")
      .then((res) => res.json())
      .then((data) => {
        const found = data.find((item) => item.id === id);
        setIncident(found);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load incident:", err);
        setLoading(false);
      });
  }, [id]);

  if (loading) return <p className="text-center mt-10">Loading...</p>;

  if (!incident)
    return <p className="text-center text-red-500 mt-10">Incident not found.</p>;

  return (
    <div className="min-h-screen bg-gray-100 p-6">
        <button
            onClick={() => navigate(-1)}
            className="mb-4 text-blue-600 hover:underline text-sm"
        >
            ← Back
        </button>
      <h1 className="text-2xl font-bold text-blue-700 mb-4">{incident.title}</h1>
      <p className="text-gray-600 mb-6">{incident.description}</p>

      <ul className="space-y-4">
        {incident.timeline.map((event, idx) => (
          <li key={idx} className="relative pl-6 border-l-2 border-blue-500">
            <div className="absolute left-0 top-1.5 w-3 h-3 bg-blue-500 rounded-full"></div>
            <div className="bg-white p-4 rounded shadow-sm">
              <p className="text-xs text-gray-500">{event.timestamp}</p>
              <h2 className="text-lg font-bold">{event.type}</h2>
              <p className="text-sm text-gray-600">
                <span className="font-semibold">Source:</span> {event.source}
              </p>
              <p className="text-gray-800 mt-1">{event.description}</p>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default IncidentDetail;
