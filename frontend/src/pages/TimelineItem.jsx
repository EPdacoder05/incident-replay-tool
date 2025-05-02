import { useState } from 'react';

function TimelineItem({ event }) {
  const [expanded, setExpanded] = useState(false);

  const isExpandable = event.errors || event.alerts || event.teams_logs;
  const toggleExpanded = () => setExpanded(!expanded);

  return (
    <div className="bg-white border border-gray-200 rounded shadow p-4 mb-4 relative">
      <div className="pl-4 border-l-4 border-transparent">
        {/* Solid stripe */}
        <div className="absolute top-0 bottom-0 left-0 w-1 rounded-l bg-quantum-green" />
  
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-md font-semibold text-quantum-green mb-1">{event.type}</h3>
            <p className="text-sm text-gray-500">
              {event.timestamp} · <span className="italic">{event.source}</span>
            </p>
            <p className="text-gray-700">{event.description}</p>
          </div>
          {isExpandable && (
            <button
              onClick={toggleExpanded}
              className="text-sm text-blue-600 hover:underline ml-4"
            >
              {expanded ? 'Hide Details' : 'Show Details'}
            </button>
          )}
        </div>
  
        {expanded && event.errors && (
          <div className="bg-gray-50 border rounded p-3 mt-3 text-sm text-gray-700">
            <strong>Error Logs:</strong>
            <ul className="list-disc ml-5 mt-1">
              {event.errors.map((err, idx) => (
                <li key={idx}>{err}</li>
              ))}
            </ul>
          </div>
        )}
  
        {expanded && event.alerts && (
          <div className="bg-gray-50 border rounded p-3 mt-3 text-sm text-gray-700">
            <strong>Pagers Sent:</strong>
            <ul className="list-disc ml-5 mt-1">
              {event.alerts.map((alert, idx) => (
                <li key={idx}>
                  {alert.recipient}{' '}
                  <span className="text-gray-500 text-xs italic">
                    — {new Date(alert.timestamp).toLocaleString()}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}
  
        {expanded && event.teams_logs && (
          <div className="bg-gray-50 border rounded p-3 mt-3 text-sm text-gray-700 space-y-1">
            <p><strong>Meeting Started:</strong> {event.teams_logs.meeting_started}</p>
            <p><strong>Meeting Ended:</strong> {event.teams_logs.meeting_ended}</p>
            <p><strong>Joined Users:</strong> {event.teams_logs.joined_users.join(", ")}</p>
            <div>
              <strong>Chat Log:</strong>
              <ul className="list-disc ml-5 mt-1">
                {event.teams_logs.chat_log.map((line, idx) => (
                  <li key={idx}>{line}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );      
}

export default TimelineItem;
