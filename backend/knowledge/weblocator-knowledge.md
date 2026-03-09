# Knowledge Base: Web Locator Strategy for UI Automation
> Covers locator selection weightage, Playwright-specific strategy, and Selenium-specific strategy.

---

## 1. Core Principles

- **Locators must be resilient** — survive UI refactors, theme changes, and DOM reorders.
- **Locators must be readable** — another engineer should understand what element is targeted without running the test.
- **Locators must be unique** — never match more than the intended element.
- **Prefer semantic over structural** — what the element *means* over where it *is*.
- **Never use auto-generated or dynamic values** — no session IDs, timestamps, or random hashes in locators.

---

## 2. Universal Locator Weightage (Framework-Agnostic)

Use this priority order regardless of framework. Higher weight = use first.

| Weight | Locator Type | Rationale |
|--------|-------------|-----------|
| **W1 — Highest** | `data-testid` / `data-cy` / `data-qa` custom attributes | Purpose-built for testing; immune to style and layout changes |
| **W2** | ARIA Role + Accessible Name (`role` + `aria-label` / visible text) | Semantic, accessibility-aligned, stable across visual redesigns |
| **W3** | Semantic HTML attributes (`type`, `name`, `for`, `placeholder`) | Functionally tied to element behaviour |
| **W4** | Stable `id` (non-dynamic) | Fast and unique — only if id is truly static |
| **W5** | Stable `class` (BEM / semantic, non-utility) | Use only if class is behaviour/component-scoped, not utility-CSS |
| **W6** | Link text / Button text (exact or partial) | Readable but brittle to copy changes |
| **W7** | Relative XPath / CSS structural selectors | Use only when no semantic option exists |
| **W8 — Lowest** | Absolute XPath | Last resort; breaks on any DOM structural change |

### 2.1 Locator Anti-Patterns (Avoid at All Weights)

| Anti-Pattern | Why |
|-------------|-----|
| `//div[3]/span[2]/button` | Absolute positional XPath — breaks on reorder |
| `.btn-primary` (Tailwind / Bootstrap utility) | Utility classes are not element-specific |
| Dynamic `id` containing timestamps or UUIDs | Changes on every render |
| `document.querySelectorAll` with index `[0]` | Order-dependent |
| Inline `style` attributes | Not semantic or stable |

---

## 3. Playwright Locator Strategy

> Playwright has a **first-class locator API** that enforces auto-waiting and actionability checks. Prefer Playwright's built-in locators over raw selectors.

### 3.1 Playwright Locator Priority (Weighted)

| Weight | Playwright API | Example | Notes |
|--------|---------------|---------|-------|
| **W1** | `getByTestId()` | `page.getByTestId('submit-btn')` | Maps to `data-testid`. Configure via `testIdAttribute` in `playwright.config.ts` |
| **W2** | `getByRole()` | `page.getByRole('button', { name: 'Submit' })` | ARIA-based; most resilient to redesigns |
| **W3** | `getByLabel()` | `page.getByLabel('Email address')` | Targets form inputs by their `<label>` text |
| **W4** | `getByPlaceholder()` | `page.getByPlaceholder('Enter your email')` | Useful for inputs without labels |
| **W5** | `getByText()` | `page.getByText('Welcome back')` | Exact or regex match on visible text |
| **W6** | `getByAltText()` | `page.getByAltText('Company logo')` | Images and media elements |
| **W7** | `getByTitle()` | `page.getByTitle('Close dialog')` | Tooltip / title attribute |
| **W8** | `locator()` with CSS | `page.locator('[name="username"]')` | Fallback; prefer attribute selectors over class |
| **W9** | `locator()` with XPath | `page.locator('xpath=//button[@type="submit"]')` | Last resort |

### 3.2 Playwright Chaining & Filtering

```typescript
// Scope to a component region first, then locate within it
const modal = page.getByRole('dialog', { name: 'Confirm Delete' });
await modal.getByRole('button', { name: 'Delete' }).click();

// Filter by child content
page.getByRole('listitem').filter({ hasText: 'Product A' });

// nth match (use sparingly)
page.getByRole('row').nth(2);

// Combining locators
page.locator('.card').filter({ has: page.getByTestId('featured-badge') });
```

### 3.3 Playwright-Specific Configuration

```typescript
// playwright.config.ts — custom test ID attribute
use: {
  testIdAttribute: 'data-qa',  // default is 'data-testid'
}
```

### 3.4 Playwright Locator Decision Tree

