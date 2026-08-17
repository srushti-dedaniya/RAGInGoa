import Navbar from "../../components/Navbar/Navbar";
import Hero from "../../components/Hero/Hero";
import QueryWorkspace from "../../components/QueryWorkspace/QueryWorkspace";
import PipelineSection from "../../components/Pipeline/PipelineSection";
import Chunking from "../../components/Chunking/Chunking";
import Guardrails from "../../components/Guardrails/Guardrails";
import Benchmark from "../../components/Benchmark/Benchmark";
import SystemStatus from "../../components/SystemStatus/SystemStatus";
import Footer from "../../components/Footer/Footer";

export default function Home() {
  return (
    <main className="relative overflow-x-hidden min-h-screen">
      <Navbar />
      <Hero />
      <QueryWorkspace />
      <PipelineSection />
      <Chunking />
      <Guardrails />
      <Benchmark />
      <SystemStatus />
      <Footer />
    </main>
  );
}
