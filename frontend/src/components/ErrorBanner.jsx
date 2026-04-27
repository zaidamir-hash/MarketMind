const toneMap = {
  error: "banner-error",
  success: "banner-success",
  info: "banner-info",
  warning: "banner-warning",
};


export default function ErrorBanner({ title, message, tone = "error", onDismiss }) {
  if (!message) {
    return null;
  }

  return (
    <div className={`banner ${toneMap[tone] || toneMap.error}`} role={tone === "error" ? "alert" : "status"}>
      <div className="banner-copy">
        {title ? <strong>{title}</strong> : null}
        <span>{message}</span>
      </div>
      {onDismiss ? (
        <button type="button" className="link-button" onClick={onDismiss}>
          Dismiss
        </button>
      ) : null}
    </div>
  );
}
