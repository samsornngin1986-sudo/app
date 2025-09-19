#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Marq' E Donuts Management System
Tests all backend API endpoints and business logic
"""

import requests
import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Any

# Configuration
BASE_URL = "https://donut-analytics-pro.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

class DonutShopTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS
        self.test_results = []
        self.created_products = []
        self.created_employees = []
        self.created_customers = []
        
    def log_test(self, test_name: str, success: bool, message: str, details: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def make_request(self, method: str, endpoint: str, data: Dict = None) -> tuple:
        """Make HTTP request and return (success, response_data, status_code)"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=self.headers, json=data, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=self.headers, timeout=30)
            else:
                return False, {"error": f"Unsupported method: {method}"}, 0
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}
            
            return response.status_code < 400, response_data, response.status_code
        except requests.exceptions.RequestException as e:
            return False, {"error": str(e)}, 0
    
    def test_product_crud_operations(self):
        """Test Product CRUD operations for all categories"""
        print("\n🧪 Testing Product CRUD Operations...")
        
        # Test data for different categories
        test_products = [
            {
                "name": "Glazed Original Donut",
                "category": "donuts",
                "price": 1.25,
                "cost": 0.45,
                "description": "Classic glazed donut with sweet glaze",
                "ingredients": ["flour", "sugar", "eggs", "butter", "yeast", "glaze"],
                "prep_time": 30,
                "is_available": True
            },
            {
                "name": "Breakfast Taco Supreme",
                "category": "tacos",
                "price": 3.50,
                "cost": 1.20,
                "description": "Scrambled eggs, bacon, cheese, and salsa",
                "ingredients": ["tortilla", "eggs", "bacon", "cheese", "salsa", "peppers"],
                "prep_time": 15,
                "is_available": True
            },
            {
                "name": "Sausage Kolache",
                "category": "kolaches",
                "price": 2.75,
                "cost": 0.95,
                "description": "Traditional Czech pastry with sausage filling",
                "ingredients": ["dough", "sausage", "cheese", "onions"],
                "prep_time": 45,
                "is_available": True
            },
            {
                "name": "Butter Croissant",
                "category": "croissants",
                "price": 2.25,
                "cost": 0.75,
                "description": "Flaky, buttery French croissant",
                "ingredients": ["flour", "butter", "eggs", "milk", "salt"],
                "prep_time": 60,
                "is_available": True
            },
            {
                "name": "House Blend Coffee",
                "category": "coffee",
                "price": 2.50,
                "cost": 0.35,
                "description": "Medium roast coffee blend",
                "ingredients": ["coffee beans", "water"],
                "prep_time": 5,
                "is_available": True
            },
            {
                "name": "Fresh Orange Juice",
                "category": "beverages",
                "price": 3.25,
                "cost": 1.10,
                "description": "Freshly squeezed orange juice",
                "ingredients": ["oranges"],
                "prep_time": 10,
                "is_available": True
            }
        ]
        
        # Test CREATE products
        for product_data in test_products:
            success, response, status_code = self.make_request("POST", "/products", product_data)
            if success and "id" in response:
                self.created_products.append(response)
                self.log_test(
                    f"Create Product - {product_data['name']}", 
                    True, 
                    f"Created {product_data['category']} product successfully",
                    {"product_id": response["id"], "status_code": status_code}
                )
            else:
                self.log_test(
                    f"Create Product - {product_data['name']}", 
                    False, 
                    f"Failed to create product",
                    {"response": response, "status_code": status_code}
                )
        
        # Test GET all products
        success, response, status_code = self.make_request("GET", "/products")
        if success and isinstance(response, list):
            self.log_test(
                "Get All Products", 
                True, 
                f"Retrieved {len(response)} products",
                {"count": len(response), "status_code": status_code}
            )
        else:
            self.log_test(
                "Get All Products", 
                False, 
                "Failed to retrieve products",
                {"response": response, "status_code": status_code}
            )
        
        # Test GET products by category
        categories = ["donuts", "tacos", "kolaches", "croissants", "coffee", "beverages"]
        for category in categories:
            success, response, status_code = self.make_request("GET", f"/products?category={category}")
            if success and isinstance(response, list):
                category_count = len(response)
                self.log_test(
                    f"Get Products by Category - {category}", 
                    True, 
                    f"Retrieved {category_count} {category} products",
                    {"count": category_count, "status_code": status_code}
                )
            else:
                self.log_test(
                    f"Get Products by Category - {category}", 
                    False, 
                    f"Failed to retrieve {category} products",
                    {"response": response, "status_code": status_code}
                )
        
        # Test GET single product
        if self.created_products:
            product_id = self.created_products[0]["id"]
            success, response, status_code = self.make_request("GET", f"/products/{product_id}")
            if success and "id" in response:
                self.log_test(
                    "Get Single Product", 
                    True, 
                    f"Retrieved product: {response.get('name', 'Unknown')}",
                    {"product_id": product_id, "status_code": status_code}
                )
            else:
                self.log_test(
                    "Get Single Product", 
                    False, 
                    "Failed to retrieve single product",
                    {"response": response, "status_code": status_code}
                )
        
        # Test UPDATE product
        if self.created_products:
            product_id = self.created_products[0]["id"]
            update_data = {
                "price": 1.50,
                "description": "Updated classic glazed donut with premium glaze"
            }
            success, response, status_code = self.make_request("PUT", f"/products/{product_id}", update_data)
            if success and response.get("price") == 1.50:
                self.log_test(
                    "Update Product", 
                    True, 
                    "Product updated successfully",
                    {"product_id": product_id, "new_price": response.get("price"), "status_code": status_code}
                )
            else:
                self.log_test(
                    "Update Product", 
                    False, 
                    "Failed to update product",
                    {"response": response, "status_code": status_code}
                )
    
    def test_inventory_management(self):
        """Test Inventory Management with Stock Alerts"""
        print("\n🧪 Testing Inventory Management...")
        
        # Test GET all inventory
        success, response, status_code = self.make_request("GET", "/inventory")
        if success and isinstance(response, list):
            self.log_test(
                "Get All Inventory", 
                True, 
                f"Retrieved {len(response)} inventory items",
                {"count": len(response), "status_code": status_code}
            )
        else:
            self.log_test(
                "Get All Inventory", 
                False, 
                "Failed to retrieve inventory",
                {"response": response, "status_code": status_code}
            )
        
        # Test inventory updates for created products
        if self.created_products:
            for i, product in enumerate(self.created_products[:3]):  # Test first 3 products
                product_id = product["id"]
                
                # Test GET single inventory item
                success, response, status_code = self.make_request("GET", f"/inventory/{product_id}")
                if success and "product_id" in response:
                    self.log_test(
                        f"Get Inventory Item - {product['name']}", 
                        True, 
                        f"Retrieved inventory for {product['name']}",
                        {"product_id": product_id, "quantity": response.get("quantity"), "status_code": status_code}
                    )
                else:
                    self.log_test(
                        f"Get Inventory Item - {product['name']}", 
                        False, 
                        f"Failed to retrieve inventory for {product['name']}",
                        {"response": response, "status_code": status_code}
                    )
                
                # Test UPDATE inventory with different stock levels
                stock_levels = [50, 5, 0]  # in_stock, low_stock, out_of_stock
                update_data = {
                    "quantity": stock_levels[i],
                    "min_threshold": 10,
                    "max_capacity": 100
                }
                
                success, response, status_code = self.make_request("PUT", f"/inventory/{product_id}", update_data)
                if success and "status" in response:
                    expected_status = ["in_stock", "low_stock", "out_of_stock"][i]
                    actual_status = response.get("status")
                    status_correct = actual_status == expected_status
                    
                    self.log_test(
                        f"Update Inventory - {product['name']}", 
                        status_correct, 
                        f"Updated inventory: quantity={response.get('quantity')}, status={actual_status}",
                        {
                            "product_id": product_id, 
                            "expected_status": expected_status,
                            "actual_status": actual_status,
                            "status_code": status_code
                        }
                    )
                else:
                    self.log_test(
                        f"Update Inventory - {product['name']}", 
                        False, 
                        f"Failed to update inventory for {product['name']}",
                        {"response": response, "status_code": status_code}
                    )
        
        # Test low stock alerts
        success, response, status_code = self.make_request("GET", "/inventory/alerts/low-stock")
        if success and isinstance(response, list):
            self.log_test(
                "Get Low Stock Alerts", 
                True, 
                f"Retrieved {len(response)} low stock alerts",
                {"alert_count": len(response), "alerts": response, "status_code": status_code}
            )
        else:
            self.log_test(
                "Get Low Stock Alerts", 
                False, 
                "Failed to retrieve low stock alerts",
                {"response": response, "status_code": status_code}
            )
    
    def test_employee_management(self):
        """Test Employee Management"""
        print("\n🧪 Testing Employee Management...")
        
        # Test data for employees
        test_employees = [
            {
                "name": "Sarah Johnson",
                "role": "manager",
                "email": "sarah.johnson@marqedonuts.com",
                "phone": "(555) 123-4567",
                "hourly_wage": 22.50
            },
            {
                "name": "Mike Rodriguez",
                "role": "baker",
                "email": "mike.rodriguez@marqedonuts.com",
                "phone": "(555) 234-5678",
                "hourly_wage": 18.00
            },
            {
                "name": "Emily Chen",
                "role": "cashier",
                "email": "emily.chen@marqedonuts.com",
                "phone": "(555) 345-6789",
                "hourly_wage": 16.50
            }
        ]
        
        # Test CREATE employees
        for employee_data in test_employees:
            success, response, status_code = self.make_request("POST", "/employees", employee_data)
            if success and "id" in response:
                self.created_employees.append(response)
                self.log_test(
                    f"Create Employee - {employee_data['name']}", 
                    True, 
                    f"Created {employee_data['role']} successfully",
                    {"employee_id": response["id"], "status_code": status_code}
                )
            else:
                self.log_test(
                    f"Create Employee - {employee_data['name']}", 
                    False, 
                    f"Failed to create employee",
                    {"response": response, "status_code": status_code}
                )
        
        # Test GET all employees
        success, response, status_code = self.make_request("GET", "/employees")
        if success and isinstance(response, list):
            self.log_test(
                "Get All Employees", 
                True, 
                f"Retrieved {len(response)} employees",
                {"count": len(response), "status_code": status_code}
            )
        else:
            self.log_test(
                "Get All Employees", 
                False, 
                "Failed to retrieve employees",
                {"response": response, "status_code": status_code}
            )
    
    def test_customer_management(self):
        """Test Customer Management"""
        print("\n🧪 Testing Customer Management...")
        
        # Test data for customers
        test_customers = [
            {
                "name": "John Smith",
                "email": "john.smith@email.com",
                "phone": "(555) 111-2222"
            },
            {
                "name": "Maria Garcia",
                "email": "maria.garcia@email.com",
                "phone": "(555) 333-4444"
            },
            {
                "name": "David Wilson",
                "email": "david.wilson@email.com",
                "phone": "(555) 555-6666"
            }
        ]
        
        # Test CREATE customers
        for customer_data in test_customers:
            success, response, status_code = self.make_request("POST", "/customers", customer_data)
            if success and "id" in response:
                self.created_customers.append(response)
                self.log_test(
                    f"Create Customer - {customer_data['name']}", 
                    True, 
                    f"Created customer successfully",
                    {"customer_id": response["id"], "status_code": status_code}
                )
            else:
                self.log_test(
                    f"Create Customer - {customer_data['name']}", 
                    False, 
                    f"Failed to create customer",
                    {"response": response, "status_code": status_code}
                )
        
        # Test GET all customers
        success, response, status_code = self.make_request("GET", "/customers")
        if success and isinstance(response, list):
            self.log_test(
                "Get All Customers", 
                True, 
                f"Retrieved {len(response)} customers",
                {"count": len(response), "status_code": status_code}
            )
        else:
            self.log_test(
                "Get All Customers", 
                False, 
                "Failed to retrieve customers",
                {"response": response, "status_code": status_code}
            )
    
    def test_sales_processing(self):
        """Test Sales Transaction Processing"""
        print("\n🧪 Testing Sales Transaction Processing...")
        
        if not self.created_products or not self.created_customers:
            self.log_test(
                "Sales Processing Setup", 
                False, 
                "Cannot test sales - missing products or customers",
                {"products": len(self.created_products), "customers": len(self.created_customers)}
            )
            return
        
        # Create test sales with realistic orders
        test_sales = [
            {
                "items": [
                    {
                        "product_id": self.created_products[0]["id"],  # Glazed donut
                        "quantity": 6,
                        "price": 1.25
                    },
                    {
                        "product_id": self.created_products[4]["id"],  # Coffee
                        "quantity": 2,
                        "price": 2.50
                    }
                ],
                "total_amount": 12.50,
                "payment_method": "credit_card",
                "customer_name": self.created_customers[0]["name"],
                "order_type": "takeout"
            },
            {
                "items": [
                    {
                        "product_id": self.created_products[1]["id"],  # Breakfast taco
                        "quantity": 2,
                        "price": 3.50
                    },
                    {
                        "product_id": self.created_products[5]["id"],  # Orange juice
                        "quantity": 1,
                        "price": 3.25
                    }
                ],
                "total_amount": 10.25,
                "payment_method": "cash",
                "customer_name": self.created_customers[1]["name"],
                "order_type": "dine_in"
            }
        ]
        
        # Test CREATE sales
        created_sales = []
        for i, sale_data in enumerate(test_sales):
            success, response, status_code = self.make_request("POST", "/sales", sale_data)
            if success and "id" in response:
                created_sales.append(response)
                self.log_test(
                    f"Create Sale #{i+1}", 
                    True, 
                    f"Created sale for ${sale_data['total_amount']} successfully",
                    {"sale_id": response["id"], "total": sale_data["total_amount"], "status_code": status_code}
                )
            else:
                self.log_test(
                    f"Create Sale #{i+1}", 
                    False, 
                    f"Failed to create sale",
                    {"response": response, "status_code": status_code}
                )
        
        # Test GET all sales
        success, response, status_code = self.make_request("GET", "/sales")
        if success and isinstance(response, list):
            self.log_test(
                "Get All Sales", 
                True, 
                f"Retrieved {len(response)} sales records",
                {"count": len(response), "status_code": status_code}
            )
        else:
            self.log_test(
                "Get All Sales", 
                False, 
                "Failed to retrieve sales",
                {"response": response, "status_code": status_code}
            )
        
        # Verify inventory was updated after sales
        if self.created_products:
            product_id = self.created_products[0]["id"]  # Check glazed donut inventory
            success, response, status_code = self.make_request("GET", f"/inventory/{product_id}")
            if success and "quantity" in response:
                # Should be reduced from 50 to 44 (6 sold)
                expected_quantity = 44
                actual_quantity = response.get("quantity")
                inventory_updated = actual_quantity == expected_quantity
                
                self.log_test(
                    "Inventory Update After Sale", 
                    inventory_updated, 
                    f"Inventory updated correctly: {actual_quantity} remaining",
                    {
                        "product_id": product_id,
                        "expected_quantity": expected_quantity,
                        "actual_quantity": actual_quantity,
                        "status_code": status_code
                    }
                )
            else:
                self.log_test(
                    "Inventory Update After Sale", 
                    False, 
                    "Failed to verify inventory update",
                    {"response": response, "status_code": status_code}
                )
    
    def test_dashboard_analytics(self):
        """Test Dashboard Analytics API Endpoints"""
        print("\n🧪 Testing Dashboard Analytics...")
        
        # Test dashboard overview
        success, response, status_code = self.make_request("GET", "/dashboard/overview")
        if success and isinstance(response, dict):
            required_fields = ["today_revenue", "today_orders", "low_stock_alerts", "total_products", "total_customers", "active_employees"]
            has_all_fields = all(field in response for field in required_fields)
            
            self.log_test(
                "Dashboard Overview", 
                has_all_fields, 
                f"Dashboard overview retrieved with all required fields",
                {
                    "fields_present": list(response.keys()),
                    "today_revenue": response.get("today_revenue"),
                    "today_orders": response.get("today_orders"),
                    "status_code": status_code
                }
            )
        else:
            self.log_test(
                "Dashboard Overview", 
                False, 
                "Failed to retrieve dashboard overview",
                {"response": response, "status_code": status_code}
            )
        
        # Test daily analytics
        success, response, status_code = self.make_request("GET", "/sales/analytics/daily")
        if success and isinstance(response, dict):
            required_fields = ["date", "total_revenue", "total_orders", "average_order_value", "popular_items"]
            has_all_fields = all(field in response for field in required_fields)
            
            self.log_test(
                "Daily Analytics", 
                has_all_fields, 
                f"Daily analytics retrieved successfully",
                {
                    "total_revenue": response.get("total_revenue"),
                    "total_orders": response.get("total_orders"),
                    "popular_items_count": len(response.get("popular_items", [])),
                    "status_code": status_code
                }
            )
        else:
            self.log_test(
                "Daily Analytics", 
                False, 
                "Failed to retrieve daily analytics",
                {"response": response, "status_code": status_code}
            )
        
        # Test category analytics
        success, response, status_code = self.make_request("GET", "/sales/analytics/category")
        if success and isinstance(response, dict):
            self.log_test(
                "Category Analytics", 
                True, 
                f"Category analytics retrieved for {len(response)} categories",
                {
                    "categories": list(response.keys()),
                    "category_data": response,
                    "status_code": status_code
                }
            )
        else:
            self.log_test(
                "Category Analytics", 
                False, 
                "Failed to retrieve category analytics",
                {"response": response, "status_code": status_code}
            )
    
    def test_product_deletion(self):
        """Test Product Deletion (cleanup)"""
        print("\n🧪 Testing Product Deletion...")
        
        # Delete one test product to verify deletion works
        if self.created_products:
            product_to_delete = self.created_products[-1]  # Delete last product
            product_id = product_to_delete["id"]
            
            success, response, status_code = self.make_request("DELETE", f"/products/{product_id}")
            if success and "message" in response:
                self.log_test(
                    f"Delete Product - {product_to_delete['name']}", 
                    True, 
                    f"Product deleted successfully",
                    {"product_id": product_id, "message": response.get("message"), "status_code": status_code}
                )
                
                # Verify product is actually deleted
                success, response, status_code = self.make_request("GET", f"/products/{product_id}")
                deletion_verified = not success and status_code == 404
                
                self.log_test(
                    "Verify Product Deletion", 
                    deletion_verified, 
                    "Product deletion verified" if deletion_verified else "Product still exists after deletion",
                    {"product_id": product_id, "status_code": status_code}
                )
            else:
                self.log_test(
                    f"Delete Product - {product_to_delete['name']}", 
                    False, 
                    f"Failed to delete product",
                    {"response": response, "status_code": status_code}
                )
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Comprehensive Backend Testing for Marq' E Donuts Management System")
        print(f"🌐 Testing API at: {self.base_url}")
        print("=" * 80)
        
        start_time = time.time()
        
        # Run all test suites
        self.test_product_crud_operations()
        self.test_inventory_management()
        self.test_employee_management()
        self.test_customer_management()
        self.test_sales_processing()
        self.test_dashboard_analytics()
        self.test_product_deletion()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Generate summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['message']}")
        
        print("\n" + "=" * 80)
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "duration": duration,
            "detailed_results": self.test_results
        }

if __name__ == "__main__":
    tester = DonutShopTester()
    results = tester.run_all_tests()
    
    # Save detailed results to file
    with open("/app/backend_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: /app/backend_test_results.json")