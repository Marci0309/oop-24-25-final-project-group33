import streamlit as st
import os
import json
import pandas as pd
import pickle

# Set the page configuration
st.set_page_config(page_title="Deployment", page_icon="🚀")

# Custom CSS for enhanced styling
st.markdown("""
    <style>
    .stFileUploader { font-size: 1rem; }
    .stDataFrame { margin-top: 1rem; }
    .prediction-box {
        font-size: 1.1rem;
        color: #4CAF50;
        font-weight: bold;
        padding: 0.5em;
        border: 1px solid #4CAF50;
        border-radius: 0.5em;
        background-color: #e8f5e9;
        margin-top: 1em;
    }
    .header { font-size: 1.5rem; font-weight: bold; color: #333333; }
    </style>
""", unsafe_allow_html=True)

# Title for the deployment page
st.write("# 🚀 Deployment")
st.write("View and manage your saved machine learning pipelines here.")

# Directory where saved pipeline artifacts are stored
PIPELINES_DIR = os.path.join('assets', 'pipelines')

# Ensure the directory exists
if not os.path.exists(PIPELINES_DIR):
    os.makedirs(PIPELINES_DIR)


# Function to get list of saved pipelines
def get_saved_pipelines() -> list:
    """ Get the list of saved pipelines """
    return [f for f in os.listdir(PIPELINES_DIR) if f.endswith('.json')]


# Load existing pipelines
pipelines = get_saved_pipelines()

# Check if there are any saved pipelines
if pipelines:
    # Create a selectbox to select a pipeline to view
    selected_pipeline_name = st.selectbox(
        "Select a saved pipeline", [os.path.splitext(p)[0] for p in pipelines])

    # Load and display the selected pipeline
    if selected_pipeline_name:
        pipeline_path = os.path.join(
            PIPELINES_DIR, selected_pipeline_name + '.json')
        try:
            # Load the pipeline details from the JSON file
            with open(pipeline_path, 'r') as f:
                pipeline_data = json.load(f)
            # Display pipeline details with safe key access
            st.subheader("Pipeline Summary")
            st.markdown(f"<div class='header'>Pipeline:\
{selected_pipeline_name}</div>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Model Type:** \
{pipeline_data.get('model_type', 'N/A')}")
                st.write(f"**Target Feature:** \
{pipeline_data.get('target_feature', 'N/A')}")
                st.write(f"**Split Ratio:** \
{pipeline_data.get('split', 'N/A')}")
            with col2:
                st.write(f"**Model Name:** \
{pipeline_data.get('model_name', 'N/A')}")
                st.write(f"**Input Features:** \
{', '.join(pipeline_data.get('input_features', []))}")
            st.write("**Metrics:**")
            for metric, values in pipeline_data.get('metrics', {}).items():
                st.write(f"- {metric}: Train:\
{values.get('train', 'N/A')}, Test: {values.get('test', 'N/A')}")
            # Model file path
            model_file_path = os.path.join(PIPELINES_DIR, f"\
{selected_pipeline_name}_model.pkl")

            # Load the model
            if os.path.exists(model_file_path):
                with open(model_file_path, 'rb') as model_file:
                    model = pickle.load(model_file)
                # Section: Upload CSV for Predictions
                st.subheader("Upload CSV for Predictions")
                uploaded_file = st.file_uploader(
                    "Choose a CSV file for predictions", type=["csv"])
                if uploaded_file is not None:
                    input_data = pd.read_csv(uploaded_file)
                    st.write("Preview of uploaded data:")
                    st.dataframe(input_data.head())

                    # Check if the uploaded data contains the required input
                    missing_features = [
                        f for f in pipeline_data.get('input_features', [])
                        if f not in input_data.columns
                    ]
                    if missing_features:
                        st.error(f"The uploaded CSV is missing \
the following required features: {', '.join(missing_features)}")
                    else:
                        # Perform predictions
                        predictions = model.predict(
                            input_data[pipeline_data['input_features']])
                        # Display predictions in a styled box
                        st.markdown(
                            "<div class='prediction-box'>"
                            "Prediction Results:</div>",
                            unsafe_allow_html=True
                        )
                        st.dataframe(predictions, width=700)
            else:
                st.error(f"Model file not found for pipeline\
                          '{selected_pipeline_name}'.")

        except Exception as e:
            st.error(f"Error loading pipeline '{selected_pipeline_name}': {e}")
else:
    st.write(
        "No saved pipelines available. "
        "Please create a pipeline to view it here."
    )