```
Does the element have data-testid / data-qa?
  └─ YES → getByTestId()                          [W1]
Does the element have a meaningful ARIA role + name?
  └─ YES → getByRole()                            [W2]
Is it a form input with a <label>?
  └─ YES → getByLabel()                           [W3]
Is it an input with a placeholder?
  └─ YES → getByPlaceholder()                     [W4]
Does it have unique, stable visible text?
  └─ YES → getByText()                            [W5]
Is it an image with alt text?
  └─ YES → getByAltText()                         [W6]
Does it have a stable, non-dynamic id or name attr?
  └─ YES → locator('[id="..."]') or locator('[name="..."]')  [W8]
Does it have a stable semantic class (BEM, component)?
  └─ YES → locator('.ComponentName__element')     [W8]
Nothing else works?
  └─ locator('xpath=...')                         [W9]
```

### 3.5 Playwright Examples by Scenario

| Scenario | Recommended Locator |
|----------|-------------------|
| Primary CTA button | `page.getByRole('button', { name: 'Get Started' })` |
| Email input field | `page.getByLabel('Email')` or `page.getByPlaceholder('you@example.com')` |
| Navigation link | `page.getByRole('link', { name: 'Dashboard' })` |
| Checkbox | `page.getByRole('checkbox', { name: 'Accept terms' })` |
| Dropdown / select | `page.getByRole('combobox', { name: 'Country' })` |
| Table row with content | `page.getByRole('row').filter({ hasText: 'Invoice #1042' })` |
| Toast / alert message | `page.getByRole('alert')` |
| Modal close button | `page.getByRole('dialog').getByRole('button', { name: 'Close' })` |
| Icon-only button | `page.getByRole('button', { name: /delete/i })` or `getByTestId('delete-icon-btn')` |

---

## 4. Selenium Locator Strategy

> Selenium uses `By.*` locator strategies. Unlike Playwright, Selenium does **not** auto-wait — pair locators with explicit `WebDriverWait` / `ExpectedConditions`.

### 4.1 Selenium Locator Priority (Weighted)

| Weight | Selenium Strategy | Example | Notes |
|--------|------------------|---------|-------|
| **W1** | `By.cssSelector` with `data-testid` | `By.cssSelector("[data-testid='submit-btn']")` | Purpose-built test attribute; fastest after ID |
| **W2** | `By.id` (static) | `By.id("login-form")` | Fastest locator — only if id is static |
| **W3** | `By.name` | `By.name("username")` | Good for form inputs |
| **W4** | `By.cssSelector` (semantic attribute) | `By.cssSelector("[aria-label='Close dialog']")` | Semantic + CSS; better than class |
| **W5** | `By.cssSelector` (stable class) | `By.cssSelector(".NavBar__logo")` | BEM/component-scoped only; not utility classes |
| **W6** | `By.linkText` / `By.partialLinkText` | `By.linkText("Sign In")` | Anchors only; brittle to copy changes |
| **W7** | `By.xpath` (attribute-based) | `By.xpath("//button[@type='submit']")` | Avoid positional axes |
| **W8** | `By.tagName` | `By.tagName("h1")` | Only for unique tags on page |
| **W9 — Lowest** | `By.xpath` (positional) | `By.xpath("//div[2]/ul/li[1]/a")` | Last resort; very fragile |

### 4.2 Selenium CSS Selector Patterns

```java
// Attribute selector (preferred over class)
By.cssSelector("[data-testid='user-menu']")
By.cssSelector("[aria-label='Search']")
By.cssSelector("input[type='email']")
By.cssSelector("button[type='submit']")

// Descendant (scope to container)
By.cssSelector(".ProductCard [data-testid='add-to-cart']")

// Attribute contains
By.cssSelector("[class*='Modal__overlay']")  // use cautiously

// Pseudo-classes (use sparingly)
By.cssSelector("li:first-child > a")
By.cssSelector("input:not([disabled])")
```

### 4.3 Selenium XPath Patterns (When CSS Is Insufficient)

```java
// By text content
By.xpath("//button[normalize-space()='Submit Order']")

// By partial text
By.xpath("//a[contains(text(),'View Details')]")

// Sibling traversal (e.g., label → input)
By.xpath("//label[text()='Email']/following-sibling::input")

// Parent traversal (e.g., error message sibling to input)
By.xpath("//input[@name='email']/parent::div/span[@class='error']")

// By ARIA attribute
By.xpath("//*[@aria-label='Close dialog']")

// Avoid absolute paths
// ❌ By.xpath("/html/body/div[1]/div[2]/form/button")
```

### 4.4 Selenium Explicit Wait Pattern

```java
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));

// Wait for element to be clickable
WebElement btn = wait.until(
    ExpectedConditions.elementToBeClickable(By.cssSelector("[data-testid='submit-btn']"))
);
btn.click();

// Wait for visibility
WebElement msg = wait.until(
    ExpectedConditions.visibilityOfElementLocated(By.xpath("//div[@role='alert']"))
);
```

