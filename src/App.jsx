import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/Home.jsx";
import Processing from "./pages/Processing.jsx";
import Outputs from "./pages/Outputs.jsx";
import Results from "./pages/Results.jsx";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/processing/:type" element={<Processing />} />
        <Route path="/outputs" element={<Outputs />} />
        <Route path="/results" element={<Results />} />
      </Routes>
    </Router>
  );
}

export default App;
