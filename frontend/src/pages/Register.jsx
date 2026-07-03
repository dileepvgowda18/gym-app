import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./Auth.css";

export default function Register() {
  const [form, setForm] = useState({ name: "", email: "", phone: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register(form);
      navigate("/dashboard");
    } catch (e) {
      setError(e.response?.data?.error || "Registration failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-wrap container">
      <form className="auth-card card" onSubmit={handleSubmit}>
        <span className="eyebrow">Join IronCore</span>
        <h2>Create your account</h2>

        {error && <div className="error-banner">{error}</div>}

        <div className="form-row">
          <label>Full name</label>
          <input required value={form.name} onChange={update("name")} placeholder="Alex Rivera" />
        </div>
        <div className="form-row">
          <label>Email</label>
          <input type="email" required value={form.email} onChange={update("email")} placeholder="you@example.com" />
        </div>
        <div className="form-row">
          <label>Phone</label>
          <input value={form.phone} onChange={update("phone")} placeholder="98765 43210" />
        </div>
        <div className="form-row">
          <label>Password</label>
          <input type="password" required minLength={6} value={form.password} onChange={update("password")} placeholder="At least 6 characters" />
        </div>
        <button className="btn btn-primary btn-block" disabled={loading}>
          {loading ? "Creating account…" : "Create account"}
        </button>
        <p className="auth-switch">
          Already a member? <Link to="/login">Log in</Link>
        </p>
      </form>
    </div>
  );
}
