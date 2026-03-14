const STATUS_COLORS: Record<string, string> = {
  draft: "bg-gray-700 text-gray-300",
  active: "bg-green-900 text-green-300",
  archived: "bg-yellow-900 text-yellow-300",
  review: "bg-blue-900 text-blue-300",
  approved: "bg-green-900 text-green-300",
  superseded: "bg-gray-700 text-gray-400",
  proposed: "bg-blue-900 text-blue-300",
  accepted: "bg-green-900 text-green-300",
  deprecated: "bg-red-900 text-red-300",
  open: "bg-orange-900 text-orange-300",
  answered: "bg-green-900 text-green-300",
  deferred: "bg-gray-700 text-gray-400",
  pending: "bg-gray-700 text-gray-300",
  rendering: "bg-blue-900 text-blue-300",
  success: "bg-green-900 text-green-300",
  error: "bg-red-900 text-red-300",
};

export function StatusBadge({ status }: { status: string }) {
  const colors = STATUS_COLORS[status] ?? "bg-gray-700 text-gray-300";
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${colors}`}>
      {status}
    </span>
  );
}
