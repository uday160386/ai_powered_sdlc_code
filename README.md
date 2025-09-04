# README.md

# AI-Powered SDLC Workflow with LangGraph

A sophisticated AI-powered workflow system that automatically generates user stories, production-ready code, containerization code, and comprehensive unit tests from Swagger/OpenAPI specifications using LangGraph and multiple AI agents. Includes real-time workflow visualization and multi-cloud support.

## Features

- **Multi-Agent Architecture**: Specialized AI agents for Swagger analysis, user story generation, code, container, and test generation
- **LangGraph Orchestration**: Robust workflow management and state handling
- **Swagger/OpenAPI Support**: Parse and analyze API specifications
- **User Story Generation**: Create detailed user stories with acceptance criteria
- **Code Generation**: Generate production-ready code in multiple frameworks
- **Containerization**: Generate Docker/container code for cloud deployment
- **Test Generation**: Comprehensive unit and integration tests
- **Multi-Cloud Support**: Select AWS or Azure for container code
- **Interactive UI**: User-friendly Streamlit interface
- **Real-Time Workflow Visualization**: Mermaid diagrams show workflow state and errors
- **Export Capabilities**: Download complete project as ZIP

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file and add your Anthropic API key:
	```
	ANTHROPIC_API_KEY=your-anthropic-key-here
	```
4. Run: `streamlit run main.py`

## Usage

1. Upload your Swagger/OpenAPI file (JSON or YAML) in the sidebar
2. Select your preferred code framework, test framework, and public cloud (AWS or Azure)
3. Click "🚀 Generate Components"
4. Watch the real-time workflow diagram update as each step completes
5. Review generated user stories, code, container code, and tests in the results tabs
6. Download the complete project as a ZIP file

## Architecture

### Agents
- **SwaggerAnalyzerAgent**: Analyzes API specifications and extracts metadata
- **UserStoryAgent**: Generates user stories with business value focus
- **CodeGeneratorAgent**: Creates production-ready code following best practices
- **ContainerziedCodeGenerationAgent**: Generates Docker/container code for cloud deployment
- **TestGeneratorAgent**: Generates comprehensive test suites

### Workflow
The LangGraph workflow orchestrates agents in sequence:
1. Swagger Analysis → 2. User Story Generation → 3. Code Generation → 4. Test Generation → 5. Container Code Generation

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

**Container/Cloud:**
- AWS (Docker)
- Azure (Docker)

## Configuration

Customize the workflow behavior by modifying `config.yaml`:
- Agent timeouts
- Model parameters (e.g., temperature, max_tokens)
- Framework preferences
- Cloud provider
- Feature toggles

## Real-Time Workflow Visualization

The app displays a real-time Mermaid diagram of the workflow, showing:
- Each step (node) in the workflow
- Number of generated items per step
- Current step highlighted
- Errors highlighted in red

## License

MIT