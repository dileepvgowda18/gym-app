import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./Navbar.css";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const dashboardPath = user?.role === "admin" ? "/admin" : "/dashboard";

  return (
    <header className="nav">
      <div className="container nav-inner">
        <Link to="/" className="nav-logo">
          IRON<span>CORE</span>
        </Link>
        <nav className="nav-links">
          <NavLink to="/plans">Plans</NavLink>
          <NavLink to="/trainers">Trainers</NavLink>
          <NavLink to="/classes">Classes</NavLink>
        </nav>
        <div className="nav-actions">
          {user ? (
            <>
              <Link to={dashboardPath} className="btn btn-outline">
                {user.role === "admin" ? "Admin Panel" : "My Dashboard"}
              </Link>
              <button className="btn btn-primary" onClick={handleLogout}>Log out</button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-outline">Log in</Link>
              <Link to="/register" className="btn btn-primary">Join now</Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
