import { useState } from "react";
import { useNavigate } from "react-router-dom";
import OutputCard from "../components/OutputCard";
import "./Outputs.css";

function Outputs() {
  const navigate = useNavigate(); // hook for navigation
  const [selected, setSelected] = useState([]);

  const outputs = [
    { title: "Meeting Summary", desc: "Clean overview of key points and decisions", color: "blue" },
    { title: "Task Division", desc: "Auto-assign action items to team members", color: "green" },
    { title: "Action Flow", desc: "Visual workflow with dependencies & timelines", color: "purple" },
    { title: "Smart Chatbot", desc: "Ask questions about your meeting anytime", color: "pink" },
    { title: "Avatar Explainer", desc: "Friendly AI explains key points in simple terms", color: "yellow" },
  ];

  const toggleSelect = (title) => {
    setSelected((prev) => (prev.includes(title) ? prev.filter((s) => s !== title) : [...prev, title]));
  };

  return (
    <div className="outputs">
      {/* Back Button */}
      <button className="back-btn" onClick={() => navigate(-1)}>← Back</button>

      <h1 className="title">
        What do you need from this meeting? <span>✨</span>
      </h1>
      <p className="subtitle">
        Choose one or more outputs to generate from your meeting content
      </p>

      <div className="outputs-grid">
        {outputs.map((o) => (
          <OutputCard
            key={o.title}
            {...o}
            isSelected={selected.includes(o.title)}
            onSelect={() => toggleSelect(o.title)}
          />
        ))}
      </div>

      {selected.length > 0 && (
        <div className="selection-box">
          <p>You’ve selected {selected.length} outputs</p>
          <div className="tags">
            {selected.map((s) => (
              <span key={s} className="tag">
                {s}
              </span>
            ))}
          </div>
        </div>
      )}

      <button className="generate-btn">✨ Generate Outputs ✨</button>
    </div>
  );
}

export default Outputs;
