# Test Cases - Plain English Format

**Generated:** 2025-10-02 13:43:33
**Provider:** openai
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

## Test Case 1: Add Item to Cart from Product Listing

**Description:** Test that a user can add an item to the shopping cart from the product listing page.

**Steps:**
1. Navigate to the product listing page.
2. Select a product and click on 'Add to Cart'.

**Expected Result:** The item is added to the cart and the cart displays the correct product name, price, quantity, and subtotal.

## Test Case 2: Update Item Quantity in Cart

**Description:** Test that a user can update the quantity of an item directly from the cart.

**Steps:**
1. Navigate to the shopping cart.
2. Increase the quantity of an item.
3. Save or update the cart.

**Expected Result:** The item quantity is updated, and the subtotal and total cart amount reflect the changes.

## Test Case 3: Add Out of Stock Item to Cart

**Description:** Test that the system prevents the user from adding an out-of-stock item to the cart.

**Steps:**
1. Navigate to the product detail page of the out-of-stock item.
2. Click on 'Add to Cart'.

**Expected Result:** A notification appears indicating the item is out of stock and it does not get added to the cart.

## Test Case 4: Automatic Cart Total Update

**Description:** Test that the cart total updates automatically when items or quantities change.

**Steps:**
1. Navigate to the shopping cart.
2. Change the quantity of one or more items.
3. Observe the cart total.

**Expected Result:** The cart total updates automatically without needing to refresh the page.

## Test Case 5: Cart Persistence Across Sessions

**Description:** Verify that the cart contents persist for logged-in users when they log out and log back in.

**Steps:**
1. Add items to the shopping cart.
2. Log out of the account.
3. Log back in to the same account.

**Expected Result:** The items previously added to the cart are still present.

