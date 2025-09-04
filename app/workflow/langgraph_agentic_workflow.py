import streamlit as st
import json
import yaml
from typing import Dict, List, Any, TypedDict
from dataclasses import dataclass
from enum import Enum
import asyncio
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import tempfile
import zipfile
import io
import re
import os
from dotenv import load_dotenv
from langchain_community.llms import Anthropic


# State Management
class WorkflowState(TypedDict):
    swagger_content: Dict[str, Any]
    user_stories: List[Dict[str, Any]]
    generated_code: Dict[str, str]
    unit_tests: Dict[str, str]
    current_step: str
    errors: List[str]
    metadata: Dict[str, Any]

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
    


# LangGraph Workflow Definition
class AgenticWorkflow:
    def __init__(self, api_key: str):
        
        self.llm = Anthropic(
            api_key=api_key,
            model="claude-3-sonnet-20240229",
            temperature=0.3
        )
        
        self.swagger_agent = SwaggerAnalyzerAgent(self.llm)
        self.story_agent = UserStoryAgent(self.llm)
        self.code_agent = CodeGeneratorAgent(self.llm)
        self.test_agent = TestGeneratorAgent(self.llm)
        
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        # Create the state graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("analyze_swagger", self.swagger_agent.analyze)
        workflow.add_node("generate_stories", self.story_agent.generate_stories)
        workflow.add_node("generate_code", self.code_agent.generate_code)
        workflow.add_node("generate_tests", self.test_agent.generate_tests)
        
        # Define the workflow edges
        workflow.add_edge("analyze_swagger", "generate_stories")
        workflow.add_edge("generate_stories", "generate_code")
        workflow.add_edge("generate_code", "generate_tests")
        workflow.add_edge("generate_tests", END)
        
        # Set entry point
        workflow.set_entry_point("analyze_swagger")
        
        return workflow.compile()
    
    async def run_workflow(self, swagger_content: Dict[str, Any]) -> WorkflowState:
        initial_state: WorkflowState = {
            "swagger_content": swagger_content,
            "user_stories": [],
            "generated_code": {},
            "unit_tests": {},
            "current_step": "analyze_swagger",
            "errors": [],
            "metadata": {}
        }
        
        result = await self.workflow.ainvoke(initial_state)
        return result
