Feature: The wishlist service back-end
    As an online shopper
    I need a RESTful wishlist service
    So that I can keep track of all my wishlists and desired items

Background:
    Given the following wishlists
        | name       | type     | user_id | created_date|
        | home       | personal | 1       | 2019-11-18  |
        | work       | public   | 2       | 2020-08-13  |
        | garden     | personal | 3       | 2021-04-01  |
        | tech       | public   | 4       | 2018-06-04  |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Wishlist Demo REST API Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Wishlist
    When I visit the "Home Page"
    And I set the "Name" to "Summer"
    And I set the "Type" to "Public"
    And I set the "User_ID" to "123"
    And I set the "Created_Date" to "05-20-2022"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "Type" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see "Summer" in the "Name" field
    And I should see "Public" in the "Type" field
    And I should see "123" in the "User_ID" field

Scenario: List all wishlists
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "home" in the results
    And I should see "work" in the results
    And I should see "garden" in the results
    And I should see "tech" in the results

Scenario: Search for tech
    When I visit the "Home Page"
    And I set the "Name" to "tech"
    And I press the "Search" button
    Then I should see "public" in the "Type" field
    And I should see "4" in the "User_ID" field

Scenario: Update a Wishlist
    When I visit the "Home Page"
    And I set the "Name" to "home"
    And I press the "Search" button
    Then I should see "home" in the "Name" field
    When I change "Name" to "apartment"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see "apartment" in the "Name" field
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see "apartment" in the results
    And I should not see "home" in the results