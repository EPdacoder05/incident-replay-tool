import { Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import IncidentDetail from './pages/IncidentDetail';
import NavBar from './pages/NavBar';

function App() {
  return (
  <>
    <NavBar />
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/incident/:id" element={<IncidentDetail />} />
    </Routes>
  </>
  );
}

export default App;
