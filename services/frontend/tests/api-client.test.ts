import { describe, it, expect, vi, beforeEach } from "vitest";
import { clientsApi, projectsApi, versionsApi, adrsApi, questionsApi } from "../src/api/client";

const mockFetch = vi.fn();
global.fetch = mockFetch;

beforeEach(() => {
  mockFetch.mockReset();
});

function mockResponse(data: unknown, status = 200) {
  mockFetch.mockResolvedValueOnce({
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(data),
    statusText: "OK",
  });
}

describe("clientsApi", () => {
  it("list calls GET /api/v1/clients", async () => {
    mockResponse([{ id: "1", name: "Acme" }]);
    const result = await clientsApi.list();
    expect(mockFetch).toHaveBeenCalledWith("/api/v1/clients", expect.objectContaining({ headers: expect.any(Object) }));
    expect(result).toHaveLength(1);
  });

  it("create calls POST /api/v1/clients", async () => {
    mockResponse({ id: "1", name: "Acme", slug: "acme" }, 201);
    await clientsApi.create({ name: "Acme" });
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/clients",
      expect.objectContaining({ method: "POST", body: JSON.stringify({ name: "Acme" }) }),
    );
  });

  it("delete calls DELETE /api/v1/clients/:id", async () => {
    mockFetch.mockResolvedValueOnce({ ok: true, status: 204, json: () => Promise.resolve(null) });
    await clientsApi.delete("123");
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/clients/123",
      expect.objectContaining({ method: "DELETE" }),
    );
  });
});

describe("projectsApi", () => {
  it("list calls GET /api/v1/clients/:id/projects", async () => {
    mockResponse([]);
    await projectsApi.list("c1");
    expect(mockFetch).toHaveBeenCalledWith("/api/v1/clients/c1/projects", expect.any(Object));
  });
});

describe("versionsApi", () => {
  it("create calls POST /api/v1/projects/:id/versions", async () => {
    mockResponse({ id: "v1", version_number: "1.0.0" }, 201);
    await versionsApi.create("p1", { version_number: "1.0.0" });
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/projects/p1/versions",
      expect.objectContaining({ method: "POST" }),
    );
  });
});

describe("adrsApi", () => {
  it("supersede calls POST /api/v1/versions/:id/adrs/:id/supersede", async () => {
    mockResponse({ id: "a2", adr_number: 2 }, 201);
    await adrsApi.supersede("v1", "a1", {
      title: "New ADR",
      context: "ctx",
      decision: "dec",
      consequences: "con",
    });
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/versions/v1/adrs/a1/supersede",
      expect.objectContaining({ method: "POST" }),
    );
  });
});

describe("questionsApi", () => {
  it("list with filters appends query params", async () => {
    mockResponse([]);
    await questionsApi.list("v1", { status: "open", category: "security" });
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/versions/v1/questions?status=open&category=security",
      expect.any(Object),
    );
  });
});
