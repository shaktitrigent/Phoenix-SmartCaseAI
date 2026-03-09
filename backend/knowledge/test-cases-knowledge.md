# Knowledge Base: Test Case Generation
> Covers Gherkin (BDD) and Plain English formats for Functional and Non-Functional test cases.

---

## 1. Core Principles

- Every test case must map to **one or more acceptance criteria** from an Intent or Feature document.
- Test cases should be **atomic** — one behaviour per test.
- Every test case must have a clear **pass/fail signal**.
- Avoid implementation detail in test case language; describe **observable behaviour**.
- Each test case must have a unique, human-readable **ID** and a **priority** (P0–P3).

---

## 2. Test Case Taxonomy

| Type        | Sub-type                    | Format Preferred       |
|-------------|-----------------------------|------------------------|
| Functional  | Happy Path                  | Gherkin or Plain       |
| Functional  | Alternate Flow              | Gherkin or Plain       |
| Functional  | Negative / Error            | Gherkin                |
| Functional  | Boundary / Edge             | Gherkin (Scenario Outline) |
| Functional  | Integration                 | Plain English          |
| Non-Functional | Performance / Load       | Plain English          |
| Non-Functional | Security                 | Plain English          |
| Non-Functional | Accessibility (a11y)     | Gherkin or Plain       |
| Non-Functional | Usability                | Plain English          |
| Non-Functional | Reliability / Recovery   | Plain English          |
| Non-Functional | Compatibility            | Plain English          |

---

## 3. Gherkin Format

### 3.1 Structure Rules

```gherkin
Feature: <Feature name — matches Feature Intent Document title>
  As a <role>
  I want <capability>
  So that <business value>

  Background: (optional — shared preconditions for all scenarios)
    Given <shared setup step>

  @tag1 @tag2
  Scenario: <Concise, behaviour-first title>
    Given <initial context / precondition>
    When  <action performed by actor>
    Then  <observable outcome>
    And   <additional outcome> (if needed)
    But   <excluded outcome> (if needed)
```

### 3.2 Scenario Outline (Data-Driven)

```gherkin
  Scenario Outline: <title with <variable>>
    Given <context with "<param>">
    When  <action with "<param>">
    Then  <outcome with "<expected>">

    Examples:
      | param     | expected        |
      | value_1   | result_1        |
      | value_2   | result_2        |
```

### 3.3 Gherkin Writing Rules

| Rule | Guidance |
|------|----------|
| **Given** | State, not action. Sets precondition. Never starts with "I". |
| **When** | Single user action or system event. One `When` per scenario ideally. |
| **Then** | Verifiable outcome. Must be assertable. Avoid vague words like "correct". |
| **And / But** | Continues previous step type. Never use as first step. |
| **Background** | Use only for steps repeated in ALL scenarios in a Feature. |
| **Tags** | Use `@smoke`, `@regression`, `@p0`–`@p3`, `@functional`, `@nonfunctional`, `@security`, `@a11y`, `@perf` |

### 3.4 Gherkin Anti-Patterns (Avoid)

- `When I click the submit button` → `When the user submits the registration form`
- `Then it should work` → `Then the dashboard displays the user's full name`
- Multiple `When` steps → split into separate scenarios
- UI implementation detail in steps (XPath, CSS selectors, button IDs)
- Conjunctive scenarios: `Scenario: Login and view dashboard and export report`

---

## 4. Plain English Format

### 4.1 Structure Template

```
Test Case ID : <MODULE>-<TYPE>-<NNN>   (e.g. AUTH-FUNC-001, API-PERF-003)
Title        : <Action + Subject + Context>
Priority     : P0 | P1 | P2 | P3
Type         : Functional | Non-Functional
Sub-type     : Happy Path | Negative | Boundary | Performance | Security | …
Linked To    : <Feature Intent Doc / ADR / User Story ID>

Preconditions:
  1. <State that must be true before execution>
  2. <Any required test data or environment>

Test Steps:
  1. <Actor performs action>
  2. <Actor performs next action>
  …

Expected Result:
  - <Observable system response for each key step>
  - <Final state of the system>

Postconditions / Cleanup:
  - <State after test completes, data rollback if needed>

Notes:
  - <Edge cases, related tests, known constraints>
```

### 4.2 Priority Definitions

| Priority | Meaning | Examples |
|----------|---------|---------|
| **P0** | System cannot function without this | Login, payment, data save |
| **P1** | Core user journey degraded | Search, filter, checkout |
| **P2** | Important but workaround exists | Export, notifications |
| **P3** | Nice-to-have / cosmetic | Tooltip text, animation |

---

## 5. Functional Test Case Patterns

### 5.1 Happy Path
```gherkin
Scenario: Successful login with valid credentials
  Given the user is on the login page
  When  the user enters valid credentials and submits
  Then  the user is redirected to the home dashboard
  And   a welcome message displaying the user's name is shown
```

### 5.2 Negative / Error Path
```gherkin
Scenario: Login fails with incorrect password
  Given the user is on the login page
  When  the user enters a valid email and an incorrect password
  Then  an error message "Invalid credentials" is displayed
  And   the user remains on the login page
  And   the password field is cleared
```

