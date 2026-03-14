Feature: Document Rendering
  As an architect user
  I want to create and render markdown documents
  So that I can produce formatted architecture documentation

  Background:
    Given a client named "Acme Corp" exists
    And the client has a project named "Cloud Migration"
    And the project has version "1.0.0"

  Scenario: Create a document artifact
    When I create an artifact named "Architecture Doc" with type "document" and engine "markdown"
    Then the artifact appears in the artifact list
    And the artifact render_status is "pending"

  Scenario: Render markdown to HTML
    Given a document artifact with markdown source
    When I trigger a render
    Then the artifact render_status is "success"
    And the output_paths contains "document.html"

  Scenario: Render markdown with diagram reference
    Given a diagram artifact with a successful render
    And a document artifact referencing that diagram
    When I trigger a render of the document
    Then the output HTML contains the embedded diagram

  Scenario: Render markdown with table
    Given a document artifact with a markdown table
    When I trigger a render
    Then the output HTML contains a styled table

  Scenario: Create document from template
    When I create a document from the "architecture" template
    Then the source code contains section headings

  Scenario: View rendered document
    Given a document artifact with a successful render
    When I request the HTML output
    Then the response content type is "text/html"
    And the HTML has inline styling
