import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";
import "./Plans.css";

export default function Plans() {
  const [plans, setPlans] = useState([]);
  const [error, setError] = useState("");
  const [subscribing, setSubscribing] = useState(null);
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    api.get("/plans").then((res) => setPlans(res.data)).catch(() => setError("Could not load plans."));
  }, []);

  const handleSubscribe = async (planId) => {
    if (!user) {
      navigate("/login");
      return;
    }
    setSubscribing(planId);
    setError("");
    try {
      await api.post("/memberships/subscribe", { plan_id: planId });
      navigate("/dashboard");
    } catch (e) {
      setError(e.response?.data?.error || "Subscription failed.");
    } finally {
      setSubscribing(null);
    }
  };

  return (
    <div className="section container">
      <div className="section-head">
        <span className="eyebrow">Membership</span>
        <h2>Plans built around how often you train</h2>
        <p>No hidden fees. Cancel or upgrade any time from your dashboard.</p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="plans-grid">
        {plans.map((p, i) => (
          <div className={`plan-card ${i === 1 ? "plan-featured" : ""}`} key={p.id}>
            {i === 1 && <span className="plan-tag">Most popular</span>}
            <h3>{p.name}</h3>
            <div className="plan-price">
              <span>₹{p.price}</span> / {p.duration_days} days
            </div>
            <ul className="plan-features">
              {p.features.map((f, idx) => <li key={idx}>{f}</li>)}
            </ul>
            <button
              className={`btn btn-block ${i === 1 ? "btn-primary" : "btn-outline"}`}
              onClick={() => handleSubscribe(p.id)}
              disabled={subscribing === p.id}
            >
              {subscribing === p.id ? "Processing…" : "Choose plan"}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
