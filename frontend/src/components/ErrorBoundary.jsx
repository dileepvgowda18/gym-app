import { Component } from "react";

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="card dash-card" role="alert">
          <h3>This section could not be displayed</h3>
          <p style={{ color: "var(--paper-dim)", marginTop: 10 }}>
            Try another dashboard tab, or refresh the page.
          </p>
        </div>
      );
    }

    return this.props.children;
  }
}
