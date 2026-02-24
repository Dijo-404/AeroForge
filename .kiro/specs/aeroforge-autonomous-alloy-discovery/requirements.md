# Requirements Document: AeroForge Autonomous Multi-Agent Alloy Discovery System

## Introduction

AeroForge is an AI-driven materials design system that automates the discovery, formulation, and validation of aerospace alloys. The system enables materials scientists and aerospace engineers to rapidly explore alloy compositions through automated literature synthesis, thermodynamic validation, and high-fidelity finite element analysis. By integrating Google's Agent Development Kit with physics-based simulation tools (PyCALPHAD, PyAnsys), the system reduces alloy development cycles from months to minutes while maintaining rigorous scientific validation.

## Glossary

- **System**: The AeroForge autonomous multi-agent alloy discovery system
- **Discovery_Branch**: The subsystem responsible for literature research and alloy formulation
- **Simulation_Branch**: The subsystem responsible for thermodynamic and FEA validation
- **Discovery_Lead**: The orchestrator agent that routes user requests to specialized sub-agents
- **Research_Agent**: The agent that queries scientific literature via Vertex AI Search
- **Composition_Agent**: The generator agent that creates candidate alloy formulations
- **Critic_Agent**: The evaluator agent that validates alloy candidates against thermodynamic constraints
- **Simulation_Lead**: The orchestrator agent that routes validated alloys to simulation tools
- **Session_State**: The shared data structure for inter-agent communication
- **Alloy_Candidate**: A proposed alloy composition with element matrix and target temperature
- **Research_Plan**: Synthesized constraints and element suggestions from literature
- **TDB_Database**: Thermodynamic database file in CALPHAD format
- **FEA**: Finite Element Analysis for structural and thermal validation
- **MAPDL**: Ansys Mechanical APDL solver for FEA simulations
- **Vertex_AI_Search**: Google's RAG framework for scientific literature retrieval
- **PyCALPHAD**: Python library for thermodynamic phase equilibrium calculations
- **Gemini**: Google's large language model (Gemini 3.1 Pro) powering agent reasoning
- **Thinking_Level**: Configuration parameter controlling agent reasoning depth (low/medium/high)
- **Multimodal_Reporter**: The synthesis component that generates presentation assets
- **User**: Materials scientist or aerospace engineer using the system

## Requirements

### Requirement 1: User Intent Processing and Routing

**User Story:** As a materials scientist, I want to submit natural language alloy requirements, so that the system can automatically route my request to appropriate discovery workflows.

#### Acceptance Criteria

1. WHEN a User submits a natural language prompt, THE Discovery_Lead SHALL parse the intent and extract alloy requirements
2. WHEN the Discovery_Lead processes a user prompt, THE Discovery_Lead SHALL initialize Session_State with the original request
3. WHEN intent analysis is complete, THE Discovery_Lead SHALL route the request to the Research_Agent
4. WHEN routing decisions are made, THE Discovery_Lead SHALL use low Thinking_Level for fast response times
5. WHEN the user prompt exceeds 1000 characters, THE System SHALL reject the input and return an error message

### Requirement 2: Scientific Literature Research and Synthesis

**User Story:** As a materials scientist, I want the system to automatically search relevant scientific literature, so that alloy formulations are grounded in published research.

#### Acceptance Criteria

1. WHEN the Research_Agent receives a query intent, THE Research_Agent SHALL construct optimized search queries for Vertex_AI_Search
2. WHEN querying literature, THE Research_Agent SHALL execute hybrid search combining keyword and semantic vector search
3. WHEN scientific PDFs are retrieved, THE Research_Agent SHALL parse OCR-extracted content including tables and formulas
4. WHEN search results are returned, THE Research_Agent SHALL apply re-ranking for relevance scoring
5. WHEN literature synthesis is complete, THE Research_Agent SHALL generate a Research_Plan containing required properties, suggested elements, and thermodynamic constraints
6. WHEN the Research_Plan is created, THE Research_Agent SHALL ensure suggested_elements is a non-empty list of valid chemical symbols
7. IF Vertex_AI_Search is unavailable, THEN THE Research_Agent SHALL fall back to a default research plan with common aerospace alloy elements

