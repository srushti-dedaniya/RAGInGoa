import Navbar from "../../components/Navbar/Navbar";
import Hero from "../../components/Hero/Hero";
import WhyQueryGoa from "./WhyQueryGoa";
import FinalCTA from "./FinalCTA";
import Footer from "../../components/Footer/Footer";

export default function Landing() {
  return (
    <main className="relative overflow-x-hidden min-h-screen">
      <div
        aria-hidden="true"
        className="absolute inset-0"
        style={{
          backgroundImage: "url('/rag-background.jpeg')",
          backgroundSize: "cover",
          backgroundPosition: "center top",
          backgroundRepeat: "no-repeat",
          backgroundAttachment: "scroll",
        }}
      />
      <div aria-hidden="true" className="absolute inset-0 bg-cream/70" />
      <div className="relative z-10">
        <Navbar />
        <Hero />
        <WhyQueryGoa />
        <FinalCTA />
        <Footer />
      </div>
    </main>
  );
}