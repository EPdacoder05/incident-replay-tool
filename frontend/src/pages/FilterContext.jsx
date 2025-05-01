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

const allCategories = [
  "Member Website",
  "Authorizations",
  "Database"
];

const allDurations = [
  "<1hr",
  "1-2hr",
  "2+hr"
];

const FilterContext = createContext();

export function FilterProvider({ children }) {
  const [activeTypes, setActiveTypes] = useState(allEventTypes);
  const [activeCategories, setActiveCategories] = useState(allCategories);
  const [activeDurations, setActiveDurations] = useState(allDurations);

  const toggleType = (type) => {
    setActiveTypes((prev) =>
      prev.includes(type)
        ? prev.filter((t) => t !== type)
        : [...prev, type]
    );
  };

  const toggleCategory = (category) => {
    setActiveCategories((prev) =>
      prev.includes(category)
        ? prev.filter((c) => c !== category)
        : [...prev, category]
    );
  };

  const toggleDuration = (range) => {
    setActiveDurations((prev) =>
      prev.includes(range)
        ? prev.filter((d) => d !== range)
        : [...prev, range]
    );
  };

  return (
    <FilterContext.Provider
      value={{
        activeTypes,
        toggleType,
        allEventTypes,
        activeCategories,
        toggleCategory,
        allCategories,
        activeDurations,
        toggleDuration,
        allDurations
      }}
    >
      {children}
    </FilterContext.Provider>
  );
}

export function useFilter() {
  return useContext(FilterContext);
}
