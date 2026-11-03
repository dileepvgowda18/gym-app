import { useEffect, useMemo, useState } from "react";
import api from "../api/client";
import ErrorBoundary from "../components/ErrorBoundary";
import "./Dashboard.css";

const TABS = ["Overview", "Members", "Plans", "Trainers", "Classes"];

function getErrorMessage(error, fallback) {
  return error.response?.data?.error || fallback;
}

function formatDate(value) {
  if (!value) return "—";
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? "—" : parsed.toLocaleDateString();
}

function StateMessage({ loading, error, empty, children }) {
  if (loading) return <p role="status" style={{ color: "var(--paper-dim)" }}>Loading…</p>;
  if (error) return <div className="error-banner" role="alert">{error}</div>;
  if (empty) return <p style={{ color: "var(--paper-dim)" }}>{empty}</p>;
  return children;
}

export default function AdminDashboard() {
  const [tab, setTab] = useState("Overview");

  const tabContent = {
    Overview: <OverviewTab />,
    Members: <MembersTab />,
    Plans: <PlansTab />,
    Trainers: <TrainersTab />,
    Classes: <ClassesTab />,
  };

  return (
    <div className="container section">
      <div className="section-head">
        <span className="eyebrow">Admin panel</span>
        <h2>Run the gym from here</h2>
      </div>

      <div className="admin-tabs" role="tablist" aria-label="Admin dashboard sections">
        {TABS.map((name) => (
          <button
            type="button"
            role="tab"
            aria-selected={tab === name}
            key={name}
            className={tab === name ? "active" : ""}
            onClick={() => setTab(name)}
          >
            {name}
          </button>
        ))}
      </div>

      <ErrorBoundary key={tab}>
        {tabContent[tab]}
      </ErrorBoundary>
    </div>
  );
}

function OverviewTab() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    api.get("/admin/stats")
      .then(({ data }) => {
        if (active) setStats(data || {});
      })
      .catch((requestError) => {
        if (active) setError(getErrorMessage(requestError, "Could not load dashboard statistics."));
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => { active = false; };
  }, []);

  if (loading || error) return <StateMessage loading={loading} error={error} />;
  const cards = [
    { label: "Total members", value: Number(stats.total_members || 0).toLocaleString() },
    { label: "Active memberships", value: Number(stats.active_memberships || 0).toLocaleString() },
    { label: "Revenue", value: `₹${Number(stats.total_revenue || 0).toLocaleString()}` },
    { label: "Confirmed bookings", value: Number(stats.total_bookings || 0).toLocaleString() },
    { label: "Classes running", value: Number(stats.total_classes || 0).toLocaleString() },
  ];

  return (
    <div className="stat-row">
      {cards.map((card) => (
        <div className="card stat-card" key={card.label}>
          <div className="stat-value">{card.value}</div>
          <div className="stat-label">{card.label}</div>
        </div>
      ))}
    </div>
  );
}

