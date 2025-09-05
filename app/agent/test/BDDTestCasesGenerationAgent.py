# def __init__(self, api_key: str):
#         self.api_key = api_key
    
#     def generate_stories(self, state: WorkflowState) -> WorkflowState:
#         """Generate user stories from API analysis."""
#         try:
#             system_msg = "You are a product manager expert in writing user stories. Create detailed, valuable user stories."
            
#             prompt = f"""
#             Based on the API analysis, generate comprehensive user stories:
            
#             API Analysis: {json.dumps(state.metadata, indent=2)}
#             API Paths: {json.dumps(state.swagger_content.get('paths', {}), indent=2)[:2000]}
            
#             For each major endpoint/feature, create user stories with:
#             1. "title": Short descriptive title
#             2. "story": User story in "As a [user type], I want [goal] so that [benefit]" format
#             3. "acceptance_criteria": Array of Given/When/Then statements
#             4. "priority": "High", "Medium", or "Low"
#             5. "effort": Story points from 1-13
            
#             Focus on business value and different user personas (end users, admins, developers).
#             Return as a JSON array of user story objects. Return only valid JSON.
#             """
            
#             response = make_openai_call(self.api_key, prompt, system_msg)
            
#             if response:
#                 try:
#                     stories = json.loads(response)
#                     state.user_stories = stories if isinstance(stories, list) else [stories]
#                 except json.JSONDecodeError:
#                     state.user_stories = self._fallback_stories(state.swagger_content)
#             else:
#                 state.user_stories = self._fallback_stories(state.swagger_content)
            
#             state.current_step = "code_generation"
#             return state
            
#         except Exception as e:
#             state.errors.append(f"User story generation failed: {str(e)}")
#             state.user_stories = self._fallback_stories(state.swagger_content)
#             return state
    
#     def _fallback_stories(self, swagger_content: dict) -> list:
#         """Generate basic user stories without LLM."""
#         stories = []
#         paths = swagger_content.get("paths", {})
        
#         for path, methods in paths.items():
#             for method, operation in methods.items():
#                 title = operation.get("summary", f"{method.upper()} {path}")
                
#                 stories.append({
#                     "title": title,
#                     "story": f"As a user, I want to {title.lower()} so that I can manage my data effectively",
#                     "acceptance_criteria": [
#                         "Given I have valid credentials",
#                         f"When I make a {method.upper()} request to {path}",
#                         "Then I should receive a valid response",
#                         "And the response should contain expected data"
#                     ],
#                     "priority": "Medium",
#                     "effort": "3"
#                 })
        
#         return stories
