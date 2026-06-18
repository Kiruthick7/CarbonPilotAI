interface EmptyStateProps {
  message: string;
}

export function EmptyState({ message }: EmptyStateProps) {
  return (
    <div className="flex items-center justify-center h-full min-h-[300px]">
      <p className="text-gray-500">{message}</p>
    </div>
  );
}
