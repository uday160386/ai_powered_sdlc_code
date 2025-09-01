import json
from typing import Dict, List, Any, Optional
from langchain.prompts import ChatPromptTemplate
from app.util.safe_text_genneration import safe_load, is_structured_data, safe_json_loads


from app.workflow.langgraph_agentic_workflow import WorkflowState
class UserStoryAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_template("""
        You are an expert API business analyst. Include edge cases and error handling scenarios.
        Based on the Swagger API analysis, generate comprehensive user stories:
        
        For each endpoint, create user stories that include:
        1. Title
        2. user_story (As a... I want... So that...)
        3. acceptance_criteria (Given/When/Then format)
        4. priority (High/Medium/Low)
        5. estimated_effort (Story points 1-13)
        6. Create both functional and non-functional stories.
        7. Include edge cases and error handling scenarios.
        
        Focus on business value and user needs. Consider different user personas.
        Return as a JSON array of user story objects.
        """)
    
    
    
    async def analyze(self, state: WorkflowState) -> WorkflowState:
        """
        Performs comprehensive analysis of Swagger/OpenAPI specification with detailed storytelling
        """
        try:
            # Prepare enriched context for analysis
            swagger_content = state.get("swagger_content", {})
            
            # Extract additional context clues
            api_title = swagger_content.get("info", {}).get("title", "Unknown API")
            api_version = swagger_content.get("info", {}).get("version", "Unknown")
            base_url = swagger_content.get("servers", [{}])[0].get("url", "Unknown")
            
            print(f"🔍 Analyzing {api_title} v{api_version}...")
            print(f"📡 Base URL: {base_url}")
            
            # Enhanced chain execution with retry logic
            chain = self.prompt | self.llm
            
           
            
            response = await chain.ainvoke({
                "swagger_content": json.dumps(state["swagger_content"], indent=2)
            })
            
            print("✅ Raw AI Response Generated______User Stioyr Gen")
            print(f"📄 Response Length: {len(response.content)} characters")
            
            # Parse and enrich the analysis
            print("step2")
            print(response.content)
            print("next")
            try:
                print(is_structured_data(response.content))
                analysis = safe_json_loads(response.content)
                
                # Add metadata about the analysis process
                analysis_metadata = {
                    "analysis_timestamp": state.get("timestamp"),
                    "api_complexity_score": self._calculate_complexity_score(swagger_content),
                    "endpoint_count": len(swagger_content.get("paths", {})),
                    "schema_count": len(swagger_content.get("components", {}).get("schemas", {})),
                    "analysis_completeness": self._assess_analysis_completeness(analysis),
                    "recommended_next_steps": self._generate_next_steps(analysis)
                }
                
                # Merge analysis with metadata
                enriched_analysis = {
                    **analysis,
                    "analysis_metadata": analysis_metadata
                }
                
                state["metadata"] = enriched_analysis
                state["current_step"] = "user_stories"
                
                print("🎯 Analysis Complete - Key Insights:")
                if "api_story_business_context" in analysis:
                    context = analysis["api_story_business_context"]
                    print(f"   📊 Business Domain: {context.get('business_domain', 'Not identified')}")
                    print(f"   🎯 Primary Use Case: {context.get('primary_use_case', 'Not identified')}")
                    print(f"   👥 Target Users: {context.get('target_users', 'Not identified')}")
                
                return state
                
            except json.JSONDecodeError as json_error:
                print(f"⚠️ JSON parsing failed, storing raw response: {str(json_error)}")
                # Fallback: store raw response with error context
                state["metadata"] = {
                    "raw_analysis": response.content,
                    "parsing_error": str(json_error),
                    "analysis_status": "partial"
                }
                state["warnings"] = state.get("warnings", [])
                state["warnings"].append("Analysis returned non-JSON format, stored as raw text")
                return state
                
        except Exception as e:
            error_details = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "analysis_step": "swagger_analysis",
                "troubleshooting_hints": [
                    "Check if Swagger content is valid JSON",
                    "Verify LLM connectivity and rate limits",
                    "Ensure sufficient context window size",
                    "Review prompt template formatting"
                ]
            }
            
            state["errors"].append(f"Swagger analysis failed: {json.dumps(error_details, indent=2)}")
            print(f"❌ Analysis Failed: {str(e)}")
            
            # Set partial state for debugging
            state["debug_info"] = {
                "failed_at": "swagger_analysis",
                "swagger_content_available": bool(state.get("swagger_content")),
                "llm_available": bool(self.llm)
            }
            
            return state
    
    def _calculate_complexity_score(self, swagger_content: Dict) -> Dict[str, Any]:
        """Calculate API complexity metrics"""
        paths = swagger_content.get("paths", {})
        schemas = swagger_content.get("components", {}).get("schemas", {})
        
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
    
    def _get_complexity_rating(self, operations: int, schemas: int) -> str:
        """Determine API complexity rating"""
        total_complexity = operations + (schemas * 2)  # Weight schemas more heavily
        
        if total_complexity < 10:
            return "Simple"
        elif total_complexity < 50:
            return "Moderate"
        elif total_complexity < 150:
            return "Complex"
        else:
            return "Highly Complex"
    
    def _assess_analysis_completeness(self, analysis: Dict) -> Dict[str, Any]:
        """Assess how complete the analysis is"""
        expected_sections = [
            "api_story_business_context",
            "detailed_endpoint_analysis", 
            "data_model_deep_dive",
            "security_compliance_story",
            "integration_ecosystem",
            "technical_quality_assessment",
            "business_intelligence_insights",
            "user_experience_journey",
            "potential_improvements_recommendations",
            "risk_assessment"
        ]
        
        present_sections = [section for section in expected_sections if section in analysis]
        completeness_score = len(present_sections) / len(expected_sections)
        
        return {
            "completeness_percentage": round(completeness_score * 100, 2),
            "present_sections": present_sections,
            "missing_sections": [s for s in expected_sections if s not in present_sections],
            "quality_assessment": "High" if completeness_score > 0.8 else "Medium" if completeness_score > 0.5 else "Low"
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