"use client";

import { useInventarioStore } from "@/store/useInventarioStore";

export default function RegistroList() {
  const registros = useInventarioStore((s) => s.registros);

  return (
    <div className="p-4">
      <h1 className="text-xl font-semibold">Inventário Digital</h1>
      {registros.length === 0 ? (
        <p className="mt-4 text-gray-500">Nenhum registro cadastrado.</p>
      ) : (
        <ul className="mt-4" />
      )}
    </div>
  );
}
