import React, { useState, useEffect } from 'react';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const App = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [dashboardData, setDashboardData] = useState({});
  const [products, setProducts] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [sales, setSales] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [alerts, setAlerts] = useState([]);

  // API calls
  const fetchDashboardData = async () => {
    try {
      const response = await fetch(`${API}/dashboard/overview`);
      const data = await response.json();
      setDashboardData(data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
  };

  const fetchProducts = async () => {
    try {
      const response = await fetch(`${API}/products`);
      const data = await response.json();
      setProducts(data);
    } catch (error) {
      console.error('Error fetching products:', error);
    }
  };

  const fetchInventory = async () => {
    try {
      const response = await fetch(`${API}/inventory`);
      const data = await response.json();
      setInventory(data);
      
      // Fetch alerts
      const alertsResponse = await fetch(`${API}/inventory/alerts/low-stock`);
      const alertsData = await alertsResponse.json();
      setAlerts(alertsData);
    } catch (error) {
      console.error('Error fetching inventory:', error);
    }
  };

  const fetchSales = async () => {
    try {
      const response = await fetch(`${API}/sales?limit=50`);
      const data = await response.json();
      setSales(data);
    } catch (error) {
      console.error('Error fetching sales:', error);
    }
  };

  const fetchEmployees = async () => {
    try {
      const response = await fetch(`${API}/employees`);
      const data = await response.json();
      setEmployees(data);
    } catch (error) {
      console.error('Error fetching employees:', error);
    }
  };

  const fetchCustomers = async () => {
    try {
      const response = await fetch(`${API}/customers`);
      const data = await response.json();
      setCustomers(data);
    } catch (error) {
      console.error('Error fetching customers:', error);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    fetchProducts();
    fetchInventory();
    fetchSales();
    fetchEmployees();
    fetchCustomers();
  }, []);

  // Component for Dashboard
  const Dashboard = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Marq' E Donuts Dashboard</h1>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
          <span className="text-sm text-gray-600">Live Data</span>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 p-6 rounded-xl text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100">Today's Revenue</p>
              <p className="text-2xl font-bold">${dashboardData.today_revenue?.toFixed(2) || '0.00'}</p>
            </div>
            <div className="text-3xl">💰</div>
          </div>
        </div>

        <div className="bg-gradient-to-r from-green-500 to-green-600 p-6 rounded-xl text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100">Today's Orders</p>
              <p className="text-2xl font-bold">{dashboardData.today_orders || 0}</p>
            </div>
            <div className="text-3xl">📋</div>
          </div>
        </div>

        <div className="bg-gradient-to-r from-yellow-500 to-yellow-600 p-6 rounded-xl text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-yellow-100">Low Stock Alerts</p>
              <p className="text-2xl font-bold">{dashboardData.low_stock_alerts || 0}</p>
            </div>
            <div className="text-3xl">⚠️</div>
          </div>
        </div>

        <div className="bg-gradient-to-r from-purple-500 to-purple-600 p-6 rounded-xl text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100">Total Products</p>
              <p className="text-2xl font-bold">{dashboardData.total_products || 0}</p>
            </div>
            <div className="text-3xl">🍩</div>
          </div>
        </div>
      </div>

      {/* Alerts Section */}
      {alerts.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center mb-2">
            <span className="text-red-600 text-lg font-medium">🚨 Stock Alerts</span>
          </div>
          <div className="space-y-2">
            {alerts.map((alert, index) => (
              <div key={index} className="flex justify-between items-center text-sm">
                <span className="text-red-700 font-medium">{alert.product_name}</span>
                <span className="text-red-600">{alert.current_quantity} left (min: {alert.min_threshold})</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Sales */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Recent Sales</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Customer</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Items</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Payment</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {sales.slice(0, 5).map((sale, index) => (
                <tr key={index}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(sale.timestamp).toLocaleTimeString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {sale.customer_name || 'Walk-in'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {sale.items.length} items
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    ${sale.total_amount.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {sale.payment_method}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  // Component for Products Management
  const ProductsManager = () => {
    const [selectedCategory, setSelectedCategory] = useState('all');
    const [showAddProduct, setShowAddProduct] = useState(false);
    const [newProduct, setNewProduct] = useState({
      name: '',
      category: 'donuts',
      price: '',
      cost: '',
      description: '',
      ingredients: [],
      prep_time: ''
    });

    const filteredProducts = selectedCategory === 'all' 
      ? products 
      : products.filter(p => p.category === selectedCategory);

    const categories = [
      { value: 'all', label: 'All Categories', icon: '📋' },
      { value: 'donuts', label: 'Donuts', icon: '🍩' },
      { value: 'tacos', label: 'Tacos', icon: '🌮' },
      { value: 'kolaches', label: 'Kolaches', icon: '🥟' },
      { value: 'croissants', label: 'Croissants', icon: '🥐' },
      { value: 'coffee', label: 'Coffee', icon: '☕' },
      { value: 'beverages', label: 'Beverages', icon: '🥤' }
    ];

    const handleAddProduct = async (e) => {
      e.preventDefault();
      try {
        const response = await fetch(`${API}/products`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            ...newProduct,
            price: parseFloat(newProduct.price),
            cost: parseFloat(newProduct.cost),
            prep_time: parseInt(newProduct.prep_time) || 0,
            ingredients: newProduct.ingredients.filter(i => i.trim())
          })
        });
        
        if (response.ok) {
          fetchProducts();
          setShowAddProduct(false);
          setNewProduct({
            name: '',
            category: 'donuts',
            price: '',
            cost: '',
            description: '',
            ingredients: [],
            prep_time: ''
          });
        }
      } catch (error) {
        console.error('Error adding product:', error);
      }
    };

    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Products Manager</h1>
          <button
            onClick={() => setShowAddProduct(!showAddProduct)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            {showAddProduct ? 'Cancel' : 'Add Product'}
          </button>
        </div>

        {/* Category Filter */}
        <div className="flex flex-wrap gap-2">
          {categories.map(cat => (
            <button
              key={cat.value}
              onClick={() => setSelectedCategory(cat.value)}
              className={`px-4 py-2 rounded-lg transition-colors ${
                selectedCategory === cat.value
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {cat.icon} {cat.label}
            </button>
          ))}
        </div>

        {/* Add Product Form */}
        {showAddProduct && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Add New Product</h2>
            <form onSubmit={handleAddProduct} className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input
                  type="text"
                  value={newProduct.name}
                  onChange={(e) => setNewProduct({...newProduct, name: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                <select
                  value={newProduct.category}
                  onChange={(e) => setNewProduct({...newProduct, category: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                >
                  {categories.slice(1).map(cat => (
                    <option key={cat.value} value={cat.value}>{cat.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Price ($)</label>
                <input
                  type="number"
                  step="0.01"
                  value={newProduct.price}
                  onChange={(e) => setNewProduct({...newProduct, price: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Cost ($)</label>
                <input
                  type="number"
                  step="0.01"
                  value={newProduct.cost}
                  onChange={(e) => setNewProduct({...newProduct, cost: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  required
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={newProduct.description}
                  onChange={(e) => setNewProduct({...newProduct, description: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  rows="3"
                />
              </div>

              <div className="md:col-span-2">
                <button
                  type="submit"
                  className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors"
                >
                  Add Product
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Products Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProducts.map(product => (
            <div key={product.id} className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-semibold">{product.name}</h3>
                <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                  {product.category}
                </span>
              </div>
              
              <p className="text-gray-600 text-sm mb-3">{product.description}</p>
              
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Price:</span>
                  <span className="font-medium">${product.price.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Cost:</span>
                  <span className="font-medium">${product.cost.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Profit:</span>
                  <span className="font-medium text-green-600">
                    ${(product.price - product.cost).toFixed(2)}
                  </span>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t">
                <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs ${
                  product.is_available
                    ? 'bg-green-100 text-green-800'
                    : 'bg-red-100 text-red-800'
                }`}>
                  {product.is_available ? '✅ Available' : '❌ Unavailable'}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  // Component for Inventory Management
  const InventoryManager = () => {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-900">Inventory Management</h1>

        {/* Stock Status Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
              <span className="font-medium text-green-800">In Stock</span>
            </div>
            <p className="text-2xl font-bold text-green-900 mt-2">
              {inventory.filter(item => item.status === 'in_stock').length}
            </p>
          </div>

          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-yellow-500 rounded-full mr-2"></div>
              <span className="font-medium text-yellow-800">Low Stock</span>
            </div>
            <p className="text-2xl font-bold text-yellow-900 mt-2">
              {inventory.filter(item => item.status === 'low_stock').length}
            </p>
          </div>

          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
              <span className="font-medium text-red-800">Out of Stock</span>
            </div>
            <p className="text-2xl font-bold text-red-900 mt-2">
              {inventory.filter(item => item.status === 'out_of_stock').length}
            </p>
          </div>
        </div>

        {/* Inventory Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Product</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Current Stock</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Min Threshold</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Restocked</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {inventory.map((item, index) => {
                  const product = products.find(p => p.id === item.product_id);
                  return (
                    <tr key={index}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {product?.name || 'Unknown Product'}
                        </div>
                        <div className="text-sm text-gray-500">
                          {product?.category}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {item.quantity}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {item.min_threshold}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          item.status === 'in_stock'
                            ? 'bg-green-100 text-green-800'
                            : item.status === 'low_stock'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {item.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {new Date(item.last_restocked).toLocaleDateString()}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  };

  // Navigation component
  const Navigation = () => {
    const tabs = [
      { id: 'dashboard', name: 'Dashboard', icon: '📊' },
      { id: 'products', name: 'Products', icon: '🍩' },
      { id: 'inventory', name: 'Inventory', icon: '📦' },
      { id: 'sales', name: 'Sales', icon: '💰' },
      { id: 'employees', name: 'Employees', icon: '👥' },
      { id: 'customers', name: 'Customers', icon: '👤' }
    ];

    return (
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex space-x-8">
                <div className="flex items-center">
                  <h1 className="text-xl font-bold text-gray-900">Marq' E Donuts</h1>
                </div>
                {tabs.map(tab => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                      activeTab === tab.id
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <span className="mr-2">{tab.icon}</span>
                    {tab.name}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </nav>
    );
  };

  // Main render function
  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'products':
        return <ProductsManager />;
      case 'inventory':
        return <InventoryManager />;
      case 'sales':
        return <div className="p-6"><h1 className="text-3xl font-bold">Sales Analytics</h1><p>Coming soon...</p></div>;
      case 'employees':
        return <div className="p-6"><h1 className="text-3xl font-bold">Employee Management</h1><p>Coming soon...</p></div>;
      case 'customers':
        return <div className="p-6"><h1 className="text-3xl font-bold">Customer Management</h1><p>Coming soon...</p></div>;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {renderContent()}
      </main>
    </div>
  );
};

export default App;