function ToastStack({ toasts = [], onDismiss }) {
  if (!toasts.length) {
    return null;
  }

  return (
    <div className="toast-stack">
      {toasts.map((toast) => (
        <div key={toast.id} className={`toast ${toast.type || "info"}`}>
          <span>{toast.message}</span>
          <button type="button" onClick={() => onDismiss?.(toast.id)} aria-label="Dismiss">
            x
          </button>
        </div>
      ))}
    </div>
  );
}

export default ToastStack;