function MembersTab() {
  const [members, setMembers] = useState([]);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    api.get("/admin/members")
      .then(({ data }) => {
        if (!Array.isArray(data)) throw new Error("The members API returned an invalid response.");
        if (active) setMembers(data);
      })
      .catch((requestError) => {
        if (active) setError(getErrorMessage(requestError, requestError.message || "Could not load members."));
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => { active = false; };
  }, []);

  const filteredMembers = useMemo(() => {
    const query = search.trim().toLowerCase();
    return members.filter((member) => {
      const matchesSearch = !query || [member.name, member.email]
        .some((value) => String(value || "").toLowerCase().includes(query));
      const memberStatus = String(member.membership_status || "none").toLowerCase();
      return matchesSearch && (status === "all" || memberStatus === status);
    });
  }, [members, search, status]);

  return (
    <div className="card dash-card">
      <div className="admin-list-heading">
        <h3>Members ({filteredMembers.length})</h3>
        <div className="admin-filters">
          <label>
            <span className="sr-only">Search members</span>
            <input type="search" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search name or email" />
          </label>
          <label>
            <span className="sr-only">Filter by membership status</span>
            <select value={status} onChange={(event) => setStatus(event.target.value)}>
              <option value="all">All statuses</option>
              <option value="active">Active</option>
              <option value="expired">Expired</option>
              <option value="cancelled">Cancelled</option>
              <option value="none">No membership</option>
            </select>
          </label>
        </div>
      </div>
      <StateMessage loading={loading} error={error} empty={members.length === 0 ? "No registered members yet." : filteredMembers.length === 0 ? "No members match these filters." : null}>
        <div className="admin-table-wrap">
          <table className="dash-table">
            <thead><tr><th>Name</th><th>Email</th><th>Registered</th><th>Membership status</th></tr></thead>
            <tbody>
              {filteredMembers.map((member) => (
                <tr key={member.id}>
                  <td>{member.name || "—"}</td>
                  <td>{member.email || "—"}</td>
                  <td>{formatDate(member.created_at)}</td>
                  <td><span className="badge">{member.membership_status || "none"}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </StateMessage>
    </div>
  );
}

const emptyPlanForm = { name: "", price: "", duration_days: "", features: "" };

function PlansTab() {
  const [plans, setPlans] = useState([]);
  const [form, setForm] = useState(emptyPlanForm);
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const load = async () => {
    setError("");
    try {
      const { data } = await api.get("/admin/plans");
      if (!Array.isArray(data)) throw new Error("The plans API returned an invalid response.");
      setPlans(data);
    } catch (requestError) {
      setError(getErrorMessage(requestError, requestError.message || "Could not load plans."));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void load(); }, []);

  const resetForm = () => {
    setForm(emptyPlanForm);
    setEditingId(null);
  };

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    setNotice("");
    const price = Number(form.price);
    const durationDays = Number(form.duration_days);
    if (!form.name.trim() || !Number.isFinite(price) || price < 0 || !Number.isInteger(durationDays) || durationDays < 1) {
      setError("Enter a plan name, a non-negative price, and a duration of at least one day.");
      return;
    }
    setSaving(true);
    try {
      const payload = {
        name: form.name.trim(),
        price,
        duration_days: durationDays,
        features: form.features.split(",").map((feature) => feature.trim()).filter(Boolean),
      };
      if (editingId === null) {
        await api.post("/plans", payload);
        setNotice("Plan created.");
      } else {
        await api.put(`/plans/${editingId}`, payload);
        setNotice("Plan updated.");
      }
      resetForm();
      await load();
    } catch (requestError) {
      setError(getErrorMessage(requestError, "Could not save plan."));
    } finally {
      setSaving(false);
    }
  };

  const edit = (plan) => {
    setError("");
    setNotice("");
    setEditingId(plan.id);
    setForm({
      name: plan.name || "",
      price: String(plan.price ?? ""),
      duration_days: String(plan.duration_days ?? ""),
      features: Array.isArray(plan.features) ? plan.features.join(", ") : "",
    });
  };

  const remove = async (plan) => {
    if (!window.confirm(`Deactivate the "${plan.name}" plan? Existing memberships will be preserved.`)) return;
    setError("");
    setNotice("");
    try {
      await api.delete(`/plans/${plan.id}`);
      setNotice("Plan deactivated.");
      await load();
    } catch (requestError) {
      setError(getErrorMessage(requestError, "Could not deactivate plan."));
    }
  };

  return (
    <div>
      <form className="card admin-form" onSubmit={submit}>
        <h3 className="full-row">{editingId === null ? "Create plan" : "Edit plan"}</h3>
        <div><label htmlFor="plan-name">Name</label><input id="plan-name" required maxLength="80" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} /></div>
        <div><label htmlFor="plan-price">Price (₹)</label><input id="plan-price" required min="0" step="0.01" type="number" value={form.price} onChange={(event) => setForm({ ...form, price: event.target.value })} /></div>
        <div><label htmlFor="plan-duration">Duration (days)</label><input id="plan-duration" required min="1" step="1" type="number" value={form.duration_days} onChange={(event) => setForm({ ...form, duration_days: event.target.value })} /></div>
        <div className="full-row"><label htmlFor="plan-features">Features (comma-separated)</label><input id="plan-features" value={form.features} onChange={(event) => setForm({ ...form, features: event.target.value })} /></div>
        {error && <div className="error-banner full-row" role="alert">{error}</div>}
        {notice && <div className="badge badge-active full-row" role="status">{notice}</div>}
        <div className="admin-actions full-row">
          <button className="btn btn-primary" disabled={saving}>{saving ? "Saving…" : editingId === null ? "Create plan" : "Save changes"}</button>
          {editingId !== null && <button type="button" className="btn btn-outline" onClick={resetForm}>Cancel edit</button>}
        </div>
      </form>

      <div className="card dash-card">
        <h3>Existing plans</h3>
        <StateMessage loading={loading} error={error && plans.length === 0 ? error : ""} empty={plans.length === 0 ? "No plans have been created yet." : null}>
          <div className="admin-table-wrap">
            <table className="dash-table">
              <thead><tr><th>Name</th><th>Price</th><th>Duration</th><th>Status</th><th>Actions</th></tr></thead>
              <tbody>
                {plans.map((plan) => (
                  <tr key={plan.id}>
                    <td>{plan.name || "—"}</td>
                    <td>₹{Number(plan.price || 0).toLocaleString()}</td>
                    <td>{plan.duration_days ?? "—"} days</td>
                    <td>{plan.is_active === false ? "Inactive" : "Active"}</td>
                    <td className="admin-actions">
                      <button type="button" className="btn btn-outline" onClick={() => edit(plan)}>Edit</button>
                      {plan.is_active !== false && <button type="button" className="btn btn-outline" onClick={() => remove(plan)}>Deactivate</button>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </StateMessage>
      </div>
    </div>
  );
}

const emptyTrainerForm = { name: "", email: "", password: "", specialization: "", bio: "", years_experience: "0" };

function TrainersTab() {
  const [trainers, setTrainers] = useState([]);
  const [form, setForm] = useState(emptyTrainerForm);
  const [editingId, setEditingId] = useState(null);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const load = async () => {
    setError("");
    try {
      const { data } = await api.get("/admin/trainers");
      if (!Array.isArray(data)) throw new Error("The trainers API returned an invalid response.");
      setTrainers(data);
    } catch (requestError) {
      setError(getErrorMessage(requestError, requestError.message || "Could not load trainers."));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void load(); }, []);

  const filteredTrainers = useMemo(() => {
    const query = search.trim().toLowerCase();
    return trainers.filter((trainer) => [trainer.name, trainer.specialization]
      .some((value) => String(value || "").toLowerCase().includes(query)));
  }, [trainers, search]);

  const resetForm = () => {
    setForm(emptyTrainerForm);
    setEditingId(null);
  };

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    setNotice("");
    const years = Number(form.years_experience);
    if (!form.name.trim() || !form.email.trim() || !form.specialization.trim() || !Number.isInteger(years) || years < 0) {
      setError("Enter a name, valid email, specialization, and non-negative whole years of experience.");
      return;
    }
    if (editingId === null && form.password.length < 8) {
      setError("A password of at least 8 characters is required for a new trainer account.");
      return;
    }
    setSaving(true);
    try {
      const payload = {
        name: form.name.trim(),
        email: form.email.trim(),
        specialization: form.specialization.trim(),
        bio: form.bio.trim(),
        years_experience: years,
      };
      if (form.password) payload.password = form.password;
      if (editingId === null) {
        await api.post("/trainers", payload);
        setNotice("Trainer created.");
      } else {
        await api.put(`/trainers/${editingId}`, payload);
        setNotice("Trainer updated.");
      }
      resetForm();
      await load();
    } catch (requestError) {
      setError(getErrorMessage(requestError, "Could not save trainer."));
    } finally {
      setSaving(false);
    }
  };

  const edit = (trainer) => {
    setError("");
    setNotice("");
    setEditingId(trainer.id);
    setForm({
      name: trainer.name || "",
      email: trainer.email || "",
      password: "",
      specialization: trainer.specialization || "",
      bio: trainer.bio || "",
      years_experience: String(trainer.years_experience ?? 0),
    });
  };

  const remove = async (trainer) => {
    if (!window.confirm(`Remove ${trainer.name} as a trainer? Their login and personal records will be retained, and the account becomes a member. Trainers with scheduled classes or training history cannot be removed.`)) return;
    setError("");
    setNotice("");
    try {
      await api.delete(`/trainers/${trainer.id}`);
      setNotice("Trainer removed.");
      await load();
    } catch (requestError) {
      setError(getErrorMessage(requestError, "Could not remove trainer."));
    }
  };

  return (
    <div>
      <form className="card admin-form" onSubmit={submit}>
        <h3 className="full-row">{editingId === null ? "Create trainer" : "Edit trainer"}</h3>
        <div><label htmlFor="trainer-name">Name</label><input id="trainer-name" required maxLength="120" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} /></div>
        <div><label htmlFor="trainer-email">Email</label><input id="trainer-email" required type="email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} /></div>
        <div><label htmlFor="trainer-specialization">Specialization</label><input id="trainer-specialization" required maxLength="120" value={form.specialization} onChange={(event) => setForm({ ...form, specialization: event.target.value })} /></div>
        <div><label htmlFor="trainer-years">Years experience</label><input id="trainer-years" required min="0" step="1" type="number" value={form.years_experience} onChange={(event) => setForm({ ...form, years_experience: event.target.value })} /></div>
        <div><label htmlFor="trainer-password">Password {editingId !== null && "(optional)"}</label><input id="trainer-password" required={editingId === null} minLength="8" type="password" autoComplete="new-password" value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} /></div>
        <div className="full-row"><label htmlFor="trainer-bio">Bio</label><textarea id="trainer-bio" rows="2" value={form.bio} onChange={(event) => setForm({ ...form, bio: event.target.value })} /></div>
        {error && <div className="error-banner full-row" role="alert">{error}</div>}
        {notice && <div className="badge badge-active full-row" role="status">{notice}</div>}
        <div className="admin-actions full-row">
          <button className="btn btn-primary" disabled={saving}>{saving ? "Saving…" : editingId === null ? "Create trainer" : "Save changes"}</button>
          {editingId !== null && <button type="button" className="btn btn-outline" onClick={resetForm}>Cancel edit</button>}
        </div>
      </form>

      <div className="card dash-card">
        <div className="admin-list-heading">
          <h3>Trainers ({filteredTrainers.length})</h3>
          <label>
            <span className="sr-only">Search trainers</span>
            <input type="search" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search name or specialization" />
          </label>
        </div>
        <StateMessage loading={loading} error={error && trainers.length === 0 ? error : ""} empty={trainers.length === 0 ? "No trainers have been added yet." : filteredTrainers.length === 0 ? "No trainers match this search." : null}>
          <div className="admin-table-wrap">
            <table className="dash-table">
              <thead><tr><th>Name</th><th>Specialization</th><th>Experience</th><th>Actions</th></tr></thead>
              <tbody>
                {filteredTrainers.map((trainer) => (
                  <tr key={trainer.id}>
                    <td>{trainer.name || "—"}</td>
                    <td>{trainer.specialization || "—"}</td>
                    <td>{trainer.years_experience ?? 0} yrs</td>
                    <td className="admin-actions">
                      <button type="button" className="btn btn-outline" onClick={() => edit(trainer)}>Edit</button>
                      <button type="button" className="btn btn-outline" onClick={() => remove(trainer)}>Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </StateMessage>
      </div>
    </div>
  );
}

function ClassesTab() {
  const [classes, setClasses] = useState([]);
  const [trainers, setTrainers] = useState([]);
  const [form, setForm] = useState({ name: "", trainer_id: "", schedule_day: "Monday", schedule_time: "18:00", capacity: "20", description: "" });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const load = async () => {
    setError("");
    try {
      const [classesResponse, trainersResponse] = await Promise.all([api.get("/classes"), api.get("/admin/trainers")]);
      if (!Array.isArray(classesResponse.data) || !Array.isArray(trainersResponse.data)) {
        throw new Error("The classes API returned an invalid response.");
      }
      setClasses(classesResponse.data);
      setTrainers(trainersResponse.data);
    } catch (requestError) {
      setError(getErrorMessage(requestError, requestError.message || "Could not load classes."));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void load(); }, []);

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    setNotice("");
    const capacity = Number(form.capacity);
    if (!form.name.trim() || !form.trainer_id || !Number.isInteger(capacity) || capacity < 1) {
      setError("Enter a class name, select a trainer, and set capacity to at least one.");
      return;
    }
    setSaving(true);
    try {
      await api.post("/classes", {
        ...form,
        name: form.name.trim(),
        trainer_id: Number(form.trainer_id),
        capacity,
      });
      setForm({ name: "", trainer_id: "", schedule_day: "Monday", schedule_time: "18:00", capacity: "20", description: "" });
      setNotice("Class created.");
      await load();
    } catch (requestError) {
      setError(getErrorMessage(requestError, "Could not create class."));
    } finally {
      setSaving(false);
    }
  };

  const remove = async (gymClass) => {
    if (!window.confirm(`Delete the "${gymClass.name}" class? Existing bookings may prevent deletion.`)) return;
    setError("");
    setNotice("");
    try {
      await api.delete(`/classes/${gymClass.id}`);
      setNotice("Class deleted.");
      await load();
    } catch (requestError) {
      setError(getErrorMessage(requestError, "Could not delete class."));
    }
  };

  return (
    <div>
      <form className="card admin-form" onSubmit={submit}>
        <h3 className="full-row">Create class</h3>
        <div><label htmlFor="class-name">Class name</label><input id="class-name" required maxLength="120" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} /></div>
        <div>
          <label htmlFor="class-trainer">Trainer</label>
          <select id="class-trainer" required value={form.trainer_id} onChange={(event) => setForm({ ...form, trainer_id: event.target.value })}>
            <option value="">Select…</option>
            {trainers.map((trainer) => <option key={trainer.id} value={trainer.id}>{trainer.name}</option>)}
          </select>
        </div>
        <div>
          <label htmlFor="class-day">Day</label>
          <select id="class-day" value={form.schedule_day} onChange={(event) => setForm({ ...form, schedule_day: event.target.value })}>
            {["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].map((day) => <option key={day}>{day}</option>)}
          </select>
        </div>
        <div><label htmlFor="class-time">Time</label><input id="class-time" type="time" value={form.schedule_time} onChange={(event) => setForm({ ...form, schedule_time: event.target.value })} /></div>
        <div><label htmlFor="class-capacity">Capacity</label><input id="class-capacity" required min="1" step="1" type="number" value={form.capacity} onChange={(event) => setForm({ ...form, capacity: event.target.value })} /></div>
        <div className="full-row"><label htmlFor="class-description">Description</label><input id="class-description" value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} /></div>
        {error && <div className="error-banner full-row" role="alert">{error}</div>}
        {notice && <div className="badge badge-active full-row" role="status">{notice}</div>}
        <button className="btn btn-primary full-row" disabled={saving || trainers.length === 0}>{saving ? "Saving…" : "Create class"}</button>
      </form>

      <div className="card dash-card">
        <h3>Class schedule</h3>
        <StateMessage loading={loading} error={error && classes.length === 0 ? error : ""} empty={classes.length === 0 ? "No classes have been scheduled yet." : null}>
          <div className="admin-table-wrap">
            <table className="dash-table">
              <thead><tr><th>Class</th><th>Trainer</th><th>Day / Time</th><th>Seats</th><th>Actions</th></tr></thead>
              <tbody>
                {classes.map((gymClass) => (
                  <tr key={gymClass.id}>
                    <td>{gymClass.name || "—"}</td>
                    <td>{gymClass.trainer_name || "—"}</td>
                    <td>{gymClass.schedule_day || "—"} · {gymClass.schedule_time || "—"}</td>
                    <td>{gymClass.seats_left ?? "—"}/{gymClass.capacity ?? "—"}</td>
                    <td><button type="button" className="btn btn-outline" onClick={() => remove(gymClass)}>Delete</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </StateMessage>
      </div>
    </div>
  );
}
