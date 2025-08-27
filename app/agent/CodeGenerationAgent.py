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
        
        Follow best practices:
        - Clean architecture principles
        - Error handling
        - Input validation
        - Documentation
        - Type hints/annotations
        
        Return as JSON object with filename as key and code as value.
        """)
    
    async def generate_code(self, state: WorkflowState, framework: str = "FastAPI") -> WorkflowState:
        try:
            chain = self.prompt | self.llm
            
            response = await chain.ainvoke({
                "swagger_content": json.dumps(state["swagger_content"], indent=2),
                "user_stories": json.dumps(state["user_stories"], indent=2),
                "framework": framework
            })
            
            code_files = safe_json_loads(response.content)
            state["generated_code"] = code_files
            state["current_step"] = "test_generation"
            return state
        except Exception as e:
            state["errors"].append(f"Code generation failed: {str(e)}")
            return state
    
    def create_zip_from_generated_code(self, code_files: Dict[str, str], output_path: str = None) -> str:
        """
        Create a ZIP file from the generated code files.
        
        Args:
            code_files: Dictionary with filename as key and code content as value
            output_path: Optional path for the output ZIP file
            
        Returns:
            Path to the created ZIP file
        """
        if output_path is None:
            output_path = "generated_code.zip"
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename, content in code_files.items():
                # Ensure proper file extension if not provided
                if not Path(filename).suffix and self._guess_file_extension(content):
                    filename += self._guess_file_extension(content)
                
                zipf.writestr(filename, content)
        
        return output_path
    
    def _guess_file_extension(self, content: str) -> str:
        """Guess file extension based on content."""
        content_lower = content.lower()
        
        if 'from fastapi' in content_lower or 'import fastapi' in content_lower:
            return '.py'
        elif 'from flask' in content_lower or 'import flask' in content_lower:
            return '.py'
        elif 'from django' in content_lower or 'import django' in content_lower:
            return '.py'
        elif 'class ' in content_lower and 'def ' in content_lower:
            return '.py'
        elif 'function ' in content_lower or 'const ' in content_lower or 'let ' in content_lower:
            return '.js'
        elif 'public class' in content_lower or 'import java' in content_lower:
            return '.java'
        elif '<?xml' in content_lower or '<project>' in content_lower:
            return '.xml'
        elif content_lower.strip().startswith('{') and content_lower.strip().endswith('}'):
            return '.json'
        elif 'version:' in content_lower or 'dependencies:' in content_lower:
            return '.yml'
        else:
            return '.txt'
    
    async def generate_and_download_code(self, state: WorkflowState, framework: str = "FastAPI", 
                                       output_path: str = None) -> tuple[WorkflowState, str]:
        """
        Generate code and create a downloadable ZIP file.
        
        Returns:
            Tuple of (updated_state, zip_file_path)
        """
        # First generate the code
        updated_state = await self.generate_code(state, framework)
        
        if updated_state["errors"]:
            return updated_state, None
        
        # Create ZIP file from generated code
        zip_path = self.create_zip_from_generated_code(
            updated_state["generated_code"], 
            output_path
        )
        
        return updated_state, zip_path

# Utility function to create a complete workflow with ZIP download
async def generate_code_and_create_zip(swagger_content: dict, user_stories: list, 
                                     llm, framework: str = "FastAPI", 
                                     output_dir: str = "./output") -> str:
    """
    Complete workflow to generate code and create a ZIP file.
    
    Args:
        swagger_content: Swagger/OpenAPI specification
        user_stories: List of user stories
        llm: Language model instance
        framework: Target framework (default: FastAPI)
        output_dir: Directory to save the ZIP file
        
    Returns:
        Path to the created ZIP file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize the agent
    agent = CodeGeneratorAgent(llm)
    
    # Create initial state
    initial_state = {
        "swagger_content": swagger_content,
        "user_stories": user_stories,
        "generated_code": {},
        "errors": [],
        "current_step": "code_generation"
    }
    
    # Generate code and create ZIP
    output_path = os.path.join(output_dir, f"generated_{framework.lower()}_code.zip")
    final_state, zip_path = await agent.generate_and_download_code(
        initial_state, framework, output_path
    )
    
    if final_state["errors"]:
        print("Errors occurred during code generation:")
        for error in final_state["errors"]:
            print(f"- {error}")
        return None
    
    print(f"Code generated successfully! ZIP file created at: {zip_path}")
    print(f"Generated {len(final_state['generated_code'])} files:")
    for filename in final_state['generated_code'].keys():
        print(f"- {filename}")
    
    return zip_path

# Example usage
if __name__ == "__main__":
    import asyncio
    
    # Example data (replace with your actual data)
    example_swagger = {
        "openapi": "3.0.0",
        "info": {"title": "Example API", "version": "1.0.0"},
        "paths": {
            "/users": {
                "get": {
                    "summary": "Get all users",
                    "responses": {"200": {"description": "Success"}}
                }
            }
        }
    }
    
    example_user_stories = [
        "As a user, I want to view all users",
        "As an admin, I want to create new users"
    ]
    
    async def main():
        # You'll need to provide your LLM instance here
        # llm = your_llm_instance
        
        # zip_path = await generate_code_and_create_zip(
        #     example_swagger, 
        #     example_user_stories, 
        #     llm,
        #     framework="FastAPI"
        # )
        print("Example setup complete. Provide your LLM instance to run.")
    
    asyncio.run(main())