import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import RegistroList from "./RegistroList";

describe("RegistroList", () => {
  it("mostra a mensagem de lista vazia", () => {
    render(<RegistroList />);
    expect(screen.getByText("Nenhum registro cadastrado.")).toBeInTheDocument();
  });
});