### Requirement 3: Alloy Composition Generation

**User Story:** As a materials scientist, I want the system to generate candidate alloy compositions using domain knowledge, so that I can explore novel formulations based on research constraints.

#### Acceptance Criteria

1. WHEN the Composition_Agent receives a Research_Plan, THE Composition_Agent SHALL analyze constraints including required properties and suggested elements
2. WHEN generating candidates, THE Composition_Agent SHALL use high Thinking_Level for complex physics reasoning
3. WHEN a candidate is generated, THE Composition_Agent SHALL produce an Alloy_Candidate with element matrix and target temperature
4. WHEN creating the element matrix, THE Composition_Agent SHALL use only valid chemical symbols from the periodic table
5. WHEN setting target temperature, THE Composition_Agent SHALL ensure the value is positive and expressed in Kelvin
6. WHEN the Alloy_Candidate is complete, THE Composition_Agent SHALL store it in Session_State as proposed_alloy

### Requirement 4: Thermodynamic Validation

**User Story:** As a materials scientist, I want alloy candidates validated against thermodynamic principles, so that only stable compositions proceed to expensive simulations.

#### Acceptance Criteria

1. WHEN the Critic_Agent receives a proposed alloy, THE Critic_Agent SHALL invoke PyCALPHAD for phase equilibrium calculation
2. WHEN calculating phase equilibrium, THE System SHALL load the appropriate TDB_Database for the alloy system
3. WHEN thermodynamic calculation completes, THE System SHALL return stable phases and phase fractions
4. WHEN the Critic_Agent evaluates stability, THE Critic_Agent SHALL assess results against Research_Plan constraints
5. WHEN an alloy passes validation, THE Critic_Agent SHALL return True and store validation results in Session_State
6. WHEN an alloy fails validation, THE Critic_Agent SHALL return False and provide rejection feedback
7. IF the TDB_Database is missing or corrupted, THEN THE System SHALL return is_stable as False with an error description

### Requirement 5: Generator-Critic Loop for Iterative Refinement

**User Story:** As a materials scientist, I want the system to iteratively refine alloy candidates, so that thermodynamically stable formulations are discovered efficiently.

#### Acceptance Criteria

1. WHEN the composition loop starts, THE System SHALL set a maximum iteration limit
2. WHILE the loop is active, THE System SHALL alternate between Composition_Agent generation and Critic_Agent evaluation
3. WHEN a candidate passes Critic_Agent validation, THE System SHALL store it as final_formulation and terminate the loop
4. WHEN a candidate fails validation, THE System SHALL increment loop_iterations and generate a new candidate
5. WHEN loop_iterations reaches the maximum limit without success, THE System SHALL raise a ValueError with iteration count
6. WHEN the loop terminates successfully, THE System SHALL ensure final_formulation passed thermodynamic validation
7. IF maximum iterations are reached, THEN THE System SHALL optionally relax constraints by 10 percent and retry

### Requirement 6: Finite Element Analysis Simulation

**User Story:** As an aerospace engineer, I want validated alloy candidates tested under realistic structural and thermal loads, so that I can assess component survival in operational conditions.

#### Acceptance Criteria

