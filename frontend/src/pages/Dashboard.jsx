import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";
import "./Dashboard.css";

export default function Dashboard() {
  const { user } = useAuth();
  const [memberships, setMemberships] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    Promise.all([
      api.get("/memberships"),
      api.get("/bookings"),
      api.get("/payments"),
    ]).then(([m, b, p]) => {
      setMemberships(m.data);
      setBookings(b.data.filter((x) => x.status === "confirmed"));
      setPayments(p.data);
    }).finally(() => setLoading(false));
  };

  useEffect(load, []);

  const cancelBooking = async (id) => {
    await api.delete(`/bookings/${id}`);
    load();
  };

  const activeMembership = memberships.find((m) => m.status === "active");

  if (loading) return <div className="container section">Loading your dashboard…</div>;

  return (
    <div className="container section">
      <div className="section-head">
        <span className="eyebrow">My dashboard</span>
        <h2>Welcome back, {user.name.split(" ")[0]}</h2>
      </div>

      <div className="dash-grid">
        <div className="card dash-card">
          <h3>Membership</h3>
          {activeMembership ? (
            <>
              <p className="dash-plan-name">{activeMembership.plan.name}</p>
              <span className="badge badge-active">Active until {activeMembership.end_date}</span>
            </>
          ) : (
            <>
              <p style={{ color: "var(--paper-dim)" }}>You don't have an active plan yet.</p>
              <Link to="/plans" className="btn btn-primary" style={{ marginTop: 14 }}>Browse plans</Link>
            </>
          )}
        </div>

        <div className="card dash-card">
          <h3>Upcoming classes</h3>
          {bookings.length === 0 && <p style={{ color: "var(--paper-dim)" }}>No classes booked yet.</p>}
          <ul className="dash-booking-list">
            {bookings.map((b) => (
              <li key={b.id}>
                <div>
                  <strong>{b.class.name}</strong>
                  <span>{b.class.schedule_day} · {b.class.schedule_time}</span>
                </div>
                <button className="btn btn-outline" onClick={() => cancelBooking(b.id)}>Cancel</button>
              </li>
            ))}
          </ul>
          <Link to="/classes" className="btn btn-outline" style={{ marginTop: 14 }}>Book another class</Link>
        </div>

        <div className="card dash-card dash-wide">
          <h3>Payment history</h3>
          {payments.length === 0 && <p style={{ color: "var(--paper-dim)" }}>No payments yet.</p>}
          {payments.length > 0 && (
            <table className="dash-table">
              <thead>
                <tr><th>Date</th><th>Amount</th><th>Method</th><th>Status</th></tr>
              </thead>
              <tbody>
                {payments.map((p) => (
                  <tr key={p.id}>
                    <td>{new Date(p.payment_date).toLocaleDateString()}</td>
                    <td>₹{p.amount}</td>
                    <td>{p.method}</td>
                    <td><span className="badge badge-active">{p.status}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
