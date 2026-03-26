Feature: Inventory Management
  As an architect
  I want to manage inventory data for a version
  So that I can track infrastructure components being designed

  Background:
    Given a version exists

  Scenario: Create an inventory item
    When I create an inventory item with name "VM Inventory" and data_type "vm_inventory"
    Then the inventory item is created successfully

  Scenario: Update inventory item data
    Given an inventory item exists
    When I update the inventory item data
    Then the updated_at timestamp changes

  Scenario: Delete an inventory item
    Given an inventory item exists
    When I delete the inventory item
    Then the inventory item no longer exists

  Scenario: List inventory items sorted by order
    Given multiple inventory items exist with different sort_order values
    When I list inventory items
    Then they are returned sorted by sort_order then name
