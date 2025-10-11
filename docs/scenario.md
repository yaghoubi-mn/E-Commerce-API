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


---

## Scenario: A Seller's First View

This scenario describes the journey of a new seller, "Bob," who wants to sell his products on the platform.

### 1. Seller Registration

*   **Action:** Bob wants to become a seller on the platform.
*   **Steps:**
    1.  Bob navigates to the "Become a Seller" page.
    2.  He fills out a detailed registration form, providing information about his business and bank details for `Payment`s.
    3.  The system creates a new `User` entity for Bob with a "seller" `Role` pending approval.
    4.  An admin `User` reviews Bob's application and approves it.
    5.  Bob receives a `Notification` that his seller account is active.

### 2. Store Creation

*   **Action:** Bob sets up his virtual `Store`.
*   **Steps:**
    1.  After his first login as a seller, Bob is prompted to create his `Store`.
    2.  He provides a store name ("Bob's Gadgets"), a logo, and a description.
    3.  The system creates a new `Store` entity linked to Bob's `Seller` account.
    4.  The admin approve his store.

### 3. Adding Products

*   **Action:** Bob adds his first `Product` to his `Store`.
*   **Steps:**
    1.  From his seller dashboard, Bob navigates to the "Products" section and clicks "Add New Product."
    2.  He fills out the product form with a title, description, price, and stock quantity.
    3.  He assigns the product to the "Gadgets" `Category`.
    4.  He uploads high-quality images for the product.
    5.  He waits for admin to approve his product.
    6.  The new `Product` is now live and visible to customers browsing the site.

### 4. Managing Orders

*   **Action:** A customer, Alice, purchases one of Bob's gadgets.
*   **Steps:**
    1.  Bob receives a `Notification` on his dashboard and via email about the new `Order`.
    2.  He views the order details, including the customer's shipping `Address`.
    3.  He packages the product and prepares it for shipping.
    4.  He updates the `Order` status to "Processing."

### 5. Fulfilling and Shipping

*   **Action:** Bob ships the order.
*   **Steps:**
    1.  Bob purchases a shipping label and gets a tracking number.
    2.  He updates the `Shipment` entity associated with the `Order` by adding the tracking number and changing the status to "Shipped."
    3.  This action automatically triggers a `Notification` to Alice with her tracking information.

### 6. Handling Customer Issues

*   **Action:** A customer has an issue and opens a `Ticket`.
*   **Steps:**
    1.  Bob receives a `Notification` about a new support `Ticket` related to one of his products.
    2.  He communicates with the customer via `Ticket_Message`s to resolve the issue.
    3.  Once the issue is resolved, he closes the `Ticket`.

### 7. Managing Discounts

*   **Action:** Bob wants to run a promotion to attract more customers.
*   **Steps:**
    1.  From his dashboard, Bob creates a new `Discount`.
    2.  He sets it to 15% off for all products in his `Store` for a limited time.
    3.  The `Discount` is now active and customers can use the generated code at checkout.


---

## Scenario: An Admin's First View

This scenario outlines the typical activities of a platform administrator, "Charlie," who is responsible for overseeing the entire e-commerce operation.

### 1. Admin Login and Dashboard Overview

*   **Action:** Charlie logs into the admin panel to perform daily checks.
*   **Steps:**
    1.  Charlie navigates to the admin login page (e.g., `/admin`) and enters his credentials. His `User` account has the "admin" `Role`.
    2.  He is greeted by the main dashboard, which provides a high-level overview of the platform's health:
        *   Total sales today.
        *   Number of new `User` and `Seller` sign-ups.
        *   Open support `Ticket`s.
        *   Recent `Order`s.

### 2. Admin Panels and Responsibilities

Charlie's interface is divided into several panels, each dedicated to a specific aspect of platform management.

#### a. User Management Panel

*   **Purpose:** To manage all `User` accounts, including customers and sellers.
*   **Tasks:**
    1.  **Approve Seller Accounts:** Charlie sees a pending `Seller` application from "Bob." He reviews the details and approves the account, which triggers a `Notification` to Bob.
    2.  **Manage Roles:** He can assign or revoke `Role`s. For example, he can promote a `User` to a support agent role.
    3.  **View User Details:** He can look up any user's `Order` history, `Address`es, and activity.
    4.  **Suspend Accounts:** If a user violates the terms of service, Charlie can suspend their account.

#### b. Product and Category Management Panel

*   **Purpose:** To oversee the entire product catalog.
*   **Tasks:**
    1.  **Manage Categories:** Charlie creates a new `Category` called "Wearables" for upcoming products.
    2.  **Feature Products:** He can mark certain `Product`s as "featured" to have them appear on the homepage.
    3.  **Review Comments:** He moderates `Comment`s left on products, removing any that are inappropriate.
    4.  **Approve New Sellers Products:** Charlie sees a pending `Product` application from "Bob". He reviews the details and approves the product, which triggers a `Notification` to Bob.
    5.  **Approve New Sellers Stores:** Charlie sees a pending `Store` application from "Bob". He reviews the details and approves the product, which triggers a `Notification` to Bob.

#### c. Order and Shipment Management Panel

*   **Purpose:** To monitor and manage all `Order`s and `Shipment`s.
*   **Tasks:**
    1.  **View All Orders:** Charlie can see a list of all orders, filterable by status (e.g., pending, shipped, delivered).
    2.  **Handle Disputes:** If a customer has an issue with an `Order` that the `Seller` cannot resolve, Charlie can intervene.
    3.  **Monitor Shipments:** He can track `Shipment`s to ensure sellers are meeting their delivery estimates.

#### d. Financials and Payments Panel

*   **Purpose:** To manage financial transactions, including `Payment`s and `Discount`s.
*   **Tasks:**
    1.  **Review Transactions:** Charlie reviews daily `Payment` records to check for fraud or errors.
    2.  **Manage Discounts:** He can create site-wide `Discount` codes for marketing campaigns.
    3.  **Process Payouts:** He oversees the process of paying out `Seller`s for their sales.

#### e. Support and Tickets Panel

*   **Purpose:** To manage customer and seller support.
*   **Tasks:**
    1.  **Monitor Tickets:** Charlie reviews open `Ticket`s to ensure they are being addressed in a timely manner.
    2.  **Assign Tickets:** He can assign complex `Ticket`s to specialized support agents.
    3.  **Create Knowledge Base:** He uses common questions from `Ticket_Message`s to create help articles for users.

#### f. Notifications and System Settings Panel

*   **Purpose:** To configure the platform and manage communications.
*   **Tasks:**
    1.  **Send Notifications:** Charlie can send platform-wide `Notification`s about maintenance or promotions.
    2.  **Configure Settings:** He can adjust settings like shipping options, tax rates, and payment gateways.