### 4.5 Selenium Locator Decision Tree

```
Does the element have data-testid / data-qa / data-cy?
  └─ YES → By.cssSelector("[data-testid='...']")          [W1]
Does the element have a static, unique id?
  └─ YES → By.id("...")                                   [W2]
Is it a form input with a name attribute?
  └─ YES → By.name("...")                                 [W3]
Does it have a meaningful aria-label or aria-labelledby?
  └─ YES → By.cssSelector("[aria-label='...']")           [W4]
Does it have a BEM / component-scoped stable class?
  └─ YES → By.cssSelector(".Component__element")          [W5]
Is it an anchor with unique link text?
  └─ YES → By.linkText("...")                             [W6]
Does it have a stable HTML attribute (type, role, name)?
  └─ YES → By.xpath("//*[@attr='value']")                 [W7]
Nothing else works?
  └─ By.xpath positional (document well)                  [W9]
```

### 4.6 Selenium Examples by Scenario

| Scenario | Recommended Locator |
|----------|-------------------|
| Submit button | `By.cssSelector("[data-testid='submit-btn']")` or `By.cssSelector("button[type='submit']")` |
| Email input | `By.name("email")` or `By.cssSelector("input[type='email']")` |
| Navigation link | `By.linkText("Dashboard")` |
| Checkbox | `By.cssSelector("input[type='checkbox'][name='terms']")` |
| Dropdown | `By.id("country-select")` or `By.name("country")` |
| Table cell | `By.xpath("//td[text()='Invoice #1042']")` |
| Error message | `By.cssSelector("[role='alert']")` |
| Icon-only button | `By.cssSelector("[aria-label='Delete item']")` |

---

## 5. Playwright vs. Selenium: Quick Comparison

| Dimension | Playwright | Selenium |
|-----------|-----------|---------|
| Best W1 locator | `getByTestId()` | `By.cssSelector("[data-testid='...']")` |
| Semantic/ARIA | First-class (`getByRole`) | Via XPath/CSS attribute |
| Auto-waiting | Built-in to all locator actions | Must use `WebDriverWait` explicitly |
| Chaining/scoping | `.locator()` chaining, `.filter()` | `findElement` within element |
| Text matching | `getByText()`, `filter({hasText})` | XPath `text()` or `contains(text())` |
| Regex support | Yes, native in most `getBy*` | No native; use XPath `contains()` |
| Recommended config | Set `testIdAttribute` in config | Use Page Object Model |

---

## 6. `data-testid` Naming Convention

Establish a consistent naming scheme so agents generate consistent locators.

```
Format:  data-testid="<component>-<element>-<context?>"

Examples:
  data-testid="login-form-submit"
  data-testid="product-card-add-to-cart"
  data-testid="nav-link-dashboard"
  data-testid="modal-confirm-delete"
  data-testid="search-input"
  data-testid="user-avatar-menu"
```

Rules:
- **kebab-case** only
- **No dynamic suffixes** (no IDs, no indices)
- **Max 4 segments**: `<page?>-<component>-<element>-<action?>`
- Applied at **lowest unique element** level (button, input, link) — not wrapper divs

---

## 7. AI Generation Prompt Templates

### Generate Locators from UI Description (Playwright)
```
You are a UI automation engineer using Playwright. Given the following UI element description, 
generate the most resilient locator using this priority: getByTestId > getByRole > getByLabel > 
getByPlaceholder > getByText > locator(CSS) > locator(XPath). Always prefer semantic, 
ARIA-based locators. Explain the weight level chosen.

UI element:
<describe element, its visible text, role, surrounding context>
```

### Generate Locators from UI Description (Selenium)
```
You are a UI automation engineer using Selenium WebDriver (Java/Python). Given the following 
UI element description, generate the most resilient By.* locator using this priority: 
data-testid CSS > By.id > By.name > aria-label CSS > stable class CSS > By.linkText > 
attribute XPath > positional XPath. Include the explicit wait strategy if the element is 
dynamic. Explain the weight level chosen.

UI element:
<describe element, its visible text, attributes, surrounding context>
```

---

## 8. Locator Quality Checklist

Before committing any locator:

- [ ] Uses W1–W4 strategy where possible
- [ ] Does not contain dynamic values (IDs, timestamps, session tokens)
- [ ] Is unique on the page (validated by running a query)
- [ ] Is readable without needing to inspect the DOM
- [ ] Does not rely on visual/positional structure (`nth-child`, absolute XPath)
- [ ] For Selenium: paired with explicit wait
- [ ] `data-testid` follows naming convention if used
- [ ] Locator is scoped to the nearest stable container when dealing with repeated elements
