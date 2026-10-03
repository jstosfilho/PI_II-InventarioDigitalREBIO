import MapView from "@/components/MapView";
import RegistroList from "@/components/RegistroList";

export default function Home() {
  return (
    <main className="flex h-screen w-screen">
      <aside className="w-1/2 overflow-y-auto border-r border-gray-200">
        <RegistroList />
      </aside>
      <section className="w-1/2">
        <MapView />
      </section>
    </main>
  );
}
