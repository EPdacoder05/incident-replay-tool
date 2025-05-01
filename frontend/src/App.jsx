import { useEffect, useState } from "react";

function App() {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/incidents")
      .then((res) => res.json())
      .then((data) => {
        setIncidents(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch incidents:", err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <h1 className="text-3xl font-bold mb-4">Incident Timeline</h1>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <ul className="space-y-4">
          {incidents.map((item, idx) => (
            <li
              key={idx}
              className="bg-white shadow p-4 rounded border-l-4 border-blue-500"
            >
              <p className="text-sm text-gray-500">{item.timestamp}</p>
              <p className="font-semibold">{item.type}</p>
              <p className="text-sm">
                <strong>Source:</strong> {item.source}
              </p>
              <p>{item.description}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default App;
