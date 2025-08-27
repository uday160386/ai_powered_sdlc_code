# README.md
# LangGraph Agentic AI Workflow

A sophisticated AI-powered workflow system that automatically generates user stories, production-ready code, and comprehensive unit tests from Swagger/OpenAPI specifications using LangGraph and multiple AI agents.

## Features

- **Multi-Agent Architecture**: Four specialized AI agents working in coordination
- **LangGraph Orchestration**: Robust workflow management and state handling
- **Swagger/OpenAPI Support**: Parse and analyze API specifications
- **User Story Generation**: Create detailed user stories with acceptance criteria
- **Code Generation**: Generate production-ready code in multiple frameworks
- **Test Generation**: Comprehensive unit and integration tests
- **Interactive UI**: User-friendly Streamlit interface
- **Export Capabilities**: Download complete project as ZIP

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set your OpenAI API key in the sidebar
4. Run: `streamlit run main.py`

## Usage

1. Upload your Swagger/OpenAPI file (JSON or YAML)
2. Select your preferred code and test frameworks
3. Click "Run Agentic Workflow"
4. Review generated user stories, code, and tests
5. Download the complete project

## Architecture

### Agents
- **SwaggerAnalyzerAgent**: Analyzes API specifications and extracts metadata
- **UserStoryAgent**: Generates user stories with business value focus
- **CodeGeneratorAgent**: Creates production-ready code following best practices
- **TestGeneratorAgent**: Generates comprehensive test suites

### Workflow
The LangGraph workflow orchestrates agents in sequence:
1. Swagger Analysis → 2. User Story Generation → 3. Code Generation → 4. Test Generation

## Supported Frameworks

**Code Generation:**
- FastAPI (Python)
- Flask (Python)  
- Django (Python)
- Express.js (Node.js)
- Spring Boot (Java)

**Test Frameworks:**
- pytest (Python)
- unittest (Python)
- Jest (JavaScript)
- JUnit (Java)
- Mocha (JavaScript)

## Configuration

Customize the workflow behavior by modifying `config.yaml`:
- Agent timeouts
- Model parameters
- Framework preferences
- Feature toggles