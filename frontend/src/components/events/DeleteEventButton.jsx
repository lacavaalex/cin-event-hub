import { useState } from "react";
import { ApiError, deleteEvent } from "../../services/eventsApi";
import ConfirmDeleteModal from "./ConfirmDeleteModal";

export default function DeleteEventButton({ event, onDeleted }) {
  const [isOpen, setIsOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState("");

  const closeModal = () => {
    setIsOpen(false);
    setError("");
  };

  async function handleConfirm() {
    setIsDeleting(true);
    setError("");

    try {
      await deleteEvent(event.id);
    } catch (err) {
      if (!(err instanceof ApiError && err.status === 404)) {
        setError(
          err instanceof ApiError ? err.message : "Não foi possível conectar ao servidor."
        );
        setIsDeleting(false); // mantém o modal aberto para tentar de novo
        return;
      }
    }

    setIsDeleting(false);
    setIsOpen(false);
    onDeleted(event);
  }

  return (
    <>
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        aria-label={`Excluir evento ${event.title}`}
        className="rounded-md border border-red-300 px-3 py-1.5 text-sm font-medium
                   text-red-600 hover:bg-red-50"
      >
        Excluir
      </button>

      {isOpen && (
        <ConfirmDeleteModal
          eventTitle={event.title}
          isDeleting={isDeleting}
          error={error}
          onConfirm={handleConfirm}
          onCancel={closeModal}
        />
      )}
    </>
  );
}
