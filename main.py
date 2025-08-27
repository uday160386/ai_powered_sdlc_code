
import streamlit as st
import json
import yaml
from typing import Dict, List, Any, TypedDict
from dataclasses import dataclass
from enum import Enum
import asyncio
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import tempfile
import zipfile
import io
import re
import os
from dotenv import load_dotenv
# Local agent imports
from app.agent.SwaggerAnalyzerAgent import SwaggerAnalyzerAgent
from app.agent.UserStoryGenerationAgent import UserStoryAgent
from app.agent.CodeGenerationAgent import CodeGeneratorAgent
from app.agent.UnitTestcaseGenerationAgent import TestGeneratorAgent

# State Management
class WorkflowState(TypedDict):
    swagger_content: Dict[str, Any]
    user_stories: List[Dict[str, Any]]
    generated_code: Dict[str, str]
    unit_tests: Dict[str, str]
    current_step: str
    errors: List[str]
    metadata: Dict[str, Any]

class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class AgentResult:
    success: bool
    data: Any
    message: str
    step: str
    


# LangGraph Workflow Definition
class AgenticWorkflow:
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            api_key=api_key,
            model="gpt-4-turbo-preview",
            temperature=0.3
        )
        
        self.swagger_agent = SwaggerAnalyzerAgent(self.llm)
        self.story_agent = UserStoryAgent(self.llm)
        self.code_agent = CodeGeneratorAgent(self.llm)
        self.test_agent = TestGeneratorAgent(self.llm)
        
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        # Create the state graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("analyze_swagger", self.swagger_agent.analyze)
        workflow.add_node("generate_stories", self.story_agent.analyze)
        workflow.add_node("generate_code", self.code_agent.generate_code)
        workflow.add_node("generate_tests", self.test_agent.generate_tests)
        
        # Define the workflow edges
        workflow.add_edge("analyze_swagger", "generate_stories")
        workflow.add_edge("generate_stories", "generate_code")
        workflow.add_edge("generate_code", "generate_tests")
        workflow.add_edge("generate_tests", END)
        
        # Set entry point
        workflow.set_entry_point("analyze_swagger")
        
        return workflow.compile()
    
    async def run_workflow(self, swagger_content: Dict[str, Any]) -> WorkflowState:
        initial_state: WorkflowState = {
            "swagger_content": swagger_content,
            "user_stories": [],
            "generated_code": {},
            "unit_tests": {},
            "current_step": "analyze_swagger",
            "errors": [],
            "metadata": {}
        }
        
        result = await self.workflow.ainvoke(initial_state)
        return result


# Streamlit UI
def main():
    st.set_page_config(
        page_title="SDLC AI Workflow",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 AI Powered SDLC workflow")
    # st.subtitle("Automated User Stories, Code & Test Generation from Swagger/OpenAPI")
    
    # Sidebar configuration
    st.sidebar.header("Configuration")
    
    # # API Key input
    # api_key = st.sidebar.text_input(
    #     "OpenAI API Key",
    #     type="password",
    #     help="Enter your OpenAI API key to use the AI agents"
    # )
    
    # if not api_key:
    #     st.warning("Please enter your OpenAI API key in the sidebar to continue.")
    #     return
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY", None)
    # Framework selection
    framework = st.sidebar.selectbox(
        "Code Framework",
        ["FastAPI", "Flask", "Django", "Express.js", "Spring Boot"]
    )
    
    test_framework = st.sidebar.selectbox(
        "Test Framework",
        ["pytest", "unittest", "Jest", "JUnit", "Mocha"]
    )
    
    # Initialize session state
    if 'workflow_results' not in st.session_state:
        st.session_state.workflow_results = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    
    # File upload
    # st.header("📁 Upload Swagger/OpenAPI File")
    uploaded_file = st.file_uploader(
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
            
            st.success(f"✅ Successfully loaded {uploaded_file.name}")
            
            # Display swagger info
            info = swagger_content.get('info', {})
            st.info(f"**API:** {info.get('title', 'Unknown')} v{info.get('version', '1.0')}")
            
            # Process button
            if st.button("🚀 Generate Components", type="primary", disabled=st.session_state.processing):
                st.session_state.processing = True
                
                # Progress indicators
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Initialize workflow
                    workflow = AgenticWorkflow(api_key)
                    
                    # Run the workflow
                    status_text.text("🔍 Analyzing Swagger specification...")
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
        
        # Create tabs for different outputs
        tab1, tab2, tab3, tab4 = st.tabs(["📝 User Stories", "💻 Generated Code", "🧪 Unit Tests", "📁 Download All"])
        print(results)
        with tab1:
            st.subheader("Generated User Stories")
            if results.get("user_stories"):
                for i, story in enumerate(results["user_stories"], 1):
                    with st.expander(f"Story {i}: {story.get('Title', 'Untitled')}"):
                        st.write(f"**Description:** {story.get('user_story', 'Untitled')}")
                        st.write(f"**Priority:** {story.get('priority', 'Medium')}")
                        st.write(f"**Estimated Effort:** {story.get('estimated_effort', '1')}")
                        st.write(f"**Type:** {story.get('type', 'Functional')}")
                        st.write(f"**Acceptance Criteria:** {story.get('acceptance_criteria', 'Untitled')}")
                        
            else:
                st.info("No user stories generated yet.")
        
        with tab2:
            st.subheader("Generated Code")
            if results.get("generated_code"):
                for filename, code in results["generated_code"].items():
                    with st.expander(f"📄 {filename}"):
                        st.code(code, language="python")
            else:
                st.info("No code generated yet.")
        
        with tab3:
            st.subheader("Unit Tests")
            if results.get("unit_tests"):
                for filename, test_code in results["unit_tests"].items():
                    with st.expander(f"🧪 {filename}"):
                        st.code(test_code, language="python")
            else:
                st.info("No tests generated yet.")
        
        with tab4:
            st.subheader("Download All Generated Files")
            
            if results.get("generated_code") or results.get("unit_tests"):
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