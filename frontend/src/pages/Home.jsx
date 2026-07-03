import { Link } from "react-router-dom";
import "./Home.css";

const STEPS = [
  { n: "01", title: "Pick a plan", body: "Starter, Pro, or Elite — choose the access level that fits your training." },
  { n: "02", title: "Book your slot", body: "Reserve group classes or walk in for open floor time, any day." },
  { n: "03", title: "Train & track", body: "Log attendance, follow your program, and watch your numbers move." },
];

const TICKER = [
  "1,240+ ACTIVE MEMBERS", "38 CLASSES / WEEK", "12 CERTIFIED TRAINERS",
  "5AM – 11PM DAILY", "3 TRAINING FLOORS", "1,240+ ACTIVE MEMBERS",
  "38 CLASSES / WEEK", "12 CERTIFIED TRAINERS", "5AM – 11PM DAILY", "3 TRAINING FLOORS",
];

export default function Home() {
  return (
    <div>
      <section className="hero">
        <div className="container hero-inner">
          <span className="eyebrow">IronCore Gym · Bengaluru</span>
          <h1>
            Strength is built<br />
            <span className="hero-cut">one rep</span> at a time.
          </h1>
          <p className="hero-sub">
            A no-nonsense strength &amp; conditioning gym with certified trainers,
            structured programs, and a membership system that stays out of your way.
          </p>
          <div className="hero-actions">
            <Link to="/plans" className="btn btn-primary">See membership plans</Link>
            <Link to="/classes" className="btn btn-outline">Browse class schedule</Link>
          </div>
        </div>
        <div className="hero-plate" aria-hidden="true" />
      </section>

      <div className="ticker">
        <div className="ticker-track">
          {TICKER.map((t, i) => (
            <span key={i}>{t}</span>
          ))}
        </div>
      </div>

      <section className="section">
        <div className="container">
          <div className="section-head">
            <span className="eyebrow">How it works</span>
            <h2>Three steps to your first session</h2>
          </div>
          <div className="steps-grid">
            {STEPS.map((s) => (
              <div className="step-card" key={s.n}>
                <span className="step-n">{s.n}</span>
                <h3>{s.title}</h3>
                <p>{s.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="section cta-section">
        <div className="container cta-inner">
          <div>
            <span className="eyebrow">Ready when you are</span>
            <h2>Your first week starts today.</h2>
          </div>
          <Link to="/register" className="btn btn-primary">Create your account</Link>
        </div>
      </section>
    </div>
  );
}
