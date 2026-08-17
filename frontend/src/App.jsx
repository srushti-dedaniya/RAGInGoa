import { RAGProvider } from "./context/RAGContext";
import Home from "./pages/Home/Home";

export default function App() {
  return (
    <RAGProvider>
      <Home />
    </RAGProvider>
  );
}
