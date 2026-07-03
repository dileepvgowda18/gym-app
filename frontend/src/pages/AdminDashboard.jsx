import { useEffect, useState } from "react";
import api from "../api/client";
import "./Dashboard.css";

const TABS = ["Overview", "Members", "Plans", "Trainers", "Classes"];

export default function AdminDashboard() {
  const [tab, setTab] = useState("Overview");

  return (
    <div className="container section">
      <div className="section-head">
        <span className="eyebrow">Admin panel</span>
        <h2>Run the gym from here</h2>
      </div>

      <div className="admin-tabs">
        {TABS.map((t) => (
          <button key={t} className={tab === t ? "active" : ""} onClick={() => setTab(t)}>{t}</button>
        ))}
      </div>

      {tab === "Overview" && <OverviewTab />}
      {tab === "Members" && <MembersTab />}
      {tab === "Plans" && <PlansTab />}
      {tab === "Trainers" && <TrainersTab />}
      {tab === "Classes" && <ClassesTab />}
    </div>
  );
}

function OverviewTab() {
  const [stats, setStats] = useState(null);
  useEffect(() => { api.get("/admin/stats").then((res) => setStats(res.data)); }, []);
  if (!stats) return <p style={{ color: "var(--paper-dim)" }}>Loading stats…</p>;

  const cards = [
    { label: "Total members", value: stats.total_members },
    { label: "Active memberships", value: stats.active_memberships },
    { label: "Revenue", value: `₹${stats.total_revenue.toLocaleString()}` },
    { label: "Confirmed bookings", value: stats.total_bookings },
    { label: "Classes running", value: stats.total_classes },
  ];

  return (
    <div className="stat-row">
      {cards.map((c) => (
        <div className="card stat-card" key={c.label}>
          <div className="stat-value">{c.value}</div>
          <div className="stat-label">{c.label}</div>
        </div>
      ))}
    </div>
  );
}

