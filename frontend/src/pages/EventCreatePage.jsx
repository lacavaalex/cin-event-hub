import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import EventForm from '../components/events/EventForm';
import { ApiError, createEvent, toFieldErrors } from '../services/eventsApi';
import '../styles/admin.css';

const EMPTY_VALUES = {
  title: '',
  description: '',
  date: '',
  time: '',
  location: '',
  event_type: '',
  registration_link: '',
};

export default function EventCreatePage() {
  const navigate = useNavigate();
  const [isSaving, setIsSaving] = useState(false);
  const [serverErrors, setServerErrors] = useState({});
  const [submitError, setSubmitError] = useState('');

  const goToList = () => navigate('/admin/events');

  async function handleSubmit(values) {
    setIsSaving(true);
    setServerErrors({});
    setSubmitError('');

    try {
      await createEvent(values);
      navigate('/admin/events', { state: { flash: 'Evento criado com sucesso.' } });
    } catch (error) {
      const fieldErrors = error instanceof ApiError ? toFieldErrors(error.detail) : {};
      setServerErrors(fieldErrors);
      if (Object.keys(fieldErrors).length === 0) {
        setSubmitError(
          error instanceof ApiError ? error.message : 'Não foi possível conectar ao servidor.'
        );
      }
      setIsSaving(false);
    }
  }

  return (
    <section className="admin-page">
      <h1 className="admin-title">Novo evento</h1>
      {submitError && (
        <p role="alert" className="admin-form-error">
          {submitError}
        </p>
      )}

      <EventForm
        initialValues={EMPTY_VALUES}
        onSubmit={handleSubmit}
        onCancel={goToList}
        isSubmitting={isSaving}
        serverErrors={serverErrors}
        submitLabel="Criar evento"
      />
    </section>
  );
}
