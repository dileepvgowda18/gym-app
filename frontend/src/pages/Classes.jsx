import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";
import "./Classes.css";

const DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

export default function Classes() {
  const [classes, setClasses] = useState([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [bookingId, setBookingId] = useState(null);
  const { user } = useAuth();
  const navigate = useNavigate();

  const load = () => {
    api.get("/classes").then((res) => {
      const sorted = [...res.data].sort(
        (a, b) => DAY_ORDER.indexOf(a.schedule_day) - DAY_ORDER.indexOf(b.schedule_day)
      );
      setClasses(sorted);
    });
  };

  useEffect(load, []);

  const handleBook = async (classId) => {
    if (!user) {
      navigate("/login");
      return;
    }
    setBookingId(classId);
    setError("");
    setMessage("");
    try {
      await api.post("/bookings", { class_id: classId });
      setMessage("You're booked in. See it under My Dashboard.");
      load();
    } catch (e) {
      setError(e.response?.data?.error || "Could not book this class.");
    } finally {
      setBookingId(null);
    }
  };

  return (
    <div className="section container">
      <div className="section-head">
        <span className="eyebrow">Weekly schedule</span>
        <h2>Group classes, every day</h2>
        <p>Reserve your spot ahead of time — capacity is limited per session.</p>
      </div>

      {message && <div className="badge badge-active" style={{ display: "inline-block", marginBottom: 16 }}>{message}</div>}
      {error && <div className="error-banner">{error}</div>}

      <div className="classes-list">
        {classes.map((c) => (
          <div className="class-row" key={c.id}>
            <div className="class-day">{c.schedule_day}</div>
            <div className="class-info">
              <h3>{c.name}</h3>
              <p>with {c.trainer_name} · {c.schedule_time} · {c.duration_minutes} min</p>
              <p className="class-desc">{c.description}</p>
            </div>
            <div className="class-action">
              <span className={`badge ${c.seats_left > 0 ? "badge-active" : "badge-off"}`}>
                {c.seats_left > 0 ? `${c.seats_left} seats left` : "Full"}
              </span>
              <button
                className="btn btn-primary"
                disabled={c.seats_left <= 0 || bookingId === c.id}
                onClick={() => handleBook(c.id)}
              >
                {bookingId === c.id ? "Booking…" : "Book class"}
              </button>
            </div>
          </div>
        ))}
        {classes.length === 0 && <p style={{ color: "var(--paper-dim)" }}>No classes scheduled yet.</p>}
      </div>
    </div>
  );
}
