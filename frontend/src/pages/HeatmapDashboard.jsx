import { useEffect, useState, useRef } from 'react';
import html2pdf from 'html2pdf.js';

function HeatmapDashboard() {
  const [incidents, setIncidents] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [allCategories, setAllCategories] = useState([]);
  const tableRef = useRef();

  useEffect(() => {
    fetch('/mockData.json')
      .then((res) => res.json())
      .then((data) => {
        setIncidents(data);

        const categories = Array.from(new Set(data.map(i => i.category || 'Uncategorized')));
        setAllCategories(categories);
        setSelectedCategories(categories);

        const dates = data.map((i) => new Date(i.date));
        const earliest = new Date(Math.min(...dates)).toISOString().split('T')[0];
        const latest = new Date().toISOString().split('T')[0];

        setStartDate(earliest);
        setEndDate(latest);
      });
  }, []);

  useEffect(() => {
    const filtered = incidents.filter((incident) => {
      const date = new Date(incident.date);
      const afterStart = !startDate || new Date(startDate) <= date;
      const beforeEnd = !endDate || date <= new Date(endDate);
      const matchesCategory = selectedCategories.includes(incident.category);
      return afterStart && beforeEnd && matchesCategory;
    });

    const matrix = {};
    filtered.forEach((incident) => {
      const date = new Date(incident.date);
      const hour = date.getHours().toString().padStart(2, '0') + ':00';
      const category = incident.category || 'Uncategorized';

      if (!matrix[hour]) matrix[hour] = {};
      if (!matrix[hour][category]) matrix[hour][category] = 0;
      matrix[hour][category]++;
    });

    const structured = Object.entries(matrix)
      .map(([hour, catCounts]) => {
        const row = { hour };
        selectedCategories.forEach((cat) => {
          row[cat] = catCounts[cat] || 0;
        });
        return row;
      })
      .sort((a, b) => a.hour.localeCompare(b.hour));

    setFilteredData(structured);
  }, [incidents, startDate, endDate, selectedCategories]);

  const handleCategoryChange = (category) => {
    setSelectedCategories((prev) =>
      prev.includes(category)
        ? prev.filter((c) => c !== category)
        : [...prev, category]
    );
  };

  const setPreset = (daysBack) => {
    const now = new Date();
    if (daysBack === 'year') {
      const first = new Date(now.getFullYear(), 0, 1);
      setStartDate(first.toISOString().split('T')[0]);
    } else {
      const past = new Date();
      past.setDate(now.getDate() - daysBack);
      setStartDate(past.toISOString().split('T')[0]);
    }
    setEndDate(now.toISOString().split('T')[0]);
  };

  const clearFilters = () => {
    const categories = Array.from(new Set(incidents.map(i => i.category || 'Uncategorized')));
    setSelectedCategories(categories);

    const dates = incidents.map((i) => new Date(i.date));
    const earliest = new Date(Math.min(...dates)).toISOString().split('T')[0];
    const latest = new Date(Math.max(...dates)).toISOString().split('T')[0];

    setStartDate(earliest);
    setEndDate(latest);
  };

  const exportToPDF = () => {
    if (!tableRef.current) return;
    html2pdf().set({
      margin: 0.3,
      filename: 'IncidentHeatmap.pdf',
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2 },
      jsPDF: { unit: 'in', format: 'letter', orientation: 'landscape' }
    }).from(tableRef.current).save();
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6 font-sans">
      <div className="w-full bg-quantum-green py-3 mb-6 rounded shadow">
        <h1 className="text-2xl font-bold text-white text-center">Incident Heatmap</h1>
      </div>

      <div className="max-w-6xl mx-auto space-y-6">
        {/* Filters */}
        <div className="bg-white border border-gray-200 rounded shadow p-4">
          <h2 className="text-lg font-semibold text-quantum-green mb-2">Filters</h2>

          <div className="flex flex-wrap gap-4 mb-4 items-center">
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">Start Date</label>
              <input
                type="date"
                className="border rounded px-2 py-1"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">End Date</label>
              <input
                type="date"
                className="border rounded px-2 py-1"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>

            <div className="flex gap-2 items-end">
              <button onClick={() => setPreset(7)} className="text-sm text-blue-600 hover:underline">Last 7 Days</button>
              <button onClick={() => setPreset(30)} className="text-sm text-blue-600 hover:underline">Last 30 Days</button>
              <button onClick={() => setPreset('year')} className="text-sm text-blue-600 hover:underline">Current Year</button>
              <button onClick={clearFilters} className="text-sm text-red-600 hover:underline ml-4">Clear Filters</button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-2">Categories</label>
            <div className="flex flex-wrap gap-3">
              {allCategories.map((category) => (
                <label key={category} className="flex items-center gap-1 text-sm">
                  <input
                    type="checkbox"
                    className="accent-quantum-green"
                    checked={selectedCategories.includes(category)}
                    onChange={() => handleCategoryChange(category)}
                  />
                  {category}
                </label>
              ))}
            </div>
          </div>
        </div>

        {/* Export + Heatmap Table */}
        <div className="flex justify-end">
          <button
            onClick={exportToPDF}
            className="bg-quantum-green text-white px-4 py-2 rounded hover:bg-green-700 transition"
          >
            Export to PDF
          </button>
        </div>

        {filteredData.length === 0 ? (
          <p className="text-center text-gray-500">No data for selected filters.</p>
        ) : (
          <div className="overflow-x-auto" ref={tableRef}>
            <table className="min-w-full border border-gray-300 bg-white rounded shadow text-sm">
              <thead className="bg-quantum-green text-white">
                <tr>
                  <th className="text-left px-4 py-2">Hour</th>
                  {selectedCategories.map((cat) => (
                    <th key={cat} className="text-left px-4 py-2">{cat}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filteredData.map((row) => (
                  <tr key={row.hour} className="even:bg-gray-50">
                    <td className="px-4 py-2 font-medium text-gray-700">{row.hour}</td>
                    {selectedCategories.map((cat) => {
                      const count = row[cat];
                      const intensity = Math.min(255, 40 + count * 35);
                      return (
                        <td
                          key={cat}
                          className="px-4 py-2 text-center font-semibold"
                          style={{
                            backgroundColor: `rgb(255, ${255 - intensity}, ${255 - intensity})`,
                            color: count > 0 ? '#000' : '#999'
                          }}
                        >
                          {count}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default HeatmapDashboard;
