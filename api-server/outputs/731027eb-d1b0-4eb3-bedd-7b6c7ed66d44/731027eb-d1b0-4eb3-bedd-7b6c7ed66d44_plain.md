# Test Cases - Plain English Format

**Generated:** 2025-10-02 13:29:23
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

## Test Case 1: Add Single Item to Cart from Product Listing Page

**Description:** Verify user can successfully add a product to cart from product listing page

**Steps:**
1. Navigate to product listing page
2. Select a product with available stock
3. Click 'Add to Cart' button for the product

**Expected Result:** Product is added to cart with correct name, price, and quantity of 1

## Test Case 2: Update Item Quantity in Cart

**Description:** Verify user can increase and decrease item quantity in cart

**Steps:**
1. Navigate to shopping cart
2. Increase quantity of an existing cart item by 1
3. Verify subtotal updates correctly
4. Decrease quantity of the same item by 1
5. Verify subtotal updates correctly

**Expected Result:** Cart subtotal and total update automatically with quantity changes

## Test Case 3: Prevent Adding Out-of-Stock Item

**Description:** Verify system prevents adding out-of-stock product to cart

**Steps:**
1. Navigate to product detail page for out-of-stock item
2. Attempt to add product to cart

**Expected Result:** User receives out-of-stock notification, item cannot be added to cart

## Test Case 4: Cart Persistence for Logged-In User

**Description:** Verify cart contents persist across user sessions

**Steps:**
1. Add items to cart
2. Log out of the application
3. Log back in
4. Navigate to shopping cart

**Expected Result:** Previously added cart items are still present

## Test Case 5: Maximum Quantity Limit Test

**Description:** Verify system handles maximum quantity limits

**Steps:**
1. Navigate to product detail page
2. Attempt to add product quantity exceeding maximum limit

**Expected Result:** System prevents adding more than maximum allowed quantity, displays appropriate error message

