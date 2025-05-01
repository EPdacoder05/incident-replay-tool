import { useFilter } from './FilterContext';

function DurationFilter() {
  const {
    activeDurations,
    toggleDuration,
    allDurations
  } = useFilter();

  const colorDot = (label) => {
    if (label === "<1hr") return "bg-green-500";
    if (label === "1-2hr") return "bg-yellow-400";
    if (label === "2+hr") return "bg-red-500";
  };

  const labelText = {
    "<1hr": "Less than 1 hour",
    "1-2hr": "Between 1 and 2 hours",
    "2+hr": "More than 2 hours"
  };

  return (
    <div className="bg-white border border-gray-200 p-4 shadow-quantum rounded">
      <h2 className="text-md font-semibold text-quantum-green mb-2">Duration Filters</h2>

      <div className="flex justify-between mb-2 text-sm">
        <button
          onClick={() =>
            allDurations.forEach((d) => {
              if (!activeDurations.includes(d)) toggleDuration(d);
            })
          }
          className="text-quantum-green hover:underline"
        >
          Select All
        </button>
        <button
          onClick={() => activeDurations.forEach(toggleDuration)}
          className="text-red-500 hover:underline"
        >
          Clear All
        </button>
      </div>

      <div className="flex flex-col space-y-2">
        {allDurations.map((label) => (
          <label key={label} className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={activeDurations.includes(label)}
              onChange={() => toggleDuration(label)}
              className="accent-quantum-green"
            />
            <span className={`w-3 h-3 rounded-full ${colorDot(label)}`} />
            <span className="text-sm">{labelText[label]}</span>
          </label>
        ))}
      </div>
    </div>
  );
}

export default DurationFilter;
