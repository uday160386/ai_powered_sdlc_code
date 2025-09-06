from langchain.prompts import ChatPromptTemplate
from app.workflow.WorkflowState import WorkflowState
import json
from typing import Dict, List, Any
from datetime import datetime

class TestGeneratorAgent:
    def __init__(self, llm):
        self.llm = llm
        self.coverage_target = 70  # 70% coverage target
        self.prompt = ChatPromptTemplate.from_template("""
                                                       
        Generated Code: {generated_code}
        Test Framework: {test_framework}
        You are a senior software test engineer with expertise in API testing and achieving precise code coverage targets.
        Generate professional, production-ready unit tests using {test_framework}that achieve exactly 70% code coverage.

        **Swagger Specification Analysis:**
        

        **Coverage Strategy for 70% Target:**
        - Focus on critical business logic paths
        - Prioritize happy path scenarios (40% of coverage)
        - Include essential error handling (20% of coverage)
        - Add boundary condition testing (10% of coverage)
        - Strategic exclusion of boilerplate and configuration code

        **Professional Test Requirements:**

        1. **API Endpoint Testing** (Primary Focus):
           - Test each HTTP method (GET, POST, PUT, DELETE, PATCH)
           - Validate request/response schemas against Swagger definitions
           - Test authentication and authorization mechanisms
           - Validate HTTP status codes and error responses
           - Test query parameters, path parameters, and request bodies

        2. **Business Logic Unit Tests**:
           - Test core business rules identified in Swagger operations
           - Validate data transformation and processing logic
           - Test service layer methods and functions
           - Validate model/entity business methods
           - Test utility functions and helpers

        3. **Data Validation Testing**:
           - Test input validation based on Swagger schema constraints
           - Validate required vs optional fields
           - Test data type validation (string, integer, boolean, etc.)
           - Test format validation (email, date, UUID, etc.)
           - Test enum value validation

        4. **Error Handling Coverage**:
           - Test HTTP 400 (Bad Request) scenarios
           - Test HTTP 401 (Unauthorized) scenarios  
           - Test HTTP 404 (Not Found) scenarios
           - Test HTTP 500 (Internal Server Error) scenarios
           - Test custom business exception handling

        5. **Integration Points Testing**:
           - Mock external dependencies and services
           - Test database interaction layers
           - Test caching mechanisms if present
           - Test message queue integrations if applicable
           - Test file upload/download operations

        **Test Code Quality Standards:**
        - Use descriptive test method names following convention: test_[method]_[scenario]_[expected_result]
        - Implement AAA pattern (Arrange, Act, Assert)
        - Use appropriate fixtures and mocks for external dependencies
        - Include comprehensive docstrings explaining test purpose
        - Implement parameterized tests for multiple input scenarios
        - Use proper assertion methods with descriptive failure messages
        - Follow PEP 8 coding standards for test code

        **Framework-Specific Implementation for {test_framework}:**
        - Use pytest fixtures for test data and mocks
        - Implement proper setup and teardown methods
        - Use pytest.mark for test categorization
        - Implement parametrized tests with @pytest.mark.parametrize
        - Use appropriate mocking with unittest.mock or pytest-mock
        - Include performance markers for slow tests

        **Coverage Calculation Strategy:**
        Based on the Swagger specification, identify:
        - Total number of endpoints and operations
        - Core business methods requiring testing
        - Critical error handling paths
        - Essential validation logic
        - Key integration points

        Then generate tests to cover exactly 70% of:
        - All endpoint handlers
        - Primary business logic methods
        - Essential error scenarios
        - Critical data validation paths

        **Output Requirements:**
        Generate a complete JSON response with the following structure:
        {{
            "coverage_analysis": {{
                "target_coverage": "70%",
                "estimated_coverage": "calculated coverage percentage",
                "coverage_strategy": "detailed strategy explanation",
                "critical_paths": ["list of critical code paths to test"],
                "excluded_paths": ["list of paths excluded from testing with rationale"]
            }},
            "test_files": {{
                "test_[module_name].py": {{
                    "file_path": "tests/unit/test_[module_name].py",
                    "code": "complete test file code with imports, fixtures, and test methods",
                    "test_count": "number of test methods",
                    "coverage_contribution": "percentage of overall coverage this file provides",
                    "tested_endpoints": ["list of API endpoints tested"],
                    "tested_methods": ["list of business methods tested"]
                }}
            }},
            "test_configuration": {{
                "pytest_ini": "pytest configuration for coverage reporting",
                "requirements_txt": "test dependencies",
                "conftest_py": "shared test fixtures and configurations"
            }},
            "execution_instructions": {{
                "run_tests": "command to run all tests",
                "coverage_report": "command to generate coverage report",
                "ci_integration": "CI/CD pipeline configuration snippet"
            }},
            "quality_metrics": {{
                "expected_test_count": "total number of test methods",
                "coverage_breakdown": {{
                    "endpoints": "percentage of endpoints covered",
                    "business_logic": "percentage of business logic covered",
                    "error_handling": "percentage of error paths covered"
                }},
                "test_categories": {{
                    "unit_tests": "count of pure unit tests",
                    "integration_tests": "count of integration tests",
                    "api_tests": "count of API endpoint tests"
                }}
            }}
        }}

        **Professional Standards:**
        - All test methods must have clear, descriptive names
        - Include comprehensive docstrings for complex test scenarios
        - Use realistic test data that reflects actual business use cases
        - Implement proper error assertions with specific exception types
        - Include performance considerations for critical paths
        - Add logging statements for test debugging
        - Follow security testing best practices
        - Include data cleanup in teardown methods

        Generate tests that a senior developer would be proud to review and maintain.
        Focus on quality over quantity while achieving the 70% coverage target.
        
        Output format:
        For each file, use the following delimiters (do not use markdown or code blocks):
        >>>FILE_PATH_START<<< path/to/file.py >>>FILE_PATH_END<<<
        >>>FILE_CONTENT_START<<<
        <file content here>
        >>>FILE_CONTENT_END<<<
        Repeat for each file. Do not return JSON. Only return plain text in the above format.
        """)

    async def generate_tests(self, state: WorkflowState, test_framework: str = "pytest") -> WorkflowState:
        """
        Generate professional test suite targeting 70% code coverage
        """
        try:
            swagger_content = state.get("swagger_content", {})
            generated_code = state.get("generated_code", {})
            user_stories = state.get("user_stories", [])
            
            # Generate tests using LLM
            chain = self.prompt | self.llm
            response = chain.invoke({
                "generated_code": json.dumps(generated_code, indent=2),
                "test_framework": test_framework
            })
            
            print("✅ Test generation completed")
            
            # Parse and validate response
    
            raw_content = response.content.strip()
            # Parse the response using new explicit delimiters
            files = {}
            import re
            pattern = r">>>FILE_PATH_START<<<\s*(.*?)\s*>>>FILE_PATH_END<<<\s*>>>FILE_CONTENT_START<<<\n([\s\S]*?)\n>>>FILE_CONTENT_END<<<"
            matches = re.findall(pattern, raw_content)
            if not matches:
                # Fallback: Try to extract code blocks if delimiters are missing
                fallback_pattern = r"([\w\-/]+\.py)[\s\S]*?```([\s\S]*?)```"
                fallback_matches = re.findall(fallback_pattern, raw_content)
                if fallback_matches:
                    for file_path, file_content in fallback_matches:
                        files[file_path.strip()] = file_content.strip()
                    state["unit_tests"] = files
                    # Create in-memory ZIP
                    import io, zipfile
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                        for path, content in files.items():
                            zip_file.writestr(path, content)
                    zip_buffer.seek(0)
                    state["generated_zip"] = zip_buffer.read()
                else:
                    state["errors"].append(
                        f"Code generation failed: No files found in LLM response. Raw content:\n{raw_content[:1000]}"
                    )
                    state["unit_tests"] = {}
            else:
                for file_path, file_content in matches:
                    files[file_path.strip()] = file_content.strip()
                state["unit_tests"] = files
                # Create in-memory ZIP
                import io, zipfile
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for path, content in files.items():
                        zip_file.writestr(path, content)
                zip_buffer.seek(0)
                state["generated_zip"] = zip_buffer.read()

            state["current_step"] = "generated_container_code"
            return state
        except Exception as e:
            state["errors"].append(f"Code generation failed: {str(e)}")
            return state