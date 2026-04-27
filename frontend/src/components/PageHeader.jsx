export default function PageHeader({
  eyebrow,
  title,
  description,
  actions,
  children,
}) {
  return (
    <header className="page-header">
      <div className="page-header-copy">
        {eyebrow ? <span className="page-header-eyebrow">{eyebrow}</span> : null}
        <h1>{title}</h1>
        {description ? <p>{description}</p> : null}
        {children ? <div className="page-header-meta">{children}</div> : null}
      </div>

      {actions ? <div className="page-header-actions">{actions}</div> : null}
    </header>
  );
}
