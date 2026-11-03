import { useEffect, useState } from "react";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function WorkoutsPage() {
  const { user } = useAuth();
  const [exercises, setExercises] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [form, setForm] = useState({ workout_date: new Date().toISOString().slice(0, 10), notes: "", entries: [{ exercise_id: "", sets: 3, repetitions: 10, weight_kg: 0, notes: "" }] });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const load = async () => {
    try {
      const [exercisesRes, workoutsRes] = await Promise.all([
        api.get("/exercises"),
        api.get("/workouts/me"),
      ]);
      setExercises(exercisesRes.data);
      setSessions(workoutsRes.data);
    } catch (e) {
      setError(e.response?.data?.error || "Could not load workouts.");
    }
  };

  useEffect(() => { if (user) load(); }, [user]);

  const updateEntry = (index, field, value) => {
    setForm((current) => ({
      ...current,
      entries: current.entries.map((entry, i) => i === index ? { ...entry, [field]: value } : entry),
    }));
  };

  const addEntry = () => {
    setForm((current) => ({ ...current, entries: [...current.entries, { exercise_id: "", sets: 3, repetitions: 10, weight_kg: 0, notes: "" }] }));
  };

  const removeEntry = (index) => {
    setForm((current) => ({ ...current, entries: current.entries.filter((_, i) => i !== index) }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(""); setMessage("");
    try {
      await api.post("/workouts", { ...form, entries: form.entries.map((item) => ({ ...item, exercise_id: Number(item.exercise_id) })) });
      setMessage("Workout saved.");
      setForm({ workout_date: new Date().toISOString().slice(0, 10), notes: "", entries: [{ exercise_id: "", sets: 3, repetitions: 10, weight_kg: 0, notes: "" }] });
      load();
    } catch (e) {
      setError(e.response?.data?.error || "Could not save workout.");
    }
  };

  return (
    <div className="section container">
      <div className="section-head">
        <span className="eyebrow">Workout log</span>
        <h2>Track your training</h2>
      </div>

      {message && <div className="badge badge-active" style={{ display: "inline-block", marginBottom: 16 }}>{message}</div>}
      {error && <div className="error-banner">{error}</div>}

      <div className="card dash-card" style={{ marginBottom: 24 }}>
        <h3>Add workout</h3>
        <form onSubmit={handleSubmit}>
          <div className="form-row"><label>Workout date</label><input type="date" value={form.workout_date} onChange={(e) => setForm({ ...form, workout_date: e.target.value })} /></div>
          <div className="form-row"><label>Notes</label><textarea value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} rows="3" /></div>
          {form.entries.map((entry, index) => (
            <div key={index} style={{ border: "1px solid var(--line)", padding: 12, marginBottom: 12 }}>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: 12 }}>
                <div>
                  <label>Exercise</label>
                  <select value={entry.exercise_id} onChange={(e) => updateEntry(index, "exercise_id", e.target.value)}>
                    <option value="">Select exercise</option>
                    {exercises.map((exercise) => <option key={exercise.exercise_id} value={exercise.exercise_id}>{exercise.exercise_name}</option>)}
                  </select>
                </div>
                <div><label>Sets</label><input type="number" value={entry.sets} onChange={(e) => updateEntry(index, "sets", Number(e.target.value))} /></div>
                <div><label>Reps</label><input type="number" value={entry.repetitions} onChange={(e) => updateEntry(index, "repetitions", Number(e.target.value))} /></div>
                <div><label>Weight (kg)</label><input type="number" step="0.5" value={entry.weight_kg} onChange={(e) => updateEntry(index, "weight_kg", Number(e.target.value))} /></div>
              </div>
              <div style={{ marginTop: 12 }}>
                <label>Entry notes</label>
                <input value={entry.notes} onChange={(e) => updateEntry(index, "notes", e.target.value)} />
              </div>
              {form.entries.length > 1 && <button type="button" className="btn btn-outline" style={{ marginTop: 12 }} onClick={() => removeEntry(index)}>Remove</button>}
            </div>
          ))}
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginTop: 12 }}>
            <button type="button" className="btn btn-outline" onClick={addEntry}>Add exercise</button>
            <button type="submit" className="btn btn-primary">Save workout</button>
          </div>
        </form>
      </div>

      <div className="card dash-card">
        <h3>Workout history</h3>
        <table className="dash-table">
          <thead><tr><th>Date</th><th>Exercises</th><th>Notes</th></tr></thead>
          <tbody>
            {sessions.length === 0 ? (
              <tr><td colSpan="3" style={{ color: "var(--paper-dim)" }}>No workout sessions yet.</td></tr>
            ) : sessions.map((session) => (
              <tr key={session.session_id}>
                <td>{new Date(session.workout_date).toLocaleDateString()}</td>
                <td>{session.entries.map((entry) => `${entry.exercise_name} (${entry.sets}x${entry.repetitions})`).join(", ") || "—"}</td>
                <td>{session.notes || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
