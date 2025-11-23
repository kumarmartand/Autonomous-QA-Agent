# Product Specifications - E-Shop Checkout System

## Overview
This document defines the functional specifications for the E-Shop Checkout system, including cart management, discount codes, shipping options, and payment processing.

## Cart Functionality

### Add to Cart
- Users can add items to cart by clicking the "Add to Cart" button
- Each item has a quantity input field that can be manually adjusted
- Quantity can be set to 0 or any positive integer
- Cart automatically updates the total price when quantities change

### Cart Items
The checkout page includes the following products:
1. **Wireless Headphones** - Price: $99.99
2. **Smart Watch** - Price: $199.99
3. **Laptop Stand** - Price: $49.99

### Cart Summary
The cart summary displays:
- **Subtotal**: Sum of all item prices multiplied by quantities
- **Discount**: Applied discount amount (if any)
- **Shipping**: Shipping cost based on selected method
- **Total**: Final amount after discount and shipping

## Discount Code System

### Valid Discount Codes
- **SAVE15**: Applies a 15% discount to the subtotal
  - This is the only valid discount code in the system
  - Case-insensitive matching
  - Must be entered exactly as "SAVE15" (without quotes)

### Discount Application Rules
- Discount is applied to the subtotal (before shipping)
- Discount amount is calculated as: `subtotal × discount_percentage`
- If an invalid code is entered, no discount is applied
- Discount can be removed by clearing the discount code field

### Discount Display
- When a valid code is applied, a success message is displayed
- When an invalid code is entered, an error message is shown
- The discount amount is displayed in the cart summary as a negative value

## Shipping Methods

### Standard Shipping
- **Cost**: Free ($0.00)
- **Default selection**: Yes
- No additional charges

### Express Shipping
- **Cost**: $10.00
- Additional fee applied to the total
- Selected via radio button

### Shipping Selection
- Users select shipping method via radio buttons
- Only one shipping method can be selected at a time
- Shipping cost updates the total immediately upon selection change

## Payment Methods

### Available Payment Options
1. **Credit Card**
   - Default selection
   - Selected via radio button

2. **PayPal**
   - Alternative payment option
   - Selected via radio button

### Payment Processing
- Only one payment method can be selected at a time
- Selection does not affect the total price
- Payment method is required before proceeding

## User Details Form

### Required Fields
All fields in the user details form are required:
1. **Name** (text input)
   - Cannot be empty
   - Validation: Required field check

2. **Email** (email input)
   - Cannot be empty
   - Validation: Must be a valid email format (contains @ and domain)
   - Format validation: Standard email regex pattern

3. **Address** (textarea)
   - Cannot be empty
   - Validation: Required field check

### Form Validation Rules
- All required fields must be filled before payment can be processed
- Email must match the pattern: `[text]@[domain].[extension]`
- Validation errors are displayed in red text below each field
- Errors appear when:
  - Field is left empty and user attempts to submit
  - Email format is invalid
  - Field loses focus (on blur) and is invalid

### Error Messages
- **Name**: "Name is required"
- **Email**: "Please enter a valid email address" or "Email is required"
- **Address**: "Address is required"
- Error messages are displayed in red text
- Error messages appear inline below the respective input field

## Payment Processing

### Pay Now Button
- Button text: "Pay Now"
- Button color: Green (#28a745)
- Located at the bottom of the form
- Triggers form validation when clicked

### Payment Success
- When form is valid and "Pay Now" is clicked:
  - A success message is displayed: "✅ Payment Successful!"
  - Success message appears in a green background box
  - Message is centered and prominently displayed
  - Page scrolls to show the success message

### Payment Validation Flow
1. User clicks "Pay Now" button
2. System validates all form fields:
   - Name is not empty
   - Email is not empty and has valid format
   - Address is not empty
3. If validation passes:
   - Display success message
4. If validation fails:
   - Show error messages for invalid fields
   - Prevent payment processing

## UI/UX Requirements

### Visual Design
- "Pay Now" button should be green
- Error messages should be displayed in red text
- Success message should have a green background
- Form should have clear visual hierarchy

### User Experience
- Real-time validation feedback (on field blur)
- Clear error messaging
- Intuitive form layout
- Responsive design for different screen sizes

## Technical Specifications

### Element IDs
- Cart quantity inputs: `quantity-headphones`, `quantity-watch`, `quantity-stand`
- Discount code input: `discount-code`
- Name input: `name`
- Email input: `email`
- Address textarea: `address`
- Shipping radio buttons: `shipping-standard`, `shipping-express`
- Payment radio buttons: `payment-credit`, `payment-paypal`
- Pay button: `pay-button`
- Success message: `success-message`

### Element Names
- Shipping: `shipping`
- Payment: `payment`

### Classes
- Error messages: `error-message` with `show` class when visible
- Success message: `success-message` with `show` class when visible

