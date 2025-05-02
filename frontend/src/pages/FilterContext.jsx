import { createContext, useContext, useState } from 'react';

const allEventTypes = [
  "Error Log Spike",
  "Ticket Spike",
  "MI Proposed",
  "MI Approved",
  "Banner Posted",
  "PagerDuty Alert Sent",
  "Teams Channel Created",
  "Fix Implemented",
];

const allDurations = ["<1hr", "1-2hr", "2+hr"];

const FilterContext = createContext();

export function FilterProvider({ children }) {
  const [allCategories, setAllCategories] = useState([]);
  const [activeCategories, setActiveCategories] = useState([]);

  const [activeTypes, setActiveTypes] = useState(allEventTypes);
  const [activeDurations, setActiveDurations] = useState(allDurations);

  const toggleCategory = (category) => {
    setActiveCategories((prev) =>
      prev.includes(category)
        ? prev.filter((c) => c !== category)
        : [...prev, category]
    );
  };

  const toggleType = (type) => {
    setActiveTypes((prev) =>
      prev.includes(type)
        ? prev.filter((t) => t !== type)
        : [...prev, type]
    );
  };

  const toggleDuration = (range) => {
    setActiveDurations((prev) =>
      prev.includes(range)
        ? prev.filter((d) => d !== range)
        : [...prev, range]
    );
  };

  const selectAllCategories = () => setActiveCategories(allCategories);
  const clearAllCategories = () => setActiveCategories([]);

  return (
    <FilterContext.Provider
      value={{
        allEventTypes,
        activeTypes,
        toggleType,

        allCategories,
        setAllCategories,
        activeCategories,
        setActiveCategories,
        toggleCategory,
        selectAllCategories,
        clearAllCategories,

        allDurations,
        activeDurations,
        toggleDuration
      }}
    >
      {children}
    </FilterContext.Provider>
  );
}

export function useFilter() {
  return useContext(FilterContext);
}
