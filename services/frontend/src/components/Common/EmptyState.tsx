export function EmptyState({ message, action }: { message: string; action?: React.ReactNode }) {
  return (
    <div className="text-center py-12 text-gray-400">
      <p className="mb-4">{message}</p>
      {action}
    </div>
  );
}
