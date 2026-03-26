Feature: Coverage Tracking
  As an architect
  I want to track which knowledge library checklist items have been addressed
  So that I can ensure comprehensive architecture design

  Background:
    Given a version exists with id "test-version-id"

  Scenario: Create a coverage item
    When I create a coverage item with:
      | knowledge_file | general/security.md |
      | item_text | Are mandatory tags defined and enforced? |
      | priority | Critical |
    Then the coverage item is created with status "pending"

  Scenario: Update coverage item status to addressed
    Given a pending coverage item exists
    When I update the coverage item status to "addressed"
    Then the coverage item status is "addressed"

  Scenario: Link coverage item to a question
    Given a pending coverage item exists
    And a question exists in the version
    When I update the coverage item with the question_id
    Then the coverage item references the question

  Scenario: Defer a coverage item with reason
    Given a pending coverage item exists
    When I update the coverage item with status "deferred" and reason "Out of scope for phase 1"
    Then the coverage item status is "deferred"
    And the reason is "Out of scope for phase 1"

  Scenario: Get coverage summary
    Given coverage items exist with various priorities and statuses
    When I request the coverage summary
    Then I receive aggregated counts by priority and status

  Scenario: List coverage items for a version
    Given multiple coverage items exist for the version
    When I list coverage items
    Then all coverage items for the version are returned
