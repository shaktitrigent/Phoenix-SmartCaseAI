import { Component } from "react";

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error("UI crashed:", error, info);
  }

  handleReload = () => {
    window.location.reload();
  };

  render() {
    const { hasError, error } = this.state;
    if (!hasError) {
      return this.props.children;
    }

    const message = error?.message || "Something went wrong while rendering this screen.";
    return (
      <div className="card">
        <h2 className="section-title">Something went wrong</h2>
        <p className="field-muted">{message}</p>
        <div className="actions-row inline">
          <button type="button" className="btn" onClick={this.handleReload}>
            Reload
          </button>
        </div>
      </div>
    );
  }
}

export default ErrorBoundary;
