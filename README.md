# 🧭 Multi-Agent Tour Guide System using LangGraph

A conversational **AI Tour Guide Agent** powered by **LangGraph** and multiple cooperative agents. The system can handle tourist queries, suggest destinations, generate itineraries, recommend hotels/restaurants, and even respond in local languages.

---

## 🌐 Overview

This project uses **LangGraph**, an agentic framework for LLM applications, to coordinate multiple agents working together to provide a rich, interactive tour guide experience.

---

## 🧠 Agents in the System

### 1. 🕵️ Research Agent
- Gathers information about the location (weather, events, history, attractions)
- Powered by tools like Tavily, Wikipedia API, or custom RAG retriever

### 2. 📅 Planner Agent
- Creates a personalized day-wise travel itinerary
- Considers user preferences (nature, temples, nightlife, etc.)

### 3. 🍽️ Recommendation Agent
- Suggests restaurants, hotels, local foods, and activities
- Integrates with external APIs (Google Places, Zomato, etc.)

### 4. 🌐 Translator Agent (optional)
- Converts output into the user’s local language (e.g., Telugu, Hindi)

### 5. 🤖 Main Controller Agent
- Routes input/output between agents based on conversation flow
- Maintains memory, chat history, and ensures goal completion

---

## ⚙️ Tech Stack

- **LangGraph** – Agent orchestration
- **LangChain** – Agent framework
- **LLM** – OpenAI, Google Gemini, or Hugging Face (customizable)
- **Tools** – Tavily, WikipediaAPI, browser tools, translation APIs
- **Backend** – Python (FastAPI optional)
- **Frontend** – Streamlit or Web UI (optional)

---

## 🛠️ Installation

```bash
git clone https://github.com/yourusername/tour-guide-langgraph.git
cd tour-guide-langgraph
pip install -r requirements.txt
