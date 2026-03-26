Feature: File Uploads
  As an architect
  I want to upload files to a version
  So that I can attach reference documents and data files

  Background:
    Given a version exists

  Scenario: Upload a file
    When I upload a file "network_diagram.png" with content type "image/png"
    Then the upload is created with the original filename preserved
    And the file is stored on the PVC

  Scenario: Download an uploaded file
    Given a file has been uploaded
    When I download the file by upload ID
    Then I receive the file with correct content type

  Scenario: Delete an uploaded file
    Given a file has been uploaded
    When I delete the upload
    Then the upload record is removed
    And the file is deleted from the PVC

  Scenario: Reject oversized uploads
    When I upload a file exceeding 100MB
    Then the upload is rejected with a 413 error

  Scenario: List uploads for a version
    Given multiple files have been uploaded
    When I list uploads for the version
    Then all uploads are returned with metadata
