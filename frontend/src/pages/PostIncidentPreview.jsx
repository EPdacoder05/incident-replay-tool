import { useState } from 'react';
import { Link } from 'react-router-dom';

function PostIncidentPreview({ incidentId, summary }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="mt-2">
      <button
        onClick={() => setExpanded(!expanded)}
        className="text-blue-600 text-sm hover:underline focus:outline-none"
      >
        {expanded ? 'Hide' : 'Show'} Post-Incident Summary
      </button>

      {expanded && (
        <div className="mt-2 bg-gray-100 border border-gray-300 rounded p-4 text-sm text-gray-800 space-y-2">
          <div><strong>Summary:</strong> {summary.summary}</div>
          <div><strong>Root Cause:</strong> {summary.root_cause}</div>
          <div><strong>Timeline:</strong> {summary.timeline}</div>
          <div><strong>Impact:</strong> {summary.impact}</div>
          <div><strong>Detection:</strong> {summary.detection}</div>
          <div><strong>Response:</strong> {summary.response}</div>
          <div><strong>Recovery:</strong> {summary.recovery}</div>
          <div><strong>Prevention Plan:</strong> {summary.prevention_plan}</div>
          <div>
            <Link
              to={`/incident/${incidentId}`}
              className="text-blue-500 hover:underline text-sm"
            >
              View full details →
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}

export default PostIncidentPreview;
