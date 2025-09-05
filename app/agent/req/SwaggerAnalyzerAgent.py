import json
from langchain.prompts import ChatPromptTemplate

from app.workflow.WorkflowState import WorkflowState
from app.util.safe_text_genneration import safe_json_loads

class SwaggerAnalyzerAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_template("""
    Analyze the following Swagger/OpenAPI specification and extract key information:

    Swagger Content: {swagger_content}

    Please provide:
    1. API overview and purpose
    2. List of endpoints with their methods
    3. Data models and schemas
    4. Authentication requirements
    5. Key business entities identified

    Format your response as strict, valid JSON. Do not include any trailing commas, comments, or unquoted keys. Ensure all braces and brackets are closed. Do not include any text before or after the JSON object.
    """)
    
    
    async def analyze(self, state: WorkflowState) -> WorkflowState:
        try:
            chain = self.prompt | self.llm
            response = chain.invoke({
                "swagger_content": json.dumps(state["swagger_content"])
            })

            raw_content = json.loads(response.content)
           
            state["metadata"] = raw_content
            state["current_step"] = "user_stories"
            return state
        except Exception as e:
            state["errors"].append(f"Swagger analysis failed: {str(e)}")
            return state
