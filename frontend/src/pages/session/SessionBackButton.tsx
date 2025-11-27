import React from "react";
import { Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";

interface SessionBackButtonProps {
  label?: string;
  className?: string;
  tone?: "default" | "light";
}

const SessionBackButton: React.FC<SessionBackButtonProps> = ({
  label = "Quay lại",
  className = "",
  tone = "default",
}) => {
  const toneStyles = {
    default: {
      text: "text-blue-600 hover:text-blue-700",
      icon: "bg-blue-50 text-blue-600",
    },
    light: {
      text: "text-white/80 hover:text-white",
      icon: "bg-white/10 text-white",
    },
  } as const;

  const styles = toneStyles[tone];

  return (
    <Link
      to="/sessions"
      className={`inline-flex items-center gap-2 text-sm font-semibold transition ${styles.text} ${className}`}
    >
      <span
        className={`inline-flex h-9 w-9 items-center justify-center rounded-xl ${styles.icon}`}
      >
        <ArrowLeft className="h-4 w-4" />
      </span>
      {label}
    </Link>
  );
};

export default SessionBackButton;

