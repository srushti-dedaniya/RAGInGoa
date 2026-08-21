import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { RAGProvider } from "./context/RAGContext";
import Landing from "./pages/Landing/Landing";
import Ask from "./pages/Ask/Ask";
import Destinations from "./pages/Destinations/Destinations";
import About from "./pages/About/About";

export default function App() {
  return (
    <RAGProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/ask" element={<Ask />} />
          <Route path="/destinations" element={<Destinations />} />
          <Route path="/about" element={<About />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </RAGProvider>
  );
}