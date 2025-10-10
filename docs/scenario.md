# E-commerce Platform Scenario

This document outlines a user scenario for the e-commerce platform, covering the entire customer journey from registration to receiving an order.

## Entities Involved

*   **User:** The customer interacting with the platform.
*   **Product:** Items available for sale.
*   **Category:** Groups of related products.
*   **Store:** A virtual storefront for a seller.
*   **Seller:** The entity selling products.
*   **Cart:** A temporary holding place for items a user wants to buy.
*   **Order:** A confirmed purchase request.
*   **Payment:** The transaction for an order.
*   **Shipment:** The delivery process for an order.
*   **Address:** The user's shipping and billing information.
*   **Comment:** User feedback on products.
*   **Discount:** Promotional offers.
*   **Notification:** Alerts sent to users.
*   **Ticket:** A support request from a user.
*   **Role:** User permissions (e.g., customer, seller, admin).

---

## Scenario: A Customer's First Purchase

### 1. User Registration and Login

*   **Action:** A new user, "Alice," visits the website for the first time. She decides to create an account to save her preferences and track orders.
*   **Steps:**
    1.  Alice clicks the "Sign-Up" button.
    2.  She fills out the registration form with her name, phone number, and a password.
    3.  The system creates a new `User` entity for Alice with the "customer" `Role`.
    4.  Alice receives a OTP verification code via SMS.
    5.  She logs in with her new credentials.

### 2. Browsing and Discovering Products

*   **Action:** Alice is looking for a new laptop.
*   **Steps:**
    1.  Alice uses the search bar to look for "laptop."
    2.  The system displays a list of `Product` entities matching the search query.
    3.  She filters the results by the "Electronics" `Category`.
    4.  She clicks on a specific laptop to view its details, including images, description, price, and `Comment`s from other users.
    5.  She sees the product is sold by the "Tech World" `Store`, which is managed by a `Seller`.

### 3. Adding to Cart and Applying a Discount

*   **Action:** Alice decides to purchase the laptop.
*   **Steps:**
    1.  Alice clicks the "Add to Cart" button.
    2.  The system creates a `Cart` and adds the selected `Product`.
    3.  She sees a banner for a 10% off `Discount` for first-time buyers.
    4.  She navigates to her `Cart`, enters the discount code, and the total price is updated. The system records this as a `Discount_Usage`.

### 4. Checkout Process

*   **Action:** Alice is ready to complete her purchase.
*   **Steps:**
    1.  Alice proceeds to checkout.
    2.  She is prompted to add a shipping `Address`. She enters her home address, which is saved to her profile.
    3.  She selects a shipping method, which creates a `Shipment` entity associated with her potential order.
    4.  She proceeds to the payment step.

### 5. Payment and Order Confirmation

*   **Action:** Alice pays for her order.
*   **Steps:**
    1.  Alice chooses to pay with her credit card.
    2.  She enters her card details into the secure `Payment` form.
    3.  The payment is processed successfully.
    4.  The system creates a new `Order` entity, linking the `User`, `Product`s, `Address`, `Payment`, and `Shipment`.
    5.  The `Cart` is cleared.
    6.  Alice receives an `Notification` and a SMS confirming her order.

### 6. Order Fulfillment by the Seller

*   **Action:** The "Tech World" `Store` processes the order.
*   **Steps:**
    1.  The `Seller` receives a `Notification` about the new `Order`.
    2.  The seller prepares the laptop for shipping.
    3.  The seller updates the `Shipment` status to "Shipped" and adds a tracking number.
    4.  Alice receives a `Notification` with the tracking information.

### 7. Post-Purchase Interaction

*   **Action:** Alice has a question about her order.
*   **Steps:**
    1.  Alice opens a `Ticket` through the customer support section of the website.
    2.  She writes a `Ticket_Message` asking about the estimated delivery date.
    3.  A support agent (a `User` with a "support" `Role`) responds to her `Ticket_Message`.
    4.  After receiving her laptop, Alice leaves a positive `Comment` on the product page.
