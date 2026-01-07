"""
AltFlex Dashboard.

Streamlit-based visualization dashboard for the AI-powered forensic framework.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os

# =============================================================================
# Configuration
# =============================================================================

API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="AltFlex Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A5F;
        text-align: center;
        margin-bottom: 1rem;
    }
    .risk-critical { background-color: #FF4444; color: white; padding: 0.5rem; border-radius: 5px; }
    .risk-high { background-color: #FF8800; color: white; padding: 0.5rem; border-radius: 5px; }
    .risk-medium { background-color: #FFBB00; color: black; padding: 0.5rem; border-radius: 5px; }
    .risk-low { background-color: #88CC00; color: black; padding: 0.5rem; border-radius: 5px; }
    .risk-safe { background-color: #00CC66; color: white; padding: 0.5rem; border-radius: 5px; }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# Helper Functions
# =============================================================================

def check_api_health():
    """Check if the API is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def analyze_transaction(tx_data: dict):
    """Send transaction for analysis."""
    try:
        response = requests.post(f"{API_BASE_URL}/api/analyze", json=tx_data, timeout=10)
        if response.status_code == 200:
            return response.json()
        return {"error": f"API returned status {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def check_address(address: str):
    """Check if address is known attacker."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/address/check",
            json={"address": address, "include_transactions": True},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return {"error": f"API returned status {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def get_exploits():
    """Get known exploits from database."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/exploits", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def load_sample_data():
    """Load sample transaction data."""
    try:
        return pd.read_csv("data/sample_transactions.csv")
    except:
        return None


def get_risk_color(risk_level: str) -> str:
    """Get color for risk level."""
    colors = {
        "CRITICAL": "#FF4444",
        "HIGH": "#FF8800",
        "MEDIUM": "#FFBB00",
        "LOW": "#88CC00",
        "MINIMAL": "#00CC66",
        "SAFE": "#00CC66"
    }
    return colors.get(risk_level, "#888888")


# =============================================================================
# Sidebar Navigation & Session State
# =============================================================================

# Initialize session state for page navigation if not present
if "page" not in st.session_state:
    st.session_state.page = "🏠 Home"

def navigate_to(page):
    """Callback to switch pages."""
    st.session_state.page = page

st.sidebar.title("🛡️ AltFlex")
st.sidebar.markdown("---")

pages = ["🏠 Home", "🔍 Transaction Analyzer", "📍 Address Checker", "📚 Exploits Database", "📊 Data Explorer"]

# Navigation radio bound directly to session state
st.sidebar.radio(
    "Navigation",
    pages,
    key="page"
)

st.sidebar.markdown("---")

# API Status in sidebar
health = check_api_health()
if health:
    st.sidebar.success("✅ API Connected")
    with st.sidebar.expander("Component Status"):
        for component, status in health.get("components", {}).items():
            icon = "✅" if status else "❌"
            st.write(f"{icon} {component}")
else:
    st.sidebar.error("❌ API Offline")
    st.sidebar.caption("Start API with: `uvicorn src.app.main:app --reload`")


# =============================================================================
# Page: Home
# =============================================================================

if st.session_state.page == "🏠 Home":
    st.markdown("<h1 class='main-header'>🛡️ AltFlex Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #666;'>AI-Powered Forensic Framework for DeFi Exploit Detection</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Load exploits for metrics
    exploits_data = get_exploits()
    sample_df = load_sample_data()
    
    with col1:
        st.metric(
            "Known Exploits",
            exploits_data["total"] if exploits_data else "N/A",
            help="Total exploits in database"
        )
    
    with col2:
        total_loss = sum(e.get("loss_usd", 0) for e in exploits_data.get("exploits", [])) if exploits_data else 0
        st.metric(
            "Total Losses Tracked",
            f"${total_loss/1e6:.0f}M" if total_loss > 0 else "N/A",
            help="Combined losses from tracked exploits"
        )
    
    with col3:
        malicious_count = len(sample_df[sample_df['is_malicious'] == True]) if sample_df is not None else 0
        st.metric(
            "Malicious Samples",
            malicious_count if sample_df is not None else "N/A",
            help="Labeled malicious transactions in sample data"
        )
    
    with col4:
        st.metric(
            "Detection Rules",
            "6",
            help="Active rule-based detection checks"
        )
    
    st.markdown("---")
    
    # Quick Actions
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**🔍 Analyze Transaction**\n\nCheck a single transaction for exploit patterns.")
        st.button("Go to Analyzer →", on_click=navigate_to, args=("🔍 Transaction Analyzer",))
    
    with col2:
        st.warning("**📍 Check Address**\n\nVerify if an address is a known attacker.")
        st.button("Go to Address Checker →", on_click=navigate_to, args=("📍 Address Checker",))
    
    with col3:
        st.error("**📚 Exploits Database**\n\nBrowse known flash loan attacks.")
        st.button("View Database →", on_click=navigate_to, args=("📚 Exploits Database",))
    
    # About section
    st.markdown("---")
    with st.expander("ℹ️ About AltFlex"):
        st.markdown("""
        **AltFlex** is an integrated AI and digital forensics framework designed to detect and analyze 
        security exploits in cross-chain bridges and DeFi protocols.
        
        **Key Features:**
        - 🤖 ML-based anomaly detection using XGBoost
        - 🔍 Rule-based exploit signature matching
        - 📊 Known attacker address database
        - 📈 Real-time risk scoring
        
        **Technology Stack:**
        - FastAPI (Backend API)
        - Streamlit (Dashboard)
        - XGBoost (Machine Learning)
        - Python (Core Logic)
        """)


# =============================================================================
# Page: Transaction Analyzer
# =============================================================================

elif st.session_state.page == "🔍 Transaction Analyzer":
    st.title("🔍 Transaction Analyzer")
    st.markdown("Analyze individual transactions for potential exploit patterns.")
    
    tab1, tab2 = st.tabs(["Manual Input", "From Sample Data"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            from_address = st.text_input("From Address", placeholder="0x...")
            value_eth = st.number_input("Value (ETH)", min_value=0.0, value=1.0, step=0.1)
            gas_used = st.number_input("Gas Used", min_value=0, value=200000, step=10000)
        
        with col2:
            to_address = st.text_input("To Address", placeholder="0x...")
            gas_price = st.number_input("Gas Price (Gwei)", min_value=0.0, value=30.0, step=5.0)
            is_flash_loan = st.checkbox("Flash Loan Transaction")
        
        if st.button("🔍 Analyze Transaction", type="primary"):
            if not health:
                st.error("API is offline. Please start the API server.")
            elif from_address and to_address:
                with st.spinner("Analyzing transaction..."):
                    result = analyze_transaction({
                        "from_address": from_address,
                        "to_address": to_address,
                        "value_eth": value_eth,
                        "gas_used": gas_used,
                        "gas_price_gwei": gas_price,
                        "is_flash_loan": is_flash_loan
                    })
                
                if "error" in result:
                    st.error(f"Analysis failed: {result['error']}")
                else:
                    # Display results
                    st.markdown("---")
                    st.subheader("Analysis Results")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        risk_color = get_risk_color(result.get("risk_level", "SAFE"))
                        st.metric("Risk Level", result.get("risk_level", "N/A"))
                    
                    with col2:
                        st.metric("Risk Score", f"{result.get('risk_score', 0):.2%}")
                    
                    with col3:
                        st.metric("Rules Triggered", f"{len(result.get('triggered_rules', []))}/{result.get('all_rules_checked', 0)}")
                    
                    if result.get("is_suspicious"):
                        st.error("⚠️ This transaction is SUSPICIOUS!")
                    else:
                        st.success("✅ No immediate threats detected")
                    
                    # Triggered rules
                    if result.get("triggered_rules"):
                        st.subheader("Triggered Detection Rules")
                        for rule in result["triggered_rules"]:
                            with st.expander(f"🚨 {rule['rule_name']} ({rule['severity']})"):
                                st.write(f"**Details:** {rule['details']}")
                                st.write(f"**Confidence:** {rule['confidence']:.2%}")
                                if rule.get("indicators"):
                                    st.write("**Indicators:**")
                                    for ind in rule["indicators"]:
                                        st.write(f"  - {ind}")
            else:
                st.warning("Please enter both from and to addresses.")
    
    with tab2:
        sample_df = load_sample_data()
        if sample_df is not None:
            st.write(f"Loaded {len(sample_df)} sample transactions")
            
            # Select a transaction
            tx_idx = st.selectbox(
                "Select a transaction to analyze",
                options=range(len(sample_df)),
                format_func=lambda x: f"TX {x}: {sample_df.iloc[x]['label']} - {sample_df.iloc[x]['value_eth']:.2f} ETH"
            )
            
            if st.button("🔍 Analyze Selected Transaction"):
                tx = sample_df.iloc[tx_idx]
                with st.spinner("Analyzing..."):
                    result = analyze_transaction({
                        "tx_hash": tx.get("tx_hash", ""),
                        "from_address": tx["from_address"],
                        "to_address": tx["to_address"],
                        "value_eth": float(tx["value_eth"]),
                        "gas_used": int(tx["gas_used"]),
                        "gas_price_gwei": float(tx["gas_price_gwei"]),
                        "is_flash_loan": bool(tx.get("is_flash_loan", False))
                    })
                
                if "error" not in result:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Risk Level", result.get("risk_level", "N/A"))
                    with col2:
                        st.metric("Actual Label", tx.get("label", "unknown"))
        else:
            st.warning("Sample data not found. Ensure `data/sample_transactions.csv` exists.")


# =============================================================================
# Page: Address Checker
# =============================================================================

elif st.session_state.page == "📍 Address Checker":
    st.title("📍 Address Checker")
    st.markdown("Check if an Ethereum address is associated with known exploits.")
    
    # Known attacker examples
    st.info("💡 **Try these known attacker addresses:**\n"
            "- Euler: `0xb66cd966670d962C227B3EABA30a872DbFb995db`\n"
            "- bZx: `0x148426fDc4C8A51b96B4bed82A0ed5551d71dD3a`\n"
            "- Cream: `0x24354D31bC9D90F62FE5f2454709C32049cf866b`")
    
    address = st.text_input("Enter Ethereum Address", placeholder="0x...")
    
    if st.button("🔍 Check Address", type="primary"):
        if not health:
            st.error("API is offline. Please start the API server.")
        elif address:
            with st.spinner("Checking address..."):
                result = check_address(address)
            
            if "error" in result:
                st.error(f"Check failed: {result['error']}")
            else:
                st.markdown("---")
                
                if result.get("is_known_attacker"):
                    st.error(f"🚨 **WARNING: KNOWN ATTACKER!**")
                    st.write(result.get("message", ""))
                    
                    if result.get("exploit_info"):
                        exp = result["exploit_info"]
                        st.subheader("Exploit Details")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Name:** {exp.get('name', 'N/A')}")
                            st.write(f"**Date:** {exp.get('date', 'N/A')}")
                            st.write(f"**Protocol:** {exp.get('protocol', 'N/A')}")
                        with col2:
                            st.write(f"**Chain:** {exp.get('chain', 'N/A')}")
                            st.write(f"**Loss:** ${exp.get('loss_usd', 0):,}")
                            st.write(f"**Type:** {exp.get('attack_type', 'N/A')}")
                else:
                    st.success("✅ Address NOT found in known attacker database")
                    st.caption("Note: This doesn't guarantee the address is safe, only that it's not in our database.")
        else:
            st.warning("Please enter an address to check.")


# =============================================================================
# Page: Exploits Database
# =============================================================================

elif st.session_state.page == "📚 Exploits Database":
    st.title("📚 Known Exploits Database")
    st.markdown("Browse documented flash loan attacks and exploit patterns.")
    
    exploits_data = get_exploits()
    
    if exploits_data:
        st.metric("Total Exploits", exploits_data["total"])
        
        st.markdown("---")
        
        for exploit in exploits_data.get("exploits", []):
            with st.expander(f"**{exploit['name']}** - ${exploit['loss_usd']:,} loss"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Date:** {exploit['date']}")
                    st.write(f"**Chain:** {exploit['chain'].upper()}")
                    st.write(f"**Protocol:** {exploit['protocol']}")
                
                with col2:
                    st.write(f"**Attack Type:** {exploit['attack_type']}")
                    st.write(f"**Loss:** ${exploit['loss_usd']:,}")
                
                st.write(f"**Attack Vector:** {exploit['attack_vector']}")
                
                st.write("**Attacker Addresses:**")
                for addr in exploit.get("attacker_addresses", []):
                    st.code(addr)
    else:
        st.warning("Could not load exploits database. Ensure API is running.")
        
        # Show from local file if API offline
        try:
            with open("data/flash_loan_exploits.json", "r") as f:
                local_data = json.load(f)
            st.info("Showing data from local file:")
            for exploit in local_data.get("known_exploits", []):
                st.write(f"**{exploit['name']}** - ${exploit['loss_usd']:,}")
        except:
            pass


# =============================================================================
# Page: Data Explorer
# =============================================================================

elif st.session_state.page == "📊 Data Explorer":
    st.title("📊 Data Explorer")
    st.markdown("Explore the sample transaction dataset.")
    
    sample_df = load_sample_data()
    
    if sample_df is not None:
        st.subheader("Dataset Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Transactions", len(sample_df))
        with col2:
            st.metric("Malicious", len(sample_df[sample_df['is_malicious'] == True]))
        with col3:
            st.metric("Flash Loans", len(sample_df[sample_df['is_flash_loan'] == True]))
        with col4:
            st.metric("Total Value", f"{sample_df['value_eth'].sum():,.0f} ETH")
        
        st.markdown("---")
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Transaction Labels")
            label_counts = sample_df['label'].value_counts()
            fig = px.pie(
                values=label_counts.values,
                names=label_counts.index,
                title="Transaction Distribution by Label",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Value Distribution")
            fig = px.histogram(
                sample_df,
                x="value_eth",
                color="is_malicious",
                nbins=30,
                title="Transaction Value Distribution",
                labels={"value_eth": "Value (ETH)", "is_malicious": "Malicious"}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Gas analysis
        st.subheader("Gas Usage Analysis")
        fig = px.scatter(
            sample_df,
            x="gas_used",
            y="gas_price_gwei",
            color="label",
            size="value_eth",
            title="Gas Usage vs Gas Price",
            labels={"gas_used": "Gas Used", "gas_price_gwei": "Gas Price (Gwei)"}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Raw data
        with st.expander("View Raw Data"):
            st.dataframe(sample_df, use_container_width=True)
    else:
        st.warning("Sample data not found. Ensure `data/sample_transactions.csv` exists.")


# =============================================================================
# Footer
# =============================================================================

st.markdown("---")
st.caption("AltFlex v1.0.0 | AI-Powered Forensic Framework for DeFi Exploit Detection")
