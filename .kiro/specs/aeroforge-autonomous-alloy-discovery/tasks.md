# Implementation Plan: AeroForge Autonomous Multi-Agent Alloy Discovery System

## Overview

This implementation plan breaks down the AeroForge system into actionable Python development tasks following the phased approach: Infrastructure → Agent Construction → Deployment → Observability. The system uses Google's Agent Development Kit (ADK) with Gemini 3.1 Pro, integrating PyCALPHAD for thermodynamics and PyAnsys for FEA simulation. All tasks build incrementally, with early validation through code execution and testing.

## Phase 1: Infrastructure and Core Data Models

- [-] 1. Set up project structure and core dependencies
  - Create Python project with src/ directory structure
  - Set up pyproject.toml with core dependencies: google-genai, google-cloud-aiplatform, pycalphad, ansys-mapdl-core
  - Create requirements.txt for development dependencies: pytest, hypothesis, pytest-mock
  - Initialize .env.template for configuration (PROJECT_ID, LOCATION, VERTEX_DATA_STORE_ID)
  - _Requirements: 15.1, 15.2, 15.3_

- [ ] 2. Implement core data models with validation
  - [ ] 2.1 Create SessionState data model
    - Implement SessionState TypedDict with all required fields (initial_prompt, query_intent, research_plan, etc.)
    - Add validation function to ensure all values are JSON-serializable
    - Implement state initialization with default values
    - _Requirements: 7.1, 7.2, 7.3, 14.5_
  
  - [ ]* 2.2 Write property test for SessionState serializability
    - **Property 2: Session State Serializability**
    - **Validates: Requirements 7.2, 14.5**
    - Test that any valid session state can be serialized to JSON and deserialized without loss
  
  - [ ] 2.3 Create ResearchPlan, AlloyCandidate, ThermoResult, FEAResult data models
    - Implement ResearchPlan TypedDict with required_properties, suggested_elements, thermodynamic_constraints
    - Implement AlloyCandidate TypedDict with matrix and target_temp_K
    - Implement ThermoResult and FEAResult TypedDicts with all required fields
    - Add validation functions for each model (element symbols, positive temperatures, non-negative values)
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 18.1, 18.2, 18.3_
  
  - [ ]* 2.4 Write unit tests for data model validation
    - Test valid element symbol validation against periodic table
    - Test positive temperature validation
    - Test non-negative displacement and stress validation
    - Test phase fraction sum validation
    - _Requirements: 14.1, 14.2, 14.3, 14.4_

- [ ] 3. Checkpoint - Verify data models
  - Ensure all tests pass, ask the user if questions arise.

## Phase 2: Physics Simulation Tools

- [ ] 4. Implement PyCALPHAD thermodynamics tool
  - [ ] 4.1 Create calculate_phase_equilibrium function
    - Implement function signature: calculate_phase_equilibrium(elements, temperature, pressure, tdb_path) -> str
    - Load TDB database using pycalphad.Database
    - Configure equilibrium calculation with components and conditions
    - Execute Gibbs energy minimization using pycalphad.equilibrium
    - Extract stable phases and phase fractions from results
    - Return JSON string with thermodynamic assessment
    - Implement error handling for missing TDB files and calculation failures
    - _Requirements: 4.1, 4.2, 4.3, 4.7, 19.1, 19.3_
  
  - [ ]* 4.2 Write property test for thermodynamic calculation
    - **Property 4: Thermodynamic Stability Consistency**
    - **Validates: Requirements 4.3, 4.4**
    - Test that thermodynamic calculations always return valid JSON with required fields
    - Test that phase fractions sum to approximately 1.0
  
  - [ ] 4.3 Add TDB database management utilities
    - Create function to check for TDB files in multiple locations
    - Implement fallback logic for missing databases
    - Add support for Ti-Al-V, Ni-Cr-Co, Fe-Cr-Ni alloy systems
    - _Requirements: 19.1, 19.2, 19.3, 19.4_

