import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { ArtifactList } from "../src/components/Artifact/ArtifactList";
import type { Artifact } from "../src/api/types";

const makeArtifact = (overrides: Partial<Artifact> = {}): Artifact => ({
  id: "a1",
  version_id: "v1",
  name: "Test Diagram",
  artifact_type: "diagram",
  detail_level: "conceptual",
  engine: "diagrams_py",
  source_code: null,
  output_paths: [],
  render_status: "pending",
  render_error: null,
  sort_order: 0,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
  ...overrides,
});

describe("ArtifactList", () => {
  it("renders artifact names", () => {
    const artifacts = [makeArtifact({ name: "VPC Diagram" })];
    render(
      <ArtifactList artifacts={artifacts} selectedId={null} onSelect={vi.fn()} onDelete={vi.fn()} />,
    );
    expect(screen.getByText("VPC Diagram")).toBeInTheDocument();
  });

  it("filters by detail level", () => {
    const artifacts = [
      makeArtifact({ id: "a1", name: "Conceptual", detail_level: "conceptual" }),
      makeArtifact({ id: "a2", name: "Deployment", detail_level: "deployment" }),
    ];
    render(
      <ArtifactList artifacts={artifacts} selectedId={null} onSelect={vi.fn()} onDelete={vi.fn()} />,
    );

    // Click deployment tab
    fireEvent.click(screen.getByText("deployment"));
    expect(screen.getByText("Deployment")).toBeInTheDocument();
    expect(screen.queryByText("Conceptual")).not.toBeInTheDocument();
  });

  it("calls onSelect when artifact is clicked", () => {
    const onSelect = vi.fn();
    const artifact = makeArtifact({ name: "VPC Diagram" });
    render(
      <ArtifactList artifacts={[artifact]} selectedId={null} onSelect={onSelect} onDelete={vi.fn()} />,
    );
    fireEvent.click(screen.getByText("VPC Diagram"));
    expect(onSelect).toHaveBeenCalledWith(artifact);
  });

  it("highlights selected artifact", () => {
    const artifact = makeArtifact({ id: "a1", name: "VPC Diagram" });
    const { container } = render(
      <ArtifactList artifacts={[artifact]} selectedId="a1" onSelect={vi.fn()} onDelete={vi.fn()} />,
    );
    const card = container.querySelector(".border-blue-400");
    expect(card).not.toBeNull();
  });
});
