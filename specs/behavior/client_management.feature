Feature: Client Management
  As an architect user
  I want to manage clients
  So that I can organize architecture projects by client

  Scenario: Create a client
    When I create a client with name "Acme Corp"
    Then the response status is 201
    And the client has a generated UUID
    And the client slug is "acme-corp"
    And the client metadata is an empty object

  Scenario: Create a client with metadata
    When I create a client with name "Acme Corp" and metadata {"industry": "tech"}
    Then the response status is 201
    And the client metadata contains "industry" = "tech"

  Scenario: Reject duplicate client name
    Given a client named "Acme Corp" exists
    When I create a client with name "Acme Corp"
    Then the response status is 409

  Scenario: List all clients
    Given clients "Acme Corp" and "Globex Inc" exist
    When I list all clients
    Then the response status is 200
    And I receive 2 clients

  Scenario: Get a client by ID
    Given a client named "Acme Corp" exists
    When I get the client by its ID
    Then the response status is 200
    And the client name is "Acme Corp"

  Scenario: Get a non-existent client
    When I get a client with a random UUID
    Then the response status is 404

  Scenario: Update a client name
    Given a client named "Acme Corp" exists
    When I update the client name to "Acme Corporation"
    Then the response status is 200
    And the client name is "Acme Corporation"
    And the client slug is "acme-corporation"

  Scenario: Update client metadata
    Given a client named "Acme Corp" exists
    When I update the client metadata to {"industry": "finance"}
    Then the response status is 200
    And the client metadata contains "industry" = "finance"

  Scenario: Delete a client
    Given a client named "Acme Corp" exists
    When I delete the client
    Then the response status is 204
    And the client no longer exists

  Scenario: Delete a client cascades to projects
    Given a client named "Acme Corp" exists
    And the client has a project named "Cloud Migration"
    When I delete the client
    Then the response status is 204
    And the project no longer exists
