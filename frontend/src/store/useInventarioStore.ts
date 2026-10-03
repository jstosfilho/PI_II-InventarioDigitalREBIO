import { create } from "zustand";

export interface Registro {
  id: number;
}

interface InventarioState {
  registros: Registro[];
  selecionadoId: number | null;
  selecionar: (id: number | null) => void;
}

export const useInventarioStore = create<InventarioState>((set) => ({
  registros: [],
  selecionadoId: null,
  selecionar: (id) => set({ selecionadoId: id }),
}));
