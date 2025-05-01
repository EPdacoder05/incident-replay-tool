import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useFilter } from './FilterContext';
import EventTypeFilter from './EventTypeFilter';
import PostIncidentPreview from './PostIncidentPreview';
import DurationFilter from './DurationFilter';

function Home() {
  const [incidents, setIncidents] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedYear, setSelectedYear] = useState('All');
  const [availableYears, setAvailableYears] = useState([]);

  const {
    activeTypes,
    activeCategories,
    activeDurations,
    toggleCategory,
    allCategories
  } = useFilter();

  useEffect(() => {
    fetch('/mockData.json')
      .then((res) => res.json())
      .then((data) => {
        setIncidents(data);
        setFiltered(data);

        const years = Array.from(
          new Set(data.map(i => new Date(i.date).getFullYear()))
        ).sort((a, b) => b - a);
        setAvailableYears(years);
      })
      .catch(console.error);
  }, []);

  useEffect(() => {
    let result = [...incidents];

    if (searchTerm.trim()) {
      result = result.filter((incident) =>
        incident.title.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (selectedYear !== 'All') {
      result = result.filter(
        (incident) =>
          new Date(incident.date).getFullYear().toString() === selectedYear
      );
    }

    // Duration filter logic
    result = result.filter((incident) => {
      if (!incident.timeline || incident.timeline.length < 2) return false;

      const start = new Date(incident.timeline[0]?.timestamp);
      const end = new Date(incident.timeline[incident.timeline.length - 1]?.timestamp);
      const minutes = (end - start) / 1000 / 60;

      if (minutes <= 60 && activeDurations.includes("<1hr")) return true;
      if (minutes > 60 && minutes <= 120 && activeDurations.includes("1-2hr")) return true;
      if (minutes > 120 && activeDurations.includes("2+hr")) return true;

      return false;
    });

    setFiltered(result);
  }, [searchTerm, selectedYear, incidents, activeDurations]);

  return (
    <div className="min-h-screen bg-gray-50 p-6 font-sans">
      {/* Gradient Title Bar */}
      <div className="w-full bg-gradient-to-r from-quantum-yellow via-quantum-green to-quantum-yellow py-3 mb-6 rounded shadow">
        <h1 className="text-2xl font-bold text-white text-center">
          Major Incidents
        </h1>
      </div>
  
      <div className="flex flex-col lg:flex-row gap-6 max-w-6xl mx-auto">
        {/* Sidebar Filters */}
        <div className="lg:w-1/4 w-full space-y-6 sticky top-6 self-start">
          {/* Category Filters */}
          <div className="bg-white border border-gray-200 p-4 shadow-quantum rounded">
            <h2 className="text-md font-semibold text-quantum-green mb-2">Category Filters</h2>
  
            <div className="flex justify-between mb-2 text-sm">
              <button
                onClick={() => allCategories.forEach((cat) => {
                  if (!activeCategories.includes(cat)) toggleCategory(cat);
                })}
                className="text-quantum-green hover:underline"
              >
                Select All
              </button>
              <button
                onClick={() => activeCategories.forEach(toggleCategory)}
                className="text-red-500 hover:underline"
              >
                Clear All
              </button>
            </div>
  
            <div className="flex flex-col space-y-2">
              {allCategories.map((category) => (
                <label key={category} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={activeCategories.includes(category)}
                    onChange={() => toggleCategory(category)}
                    className="accent-quantum-green"
                  />
                  <span className="text-sm">{category}</span>
                </label>
              ))}
            </div>
          </div>
  
          {/* Duration Filters */}
          <DurationFilter />
  
          {/* Event Filters */}
          <EventTypeFilter />
        </div>
  
        {/* Main Content Area */}
        <div className="lg:w-3/4 w-full">
          {/* Search and Year Filters */}
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <input
              type="text"
              placeholder="Search by title..."
              className="p-2 border border-gray-300 rounded w-full sm:w-2/3"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <select
              className="p-2 border border-gray-300 rounded w-full sm:w-1/3"
              value={selectedYear}
              onChange={(e) => setSelectedYear(e.target.value)}
            >
              <option value="All">All Years</option>
              {availableYears.map((year) => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
          </div>
  
          {/* Incident Cards */}
          <div className="space-y-4">
            {filtered.length === 0 ? (
              <p className="text-center text-gray-500">No incidents found.</p>
            ) : (
              filtered.map((incident) => {
                const start = new Date(incident.timeline[0]?.timestamp);
                const end = new Date(incident.timeline[incident.timeline.length - 1]?.timestamp);
                const durationMinutes = (end - start) / 1000 / 60;
  
                let color = 'bg-green-500';
                if (durationMinutes > 120) color = 'bg-red-500';
                else if (durationMinutes > 60) color = 'bg-yellow-400';
  
                return (
                  <div
                    key={incident.id}
                    className="bg-white border border-gray-200 p-4 rounded shadow-quantum transition-transform hover:scale-[1.01]"
                  >
                    <div className="flex items-center justify-between">
                      <Link to={`/incident/${incident.id}`} className="hover:underline">
                        <h2 className="text-lg font-semibold text-gray-800">{incident.title}</h2>
                        <p className="text-sm text-gray-500">
                          {new Date(incident.date).toLocaleDateString(undefined, {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric'
                          })}
                        </p>
                      </Link>
                      <span className="text-xs bg-quantum-green text-white font-semibold px-2 py-1 rounded-full shadow">
                        {incident.category}
                      </span>
                    </div>
  
                    <div className="mt-2 flex items-center gap-2">
                      <span className={`w-3 h-3 rounded-full ${color}`} />
                      <span className="text-xs text-gray-500">
                        Duration: {Math.round(durationMinutes)} min
                      </span>
                    </div>
  
                    {incident.post_incident_summary && (
                      <PostIncidentPreview
                        incidentId={incident.id}
                        summary={incident.post_incident_summary}
                      />
                    )}
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </div>
  );  
}

export default Home;
