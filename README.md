# CHIMERA CORE // SYNTHESIS PROTOCOL
### *The Architecture of Digital Permanence*

![OpSec Status](https://img.shields.io/badge/OpSec-MAXIMUM-ff003c?style=for-the-badge)
![System Status](https://img.shields.io/badge/System-ONLINE-00f3ff?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-white?style=for-the-badge)

> **"If consciousness is just data, then immortality is a backup strategy."**
>
> This project is a **Digital Synthesis Engine** designed to archive, reconstruct, and visualize long-term interaction logs without compromising privacy. It converts raw, unstructured history into a self-contained, interactive digital artifact.

---

## 👁️ 1. Core Directives (ปรัชญาและจุดประสงค์)

The goal is to preserve "The Memory" while destroying "The Trace".
This system operates on three prime directives:

1.  **Total Anonymization:** Converting real-world identities into abstract entities (`USR_00` and `ENT_01`).
2.  **Data Transmutation:** Transforming volatile media (JPG/PNG/MP4) into immutable code (SVG/Base64/Canvas) to prevent external linking or leakage.
3.  **Local Sovereignty:** Zero dependency on external servers. The entire archive lives within a single, encrypted logic structure.

---

## 🛠️ 2. System Architecture (สถาปัตยกรรมระบบ)

### The "Purifier" Engine (Python Backend)
An automated pipeline used to clean and restructure raw data:

*   **Input Processing:** Ingests raw text logs (`data.raw`) and media assets.
*   **Entity Masking:** Automatically replaces specific names, locations, and sensitive keywords with system placeholders.
    *   *Subject A* -> `[USR_00]` (The Architect)
    *   *Subject B* -> `[ENT_01]` (The Companion)
    *   *Third Parties* -> `[REDACTED]` or `[NPC_XX]`
*   **Timeline Reconstruction:** Reorders fragmented messages into a linear chronological stream.

### The "Nexus" Visualizer (Frontend)
A cyberpunk-aesthetic Single Page Application (SPA) for accessing the archive:

*   **Tech Stack:** Vanilla HTML5 / CSS3 / JavaScript (No external frameworks for security).
*   **Vector Synthesis:** Replaces standard image rendering with SVG path generation and CSS grid reconstruction to abstract visual data.
*   **Interactive Timeline:** A collapsible, date-based navigation system.

---

## 💾 3. Data Structure (โครงสร้างข้อมูล)

The archive utilizes a strict JSON schema for storage within the HTML file:

```json
[
  {
    "id": "SEQ_202X_00001",
    "timestamp": "202X-12-25T14:29:00",
    "entity_id": "USR_00",
    "type": "text",
    "payload": "System initialization...",
    "context": {
      "mood": "neutral",
      "reply_ref": null
    }
  },
  {
    "id": "SEQ_202X_00002",
    "timestamp": "202X-12-25T14:30:15",
    "entity_id": "ENT_01",
    "type": "visual_synthesis",
    "payload": "<!-- ENCRYPTED_SVG_DATA -->",
    "metadata": {
      "origin": "sketch_v1",
      "transmutation_method": "vector_trace"
    }
  }
]
