import { useParams } from "react-router-dom";
import { ComparisonView } from "../components/Artifact/ComparisonView";

export function ComparisonPage() {
  const { clientId, projectId } = useParams<{ clientId: string; projectId: string }>();

  if (!clientId || !projectId) return <div className="text-gray-500">Missing parameters</div>;

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Version Comparison</h1>
      <ComparisonView projectId={projectId} clientId={clientId} />
    </div>
  );
}
