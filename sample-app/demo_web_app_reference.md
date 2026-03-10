# SauceDemo Reference

## URL
https://www.saucedemo.com

## Credentials
| Username | Password | Notes |
|---|---|---|
| standard_user | secret_sauce | Primary test user |
| locked_out_user | secret_sauce | Locked account |
| problem_user | secret_sauce | Broken images |
| performance_glitch_user | secret_sauce | Slow load simulation |
| error_user | secret_sauce | Cart errors |
| visual_user | secret_sauce | Visual layout bugs |

## Page Structure

### Login Page (`/`)
- Username input: `[data-test="username"]` / `#user-name`
- Password input: `[data-test="password"]` / `#password`
- Login button: `[data-test="login-button"]` / `#login-button`
- Error container: `[data-test="error"]` / `.error-message-container`

### Inventory Page (`/inventory.html`)
- Product list: `.inventory_list`
- Each product card: `.inventory_item`
- Product name: `.inventory_item_name`
- Product price: `.inventory_item_price`
- Add to cart button: `[data-test^="add-to-cart-"]`
- Remove button: `[data-test^="remove-"]`
- Cart badge: `.shopping_cart_badge`
- Cart link: `.shopping_cart_link`
- Sort dropdown: `[data-test="product_sort_container"]`
- Sort values: `az` (A-Z), `za` (Z-A), `lohi` (price asc), `hilo` (price desc)

### Cart Page (`/cart.html`)
- Cart items: `.cart_item`
- Item name: `.inventory_item_name`
- Item price: `.inventory_item_price`
- Remove button: `[data-test^="remove-"]`
- Continue shopping: `[data-test="continue-shopping"]`
- Checkout: `[data-test="checkout"]`

### Checkout Step 1 (`/checkout-step-one.html`)
- First name: `[data-test="firstName"]` / `#first-name`
- Last name: `[data-test="lastName"]` / `#last-name`
- Zip/Postal: `[data-test="postalCode"]` / `#postal-code`
- Continue: `[data-test="continue"]` / `#continue`
- Cancel: `[data-test="cancel"]`

### Checkout Step 2 (`/checkout-step-two.html`)
- Item total: `.summary_subtotal_label`
- Tax: `.summary_tax_label`
- Total: `.summary_total_label`
- Finish: `[data-test="finish"]` / `#finish`
- Cancel: `[data-test="cancel"]`

### Order Confirmation (`/checkout-complete.html`)
- Header: `.complete-header` — text: "Thank you for your order!"
- Back home: `[data-test="back-to-products"]`

### Navigation Menu
- Hamburger: `#react-burger-menu-btn`
- All Items: `#inventory_sidebar_link`
- About: `#about_sidebar_link`
- Logout: `#logout_sidebar_link`
- Reset App State: `#reset_sidebar_link`

## Key Assertions
- After login: URL contains `/inventory.html`
- After logout: URL is `https://www.saucedemo.com/`
- After order: `.complete-header` text === "Thank you for your order!"
- Cart badge: `.shopping_cart_badge` text === expected item count