1. WHEN the Simulation_Lead receives a final formulation, THE Simulation_Lead SHALL prepare simulation parameters including geometry, loads, and boundary conditions
2. WHEN FEA simulation starts, THE System SHALL connect to MAPDL via gRPC
3. WHEN the mesh is generated, THE System SHALL define material properties derived from the alloy composition
4. WHEN boundary conditions are applied, THE System SHALL fix root attachment points and apply structural and thermal loads
5. WHEN the simulation solves, THE System SHALL extract maximum displacement and von Mises stress values
6. WHEN results are extracted, THE System SHALL assess component survival against failure criteria
7. WHEN the simulation completes, THE System SHALL return results including max_displacement_mm, von_mises_stress_MPa, thermal_gradient_K, survived, and failure_mode
8. IF MAPDL connection fails, THEN THE System SHALL fall back to analytical estimation using simplified formulas

### Requirement 7: Session State Management

**User Story:** As a system architect, I want all agents to communicate through shared session state, so that data consistency is maintained across the pipeline.

#### Acceptance Criteria

1. WHEN the pipeline initializes, THE System SHALL create Session_State with required keys
2. WHEN agents update Session_State, THE System SHALL ensure all values are serializable to JSON
3. WHEN Session_State is modified, THE System SHALL preserve data consistency across agent boundaries
4. WHEN an agent completes its task, THE System SHALL update the next_agent routing field
5. WHEN Session_State contains proposed_alloy, THE System SHALL validate that matrix is non-empty and target_temp_K is positive
6. IF Session_State becomes corrupted, THEN THE System SHALL log an error and attempt reconstruction from agent outputs

### Requirement 8: Multimodal Presentation Generation

**User Story:** As a materials scientist, I want simulation results presented as visual heatmaps and audio briefings, so that I can quickly understand alloy performance.

#### Acceptance Criteria

1. WHEN simulation results are available, THE Multimodal_Reporter SHALL extract data from Session_State
2. WHEN generating visualizations, THE Multimodal_Reporter SHALL create animated SVG heatmaps showing stress and displacement
3. WHEN creating SVG files, THE Multimodal_Reporter SHALL use Gemini for code generation
4. WHEN synthesizing audio, THE Multimodal_Reporter SHALL generate multi-speaker briefings using text-to-speech
5. WHEN presentation assets are complete, THE Multimodal_Reporter SHALL save files to the specified output directory
6. WHEN the synthesis completes, THE Multimodal_Reporter SHALL return file paths for SVG and audio assets
7. IF SVG generation fails, THEN THE System SHALL generate a static SVG without animations
8. IF audio synthesis fails, THEN THE System SHALL create a text transcript instead

### Requirement 9: Agent Hierarchy and Orchestration

**User Story:** As a system architect, I want agents organized in a clear hierarchy with single-parent relationships, so that the system is maintainable and follows ADK best practices.

#### Acceptance Criteria

1. THE System SHALL ensure each agent has at most one parent in the hierarchy
2. WHEN agents are initialized, THE System SHALL configure thinking levels appropriate to their roles
3. WHEN orchestrator agents execute, THE System SHALL use low Thinking_Level for fast routing
4. WHEN critic agents execute, THE System SHALL use medium Thinking_Level for validation reasoning
5. WHEN generator agents execute, THE System SHALL use high Thinking_Level for complex domain reasoning
6. WHEN the hierarchy is validated, THE System SHALL ensure no cycles exist in the agent graph

### Requirement 10: Error Handling and Recovery

**User Story:** As a materials scientist, I want the system to handle errors gracefully, so that partial results are preserved and I understand what went wrong.

#### Acceptance Criteria

1. WHEN an error occurs in any agent, THE System SHALL log the error with detailed context
2. WHEN Vertex_AI_Search is unavailable, THE System SHALL retry with exponential backoff up to 3 attempts
3. WHEN PyCALPHAD calculations fail, THE System SHALL return error information in JSON format
4. WHEN MAPDL connection fails, THE System SHALL fall back to analytical estimation
5. WHEN Gemini API rate limiting occurs, THE System SHALL implement exponential backoff and reduce thinking levels
6. WHEN the composition loop exhausts iterations, THE System SHALL return the best candidate from all attempts
7. WHEN errors are handled, THE System SHALL ensure Session_State remains consistent and uncorrupted
8. WHEN partial results are available, THE System SHALL return them with appropriate warning flags

