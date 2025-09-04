import zipfile
import os
import tempfile
import json
from pathlib import Path
from typing import Dict, Any
from app.util.safe_text_genneration import safe_json_loads
from langchain.prompts import ChatPromptTemplate
from app.workflow.langgraph_agentic_workflow import WorkflowState

class SetUpGuideAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_template("""
    Based on the generated production-ready code , Docker file, helm charts, public cloud code, and test files, create a user friendly readme.md file

    Generated Container Code: {generated_container_code}
    Generated Code: {generated_code}
    Test Framework: {test_framework}
    Swagger Content: {swagger_content}
    Test Framework: {test_framework}
    
    
    Output format:
    For each file, use the following delimiters (do not use markdown or code blocks):
    >>>FILE_PATH_START<<< path/to/file >>>FILE_PATH_END<<<
    >>>FILE_CONTENT_START<<<
    <file content here>
    >>>FILE_CONTENT_END<<<
    Repeat for each file. Do not return JSON. Only return plain text in the above format.
    """)
    
    async def generate_code(self, state: WorkflowState) -> WorkflowState:
        try:
            chain = self.prompt | self.llm
            response = await chain.ainvoke({
                "swagger_content": json.dumps(state["swagger_content"], indent=2),
                "user_stories": json.dumps(state["user_stories"], indent=2),
                "generated_code": json.dumps(state.get("generated_code", {}), indent=2),
                "generated_container_code": json.dumps(state["generated_container_code"], indent=2),
                
            })
            raw_content = response.content.strip()
            # Parse the response using new explicit delimiters
            files = {}
            import re
            pattern = r">>>FILE_PATH_START<<<\s*(.*?)\s*>>>FILE_PATH_END<<<\s*>>>FILE_CONTENT_START<<<\n([\s\S]*?)\n>>>FILE_CONTENT_END<<<"
            matches = re.findall(pattern, raw_content)
            if not matches:
                # Fallback: Try to extract code blocks if delimiters are missing
                fallback_pattern = r"([\w\-/]+\.)[\s\S]*?```([\s\S]*?)```"
                fallback_matches = re.findall(fallback_pattern, raw_content)
                if fallback_matches:
                    for file_path, file_content in fallback_matches:
                        files[file_path.strip()] = file_content.strip()
                    state["generated_readme_code"] = files
                    # Create in-memory ZIP
                    import io, zipfile
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                        for path, content in files.items():
                            zip_file.writestr(path, content)
                    zip_buffer.seek(0)
                    state["generated_zip"] = zip_buffer.read()
                else:
                    state["errors"].append(
                        f"Code generation failed: No files found in LLM response. Raw content:\n{raw_content[:1000]}"
                    )
                    state["generated_readme_code"] = {}
            else:
                for file_path, file_content in matches:
                    files[file_path.strip()] = file_content.strip()
                state["generated_readme_code"] = files
                # Create in-memory ZIP
                import io, zipfile
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for path, content in files.items():
                        zip_file.writestr(path, content)
                zip_buffer.seek(0)
                state["generated_zip"] = zip_buffer.read()

            state["current_step"] = "generated_readme_code"
            return state
        except Exception as e:
            state["errors"].append(f"container code  failed: {str(e)}")
            return state