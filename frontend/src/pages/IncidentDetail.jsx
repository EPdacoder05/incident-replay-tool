import { useParams, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useFilter } from './FilterContext';
import TimelineItem from './TimelineItem';
import EventTypeFilter from './EventTypeFilter';

function IncidentDetail() {
  const { id } = useParams();
  const [incident, setIncident] = useState(null);
  const navigate = useNavigate();
  const { activeTypes } = useFilter();

  useEffect(() => {
    fetch('/mockData.json')
      .then((res) => res.json())
      .then((data) => {
        const found = data.find((item) => item.id === id);
        setIncident(found);
      });
  }, [id]);

  if (!incident) return <div className="p-6">Loading...</div>;

  const filteredTimeline = incident.timeline.filter(event =>
    activeTypes.includes(event.type)
  );

  const summary = incident.post_incident_summary;

  return (
    <div className="min-h-screen bg-gray-50 p-6 font-sans">
      <button
        onClick={() => navigate(-1)}
        className="mb-4 text-quantum-green hover:underline"
      >
        ← Back
      </button>

      <h1 className="text-2xl font-bold text-quantum-green mb-1">{incident.title}</h1>
      <p className="text-gray-700 mb-1">{incident.description}</p>
      <p className="text-sm text-gray-500 mb-6 italic">
        Category: {incident.category} · Assignment Group: {incident.assignment_group}
      </p>

      <div className="max-w-4xl mb-6">
        <EventTypeFilter />
      </div>

      <div className="max-w-4xl mb-10">
        <h2 className="text-xl font-semibold text-quantum-green mb-2">Timeline</h2>
        {filteredTimeline.length === 0 ? (
          <p className="text-gray-500 italic">No events match your filters.</p>
        ) : (
          filteredTimeline.map((event, index) => (
            <TimelineItem key={index} event={event} />
          ))
        )}
      </div>

      <div className="max-w-4xl bg-white border border-gray-200 shadow-quantum rounded p-6">
        <h2 className="text-xl font-bold text-quantum-green mb-4">Post-Incident Summary</h2>
        <div className="space-y-4 text-sm text-gray-800">
          <div><strong>Summary:</strong> <p>{summary.summary}</p></div>
          <div><strong>Root Cause:</strong> <p>{summary.root_cause}</p></div>
          <div><strong>Timeline:</strong> <p>{summary.timeline}</p></div>
          <div><strong>Impact:</strong> <p>{summary.impact}</p></div>
          <div><strong>Detection:</strong> <p>{summary.detection}</p></div>
          <div><strong>Response:</strong> <p>{summary.response}</p></div>
          <div><strong>Recovery:</strong> <p>{summary.recovery}</p></div>
          <div><strong>Prevention Plan:</strong> <p>{summary.prevention_plan}</p></div>
        </div>
      </div>
    </div>
  );
}

export default IncidentDetail;