### Requirement 11: Performance and Scalability

**User Story:** As a system administrator, I want the system to complete alloy discovery pipelines within 2 minutes, so that materials scientists can iterate rapidly.

#### Acceptance Criteria

1. WHEN the discovery phase executes, THE System SHALL complete within 10 to 15 seconds
2. WHEN the composition loop executes, THE System SHALL complete within 15 to 30 seconds for average cases
3. WHEN FEA simulation executes with coarse mesh, THE System SHALL complete within 30 to 60 seconds
4. WHEN the synthesis phase executes, THE System SHALL complete within 5 to 10 seconds
5. WHEN the full pipeline executes, THE System SHALL complete within 60 to 115 seconds
6. WHEN multiple pipelines execute concurrently, THE System SHALL support 10 to 20 concurrent executions
7. WHEN thermodynamic calculations are repeated, THE System SHALL use cached results to improve performance

### Requirement 12: Security and Access Control

**User Story:** As a security administrator, I want sensitive research data and alloy formulations protected, so that proprietary information remains confidential.

#### Acceptance Criteria

1. WHEN services are deployed, THE System SHALL operate within VPC Service Controls perimeter
2. WHEN agents access external services, THE System SHALL use service accounts with least privilege
3. WHEN Session_State is stored, THE System SHALL encrypt data at rest using Cloud KMS
4. WHEN inter-service communication occurs, THE System SHALL use TLS 1.3 encryption
5. WHEN user inputs are received, THE System SHALL validate against whitelist patterns to prevent injection attacks
6. WHEN element symbols are processed, THE System SHALL sanitize inputs against the periodic table
7. WHEN data is retained, THE System SHALL implement 90-day retention policies for Session_State
8. WHEN security events occur, THE System SHALL log all data access via Cloud Audit Logs

### Requirement 13: Observability and Monitoring

**User Story:** As a system administrator, I want comprehensive logging and tracing, so that I can monitor system health and debug issues.

#### Acceptance Criteria

1. WHEN agents execute, THE System SHALL trace requests using Cloud Trace
2. WHEN agent decisions are made, THE System SHALL log decision rationale for audit trails
3. WHEN performance metrics are collected, THE System SHALL track latency for each pipeline stage
4. WHEN errors occur, THE System SHALL capture stack traces and session state snapshots
5. WHEN unusual patterns are detected, THE System SHALL alert administrators
6. WHEN API calls are made, THE System SHALL monitor for rate limiting and quota exhaustion

### Requirement 14: Data Validation and Integrity

**User Story:** As a materials scientist, I want all data validated at component boundaries, so that invalid data is caught early and doesn't propagate through the pipeline.

#### Acceptance Criteria

1. WHEN Research_Plan is created, THE System SHALL validate that suggested_elements contains only valid chemical symbols
2. WHEN Alloy_Candidate is generated, THE System SHALL validate that target_temp_K is a positive number
3. WHEN thermodynamic results are returned, THE System SHALL validate that phase fractions sum to approximately 1.0
4. WHEN FEA results are returned, THE System SHALL validate that displacement and stress values are non-negative
5. WHEN Session_State is serialized, THE System SHALL validate that all values are JSON-serializable
6. IF validation fails at any stage, THEN THE System SHALL reject the data and log a detailed error

### Requirement 15: Integration with External Services

**User Story:** As a system architect, I want seamless integration with Google Cloud services and physics simulation tools, so that the system leverages best-in-class capabilities.

#### Acceptance Criteria

