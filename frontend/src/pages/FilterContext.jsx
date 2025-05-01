import { createContext, useContext, useState } from 'react';

const allEventTypes = [
  "Error Log Spike",
  "Ticket Spike",
  "MI Proposed",
  "MI Approved",
  "Banner Posted",
  "Teams Channel Created",
  "Fix Implemented",
];

const allCategories = [
  "Member Website",
  "Authorizations",
  "Database"
];

const FilterContext = createContext();

export function FilterProvider({ children }) {
  const [activeTypes, setActiveTypes] = useState(allEventTypes);
  const [activeCategories, setActiveCategories] = useState(allCategories);

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

  return (
    <FilterContext.Provider
      value={{
        activeTypes,
        toggleType,
        allEventTypes,
        activeCategories,
        toggleCategory,
        allCategories
      }}
    >
      {children}
    </FilterContext.Provider>
  );
}

export function useFilter() {
  return useContext(FilterContext);
}
