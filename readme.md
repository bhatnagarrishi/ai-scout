# Project Cortex: Digital Twin & Architecture Governance Platform
**Design Specification & Requirements Document**
**Version:** 1.0 (Draft)
**Date:** November 30, 2025

---

## 1. Executive Summary
**Cortex** is a converged Internal Developer Platform (IDP) and Enterprise Architecture engine. It acts as a "Digital Twin" of the organization, modeling the relationship between business strategy, software design, and physical infrastructure.

The system serves as the single source of truth for software inventory, architecture drift detection, and impact analysis, enabling Architects, SREs, and Leadership to visualize the state of the enterprise across time (Past, Present, and Future).

---

## 2. Strategic Objectives

1.  **The Holistic Digital Twin:** A queryable model linking **Domains & Platforms** $\to$ **Systems** $\to$ **Containers** $\to$ **Components** $\to$ **Code**, mapped to underlying physical/logical infrastructure.
2.  **The Time Machine:** Capability to visualize the graph at $t_{-1}$ (Past Snapshots), $t_{0}$ (Live State), and $t_{+1}$ (Future/Draft State).
3.  **The Truth Engine:** Intelligent synthesis of conflicting data points (Design vs. Runtime) with confidence scoring and automated reconciliation.
4.  **Automated Governance:** Moving from manual "checkbox" compliance to automated "Policy as Code" checks against Blueprints and Patterns.
5.  **Impact Intelligence:** A 360-degree dependency graph to analyze the ripple effects of failures, costs, and strategic changes.

---

## 3. Prioritization Roadmap

*   **Priority 0: Core Metamodel & Schema** (Defining the Ontology).
*   **Priority 1: Visualization** (The UI, "Google Maps" for Architecture, and Creation Tools).
*   **Priority 2: Identity Strategy & Ingestion** (Data entry, Auto-discovery, Identity Synthesis).
*   **Priority 3: Reconciliation Strategy** (Drift detection and logic resolution).

---

## 4. Functional Requirements

### 4.1. Core Metamodel (The Data Structure)
*   **Hierarchy:** Must support **C4 Model** extended with **Domain** and **Platform** layers.
*   **Components:** Libraries, SBOM entries, Docker Images, and Sidecars are classified as *Components*.
*   **Environment Strategy:** Distinct nodes for different environments (e.g., *Payment Svc [Dev]* and *Payment Svc [Prod]* are separate nodes linked to the same System).
*   **Pattern Nodes:** "Architecture Patterns" (e.g., "Event-Driven Microservice") must exist as nodes to allow validation against them.

### 4.2. Creation & Visualization (The Interface)
*   **Visual Editor:** A generic drag-and-drop canvas (embedded or integrated) to model *Future State*.
*   **SLA-Driven Design:** The creation tool must prompt users for SLAs (Throughput, RPO/RTO).
    *   *Validation:* The system must reject designs where technology choices conflict with SLAs (e.g., "Redis for Zero Data Loss").
*   **IDE Extension:** A VS Code extension to define architecture via `cortex.yaml` and validate code against it.
*   **Conversational Architect:** An LLM-backed chat interface to generate designs via natural language.
*   **Overlays:** Ability to toggle heatmaps on the graph for Cost, Health, and Compliance.

### 4.3. Ingestion & Discovery
*   **Auto-Discovery:** Pull adapters to read Cloud APIs (AWS/Azure/GCP), K8s Clusters, TF State files, Helm Charts, and Observability logs (Dynatrace/OTel).
*   **Identity Synthesis:** A heuristic engine to link disparate records (Git Repo + AWS Service + Jira Project) into a single entity using "Fact Corroboration."

### 4.4. Governance & Reconciliation
*   **Drift Detection:** Compare *Design Spec* vs. *Runtime Status* vs. *Approved Blueprints*.
*   **Resolution:** Discrepancies are flagged for human resolution (initially) with a roadmap to agentic auto-resolution.

---

## 5. Non-Functional Requirements (NFRs)
1.  **RBAC:** Fine-grained access control for viewing (e.g., hide Vulnerabilities from contractors) and editing.
2.  **Auditability:** Immutable logs of design changes and drift resolutions.
3.  **Extensibility:** API-first design; plugin architecture for new data sources.
4.  **Scalability:** Support for 100k+ nodes with sub-second graph traversal.

---

## 6. Detailed System Architecture

### 6.1. The Schema (JSON Model)
We utilize a **Kubernetes-style Object Model** separating Identity, Versioning, Design (Spec), and Runtime (Status).

```json
{
  "kind": "CONTAINER",
  "metadata": {
    "id": "uuid-v4",
    "name": "Payment Service", 
    "slug": "payment-svc-prod",
    "labels": { "cost_center": "123" },
    // The "Rosetta Stone" for Identity
    "identity_aliases": {
        "aws_arn": "arn:aws:ecs:...",
        "git_url": "github.com/org/repo"
    }
  },
  
  "version_context": {
    "version_id": "v1.0.2",
    "valid_from": "2025-01-01T10:00:00Z",
    "author": "ci-pipeline"
  },

  // The Design (Target of Blueprints)
  "spec": {
    "technology": "Java",
    "framework": "Spring Boot",
    "design_constraints": {
      "throughput_rpm": 1000000,
      "rpo_seconds": 0
    }
  },

  // The Reality (Target of Discovery)
  "status": {
    "actual_technology": "Java 17",
    "uptime_sla": "99.9%"
  }
}
```

### 6.2. Identity Strategy
The system uses a 3-Tier Resolution Model to merge incoming data:
1.  **Tier 1 (Explicit):** Matching unique UUID tags injected into Infrastructure/Code.
2.  **Tier 2 (Fingerprint):** Matching Commit SHAs, Image Hashes, or TF Resource Addresses.
3.  **Tier 3 (Heuristic):** Probabilistic matching on Name + Owner + Tech Stack (requires manual confirmation if confidence < 90%).

---

## 7. Implementation Phase 1: Core Module
**Objective:** Stand up the Graph Store and API to support the Schema.

*   **Database:** Neo4j (Graph DB).
*   **Backend:** Node.js (NestJS) or Go.
*   **Deliverables:**
    1.  Dockerized Graph DB with constraints applied.
    2.  `PUT /nodes` API with JSON Schema validation.
    3.  `GET /graph` API for the Visualization team.
    4.  Initial Identity Logic (Exact Match merging).