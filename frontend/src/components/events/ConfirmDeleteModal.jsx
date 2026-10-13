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
      className="w-full max-w-sm rounded-lg p-6 shadow-xl backdrop:bg-black/50"
    >
      <h2 id="delete-modal-title" className="text-lg font-semibold text-gray-900">
        Excluir evento?
      </h2>
      <p id="delete-modal-description" className="mt-2 text-sm text-gray-600">
        "{eventTitle}" será removido definitivamente. Esta ação não pode ser desfeita.
      </p>

      {error && (
        <p role="alert" className="mt-3 text-sm text-red-600">
          {error}
        </p>
      )}

      <div className="mt-6 flex justify-end gap-3">
        <button type="button" onClick={onCancel} disabled={isDeleting}
          className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium
                     text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
          Cancelar
        </button>
        <button type="button" onClick={onConfirm} disabled={isDeleting}
          className="rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white
                     hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed">
          {isDeleting ? "Excluindo…" : "Excluir evento"}
        </button>
      </div>
    </dialog>
  );
}
