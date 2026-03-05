function LoadingOverlay({ show, label = "Processing..." }) {
  if (!show) {
    return null;
  }
  return (
    <div className="loading-overlay" role="status" aria-live="polite">
      <div className="loading-card">
        <span className="spinner" />
        <span>{label}</span>
      </div>
    </div>
  );
}

export default LoadingOverlay;
