const STATUS_COLORS: Record<string, string> = {
  draft: "bg-gray-100 text-gray-700",
  active: "bg-green-100 text-green-700",
  archived: "bg-yellow-100 text-yellow-700",
  review: "bg-blue-100 text-blue-700",
  approved: "bg-green-100 text-green-700",
  superseded: "bg-gray-100 text-gray-500",
  proposed: "bg-blue-100 text-blue-700",
  accepted: "bg-green-100 text-green-700",
  deprecated: "bg-red-100 text-red-700",
  open: "bg-orange-100 text-orange-700",
  answered: "bg-green-100 text-green-700",
  deferred: "bg-gray-100 text-gray-500",
  pending: "bg-gray-100 text-gray-700",
  rendering: "bg-blue-100 text-blue-700",
  success: "bg-green-100 text-green-700",
  error: "bg-red-100 text-red-700",
};

export function StatusBadge({ status }: { status: string }) {
  const colors = STATUS_COLORS[status] ?? "bg-gray-100 text-gray-700";
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${colors}`}>
      {status}
    </span>
  );
}
