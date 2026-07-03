import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="container section" style={{ textAlign: "center" }}>
      <span className="eyebrow">404</span>
      <h2 style={{ marginTop: 10, fontSize: "2rem" }}>This page skipped leg day.</h2>
      <p style={{ color: "var(--paper-dim)", marginTop: 12 }}>We couldn't find what you're looking for.</p>
      <Link to="/" className="btn btn-primary" style={{ marginTop: 24 }}>Back to home</Link>
    </div>
  );
}
