import { useParams } from "react-router-dom";
import { ComparisonView } from "../components/Artifact/ComparisonView";

export function ComparisonPage() {
  const { projectId } = useParams<{ projectId: string }>();

  if (!projectId) return <div className="text-gray-400">Missing parameters</div>;

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-100 mb-6">Version Comparison</h1>
      <ComparisonView projectId={projectId} />
    </div>
  );
}
