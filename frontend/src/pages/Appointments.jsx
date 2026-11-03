import { useEffect, useState } from "react";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function AppointmentsPage() {
  const { user } = useAuth();
  const [trainers, setTrainers] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [selectedTrainer, setSelectedTrainer] = useState("");
  const [selectedDate, setSelectedDate] = useState(new Date(Date.now() + 86400000).toISOString().slice(0, 10));
  const [slots, setSlots] = useState([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const load = async () => {
    try {
      const [trainersRes, appointmentsRes] = await Promise.all([
        api.get("/trainers"),
        api.get("/appointments/me"),
      ]);
      setTrainers(trainersRes.data);
      setAppointments(appointmentsRes.data);
    } catch (e) {
      setError(e.response?.data?.error || "Could not load appointments.");
    }
  };

  useEffect(() => { if (user) load(); }, [user]);

  useEffect(() => {
    if (!selectedTrainer || !selectedDate) return;
    api.get(`/trainers/${selectedTrainer}/availability?date=${selectedDate}`)
      .then((res) => setSlots(res.data.slots || []))
      .catch(() => setSlots([]));
  }, [selectedTrainer, selectedDate]);

  const bookAppointment = async (slot) => {
    setError(""); setMessage("");
    try {
      await api.post("/appointments", { trainer_id: Number(selectedTrainer), start_at: slot.start });
      setMessage("Appointment requested successfully.");
      load();
    } catch (e) {
      setError(e.response?.data?.error || "Could not create appointment.");
    }
  };

  return (
    <div className="section container">
      <div className="section-head">
        <span className="eyebrow">Appointments</span>
        <h2>Book a personal training session</h2>
      </div>

      {message && <div className="badge badge-active" style={{ display: "inline-block", marginBottom: 16 }}>{message}</div>}
      {error && <div className="error-banner">{error}</div>}

      <div className="card dash-card" style={{ marginBottom: 24 }}>
        <h3>Choose trainer</h3>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 12 }}>
          <div>
            <label>Trainer</label>
            <select value={selectedTrainer} onChange={(e) => setSelectedTrainer(e.target.value)}>
              <option value="">Select trainer</option>
              {trainers.map((trainer) => <option key={trainer.id} value={trainer.id}>{trainer.name}</option>)}
            </select>
          </div>
          <div>
            <label>Date</label>
            <input type="date" value={selectedDate} onChange={(e) => setSelectedDate(e.target.value)} />
          </div>
        </div>

        <div style={{ marginTop: 20 }}>
          {slots.length === 0 ? <p style={{ color: "var(--paper-dim)" }}>No slots available for this date.</p> : (
            <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
              {slots.map((slot) => (
                <button key={slot.start} className="btn btn-outline" onClick={() => bookAppointment(slot)}>
                  {new Date(slot.start).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", timeZone: "Asia/Kolkata" })}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="card dash-card">
        <h3>My appointments</h3>
        <table className="dash-table">
          <thead><tr><th>Trainer</th><th>Start</th><th>Status</th></tr></thead>
          <tbody>
            {appointments.length === 0 ? (
              <tr><td colSpan="3" style={{ color: "var(--paper-dim)" }}>No appointments yet.</td></tr>
            ) : appointments.map((appointment) => (
              <tr key={appointment.appointment_id}>
                <td>{appointment.trainer_name}</td>
                <td>{new Date(appointment.start_at).toLocaleString("en-IN", { timeZone: "Asia/Kolkata" })}</td>
                <td><span className="badge badge-pending">{appointment.status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
