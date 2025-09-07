from cmd import Cmd
from playwright.sync_api import sync_playwright
import sys
import json
import time
from datetime import datetime

class EcommerceTester(Cmd):
    intro = '''
    E-commerce Business Logic Tester v2.0
    
    Type help or ? to list commands.
    Type save_state to save current state.
    Type load_state to restore previous state.
    '''
    prompt = '(ecommerce-tester) '
    
    def __init__(self):
        super().__init__()
        self.browser = None
        self.page = None
        self.state = {
            'logged_in': False,
            'cart_items': [],
            'coupons_applied': [],
            'order_details': None,
            'errors': []
        }

    def do_save_state(self, args):
        """Save current state to a file: save_state [filename]"""
        filename = args if args else 'state.json'
        self.save_state(filename)

    def do_load_state(self, args):
        """Load state from a file: load_state [filename]"""
        filename = args if args else 'state.json'
        self.load_state(filename)

    def do_clear(self, args):
        """Clear the screen"""
        print("\033[H\033[J")
        
    def save_state(self, filename='state.json'):
        try:
            with open(filename, 'w') as f:
                json.dump(self.state, f)
            print(f"State saved to {filename}")
        except Exception as e:
            print(f"Error saving state: {str(e)}")
            
    def load_state(self, filename='state.json'):
        try:
            with open(filename, 'r') as f:
                self.state = json.load(f)
            print(f"State loaded from {filename}")
        except Exception as e:
            print(f"Error loading state: {str(e)}")
    
    def log_error(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.state['errors'].append({
            'timestamp': timestamp,
            'message': message
        })
        print(f"[ERROR] {timestamp}: {message}")
    
    def do_login(self, args):
        """Login to account: login email password"""
        if len(args.split()) != 2:
            print("Usage: login email password")
            return
            
        email, password = args.split()
        
        try:
            if not self.page:
                with sync_playwright() as p:
                    self.browser = p.chromium.launch(headless=False)
                    self.page = self.browser.new_page()
                    
            self.page.goto("https://example.com/login")
            self.page.fill('input[name="email"]', email)
            self.page.fill('input[name="password"]', password)
            self.page.click('button[type="submit"]')
            
            # Wait for redirect
            time.sleep(2)
            
            # Verify login success
            if self.page.url.startswith("https://example.com/dashboard"):
                self.state['logged_in'] = True
                self.state['current_user'] = email
                print(f"Logged in as {email}")
            else:
                self.log_error("Login failed - check credentials")
                
        except Exception as e:
            self.log_error(f"Login error: {str(e)}")
    
    def do_add_to_cart(self, args):
        """Add item to cart: add_to_cart product_id quantity"""
        if not self.state['logged_in']:
            print("Please login first")
            return
            
        try:
            product_id, quantity = args.split()
            quantity = int(quantity)
            
            self.page.goto(f"https://example.com/product/{product_id}")
            
            # Check product availability
            stock_status = self.page.query_selector('span.stock-status').inner_text()
            if "Out of Stock" in stock_status:
                self.log_error(f"Product {product_id} is out of stock")
                return
                
            # Add to cart
            self.page.fill('input[name="quantity"]', str(quantity))
            self.page.click('button.add-to-cart')
            
            # Wait for cart update
            time.sleep(1)
            
            # Verify item added
            cart_count = self.page.query_selector('span.cart-count').inner_text()
            if int(cart_count) >= len(self.state['cart_items']) + quantity:
                self.state['cart_items'].append({
                    'product_id': product_id,
                    'quantity': quantity,
                    'added_at': datetime.now().isoformat()
                })
                print(f"Added {quantity} x Product {product_id} to cart")
            else:
                self.log_error(f"Failed to add product {product_id} to cart")
                
        except Exception as e:
            self.log_error(f"Add to cart error: {str(e)}")
    
    def do_view_cart(self, args):
        """View current cart contents"""
        if not self.state['logged_in']:
            print("Please login first")
            return
            
        if not self.state['cart_items']:
            print("Cart is empty")
            return
            
        print("\nCurrent Cart:")
        print("=" * 80)
        print(f"{'Product ID':<15} {'Quantity':<10} {'Added At':<30}")
        print("-" * 80)
        
        for item in self.state['cart_items']:
            print(f"{item['product_id']:<15} {item['quantity']:<10} {item['added_at']:<30}")
            
        print("=" * 80)
        print(f"\nTotal Items: {sum(i['quantity'] for i in self.state['cart_items'])}")
    
    def do_checkout(self, args):
        """Proceed to checkout"""
        if not self.state['logged_in']:
            print("Please login first")
            return
            
        if not self.state['cart_items']:
            print("Cart is empty - nothing to checkout")
            return
            
        try:
            self.page.click('a.checkout-button')
            
            # Wait for checkout page
            time.sleep(2)
            
            if self.page.url.startswith("https://example.com/checkout"):
                print("Proceeding to checkout")
            else:
                self.log_error("Checkout failed - please verify cart")
                
        except Exception as e:
            self.log_error(f"Checkout error: {str(e)}")
    
    def do_apply_coupon(self, args):
        """Apply discount coupon: apply_coupon COUPON_CODE"""
        if not self.state['logged_in']:
            print("Please login first")
            return
            
        try:
            self.page.fill('input[name="coupon"]', args)
            self.page.click('button.apply-coupon')
            
            # Wait for coupon processing
            time.sleep(2)
            
            # Check for coupon success/error messages
            if self.page.query_selector('div.coupon-success'):
                self.state['coupons_applied'].append({
                    'code': args,
                    'applied_at': datetime.now().isoformat()
                })
                print(f"Applied coupon {args}")
            elif self.page.query_selector('div.coupon-error'):
                self.log_error(f"Coupon error: {self.page.query_selector('div.coupon-error').inner_text()}")
            else:
                self.log_error("Coupon application status unknown")
                
        except Exception as e:
            self.log_error(f"Coupon error: {str(e)}")
    
    def do_submit_order(self, args):
        """Submit order"""
        if not self.state['logged_in']:
            print("Please login first")
            return
            
        if not self.state['cart_items']:
            print("Cart is empty - nothing to order")
            return
            
        try:
            # Fill payment details
            self.page.select_option('select[name="payment-method"]', 'credit-card')
            self.page.fill('input[name="card-number"]', "4111111111111111")
            self.page.fill('input[name="card-expiry"]', "12/25")
            self.page.fill('input[name="card-cvv"]', "123")
            
            # Submit order
            self.page.click('button.submit-order')
            
            # Wait for order confirmation
            time.sleep(3)
            
            if self.page.query_selector('div.order-confirmation'):
                order_id = self.page.query_selector('span.order-id').inner_text()
                self.state['order_details'] = {
                    'order_id': order_id,
                    'submitted_at': datetime.now().isoformat(),
                    'items': self.state['cart_items'],
                    'coupons': self.state['coupons_applied']
                }
                print(f"Order submitted successfully! Order ID: {order_id}")
                
                # Clear cart
                self.state['cart_items'] = []
                self.state['coupons_applied'] = []
            else:
                self.log_error("Order submission failed - please check payment details")
                
        except Exception as e:
            self.log_error(f"Order submission error: {str(e)}")
    
    def do_view_order_history(self, args):
        """View order history"""
        if not self.state['logged_in']:
            print("Please login first")
            return
            
        if not self.state['order_details']:
            print("No orders placed yet")
            return
            
        print("\nOrder History:")
        print("=" * 80)
        print(f"{'Order ID':<15} {'Submitted At':<30} {'Items':<10}")
        print("-" * 80)
        
        print(f"{self.state['order_details']['order_id']:<15} {self.state['order_details']['submitted_at']:<30} {len(self.state['order_details']['items']):<10}")
        
        print("=" * 80)
    
    def do_test_inventory_limit(self, args):
        """Test inventory limits: test_inventory_limit product_id max_quantity"""
        if not self.state['logged_in']:
            print("Please login first")
            return
            
        try:
            product_id, max_quantity = args.split()
            max_quantity = int(max_quantity)
            
            # Save current cart state
            original_cart = self.state['cart_items'].copy()
            
            # Attempt to add more than max quantity
            self.do_add_to_cart(f"{product_id} {max_quantity + 1}")
            
            # Verify cart hasn't changed
            if len(self.state['cart_items']) > len(original_cart):
                self.log_error(f"Inventory limit test failed: able to add {max_quantity + 1} items when limit is {max_quantity}")
            else:
                print(f"Inventory limit test passed for quantity {max_quantity + 1}")

            # Restore cart
            self.state['cart_items'] = original_cart
            
            # Attempt to add exactly max quantity
            self.do_add_to_cart(f"{product_id} {max_quantity}")

            # Verify cart has changed
            if len(self.state['cart_items']) == len(original_cart) + 1:
                print(f"Inventory limit test passed for quantity {max_quantity}")
            else:
                self.log_error(f"Inventory limit test failed: unable to add {max_quantity} items when limit is {max_quantity}")

            # Restore cart
            self.state['cart_items'] = original_cart
            print("Inventory limit test finished.")

        except Exception as e:
            self.log_error(f"Inventory limit test error: {str(e)}")

    def do_quit(self, args):
        """Exit the application."""
        if self.browser:
            self.browser.close()
        return True

    def do_exit(self, args):
        """Exit the application."""
        return self.do_quit(args)

if __name__ == '__main__':
    EcommerceTester().cmdloop()
            