function TimelineFilter({ allTypes, activeTypes, toggleType, toggleAll }) {
    return (
      <div className="bg-white border border-gray-200 p-4 shadow-quantum rounded">
        <h2 className="text-md font-semibold text-quantum-green mb-2">Timeline Event Filters</h2>
        <div className="flex justify-between mb-2 text-sm">
          <button
            onClick={() => toggleAll(true)}
            className="text-quantum-green hover:underline"
          >
            Select All
          </button>
          <button
            onClick={() => toggleAll(false)}
            className="text-red-500 hover:underline"
          >
            Clear All
          </button>
        </div>
        <div className="flex flex-col space-y-2">
          {allTypes.map((type) => (
            <label key={type} className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={activeTypes.includes(type)}
                onChange={() => toggleType(type)}
                className="accent-quantum-green"
              />
              <span className="text-sm">{type}</span>
            </label>
          ))}
        </div>
      </div>
    );
  }
  
  export default TimelineFilter;
  