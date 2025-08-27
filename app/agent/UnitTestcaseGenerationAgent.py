from app.util.safe_text_genneration import safe_json_loads
from langchain.prompts import ChatPromptTemplate
from app.workflow.langgraph_agentic_workflow import WorkflowState
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

class TestGeneratorAgent:
    def __init__(self, llm):
        self.llm = llm
        self.coverage_target = 70  # 70% coverage target
        self.prompt = ChatPromptTemplate.from_template("""
        You are a senior software test engineer with expertise in API testing and achieving precise code coverage targets.
        Generate professional, production-ready unit tests that achieve exactly 70% code coverage.

        **Swagger Specification Analysis:**
        Swagger Content: {swagger_content}
        Generated Code: {generated_code}
        User Stories: {user_stories}
        Test Framework: {test_framework}

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
        """)

    async def generate_tests(self, state: WorkflowState, test_framework: str = "pytest") -> WorkflowState:
        """
        Generate professional test suite targeting 70% code coverage
        """
        try:
            swagger_content = state.get("swagger_content", {})
            generated_code = state.get("generated_code", {})
            user_stories = state.get("user_stories", [])
            
            print(f"🎯 Generating professional test suite targeting 70% coverage...")
            print(f"📋 Framework: {test_framework}")
            
            # Analyze Swagger specification for test planning
            coverage_plan = self._analyze_swagger_for_coverage(swagger_content)
            print(f"📊 Coverage Plan: {coverage_plan['total_endpoints']} endpoints, {coverage_plan['complexity_score']} complexity")
            
            # Generate tests using LLM
            chain = self.prompt | self.llm
            response = await chain.ainvoke({
                "swagger_content": json.dumps(swagger_content, indent=2),
                "generated_code": json.dumps(generated_code, indent=2),
                "user_stories": json.dumps(user_stories, indent=2),
                "test_framework": test_framework
            })
            
            print("✅ Test generation completed")
            
            # Parse and validate response
            test_suite = safe_json_loads(response.content)
            
            # Enrich test suite with additional metadata
            enriched_test_suite = self._enrich_test_suite(test_suite, coverage_plan, swagger_content)
            
            # Update state
            state["unit_tests"] = enriched_test_suite
            state["test_coverage_target"] = self.coverage_target
            state["test_generation_metadata"] = {
                "framework": test_framework,
                "generation_timestamp": datetime.now().isoformat(),
                "coverage_analysis": coverage_plan,
                "estimated_test_count": self._count_tests_in_suite(enriched_test_suite)
            }
            state["current_step"] = "test_validation"
            
            # Log success metrics
            self._log_test_generation_success(enriched_test_suite, coverage_plan)
            
            return state
            
        except json.JSONDecodeError as json_error:
            error_msg = f"Failed to parse test generation response as JSON: {str(json_error)}"
            print(f"❌ JSON Parse Error: {error_msg}")
            
            # Store raw response for debugging
            state["unit_tests"] = {
                "generation_error": "json_parse_failure",
                "raw_response": response.content if 'response' in locals() else "No response generated",
                "error_details": str(json_error)
            }
            state["errors"].append(error_msg)
            return state
            
        except Exception as e:
            error_msg = f"Test generation failed: {str(e)}"
            print(f"❌ Test Generation Error: {error_msg}")
            
            state["errors"].append(error_msg)
            state["test_generation_metadata"] = {
                "status": "failed",
                "error_type": type(e).__name__,
                "error_message": str(e),
                "framework": test_framework,
                "timestamp": datetime.now().isoformat()
            }
            return state

    def _analyze_swagger_for_coverage(self, swagger_content: Dict) -> Dict[str, Any]:
        """
        Analyze Swagger specification to plan test coverage strategy
        """
        paths = swagger_content.get("paths", {})
        components = swagger_content.get("components", {})
        schemas = components.get("schemas", {})
        
        # Count endpoints and operations
        total_endpoints = len(paths)
        total_operations = 0
        http_methods = set()
        
        for path, methods in paths.items():
            for method in methods:
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                    total_operations += 1
                    http_methods.add(method.upper())
        
        # Analyze schemas for validation testing
        schema_properties = 0
        required_fields = 0
        
        for schema_name, schema_def in schemas.items():
            properties = schema_def.get("properties", {})
            schema_properties += len(properties)
            required_fields += len(schema_def.get("required", []))
        
        # Calculate complexity score
        complexity_score = (
            total_operations * 2 +  # Each operation needs multiple tests
            schema_properties * 1 +  # Each property needs validation
            len(http_methods) * 1    # Each HTTP method type
        )
        
        # Determine critical paths for 70% coverage
        critical_paths = self._identify_critical_paths(paths)
        
        return {
            "total_endpoints": total_endpoints,
            "total_operations": total_operations,
            "http_methods": list(http_methods),
            "schema_count": len(schemas),
            "schema_properties": schema_properties,
            "required_fields": required_fields,
            "complexity_score": complexity_score,
            "critical_paths": critical_paths,
            "coverage_strategy": self._create_coverage_strategy(total_operations, complexity_score)
        }
    
    def _identify_critical_paths(self, paths: Dict) -> List[Dict]:
        """
        Identify critical API paths that must be covered for 70% target
        """
        critical_paths = []
        
        for path, methods in paths.items():
            for method, operation_def in methods.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                    # Determine criticality based on operation characteristics
                    criticality = self._calculate_path_criticality(operation_def)
                    
                    critical_paths.append({
                        "path": path,
                        "method": method.upper(),
                        "operation_id": operation_def.get("operationId", f"{method}_{path}"),
                        "criticality_score": criticality,
                        "requires_auth": "security" in operation_def,
                        "has_request_body": "requestBody" in operation_def,
                        "response_codes": list(operation_def.get("responses", {}).keys())
                    })
        
        # Sort by criticality and select top 70%
        critical_paths.sort(key=lambda x: x["criticality_score"], reverse=True)
        coverage_count = int(len(critical_paths) * 0.7)
        
        return critical_paths[:coverage_count]
    
    def _calculate_path_criticality(self, operation_def: Dict) -> int:
        """
        Calculate criticality score for an API operation
        """
        score = 0
        
        # Base score for all operations
        score += 10
        
        # Higher score for operations with request bodies (data modification)
        if "requestBody" in operation_def:
            score += 15
        
        # Higher score for operations with security requirements
        if "security" in operation_def:
            score += 10
        
        # Higher score for operations with multiple response codes
        responses = operation_def.get("responses", {})
        score += len(responses) * 2
        
        # Higher score for operations with parameters
        parameters = operation_def.get("parameters", [])
        score += len(parameters) * 3
        
        # Higher score for CRUD operations
        operation_id = operation_def.get("operationId", "").lower()
        crud_keywords = ["create", "update", "delete", "get", "list", "find"]
        if any(keyword in operation_id for keyword in crud_keywords):
            score += 8
        
        return score
    
    def _create_coverage_strategy(self, total_operations: int, complexity_score: int) -> Dict:
        """
        Create detailed coverage strategy for 70% target
        """
        target_operations = int(total_operations * 0.7)
        
        return {
            "total_operations": total_operations,
            "target_operations": target_operations,
            "coverage_distribution": {
                "happy_path": "40%",
                "error_handling": "20%", 
                "edge_cases": "10%"
            },
            "test_priorities": [
                "Critical business operations",
                "Data validation paths",
                "Authentication/authorization",
                "Primary error scenarios",
                "Essential integrations"
            ],
            "excluded_areas": [
                "Boilerplate code",
                "Configuration files", 
                "Simple getters/setters",
                "Non-critical utility functions"
            ]
        }
    
    def _enrich_test_suite(self, test_suite: Dict, coverage_plan: Dict, swagger_content: Dict) -> Dict:
        """
        Enrich generated test suite with additional metadata and validation
        """
        if not isinstance(test_suite, dict):
            return {"error": "Invalid test suite format", "raw_content": str(test_suite)}
        
        # Add coverage analysis
        test_suite["coverage_validation"] = {
            "target_coverage": f"{self.coverage_target}%",
            "critical_paths_covered": len(coverage_plan.get("critical_paths", [])),
            "total_operations": coverage_plan.get("total_operations", 0),
            "estimated_coverage": self._estimate_actual_coverage(test_suite, coverage_plan)
        }
        
        # Add test execution metadata
        test_suite["execution_metadata"] = {
            "recommended_parallel_execution": True,
            "estimated_execution_time": self._estimate_execution_time(test_suite),
            "resource_requirements": {
                "memory": "512MB minimum",
                "cpu": "2 cores recommended",
                "storage": "100MB for test artifacts"
            }
        }
        
        # Add quality gates
        test_suite["quality_gates"] = {
            "minimum_coverage": "65%",
            "target_coverage": "70%",
            "maximum_test_execution_time": "300 seconds",
            "code_quality_score": "A- or better"
        }
        
        return test_suite
    
    def _estimate_actual_coverage(self, test_suite: Dict, coverage_plan: Dict) -> str:
        """
        Estimate actual coverage percentage based on generated tests
        """
        if "test_files" not in test_suite:
            return "0%"
        
        test_files = test_suite["test_files"]
        total_coverage = 0
        
        for file_data in test_files.values():
            if isinstance(file_data, dict) and "coverage_contribution" in file_data:
                try:
                    contrib = file_data["coverage_contribution"]
                    if isinstance(contrib, str) and contrib.endswith("%"):
                        total_coverage += float(contrib[:-1])
                    elif isinstance(contrib, (int, float)):
                        total_coverage += contrib
                except (ValueError, TypeError):
                    continue
        
        return f"{min(total_coverage, 100):.1f}%"
    
    def _estimate_execution_time(self, test_suite: Dict) -> str:
        """
        Estimate test execution time based on test count and complexity
        """
        test_count = self._count_tests_in_suite(test_suite)
        
        # Estimate 0.5 seconds per unit test, 2 seconds per integration test
        unit_tests = test_count.get("unit_tests", 0)
        integration_tests = test_count.get("integration_tests", 0)
        
        estimated_seconds = (unit_tests * 0.5) + (integration_tests * 2.0)
        
        if estimated_seconds < 60:
            return f"{estimated_seconds:.0f} seconds"
        else:
            return f"{estimated_seconds/60:.1f} minutes"
    
    def _count_tests_in_suite(self, test_suite: Dict) -> Dict[str, int]:
        """
        Count different types of tests in the generated suite
        """
        if not isinstance(test_suite, dict) or "test_files" not in test_suite:
            return {"unit_tests": 0, "integration_tests": 0, "total": 0}
        
        unit_tests = 0
        integration_tests = 0
        
        for file_data in test_suite["test_files"].values():
            if isinstance(file_data, dict):
                test_count = file_data.get("test_count", 0)
                if isinstance(test_count, str):
                    try:
                        test_count = int(test_count)
                    except ValueError:
                        test_count = 0
                
                # Categorize based on file name or content
                if "integration" in str(file_data.get("file_path", "")).lower():
                    integration_tests += test_count
                else:
                    unit_tests += test_count
        
        return {
            "unit_tests": unit_tests,
            "integration_tests": integration_tests,
            "total": unit_tests + integration_tests
        }
    
    def _log_test_generation_success(self, test_suite: Dict, coverage_plan: Dict):
        """
        Log successful test generation metrics
        """
        test_counts = self._count_tests_in_suite(test_suite)
        
        print("🎉 Test Generation Success:")
        print(f"   📊 Total Tests: {test_counts['total']}")
        print(f"   🔧 Unit Tests: {test_counts['unit_tests']}")
        print(f"   🔗 Integration Tests: {test_counts['integration_tests']}")
        print(f"   🎯 Target Coverage: {self.coverage_target}%")
        print(f"   📈 Estimated Coverage: {self._estimate_actual_coverage(test_suite, coverage_plan)}")
        print(f"   ⏱️ Estimated Execution: {self._estimate_execution_time(test_suite)}")
