Feature: Question Tracking
  As an architect user
  I want to track clarifying questions per project
  So that missing requirements are identified and resolved

  Background:
    Given a client named "Acme Corp" exists
    And the client has a project named "Cloud Migration"

  Scenario: Create a question
    When I create a question "What is the RPO requirement?"
    Then the response status is 201
    And the question status is "open"
    And the question category is "requirements"

  Scenario: Create a question with category
    When I create a question "What compliance standards apply?" with category "compliance"
    Then the response status is 201
    And the question category is "compliance"

  Scenario: List questions for a project
    Given the project has questions "What is the RPO?" and "What is the RTO?"
    When I list questions for the project
    Then the response status is 200
    And I receive 2 questions

  Scenario: Filter questions by status
    Given the project has an open question "What is the RPO?"
    And the project has an answered question "What is the budget?"
    When I list questions with status "open"
    Then the response status is 200
    And I receive 1 question
    And the question text is "What is the RPO?"

  Scenario: Filter questions by category
    Given the project has a question "What is the RPO?" with category "requirements"
    And the project has a question "What about PCI?" with category "compliance"
    When I list questions with category "compliance"
    Then the response status is 200
    And I receive 1 question

  Scenario: Answer a question
    Given the project has an open question "What is the RPO?"
    When I update the question with answer "4 hours" and status "answered"
    Then the response status is 200
    And the question answer is "4 hours"
    And the question status is "answered"

  Scenario: Defer a question
    Given the project has an open question "What is the RPO?"
    When I update the question status to "deferred"
    Then the response status is 200
    And the question status is "deferred"

  Scenario: Get a question by ID
    Given the project has a question "What is the RPO?"
    When I get the question by its ID
    Then the response status is 200
    And the question text is "What is the RPO?"

  Scenario: Change question category
    Given the project has a question "What is the RPO?" with category "requirements"
    When I update the question category to "operations"
    Then the response status is 200
    And the question category is "operations"
