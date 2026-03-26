Feature: Architecture Chat
  As an architect
  I want to chat with an LLM-powered assistant
  So that I can design cloud architectures with knowledge library guidance

  Background:
    Given a client "Test Corp" exists
    And a project "Migration" exists for "Test Corp"
    And version "1.0.0" exists for "Migration"

  Scenario: Stream a chat response
    When I send a chat message "What networking patterns should I consider?"
    Then I receive SSE events with type "content"
    And the stream ends with a "done" event

  Scenario: Chat with knowledge library context
    Given the knowledge library is indexed
    When I send a chat message "What are the critical items for disaster recovery?"
    Then the response references knowledge library content
    And the response cites source file paths

  Scenario: Chat creates an artifact via tool call
    Given version "1.0.0" is selected in the chat context
    When I send a chat message "Create a network diagram for a three-tier web app"
    Then I receive SSE events with type "tool_call" for "create_artifact"
    And I receive SSE events with type "tool_result"
    And an artifact exists in version "1.0.0"

  Scenario: Chat creates an ADR via tool call
    Given version "1.0.0" is selected in the chat context
    When I send a chat message "Record a decision to use PostgreSQL for the database"
    Then I receive SSE events with type "tool_call" for "create_adr"
    And an ADR exists in version "1.0.0" with title containing "PostgreSQL"

  Scenario: Chat falls back when tools not supported
    When I send a chat message using a provider that does not support tools
    Then the response streams content without tool calls
    And no error events are received

  Scenario: Chat with no version selected
    When I send a chat message without a version_id
    Then only knowledge search tools are available
    And artifact/ADR tools are not invoked
