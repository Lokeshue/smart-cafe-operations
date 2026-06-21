interface RushAlertProps {
  detected: boolean;
  message?: string;
}

export default function RushAlert({ detected, message }: RushAlertProps) {
  if (!detected) return null;

  return (
    <div className="flex items-center gap-3 rounded-lg border border-red-300 bg-red-50 px-4 py-3 text-red-800">
      <span className="text-xl">⚠️</span>
      <div>
        <p className="font-semibold">Rush Hour Alert</p>
        <p className="text-sm">{message || "High order volume detected."}</p>
      </div>
    </div>
  );
}
