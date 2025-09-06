# LangGraph Workflow Definition
from langchain_anthropic import ChatAnthropic

# Local imports
from app.agent.req.SwaggerAnalyzerAgent import SwaggerAnalyzerAgent
from app.agent.story.UserStoryGenerationAgent import UserStoryAgent
from app.agent.code.CodeGenerationAgent import CodeGeneratorAgent
from app.agent.test.UnitTestcaseGenerationAgent import TestGeneratorAgent
from app.agent.container.ContainerziedCodeGenerationAgent import ContainerziedCodeGenerationAgent
from app.agent.monitor.ProductionMonitorAgent import ProductionMonitorGenerationAgent
from app.agent.info.SetUpguideAgent import SetUpGuideAgent

from langgraph.graph import StateGraph, END

from dataclasses import dataclass
from typing import Dict, Any

from enum import Enum

from app.workflow.WorkflowState import WorkflowState
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
    
    

class AgenticWorkflow:
    def __init__(self, api_key: str, framework: str, test_framework: str, cloud_option: str):
        
        
        self.llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",  # Or other models like "claude-3-opus-20240229"
            api_key=api_key,  # Use this if not using environment variable
            temperature=0.3,
            max_tokens=7000  # Set a reasonable max token limit for output
        )
        
        self.framework = framework
        self.test_framework= test_framework
        self.cloud_option = cloud_option
        self.swagger_agent = SwaggerAnalyzerAgent(self.llm)
        self.story_agent = UserStoryAgent(self.llm)
        self.code_agent = CodeGeneratorAgent(self.llm)
        self.container_code_agent = ContainerziedCodeGenerationAgent(self.llm)
        self.test_agent = TestGeneratorAgent(self.llm)
        self.setup_agent = SetUpGuideAgent(self.llm)
        self.monitor_agent = ProductionMonitorGenerationAgent(self.llm)
        
        self.workflow = self._build_workflow()
        
        

    def _build_workflow(self) -> StateGraph:
        # Create the state graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("analyze_swagger", self.swagger_agent.analyze)
       
        workflow.add_node("generate_stories", self.story_agent.generate_stories)
        workflow.add_node("generated_container_code",  self.container_code_agent.generate_code )
        workflow.add_node("generated_readme_code",  self.setup_agent.generate_code )

        workflow.add_node("generated_monitor_configs",  self.monitor_agent.generate_code )
        
        async def generate_code_with_framework(state):
            state["framework"] = self.framework
            return await self.code_agent.generate_code(state, self.framework)
        
        async def generate_code_with_test_framework(state):
            state["test_framework"] = self.test_framework
            return await self.test_agent.generate_tests(state, self.test_framework)
        async def select_cloud_code(state):
            state["generated_container_code"] = self.cloud_option
            return await self.container_code_agent.generate_code(state, self.cloud_option)
        
        workflow.add_node("generate_code", generate_code_with_framework)
        workflow.add_node("generate_tests", generate_code_with_test_framework)
        
        # Define the workflow edges
        workflow.add_edge("analyze_swagger", "generate_stories")
        workflow.add_edge("generate_stories", "generate_code")
        workflow.add_edge("generate_code", "generate_tests")
        workflow.add_edge("generate_tests", "generated_container_code")
        workflow.add_edge("generated_container_code", "generated_monitor_configs")
        workflow.add_edge("generated_monitor_configs", "generated_readme_code")
        workflow.add_edge("generated_readme_code", END)

        # Set entry point
        workflow.set_entry_point("analyze_swagger")
        
        return workflow.compile()
    
    
    async def run_workflow(self, swagger_content: Dict[str, Any]) -> WorkflowState:
        initial_state: WorkflowState = {
            "swagger_content": swagger_content,
            "user_stories": [],
            "generated_code": {},
            "unit_tests": {},
            "generated_container_code": {},
            "readme": {},
            "generated_monitor_configs": {},
            "current_step": "analyze_swagger",
            "errors": [],
            "metadata": {}
        }
        
        result = await self.workflow.ainvoke(initial_state)
        return result
