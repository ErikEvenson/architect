import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { DiagramViewer } from "../src/components/Artifact/DiagramViewer";

const mockFetch = vi.fn();
global.fetch = mockFetch as unknown as typeof fetch;

beforeEach(() => {
  mockFetch.mockReset();
  mockFetch.mockResolvedValue({
    text: () => Promise.resolve('<svg width="100" height="100"><rect /></svg>'),
  });
});

describe("DiagramViewer", () => {
  it("fetches the SVG from the given URL and renders it inline", async () => {
    const url = "/api/v1/versions/v1/artifacts/a1/outputs/diagram.svg";
    const { container } = render(<DiagramViewer svgUrl={url} />);

    expect(mockFetch).toHaveBeenCalledWith(url);
    await waitFor(() => {
      expect(container.querySelector("svg")).not.toBeNull();
    });
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
