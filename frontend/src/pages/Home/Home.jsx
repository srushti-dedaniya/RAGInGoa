import Navbar from "../../components/Navbar/Navbar";
import Hero from "../../components/Hero/Hero";
import QueryWorkspace from "../../components/QueryWorkspace/QueryWorkspace";
import Footer from "../../components/Footer/Footer";

export default function Home() {
  return (
    <main className="relative overflow-x-hidden min-h-screen">
      <Navbar />
      <Hero />
      <QueryWorkspace />
      <Footer />
    </main>
  );
}
