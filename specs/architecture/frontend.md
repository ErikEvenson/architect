# Frontend Architecture

## Overview

React SPA built with Vite and TypeScript, served by nginx-unprivileged. Communicates with the backend via `/api/` reverse proxy.

## Component Hierarchy

```
App
├── Layout
│   ├── Header (logo, app title)
│   ├── Sidebar (client/project/version tree navigation)
│   └── Content (routed pages)
│
├── Pages
│   ├── DashboardPage (overview, recent activity)
│   ├── ClientDetailPage (client info, project list)
│   ├── ProjectDetailPage (project info, versions, ADRs, questions)
│   ├── VersionDetailPage (version info, artifact list)
│   ├── ADRListPage (ADRs for a project)
│   ├── ADRDetailPage (single ADR view/edit)
│   └── QuestionListPage (questions for a project)
│
└── Components
    ├── Sidebar/
    │   └── NavigationTree (expandable client → project → version)
    ├── Client/
    │   ├── ClientForm (create/edit)
    │   └── ClientCard
    ├── Project/
    │   ├── ProjectForm (create/edit)
    │   ├── ProjectCard
    │   └── BestPracticesPanel (contextual suggestions)
    ├── Version/
    │   ├── VersionForm (create/edit)
    │   └── VersionCard
    ├── ADR/
    │   ├── ADRForm (create/edit)
    │   ├── ADRCard
    │   └── ADRStatusBadge
    ├── Question/
    │   ├── QuestionForm (create/answer)
    │   ├── QuestionCard
    │   └── QuestionCategoryBadge
    └── Common/
        ├── StatusBadge
        ├── EmptyState
        └── ConfirmDialog
```

## Routing

| Path | Page | Description |
|---|---|---|
| `/` | DashboardPage | Overview |
| `/clients/:clientId` | ClientDetailPage | Client details + projects |
| `/clients/:clientId/projects/:projectId` | ProjectDetailPage | Project details + versions |
| `/clients/:clientId/projects/:projectId/versions/:versionId` | VersionDetailPage | Version details + artifacts |
| `/clients/:clientId/projects/:projectId/adrs` | ADRListPage | ADR list |
| `/clients/:clientId/projects/:projectId/adrs/:adrId` | ADRDetailPage | ADR detail |
| `/clients/:clientId/projects/:projectId/questions` | QuestionListPage | Question list |

## State Management

- **Server state**: TanStack Query for API data fetching, caching, and mutations
- **Client state**: Zustand for UI state (sidebar collapse, selected items)
- No global form state — forms use local React state

## API Client

- Generated from OpenAPI spec types (manual TypeScript types matching `rest-api.yaml`)
- Base URL from `window.ARCHITECT_CONFIG.API_URL` (injected via ConfigMap)
- All requests go through `/api/` which nginx proxies to the backend

## Styling

- Tailwind CSS for utility-first styling
- Clean default theme: neutral grays, blue accent (#2563EB)
- Responsive layout with collapsible sidebar

## nginx Configuration

- HTTP :8080 — health check only
- HTTPS :8443 — SPA + API reverse proxy
- `/api/` → `http://architect-backend:8000/`
- Static assets: 1-year cache with immutable
- SPA fallback: `try_files $uri $uri/ /index.html`

## Build

- Vite production build → `dist/`
- TypeScript strict mode
- Code splitting by route (lazy loading)
