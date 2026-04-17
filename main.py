import streamlit as st
import json
import asyncio

from google.genai import types

from functions.ux import run_personas, get_ux_lead_analysis

personas = {}
with open('input/personas.json', 'r') as f:
    personas = json.load(f)

# --- Page Config ---
st.set_page_config(page_title="Vision Sync", layout="centered")

# Initialize Session State for Navigation
if "step" not in st.session_state:
    st.session_state.step = 1
if "run_active" not in st.session_state:
    st.session_state.run_active = False

# --- UI Layout ---
st.title("Vision Sync")

# Screen 1: Video Selection
if st.session_state.step == 1:
    st.write("### Upload Workflow Video")
    video_file = st.file_uploader("Select the file location of the video clip", type=["mp4", "mov", "avi", "mkv"])

    if video_file is not None:
        st.video(video_file)
        st.success(f"Loaded: {video_file.name}")
        video_bytes = video_file.getvalue()
        st.session_state.video_part = types.Part(
            inline_data = types.Blob(
                mime_type = 'video/mp4',
                data=video_bytes
            )
        )

        if st.button("Next"):
            st.session_state.step = 2
            st.rerun()

    else:
        st.info("Please upload a video to proceed")

# Screen 2: UX Analysis
if st.session_state.step == 2:
    st.write("### UX Analysis")

    # Section 1: Options Selection
    st.write("Select Personas to Simulate")
    selected_options = []
    col1, col2, col3 = st.columns(3)

    i = 1
    for persona in personas:
        if i%3 == 0:
            with col3:
                if st.checkbox(persona):
                    selected_options.append(persona)
        elif i%2 == 0:
            with col2:
                if st.checkbox(persona):
                    selected_options.append(persona)
        else:
            with col1:
                if st.checkbox(persona):
                    selected_options.append(persona)
        
        i += 1

    run_pressed = st.button("Run")

    # Use session state to keep the window open after the button is pressed
    if "run_active" not in st.session_state:
        st.session_state.run_active = False

    if run_pressed:
        if not selected_options:
            st.warning("Please select at least one option.")
            st.session_state.run_active = False
        else:
            st.session_state.run_active = True
            st.session_state.last_selected = selected_options
            st.session_state.ux_results = None

    # Section 2: Output Window
    if st.session_state.run_active:
        ux_state = asyncio.run(
            run_personas(st.session_state.last_selected, st.session_state.video_part, app_name='VisionSync', user_id='User')
        )
        st.info("Conducted surveys..")
        ux_results = asyncio.run(
            get_ux_lead_analysis(ux_state, st.session_state.video_part, app_name='VisionSync', user_id='User')
        )
        print(ux_results)
        st.session_state.ux_results = ux_results
        st.markdown("---")
        # Custom CSS for the "small window" look
        st.write("### Agent Critique Window")
        st.session_state.run_active = False
        
    if "ux_results" in st.session_state:
        with st.container(border=True):
            # Dropdown at the top of the window
            option_to_display = st.selectbox(
                "Select Persona to View:", 
                options=st.session_state.ux_results.keys()
            )
            
            # Display the markdown content
            st.markdown(st.session_state.ux_results[option_to_display])