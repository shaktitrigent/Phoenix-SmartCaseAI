# Test Cases - Plain English Format

**Generated on:** 2025-09-10 19:14:21

**User Story:** As a user, I want to log in to the system so that I can access my account.

---

## Test Case 1: Login with valid credentials

**Description:** Verify that a user can successfully log in with valid username and password

**Type:** positive

**Preconditions:** User has a valid account in the system

**Steps:**
1. Navigate to the login page
2. Enter valid username in the username field
3. Enter valid password in the password field
4. Click the 'Login' button

**Expected Result:** User should be successfully logged in and redirected to the dashboard

---

## Test Case 2: Login with invalid password

**Description:** Verify that login fails with invalid password

**Type:** negative

**Preconditions:** User has a valid username but incorrect password

**Steps:**
1. Navigate to the login page
2. Enter valid username in the username field
3. Enter invalid password in the password field
4. Click the 'Login' button

**Expected Result:** Error message should be displayed: 'Invalid username or password'

---

