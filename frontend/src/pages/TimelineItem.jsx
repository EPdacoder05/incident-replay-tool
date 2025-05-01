function TimelineItem({ event }) {
    return (
      <div className="border-l-4 border-blue-500 pl-4 ml-2 mb-4">
        <h3 className="text-md font-semibold text-blue-700 mb-1">{event.type}</h3>
        <p className="text-sm text-gray-500">
          {event.timestamp} · <span className="italic">{event.source}</span>
        </p>
        <p className="text-gray-700">{event.description}</p>
      </div>
    );
  }
  
  export default TimelineItem;
  