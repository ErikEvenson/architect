Feature: PDF Export
  As an architect user
  I want to export a version as a professional PDF report
  So that I can share architecture documentation with stakeholders

  Background:
    Given a client named "Acme Corp" exists
    And the client has a project named "Cloud Migration"
    And the project has version "1.0.0"

  Scenario: Create a PDF report artifact
    When I create an artifact with type "pdf_report" and engine "weasyprint"
    Then the artifact appears in the artifact list

  Scenario: Export version as PDF
    Given the version has diagram and document artifacts
    When I trigger a render of the PDF report artifact
    Then the artifact render_status is "success"
    And the output_paths contains "report.pdf"

  Scenario: PDF includes cover page
    Given a successfully rendered PDF report
    Then the PDF contains the project name "Cloud Migration"
    And the PDF contains the client name "Acme Corp"
    And the PDF contains the version number "1.0.0"

  Scenario: PDF includes table of contents
    Given a version with multiple artifacts
    And a successfully rendered PDF report
    Then the PDF contains a table of contents with artifact names

  Scenario: PDF embeds diagrams
    Given a diagram artifact with a successful SVG render
    And a successfully rendered PDF report
    Then the PDF contains the embedded diagram

  Scenario: Download PDF
    Given a successfully rendered PDF report
    When I request the PDF output file
    Then the response status is 200
    And the content type is "application/pdf"

  Scenario: PDF with no sibling artifacts
    Given a version with only a PDF report artifact
    When I trigger a render
    Then the PDF is generated with a warning about no content
