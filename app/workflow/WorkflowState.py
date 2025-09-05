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