function MembersTab() {
  const [members, setMembers] = useState([]);
  useEffect(() => { api.get("/admin/members").then((res) => setMembers(res.data)); }, []);

  return (
    <div className="card dash-card">
      <h3>Members ({members.length})</h3>
      <table className="dash-table">
        <thead><tr><th>Name</th><th>Email</th><th>Phone</th><th>Joined</th></tr></thead>
        <tbody>
          {members.map((m) => (
            <tr key={m.id}>
              <td>{m.name}</td>
              <td>{m.email}</td>
              <td>{m.phone || "—"}</td>
              <td>{new Date(m.created_at).toLocaleDateString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function PlansTab() {
  const [plans, setPlans] = useState([]);
  const [form, setForm] = useState({ name: "", price: "", duration_days: "", features: "" });
  const [error, setError] = useState("");

  const load = () => api.get("/plans").then((res) => setPlans(res.data));
  useEffect(load, []);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.post("/plans", {
        name: form.name,
        price: parseFloat(form.price),
        duration_days: parseInt(form.duration_days, 10),
        features: form.features.split(",").map((f) => f.trim()).filter(Boolean),
      });
      setForm({ name: "", price: "", duration_days: "", features: "" });
      load();
    } catch (e) {
      setError(e.response?.data?.error || "Could not create plan.");
    }
  };

  const remove = async (id) => { await api.delete(`/plans/${id}`); load(); };

  return (
    <div>
      <form className="card admin-form" onSubmit={submit}>
        <div><label>Name</label><input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></div>
        <div><label>Price (₹)</label><input required type="number" value={form.price} onChange={(e) => setForm({ ...form, price: e.target.value })} /></div>
        <div><label>Duration (days)</label><input required type="number" value={form.duration_days} onChange={(e) => setForm({ ...form, duration_days: e.target.value })} /></div>
        <div className="full-row"><label>Features (comma-separated)</label><input value={form.features} onChange={(e) => setForm({ ...form, features: e.target.value })} /></div>
        {error && <div className="error-banner full-row">{error}</div>}
        <button className="btn btn-primary full-row">Add plan</button>
      </form>

      <div className="card dash-card">
        <h3>Existing plans</h3>
        <table className="dash-table">
          <thead><tr><th>Name</th><th>Price</th><th>Duration</th><th></th></tr></thead>
          <tbody>
            {plans.map((p) => (
              <tr key={p.id}>
                <td>{p.name}</td>
                <td>₹{p.price}</td>
                <td>{p.duration_days} days</td>
                <td><button className="btn btn-outline" onClick={() => remove(p.id)}>Delete</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function TrainersTab() {
  const [trainers, setTrainers] = useState([]);
  const [form, setForm] = useState({ name: "", email: "", specialization: "", bio: "", years_experience: "" });
  const [error, setError] = useState("");

  const load = () => api.get("/trainers").then((res) => setTrainers(res.data));
  useEffect(load, []);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.post("/trainers", { ...form, years_experience: parseInt(form.years_experience || "0", 10) });
      setForm({ name: "", email: "", specialization: "", bio: "", years_experience: "" });
      load();
    } catch (e) {
      setError(e.response?.data?.error || "Could not add trainer.");
    }
  };

  const remove = async (id) => { await api.delete(`/trainers/${id}`); load(); };

  return (
    <div>
      <form className="card admin-form" onSubmit={submit}>
        <div><label>Name</label><input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></div>
        <div><label>Email</label><input required type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></div>
        <div><label>Specialization</label><input value={form.specialization} onChange={(e) => setForm({ ...form, specialization: e.target.value })} /></div>
        <div><label>Years experience</label><input type="number" value={form.years_experience} onChange={(e) => setForm({ ...form, years_experience: e.target.value })} /></div>
        <div className="full-row"><label>Bio</label><input value={form.bio} onChange={(e) => setForm({ ...form, bio: e.target.value })} /></div>
        {error && <div className="error-banner full-row">{error}</div>}
        <button className="btn btn-primary full-row">Add trainer</button>
      </form>

      <div className="card dash-card">
        <h3>Trainers</h3>
        <table className="dash-table">
          <thead><tr><th>Name</th><th>Specialization</th><th>Experience</th><th></th></tr></thead>
          <tbody>
            {trainers.map((t) => (
              <tr key={t.id}>
                <td>{t.name}</td>
                <td>{t.specialization}</td>
                <td>{t.years_experience} yrs</td>
                <td><button className="btn btn-outline" onClick={() => remove(t.id)}>Delete</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ClassesTab() {
  const [classes, setClasses] = useState([]);
  const [trainers, setTrainers] = useState([]);
  const [form, setForm] = useState({ name: "", trainer_id: "", schedule_day: "Monday", schedule_time: "18:00", capacity: 20, description: "" });
  const [error, setError] = useState("");

  const load = () => {
    api.get("/classes").then((res) => setClasses(res.data));
    api.get("/trainers").then((res) => setTrainers(res.data));
  };
  useEffect(load, []);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.post("/classes", { ...form, trainer_id: parseInt(form.trainer_id, 10), capacity: parseInt(form.capacity, 10) });
      setForm({ name: "", trainer_id: "", schedule_day: "Monday", schedule_time: "18:00", capacity: 20, description: "" });
      load();
    } catch (e) {
      setError(e.response?.data?.error || "Could not create class.");
    }
  };

  const remove = async (id) => { await api.delete(`/classes/${id}`); load(); };

  return (
    <div>
      <form className="card admin-form" onSubmit={submit}>
        <div><label>Class name</label><input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></div>
        <div>
          <label>Trainer</label>
          <select required value={form.trainer_id} onChange={(e) => setForm({ ...form, trainer_id: e.target.value })}>
            <option value="">Select…</option>
            {trainers.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
          </select>
        </div>
        <div>
          <label>Day</label>
          <select value={form.schedule_day} onChange={(e) => setForm({ ...form, schedule_day: e.target.value })}>
            {["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].map((d) => <option key={d}>{d}</option>)}
          </select>
        </div>
        <div><label>Time</label><input type="time" value={form.schedule_time} onChange={(e) => setForm({ ...form, schedule_time: e.target.value })} /></div>
        <div><label>Capacity</label><input type="number" value={form.capacity} onChange={(e) => setForm({ ...form, capacity: e.target.value })} /></div>
        <div className="full-row"><label>Description</label><input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></div>
        {error && <div className="error-banner full-row">{error}</div>}
        <button className="btn btn-primary full-row">Add class</button>
      </form>

      <div className="card dash-card">
        <h3>Class schedule</h3>
        <table className="dash-table">
          <thead><tr><th>Class</th><th>Trainer</th><th>Day / Time</th><th>Seats</th><th></th></tr></thead>
          <tbody>
            {classes.map((c) => (
              <tr key={c.id}>
                <td>{c.name}</td>
                <td>{c.trainer_name}</td>
                <td>{c.schedule_day} · {c.schedule_time}</td>
                <td>{c.seats_left}/{c.capacity}</td>
                <td><button className="btn btn-outline" onClick={() => remove(c.id)}>Delete</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
