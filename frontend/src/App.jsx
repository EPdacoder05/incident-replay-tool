import { Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import IncidentDetail from './pages/IncidentDetail';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/incident/:id" element={<IncidentDetail />} />
    </Routes>
  );
}

export default App;