- [ ] 5. Implement PyAnsys FEA simulation tool
  - [ ] 5.1 Create run_fea_analysis function
    - Implement function signature: run_fea_analysis(mesh_geometry, thermal_load, structural_load) -> str
    - Connect to Ansys MAPDL via ansys.mapdl.core.launch_mapdl
    - Define geometry using MAPDL preprocessor commands
    - Set material properties (elastic modulus, Poisson's ratio)
    - Generate mesh with SOLID185 elements
    - Apply boundary conditions (fixed constraints, loads)
    - Execute static structural analysis
    - Extract maximum displacement and von Mises stress from post-processing
    - Assess component survival against failure criteria
    - Return JSON string with FEA results
    - Implement proper MAPDL connection cleanup
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_
  
  - [ ] 5.2 Add analytical fallback for MAPDL connection failures
    - Implement simplified analytical estimation formulas
    - Return results with analytical_fallback flag
    - Log warnings when fallback is used
    - _Requirements: 6.8, 10.4_
  
  - [ ]* 5.3 Write property test for FEA result completeness
    - **Property 5: FEA Result Completeness**
    - **Validates: Requirements 6.7, 14.4**
    - Test that FEA results always contain all required fields
    - Test that displacement and stress values are non-negative

- [ ] 6. Checkpoint - Verify simulation tools
  - Ensure all tests pass, ask the user if questions arise.

## Phase 3: Agent Implementation

- [ ] 7. Implement base agent infrastructure
  - [ ] 7.1 Create BaseAgent abstract class
    - Define BaseAgent with name and thinking_level attributes
    - Add abstract methods for agent execution
    - Implement session state update helpers
    - _Requirements: 9.2, 9.3_
  
  - [ ] 7.2 Set up Google ADK integration
    - Configure google-genai client with API credentials
    - Implement Gemini 3.1 Pro model initialization with thinking levels
    - Add retry logic with exponential backoff for rate limiting
    - _Requirements: 10.5, 15.3_

- [ ] 8. Implement Discovery Branch agents
  - [ ] 8.1 Create DiscoveryLeadAgent (orchestrator)
    - Extend BaseAgent with thinking_level="low"
    - Implement dispatch method to parse user intent
    - Initialize session state with user prompt
    - Route to Research Agent by setting next_agent field
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 9.3_
  
  - [ ] 8.2 Create ResearchAgent with Vertex AI Search integration
    - Extend BaseAgent with thinking_level="medium"
    - Implement execute method to process query intent
    - Create query_vertex_search method for hybrid search
    - Configure Vertex AI Search client with data store ID
    - Execute hybrid search (keyword + semantic vector)
    - Parse OCR-extracted content from PDFs
    - Apply re-ranker for relevance scoring
    - Synthesize research plan with required properties, suggested elements, constraints
    - Implement fallback to default research plan if Vertex AI unavailable
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 10.2, 15.2_
  
  - [ ]* 8.3 Write property test for research plan validity
    - **Property 6: Research Plan Validity**
    - **Validates: Requirements 2.6, 14.1**
    - Test that research plans always contain non-empty suggested elements
    - Test that all element symbols are valid

- [ ] 9. Implement Composition Loop agents
  - [ ] 9.1 Create CompositionAgent (generator)
    - Extend BaseAgent with thinking_level="high"
    - Implement generate method to create alloy candidates
    - Analyze research plan constraints (required properties, suggested elements)
    - Use Gemini 3.1 Pro with high thinking level for complex physics reasoning
    - Generate AlloyCandidate with element matrix and target temperature
    - Validate element symbols against periodic table
    - Ensure target temperature is positive
    - Store proposed alloy in session state
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 18.1, 18.2, 18.3_
  
  - [ ] 9.2 Create CriticAgent (evaluator)
    - Extend BaseAgent with thinking_level="medium"
    - Implement evaluate method to validate alloy candidates
    - Extract proposed alloy from session state
    - Invoke calculate_phase_equilibrium tool
    - Assess phase stability against research plan constraints
    - Return boolean indicating pass/fail
    - Store validation results in session state
    - Provide rejection feedback for failed candidates
    - _Requirements: 4.1, 4.4, 4.5, 4.6_
  
  - [ ] 9.3 Implement run_composition_loop function
    - Create function with session_state and max_iterations parameters
    - Initialize CompositionAgent and CriticAgent
    - Implement generator-critic loop pattern
    - Alternate between generation and evaluation
    - Track loop iterations in session state
    - Terminate on successful validation and store final_formulation
    - Raise ValueError if max iterations reached without success
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_
  
  - [ ]* 9.4 Write property test for composition loop termination
    - **Property 3: Composition Loop Termination**
    - **Validates: Requirements 5.5, 5.6**
    - Test that loop always terminates within max_iterations
    - Test that successful termination produces valid final_formulation

- [ ] 10. Checkpoint - Verify agent implementation
  - Ensure all tests pass, ask the user if questions arise.

## Phase 4: Simulation Branch and Synthesis

- [ ] 11. Implement Simulation Branch agents
  - [ ] 11.1 Create SimulationLeadAgent (orchestrator)
    - Extend BaseAgent with thinking_level="low"
    - Implement dispatch method to route to FEA simulation
    - Prepare simulation parameters (geometry, loads, boundary conditions)
    - Extract final formulation from session state
    - Invoke run_fea_analysis tool
    - Store simulation results in session state
    - _Requirements: 6.1, 6.2, 9.3_
  
  - [ ]* 11.2 Write integration test for simulation pipeline
    - Test end-to-end flow from final formulation to simulation results
    - Verify session state updates correctly
    - _Requirements: 6.7, 16.5_

- [ ] 12. Implement multimodal presentation synthesis
  - [ ] 12.1 Create generate_svg_heatmap function
    - Extract simulation results from session state
    - Use Gemini 3.1 Pro for SVG code generation
    - Generate animated SVG with stress and displacement visualization
    - Implement fallback to static SVG if animation fails
    - Save SVG file to output directory
    - Return file path
    - _Requirements: 8.2, 8.3, 8.7, 20.1, 20.2, 20.3_
  
  - [ ] 12.2 Create generate_audio_briefing function
    - Synthesize multi-speaker audio briefing using Gemini TTS
    - Apply MultiSpeakerVoiceConfig for narrator variety
    - Implement fallback to text transcript if TTS fails
    - Save audio file to output directory
    - Return file path
    - _Requirements: 8.4, 8.5, 8.8, 20.4, 20.5_
  
  - [ ] 12.3 Create finalize_presentation function
    - Implement function signature: finalize_presentation(session_state, output_dir) -> tuple[str, str]
    - Call generate_svg_heatmap and generate_audio_briefing
    - Ensure output directory exists
    - Return tuple of (svg_path, audio_path)
    - _Requirements: 8.1, 8.6_
  
  - [ ]* 12.4 Write property test for multimodal output existence
    - **Property 8: Multimodal Output Existence**
    - **Validates: Requirements 8.6, 20.6**
    - Test that successful pipeline execution creates both SVG and audio files

- [ ] 13. Checkpoint - Verify synthesis layer
  - Ensure all tests pass, ask the user if questions arise.

## Phase 5: Main Pipeline Orchestration

- [ ] 14. Implement main pipeline workflow
  - [ ] 14.1 Create execute_pipeline function
    - Implement function signature: execute_pipeline(user_prompt) -> dict
    - Initialize session state with user prompt
    - Create agent instances (DiscoveryLead, Research, SimulationLead)
    - Execute Phase 1: Discovery Lead dispatch
    - Execute Phase 2: Research Agent with Vertex AI Search
    - Execute Phase 3: Composition Loop (generator-critic pattern)
    - Execute Phase 4: Simulation Lead dispatch and FEA
    - Execute Phase 5: Multimodal synthesis
    - Implement comprehensive error handling for each phase
    - Log pipeline progress at each stage
    - Return complete session state
    - _Requirements: 17.1, 17.2, 17.3_
  
  - [ ]* 14.2 Write property test for pipeline monotonic progress
    - **Property 7: Pipeline Monotonic Progress**
    - **Validates: Requirements 17.1, 17.2, 17.3**
    - Test that pipeline stages execute in correct order
    - Test that timestamps progress monotonically
  
  - [ ] 14.3 Add input validation for user prompts
    - Validate prompt length (max 1000 characters)
    - Sanitize inputs against injection patterns
    - Reject invalid inputs with error messages
    - _Requirements: 1.5, 12.5, 12.6_

- [ ] 15. Implement error handling and recovery
  - [ ] 15.1 Add retry logic with exponential backoff
    - Implement retry decorator for Vertex AI Search (3 attempts)
    - Implement retry decorator for Gemini API with backoff
    - Add rate limiting detection and handling
    - _Requirements: 10.2, 10.5_
  
  - [ ] 15.2 Add composition loop constraint relaxation
    - Implement optional constraint relaxation (10%) on loop exhaustion
    - Return best candidate from all iterations if all fail
    - Flag formulation as "unvalidated" in session state
    - _Requirements: 5.7, 10.6_
  
  - [ ] 15.3 Add session state validation and recovery
    - Implement state consistency checks at stage boundaries
    - Add state reconstruction from agent outputs
    - Implement checkpoint/restore mechanism
    - _Requirements: 7.6, 10.7, 10.8_
  
  - [ ]* 15.4 Write property test for error handling robustness
    - **Property 10: Error Handling Robustness**
    - **Validates: Requirements 10.7, 10.8**
    - Test that errors don't corrupt session state
    - Test that partial results are preserved

- [ ] 16. Checkpoint - Verify main pipeline
  - Ensure all tests pass, ask the user if questions arise.

## Phase 6: Security and Observability

- [ ] 17. Implement security controls
  - [ ] 17.1 Add VPC Service Controls configuration
    - Create VPC SC perimeter configuration
    - Configure restricted services (aiplatform, discoveryengine)
    - Set up ingress/egress policies
    - _Requirements: 12.1, 12.2_
  
  - [ ] 17.2 Configure IAM and service accounts
    - Create service account configurations for each agent type
    - Implement least privilege access patterns
    - Add credential rotation reminders
    - _Requirements: 12.2, 12.3_
  
  - [ ] 17.3 Add data encryption and retention policies
    - Configure Cloud KMS for session state encryption
    - Implement TLS 1.3 for inter-service communication
    - Add 90-day retention policy for session state
    - _Requirements: 12.3, 12.4, 12.7_

- [ ] 18. Implement observability and monitoring
  - [ ] 18.1 Add Cloud Trace integration
    - Instrument agents with trace spans
    - Track latency for each pipeline stage
    - Add trace context propagation
    - _Requirements: 13.1, 13.3_
  
  - [ ] 18.2 Add structured logging
    - Implement logging for agent decisions and rationale
    - Log error stack traces with session state snapshots
    - Add audit logging for data access
    - _Requirements: 13.2, 13.4, 12.8_
  
  - [ ] 18.3 Add performance monitoring
    - Track API call rates and quota usage
    - Monitor for rate limiting and unusual patterns
    - Add alerting for performance degradation
    - _Requirements: 13.5, 13.6_

- [ ] 19. Checkpoint - Verify security and observability
  - Ensure all tests pass, ask the user if questions arise.

## Phase 7: Integration Testing and Validation

- [ ] 20. Implement comprehensive integration tests
  - [ ]* 20.1 Write end-to-end pipeline integration test
    - Test full pipeline with mocked external services
    - Verify session state propagation across all agents
    - Test error propagation and recovery
    - _Requirements: 16.5_
  
  - [ ]* 20.2 Write agent hierarchy validation test
    - **Property 1: Agent Hierarchy Integrity**
    - **Validates: Requirements 9.1, 9.6**
    - Test that no agent has multiple parents
    - Test that no cycles exist in agent graph
  
  - [ ]* 20.3 Write property test for thinking level appropriateness
    - **Property 9: Thinking Level Appropriateness**
    - **Validates: Requirements 9.3, 9.4, 9.5**
    - Test that orchestrators use low thinking level
    - Test that critics use medium thinking level
    - Test that generators use high thinking level
  
  - [ ]* 20.4 Write performance benchmark tests
    - Test discovery phase completes within 10-15s
    - Test composition loop completes within 15-30s
    - Test FEA simulation completes within 30-60s
    - Test full pipeline completes within 60-115s
    - _Requirements: 11.1, 11.2, 11.3, 11.5_

- [ ] 21. Create example usage and documentation
  - [ ] 21.1 Create example scripts
    - Write example for basic pipeline execution
    - Write example for individual component usage
    - Write example for direct tool usage
    - Write example for composition loop with custom iterations
    - Write example for multimodal synthesis
    - _Requirements: 16.1_
  
  - [ ] 21.2 Create README with setup instructions
    - Document installation steps
    - Document configuration requirements
    - Document API credentials setup
    - Document TDB database setup
    - Document Ansys MAPDL setup

- [ ] 22. Final checkpoint - Complete system validation
  - Run all unit tests and verify 85% coverage for core logic
  - Run all property-based tests
  - Run all integration tests
  - Execute example scripts to verify end-to-end functionality
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation throughout implementation
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- The implementation follows the phased approach: Infrastructure → Agents → Simulation → Synthesis → Integration
- Python is used throughout with type hints for clarity and IDE support
- All external service dependencies (Vertex AI, PyCALPHAD, PyAnsys) are properly abstracted for testing
