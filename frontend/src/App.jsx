import { useEffect, useState } from "react";

function App() {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/incidents")
      .then((res) => res.json())
      .then((data) => {
        setIncidents(data);
        console.log("Fetched incidents:", data);

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
        <ul className="space-y-6">
  {incidents.map((item, idx) => (
    <li key={idx} className="relative pl-6 border-l-2 border-blue-500">
      <div className="absolute left-0 top-1.5 w-3 h-3 bg-blue-500 rounded-full"></div>
      <div className="bg-white p-4 rounded shadow-sm">
        <p className="text-xs text-gray-500">{item.timestamp}</p>
        <h2 className="text-lg font-bold">{item.type}</h2>
        <p className="text-sm text-gray-600">
          <span className="font-semibold">Source:</span> {item.source}
        </p>
        <p className="text-gray-800 mt-1">{item.description}</p>
      </div>
    </li>
  ))}
</ul>

      )}
    </div>
  );
}

export default App;
