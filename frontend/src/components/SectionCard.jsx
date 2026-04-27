export default function SectionCard({
  title,
  description,
  actions,
  className = "",
  children,
}) {
  const sectionClassName = ["card", "section-card", className].filter(Boolean).join(" ");

  return (
    <section className={sectionClassName}>
      {title || description || actions ? (
        <div className="section-header">
          <div>
            {title ? <h2>{title}</h2> : null}
            {description ? <p>{description}</p> : null}
          </div>
          {actions ? <div className="section-actions">{actions}</div> : null}
        </div>
      ) : null}
      {children}
    </section>
  );
}