### 5.3 Boundary / Edge (Outline)
```gherkin
Scenario Outline: Username length boundary validation
  Given the user is on the registration page
  When  the user enters a username of <length> characters
  Then  the form displays <outcome>

  Examples:
    | length | outcome                        |
    | 2      | "Username too short" error     |
    | 3      | no validation error            |
    | 50     | no validation error            |
    | 51     | "Username too long" error      |
```

### 5.4 Integration Test (Plain English)
```
Test Case ID : INT-FUNC-001
Title        : Order placement triggers inventory deduction
Preconditions:
  1. Product A has stock quantity = 10
  2. User is authenticated
Test Steps:
  1. User places an order for 3 units of Product A
  2. Payment is confirmed via payment gateway stub
Expected Result:
  - Order record is created with status "Confirmed"
  - Product A stock is reduced to 7 in the inventory service
  - Confirmation email event is published to the notification queue
```

---

## 6. Non-Functional Test Case Patterns

### 6.1 Performance / Load (Plain English)
```
Test Case ID : HOME-PERF-001
Title        : Home page loads within SLA under peak load
Type         : Non-Functional — Performance
Preconditions:
  1. Production-equivalent environment
  2. 500 concurrent virtual users configured in load tool
Test Steps:
  1. Ramp up 500 concurrent users over 2 minutes
  2. Sustain load for 10 minutes hitting the home page
  3. Capture p50, p95, p99 response times and error rate
Expected Result:
  - p95 response time ≤ 2 seconds
  - Error rate < 0.5%
  - No memory leak observed (heap stable across ramp)
```

### 6.2 Security (Plain English)
```
Test Case ID : AUTH-SEC-001
Title        : Brute-force lockout after N failed login attempts
Type         : Non-Functional — Security
Preconditions:
  1. Account exists with known credentials
Test Steps:
  1. Submit 5 consecutive invalid password attempts for the account
  2. Attempt a 6th login with the correct password
Expected Result:
  - After 5 failures, account is locked for 15 minutes
  - 6th attempt returns "Account locked" message even with correct credentials
  - Lock event is logged in the audit trail
```

### 6.3 Accessibility — WCAG 2.1 AA (Gherkin)
```gherkin
@a11y
Scenario: Form inputs are accessible via keyboard navigation
  Given the user is on the contact form page
  When  the user navigates using only the Tab key
  Then  each interactive element receives visible focus in logical order
  And   no focus trap exists outside modal contexts
  And   all form fields have associated visible labels
```

### 6.4 Usability (Plain English)
```
Test Case ID : ONBOARD-USAB-001
Title        : First-time user completes onboarding without external help
Type         : Non-Functional — Usability
Test Steps:
  1. New user account with no prior session opens the app
  2. Observe whether user can locate and complete onboarding flow unaided
Expected Result:
  - User completes all 4 onboarding steps within 5 minutes
  - No more than 1 navigation error (back/wrong path) occurs
  - User reaches the main dashboard without contacting support
```

### 6.5 Reliability / Recovery (Plain English)
```
Test Case ID : API-REL-001
Title        : Service recovers and resumes processing after a crash
Type         : Non-Functional — Reliability
Test Steps:
  1. Confirm service is running and processing requests normally
  2. Forcefully terminate the service process (SIGKILL)
  3. Wait for auto-restart via process manager
  4. Send a new request immediately after restart
Expected Result:
  - Service restarts within 30 seconds
  - In-flight requests at crash time are either retried or reported as failed (no silent data loss)
  - First post-restart request is handled successfully
```

---

## 7. AI Generation Prompt Templates

### Generate Gherkin from a Feature Description
```
You are a senior QA engineer. Given the following feature description, generate comprehensive 
Gherkin scenarios covering: happy path, alternate flows, negative/error cases, and boundary 
conditions. Follow BDD best practices — no UI implementation detail in steps, one action per 
When, observable outcomes in Then. Tag each scenario with @smoke, @regression, or @edge as 
appropriate.

Feature description:
<paste feature intent here>
```

### Generate Plain English NFRs from Acceptance Criteria
```
You are a senior QA engineer. Given the acceptance criteria below, generate non-functional 
test cases for: performance, security, accessibility, and reliability. Use the plain English 
template with Test Case ID, Preconditions, Steps, and Expected Results. Include measurable 
thresholds in Expected Results wherever possible.

Acceptance Criteria:
<paste criteria here>
```

---

## 8. Quality Checklist

Before finalising any generated test case, verify:

- [ ] Covers at least one acceptance criterion explicitly
- [ ] Has a unique, meaningful ID
- [ ] Expected result is assertable (measurable, not vague)
- [ ] No implementation detail in step language
- [ ] Priority is assigned
- [ ] Tagged appropriately (Gherkin)
- [ ] Preconditions are complete and realistic
- [ ] NFR test cases have quantified thresholds (ms, %, count)
- [ ] Boundary tests cover: min, min-1, max, max+1
