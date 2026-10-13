import { describe, test, expect, vi, afterEach } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import FavoriteButton from "../../../src/components/events/FavoriteButton";
import { favoriteEvent, unfavoriteEvent } from "../../../src/services/eventsApi";

vi.mock("../../../src/services/eventsApi");

describe("FavoriteButton (US 6.1)", () => {
  afterEach(() => vi.clearAllMocks());

  test(
    "Dado um evento não favoritado, quando o usuário clica, " +
      "então favorita via API e o ícone fica ativo",
    async () => {
      favoriteEvent.mockResolvedValueOnce({ event_id: 1, is_favorited: true });

      render(<FavoriteButton eventId={1} initialIsFavorited={false} />);
      const button = screen.getByRole("button");
      expect(button).toHaveAttribute("aria-pressed", "false");

      fireEvent.click(button);

      expect(button).toHaveAttribute("aria-pressed", "true");
      await waitFor(() => expect(favoriteEvent).toHaveBeenCalledWith(1));
      expect(unfavoriteEvent).not.toHaveBeenCalled();
    }
  );

  test(
    "Dado um evento favoritado, quando o usuário clica, " +
      "então remove via API e o ícone fica inativo",
    async () => {
      unfavoriteEvent.mockResolvedValueOnce({ event_id: 1, is_favorited: false });

      render(<FavoriteButton eventId={1} initialIsFavorited={true} />);
      const button = screen.getByRole("button");
      expect(button).toHaveAttribute("aria-pressed", "true");

      fireEvent.click(button);

      expect(button).toHaveAttribute("aria-pressed", "false");
      await waitFor(() => expect(unfavoriteEvent).toHaveBeenCalledWith(1));
      expect(favoriteEvent).not.toHaveBeenCalled();
    }
  );

  test("se a chamada à API falhar ao favoritar, o ícone volta ao estado anterior", async () => {
    favoriteEvent.mockRejectedValueOnce(new Error("network error"));

    render(<FavoriteButton eventId={1} initialIsFavorited={false} />);
    const button = screen.getByRole("button");

    fireEvent.click(button);
    expect(button).toHaveAttribute("aria-pressed", "true"); 

    await waitFor(() => expect(button).toHaveAttribute("aria-pressed", "false")); 
  });

  test("chama onChange com o novo estado após o sucesso da API", async () => {
    favoriteEvent.mockResolvedValueOnce({ event_id: 1, is_favorited: true });
    const handleChange = vi.fn();

    render(<FavoriteButton eventId={1} initialIsFavorited={false} onChange={handleChange} />);
    fireEvent.click(screen.getByRole("button"));

    await waitFor(() => expect(handleChange).toHaveBeenCalledWith(true));
  });

  test("ignora cliques repetidos enquanto uma chamada está em andamento", async () => {
    let resolveCall;
    favoriteEvent.mockReturnValueOnce(
      new Promise((resolve) => {
        resolveCall = resolve;
      })
    );

    render(<FavoriteButton eventId={1} initialIsFavorited={false} />);
    const button = screen.getByRole("button");

    fireEvent.click(button); // dispara a chamada
    fireEvent.click(button); // deveria ser ignorado: isSaving ainda é true
    fireEvent.click(button);

    resolveCall({ event_id: 1, is_favorited: true });
    await waitFor(() => expect(favoriteEvent).toHaveBeenCalledTimes(1));
  });
});