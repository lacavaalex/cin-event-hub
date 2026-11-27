import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import EventForm from "../components/events/EventForm";
import { ApiError, getEvent, toFieldErrors, updateEvent } from "../services/eventsApi";
import '../styles/admin.css';

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

  const [state, setState] = useState({ id: null, status: "loading", event: null });
  const [isSaving, setIsSaving] = useState(false);
  const [serverErrors, setServerErrors] = useState({}); 
  const [submitError, setSubmitError] = useState(""); 

  useEffect(() => {
    const controller = new AbortController();

    getEvent(id, controller.signal)
      .then((data) => setState({ id, status: "ready", event: data }))
      .catch((error) => {
        if (error.name === "AbortError") return; 
        setState({
          id,
          status: error.status === 404 ? "notFound" : "error",
          event: null,
        });
      });

    return () => controller.abort(); 
  }, [id]);

  const { status, event } = state.id === id
    ? state
    : { status: "loading", event: null };

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
    return <p role="status" className="admin-loading">Carregando evento…</p>;

  if (status === "notFound" || status === "error") {
    return (
      <section className="admin-page">
        <p role="alert" className="admin-form-error">
          {status === "notFound"
            ? "Este evento não existe mais."
            : "Não foi possível carregar o evento. Tente novamente em instantes."}
        </p>
        <button type="button" onClick={goToList} className="admin-secondary-button">
          Voltar à listagem
        </button>
      </section>
    );
  }

  return (
    <section className="admin-page">
      <h1 className="admin-title">Editar evento</h1>
      {submitError && (
        <p role="alert" className="admin-form-error">
          {submitError}
        </p>
      )}

      <EventForm
        key={id}
        initialValues={toFormValues(event)}
        onSubmit={handleSubmit}
        onCancel={goToList}
        isSubmitting={isSaving}
        serverErrors={serverErrors}
      />
    </section>
  );
}
