import { Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import IncidentDetail from './pages/IncidentDetail';
import NavBar from './pages/NavBar';
import AlertDashboard from './pages/AlertDashboard';
import HeatmapDashboard from './pages/HeatmapDashboard';

function App() {
  return (
  <>
    <NavBar />
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/alerts" element={<AlertDashboard />} />
      <Route path="/dashboard" element={<HeatmapDashboard />} />
      <Route path="/incident/:id" element={<IncidentDetail />} />
    </Routes>
  </>
  );
}

export default App;
