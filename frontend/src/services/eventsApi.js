const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(status, detail) {
    super(typeof detail === "string" ? detail : "Não foi possível concluir a operação.");
    this.status = status;
    this.detail = detail;
  }
}

async function request(path, options = {}) {
  
  const response = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new ApiError(response.status, body.detail);
  }
  // 204 No Content (ex.: DELETE) não tem corpo; chamar .json() lançaria erro.
  if (response.status === 204) return null;
  return response.json();
}

export const getEvent = (id, signal) => request(`/events/${id}`, { signal });


export const updateEvent = (id, payload) =>
  request(`/events/${id}`, { method: "PUT", body: JSON.stringify(payload) });


export const deleteEvent = (id) => request(`/events/${id}`, { method: "DELETE" });

export function toFieldErrors(detail) {
  if (!Array.isArray(detail)) return {};
  return Object.fromEntries(detail.map((e) => [e.loc.at(-1), e.msg]));
}
