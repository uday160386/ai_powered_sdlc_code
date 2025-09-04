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
    Return your response as a strict, valid JSON array. Do not include any trailing commas, comments, or unquoted keys. Ensure all brackets and braces are closed. Do not include any text before or after the JSON array.
    """)
    
    async def generate_stories(self, state: WorkflowState) -> WorkflowState:
        try:
            paths = state["swagger_content"].get("paths", {})
            chain = self.prompt | self.llm
            response = chain.invoke({
                "analysis": json.dumps(state["metadata"], indent=2),
                "paths": json.dumps(paths, indent=2)
            })
            raw_content = json.loads(response.content)
            print("raw_content")
            
            # try:
            #     stories = safe_json_loads(raw_content)
            # except Exception as parse_err:
            #     # Fallback: Try to extract the largest valid JSON array from the response
            #     import re
            #     match = re.search(r'(\[[\s\S]+\])', raw_content)
            #     if match:
            #         candidate = match.group(1)
            #         try:
            #             stories = safe_json_loads(candidate)
            #         except Exception as inner_err:
            #             # Attempt to auto-close brackets/braces
            #             open_brackets = candidate.count('[')
            #             close_brackets = candidate.count(']')
            #             open_braces = candidate.count('{')
            #             close_braces = candidate.count('}')
            #             fixed = candidate + (']' * (open_brackets - close_brackets)) + ('}' * (open_braces - close_braces))
            #             try:
            #                 stories = safe_json_loads(fixed)
            #             except Exception as final_err:
            #                 state["errors"].append(
            #                     f"User story generation failed: Could not parse JSON array after auto-fix. Raw content:\n{raw_content[:1000]}"
            #                 )
            #                 stories = []
            #     else:
            #         state["errors"].append(f"User story generation failed: Could not find JSON array. Raw content:\n{raw_content[:1000]}")
            #         stories = []
            state["user_stories"] = raw_content
            state["current_step"] = "code_generation"
            return state
        except Exception as e:
            state["errors"].append(f"User story generation failed: {str(e)}")
            return state

   