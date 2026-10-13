import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import EventForm from "../components/events/EventForm";
import { ApiError, getEvent, toFieldErrors, updateEvent } from "../services/eventsApi";

// Rota da listagem de eventos do admin. Ajustar para a rota real do projeto.
const EVENTS_LIST_PATH = "/admin/events";

// A API devolve time como "14:00:00"; <input type="time"> trabalha com "14:00".
function toFormValues(event) {
  return {
    title: event.title,
    description: event.description,
    date: event.date, // "AAAA-MM-DD", formato que <input type="date"> espera
    time: event.time.slice(0, 5),
    location: event.location,
    event_type: event.event_type,
    registration_link: event.registration_link,
  };
}

export default function EventEditPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [event, setEvent] = useState(null);
  const [status, setStatus] = useState("loading"); 
  const [isSaving, setIsSaving] = useState(false);
  const [serverErrors, setServerErrors] = useState({}); 
  const [submitError, setSubmitError] = useState(""); 

  useEffect(() => {
    const controller = new AbortController();
    setStatus("loading");

    getEvent(id, controller.signal)
      .then((data) => {
        setEvent(data);
        setStatus("ready");
      })
      .catch((error) => {
        if (error.name === "AbortError") return; 
        setStatus(error.status === 404 ? "notFound" : "error");
      });

    return () => controller.abort(); 
  }, [id]);

  const goToList = () => navigate(EVENTS_LIST_PATH);

  async function handleSubmit(values) {
    setIsSaving(true);
    setServerErrors({});
    setSubmitError("");

    try {
      await updateEvent(id, values);
      navigate(EVENTS_LIST_PATH, { state: { flash: "Evento atualizado com sucesso." } });
    } catch (error) {
      const fieldErrors = error instanceof ApiError ? toFieldErrors(error.detail) : {};
      setServerErrors(fieldErrors);
      if (Object.keys(fieldErrors).length === 0) {
        setSubmitError(
          error instanceof ApiError ? error.message : "Não foi possível conectar ao servidor."
        );
      }
      setIsSaving(false); 
    }
  }

  if (status === "loading")
    return <p className="p-6 text-sm text-gray-600">Carregando evento…</p>;

  if (status === "notFound" || status === "error") {
    return (
      <main className="mx-auto max-w-2xl p-6">
        <p role="alert" className="text-sm text-red-600">
          {status === "notFound"
            ? "Este evento não existe mais."
            : "Não foi possível carregar o evento. Tente novamente em instantes."}
        </p>
        <button type="button" onClick={goToList}
          className="mt-4 rounded-md border border-gray-300 px-4 py-2 text-sm font-medium
                     text-gray-700 hover:bg-gray-50">
          Voltar à listagem
        </button>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-2xl p-6">
      <h1 className="mb-6 text-2xl font-semibold text-gray-900">Editar evento</h1>
      {submitError && (
        <p role="alert" className="mb-4 text-sm text-red-600">
          {submitError}
        </p>
      )}

      <EventForm
        initialValues={toFormValues(event)}
        onSubmit={handleSubmit}
        onCancel={goToList}
        isSubmitting={isSaving}
        serverErrors={serverErrors}
      />
    </main>
  );
}
