import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { DiagramViewer } from "../src/components/Artifact/DiagramViewer";

describe("DiagramViewer", () => {
  it("renders an image with the SVG URL", () => {
    render(<DiagramViewer svgUrl="/api/v1/versions/v1/artifacts/a1/outputs/diagram.svg" />);
    const img = screen.getByAltText("Diagram");
    expect(img).toBeInTheDocument();
    expect(img).toHaveAttribute("src", "/api/v1/versions/v1/artifacts/a1/outputs/diagram.svg");
  });

  it("has zoom controls", () => {
    render(<DiagramViewer svgUrl="/test.svg" />);
    expect(screen.getByText("+")).toBeInTheDocument();
    expect(screen.getByText("-")).toBeInTheDocument();
    expect(screen.getByText("Reset")).toBeInTheDocument();
  });

  it("has fullscreen button", () => {
    render(<DiagramViewer svgUrl="/test.svg" />);
    expect(screen.getByText("Fullscreen")).toBeInTheDocument();
  });

  it("shows scale percentage", () => {
    render(<DiagramViewer svgUrl="/test.svg" />);
    expect(screen.getByText("100%")).toBeInTheDocument();
  });

  it("zoom in increases scale", () => {
    render(<DiagramViewer svgUrl="/test.svg" />);
    fireEvent.click(screen.getByText("+"));
    expect(screen.getByText("120%")).toBeInTheDocument();
  });
});
