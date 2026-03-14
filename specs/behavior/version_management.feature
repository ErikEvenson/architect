Feature: Version Management
  As an architect user
  I want to manage versions within a project
  So that I can track architecture evolution over time

  Background:
    Given a client named "Acme Corp" exists
    And the client has a project named "Cloud Migration"

  Scenario: Create a version
    When I create a version "1.0.0" for the project
    Then the response status is 201
    And the version status is "draft"

  Scenario: Create a version with label and notes
    When I create a version "1.0.0" with label "Initial" and notes "First draft"
    Then the response status is 201
    And the version label is "Initial"
    And the version notes is "First draft"

  Scenario: Reject duplicate version number per project
    Given the project has version "1.0.0"
    When I create a version "1.0.0" for the project
    Then the response status is 409

  Scenario: List versions for a project
    Given the project has versions "1.0.0" and "2.0.0"
    When I list versions for the project
    Then the response status is 200
    And I receive 2 versions

  Scenario: Get a version by ID
    Given the project has version "1.0.0"
    When I get the version by its ID
    Then the response status is 200
    And the version number is "1.0.0"

  Scenario: Update version status
    Given the project has version "1.0.0"
    When I update the version status to "review"
    Then the response status is 200
    And the version status is "review"

  Scenario: Update version label
    Given the project has version "1.0.0"
    When I update the version label to "Final Draft"
    Then the response status is 200
    And the version label is "Final Draft"
