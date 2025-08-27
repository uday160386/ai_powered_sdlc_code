# # Standard library imports
# import os
# import io
# import json
# import yaml
# import zipfile
# import asyncio
# from enum import Enum
# from dataclasses import dataclass
# from typing import Dict, List, Any, TypedDict

# # Third-party imports
# import streamlit as st
# from dotenv import load_dotenv

# # LangChain and LangGraph imports
# from langchain_openai import ChatOpenAI
# from langgraph.graph import StateGraph, END
# from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
# from langchain_core.prompts import ChatPromptTemplate

# # Local agent imports
# from app.agent.SwaggerAnalyzerAgent import SwaggerAnalyzerAgent
# from app.agent.UserStoryGenerationAgent import UserStoryAgent
# from app.agent.CodeGenerationAgent import CodeGeneratorAgent
# from app.agent.UnitTestcaseGenerationAgent import TestGeneratorAgent

# # State Management
# class WorkflowState(TypedDict):
#     swagger_content: Dict[str, Any]
#     user_stories: List[Dict[str, Any]]
#     generated_code: Dict[str, str]
#     unit_tests: Dict[str, str]
#     current_step: str
#     errors: List[str]
#     metadata: Dict[str, Any]


# # LangGraph Workflow Definition
# class AgenticWorkflow:
#     def __init__(self, api_key: str):
#         self.llm = ChatOpenAI(
#             api_key=api_key,
#             model="gpt-4-turbo-preview",
#             temperature=0.3
#         )
#         self.swagger_agent = SwaggerAnalyzerAgent(self.llm)
#         self.story_agent = UserStoryAgent(self.llm)
#         self.code_agent = CodeGeneratorAgent(self.llm)
#         self.test_agent = TestGeneratorAgent(self.llm)
#         self.workflow = self._build_workflow()

#     def _build_workflow(self) -> StateGraph:
#         workflow = StateGraph(WorkflowState)
#         workflow.add_node("analyze_swagger", self.swagger_agent.analyze)
#         workflow.add_node("generate_stories", self.story_agent.generate_stories)
#         workflow.add_node("generate_code", self.code_agent.generate_code)
#         workflow.add_node("generate_tests", self.test_agent.generate_tests)
#         workflow.add_edge("analyze_swagger", "generate_stories")
#         workflow.add_edge("generate_stories", "generate_code")
#         workflow.add_edge("generate_code", "generate_tests")
#         workflow.add_edge("generate_tests", END)
#         workflow.set_entry_point("analyze_swagger")
#         return workflow.compile()

#     async def run_workflow(self, swagger_content: Dict[str, Any]) -> WorkflowState:
#         initial_state: WorkflowState = {
#             "swagger_content": swagger_content,
#             "user_stories": [],
#             "generated_code": {},
#             "unit_tests": {},
#             "current_step": "analyze_swagger",
#             "errors": [],
#             "metadata": {}
#         }
#         result = await self.workflow.ainvoke(initial_state)
#         return result


# class StepStatus(Enum):
#     PENDING = "pending"
#     RUNNING = "running"
#     COMPLETED = "completed"
#     FAILED = "failed"


# @dataclass
# class AgentResult:
#     success: bool
#     data: Any
#     message: str
#     step: str




