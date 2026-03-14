Feature: Project Management
  As an architect user
  I want to manage projects within a client
  So that I can track architecture work per engagement

  Background:
    Given a client named "Acme Corp" exists

  Scenario: Create a project
    When I create a project named "Cloud Migration" for the client
    Then the response status is 201
    And the project slug is "cloud-migration"
    And the project status is "draft"
    And the project cloud_providers is an empty array

  Scenario: Create a project with cloud providers
    When I create a project named "Hybrid Cloud" with cloud_providers ["aws", "nutanix"]
    Then the response status is 201
    And the project cloud_providers contains "aws" and "nutanix"

  Scenario: Reject duplicate project name per client
    Given the client has a project named "Cloud Migration"
    When I create a project named "Cloud Migration" for the client
    Then the response status is 409

  Scenario: Allow same project name for different clients
    Given a client named "Globex Inc" exists
    And "Acme Corp" has a project named "Cloud Migration"
    When I create a project named "Cloud Migration" for "Globex Inc"
    Then the response status is 201

  Scenario: List projects for a client
    Given the client has projects "Cloud Migration" and "DR Setup"
    When I list projects for the client
    Then the response status is 200
    And I receive 2 projects

  Scenario: Get a project by ID
    Given the client has a project named "Cloud Migration"
    When I get the project by its ID
    Then the response status is 200
    And the project name is "Cloud Migration"

  Scenario: Update project status
    Given the client has a project named "Cloud Migration"
    When I update the project status to "active"
    Then the response status is 200
    And the project status is "active"

  Scenario: Update project description
    Given the client has a project named "Cloud Migration"
    When I update the project description to "Migrate on-prem to AWS"
    Then the response status is 200
    And the project description is "Migrate on-prem to AWS"

  Scenario: Delete a project
    Given the client has a project named "Cloud Migration"
    When I delete the project
    Then the response status is 204
    And the project no longer exists
