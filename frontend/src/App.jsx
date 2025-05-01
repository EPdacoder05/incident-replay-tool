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
    <div className="min-h-screen bg-gray-100 px-6 py-10 font-sans">
      <h1 className="text-4xl font-bold text-center text-blue-800 mb-10">
        Incident Timeline
      </h1>

      {loading ? (
        <p className="text-center text-gray-500">Loading...</p>
      ) : (
        <ul className="relative border-l-2 border-blue-500 max-w-3xl mx-auto list-none space-y-10">
          {incidents.map((item, idx) => (
            <li key={idx} className="relative pl-8">
              <div className="absolute top-2 left-0 w-4 h-4 bg-blue-600 rounded-full border-4 border-white shadow-md"></div>
              <div className="bg-white rounded-md shadow-sm p-5">
                <p className="text-xs text-gray-500">{item.timestamp}</p>
                <h2 className="text-lg font-semibold text-blue-700">{item.type}</h2>
                <p className="text-sm text-gray-700">
                  <strong>Source:</strong> {item.source}
                </p>
                <p className="mt-2 text-gray-800">{item.description}</p>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default App;
