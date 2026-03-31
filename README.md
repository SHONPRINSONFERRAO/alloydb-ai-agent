# 🤖 AlloyDB AI Interactive Agent (Cloud Run & Vertex AI)

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python) 
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi) 
![Google Cloud](https://img.shields.io/badge/Google_Cloud-Cloud_Run-4285F4?style=for-the-badge&logo=google-cloud) 
![AlloyDB](https://img.shields.io/badge/Database-AlloyDB_for_PostgreSQL-green?style=for-the-badge)

A fully serverless, highly-interactive database agent that allows non-technical users to chat directly with an e-commerce inventory database. 

Instead of writing complex PostgreSQL queries or using rigid reporting dashboards, users can simply type natural language (e.g., *"Which products are out of stock?"*) into a sleek web interface. The agent intelligently translates the concept into optimized SQL, executes it against a private **AlloyDB** instance, and visually renders the results as stylized product cards.

---

## 🛠️ Technology/ Tools
*   **Framework:** FastAPI (Python)
*   **Intelligence:** Gemini 1.5 Flash (via Vertex AI)
*   **Tooling/Drivers:** `asyncpg` (PostgreSQL driver), `google-genai` (Vertex AI SDK)
*   **Database:** AlloyDB for PostgreSQL (with Vector Embeddings)
*   **Deployment:** Google Cloud Run 

## 🏗️ Architecture

```mermaid
graph LR
    subgraph Client ["🌐 Client Side"]
    User([Business User]) 
    style User fill:#e8f0fe,stroke:#1a73e8,stroke-width:2px
    end

    subgraph CloudRun ["☁️ Google Cloud Run"]
    Agent[FastAPI Python Agent] 
    UI[Custom HTML/JS Chat UI]
    style Agent fill:#fff,stroke:#4285F4,stroke-width:2px
    style UI fill:#fff,stroke:#4285F4,stroke-width:2px
    end

    subgraph AI ["🧠 Serverless AI"]
    VertexAI[Vertex AI<br/>Gemini 1.5 Flash] 
    style VertexAI fill:#fce4ec,stroke:#d81b60,stroke-width:2px
    end

    subgraph DB ["🗄️ Virtual Private Cloud"]
    AlloyDB[(AlloyDB SQL Database<br/>with Vector Embeddings)] 
    style AlloyDB fill:#e6f4ea,stroke:#1e8e3e,stroke-width:2px
    end

    User <-->|HTTP / HTML / JSON| UI
    UI <-->|POST /query| Agent
    
    Agent -->|1. Prompt| VertexAI
    VertexAI -->|2. SQL Query| Agent
    
    Agent -->|3. asyncpg| AlloyDB
    AlloyDB -->|4. Results| Agent

    %% Styling
    classDef default font-family:Arial,font-size:13px;
    style CloudRun fill:#f8f9fa,stroke:#4285F4,stroke-dasharray: 5 5
    style AI fill:#fff5f8,stroke:#d81b60,stroke-dasharray: 5 5
    style DB fill:#f1f8e9,stroke:#1e8e3e,stroke-dasharray: 5 5
```

## ✨ Key Features
*   **🗣️ Natural Language to SQL:** No more complex filters just type in English to query your live database records.
*   **🧠 Vector Similarity Search:** Built utilizing AlloyDB's native `vector` extensions to perform conceptual searches (e.g., "Show me music-related items").
*   **🎨 Interactive Chat UI:** A sleek, product-card based interface that replaces raw JSON with user-friendly visuals.
*   **☁️ Zero-Ops Deployment:** No Dockerfile required—utilizing Google Cloud Native Buildpacks and Secure VPC Connectivity.

## 🚀 Usage Examples

### Request: 
*"Which products are out of stock?"*

### Response: 
*   **☕ Coffee Maker** (Category: Home | Price: $45.00 | Stock: 0) — *Programmable coffee maker with a 12-cup glass carafe.*
*   **⛺ Camping Tent** (Category: Outdoors | Price: $120.00 | Stock: 0) — *Spacious waterproof dome tent.*
*   **🪑 Ergonomic Office Chair** (Category: Furniture | Price: $149.50 | Stock: 0) — *Adjustable mesh office chair with lumbar support for long working hours.*

---

### Request: 
*"Show me items under $100"*

### Response: 
*   **👟 Running Shoes** (Category: Apparel | Price: $89.50 | Stock: 20) — *Lightweight and durable.*
*   **☕ Coffee Maker** (Category: Home | Price: $45.00 | Stock: 0)
*   **🧘 Yoga Mat** (Category: Outdoors | Price: $25.00 | Stock: 100)
*   **🔈 Bluetooth Speaker** (Category: Electronics | Price: $39.99 | Stock: 50)
*   **💧 Stainless Steel Water Bottle** (Category: Outdoors | Price: $15.00 | Stock: 200)
*   **🖱️ Wireless Gaming Mouse** (Category: Electronics | Price: $59.90 | Stock: 25)
*   **🧥 Cotton Hooded Sweatshirt** (Category: Apparel | Price: $45.00 | Stock: 40)
*   **⌚ Fitness Tracker Watch** (Category: Electronics | Price: $89.99 | Stock: 60)
*   **🪥 Electric Toothbrush** (Category: Health & Beauty | Price: $49.99 | Stock: 30)
*   **☕ Ceramic Coffee Mug Set** (Category: Home | Price: $22.50 | Stock: 100)
*   **👛 Leather Wallet** (Category: Accessories | Price: $35.00 | Stock: 50)

## Created by Shon Ferrao
