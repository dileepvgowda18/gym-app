import "./Footer.css";

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container footer-inner">
        <div>
          <div className="nav-logo">IRON<span>CORE</span></div>
          <p>124 Foundry Road, Bengaluru · Open daily 5am – 11pm</p>
        </div>
        <div className="footer-cols">
          <div>
            <h4>Gym</h4>
            <p>Plans</p>
            <p>Trainers</p>
            <p>Classes</p>
          </div>
          <div>
            <h4>Account</h4>
            <p>Log in</p>
            <p>Join now</p>
          </div>
        </div>
      </div>
      <div className="container footer-bottom">
        © {new Date().getFullYear()} IronCore Gym. Built for training, not templates.
      </div>
    </footer>
  );
}
