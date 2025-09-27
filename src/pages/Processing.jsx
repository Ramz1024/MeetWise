import { useParams, useNavigate } from "react-router-dom";
import "./Processing.css";

const typeConfig = {
  text: {
    title: "Text Transcript",
    desc: "Paste your meeting notes or transcript",
    icon: "📄",
    color: "#4f46e5", // blue
    buttonText: "Process Text Notes",
  },
  photo: {
    title: "Whiteboard Photo",
    desc: "Upload photos of whiteboards or notes",
    icon: "📷",
    color: "#ec4899", // pink
    buttonText: "Process Photos",
  },
  audio: {
    title: "Audio Recording",
    desc: "Upload meeting audio or voice memos",
    icon: "🎤",
    color: "#8b5cf6", // purple
    buttonText: "Process Audio",
  },
};

function Processing() {
  const { type } = useParams();
  const navigate = useNavigate();
  const config = typeConfig[type];

  if (!config) return <p>Invalid type selected!</p>;

  const handleProcess = () => {
    navigate(`/${type}`);
  };

  return (
    <div className="processing-container" style={{ borderColor: config.color }}>
      <div className="processing-header" style={{ color: config.color }}>
        <h2>{config.icon} Processing {config.title}...</h2>
        <p>{config.desc}</p>
      </div>

      <div className="processing-box">
        <div className="spinner">🔄</div>
        <p>Processing your {type}...</p>
      </div>

      {type === "text" && (
        <div className="transcript-box">
          <strong>Transcript preview:</strong>
          <pre>
Speaker 1: "We need to focus on our Q3 targets..."
Speaker 2: "I think we should prioritize the product launch first..."
Speaker 1: "Good point. Alex, can you take lead on that?"
Alex: "Absolutely, I can have the initial plan ready by Friday."
          </pre>
        </div>
      )}

      <button
        className="process-btn"
        onClick={handleProcess}
        style={{ backgroundColor: config.color }}
      >
        ✨ {config.buttonText} ✨
      </button>
    </div>
  );
}

export default Processing;
