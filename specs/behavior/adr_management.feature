Feature: ADR Management
  As an architect user
  I want to manage Architectural Decision Records per project
  So that design decisions are documented with context and consequences

  Background:
    Given a client named "Acme Corp" exists
    And the client has a project named "Cloud Migration"

  Scenario: Create an ADR
    When I create an ADR with title "Use PostgreSQL" and context "Need relational DB" and decision "PostgreSQL 16" and consequences "Team needs PG experience"
    Then the response status is 201
    And the ADR number is 1
    And the ADR status is "proposed"

  Scenario: ADR numbers are sequential per project
    Given the project has an ADR titled "Use PostgreSQL"
    When I create an ADR with title "Use Kubernetes"
    Then the response status is 201
    And the ADR number is 2

  Scenario: ADR numbers are independent per project
    Given the project has an ADR titled "Use PostgreSQL"
    And a second project "DR Setup" exists for the client
    When I create an ADR with title "Use S3" for project "DR Setup"
    Then the response status is 201
    And the ADR number is 1

  Scenario: List ADRs for a project
    Given the project has ADRs "Use PostgreSQL" and "Use Kubernetes"
    When I list ADRs for the project
    Then the response status is 200
    And I receive 2 ADRs

  Scenario: Get an ADR by ID
    Given the project has an ADR titled "Use PostgreSQL"
    When I get the ADR by its ID
    Then the response status is 200
    And the ADR title is "Use PostgreSQL"

  Scenario: Update ADR status
    Given the project has an ADR titled "Use PostgreSQL"
    When I update the ADR status to "accepted"
    Then the response status is 200
    And the ADR status is "accepted"

  Scenario: Supersede an ADR
    Given the project has an ADR titled "Use MySQL" with status "accepted"
    When I supersede the ADR with title "Use PostgreSQL" and context "MySQL lacks features" and decision "Switch to PostgreSQL" and consequences "Migration needed"
    Then the response status is 201
    And the new ADR number is 2
    And the new ADR status is "proposed"
    And the original ADR status is "superseded"
    And the original ADR superseded_by points to the new ADR

  Scenario: Update ADR content
    Given the project has an ADR titled "Use PostgreSQL"
    When I update the ADR context to "Need JSONB support"
    Then the response status is 200
    And the ADR context is "Need JSONB support"
