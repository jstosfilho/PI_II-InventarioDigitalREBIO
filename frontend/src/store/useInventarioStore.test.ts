import { beforeEach, describe, expect, it } from "vitest";
import { useInventarioStore } from "./useInventarioStore";

describe("useInventarioStore", () => {
  beforeEach(() => {
    useInventarioStore.setState({ registros: [], selecionadoId: null });
  });

  it("começa vazio e sem seleção", () => {
    const s = useInventarioStore.getState();
    expect(s.registros).toEqual([]);
    expect(s.selecionadoId).toBeNull();
  });

  it("seleciona e limpa um registro", () => {
    useInventarioStore.getState().selecionar(3);
    expect(useInventarioStore.getState().selecionadoId).toBe(3);
    useInventarioStore.getState().selecionar(null);
    expect(useInventarioStore.getState().selecionadoId).toBeNull();
  });
});
