# Test Cases - Plain English Format

**Generated:** 2025-10-02 14:10:54
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

## Test Case 1: Add Item from Product Listing Page

**Description:** Verify that a user can successfully add an item to the cart from the product listing page.

**Steps:**
1. Locate the product on the listing page.
2. Click on the 'Add to Cart' button for that product.
3. Navigate to the shopping cart.

**Expected Result:** The cart should display the added product with correct name, price, quantity as 1, and the corresponding subtotal.

## Test Case 2: Add Item from Product Detail Page

**Description:** Verify that a user can successfully add an item to the cart from the product detail page.

**Steps:**
1. View product details.
2. Click on the 'Add to Cart' button.
3. Navigate to the shopping cart.

**Expected Result:** The cart should display the added product with correct name, price, quantity as 1, and the corresponding subtotal.

## Test Case 3: Update Item Quantity in Cart

**Description:** Verify that a user can increase or decrease the quantity of an item in the cart.

**Steps:**
1. Navigate to the shopping cart.
2. Increase the quantity of an item.
3. Verify that the subtotal and cart total are updated accordingly.
4. Decrease the quantity of the same item.
5. Verify that the subtotal and cart total are updated accordingly.

**Expected Result:** The cart should correctly reflect the updated quantities and recalculate the subtotals as well as the cart total.

## Test Case 4: Out of Stock Notification

**Description:** Verify that the system correctly handles an attempt to add an out-of-stock item to the cart.

**Steps:**
1. Locate the out-of-stock item on the product listing or detail page.
2. Click on the 'Add to Cart' button.
3. Check for any notification messages.

**Expected Result:** The system should display a notification stating the item is out of stock and not add the item to the cart.

## Test Case 5: Automatic Cart Total Update

**Description:** Verify that the cart total updates automatically when items or their quantities change.

**Steps:**
1. Navigate to the shopping cart.
2. Increase the quantity of one item.
3. Observe the cart total.
4. Decrease the quantity of another item.
5. Observe the cart total again.

**Expected Result:** The cart total should reflect the changes in quantity without needing to refresh the page.

