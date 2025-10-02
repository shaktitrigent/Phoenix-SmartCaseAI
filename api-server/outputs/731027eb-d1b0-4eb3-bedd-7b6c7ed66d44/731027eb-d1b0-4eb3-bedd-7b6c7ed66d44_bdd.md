# BDD Test Scenarios - Gherkin Format

**Generated:** 2025-10-02 13:29:53
**Provider:** claude
**User Story:** User Story
As an e-commerce customer,
I want to add items to my shopping cart and update quantities,
So that I can review and purchase multiple products in one checkout.

Acceptance Criteria

User can add items to the cart from product listing and product detail pages.

Cart should display product name, price, quantity, and subtotal for each item.

User can update item quantity (increase/decrease) directly from the cart.

If a product is out of stock, the cart should notify the user and prevent checkout.

The cart total should update automatically when items or quantities change.

Cart contents should persist for logged-in users across sessions.

## Scenario 1: Add single item to cart from product listing page

**Feature:** Shopping Cart Management

```gherkin
Feature: Shopping Cart Management

Scenario: Add single item to cart from product listing page
  Given the user is logged in
  Given a product is available in stock
  Given the user is on the product listing page
  When the user clicks the 'Add to Cart' button for a specific product
  When the user navigates to the cart page
  Then the product should be added to the cart
  Then the cart should display the correct product details
  Then the cart total should reflect the added item's price
```

## Scenario 2: Update item quantity in cart

**Feature:** Shopping Cart Management

```gherkin
Feature: Shopping Cart Management

Scenario: Update item quantity in cart
  Given the user is logged in
  Given at least one item is already in the cart
  When the user increases the quantity of an item in the cart
  When the user clicks the update button
  Then the item quantity should be updated
  Then the subtotal for that item should be recalculated
  Then the cart total should update automatically
```

## Scenario 3: Prevent checkout with out-of-stock item

**Feature:** Shopping Cart Management

```gherkin
Feature: Shopping Cart Management

Scenario: Prevent checkout with out-of-stock item
  Given the user is logged in
  Given a product has become out of stock
  Given the out-of-stock product is in the user's cart
  When the user attempts to proceed to checkout
  Then the system should display an out-of-stock notification
  Then checkout should be prevented
  Then the user should be prompted to remove the out-of-stock item
```

## Scenario 4: Persist cart contents across user sessions

**Feature:** Shopping Cart Management

```gherkin
Feature: Shopping Cart Management

Scenario: Persist cart contents across user sessions
  Given the user is logged in
  Given the user has items in their cart
  When the user logs out
  When the user logs back in
  Then the cart should contain the same items as before logging out
  Then item quantities should remain unchanged
```

## Scenario 5: Add multiple items from product detail page

**Feature:** Shopping Cart Management

```gherkin
Feature: Shopping Cart Management

Scenario: Add multiple items from product detail page
  Given the user is logged in
  Given multiple products are available in stock
  Given the user is on different product detail pages
  When the user adds multiple different products to the cart
  When the user navigates to the cart page
  Then all selected products should be in the cart
  Then each product should have its correct details
  Then the cart total should be the sum of all product prices
```

