import os
import sys
import time
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag_engine import RAGEngine
from src.openrouter_client import OpenRouterClient, DEFAULT_FREE_MODELS

# Page configuration
st.set_page_config(
    page_title="DarGlobal & Wasalt Real Estate AI",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Adaptive Luxury CSS Styling (Supports both Light and Dark mode seamlessly)
st.markdown("""
<style>
    /* Luxury Typography */
    h1, h2, h3 {
        font-family: 'Playfair Display', Georgia, serif;
        letter-spacing: -0.01em;
    }
    
    /* Default / Light Mode Styling */
    h1, h2, h3 {
        color: #946c15 !important;
    }
    
    .badge-darglobal {
        background-color: var(--secondary-background-color, #f8f9fa);
        border: 1px solid #b8860b;
        border-radius: 8px;
        padding: 12px 14px;
        margin-bottom: 10px;
        color: var(--text-color, #1e293b);
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    
    .badge-gold {
        color: #946c15;
        font-weight: 700;
    }
    
    /* Chat message styling */
    .stChatMessage {
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 10px;
    }
    
    /* Property Highlight Card */
    .property-card {
        background-color: var(--secondary-background-color, #ffffff);
        border: 1px solid rgba(184, 134, 11, 0.35);
        border-radius: 10px;
        padding: 16px;
        margin-top: 10px;
        margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }
    
    .property-card:hover {
        border-color: #b8860b;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(184, 134, 11, 0.15);
    }
    
    .property-card h4 {
        margin: 0 0 8px 0;
        color: #946c15 !important;
        font-weight: 700;
    }
    
    .property-card p {
        color: var(--text-color, #334155) !important;
        font-size: 0.88rem;
        line-height: 1.5;
        margin-top: 8px;
        margin-bottom: 8px;
    }
    
    .property-tag {
        display: inline-block;
        background-color: rgba(184, 134, 11, 0.12);
        color: #8a6508 !important;
        border: 1px solid rgba(184, 134, 11, 0.4);
        font-size: 0.75rem;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 4px;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    
    .link-btn {
        display: inline-block;
        color: #ffffff !important;
        background: #b8860b;
        text-decoration: none !important;
        padding: 6px 14px;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-top: 8px;
        transition: background 0.2s ease;
    }
    .link-btn:hover {
        background: #946c15;
    }

    /* Dark Mode Overrides */
    @media (prefers-color-scheme: dark) {
        h1, h2, h3 {
            color: #e2c082 !important;
        }
        
        .badge-darglobal {
            background: linear-gradient(135deg, #161b22 0%, #21262d 100%);
            border: 1px solid #c5a059;
            color: #f0f6fc;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
        }
        
        .badge-gold {
            color: #d4af37;
        }
        
        .property-card {
            background-color: #161b22;
            border: 1px solid #30363d;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }
        
        .property-card:hover {
            border-color: #c5a059;
        }
        
        .property-card h4 {
            color: #e2c082 !important;
        }
        
        .property-card p {
            color: #c9d1d9 !important;
        }
        
        .property-tag {
            background-color: #21262d;
            color: #e2c082 !important;
            border: 1px solid #c5a059;
        }
        
        .link-btn {
            background: #c5a059;
            color: #0d1117 !important;
        }
        .link-btn:hover {
            background: #d4af37;
        }
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_rag_engine():
    return RAGEngine()

rag_engine = load_rag_engine()

# Sidebar Setup
with st.sidebar:
    st.markdown("## 🏛️ DarGlobal & Wasalt")
    st.markdown("*Premier Real Estate AI Advisor*")
    st.markdown("---")

    # API Key Configuration
    env_api_key = os.getenv("OPENROUTER_API_KEY", "")
    api_key_input = st.text_input(
        "OpenRouter API Key",
        value=st.session_state.get("openrouter_key", env_api_key),
        type="password",
        help="Free models from OpenRouter (e.g. Llama 3.3 70B, Gemini 2.0 Flash) will be used."
    )
    if api_key_input:
        st.session_state["openrouter_key"] = api_key_input

    # Model Selection
    selected_model = st.selectbox(
        "Select Free OpenRouter Model",
        options=DEFAULT_FREE_MODELS,
        index=0,
        help="These models are accessible for free on OpenRouter."
    )

    # Source Filter
    source_filter = st.selectbox(
        "Knowledge Source Filter",
        options=["All Sources", "DarGlobal", "Wasalt", "Dar Al Arkan / DarGlobal"],
        index=0
    )

    st.markdown("---")
    st.markdown("### 📊 Knowledge Base Stats")
    st.markdown("""
    <div class="badge-darglobal">
        <div>🌍 <b>Indexed Assets</b>: <span class="badge-gold">368 Properties & Projects</span></div>
        <div style="margin-top:4px;">🏢 <b>Global Brands</b>: Lamborghini, Aston Martin, Pagani, Trump, Missoni, Fendi, Elie Saab</div>
        <div style="margin-top:4px;">🇸🇦 <b>Wasalt Coverage</b>: Riyadh, Jeddah, Al Khobar, Dammam, Makkah, Madinah</div>
        <div style="margin-top:4px;">📈 <b>LSE Listing</b>: LSE: DAR (17.3% ROE)</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": """Welcome! I am your **DarGlobal & Wasalt Luxury Real Estate Advisor**.

I can help you explore:
* **DarGlobal Signature Flagships**: *Tierra Viva by Lamborghini* (Spain), *DaVinci Tower by Pagani* (Dubai), *The Astera by Aston Martin* (RAK), *AIDA by Trump & Fendi Casa* (Oman), *Trump Tower Dubai*, and *Trump Plaza Jeddah*.
* **Wasalt Properties & Saudi Markets**: Active listings for apartments, luxury villas, and compounds across Riyadh, Jeddah, Al Khobar, and Dammam.
* **Investment Insights**: Freehold foreign ownership laws, Golden Visa perks, and corporate financial performance (LSE: DAR).

How may I assist your property portfolio today?"""
        }
    ]

# Header Area
st.title("🏛️ DarGlobal & Wasalt Real Estate AI")
st.caption("AI-Powered Real Estate Advisory & Property Intelligence across Global Portfolios & the Kingdom of Saudi Arabia")

# Quick suggestion chips
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("🏎️ Tierra Viva Lamborghini", use_container_width=True):
        st.session_state["prompt_input"] = "Tell me about Tierra Viva Lamborghini villas in Spain: prices, specifications, and villa types."
with col2:
    if st.button("⛳ AIDA Trump & Fendi Oman", use_container_width=True):
        st.session_state["prompt_input"] = "What are the prices, villa types, and residency perks for AIDA Trump Golf and Fendi Casa villas in Oman?"
with col3:
    if st.button("🏙️ Riyadh Apartments (Wasalt)", use_container_width=True):
        st.session_state["prompt_input"] = "Show me luxury apartments for sale in Riyadh from Wasalt, including price in SAR, area, and district."
with col4:
    if st.button("📈 DarGlobal Corporate & ROE", use_container_width=True):
        st.session_state["prompt_input"] = "What is DarGlobal's background, London Stock Exchange listing, CEO, and Return on Ego (ROE) philosophy?"

# Display existing messages
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "retrieved_docs" in msg and msg["retrieved_docs"]:
            with st.expander("📚 Verified Real Estate Sources & Property Links"):
                for doc in msg["retrieved_docs"]:
                    st.markdown(f"""
                    <div class="property-card">
                        <h4>{doc['title']}</h4>
                        <span class="property-tag">{doc['source']}</span>
                        <span class="property-tag">{doc['category']}</span>
                        <span class="property-tag">{doc['city']}, {doc['country']}</span>
                        <span class="property-tag">Price: {doc['price']}</span>
                        <p style="font-size:0.85rem; color:#8b949e; margin-top:6px;">{doc['content'][:250]}...</p>
                        <a href="{doc['url']}" target="_blank" class="link-btn">View Official Listing ↗</a>
                    </div>
                    """, unsafe_allow_html=True)

# Prompt input
user_query = st.chat_input("Ask about DarGlobal developments, Wasalt listings, prices, or investment terms...")
if "prompt_input" in st.session_state and st.session_state["prompt_input"]:
    user_query = st.session_state["prompt_input"]
    del st.session_state["prompt_input"]

if user_query:
    # 1. Add user message
    st.session_state["messages"].append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # 2. Retrieve relevant docs via RAGEngine
    filter_choice = None if source_filter == "All Sources" else source_filter
    retrieved_docs = rag_engine.retrieve(user_query, n_results=4, source_filter=filter_choice)

    # 3. Format prompt messages
    history_turns = [{"role": m["role"], "content": m["content"]} for m in st.session_state["messages"][-6:-1]]
    formatted_messages = rag_engine.format_prompt(user_query, retrieved_docs, chat_history=history_turns)

    # 4. Generate response via OpenRouter
    api_key_to_use = st.session_state.get("openrouter_key", os.getenv("OPENROUTER_API_KEY", ""))
    client = OpenRouterClient(api_key=api_key_to_use)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        if api_key_to_use:
            # Stream from OpenRouter LLM
            stream_gen = client.generate_response(
                messages=formatted_messages,
                model=selected_model,
                temperature=0.3,
                max_tokens=1000,
                stream=True
            )
            for chunk in stream_gen:
                full_response += chunk
                response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)
        else:
            # Informative fallback if API key is not yet provided
            synth_response = f"### ⚠️ OpenRouter API Key Not Detected\n\n"
            synth_response += "To enable real-time conversational answers using free models (**Llama 3.3 70B**, **Gemini 2.0 Flash**, or **Qwen 2.5**), please enter your OpenRouter API Key in the left sidebar.\n\n"
            synth_response += "#### 🔍 Relevant Database Records Retrieved for Your Query:\n"
            for idx, doc in enumerate(retrieved_docs):
                synth_response += f"\n**{idx+1}. [{doc['source']}] {doc['title']}** ({doc['city']}, {doc['country']})\n"
                synth_response += f"- **Price / Guide**: {doc['price']}\n"
                synth_response += f"- **Key Details**: {doc['content'][:280]}...\n"
                synth_response += f"- [Official Link]({doc['url']})\n"
            full_response = synth_response
            response_placeholder.markdown(full_response)

        # Show source cards
        if retrieved_docs:
            with st.expander("📚 Verified Real Estate Sources & Property Links", expanded=True):
                for doc in retrieved_docs:
                    st.markdown(f"""
                    <div class="property-card">
                        <h4>{doc['title']}</h4>
                        <span class="property-tag">{doc['source']}</span>
                        <span class="property-tag">{doc['category']}</span>
                        <span class="property-tag">{doc['city']}, {doc['country']}</span>
                        <span class="property-tag">Price: {doc['price']}</span>
                        <p style="font-size:0.85rem; color:#8b949e; margin-top:6px;">{doc['content'][:250]}...</p>
                        <a href="{doc['url']}" target="_blank" class="link-btn">View Official Listing ↗</a>
                    </div>
                    """, unsafe_allow_html=True)

    # Save assistant message
    st.session_state["messages"].append({
        "role": "assistant",
        "content": full_response,
        "retrieved_docs": retrieved_docs
    })

