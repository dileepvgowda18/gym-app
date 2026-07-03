import { useEffect, useState } from "react";
import api from "../api/client";
import "./Trainers.css";

export default function Trainers() {
  const [trainers, setTrainers] = useState([]);

  useEffect(() => {
    api.get("/trainers").then((res) => setTrainers(res.data)).catch(() => {});
  }, []);

  return (
    <div className="section container">
      <div className="section-head">
        <span className="eyebrow">Coaching staff</span>
        <h2>Trainers who actually coach</h2>
        <p>Certified, hands-on, and assigned to your goals — not just running the clock.</p>
      </div>

      <div className="trainers-grid">
        {trainers.map((t) => (
          <div className="trainer-card" key={t.id}>
            <div className="trainer-avatar">{t.name?.split(" ").map((n) => n[0]).join("")}</div>
            <h3>{t.name}</h3>
            <span className="eyebrow">{t.specialization}</span>
            <p>{t.bio}</p>
            <div className="trainer-exp">{t.years_experience} yrs experience</div>
          </div>
        ))}
        {trainers.length === 0 && <p style={{ color: "var(--paper-dim)" }}>No trainers listed yet.</p>}
      </div>
    </div>
  );
}
