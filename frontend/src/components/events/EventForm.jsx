import { useState } from "react";

const EVENT_TYPES = ["Palestra", "Workshop", "Hackathon", "Outro"];

const todayISO = () => new Date().toLocaleDateString("sv-SE");

function validate(values, originalDate) {
  const errors = {};
  if (!values.title.trim()) errors.title = "Informe o título do evento.";
  if (!values.description.trim()) errors.description = "Informe a descrição do evento.";
  if (!values.date) errors.date = "Informe a data do evento.";
  else if (values.date !== originalDate && values.date < todayISO())
    errors.date = "A data do evento não pode estar no passado.";
  if (!values.time) errors.time = "Informe o horário do evento.";
  if (!values.location.trim()) errors.location = "Informe o local do evento.";
  if (!values.event_type) errors.event_type = "Selecione o tipo do evento.";
  if (!values.registration_link.trim())
    errors.registration_link = "Informe o link de inscrição.";
  return errors;
}

const inputClasses = (hasError) =>
  `mt-1 block w-full rounded-md border px-3 py-2 text-sm shadow-sm
   focus:outline-none focus:ring-2 focus:ring-indigo-500
   ${hasError ? "border-red-500" : "border-gray-300"}`;

function Field({ id, label, error, children }) {
  return (
    <div className="mb-4">
      <label htmlFor={id} className="block text-sm font-medium text-gray-700">
        {label}
      </label>
      {children}
      {error && (
        <span role="alert" className="mt-1 block text-sm text-red-600">
          {error}
        </span>
      )}
    </div>
  );
}

export default function EventForm({
  initialValues,
  onSubmit,
  onCancel,
  isSubmitting = false,
  serverErrors = {},
}) {
  const [values, setValues] = useState(initialValues);
  const [clientErrors, setClientErrors] = useState({});
  const handleChange = (event) => {
    const { name, value } = event.target;
    setValues((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault(); // evita o reload da página
    const found = validate(values, initialValues.date);
    setClientErrors(found);
    if (Object.keys(found).length === 0) onSubmit(values);
  };

  const errors = { ...clientErrors, ...serverErrors };

  return (
    <form onSubmit={handleSubmit} noValidate>
      <Field id="title" label="Título" error={errors.title}>
        <input id="title" name="title" value={values.title} onChange={handleChange}
          maxLength={200} aria-invalid={Boolean(errors.title)}
          className={inputClasses(Boolean(errors.title))} />
      </Field>

      <Field id="description" label="Descrição" error={errors.description}>
        <textarea id="description" name="description" rows={5} value={values.description}
          onChange={handleChange} aria-invalid={Boolean(errors.description)}
          className={inputClasses(Boolean(errors.description))} />
      </Field>

      <Field id="date" label="Data" error={errors.date}>
        <input id="date" name="date" type="date" value={values.date}
          onChange={handleChange} aria-invalid={Boolean(errors.date)}
          className={inputClasses(Boolean(errors.date))} />
      </Field>

      <Field id="time" label="Horário" error={errors.time}>
        <input id="time" name="time" type="time" value={values.time}
          onChange={handleChange} aria-invalid={Boolean(errors.time)}
          className={inputClasses(Boolean(errors.time))} />
      </Field>

      <Field id="location" label="Local" error={errors.location}>
        <input id="location" name="location" value={values.location}
          onChange={handleChange} maxLength={200} aria-invalid={Boolean(errors.location)}
          className={inputClasses(Boolean(errors.location))} />
      </Field>

      <Field id="event_type" label="Tipo" error={errors.event_type}>
        <select id="event_type" name="event_type" value={values.event_type}
          onChange={handleChange} aria-invalid={Boolean(errors.event_type)}
          className={inputClasses(Boolean(errors.event_type))}>
          <option value="">Selecione…</option>
          {EVENT_TYPES.map((type) => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
      </Field>

      <Field id="registration_link" label="Link de inscrição" error={errors.registration_link}>
        <input id="registration_link" name="registration_link" type="url"
          value={values.registration_link} onChange={handleChange}
          aria-invalid={Boolean(errors.registration_link)}
          className={inputClasses(Boolean(errors.registration_link))} />
      </Field>

      <div className="flex gap-3 pt-4">
        <button type="submit" disabled={isSubmitting}
          className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white
                     hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed">
          {isSubmitting ? "Salvando…" : "Salvar alterações"}
        </button>
        {/* type="button" é essencial: sem ele, o botão dentro do <form> dispararia o submit. */}
        <button type="button" onClick={onCancel} disabled={isSubmitting}
          className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium
                     text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
          Cancelar
        </button>
      </div>
    </form>
  );
}
