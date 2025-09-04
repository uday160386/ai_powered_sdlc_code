# Standard imports
import os
import io
import json
import yaml
import zipfile
import asyncio


from app.workflow.AgenticWorkflow import AgenticWorkflow

# Third-party imports
import streamlit as st
from dotenv import load_dotenv

# Streamlit UI
def main():
    st.set_page_config(
        page_title="SDLC AI Workflow",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 SToP")
    st.subheader("AI Powered, production-ready code generator")
    
    # Sidebar configuration
    st.sidebar.header("Configuration")

    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY", None)
    
    # user story selection option
    user_story_selection = st.sidebar.selectbox(
        "User Story Generation",
        ["Yes",  "No"]
    )
    
    # Framework selection
    framework = st.sidebar.selectbox(
        "Code Framework",
        ["FastAPI", "Flask", "Django", "Express.js", "Spring Boot", "No Selection"]
    )
    test_framework = st.sidebar.selectbox(
        "Test Framework",
        ["pytest", "unittest", "Jest", "JUnit", "Mocha", "No Selection"]
    )
    
    cloud_option = st.sidebar.selectbox(
        "Public Cloud",
        ["AWS", "Azure", "No Selection"]
    )
   
    
    # Initialize session state
    if 'workflow_results' not in st.session_state:
        st.session_state.workflow_results = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    
    # File upload
    # st.header("📁 Upload Swagger/OpenAPI File")
    uploaded_file = st.sidebar.file_uploader(
        "Choose a Swagger/OpenAPI file",
        type=['json', 'yaml', 'yml'],
        help="Upload your Swagger/OpenAPI specification file"
    )
    
    if uploaded_file is not None:
        try:
            # Parse the uploaded file
            if uploaded_file.name.endswith('.json'):
                swagger_content = json.loads(uploaded_file.read())
            else:
                swagger_content = yaml.safe_load(uploaded_file.read())

            import time
            success_msg = st.sidebar.empty()
            success_msg.success(f"✅ Successfully loaded {uploaded_file.name}")
       
            success_msg.empty()


            # Process button
            if st.sidebar.button("🚀 Generate Components", type="primary", disabled=st.session_state.processing):
                st.session_state.processing = True
                
                # Progress indicators
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Initialize workflow with framework
                    workflow = AgenticWorkflow(api_key, framework, test_framework, cloud_option)
                    # Run the workflow
                    status_text.text("🔍 Artifacts generation in progress...")
                    progress_bar.progress(25)
                    # Since we can't use asyncio in Streamlit directly, we'll simulate the workflow
                    # In a real implementation, you'd use asyncio.run() or similar
                    result = asyncio.run(workflow.run_workflow(swagger_content))
                    progress_bar.progress(100)
                    status_text.text("✅ Workflow completed successfully!")
                    st.session_state.workflow_results = result
                except Exception as e:
                    st.error(f"❌ Workflow failed: {str(e)}")
                finally:
                    st.session_state.processing = False
        
        except Exception as e:
            st.error(f"❌ Failed to parse file: {str(e)}")
    

    # Display results
    if st.session_state.workflow_results:
        results = st.session_state.workflow_results
        st.header("📊 Workflow Results")
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📝 User Stories", "💻 Generated Code", "🧪 Unit Tests", "Container Code","Setup guide", "📁 Download All"])

        with tab1:
            st.subheader("Generated User Stories")
            if results.get("user_stories"):
                for i, story in enumerate(results["user_stories"], 1):
                    with st.expander(f"Story {i}: {story.get('title', 'Untitled')}"):
                        st.write(f"**Description:** {story.get('user_story', 'Untitled')}")
                        st.write(f"**Acceptance Criteria:** {story.get('acceptance_criteria', 'Untitled')}")
                        st.write(f"**Priority:** {story.get('priority', 'Medium')}")
                        st.write(f"**Estimated Effort:** {story.get('estimated_effort', '1')}")
                        st.write(f"**Type:** {story.get('type', 'Functional')}")
                        st.write(f"**Edge Cases:** {story.get('edge_cases', '')}")
                        st.write(f"**More Details:** {story.get('reference', '')}")
                                 
            else:
                st.info("No user stories generated yet.")
        
        with tab2:
            st.subheader("Generated Code")
            if results.get("generated_code"):
                for filename, code in results["generated_code"].items():
                    with st.expander(f"📄 {filename}"):
                        st.code(code)
            else:
                st.info("No code generated yet.")
        
        with tab3:
            st.subheader("Unit Tests")
            if results.get("unit_tests"):
                for filename, test_code in results["unit_tests"].items():
                    with st.expander(f"🧪 {filename}"):
                        st.code(test_code)
            else:
                st.info("No tests generated yet.")
        with tab4:
            st.subheader("Container Code")
            if results.get("generated_container_code"):
                for filename, test_code in results["generated_container_code"].items():
                    with st.expander(f"🧪 {filename}"):
                        st.code(test_code)
            else:
                st.info("No container code generated yet.")
        with tab5:
            st.subheader("SetUp Instructions")
            if results.get("generated_readme_code"):
                for generated_readme in results["generated_readme_code"].items():
                    with st.expander(f"🧪 Setup Instructions to follow"):
                        st.code(generated_readme)
            else:
                st.info("No Readme file generated yet.")        
        with tab6:
            st.subheader("Download All Generated Files")
            
            if results.get("generated_code") or results.get("unit_tests") or results.get("generated_container_code"):
                # Create a zip file with all generated content
                zip_buffer = io.BytesIO()
                
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    # Add user stories
                    if results.get("user_stories"):
                        stories_content = json.dumps(results["user_stories"], indent=2)
                        zip_file.writestr("user_stories.json", stories_content)
                    
                    # Add generated code
                    if results.get("generated_code"):
                        for filename, code in results["generated_code"].items():
                            zip_file.writestr(f"src/{filename}", code)
                    
                    # Add unit tests
                    if results.get("unit_tests"):
                        for filename, test_code in results["unit_tests"].items():
                            zip_file.writestr(f"tests/{filename}", test_code)
                
                zip_buffer.seek(0)
                
                st.download_button(
                    label="📦 Download Complete Project",
                    data=zip_buffer.getvalue(),
                    file_name="generated_project.zip",
                    mime="application/zip"
                )
            else:
                st.info("No files available for download yet.")
        
        # Error display
        if results.get("errors"):
            st.subheader("⚠️ Errors and Warnings")
            for error in results["errors"]:
                st.error(error)


if __name__ == "__main__":
    main()
    