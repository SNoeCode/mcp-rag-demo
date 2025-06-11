# Save the README content into a file named README.md

readme_content = """
# MCP-RAG-Demo

## 🎯 Project Overview

This project is a tablet-optimized React application built for Vant4ge to demo AIDA, an AI assistant, at an upcoming conference. It uses Retrieval-Augmented Generation (RAG) and the Armada MCP backend to intelligently answer questions about the event.

The app is styled using AG UI, hosted on Vercel, and leverages Supabase and Clerk for backend services and authentication.

---

## 🧱 Architecture Overview

### 🔹 Frontend
- **Framework**: React
- **Styling**: AG UI
- **Auth**: Clerk
- **Hosting**: Vercel

### 🔹 Backend (MCP Layer)
- Built on **Armada's MCP framework**
- Powered by **RAG**
- Data includes:
  - Conference schedule/logistics
  - AIDA demo content
  - Scripted responses
- Vector DB: **Supabase Edge Functions / Postgres + pgvector**
- Guardrails + Tooling managed by MCP

---

## 📲 Core Features (MVP Scope)

### 1. AI Chat Interface
- Conversational UI powered by GPT-4o or Claude 3
- Text interaction + scripted responses
- FAQs + Schedule + Product Questions

### 2. RAG-Powered Backend
- Ingests structured metadata (CSV, JSON, Airtable)
- Uses MCP schema to process and respond
- Logs queries and tracks basic analytics

### 3. Admin Interface
- Authenticated access to upload structured data

---

## 🔄 Tech Stack

| Layer        | Tooling                                |
|--------------|----------------------------------------|
| Hosting      | Vercel                                 |
| Auth         | Supabase (POC) → Clerk (Production)    |
| DB / Vector  | Supabase with Postgres + pgvector      |
| Frontend     | React + AG UI                          |
| AI Model     | GPT-4o or Claude 3 (via API)           |
| Backend      | Armada MCP Core                        |

---

## 📋 Step-by-Step Setup & Implementation Guide

### ✅ Step 1: Frontend Setup

1. Create the React app:

```bash
npx create-react-app mcp-rag-demo --template typescript
cd mcp-rag-demo










<!-- 
A demo project showcasing a **tablet-optimized React application** powered by an **Armada MCP (Model Context Protocol) backend** with **Retrieval-Augmented Generation (RAG)**. Conference attendees interact with **AIDA**, our AI assistant, to ask questions about the event, demo experience, and product features.

---

## 📖 **Table of Contents**
- [Project Vision](#project-vision)
- [Architecture Overview](#architecture-overview)
- [Core Features (MVP)](#core-features-mvp)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Environment Variables](#environment-variables)
  - [Clone & Install](#clone--install)
  - [Running the Backend](#running-the-backend)
  - [Running the Frontend](#running-the-frontend)
  - [Running Tests](#running-tests)
- [Branching Strategy](#branching-strategy)
- [Sprint 1 Deliverables & Timeline](#sprint-1-deliverables--timeline)
- [Epic & User Stories](#epic--user-stories)
- [Future Roadmap](#future-roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 **Project Vision**
_As a conference attendee, I want to interact with AIDA through an intuitive tablet interface so that I can learn about the conference, demo capabilities, and product features in an engaging conversational experience._

---

## 🏗 **Architecture Overview**

### **Frontend**
- **React** app optimized for **iPad/Android tablets**
- **Component Library:** AG UI
- **Hosting:** Vercel
- **Auth:** Clerk (admin/preview access)

### **Backend (MCP Layer)**
- **Framework:** FastAPI + Docker
- **MCP Core:** Armada’s MCP framework
- **RAG Knowledge Base:**
  - Conference schedule & logistics
  - AIDA demo details
  - Scripted conversation flows
- **Vector Store:** Supabase (Postgres + pgvector or Edge Functions)
- **Logging & Analytics:** Basic interaction tracking

---

## 🌟 **Core Features (MVP)**

### **1. AI Chat Interface**
- Conversational UI powered by **GPT-4o** or **Claude 3**
- Text-based interaction with optional scripted responses
- Answers include:
  - Event schedule, locations, sessions
  - AIDA feature info & technical background
  - FAQs curated by Vant4ge

### **2. MCP-Driven RAG Backend**
- Ingest conference metadata (JSON/CSV/Airtable)
- Tooling support defined via MCP schema
- Logging + basic analytics

### **3. Basic Admin Interface**
- Secure file upload (JSON/CSV) for conference data
- Clerk-protected access for Vant4ge/Banyan teams

---

## 🔧 **Tech Stack**

| Layer            | Technology                          |
|-----------------|------------------------------------|
| **Frontend**    | React + AG UI                      |
| **Hosting**     | Vercel                             |
| **Auth**        | Clerk                              |
| **Backend (MCP)** | FastAPI + Armada MCP Core       |
| **Database**    | Supabase (Postgres + pgvector)     |
| **AI Model**    | GPT-4o / Claude 3 (via API)        |
| **Containerization** | Docker                        |
| **Testing**     | Pytest + FastAPI TestClient        |

---

## 🚀 **Getting Started**

### **Prerequisites**
- Node.js ≥ 18
- Python ≥ 3.10
- Docker & Docker Compose
- Git

### **Environment Variables**
Create a `.env` in the root (backend) and `.env.local` in `frontend/`:

```env
# backend/.env
SUPABASE_URL=https://xyz.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
CLERK_PUBLISHABLE_KEY=pk_...
CLERK_SECRET_KEY=sk_...
# any other MCP/Armada settings

# frontend/.env.local
NEXT_PUBLIC_SUPABASE_URL=https://xyz.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_...


Clone & Install
# Clone repo
git clone https://github.com/SNoeCode/mcp-rag-demo.git
cd mcp-rag-demo

# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..


Running the Backend
docker build -t mcp-rag-backend .
docker run -p 8000:8000 --env-file .env mcp-rag-backend


- Health Check: GET http://localhost:8000/health
- MCP Health:   GET http://localhost:8000/mcp/health-mcp
Running the Frontend
cd frontend
npm run dev


- Open your tablet-simulated browser at: http://localhost:3000
Running Tests
# Run FastAPI backend tests
pytest --maxfail=1 --disable-warnings -q

# Run any React frontend tests (if added)
cd frontend && npm test



🔀 Branching Strategy
- main → Production-ready, updated only when merging develop
- develop → Integration branch for all new work
- feature/* → New features branch off develop
- bugfix/* → Bug fixes branch off develop
- hotfix/* → Urgent fixes branch off develop
- release/* → (Optional) Version branches off develop for QA before merging into main

📅 Sprint 1 Deliverables & Timeline
| Week | Days | Goals / Tasks | 
| 1 | Days 1–2 | Setup FastAPI, Docker, Supabase connection | 
|  | Days 3–4 | Scaffold React + AG UI chat interface with dummy messaging | 
|  | Day 5 | Implement MCP endpoint (basic schema) + health check | 
| 2 | Days 1–2 | Load sample conference/AIDA data into Supabase; build RAG retrieval logic | 
|  | Days 3–4 | Connect frontend → backend; run integration tests | 
|  | Day 5 | Build basic admin interface; finalize testing; prepare for sprint review | 



🌍 Future Roadmap
- Voice chat integration (Whisper / streaming)
- Multi-session management & engagement tracking
- Live data updates via CMS/Airtable webhooks
- Analytics dashboard (top queries, usage trends)
- Multiple conference profiles via MCP “profiles”

🤝 Contributing
- Fork the repo & clone locally
- Create a branch off develop (e.g. feature/awesome-thing)
- Make your changes & write tests
- Push & open a PR → develop
- After review, merge & delete your branch

📜 License
MIT © SNoeCode Feel free to adapt and extend this demo for your own RAG + MCP experiments!

Save this as **README.md** in your repo. 🚀 Let me know if anything needs tweaking!


📌 Steps to Save the README File
- Copy the markdown content below
- Create a new file in your repository
cd path/to/mcp-rag-demo
touch README.md
- Open the file in a text editor (VS Code, Nano, Vim, etc.)
nano README.md
- Paste the markdown content
- Save the file, commit, and push it to GitHub
git add README.md
git commit -m "docs: add detailed README"
git push origin develop



📜 Full README.md File (Copy-Paste Below)
# MCP-RAG-Demo

A demo project showcasing a **tablet-optimized React application** powered by an **Armada MCP (Model Context Protocol) backend** with **Retrieval-Augmented Generation (RAG)**. Conference attendees interact with **AIDA**, our AI assistant, to ask questions about the event, demo experience, and product features.

---

## 📖 **Table of Contents**
- [Project Vision](#project-vision)
- [Epic Breakdown](#epic-breakdown)
- [Sprint 1 User Stories](#sprint-1-user-stories)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Environment Variables](#environment-variables)
  - [Clone & Install](#clone--install)
  - [Running the Backend](#running-the-backend)
  - [Running the Frontend](#running-the-frontend)
  - [Running Tests](#running-tests)
- [Branching Strategy](#branching-strategy)
- [Sprint 1 Timeline](#sprint-1-timeline)
- [Success Metrics](#success-metrics)
- [Future Roadmap](#future-roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 **Project Vision**
_As a conference attendee, I want to interact with AIDA through an intuitive tablet interface so that I can learn about the conference, demo capabilities, and product features in an engaging conversational experience._

---

## 📋 **Epic Breakdown**
### **Epic 1: Core Chat Experience**
**Goal:** Deliver a functional chat interface that conference attendees can use to interact with AIDA.

### **Epic 2: RAG-Powered Knowledge System**
**Goal:** Implement intelligent responses using conference and product data.

### **Epic 3: Admin Content Management**
**Goal:** Enable Vant4ge team to manage and upload demo content.

### **Epic 4: Technical Foundation**
**Goal:** Establish robust, scalable technical infrastructure.

---

## 🏃‍♂️ **Sprint 1 User Stories**

### **Epic 1: Core Chat Experience**
#### **Story 1.1: Basic Chat Interface**
**Goal:** Create a clean, tablet-optimized chat interface.

#### **Acceptance Criteria**
✅ Chat interface displays properly on tablet screens (10-13 inches)  
✅ Input field is easily accessible and responsive to touch  
✅ Message history scrolls smoothly  
✅ Uses reusable UI components for consistent styling  
✅ Interface is intuitive without training  

#### **Tasks & Step-by-Step Instructions**
##### **1️⃣ Set Up React Project**
```bash
cd frontend
npx create-react-app chat-ui
cd chat-ui
npm install react-router-dom styled-components
npm start


2️⃣ Research Reusable Component Libraries
- AG UI (your project’s standard UI library)
- Material-UI (MUI) → npm install @mui/material @emotion/react @emotion/styled
- React Native Web (for touch optimization) → npm install react-native-web
- Styled Components → npm install styled-components
3️⃣ Create Responsive Chat Container Component
import React from "react";
import styled from "styled-components";

const ChatWrapper = styled.div`
  width: 100%;
  max-width: 800px;
  height: 80vh;
  display: flex;
  flex-direction: column;
  border-radius: 10px;
  background: #f5f5f5;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
`;

const MessageHistory = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 10px;
`;

const ChatContainer = () => {
  return (
    <ChatWrapper>
      <MessageHistory>
        {/* Messages will go here */}
      </MessageHistory>
    </ChatWrapper>
  );
};

export default ChatContainer;


4️⃣ Implement Message Input Component
import React, { useState } from "react";
import styled from "styled-components";

const InputWrapper = styled.div`
  display: flex;
  padding: 10px;
  background: white;
  border-top: 1px solid #ddd;
`;

const InputField = styled.input`
  flex: 1;
  padding: 12px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 5px;
  outline: none;
`;

const SendButton = styled.button`
  margin-left: 10px;
  padding: 12px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
`;

const MessageInput = ({ onSend }) => {
  const [message, setMessage] = useState("");

  const handleSend = () => {
    if (message.trim() !== "") {
      onSend(message);
      setMessage("");
    }
  };

  return (
    <InputWrapper>
      <InputField
        type="text"
        placeholder="Type a message..."
        value={message}
        onChange={(e) => setMessage(e.target.value)}
      />
      <SendButton onClick={handleSend}>Send</SendButton>
    </InputWrapper>
  );
};

export default MessageInput;


5️⃣ Add Scroll Behavior for Message History
const MessageHistory = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  scroll-behavior: smooth;
`;


6️⃣ Test on Multiple Tablet Screen Sizes
- Use Chrome DevTools:
- Open the app in Chrome.
- Right-click → Inspect → Toggle Device Toolbar.
- Select iPad Pro (11-inch, 12.9-inch) and Samsung Galaxy Tab S7.

📅 Sprint 1 Timeline
| Week | Days | Goals / Tasks | 
| 1 | Days 1–2 | Setup FastAPI, Docker, Supabase connection | 
|  | Days 3–4 | Scaffold React + AG UI chat interface with dummy messaging | 
|  | Day 5 | Implement MCP endpoint (basic schema) + health check | 
| 2 | Days 1–2 | Load sample conference/AIDA data into Supabase; build RAG retrieval logic | 
|  | Days 3–4 | Connect frontend → backend; run integration tests | 
|  | Day 5 | Build basic admin interface; finalize testing; prepare for sprint review | 



🚀 Success Metrics
✅ Response time < 3 seconds for 95% of queries
✅ Zero critical security vulnerabilities
✅ 99% uptime during demo period
✅ Mobile/tablet performance score > 90

🤝 Contributing
- Fork the repo & clone locally
- Create a branch off develop (e.g. feature/chat-ui)
- Make your changes & write tests
- Push & open a PR → develop
- After review, merge & delete your branch

📜 License
MIT © SNoeCode
Feel free to adapt and extend this demo for your own RAG + MCP experiments!

---

### **✅ Final Steps**
1. **Save this markdown content as `README.md`**  
2. **Commit & push it to GitHub**  
3. **Open your repo, and GitHub will format everything correctly**  

🚀 **Your README is now fully detailed and ready to go!**









# MCP-RAG-Demo

## 🎯 Project Overview

We are building a tablet-optimized React application for Vant4ge to demo AIDA, our AI assistant, at an upcoming conference. The goal is to provide a scripted and intelligent experience where attendees can interact with AIDA and ask questions about the conference, the demo, and the product experience.

The backend is powered by Armada's MCP layer, using Retrieval-Augmented Generation (RAG) to feed the AI with curated data and context. The front end uses AG UI components and leverages Supabase, Clerk, and Vercel for backend, auth, and hosting infrastructure.

## 🧱 Architecture Overview

### 🔹 Frontend

* React App (tablet-optimized)
* Component library: AG UI
* Hosted on Vercel
* Auth via Clerk

### 🔹 Backend (MCP Layer)

* Built on Armada MCP framework (FastAPI + Docker)
* RAG-powered knowledge base:

  * Conference schedule & logistics
  * AIDA demo experience (Vant4ge)
  * Scripted conversation flow
* Vector DB: Supabase (pgvector)
* Tooling defined via MCP concepts

---

## 🚧 Epics & Detailed Implementation Guide

### 🧩 Epic 1: Core Chat Experience

#### 1.1 Tablet-optimized UI Layout

* Install dependencies:

```bash
npx create-react-app mcp-rag-demo --template typescript
cd mcp-rag-demo
npm install ag-ui clerk-sdk react-router-dom
```

* Build responsive layout in `App.tsx`:

```tsx
import { Container, Header, Footer } from "ag-ui";

function App() {
  return (
    <Container maxWidth="md">
      <Header title="Ask AIDA" />
      <Chat />
      <Footer content="Vant4ge Conference 2024" />
    </Container>
  );
}
```

#### 1.2 Basic Message Flow + Dummy RAG

* Create `Chat.tsx`:

```tsx
import { Input } from "ag-ui";
import { useState } from "react";

export const Chat = () => {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");

  const sendMessage = () => {
    setMessages([...messages, { sender: "user", text: input }, { sender: "AIDA", text: "This is a dummy response." }]);
    setInput("");
  };

  return (
    <div className="chat-container">
      {messages.map((msg, i) => <div key={i}><b>{msg.sender}:</b> {msg.text}</div>)}
      <Input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && sendMessage()} />
    </div>
  );
};
```

---

### 🧩 Epic 2: Knowledge-Powered Backend

#### 2.1 MCP Base Schema + Endpoint

* Set up FastAPI server:

```bash
mkdir backend && cd backend
python -m venv venv && source venv/bin/activate
pip install fastapi uvicorn openai supabase
```

* Create `main.py`:

```py
from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()

class Query(BaseModel):
    question: str

@app.post("/query")
async def query(data: Query):
    return {"answer": f"Echoing your question: {data.question}"}
```

#### 2.2 Supabase + pgvector Pipeline

* SQL for vector table:

```sql
create extension if not exists vector;
create table docs (
  id uuid default uuid_generate_v4(),
  content text,
  embedding vector(1536)
);
```

* Insert from script:

```py
from openai import OpenAI
from supabase import create_client

openai.api_key = "OPENAI_API_KEY"
supabase = create_client("SUPABASE_URL", "SUPABASE_KEY")

embedding = openai.Embedding.create(input="Schedule info", model="text-embedding-ada-002")
supabase.table("docs").insert({"content": "Schedule info", "embedding": embedding["data"][0]["embedding"]}).execute()
```

#### 2.3 Upload Tooling (CSV/Airtable)

* Accept CSV in FastAPI:

```py
from fastapi import UploadFile

@app.post("/upload")
async def upload(file: UploadFile):
    content = await file.read()
    # parse CSV and embed
    return {"status": "uploaded"}
```

---

### 🧩 Epic 3: Admin Management

#### 3.1 Clerk-Gated Upload Interface

* Add ClerkProvider and upload UI:

```tsx
import { ClerkProvider, SignedIn, SignedOut, SignIn, useUser } from "@clerk/clerk-react";

const AdminUpload = () => {
  const { user } = useUser();
  const handleUpload = async (e) => {
    const file = e.target.files[0];
    const form = new FormData();
    form.append("file", file);
    await fetch("/upload", { method: "POST", body: form });
  };
  return user ? <input type="file" onChange={handleUpload} /> : null;
};
```

---

### 🧩 Epic 4: Dev Infrastructure

#### 4.1 Vercel Deploy + Domains

* Push to GitHub, connect repo to Vercel.
* Add ENV vars: `CLERK_KEY`, `SUPABASE_URL`, `OPENAI_KEY`.

#### 4.2 Containerization + CI

* Create Dockerfile:

```Dockerfile
FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

* Add CI/CD workflow via GitHub Actions.

---

## 🌍 Future Roadmap

* 🎤 Voice chat (Whisper, streaming)
* 🧠 Multi-session engagement memory
* 🔄 CMS / Airtable syncing via webhook
* 📊 Admin dashboard (top queries, usage)
* 🎭 Multi-event switching with MCP profiles

---

## ✅ Success Criteria

* Functional tablet UI
* RAG responses based on uploaded content
* Secure admin dashboard
* Response time < 3s

## 🗓️ Sprint Timeline

**Week 1**: UI Shell, MCP Setup, Sample Data **Week 2**: RAG + Integration, Admin Panel, Testing

## 🌟 Contributors

* Product Owner: Matthew Wallace
* Engineering: Banyan Labs MCP + FE Team
* Customer: Vant4ge

## 🚀 Run the Project Locally

```bash
# Frontend
cd mcp-rag-demo
npm install
npm start

# Backend
cd backend
uvicorn main:app --reload
```

> 📅 This README.md captures the full project scope and gives step-by-step developer instructions. Ensure all credentials and environment variables are securely managed.












🎯 Project Vision
As a conference attendee, I want to interact with AIDA through an intuitive tablet interface so that I can learn about the conference, demo capabilities, and product features in an engaging conversational experience.

🏗 Architecture Overview
Frontend
- React app optimized for iPad/Android tablets
- Component Library: AG UI
- Hosting: Vercel
- Auth: Clerk (admin/preview access)
Backend (MCP Layer)
- Framework: FastAPI + Docker
- MCP Core: Armada’s MCP framework
- RAG Knowledge Base:
- Conference schedule & logistics
- AIDA demo details
- Scripted conversation flows
- Vector Store: Supabase (Postgres + pgvector or Edge Functions)
- Logging & Analytics: Basic interaction tracking

🌟 Core Features (MVP)
1. AI Chat Interface
- Conversational UI powered by GPT-4o or Claude 3
- Text-based interaction with optional scripted responses
- Answers include:
- Event schedule, locations, sessions
- AIDA feature info & technical background
- FAQs curated by Vant4ge
2. MCP-Driven RAG Backend
- Ingest conference metadata (JSON/CSV/Airtable)
- Tooling support defined via MCP schema
- Logging + basic analytics
3. Basic Admin Interface
- Secure file upload (JSON/CSV) for conference data
- Clerk-protected access for Vant4ge/Banyan teams

🔧 Tech Stack
| Layer | Technology | 
| Frontend | React + AG UI | 
| Hosting | Vercel | 
| Auth | Clerk | 
| Backend (MCP) | FastAPI + Armada MCP Core | 
| Database | Supabase (Postgres + pgvector) | 
| AI Model | GPT-4o / Claude 3 (via API) | 
| Containerization | Docker | 
| Testing | Pytest + FastAPI TestClient | 



🚀 Getting Started
Prerequisites
- Node.js ≥ 18
- Python ≥ 3.10
- Docker & Docker Compose
- Git
Environment Variables
Create a .env in the root (backend) and .env.local in frontend/:
# backend/.env
SUPABASE_URL=https://xyz.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
CLERK_PUBLISHABLE_KEY=pk_...
CLERK_SECRET_KEY=sk_...
# any other MCP/Armada settings

# frontend/.env.local
NEXT_PUBLIC_SUPABASE_URL=https://xyz.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_...


Clone & Install
# Clone repo
git clone https://github.com/SNoeCode/mcp-rag-demo.git
cd mcp-rag-demo

# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..


Running the Backend
docker build -t mcp-rag-backend .
docker run -p 8000:8000 --env-file .env mcp-rag-backend


- Health Check: GET http://localhost:8000/health
- MCP Health:   GET http://localhost:8000/mcp/health-mcp
Running the Frontend
cd frontend
npm run dev


- Open your tablet-simulated browser at: http://localhost:3000
Running Tests
# Run FastAPI backend tests
pytest --maxfail=1 --disable-warnings -q

# Run any React frontend tests (if added)
cd frontend && npm test



🔀 Branching Strategy
- main → Production-ready, updated only when merging develop.
- develop → Integration branch for all new work.
- feature/* → New features branch off develop.
- bugfix/* → Bug fixes branch off develop.
- hotfix/* → Urgent fixes branch off develop.
- release/* → (Optional) Version branches off develop for QA before merging into main.

📅 Sprint 1 Deliverables & Timeline
| Week | Days | Goals / Tasks | 
| 1 | Days 1–2 | Setup FastAPI, Docker, Supabase connection | 
|  | Days 3–4 | Scaffold React + AG UI chat interface with dummy messaging | 
|  | Day 5 | Implement MCP endpoint (basic schema) + health check | 
| 2 | Days 1–2 | Load sample conference/AIDA data into Supabase; build RAG retrieval logic | 
|  | Days 3–4 | Connect frontend → backend; run integration tests | 
|  | Day 5 | Build basic admin interface; finalize testing; prepare for sprint review | 



🔥 Epic & User Stories
Epic 1: Core Chat Experience
- Story 1.1: Basic tablet-optimized chat UI
- Story 1.2: Message flow & dummy responses
Epic 2: RAG-Powered Knowledge System
- Story 2.1: MCP Backend foundation
- Story 2.2: RAG integration with Supabase
- Story 2.3: Sample data ingestion
Epic 3: Admin Content Management
- Story 3.1: Secure admin interface for data uploads
Epic 4: Technical Foundation
- Story 4.1: Vercel hosting & deployment pipeline
- Story 4.2: Supabase vector storage setup

🌍 Future Roadmap (Post-MVP)
- Voice chat integration (Whisper / streaming)
- Multi-session management & engagement tracking
- Live data updates via CMS/Airtable webhooks
- Analytics dashboard (top queries, usage trends)
- Multiple conference profiles via MCP “profiles”

🤝 Contributing
- Fork the repo & clone locally
- Create a branch off develop (e.g. feature/awesome-thing)
- Make your changes & write tests
- Push & open a PR → develop
- After review, merge & delete your branch

📜 License
MIT © SNoeCode
Feel free to adapt and extend this demo for your own RAG + MCP experiments!

This file is **ready to save as `README.md`** and commit to your repo. 🚀 Let me know if you'd like any modifications!


 -->













# MCP-RAG-Demo
🎯 Project Overview

We are building a tablet-optimized React application for Vant4ge to demo AIDA, our AI assistant, at an upcoming conference. The goal is to provide a scripted and intelligent experience where attendees can interact with AIDA and ask questions about the conference, the demo, and the product experience.

The backend will be powered by Armada, our MCP layer, using Retrieval-Augmented Generation (RAG) to feed the AI with curated data and context. The front end will use AG UI components for a clean and scalable experience and rely on Supabase, Clerk, and Vercel for backend, auth, and hosting infrastructure.

🧱 Architecture Overview

🔹 Frontend
React App (optimized for iPad/Android tablets)
Component library: AG UI
Hosted on Vercel
Auth via Clerk (for admin/secure preview access)

🔹 Backend (MCP Layer)
Built on top of Armada's MCP framework
RAG-powered knowledge base fed by:
Conference schedule & logistics
AIDA demo experience details (provided by Vant4ge)
Scripted conversation flow guidance
Vector database: Supabase Edge Functions or integrated Postgres/Vector store
Guardrails & endpoint tooling defined via MCP concepts

📲 Core Features (MVP Scope)

1. AI Chat Interface
Conversational UI powered by GPT (e.g., GPT-4o or Claude 3, pending eval)
Text-based interaction with optional scripted responses
Capable of answering:
Event schedule, locations, sessions
AIDA feature info & technical background
FAQs curated by Vant4ge

2. MCP-Driven RAG Backend
Conference metadata ingested via structured formats (JSON, CSV, Airtable, etc.)
Tooling support (functions, external links) defined in MCP schema
Logging + basic analytics of interactions

3. Basic Admin Interface
Upload static data to MCP (Vant4ge content team)
Auth via Clerk for internal use only (Vant4ge/Banyan teams)

🧪 Sprint 1 Deliverables (Weeks 1–2)



Area
Deliverable
🧱 Frontend
Basic UI shell with AG UI layout
💬 Chat UI
Working chat input/output flow (dummy LLM or placeholder initially)
🧠 Backend
Initial MCP endpoint with basic schema for conference info
📚 RAG Setup
Upload sample conference + AIDA data provided by Vant4ge
🔁 RAG Integration
Connect frontend to backend for RAG-augmented answers
🧪 QA
Internal testing flow: Ask AIDA about key conference info

🔄 Tech Stack



Layer
Tooling
Hosting
Vercel
Auth
Supabase for POC → Clerk for Production
DB / Vector Store
Supabase (Postgres w/ pgvector or embeddings)
Frontend
React + AG UI
AI Model
GPT-4o or Claude 3 via API
Backend (MCP)
Armada MCP Core + RAG Endpoints

🧭 Future Iterations (Post-MVP)

Voice chat integration (whisper / streaming)
Multi-session management (track engagement)
Live data updates (webhooks from CMS or Airtable)
Analytics dashboard (usage trends, top queries)
Multiple conference support via MCP “profiles”

👥 Key Stakeholders



Role
Name
Product Owner
Matthew Wallace (Banyan Labs)
Partner / Customer
Vant4ge Product & Marketing Team
AI Experience Lead
[Insert Vant4ge Contact]
Engineering
Banyan Labs MCP + Frontend Teams

✅ Success Criteria (for MVP)

Working tablet-ready UI with stable, styled chat interface
RAG system returns accurate answers from uploaded Vant4ge data
Vant4ge team can simulate AIDA conference experience end-to-end
Positive internal feedback on usability and experience flow

🗓️ Target Sprint 1 Timeline

Kickoff: [Insert Date]
Sprint Review: [Insert Date 2 weeks later]
Data Handoff from Vant4ge: Within 3 days of kickoff
LLM Model Selection Finalized: Within 1 week

Let me know if you’d like a Notion version of this brief or a ClickUp project plan generated from it.




🎯 Project Vision
As a conference attendee, I want to interact with AIDA through an intuitive tablet interface so that I can learn about the conference, demo capabilities, and product features in an engaging conversational experience.


📋 Epic Breakdown
Epic 1: Core Chat Experience
Goal: Deliver a functional chat interface that conference attendees can use to interact with AIDA
Epic 2: RAG-Powered Knowledge System
Goal: Implement intelligent responses using conference and product data
Epic 3: Admin Content Management
Goal: Enable Vant4ge team to manage and upload demo content
Epic 4: Technical Foundation
Goal: Establish robust, scalable technical infrastructure


🏃‍♂️ Sprint 1 User Stories
Epic 1: Core Chat Experience
Story 1.1: Basic Chat Interface
As a conference attendee
I want to see a clean, tablet-optimized chat interface
So that I can easily interact with AIDA on an iPad or Android tablet
Acceptance Criteria:
[ ] Chat interface displays properly on tablet screens (10-13 inches)
[ ] Input field is easily accessible and responsive to touch
[ ] Message history scrolls smoothly
[ ] Uses reusable UI components for consistent styling
[ ] Interface is intuitive without training
Story Points: 5
Tasks:
[ ] Set up React project 
[ ] Research reusable component libraries
[ ] Create responsive chat container component
[ ] Implement message input component with touch optimization
[ ] Design message bubble components or use one from library
[ ] Add scroll behavior for message history
[ ] Test on multiple tablet screen sizes
[ ] Implement basic loading states


Story 1.2: Message Flow
As a conference attendee
I want to send messages and receive responses from AIDA
So that I can have a natural conversation experience
Acceptance Criteria:
[ ] User can type and send messages
[ ] Mock data is used to test 
[ ] Messages appear in chat history immediately
[ ] AI responses display with appropriate timing/animation
[ ] Messages are clearly distinguished between user and AI
[ ] Character limits are handled gracefully
Story Points: 3
Tasks:
[ ] Implement message state management
[ ] Create send message functionality
[ ] Use mock message data for testing
[ ] Add message timestamp handling
[ ] Implement typing indicators
[ ] Add message delivery confirmation
[ ] Handle empty/invalid message submission


Epic 2: RAG-Powered Knowledge System
Story 2.1: MCP Backend Foundation
As a system administrator
I want a working MCP endpoint that can process conference data
So that AIDA can provide intelligent responses about the event
Acceptance Criteria:
[ ] MCP endpoint accepts and processes conference data
[ ] Basic schema defined for conference information
[ ] Endpoint returns structured responses
[ ] Error handling for malformed requests
[ ] Basic logging implemented
Story Points: 8
Tasks:
[ ] Set up Armada MCP core infrastructure or adjust existing core accordingly
[ ] Define conference data schema (JSON/CSV structure)
[ ] Create basic MCP endpoint for data ingestion
[ ] Implement error handling and validation
[ ] Set up basic logging system
[ ] Create health check endpoint
[ ] Document API endpoints


Story 2.2: RAG Integration
As a conference attendee
I want AIDA to answer questions using real conference data
So that I get accurate, relevant information about the event
Acceptance Criteria:
[ ] Frontend connects to MCP backend successfully
[ ] RAG system retrieves relevant information for queries
[ ] Responses include conference-specific details
[ ] System handles "I don't know" scenarios gracefully
[ ] Response time is under 3 seconds for typical queries
Story Points: 13
Tasks:
[ ] Set up Supabase vector database
[ ] Implement RAG retrieval logic
[ ] Connect frontend to backend API
[ ] Add query processing and context building
[ ] Implement fallback responses for unknown topics
[ ] Add response caching for common queries
[ ] Test with sample conference data


Story 2.3: Sample Data Integration
As a Vant4ge team member
I want sample conference and AIDA data loaded into the system
So that we can test the complete user experience
Acceptance Criteria:
[ ] Sample conference schedule uploaded successfully
[ ] AIDA product information available in knowledge base
[ ] FAQ data integrated and searchable
[ ] Data covers key demo scenarios
[ ] System responds accurately to test queries
Story Points: 5
Tasks:
[ ] Create sample conference data (schedule, sessions, locations)
[ ] Prepare AIDA product information dataset
[ ] Create FAQ dataset for common questions
[ ] Upload data to vector database
[ ] Test data retrieval accuracy
[ ] Validate responses match expected content


Epic 3: Admin Content Management
Story 3.1: Basic Admin Interface
As a Vant4ge content manager
I want a simple interface to upload conference data
So that I can manage the content AIDA will reference
Acceptance Criteria:
[ ] Secure admin interface accessible via authentication
[ ] File upload functionality for JSON/CSV data
[ ] Upload progress indication
[ ] Success/error feedback for uploads
[ ] Basic data validation before processing
Story Points: 8
Tasks:
[ ] Set up Clerk/Supabase authentication
[ ] Create admin dashboard layout
[ ] Implement file upload component
[ ] Add data validation logic
[ ] Create upload progress tracking
[ ] Implement success/error notifications
[ ] Add basic user role management


Epic 4: Technical Foundation
Story 4.1: Hosting and Deployment
As a developer
I want the application deployed to Vercel with proper configuration
So that the demo is accessible and performant for conference use
Acceptance Criteria:
[ ] Application successfully deployed to Vercel
[ ] Environment variables properly configured
[ ] Build process optimized for production
[ ] HTTPS and security headers configured
[ ] Performance meets tablet optimization standards
Story Points: 3
Tasks:
[ ] Configure Vercel deployment pipeline
[ ] Set up environment variables
[ ] Optimize build configuration
[ ] Configure security headers
[ ] Set up monitoring and error tracking
[ ] Test deployment on tablet devices


Story 4.2: Database Setup
As a system administrator
I want Supabase configured with vector storage capabilities
So that the RAG system can efficiently store and retrieve data
Acceptance Criteria:
[ ] Supabase project created and configured
[ ] Vector storage (pgvector) enabled
[ ] Database schema matches MCP requirements
[ ] Connection pooling configured for performance
[ ] Backup and recovery procedures documented
Story Points: 5
Tasks:
[ ] Create Supabase project
[ ] Enable pgvector extension
[ ] Design database schema for conference data
[ ] Set up connection configuration
[ ] Configure database security rules
[ ] Test database performance with sample data


🧪 Definition of Done
For each User Story:
[ ] All acceptance criteria met
[ ] Code reviewed and approved
[ ] Unit tests written and passing
[ ] Integration tested on tablet devices
[ ] Documented for handoff
[ ] Performance validated (under 3s response time)
[ ] Accessibility requirements met
[ ] Security review completed
For Sprint 1:
[ ] All user stories completed
[ ] End-to-end demo flow working
[ ] Vant4ge team can test complete experience
[ ] Performance benchmarks met
[ ] Deployment to staging environment successful


🎯 Sprint 1 Capacity Planning
Total Story Points: 50 Sprint Duration: 2 weeks Team Velocity Estimate: 25-30 points per week
Priority Order:
Story 4.1 & 4.2 (Technical Foundation) - 8 points
Story 1.1 & 1.2 (Basic Chat) - 8 points
Story 2.1 (MCP Backend) - 8 points
Story 2.3 (Sample Data) - 5 points
Story 2.2 (RAG Integration) - 13 points
Story 3.1 (Admin Interface) - 8 points


🚀 Success Metrics
Technical Metrics:
Response time < 3 seconds for 95% of queries
Zero critical security vulnerabilities
99% uptime during demo period
Mobile/tablet performance score > 90
User Experience Metrics:
Successful end-to-end demo completion
Positive feedback from Vant4ge team
All key conference scenarios testable
Intuitive user interaction (no training required)


📅 Sprint 1 Timeline
Week 1:
Days 1-2: Technical foundation setup
Days 3-4: Basic chat interface development
Day 5: MCP backend foundation
Week 2:
Days 1-2: Sample data integration and RAG setup
Days 3-4: RAG integration and testing
Day 5: Admin interface and final testing


  
