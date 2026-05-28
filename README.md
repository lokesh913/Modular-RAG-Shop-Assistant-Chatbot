# 🛍️ Modular RAG Shop Assistant Chatbot

[![Python Version](https://img.shields.io/badge/Python-3.14+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.45+-red.svg)](https://streamlit.io/)
[![Pinecone](https://img.shields.io/badge/Pinecone-Vector_DB-blueviolet.svg)](https://www.pinecone.io/)
[![Gemini 2.5 Flash](https://img.shields.io/badge/Gemini-2.5_Flash-orange.svg)](https://deepmind.google/technologies/gemini/)

An ultra-modern, high-performance **Modular RAG (Retrieval-Augmented Generation)** conversational shop assistant. It integrates a **FastAPI** backend endpoint, **Streamlit** frontend interface, a relational **MySQL** database for metadata/queries, and **Pinecone Vector Search DB** alongside **Gemini 2.5 Flash** for powerful semantic retrieval and intelligent agentic customer responses.

## 📸 Application Preview

![Application Preview](assets/screenshot.png)

---

## 🌟 Key Features

* **Dual-Database Architecture**: Uses **MySQL** for structured product catalogs and **Pinecone Vector Database** for fast semantic embeddings and similarity queries.
* **Modern LLM Integration**: Leverages `gemini-2.5-flash` for high-quality, friendly chat responses grounded only on your store's context.
* **Fully Modular Structure**: Clean semantic separation of concerns (frontend app, backend routes, services, db utilities, and data syncers).
* **Responsive Filtering & Search**: Streamlit catalog filtering by Brand, Gender, and Price sorting synced live with MySQL.
* **Aesthetic Premium Design**: Elegant glassmorphism dark-mode interface with custom typography (`Outfit` from Google Fonts), micro-animations, and smooth responsive elements.

---

## 📂 Project Architecture & Directory Layout

```directory
Modular-RAG-Shop-Assistant-Chatbot/
│
├── backend/                  # Core Backend REST API
│   ├── db/                   # Database utilities
│   │   └── mysql.py          # MySQL Connector connection pool
│   ├── routes/               # FastAPI route definitions
│   │   ├── chat.py           # /chat endpoint integrating Gemini RAG
│   │   └── products.py       # /products catalog fetch endpoint
│   ├── services/             # Application business logic services
│   │   ├── gemini_chain.py   # RAG pipeline with Context & Gemini LLM
│   │   └── vector_store.py   # Pinecone Vector Store initialization
│   └── main.py               # FastAPI App initialization & Middleware
│
├── frontend/                 # Interactive Streamlit UI
│   └── app.py                # Streamlit Web App with Premium Custom CSS
│
├── data/                     # Local data storage and seed scripts
│   ├── shop-product-catalog.csv # Source dataset downloaded from Kaggle
│   └── data_insertion.py     # MySQL DB ingestion/seeding script
│
├── embeddings/               # Semantic synchronization
│   └── sync_pinecone.py      # Pinecone embedding & syncing script
│
├── main.py                   # Root FastAPI server entry point launcher
├── pyproject.toml            # Project dependencies & modern UV environment configs
├── uv.lock                   # Deterministic lockfile for python environment
├── .gitignore                # Production grade Git ignore definitions
└── README.md                 # Project documentation (You are here!)
```

---

## 🚀 Setup & Installation Instructions

Follow these step-by-step instructions to get your local environment configured and servers running:

### 1. Prerequisites

Ensure you have **Python 3.14+** installed. We highly recommend using [**uv**](https://github.com/astral-sh/uv) (a fast Python package installer and resolver) to manage dependencies effortlessly.

### 2. Download the Kaggle Dataset

The product catalog dataset for this project comes from Kaggle:
* **Dataset Link**: [Shop Product Catalog on Kaggle](https://www.kaggle.com/datasets/supratimnag06/shop-product-catalog)
* **Instructions**:
  1. Download the `shop-product-catalog.csv` file from Kaggle.
  2. Create a folder named `data/` in the project root if it doesn't exist.
  3. Save the downloaded CSV file as `data/shop-product-catalog.csv`.

### 3. Database Configurations (MySQL Setup)

You will need a running **MySQL** instance locally or in the cloud.

1. Open your MySQL client (e.g., MySQL Workbench, Command Line, etc.) and run:
   ```sql
   CREATE DATABASE assistant_chatbot;
   ```
2. Navigate into the database and create the `products` table schema:
   ```sql
   USE assistant_chatbot;

   CREATE TABLE products (
       ProductID INT PRIMARY KEY,
       ProductName VARCHAR(255) NOT NULL,
       ProductBrand VARCHAR(255),
       Gender VARCHAR(50),
       Price DECIMAL(10, 2),
       Description TEXT,
       PrimaryColor VARCHAR(50)
   );
   ```

### 4. Vector Database Setup (Pinecone)

1. Create a free account at [Pinecone](https://www.pinecone.io/).
2. Create an API Key in the Pinecone Console.
3. Keep your index name as `shop-product-catalog` with the metric set to `dotproduct` and dimension set to `768` (or let the `sync_pinecone.py` script automatically create it for you!).

### 5. Setup Environment Variables

Create a file named `.env` in your project root directory and add the following keys with your local credentials:

```env
# Database Credentials
DB_PASSWORD="your_mysql_root_password"

# Pinecone Credentials
PINECONE_API_KEY="your_pinecone_api_key"

# Google Gemini Credentials
GOOGLE_API_KEY="your_gemini_api_key"
```

### 6. Dependency Installation

If you are using `uv`, synchronize your environment with:
```bash
uv sync
```
Otherwise, use standard `pip` to install packages listed in `pyproject.toml`:
```bash
pip install fastapi google-genai langchain langchain-google-genai mysql-connector-python pandas pinecone langchain-pinecone python-dotenv requests streamlit tqdm uvicorn
```

---

## ⚙️ Data Ingestion & Index Syncing

Before running the application, seed the relational database and sync your vector embeddings:

### 1. Ingest Data into MySQL
Seed your MySQL `products` database using the Kaggle CSV dataset:
```bash
# If using UV:
uv run data/data_insertion.py

# Or standard python:
python data/data_insertion.py
```

### 2. Embed and Sync with Pinecone Vector Store
Generate dense semantic embeddings using `models/gemini-embedding-001` and synchronize them into your Pinecone Index:
```bash
# If using UV:
uv run embeddings/sync_pinecone.py

# Or standard python:
python embeddings/sync_pinecone.py
```

---

## 🏃 Running the Application

Both servers can run concurrently. Open two terminal instances in your project root folder:

### Terminal 1: Launch Backend API (FastAPI)
The backend API exposes endpoints for query answering (`/chat`) and fetching the structured products catalog (`/products`).
```bash
# If using UV:
uv run main.py

# Or standard python:
python main.py
```
* **API URL**: `http://localhost:8000`
* **API Documentation**: `http://localhost:8000/docs` (Swagger UI)

### Terminal 2: Launch Frontend App (Streamlit UI)
The premium UI provides filters for catalog browsing and an interactive chatbot sidebar.
```bash
# If using UV:
uv run streamlit run frontend/app.py

# Or standard python:
python -m streamlit run frontend/app.py
```
* **UI URL**: `http://localhost:8501`

---

## 🛠️ Verification & API Handshakes

To verify system connectivity, check the following endpoints:
1. **API Health Check**: `GET http://localhost:8000/` returns `{"status": "ok", "message": "Shop Assistant API is running"}`.
2. **Product Catalog Fetch**: `GET http://localhost:8000/products` returns all seeded MySQL rows as a list.
3. **Chat Response**: `POST http://localhost:8000/chat` with body `{"query": "Do you have White Adidas shoes?"}` queries Pinecone, retrieves matching items, sends the formatted prompt context to Gemini 2.5 Flash, and returns an expert response seamlessly.

---

## 🌐 Cloud Deployment Guide

This project is fully structured to support cloud deployments. Below are step-by-step instructions to launch the stack online using popular hosting platforms.

### ⚡ Autopilot Features: Schema & Data Seeding
We have built a custom lifespan startup hook in the FastAPI backend. **When deployed to the cloud, the backend automatically detects if your MySQL table is empty. It will create the table schema and seed all 129 product records from `data/shop-product-catalog.csv` automatically!** You do not need to manually import database dumps.

### Method 1: Hybrid Platforms (Free Tier Friendly 🌟)

#### 1. Host MySQL Database Online
* Go to [Railway](https://railway.app/) or [Aiven](https://aiven.io/).
* Create a free **MySQL** database instance.
* Note down the host address, port, username, password, and database name.

#### 2. Host FastAPI Backend on Render or Railway
* Create a new Web Service pointing to your GitHub repository.
* Set the build command to install dependencies or point the service to utilize the modern `backend.Dockerfile`.
* Configure the following **Environment Variables**:
  * `MYSQLHOST`: Your cloud database host address.
  * `MYSQLUSER`: Your database username.
  * `MYSQLPASSWORD`: Your database password.
  * `MYSQLDATABASE`: Your database name.
  * `MYSQLPORT`: Your database port (usually `3306`).
  * `GOOGLE_API_KEY`: Your Google Gemini API Key.
  * `PINECONE_API_KEY`: Your Pinecone Vector DB API Key.
* Railway/Render will assign a public domain to your backend (e.g. `https://your-api.up.railway.app` or `https://your-api.onrender.com`).

#### 3. Host Streamlit Frontend on Streamlit Community Cloud
* Go to [Streamlit Community Cloud](https://streamlit.io/cloud) and click **"New App"**.
* Select your GitHub repository, branch `main`, and set the main file path to `frontend/app.py`.
* In the Advanced settings, add the following **Environment Variable**:
  * `BACKEND_URL`: `https://your-deployed-api-url.onrender.com` (use your deployed backend URL).
* Click **Deploy!** Your app is now live with a public address!

---

## 🛡️ License

This project is open-source and available under the [MIT License](LICENSE).
