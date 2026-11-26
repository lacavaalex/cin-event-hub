import { useEffect, useRef } from "react";

export default function ConfirmDeleteModal({
  eventTitle,
  isDeleting = false,
  error = "",
  onConfirm,
  onCancel,
}) {
  const dialogRef = useRef(null);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (dialog && !dialog.open) dialog.showModal();
  }, []);

  const handleDialogCancel = (event) => {
    event.preventDefault();
    if (!isDeleting) onCancel();
  };

  return (
    <dialog
      ref={dialogRef}
      onCancel={handleDialogCancel}
      aria-labelledby="delete-modal-title"
      aria-describedby="delete-modal-description"
      className="confirm-delete-modal"
    >
      <h2 id="delete-modal-title" className="confirm-delete-title">
        Excluir evento?
      </h2>
      <p id="delete-modal-description" className="confirm-delete-description">
        "{eventTitle}" será removido definitivamente. Esta ação não pode ser desfeita.
      </p>

      {error && (
        <p role="alert" className="confirm-delete-error">
          {error}
        </p>
      )}

      <div className="confirm-delete-actions">
        <button type="button" onClick={onCancel} disabled={isDeleting}
          className="admin-secondary-button">
          Cancelar
        </button>
        <button type="button" onClick={onConfirm} disabled={isDeleting}
          className="admin-danger-button">
          {isDeleting ? "Excluindo…" : "Excluir evento"}
        </button>
      </div>
    </dialog>
  );
}
