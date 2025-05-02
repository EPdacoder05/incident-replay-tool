import { useParams, Link } from 'react-router-dom';
import { useEffect, useState } from 'react';
import TimelineItem from './TimelineItem';
import TimelineFilter from './TimelineFilter';

function IncidentDetail() {
  const { id } = useParams();
  const [incident, setIncident] = useState(null);
  const [activeTypes, setActiveTypes] = useState([]);
  const [allTypes, setAllTypes] = useState([]);
  const [showSummary, setShowSummary] = useState(false);

  const [editSummary, setEditSummary] = useState(false);
  const [editFix, setEditFix] = useState(false);
  const [editedSummary, setEditedSummary] = useState({});
  const [editedFix, setEditedFix] = useState('');

  useEffect(() => {
    fetch('/mockData.json')
      .then((res) => res.json())
      .then((data) => {
        const found = data.find((inc) => inc.id === id);
        if (found) {
          setIncident(found);
          const types = Array.from(new Set(found.timeline.map(e => e.type)));
          setAllTypes(types);
          setActiveTypes(types);
          setEditedSummary(found.post_incident_summary || {});
        }
      });
  }, [id]);

  const toggleType = (type) => {
    setActiveTypes((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
    );
  };

  const toggleAll = (selectAll) => {
    setActiveTypes(selectAll ? allTypes : []);
  };

  const handleSummaryChange = (field, value) => {
    setEditedSummary((prev) => ({ ...prev, [field]: value }));
  };

  const handleFixChange = (value) => {
    setEditedFix(value);
  };

  const saveSummary = () => {
    console.log('Saving updated summary:', editedSummary);
    setEditSummary(false);
  };

  const saveFix = () => {
    console.log('Saving updated fix implemented:', editedFix);
    setEditFix(false);
  };

  if (!incident) return <div className="p-6">Loading...</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-6 font-sans">
      {/* Header */}
      <div className="w-full bg-gradient-to-r from-quantum-yellow via-quantum-green to-quantum-yellow py-3 mb-6 rounded shadow">
        <h1 className="text-2xl font-bold text-white text-center">Incident Detail</h1>
      </div>

      <div className="max-w-6xl mx-auto flex flex-col lg:flex-row gap-6">
        {/* Sidebar */}
        <div className="lg:w-1/4 w-full space-y-4 sticky top-6 self-start">
          <TimelineFilter
            allTypes={allTypes}
            activeTypes={activeTypes}
            toggleType={toggleType}
            toggleAll={toggleAll}
          />
        </div>

        {/* Main Content */}
        <div className="lg:w-3/4 w-full space-y-6">
          <Link to="/" className="text-blue-600 hover:underline text-sm">&larr; Back</Link>

          <h2 className="text-xl font-bold text-gray-800">{incident.title}</h2>
          <p className="text-gray-700 mb-1">{incident.description}</p>
          <p className="text-sm italic text-gray-500">
            Category: {incident.category} · Assignment Group: {incident.assignment_group}
          </p>

          {/* Post-Incident Summary */}
          <div className="bg-white border border-gray-200 rounded shadow p-4">
            <div className="flex justify-between items-center mb-2">
              <h3 className="text-lg font-semibold text-quantum-green">Post-Incident Summary</h3>
              <button
                onClick={() => setEditSummary(!editSummary)}
                className="text-sm text-blue-600 hover:underline"
              >
                {editSummary ? 'Cancel Edit' : 'Edit'}
              </button>
            </div>
            <button
              onClick={() => setShowSummary(!showSummary)}
              className="text-blue-600 hover:underline text-sm mb-2"
            >
              {showSummary ? 'Hide Summary' : 'Show Summary'}
            </button>

            {showSummary && (
              <div className="space-y-2 text-sm text-gray-700 mt-2">
                {Object.entries(incident.post_incident_summary || {}).map(([key, value]) => {
                  const editable = ['root_cause', 'recovery', 'prevention_plan'].includes(key);
                  return (
                    <div key={key}>
                      <strong className="capitalize">{key.replace(/_/g, ' ')}:</strong>{' '}
                      {editSummary && editable ? (
                        <textarea
                          className="w-full h-28 border rounded p-2 text-sm resize-y"
                          value={editedSummary[key] || ''}
                          onChange={(e) => handleSummaryChange(key, e.target.value)}
                        />
                      ) : (
                        <span>{editedSummary[key] || '—'}</span>
                      )}
                    </div>
                  );
                })}
                {editSummary && (
                  <div className="flex justify-end mt-2">
                    <button
                      onClick={saveSummary}
                      className="bg-quantum-green text-white px-4 py-2 rounded hover:bg-green-700 transition"
                    >
                      Save Summary
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Timeline */}
          <div>
            <h3 className="text-lg font-semibold text-quantum-green mb-2">Timeline</h3>
            {incident.timeline
              .filter((event) => activeTypes.includes(event.type))
              .map((event, idx) => {
                if (event.type === 'Fix Implemented') {
                  return (
                    <div key={idx} className="bg-white border border-gray-200 rounded shadow p-4 mb-4 relative">
                      <div className="absolute top-0 bottom-0 left-0 w-1 rounded-l bg-gradient-to-b from-quantum-yellow via-quantum-green to-quantum-yellow" />
                      <div className="flex justify-between items-start">
                        <div className="w-full">
                          <h3 className="text-md font-semibold text-quantum-green mb-1">{event.type}</h3>
                          <p className="text-sm text-gray-500">
                            {event.timestamp} · <span className="italic">{event.source}</span>
                          </p>
                          {editFix ? (
                            <textarea
                              className="w-full h-28 border rounded p-2 mt-2 text-sm resize-y"
                              value={editedFix || event.description}
                              onChange={(e) => handleFixChange(e.target.value)}
                            />
                          ) : (
                            <p className="text-gray-700 mt-2">{editedFix || event.description}</p>
                          )}
                        </div>
                        <button
                          onClick={() => setEditFix(!editFix)}
                          className="text-sm text-blue-600 hover:underline ml-4"
                        >
                          {editFix ? 'Cancel Edit' : 'Edit'}
                        </button>
                      </div>
                      {editFix && (
                        <div className="flex justify-end mt-2">
                          <button
                            onClick={saveFix}
                            className="bg-quantum-green text-white px-4 py-2 rounded hover:bg-green-700 transition"
                          >
                            Save Fix
                          </button>
                        </div>
                      )}
                    </div>
                  );
                }

                return <TimelineItem key={idx} event={event} />;
              })}
          </div>
        </div>
      </div>
    </div>
  );
}

export default IncidentDetail;
