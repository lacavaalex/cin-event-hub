import { downloadIcs } from '../services/calendarService';

export default function AddToCalendarButton({ event, url }) {
  return (
    <button type="button" className="details-calendar" onClick={() => downloadIcs(event, { url })}>
      Adicionar à Agenda
    </button>
  );
}