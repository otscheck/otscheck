# Libateli — Architecture & Product Notes (Public)
Libateli is an operations management platform for security companies (DRC).

## What problem it solves
- Staff, sites, missions, incidents, reporting (field-to-office traceability)
- Built for low bandwidth + real operational constraints

## Architecture (high-level)
- Backend: Laravel API (Sanctum), modular domain
- Frontend: Vue 3 (Composition API), Tailwind
- DB: MySQL
- CI/CD: GitHub Actions → VPS/Shared hosting

## What’s inside this repo
- Domain model (entities, boundaries)
- API contract (OpenAPI sample)
- Deployment notes & ops checklist
- Diagrams (Mermaid)

## What’s not here
No client data, no proprietary code. This is a public engineering overview.
