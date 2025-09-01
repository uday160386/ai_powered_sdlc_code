import zipfile
import os
import tempfile
import json
from pathlib import Path
from typing import Dict, Any
from app.util.safe_text_genneration import safe_json_loads
from langchain.prompts import ChatPromptTemplate
from app.workflow.langgraph_agentic_workflow import WorkflowState

class CodeGeneratorAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_template("""
    Generate production-ready code based on the Swagger specification:
        
    Swagger Content: {swagger_content}
    User Stories: {user_stories}
    Target Framework: {framework}
        
    Generate:
    1. API models/schemas
    2. Service layer classes
    3. Controller/Router implementations
    4. Database models (if applicable)
    5. Configuration files
    6. Folder structure

    Follow best practices:
    - Clean architecture principles
    - Error handling
    - Input validation
    - Documentation
    - Type hints/annotations

    Output format:
    For each file, use the following delimiters:
    <file_path>: <relative/path/to/file.py>
    <file_content>
    ---END FILE---
    Repeat for each file. Do not return JSON. Only return plain text in the above format.
    """)
    
    async def generate_code(self, state: WorkflowState, framework: str = "FastAPI") -> WorkflowState:
        print(framework)
        try:
            chain = self.prompt | self.llm
            response = await chain.ainvoke({
                "swagger_content": json.dumps(state["swagger_content"], indent=2),
                "user_stories": json.dumps(state["user_stories"], indent=2),
                "framework": framework
            })
            raw_content = response.content.strip()
            # Parse the response using delimiters
            files = {}
            import re
            pattern = r"<file_path>:\s*(.*?)\n<file_content>\n([\s\S]*?)(?=---END FILE---)"
            matches = re.findall(pattern, raw_content)
            if not matches:
                state["errors"].append(
                    f"Code generation failed: No files found in LLM response. Raw content:\n{raw_content[:1000]}"
                )
                state["generated_code"] = {}
            else:
                for file_path, file_content in matches:
                    files[file_path.strip()] = file_content.strip()
                state["generated_code"] = files

                # Create in-memory ZIP
                import io, zipfile
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for path, content in files.items():
                        zip_file.writestr(path, content)
                zip_buffer.seek(0)
                state["generated_zip"] = zip_buffer.read()

            state["current_step"] = "test_generation"
            return state
        except Exception as e:
            state["errors"].append(f"Code generation failed: {str(e)}")
            return state