import streamlit as st
import sys
import os

# Align python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.app.config import settings
from src.app.data.repository import RestaurantRepository
from src.app.services.filter_service import FilterService
from src.app.services.orchestrator import RecommendationOrchestrator
from src.app.models.domain import UserPreferences

# Sleek and premium dark page layout config
st.set_page_config(
    page_title="Zomato AI - Gourmet Hub",
    page_icon="🍔",
    layout="wide"
)

# Custom premium styling injections (vibrant accents, dark mode, card hovers, elegant borders)
st.markdown("""
    <style>
    .main { 
        background-color: #0d0f12; 
        color: #e2e8f0; 
    }
    .restaurant-card {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .restaurant-card:hover { 
        transform: translateY(-5px); 
        border-color: #ef4444; 
        box-shadow: 0 8px 30px rgba(239, 68, 68, 0.15);
    }
    .badge-rating { 
        background: linear-gradient(135deg, #22c55e, #15803d); 
        color: white; 
        padding: 4px 10px; 
        border-radius: 6px; 
        font-weight: bold; 
        font-size: 14px;
        box-shadow: 0 2px 5px rgba(34, 197, 94, 0.3);
    }
    .badge-cost { 
        background: linear-gradient(135deg, #3b82f6, #1d4ed8); 
        color: white; 
        padding: 4px 10px; 
        border-radius: 6px; 
        font-weight: bold; 
        font-size: 14px;
        box-shadow: 0 2px 5px rgba(59, 130, 246, 0.3);
    }
    .cuisine-tag {
        background: rgba(51, 65, 85, 0.6);
        color: #cbd5e1;
        padding: 3px 8px;
        border-radius: 6px;
        margin-right: 6px;
        font-size: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .explanation-box { 
        font-style: italic; 
        color: #94a3b8; 
        border-left: 4px solid #ef4444; 
        padding-left: 14px; 
        margin-top: 16px; 
        font-size: 14.5px;
        line-height: 1.6;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_services():
    repo = RestaurantRepository(storage_type="parquet", file_path=settings.DATA_PATH)
    filter_svc = FilterService(repo, settings.MAX_CANDIDATES)
    orch = RecommendationOrchestrator(filter_svc)
    return repo, orch

repo, orchestrator = get_services()

# Persistent state management to prevent recommendations from disappearing on widget interactions
if "recommendations" not in st.session_state:
    st.session_state.recommendations = None

st.title("🎯 Zomato AI Recommendation Hub")
st.markdown("Your custom gourmet matching portal based on real-world eating patterns.")

# Layout search parameters in Sidebar
with st.sidebar:
    st.header("Search Parameters")
    locations = repo.get_unique_locations()
    cuisines = repo.get_unique_cuisines()
    
    # Smart defaults to avoid zero matches on initial load
    default_loc = "Indiranagar"
    default_cuisine = "north indian"
    default_loc_idx = locations.index(default_loc) if default_loc in locations else 0
    default_cuisine_idx = cuisines.index(default_cuisine) if default_cuisine in cuisines else 0
    
    selected_location = st.selectbox("Where to eat?", options=locations, index=default_loc_idx)
    selected_cuisine = st.selectbox(
        "What cuisine?", 
        options=cuisines, 
        index=default_cuisine_idx,
        format_func=lambda x: str(x).title()
    )
    selected_budget = st.radio("Budget Tier", options=["Low", "Medium", "High"], index=1)
    selected_rating = st.slider("Min Rating", 0.0, 5.0, 3.5, 0.1)
    subjective_pref = st.text_area("Subjective mood/preferences", placeholder="e.g. cozy spot for date night with low music")
    top_k = st.number_input("Max recommendations", 1, 10, 5)
    submit = st.button("Generate Suggestions", type="primary", use_container_width=True)

if submit:
    prefs = UserPreferences(
        location=selected_location,
        budget=selected_budget.lower(),
        cuisine=selected_cuisine.lower(),
        min_rating=selected_rating,
        additional_preferences=subjective_pref,
        top_k=top_k
    )
    
    with st.spinner("⚡ Curating options matching your gourmet palette..."):
        res = orchestrator.get_recommendations(prefs)
        st.session_state.recommendations = res

# Persist and render recommendations from session state
if st.session_state.recommendations is not None:
    res = st.session_state.recommendations
    
    if not res.recommendations:
        st.warning("⚠️ No restaurants match these filters.")
    else:
        st.success("Suggestions curated successfully.")
        st.info(res.summary)
        
        for rec in res.recommendations:
            rest = rec.restaurant
            cuisine_tags = " ".join([f"<span class='cuisine-tag'>{str(c).title()}</span>" for c in rest.cuisines])
            
            st.markdown(f"""
                <div class="restaurant-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h3 style="margin:0; color:#ffffff; font-size:20px;">#{rec.rank} - {rest.name}</h3>
                        <div>
                            <span class="badge-rating">⭐ {rest.rating:.1f}</span>
                            <span class="badge-cost">💰 ₹{rest.estimated_cost:.0f}</span>
                        </div>
                    </div>
                    <p style="margin-top:8px; margin-bottom:8px; font-size:14.5px; color:#cbd5e1;">📍 {rest.location}</p>
                    <div style="margin-top:10px; margin-bottom:14px; display:flex; flex-wrap:wrap; gap:4px;">{cuisine_tags}</div>
                    <div class="explanation-box">
                        <strong>AI Recommendation Rationale:</strong><br>
                        "{rec.explanation}"
                    </div>
                </div>
            """, unsafe_allow_html=True)

