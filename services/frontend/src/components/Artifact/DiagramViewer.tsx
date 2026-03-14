import { useState, useRef, useEffect } from "react";

interface DiagramViewerProps {
  svgUrl: string;
}

export function DiagramViewer({ svgUrl }: DiagramViewerProps) {
  const [scale, setScale] = useState(1);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [dragging, setDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [fullscreen, setFullscreen] = useState(false);
  const [svgContent, setSvgContent] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const containerRef = useRef<HTMLDivElement>(null);

  // Fetch SVG content inline
  useEffect(() => {
    setLoading(true);
    setSvgContent(null);
    setScale(1);
    setPosition({ x: 0, y: 0 });

    fetch(svgUrl)
      .then((res) => res.text())
      .then((text) => {
        // Add width/height 100% to the SVG root element so it scales
        const patched = text.replace(
          /<svg\s/,
          '<svg style="width:100%;height:100%;" '
        );
        setSvgContent(patched);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [svgUrl]);

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.1 : 0.1;
    setScale((s) => Math.max(0.1, Math.min(5, s + delta)));
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    setDragging(true);
    setDragStart({ x: e.clientX - position.x, y: e.clientY - position.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!dragging) return;
    setPosition({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y,
    });
  };

  const handleMouseUp = () => setDragging(false);

  const resetView = () => {
    setScale(1);
    setPosition({ x: 0, y: 0 });
  };

  const toggleFullscreen = () => {
    if (!fullscreen && containerRef.current) {
      containerRef.current.requestFullscreen?.();
    } else {
      document.exitFullscreen?.();
    }
  };

  useEffect(() => {
    const handler = () => setFullscreen(!!document.fullscreenElement);
    document.addEventListener("fullscreenchange", handler);
    return () => document.removeEventListener("fullscreenchange", handler);
  }, []);

  return (
    <div ref={containerRef} className="relative bg-white rounded border border-gray-700 overflow-hidden">
      {/* Controls */}
      <div className="absolute top-2 right-2 z-10 flex gap-1">
        <button
          onClick={() => setScale((s) => Math.min(5, s + 0.2))}
          className="px-2 py-1 bg-gray-800 border border-gray-600 rounded text-sm hover:bg-gray-700 text-gray-200"
        >
          +
        </button>
        <button
          onClick={() => setScale((s) => Math.max(0.1, s - 0.2))}
          className="px-2 py-1 bg-gray-800 border border-gray-600 rounded text-sm hover:bg-gray-700 text-gray-200"
        >
          -
        </button>
        <button
          onClick={resetView}
          className="px-2 py-1 bg-gray-800 border border-gray-600 rounded text-sm hover:bg-gray-700 text-gray-200"
        >
          Reset
        </button>
        <button
          onClick={toggleFullscreen}
          className="px-2 py-1 bg-gray-800 border border-gray-600 rounded text-sm hover:bg-gray-700 text-gray-200"
        >
          {fullscreen ? "Exit" : "Fullscreen"}
        </button>
      </div>

      {/* Scale indicator */}
      <div className="absolute bottom-2 left-2 z-10 text-xs text-gray-100 bg-gray-800/80 px-2 py-0.5 rounded">
        {Math.round(scale * 100)}%
      </div>

      {/* SVG viewport */}
      <div
        className="cursor-grab active:cursor-grabbing"
        style={{ height: fullscreen ? "100vh" : "500px" }}
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        {loading ? (
          <div className="flex items-center justify-center h-full text-gray-400">Loading...</div>
        ) : svgContent ? (
          <div
            style={{
              transform: `translate(${position.x}px, ${position.y}px) scale(${scale})`,
              transformOrigin: "center top",
              width: "100%",
              height: "100%",
            }}
            dangerouslySetInnerHTML={{ __html: svgContent }}
          />
        ) : (
          <div className="flex items-center justify-center h-full text-gray-400">Failed to load diagram</div>
        )}
      </div>
    </div>
  );
}
