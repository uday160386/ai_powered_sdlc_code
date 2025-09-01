import json
from langchain.prompts import ChatPromptTemplate

from app.workflow.langgraph_agentic_workflow import WorkflowState
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
        
        Format your response as structured JSON.
        """)
    
    
    async def analyze(self, state: WorkflowState) -> WorkflowState:
        try:
            chain = self.prompt | self.llm
            response = await chain.ainvoke({
                "swagger_content": json.dumps(state["swagger_content"], indent=2)
            })
            analysis = safe_json_loads(response.content)
            state["metadata"] = analysis
            state["current_step"] = "user_stories"
            return state
        except Exception as e:
            state["errors"].append(f"Swagger analysis failed: {str(e)}")
            return state
