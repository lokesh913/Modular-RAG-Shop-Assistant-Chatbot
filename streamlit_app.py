"""
Streamlit Cloud Deployment Entry Point
=======================================
A self-contained version of the Shop Assistant that embeds the RAG pipeline
directly (Pinecone vector search + Gemini 2.5 Flash) and loads the product
catalog from the bundled CSV file — no separate FastAPI server or MySQL
database required.

For local development with FastAPI + MySQL, use: frontend/app.py
"""

import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from google import genai

# ---------------------------------------------------------------------------
# Configuration — supports both Streamlit Cloud (st.secrets) and local (.env)
# ---------------------------------------------------------------------------
load_dotenv()


def get_secret(key):
    """Retrieve a secret from Streamlit Cloud secrets or fall back to .env."""
    try:
        return st.secrets[key]
    except (FileNotFoundError, KeyError):
        return os.getenv(key)


# LangChain reads GOOGLE_API_KEY from the environment automatically
_google_api_key = get_secret("GOOGLE_API_KEY")
if _google_api_key:
    os.environ["GOOGLE_API_KEY"] = _google_api_key

# ---------------------------------------------------------------------------
# RAG Services (embedded — replaces backend/services/)
# ---------------------------------------------------------------------------
_vectorstore = None


def get_vectorstore():
    """Return a cached PineconeVectorStore, creating it on first call."""
    global _vectorstore
    if _vectorstore is None:
        embedding_model = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            output_dimensionality=768,
        )
        pc = Pinecone(api_key=get_secret("PINECONE_API_KEY"))
        index = pc.Index("shop-product-catalog")
        _vectorstore = PineconeVectorStore(
            index=index,
            embedding=embedding_model,
            text_key="Description",
        )
    return _vectorstore


SYSTEM_MESSAGE = (
    "You are a helpful shop assistant. Answer only about the shop's product catalog. "
    "Use a friendly tone. If irrelevant, say: 'I can only help with product-related queries, sir.'"
)


def get_relevant_context(query):
    """Perform a Pinecone similarity search and format the top result."""
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search(query, k=1)
    if results:
        metadata = results[0].metadata
        return (
            f"Product Name: {metadata.get('ProductName')}\n"
            f"Brand: {metadata.get('ProductBrand')}\n"
            f"Price: {metadata.get('Price')}\n"
            f"Gender: {metadata.get('Gender')}\n"
            f"Color: {metadata.get('PrimaryColor')}\n"
            f"Description: {results[0].page_content}"
        )
    return "No relevant search found."


def generate_response(query, history):
    """Build a RAG prompt with vector context and call Gemini 2.5 Flash."""
    client = genai.Client(api_key=get_secret("GOOGLE_API_KEY"))
    history.append(f"User: {query}")
    context = get_relevant_context(query)
    prompt = (
        f"{SYSTEM_MESSAGE}\n\n"
        + "\n".join(history)
        + f"\n\nContext:\n{context}\n\nAssistant:"
    )
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt
    ).text
    history.append(f"Assistant: {response}")
    return response, history


# ---------------------------------------------------------------------------
# Data — load product catalog directly from CSV (replaces MySQL)
# ---------------------------------------------------------------------------
@st.cache_data
def load_products():
    """Load product catalog from the bundled CSV file."""
    csv_path = os.path.join(os.path.dirname(__file__), "data", "shop-product-catalog.csv")
    df = pd.read_csv(csv_path)
    return df.to_dict(orient="records")


# ============================================================================
# STREAMLIT UI — identical premium design to frontend/app.py
# ============================================================================
st.set_page_config(page_title="🛍️ Shop Assistant", layout="wide")

