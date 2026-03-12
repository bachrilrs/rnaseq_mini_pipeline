"""Streamlit dashboard for pipeline visualization."""

import streamlit as st
import pandas as pd
from rnaseq.utils.config import ConfigManager
from rnaseq.db_setup import DatabaseConnection

st.set_page_config(
    page_title="RNA-seq Pipeline Dashboard",
    page_icon="🧬",
    layout="wide"
)

st.title("🧬 RNA-seq Pipeline Dashboard")
st.markdown("---")

# Load configuration
try:
    config_manager = ConfigManager("config.yaml")
    db_config = config_manager.get_database_config()
except Exception as e:
    st.error(f"Failed to load configuration: {e}")
    st.stop()

# Sidebar
with st.sidebar:
    st.header("Navigation")
    page = st.radio("Select Page:", ["Overview", "QC Metrics", "Sample Details", "Runs History"])

# Main content
if page == "Overview":
    st.header("Pipeline Overview")
    
    try:
        db = DatabaseConnection(db_config)
        db.connect()
        
        col1, col2, col3 = st.columns(3)
        
        runs_result = db.execute_query("SELECT COUNT(*) as count FROM runs")
        with col1:
            st.metric("Total Runs", runs_result[0]['count'] if runs_result else 0)
        
        samples_result = db.execute_query("SELECT COUNT(DISTINCT sample_id) as count FROM samples")
        with col2:
            st.metric("Total Samples", samples_result[0]['count'] if samples_result else 0)
        
        metrics_result = db.execute_query("SELECT COUNT(*) as count FROM qc_metrics")
        with col3:
            st.metric("QC Metrics", metrics_result[0]['count'] if metrics_result else 0)
        
        db.close()
        
    except Exception as e:
        st.error(f"Database error: {e}")

elif page == "QC Metrics":
    st.header("Quality Control Metrics")
    
    try:
        db = DatabaseConnection(db_config)
        db.connect()
        
        results = db.execute_query("""
            SELECT 
                s.condition,
                AVG(qm.library_size) as avg_library_size,
                AVG(qm.mean_counts) as avg_mean_counts,
                COUNT(*) as sample_count
            FROM qc_metrics qm
            JOIN samples s ON qm.sample_id = s.sample_id
            GROUP BY s.condition
        """)
        
        if results:
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No data available")
        
        db.close()
        
    except Exception as e:
        st.error(f"Error: {e}")

elif page == "Sample Details":
    st.header("Sample Details")
    
    try:
        db = DatabaseConnection(db_config)
        db.connect()
        
        results = db.execute_query("""
            SELECT 
                s.sample_id,
                s.condition,
                s.replicate,
                qm.library_size,
                qm.mean_counts
            FROM samples s
            LEFT JOIN qc_metrics qm ON s.sample_id = qm.sample_id
            ORDER BY s.condition, s.replicate
        """)
        
        if results:
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No samples found")
        
        db.close()
        
    except Exception as e:
        st.error(f"Error: {e}")

elif page == "Runs History":
    st.header("Pipeline Runs History")
    
    try:
        db = DatabaseConnection(db_config)
        db.connect()
        
        results = db.execute_query("""
            SELECT 
                id,
                version,
                dataset_source,
                timestamp
            FROM runs
            ORDER BY timestamp DESC
        """)
        
        if results:
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No runs found")
        
        db.close()
        
    except Exception as e:
        st.error(f"Error: {e}")

st.markdown("---")
st.markdown("📊 Built with Streamlit | 🧬 RNA-seq Pipeline v1.0.0")