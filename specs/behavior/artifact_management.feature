Feature: Artifact Management
  As an architect user
  I want to manage artifacts within a version
  So that I can create, edit, render, and view architecture diagrams and documents

  Background:
    Given a client named "Acme Corp" exists
    And the client has a project named "Cloud Migration"
    And the project has version "1.0.0"

  Scenario: Create a diagram artifact
    When I create an artifact named "VPC Diagram" with type "diagram" and engine "diagrams_py"
    Then the artifact appears in the artifact list
    And the artifact detail_level is "conceptual"
    And the artifact render_status is "pending"

  Scenario: Filter artifacts by detail level
    Given artifacts exist at all four detail levels
    When I filter by detail level "deployment"
    Then only deployment-level artifacts are shown

  Scenario: Edit artifact source code
    Given an artifact named "VPC Diagram" exists
    When I edit the source code in the code editor
    And I save the artifact
    Then the source code is updated

  Scenario: Trigger render from artifact view
    Given an artifact with source code
    When I click the render button
    Then the render status indicator shows "rendering"
    And when rendering completes the status shows "success"

  Scenario: View rendered diagram
    Given an artifact with a successful render
    When I view the artifact
    Then the diagram viewer displays the SVG output
    And pan/zoom controls are available

  Scenario: View render error
    Given an artifact with a failed render
    When I view the artifact
    Then the render error message is displayed

  Scenario: Delete an artifact
    Given an artifact named "VPC Diagram" exists
    When I delete the artifact
    Then it is removed from the artifact list

  Scenario: Create artifact with D2 engine
    When I create an artifact named "Network Topology" with type "diagram" and engine "d2"
    Then the code editor shows D2 syntax highlighting

  Scenario: Fullscreen diagram viewer
    Given an artifact with a successful render
    When I click the fullscreen button on the diagram viewer
    Then the diagram is shown in fullscreen mode
