# BDD Test Scenarios - Gherkin Format

**Generated on:** 2025-09-10 19:14:21

**User Story:** As a user, I want to log in to the system so that I can access my account.

---

## Scenario 1: Successful login with valid credentials

**Feature:** User Authentication

```gherkin
Feature: User Authentication

Scenario: Successful login with valid credentials
  Given the user is on the login page
  Given the user has valid account credentials
  When the user enters their valid username
  When the user enters their valid password
  When the user clicks the login button
  Then the user should be logged in successfully
  Then the user should be redirected to the dashboard
  Then the user session should be active
```

---

## Scenario 2: Failed login with invalid password

**Feature:** User Authentication

```gherkin
Feature: User Authentication

Scenario: Failed login with invalid password
  Given the user is on the login page
  Given the user has a valid username but invalid password
  When the user enters their valid username
  When the user enters an invalid password
  When the user clicks the login button
  Then the login should fail
  Then an error message should be displayed
  Then the user should remain on the login page
```

---

