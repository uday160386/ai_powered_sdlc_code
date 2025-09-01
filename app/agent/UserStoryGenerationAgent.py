import json
from typing import Dict, List, Any, Optional
from langchain.prompts import ChatPromptTemplate
from app.util.safe_text_genneration import safe_json_loads


from app.workflow.langgraph_agentic_workflow import WorkflowState


class UserStoryAgent:
    def __init__(self, llm):
        self.llm = llm

        self.prompt = ChatPromptTemplate.from_template("""
        You are an expert API business analyst. Include edge cases and error handling scenarios.
        Based on the Swagger API analysis, generate comprehensive user stories:
        
        API Analysis: {analysis}
        Swagger Paths: {paths}
        
        For each endpoint, create user stories that include:
        1. title
        2. user_story (As a... I want... So that...)
        3. acceptance_criteria (Given/When/Then format)
        4. priority (High/Medium/Low)
        5. estimated_effort (Story points 1-13)
        6. type (functional or non-functional)
        7. edge_cases Create both functional and non-functional stories.
        8. reference provide clear references to the API documentation, request payload and other relevant resources.

        
        Focus on business value and user needs. Consider different user personas.
        Return as a JSON array of user story objects.
        """)
    
    async def generate_stories(self, state: WorkflowState) -> WorkflowState:
        try:
            paths = state["swagger_content"].get("paths", {})
            chain = self.prompt | self.llm
            
            response = await chain.ainvoke({
                "analysis": json.dumps(state["metadata"], indent=2),
                "paths": json.dumps(paths, indent=2)
            })
            
            stories = safe_json_loads(response.content)
            state["user_stories"] = stories
            state["current_step"] = "code_generation"
            return state
        except Exception as e:
            state["errors"].append(f"User story generation failed: {str(e)}")
            return state

    def _calculate_complexity_score(self, paths: Dict, schemas: Dict) -> Dict[str, Any]:
      
        
        # Count different HTTP methods
        method_counts = {}
        total_operations = 0
        
        for path, methods in paths.items():
            for method in methods:
                if method in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                    method_counts[method] = method_counts.get(method, 0) + 1
                    total_operations += 1
        
        # Calculate schema complexity
        schema_complexity = sum(
            len(schema.get('properties', {})) for schema in schemas.values()
        )
        
        return {
            "total_endpoints": len(paths),
            "total_operations": total_operations,
            "method_distribution": method_counts,
            "schema_count": len(schemas),
            "schema_complexity_score": schema_complexity,
            "complexity_rating": self._get_complexity_rating(total_operations, len(schemas))
        }
    
    def _generate_next_steps(self, analysis: Dict) -> List[str]:
        """Generate recommended next steps based on analysis"""
        next_steps = ["Generate user stories based on API analysis"]
        
        # Add conditional steps based on analysis content
        if "potential_improvements_recommendations" in analysis:
            next_steps.append("Review and prioritize improvement recommendations")
        
        if "risk_assessment" in analysis:
            next_steps.append("Create risk mitigation plan")
        
        if "security_compliance_story" in analysis:
            next_steps.append("Validate security and compliance requirements")
        
        next_steps.extend([
            "Create API integration documentation",
            "Develop testing strategy",
            "Plan monitoring and observability"
        ])
        
        return next_steps
