import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

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
with st.sidebar.form(key='chat_form', clear_on_submit=True):
    user_query = st.text_input("Your question:")
    submit_button = st.form_submit_button("Send", use_container_width=True)

if submit_button and user_query.strip():
    try:
        res = requests.post(f"{BACKEND_URL}/chat", json={
            "query": user_query,
            "history": st.session_state.chat_history
        })
        data = res.json()
        st.session_state.chat_history = data["history"]
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"❌ API Error: {e}")

# Reset Chat History button
st.sidebar.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
if st.sidebar.button("🗑️ Reset Chat History", use_container_width=True):
    st.session_state.chat_history = []
    st.rerun()

# ---- Main Page ----
st.title("🛒 Shop Product Catalog")
st.markdown("<hr>", unsafe_allow_html=True)

# Fetch product data from backend
try:
    response = requests.get(f"{BACKEND_URL}/products")
    products = response.json()

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
    st.error(f"⚠️ Could not fetch products: {e}")