# ---- Premium Global & Component Styling ----
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

    /* Global Font Apply - Safe selectors that don't override Streamlit's icon fonts */
    html, body, [data-testid="stAppViewContainer"], .main, .stMarkdown, p, h1, h2, h3, select, input, button {
        font-family: 'Outfit', sans-serif;
    }

    /* Specifically target our custom component classes to use Outfit */
    .chat-bubble-user, .chat-bubble-assistant, .chat-header-user, .chat-header-assistant,
    .product-card, .product-title, .product-meta, .product-desc {
        font-family: 'Outfit', sans-serif !important;
    }

    /* Prevent custom font from breaking Streamlit's Material Symbols and Icons */
    [class^="material-"], [class*="material-"], .material-icons, [data-testid="collapsedControl"] i, [data-testid="stHeader"] i {
        font-family: 'Material Symbols Outlined', 'Material Symbols Rounded', 'Material Symbols Sharp', 'Material Icons' !important;
    }

    /* Chat bubble styles */
    .chat-bubble-user {
        background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
        color: #ffffff;
        padding: 12px 16px;
        border-radius: 16px 16px 4px 16px;
        box-shadow: 0 4px 12px rgba(30, 136, 229, 0.15);
        font-size: 14px;
        line-height: 1.4;
        margin-bottom: 12px;
        width: fit-content;
        max-width: 95%;
        margin-left: auto;
    }
    .chat-bubble-assistant {
        background-color: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(8px);
        color: #f5f5f5;
        padding: 12px 16px;
        border-radius: 16px 16px 16px 4px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        font-size: 14px;
        line-height: 1.4;
        margin-bottom: 12px;
        width: fit-content;
        max-width: 95%;
    }
    .chat-header-user {
        font-size: 11px;
        font-weight: 700;
        color: rgba(255, 255, 255, 0.6);
        margin-bottom: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        text-align: right;
    }
    .chat-header-assistant {
        font-size: 11px;
        font-weight: 700;
        color: #66bb6a;
        margin-bottom: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Product catalog styles */
    .product-card {
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        backdrop-filter: blur(12px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .product-card:hover {
        border-color: rgba(30, 136, 229, 0.4);
        box-shadow: 0 10px 30px rgba(30, 136, 229, 0.15);
        transform: translateY(-2px);
    }
    .product-title {
        font-size: 22px;
        font-weight: 600;
        margin-bottom: 10px;
        color: #ffffff;
    }
    .product-meta {
        font-size: 13px;
        color: #a0aab2;
        margin-bottom: 6px;
    }
    .product-desc {
        font-size: 14px;
        color: #cfd8dc;
        margin-top: 14px;
        line-height: 1.5;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
        padding-top: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---- Sidebar Chat UI ----
st.sidebar.title("💬 Assistant Chat")
st.sidebar.markdown("Ask anything about our products:")

# Display full chat history in sidebar
for msg in st.session_state.chat_history:
    if msg.startswith("User:"):
        text = msg[len("User:"):].strip()
        st.sidebar.markdown(f"""
            <div class="chat-header-user">You</div>
            <div class="chat-bubble-user">{text}</div>
        """, unsafe_allow_html=True)
    else:
        text = msg[len("Assistant:"):].strip()
        st.sidebar.markdown(f"""
            <div class="chat-header-assistant">🛍️ Assistant</div>
            <div class="chat-bubble-assistant">{text}</div>
        """, unsafe_allow_html=True)

# User input form to automatically clear input on submit
with st.sidebar.form(key="chat_form", clear_on_submit=True):
    user_query = st.text_input("Your question:")
    submit_button = st.form_submit_button("Send", use_container_width=True)

if submit_button and user_query.strip():
    try:
        response, history = generate_response(
            user_query, st.session_state.chat_history
        )
        st.session_state.chat_history = history
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"❌ AI Service Error: {e}")

# Reset Chat History button
st.sidebar.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
if st.sidebar.button("🗑️ Reset Chat History", use_container_width=True):
    st.session_state.chat_history = []
    st.rerun()

# ---- Main Page ----
st.title("🛒 Shop Product Catalog")
st.markdown("<hr>", unsafe_allow_html=True)

# Load product data from CSV
try:
    products = load_products()

    if not products:
        st.warning("No products found.")
    else:
        # Get filter values
        brands = sorted(set(p["ProductBrand"] for p in products if p["ProductBrand"]))
        genders = sorted(set(p["Gender"] for p in products if p["Gender"]))

        st.subheader("🔍 Filter Products")
        col1, col2, col3 = st.columns(3)

        with col1:
            selected_brand = st.selectbox("Brand", ["All"] + brands)
        with col2:
            selected_gender = st.selectbox("Gender", ["All"] + genders)
        with col3:
            sort_order = st.selectbox("Sort by Price", ["Default", "Low to High", "High to Low"])

        # Apply filters
        filtered = products
        if selected_brand != "All":
            filtered = [p for p in filtered if p["ProductBrand"] == selected_brand]
        if selected_gender != "All":
            filtered = [p for p in filtered if p["Gender"] == selected_gender]

        # Apply sorting
        if sort_order == "Low to High":
            filtered = sorted(filtered, key=lambda x: float(x["Price"]))
        elif sort_order == "High to Low":
            filtered = sorted(filtered, key=lambda x: float(x["Price"]), reverse=True)

        # Display products in two columns
        cols = st.columns(2)
        for idx, product in enumerate(filtered):
            with cols[idx % 2]:
                st.markdown(f"""
                    <div class="product-card">
                        <div class="product-title">{product['ProductName']}</div>
                        <div class="product-meta"><b>Brand:</b> {product['ProductBrand']} &nbsp; | &nbsp; <b>Gender:</b> {product['Gender']}</div>
                        <div class="product-meta"><b>Price:</b> ₹{product['Price']} &nbsp; | &nbsp; <b>Color:</b> {product['PrimaryColor']}</div>
                        <div class="product-desc">{product['Description']}</div>
                    </div>
                """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"⚠️ Could not load products: {e}")
