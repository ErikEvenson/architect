Feature: Diagram Rendering
  As an architect user
  I want to render diagram source code into visual outputs
  So that I can generate architecture diagrams from code

  Background:
    Given a client named "Acme Corp" exists
    And the client has a project named "Cloud Migration"
    And the project has version "1.0.0"

  Scenario: Trigger render for a diagrams_py artifact
    Given an artifact with engine "diagrams_py" and valid source code
    When I trigger a render for the artifact
    Then the response status is 202
    And the artifact render_status is "rendering"

  Scenario: Successful render produces output files
    Given an artifact with engine "diagrams_py" and valid source code
    When I trigger a render and wait for completion
    Then the artifact render_status is "success"
    And the artifact output_paths contains an SVG file
    And the artifact output_paths contains a PNG file

  Scenario: Retrieve rendered SVG output
    Given an artifact with a successful render
    When I request the SVG output file
    Then the response status is 200
    And the content type is "image/svg+xml"

  Scenario: Retrieve rendered PNG output
    Given an artifact with a successful render
    When I request the PNG output file
    Then the response status is 200
    And the content type is "image/png"

  Scenario: Render fails with invalid Python source
    Given an artifact with engine "diagrams_py" and invalid source code
    When I trigger a render and wait for completion
    Then the artifact render_status is "error"
    And the artifact render_error contains an error message

  Scenario: Render fails with missing show=False
    Given an artifact with engine "diagrams_py" and source missing "show=False"
    When I attempt to validate the source
    Then validation returns an error about show=False

  Scenario: Render fails on timeout
    Given an artifact with engine "diagrams_py" and source that hangs
    When I trigger a render with a short timeout
    Then the artifact render_status is "error"
    And the artifact render_error mentions timeout

  Scenario: Render artifact with no source code
    Given an artifact with engine "diagrams_py" and no source code
    When I attempt to trigger a render
    Then the response status is 400
    And the error mentions missing source code

  Scenario: Output files stored in correct directory structure
    Given an artifact with a successful render
    Then the output files are stored under "{client_slug}/{project_slug}/{version_number}/{artifact_id}/"
