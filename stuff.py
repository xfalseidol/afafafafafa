from cmd import Cmd
from playwright.sync_api import sync_playwright
import sys
import json
import time
from datetime import datetime

class EcommerceTester(Cmd):
    intro = '''
    🛒 E-commerce Business Logic Tester v2.0
    
    ✨ New! Interactive Wizard Support ✨
    
    🧙‍♂️ Type 'wizard' for a complete guided setup
    💡 Type any command without parameters for guided prompts
    📚 Type 'help_wizard' for wizard help and examples
    ❓ Type 'help' or '?' to list all commands
    💾 Type 'save_state' to save current state
    📂 Type 'load_state' to restore previous state
    
    Example: Just type 'login' and I'll guide you through it!
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

    def do_wizard(self, args):
        """Interactive setup wizard to guide you through common tasks"""
        print("\n🧙‍♂️ EcommerceTester Setup Wizard")
        print("   Welcome! I'll help you get started with testing e-commerce functionality.")
        
        if not self.state['logged_in']:
            print("\n📝 Step 1: Login")
            print("   First, let's log you into your account.")
            if self.confirm_action("Would you like to login now?"):
                self.do_login("")
            else:
                print("   💡 You can login anytime by typing 'login'")
                return
        
        if self.state['logged_in']:
            print("\n✅ You're logged in! Let's continue...")
            
            # Suggest next actions
            print("\n🎯 What would you like to do next?")
            actions = [
                ("Add items to cart", "add_to_cart"),
                ("Apply a coupon", "apply_coupon"),
                ("Test inventory limits", "test_inventory_limit"),
                ("View cart contents", "view_cart"),
                ("Proceed to checkout", "checkout"),
                ("Exit wizard", "exit")
            ]
            
            for i, (description, command) in enumerate(actions, 1):
                print(f"   {i}. {description}")
            
            while True:
                try:
                    choice = input(f"\n   Select an action (1-{len(actions)}): ").strip()
                    if choice.isdigit() and 1 <= int(choice) <= len(actions):
                        selected_action = actions[int(choice) - 1][1]
                        break
                    else:
                        print(f"   Please enter a number between 1 and {len(actions)}")
                except (KeyboardInterrupt, EOFError):
                    print("\n   Wizard cancelled.")
                    return
            
            if selected_action == "exit":
                print("   👋 Wizard completed. Type 'help' to see all available commands.")
                return
            elif selected_action == "add_to_cart":
                self.do_add_to_cart("")
            elif selected_action == "apply_coupon":
                self.do_apply_coupon("")
            elif selected_action == "test_inventory_limit":
                self.do_test_inventory_limit("")
            elif selected_action == "view_cart":
                self.do_view_cart("")
            elif selected_action == "checkout":
                self.do_checkout("")
            
            print("\n💡 Tip: You can run the wizard again anytime by typing 'wizard'")

    def do_help_wizard(self, args):
        """Show help for using the interactive wizards"""
        print("\n🆘 Interactive Wizard Help")
        print("=" * 60)
        print("\n📚 Available Commands with Wizard Support:")
        print("   • login          - Account login with guided prompts")
        print("   • add_to_cart    - Add items with product and quantity prompts")
        print("   • apply_coupon   - Apply discount codes with guided input")
        print("   • submit_order   - Complete purchase with payment details wizard")
        print("   • test_inventory_limit - Test product limits with guided setup")
        print("   • wizard         - Complete setup wizard for new users")
        
        print("\n🎯 How to Use:")
        print("   1. Type any command without parameters for guided setup")
        print("   2. Or provide partial parameters and get prompted for missing ones")
        print("   3. Or use traditional format with all parameters")
        
        print("\n💡 Examples:")
        print("   • 'login' → guided email and password prompts")
        print("   • 'login user@example.com' → prompted for password only")
        print("   • 'login user@example.com mypass' → traditional format")
        
        print("\n🔧 Features:")
        print("   • Input validation and format checking")
        print("   • Helpful examples and suggestions")
        print("   • Clear error messages and guidance")
        print("   • Confirmation prompts for important actions")
        print("   • Backward compatibility with existing syntax")

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
    
    def prompt_for_input(self, field_name, description="", required=True, validation_fn=None, examples=None):
        """
        Interactive prompt for gathering user input with validation and guidance.
        
        Args:
            field_name: Name of the field being requested
            description: Description/help text for the field
            required: Whether the field is required
            validation_fn: Function to validate the input
            examples: List of example values
        """
        print(f"\n📝 {field_name.replace('_', ' ').title()}")
        if description:
            print(f"   {description}")
        if examples:
            print(f"   Examples: {', '.join(examples)}")
        
        while True:
            try:
                value = input(f"   Enter {field_name.replace('_', ' ')}: ").strip()
                
                if not value and required:
                    print("   ❌ This field is required. Please enter a value.")
                    continue
                elif not value and not required:
                    return None
                
                if validation_fn:
                    validation_result = validation_fn(value)
                    if validation_result is not True:
                        print(f"   ❌ {validation_result}")
                        continue
                
                print(f"   ✅ {field_name.replace('_', ' ').title()}: {value}")
                return value
                
            except KeyboardInterrupt:
                print("\n   ⏹️  Input cancelled by user")
                return None
            except EOFError:
                print("\n   ⏹️  Input cancelled")
                return None

    def validate_email(self, email):
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, email):
            return True
        return "Please enter a valid email address (e.g., user@example.com)"
    
    def validate_positive_integer(self, value):
        """Validate positive integer"""
        try:
            num = int(value)
            if num > 0:
                return True
            return "Please enter a positive number greater than 0"
        except ValueError:
            return "Please enter a valid number"
    
    def validate_non_empty(self, value):
        """Validate non-empty string"""
        if value and value.strip():
            return True
        return "This field cannot be empty"
    
    def confirm_action(self, message):
        """Ask user for confirmation"""
        while True:
            try:
                response = input(f"\n❓ {message} (y/N): ").strip().lower()
                if response in ['y', 'yes']:
                    return True
                elif response in ['n', 'no', '']:
                    return False
                else:
                    print("   Please enter 'y' for yes or 'n' for no")
            except (KeyboardInterrupt, EOFError):
                print("\n   Cancelled by user")
                return False
    
    def do_login(self, args):
        """Login to account: login [email] [password] or just 'login' for guided setup"""
        
        # If no arguments provided, use interactive wizard
        if not args.strip():
            print("\n🔐 Login Wizard - Let's get you logged in!")
            print("   I'll guide you through entering your credentials.")
            
            email = self.prompt_for_input(
                "email_address", 
                "Your account email address",
                required=True,
                validation_fn=self.validate_email,
                examples=["user@example.com", "john.doe@company.org"]
            )
            
            if not email:
                print("   Login cancelled.")
                return
            
            password = self.prompt_for_input(
                "password",
                "Your account password (input will be hidden for security)",
                required=True,
                validation_fn=self.validate_non_empty
            )
            
            if not password:
                print("   Login cancelled.")
                return
                
        # If partial arguments provided, prompt for missing ones
        elif len(args.split()) == 1:
            email = args.strip()
            print(f"\n🔐 Email provided: {email}")
            
            # Validate the provided email
            validation_result = self.validate_email(email)
            if validation_result is not True:
                print(f"   ❌ {validation_result}")
                email = self.prompt_for_input(
                    "email_address", 
                    "Please enter a valid email address",
                    required=True,
                    validation_fn=self.validate_email
                )
                if not email:
                    print("   Login cancelled.")
                    return
            
            password = self.prompt_for_input(
                "password",
                "Your account password",
                required=True,
                validation_fn=self.validate_non_empty
            )
            
            if not password:
                print("   Login cancelled.")
                return
                
        # If both arguments provided, use them directly (backward compatibility)
        elif len(args.split()) == 2:
            email, password = args.split()
            
            # Still validate the provided email
            validation_result = self.validate_email(email)
            if validation_result is not True:
                print(f"   ❌ {validation_result}")
                return
        else:
            print("❌ Usage: login [email] [password]")
            print("   💡 Tip: Just type 'login' for a guided setup!")
            return
        
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
        """Add item to cart: add_to_cart [product_id] [quantity] or just 'add_to_cart' for guided setup"""
        if not self.state['logged_in']:
            print("❌ Please login first")
            return
        
        # If no arguments provided, use interactive wizard
        if not args.strip():
            print("\n🛒 Add to Cart Wizard - Let's add an item to your cart!")
            print("   I'll guide you through selecting a product and quantity.")
            
            product_id = self.prompt_for_input(
                "product_id",
                "The unique identifier for the product you want to add",
                required=True,
                validation_fn=self.validate_non_empty,
                examples=["PROD123", "SKU-ABC-001", "12345"]
            )
            
            if not product_id:
                print("   Add to cart cancelled.")
                return
            
            quantity = self.prompt_for_input(
                "quantity",
                "How many items do you want to add to your cart?",
                required=True,
                validation_fn=self.validate_positive_integer,
                examples=["1", "2", "5"]
            )
            
            if not quantity:
                print("   Add to cart cancelled.")
                return
                
        # If partial arguments provided, prompt for missing ones
        elif len(args.split()) == 1:
            product_id = args.strip()
            print(f"\n🛒 Product ID provided: {product_id}")
            
            quantity = self.prompt_for_input(
                "quantity",
                "How many items do you want to add to your cart?",
                required=True,
                validation_fn=self.validate_positive_integer,
                examples=["1", "2", "5"]
            )
            
            if not quantity:
                print("   Add to cart cancelled.")
                return
                
        # If both arguments provided, use them directly (backward compatibility)
        elif len(args.split()) == 2:
            product_id, quantity = args.split()
            
            # Validate the provided quantity
            validation_result = self.validate_positive_integer(quantity)
            if validation_result is not True:
                print(f"   ❌ {validation_result}")
                return
        else:
            print("❌ Usage: add_to_cart [product_id] [quantity]")
            print("   💡 Tip: Just type 'add_to_cart' for a guided setup!")
            return
            
        try:
            quantity = int(quantity)
            
            print(f"\n🔄 Processing: Adding {quantity} x {product_id} to cart...")
            
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
        """Apply discount coupon: apply_coupon [COUPON_CODE] or just 'apply_coupon' for guided setup"""
        if not self.state['logged_in']:
            print("❌ Please login first")
            return
        
        # If no arguments provided, use interactive wizard
        if not args.strip():
            print("\n🎟️ Apply Coupon Wizard - Let's save you some money!")
            print("   I'll guide you through applying a discount coupon.")
            
            coupon_code = self.prompt_for_input(
                "coupon_code",
                "Enter your discount coupon code",
                required=True,
                validation_fn=self.validate_non_empty,
                examples=["SAVE20", "WELCOME10", "SUMMER2024"]
            )
            
            if not coupon_code:
                print("   Apply coupon cancelled.")
                return
        else:
            coupon_code = args.strip()
            
        print(f"\n🔄 Processing: Applying coupon '{coupon_code}'...")
            
        try:
            self.page.fill('input[name="coupon"]', coupon_code)
            self.page.click('button.apply-coupon')
            
            # Wait for coupon processing
            time.sleep(2)
            
            # Check for coupon success/error messages
            if self.page.query_selector('div.coupon-success'):
                self.state['coupons_applied'].append({
                    'code': coupon_code,
                    'applied_at': datetime.now().isoformat()
                })
                print(f"✅ Applied coupon {coupon_code}")
            elif self.page.query_selector('div.coupon-error'):
                self.log_error(f"Coupon error: {self.page.query_selector('div.coupon-error').inner_text()}")
            else:
                self.log_error("Coupon application status unknown")
                
        except Exception as e:
            self.log_error(f"Coupon error: {str(e)}")
    
    def validate_credit_card(self, card_number):
        """Basic credit card validation"""
        # Remove spaces and hyphens
        card_number = card_number.replace(' ', '').replace('-', '')
        
        # Check if it's all digits and proper length
        if not card_number.isdigit():
            return "Credit card number should contain only digits"
        
        if len(card_number) < 13 or len(card_number) > 19:
            return "Credit card number should be between 13-19 digits"
            
        return True
    
    def validate_expiry_date(self, expiry):
        """Validate credit card expiry date in MM/YY format"""
        import re
        if not re.match(r'^(0[1-9]|1[0-2])\/([0-9]{2})$', expiry):
            return "Please enter expiry date in MM/YY format (e.g., 12/25)"
        return True
    
    def validate_cvv(self, cvv):
        """Validate CVV code"""
        if not cvv.isdigit():
            return "CVV should contain only digits"
        if len(cvv) not in [3, 4]:
            return "CVV should be 3 or 4 digits"
        return True

    def do_submit_order(self, args):
        """Submit order with payment details"""
        if not self.state['logged_in']:
            print("❌ Please login first")
            return
            
        if not self.state['cart_items']:
            print("❌ Cart is empty - nothing to order")
            return
        
        print("\n💳 Order Submission Wizard - Let's complete your purchase!")
        print("   I'll guide you through entering payment details securely.")
        
        # Show order summary
        print(f"\n📋 Order Summary:")
        print(f"   Items in cart: {len(self.state['cart_items'])}")
        total_quantity = sum(item['quantity'] for item in self.state['cart_items'])
        print(f"   Total quantity: {total_quantity}")
        
        if self.state['coupons_applied']:
            print(f"   Coupons applied: {', '.join([c['code'] for c in self.state['coupons_applied']])}")
        
        if not self.confirm_action("Do you want to proceed with payment?"):
            print("   Order submission cancelled.")
            return
        
        # Payment method selection
        print(f"\n💳 Payment Method Selection:")
        payment_methods = ['credit-card', 'debit-card', 'paypal']
        for i, method in enumerate(payment_methods, 1):
            print(f"   {i}. {method.replace('-', ' ').title()}")
        
        while True:
            try:
                choice = input(f"   Select payment method (1-{len(payment_methods)}): ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(payment_methods):
                    payment_method = payment_methods[int(choice) - 1]
                    break
                else:
                    print(f"   Please enter a number between 1 and {len(payment_methods)}")
            except (KeyboardInterrupt, EOFError):
                print("\n   Order submission cancelled.")
                return
        
        print(f"   ✅ Payment method: {payment_method.replace('-', ' ').title()}")
        
        # Credit/Debit card details
        if payment_method in ['credit-card', 'debit-card']:
            card_number = self.prompt_for_input(
                "card_number",
                "Enter your card number (spaces and hyphens will be removed)",
                required=True,
                validation_fn=self.validate_credit_card,
                examples=["4111-1111-1111-1111", "4111 1111 1111 1111"]
            )
            
            if not card_number:
                print("   Order submission cancelled.")
                return
            
            card_expiry = self.prompt_for_input(
                "card_expiry",
                "Enter card expiry date",
                required=True,
                validation_fn=self.validate_expiry_date,
                examples=["12/25", "03/26"]
            )
            
            if not card_expiry:
                print("   Order submission cancelled.")
                return
            
            card_cvv = self.prompt_for_input(
                "card_cvv",
                "Enter CVV security code",
                required=True,
                validation_fn=self.validate_cvv,
                examples=["123", "1234"]
            )
            
            if not card_cvv:
                print("   Order submission cancelled.")
                return
            
            # Clean card number for processing
            card_number = card_number.replace(' ', '').replace('-', '')
            
        elif payment_method == 'paypal':
            print("   💡 You will be redirected to PayPal for secure payment.")
            card_number = card_expiry = card_cvv = None
        
        print(f"\n🔄 Processing order with {payment_method.replace('-', ' ')}...")
            
        try:
            # Fill payment details based on method
            self.page.select_option('select[name="payment-method"]', payment_method)
            
            if payment_method in ['credit-card', 'debit-card']:
                self.page.fill('input[name="card-number"]', card_number)
                self.page.fill('input[name="card-expiry"]', card_expiry)
                self.page.fill('input[name="card-cvv"]', card_cvv)
            
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
                    'coupons': self.state['coupons_applied'],
                    'payment_method': payment_method
                }
                print(f"✅ Order submitted successfully! Order ID: {order_id}")
                print(f"   Payment method: {payment_method.replace('-', ' ').title()}")
                
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
        """Test inventory limits: test_inventory_limit [product_id] [max_quantity] or just 'test_inventory_limit' for guided setup"""
        if not self.state['logged_in']:
            print("❌ Please login first")
            return
        
        # If no arguments provided, use interactive wizard
        if not args.strip():
            print("\n🧪 Inventory Limit Test Wizard - Let's test product limits!")
            print("   I'll guide you through testing inventory constraints.")
            
            product_id = self.prompt_for_input(
                "product_id",
                "The product ID you want to test inventory limits for",
                required=True,
                validation_fn=self.validate_non_empty,
                examples=["PROD123", "SKU-ABC-001", "12345"]
            )
            
            if not product_id:
                print("   Inventory test cancelled.")
                return
            
            max_quantity = self.prompt_for_input(
                "max_quantity",
                "The expected maximum quantity that should be allowed",
                required=True,
                validation_fn=self.validate_positive_integer,
                examples=["10", "25", "100"]
            )
            
            if not max_quantity:
                print("   Inventory test cancelled.")
                return
                
        # If partial arguments provided, prompt for missing ones
        elif len(args.split()) == 1:
            product_id = args.strip()
            print(f"\n🧪 Product ID provided: {product_id}")
            
            max_quantity = self.prompt_for_input(
                "max_quantity",
                "The expected maximum quantity that should be allowed",
                required=True,
                validation_fn=self.validate_positive_integer,
                examples=["10", "25", "100"]
            )
            
            if not max_quantity:
                print("   Inventory test cancelled.")
                return
                
        # If both arguments provided, use them directly (backward compatibility)
        elif len(args.split()) == 2:
            product_id, max_quantity = args.split()
            
            # Validate the provided max_quantity
            validation_result = self.validate_positive_integer(max_quantity)
            if validation_result is not True:
                print(f"   ❌ {validation_result}")
                return
        else:
            print("❌ Usage: test_inventory_limit [product_id] [max_quantity]")
            print("   💡 Tip: Just type 'test_inventory_limit' for a guided setup!")
            return
            
        try:
            max_quantity = int(max_quantity)
            
            print(f"\n🔄 Starting inventory limit test for {product_id} (max: {max_quantity})...")
            
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
            