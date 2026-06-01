import streamlit as st
import subprocess
import os
import pandas as pd
import gzip
import json

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="VPCThreatLens - AI SOC Analyst",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# CSS TO HIDE BRANDING & IMPROVE UI
# -----------------------------
hide_st_style = """
            <style>
            /* Targeted hide for the Deploy button div */
            div.stAppDeployButton {
                display: none !important;
            }
            
            /* Hide the Streamlit "three dots" menu, footer, and deploy button */
            #MainMenu {visibility: hidden !important;}
            footer {visibility: hidden !important;}
            .stDeployButton {display:none !important;}
            
            /* Aggressive hide for the entire status/deploy area in header */
            [data-testid="stStatusWidget"] {
                display: none !important;
            }
            
            /* Ensure the sidebar toggle (hamburger) is visible on mobile */
            header[data-testid="stHeader"] {
                background: transparent !important;
            }
            
            /* Optional: Adjust padding to move content up since we removed branding */
            .block-container {
                padding-top: 1rem;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# -----------------------------
# SESSION STATE FOR QUERY
# -----------------------------
if 'main_query_input' not in st.session_state:
    st.session_state.main_query_input = ""

def set_query(q):
    st.session_state.main_query_input = q

# -----------------------------
# NAVIGATION
# -----------------------------
st.sidebar.title("🛡️ VPCThreatLens")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigation", ["Main Runtime", "Raw Dataset", "Final Dataset", "Project Architecture", "About"])

st.sidebar.markdown("---")
st.sidebar.markdown("Developed by **V P Joshi**")
st.sidebar.markdown("[vpjoshi.in](https://vpjoshi.in)")
st.sidebar.markdown("[GitHub Repo](https://github.com/Joshi-labs/VPCThreatLens)")

# -----------------------------
# MAIN RUNTIME PAGE
# -----------------------------
if page == "Main Runtime":
    st.title("🛡️ AI SOC Analyst")
    st.markdown("### Natural Language Security Investigation System")
    st.info("VPCThreatLens leverages AI-powered RAG to analyze VPC Flow Logs for disaster and threat analysis.")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Main search area
        query = st.text_input(
            "Enter Investigation Query", 
            placeholder="e.g., show high severity ssh attacks",
            key="main_query_input"
        )
        
        if st.button("Run Investigation", use_container_width=True):
            if query.strip() == "":
                st.warning("Please enter a query")
            else:
                with st.spinner("🔍 Agentic RAG in progress..."):
                    process = subprocess.Popen(
                        [r".\.venv\Scripts\python.exe", "-u", "agentic_query.py"],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        bufsize=1
                    )
                    
                    # Pass the query to stdin
                    process.stdin.write(query + "\n")
                    process.stdin.flush()
                    
                    st.subheader("📊 Analysis Report")
                    report_placeholder = st.empty()
                    log_placeholder = st.empty()
                    
                    full_output = ""
                    analysis_content = ""
                    is_analysis = False
                    
                    # Stream output from the process
                    for line in iter(process.stdout.readline, ""):
                        full_output += line
                        if "========== ANALYSIS ==========" in line:
                            is_analysis = True
                            continue
                        
                        if is_analysis:
                            analysis_content += line
                            report_placeholder.markdown(analysis_content)
                        else:
                            # Show logs in a small area while waiting for analysis
                            log_placeholder.caption(f"Logs: {line.strip()}")
                    
                    process.stdout.close()
                    return_code = process.wait()
                    
                    # Final cleanup
                    log_placeholder.empty()
                    with st.expander("View Execution Logs"):
                        st.code(full_output, language="text")

                if process.returncode != 0:
                    stderr = process.stderr.read()
                    if stderr:
                        with st.expander("Errors", expanded=True):
                            st.code(stderr, language="text")

    with col2:
        st.subheader("Example Queries")
        examples = [
            "show high severity ssh attacks",
            "what happened between 12:10 and 12:20",
            "find suspicious traffic",
            "show rejected activity",
            "find port scanning activity"
        ]
        for ex in examples:
            # Use the callback method but keep the buttons on the main page
            st.button(ex, key=f"btn_{ex}", on_click=set_query, args=(ex,), use_container_width=True)

# -----------------------------
# RAW DATASET PAGE
# -----------------------------
elif page == "Raw Dataset":
    st.title("📂 Raw Dataset")
    st.markdown("VPC Flow Logs in their original `.log.gz` format from AWS S3.")
    
    raw_dir = "data/raw"
    if os.path.exists(raw_dir):
        files = [f for f in os.listdir(raw_dir) if f.endswith(".gz")]
        if files:
            selected_file = st.selectbox("Select a raw log file to preview", files)
            file_path = os.path.join(raw_dir, selected_file)
            
            with gzip.open(file_path, 'rt') as f:
                content = [f.readline() for _ in range(10)]
            
            st.subheader("Preview (First 10 lines)")
            st.code("".join(content), language="text")
            
            with open(file_path, "rb") as f:
                st.download_button(
                    label="Download Raw Log File",
                    data=f,
                    file_name=selected_file,
                    mime="application/gzip"
                )
        else:
            st.warning("No raw log files found in data/raw")
    else:
        st.error("Directory data/raw not found")

# -----------------------------
# FINAL DATASET PAGE
# -----------------------------
elif page == "Final Dataset":
    st.title("📊 Final Dataset")
    st.markdown("Processed and enriched security events ready for AI analysis.")
    
    dataset_path = "data/datasets/events.jsonl"
    if os.path.exists(dataset_path):
        st.subheader("Enriched Security Events")
        
        events = []
        with open(dataset_path, 'r') as f:
            for line in f:
                events.append(json.loads(line))
                if len(events) >= 100: # Limit for UI performance
                    break
        
        df = pd.DataFrame(events)
        st.dataframe(df.head(20), use_container_width=True)
        
        with open(dataset_path, "rb") as f:
            st.download_button(
                label="Download Full Enriched Dataset (JSONL)",
                data=f,
                file_name="events.jsonl",
                mime="application/jsonl"
            )
    else:
        st.error(f"Dataset not found at {dataset_path}")

# -----------------------------
# PROJECT ARCHITECTURE PAGE
# -----------------------------
elif page == "Project Architecture":
    st.title("🏗️ Project Architecture")
    
    # Using Graphviz for a native Streamlit diagram
    st.graphviz_chart('''
    digraph G {
        rankdir=LR;
        node [shape=box, style=filled, color=lightblue];
        A [label="AWS VPC Flow Logs (.log.gz)"];
        B [label="Log Parser"];
        C [label="Security Enrichment"];
        D [label="Threat Detection"];
        E [label="Processed Events (.jsonl)"];
        F [label="Vector Embeddings"];
        G [label="ChromaDB"];
        H [label="Agentic RAG Chain"];
        I [label="AI SOC Analysis"];
        
        A -> B;
        B -> C;
        C -> D;
        D -> E;
        E -> F;
        F -> G;
        G -> H;
        H -> I;
    }
    ''')
    
    st.markdown("""
    ### Key Components:
    1. **Data Ingestion**: Pulls raw VPC flow logs (Gzip compressed).
    2. **Parsing & Enrichment**: Transforms raw logs into structured JSON, enriching them with threat intelligence and severity scores.
    3. **Vector Database**: Uses **ChromaDB** to store event embeddings for fast semantic retrieval.
    4. **Agentic RAG**: A LangChain-powered agent that understands security context and retrieves relevant events to provide deep analysis.
    5. **Disaster Analysis**: Specifically tuned to identify attack patterns like SSH brute force, port scanning, and traffic anomalies.
    """)

# -----------------------------
# ABOUT PAGE
# -----------------------------
elif page == "About":
    st.title("ℹ️ About VPCThreatLens")
    
    st.markdown("""
    ### Purpose & Goals
    Current cloud monitoring solutions like **AWS Athena** and **AWS OpenSearch** are excellent for querying VPC Flow Logs using SQL or DSL. However, they lack a native **AI RAG (Retrieval-Augmented Generation) solution** specifically tailored for **Disaster Analysis** and automated security investigations.

    **VPCThreatLens** fills this gap. It is an open-source project designed to:
    - Provide a natural language interface for security analysts.
    - Automatically identify and group suspicious network patterns.
    - Offer human-readable explanations and recommendations for complex network events.
    - Enable rapid disaster response by pinpointing the root cause of network anomalies.

    ### Why VPCThreatLens?
    - **Open Source**: Built for the community.
    - **No Re-inventing**: Uses standard VPC flow log formats.
    - **AI-First**: Not just a search tool, but an intelligence tool.
    - **Truly Unique**: There is currently nothing else like this in the open-source world that combines VPC logs with local vector stores and agentic RAG for disaster analysis. It is designed to be highly effective and easy to use.

    ### Developer
    Developed with ❤️ by **V P Joshi**.
    
    - **Website**: [vpjoshi.in](https://vpjoshi.in)
    - **GitHub**: [Joshi-labs/VPCThreatLens](https://github.com/Joshi-labs/VPCThreatLens)
    
    *It's not just a tool; it's your AI-powered SOC companion.*
    """)