1. WHEN the System initializes, THE System SHALL connect to Vertex AI Agent Engine for agent deployment
2. WHEN literature search is needed, THE System SHALL query Vertex_AI_Search with hybrid search enabled
3. WHEN agent reasoning is required, THE System SHALL invoke Gemini 3.1 Pro API with appropriate thinking levels
4. WHEN thermodynamic calculations are needed, THE System SHALL invoke PyCALPHAD with the appropriate TDB_Database
5. WHEN FEA simulation is needed, THE System SHALL connect to MAPDL via gRPC or Private Service Connect
6. WHEN presentation assets are stored, THE System SHALL use Cloud Storage for persistence
7. IF any external service is unavailable, THEN THE System SHALL implement appropriate fallback strategies

### Requirement 16: Testing and Validation

**User Story:** As a developer, I want comprehensive test coverage, so that the system behaves correctly under all conditions.

#### Acceptance Criteria

1. THE System SHALL include unit tests for all agent dispatch logic and state updates
2. THE System SHALL include property-based tests for session state serializability
3. THE System SHALL include property-based tests for composition loop termination
4. THE System SHALL include property-based tests for thermodynamic consistency
5. THE System SHALL include integration tests for end-to-end pipeline execution
6. THE System SHALL achieve 85 percent test coverage for core logic
7. THE System SHALL achieve 70 percent test coverage for integration points

### Requirement 17: Pipeline Execution Ordering

**User Story:** As a materials scientist, I want the pipeline to execute stages in the correct order, so that each stage has the data it needs from previous stages.

#### Acceptance Criteria

1. WHEN the pipeline executes, THE System SHALL progress through stages in order: discovery, research, composition, simulation, synthesis
2. WHEN a stage completes, THE System SHALL ensure the next stage does not start until required data is available
3. WHEN timestamps are recorded, THE System SHALL ensure each stage timestamp is later than the previous stage
4. IF a stage fails, THEN THE System SHALL not proceed to subsequent stages

### Requirement 18: Alloy Composition Constraints

**User Story:** As a materials scientist, I want alloy compositions constrained to physically valid ranges, so that generated candidates are realistic.

#### Acceptance Criteria

1. WHEN element matrices are generated, THE System SHALL ensure all elements are valid chemical symbols
2. WHEN concentrations are specified, THE System SHALL ensure values are between 0 and 100 percent
3. WHEN temperature is specified, THE System SHALL ensure values are positive and expressed in Kelvin
4. WHEN pressure is specified, THE System SHALL ensure values are positive and expressed in Pascals
5. IF invalid compositions are generated, THEN THE Critic_Agent SHALL reject them with specific feedback

### Requirement 19: Thermodynamic Database Management

**User Story:** As a system administrator, I want thermodynamic databases managed and accessible, so that phase equilibrium calculations have the data they need.

#### Acceptance Criteria

1. WHEN PyCALPHAD is invoked, THE System SHALL load the appropriate TDB_Database for the alloy system
2. WHEN TDB files are needed, THE System SHALL support common aerospace alloy systems including Ti-Al-V, Ni-Cr-Co, and Fe-Cr-Ni
3. WHEN a TDB_Database is missing, THE System SHALL check alternative locations before failing
4. WHEN TDB files are stored, THE System SHALL use Cloud Storage for centralized access
5. IF no TDB_Database is available, THEN THE System SHALL skip thermodynamic validation and flag results with a warning

### Requirement 20: Presentation Asset Quality

**User Story:** As a materials scientist, I want high-quality presentation assets, so that I can effectively communicate results to stakeholders.

#### Acceptance Criteria

1. WHEN SVG heatmaps are generated, THE System SHALL include stress and displacement visualizations
2. WHEN SVG files are created, THE System SHALL ensure valid SVG markup and proper rendering
3. WHEN animations are included, THE System SHALL ensure smooth transitions and clear labeling
4. WHEN audio briefings are generated, THE System SHALL use multi-speaker voice configuration for variety
5. WHEN text-to-speech is used, THE System SHALL ensure clear pronunciation of technical terms
6. WHEN presentation files are saved, THE System SHALL ensure they are readable and properly formatted
