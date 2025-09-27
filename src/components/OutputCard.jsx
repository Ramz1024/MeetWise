import "./OutputCard.css";

function OutputCard({ title, desc, color, isSelected, onSelect }) {
  return (
    <div
      className={`output-card ${color} ${isSelected ? "selected" : ""}`}
      onClick={onSelect}
    >
      <div className="top">
        <h3>{title}</h3>
        {isSelected && <span className="check">✔</span>}
      </div>
      <p>{desc}</p>
      <div className="footer">
        {isSelected ? <span className="selected-text">Selected</span> : "Click to add"}
      </div>
    </div>
  );
}

export default OutputCard;
