import { useEffect, useState } from "react";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function AttendancePage() {
  const { user } = useAuth();
  const [data, setData] = useState({ current_status: "checked_out", total_visits: 0, monthly_visits: 0, records: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const load = async () => {
    setLoading(true);
    try {
      const res = await api.get("/attendance/me");
      setData(res.data);
    } catch (e) {
      setError(e.response?.data?.error || "Could not load attendance data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) load();
  }, [user]);

  const handleCheckIn = async () => {
    setError(""); setMessage("");
    try {
      await api.post("/attendance/check-in");
      setMessage("Check-in recorded successfully.");
      load();
    } catch (e) {
      setError(e.response?.data?.error || "Check-in failed.");
    }
  };

  const handleCheckOut = async () => {
    setError(""); setMessage("");
    try {
      await api.post("/attendance/check-out");
      setMessage("Check-out recorded successfully.");
      load();
    } catch (e) {
      setError(e.response?.data?.error || "Check-out failed.");
    }
  };

  return (
    <div className="section container">
      <div className="section-head">
        <span className="eyebrow">Attendance</span>
        <h2>Gym attendance tracker</h2>
      </div>

      {message && <div className="badge badge-active" style={{ display: "inline-block", marginBottom: 16 }}>{message}</div>}
      {error && <div className="error-banner">{error}</div>}

      {loading ? <p style={{ color: "var(--paper-dim)" }}>Loading attendance…</p> : (
        <>
          <div className="dash-grid">
            <div className="card dash-card">
              <h3>Today's status</h3>
              <p className="dash-plan-name">{data.current_status === "checked_in" ? "Checked in" : "Checked out"}</p>
              <div style={{ display: "flex", gap: 12, marginTop: 16, flexWrap: "wrap" }}>
                <button className="btn btn-primary" onClick={handleCheckIn} disabled={data.current_status === "checked_in"}>Check in</button>
                <button className="btn btn-outline" onClick={handleCheckOut} disabled={data.current_status !== "checked_in"}>Check out</button>
              </div>
            </div>

            <div className="card dash-card">
              <h3>Statistics</h3>
              <p>Total visits: <strong>{data.total_visits}</strong></p>
              <p>Monthly visits: <strong>{data.monthly_visits}</strong></p>
            </div>
          </div>

          <div className="card dash-card" style={{ marginTop: 24 }}>
            <h3>Attendance history</h3>
            <table className="dash-table">
              <thead>
                <tr><th>Check in</th><th>Check out</th><th>Duration</th></tr>
              </thead>
              <tbody>
                {data.records.length === 0 ? (
                  <tr><td colSpan="3" style={{ color: "var(--paper-dim)" }}>No attendance records yet.</td></tr>
                ) : data.records.map((record) => (
                  <tr key={record.attendance_id}>
                    <td>{record.check_in ? new Date(record.check_in).toLocaleString("en-IN", { timeZone: "Asia/Kolkata" }) : "—"}</td>
                    <td>{record.check_out ? new Date(record.check_out).toLocaleString("en-IN", { timeZone: "Asia/Kolkata" }) : "Open"}</td>
                    <td>{record.duration_minutes || 0} min</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
