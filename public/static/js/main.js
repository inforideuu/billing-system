// Sidebar Toggle Logic
document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const openBtn = document.getElementById('openSidebar');
    const closeBtn = document.getElementById('closeSidebar');

    if (openBtn && sidebar) {
        openBtn.addEventListener('click', () => {
            sidebar.classList.remove('-translate-x-full');
        });
    }

    if (closeBtn && sidebar) {
        closeBtn.addEventListener('click', () => {
            sidebar.classList.add('-translate-x-full');
        });
    }
});

// Notification Bell Click Handler
const notificationBell = document.getElementById('notificationBell');
if (notificationBell) {
    notificationBell.addEventListener('click', () => {
        console.log('Notification bell clicked');
        const badge = notificationBell.querySelector('span');
        const count = badge ? badge.textContent.trim() : '0';
        const plural = count === '1' ? '' : 's';
        showToast(`You have ${count} new notification${plural}`, 'info');
    });
}

// Toast Notification System
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    const bgColor = type === 'success' ? 'bg-green-500' : (type === 'error' ? 'bg-red-500' : 'bg-blue-500');
    const icon = type === 'success' ? 'fa-check-circle' : (type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle');

    toast.className = `toast glass-panel ${bgColor} text-white px-4 py-3 rounded-lg shadow-lg flex items-center min-w-[250px]`;
    toast.innerHTML = `
        <i class="fas ${icon} mr-3 text-xl"></i>
        <span class="font-medium">${message}</span>
    `;

    container.appendChild(toast);

    // Animate in
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);

    // Remove after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 300); // Wait for transition
    }, 3000);
}

// Multi-language Dictionary (English / Tamil)
// Sorted by length descending automatically inside translateDOM
const translations = {
    'EN': {
        // Base / Sidebar / Navbar
        'Zenelait Infotech Billing System': 'Zenelait Infotech Billing System',
        'Zenelait Infotech': 'Zenelait Infotech',
        'Overview': 'Overview',
        'Console': 'Console',
        'Dashboard': 'Dashboard',
        'Billing (POS)': 'Billing (POS)',
        'Catalog': 'Catalog',
        'Offers': 'Offers',
        'Customers': 'Customers',
        'Staff': 'Staff',
        'Ledger': 'Ledger',
        'Analytics': 'Analytics',
        'P&L / Tax': 'P&L / Tax',
        'EN': 'EN',
        'Logout': 'Logout',
        'Good day,': 'Good day,',
        'Admin User': 'Admin User',
        'Staff Management': 'Staff Management',
        'New Staff Onboarding': 'New Staff Onboarding',
        'Super Admin Command Center': 'Super Admin Command Center',
        'Products & Services': 'Products & Services',
        'Tax & Profit Reporter': 'Tax & Profit Reporter',
        'Periodical Analytics': 'Periodical Analytics',
        'Purchase & Sales Tracking': 'Purchase & Sales Tracking',
        'Point of Sale (POS)': 'Point of Sale (POS)',
        'Tax Invoice': 'Tax Invoice',
        'Festival Offer Management': 'Festival Offer Management',
        'Customer Management': 'Customer Management',

        // Login Page
        'Return Home': 'Return Home',
        'Unlock Secure ': 'Unlock Secure ',
        'Console Access.': 'Console Access.',
        'Unlock Secure Console Access.': 'Unlock Secure Console Access.',
        'Seamlessly manage point-of-sale invoicing, complete statutory ledger audit files, and monitor multi-agent performance metrics.': 'Seamlessly manage point-of-sale invoicing, complete statutory ledger audit files, and monitor multi-agent performance metrics.',
        'Operator Sign-In': 'Operator Sign-In',
        'Console Authentication Core v3.0': 'Console Authentication Core v3.0',
        'Access Identity': 'Access Identity',
        'Operator Username': 'Operator Username',
        'Security Key': 'Security Key',
        'Reset Path': 'Reset Path',
        'SSL Encrypted Client-Session Node': 'SSL Encrypted Client-Session Node',
        'Initialize Connection': 'Initialize Connection',

        // POS
        'Search catalog by name...': 'Search catalog by name...',
        'Scan/Type Barcode/SKU...': 'Scan/Type Barcode/SKU...',
        'Open Camera Scan': 'Open Camera Scan',
        'Scan Product Barcode / QR': 'Scan Product Barcode / QR',
        'Add to Cart': 'Add to Cart',
        'Cart is empty': 'Cart is empty',
        'Current Invoice': 'Current Invoice',
        'Clear': 'Clear',
        'Customer Name': 'Customer Name',
        'Phone Number': 'Phone Number',
        'Email': 'Email',
        'GSTIN (B2B Only)': 'GSTIN (B2B Only)',
        'Subtotal:': 'Subtotal:',
        'CGST (Central @ 50%):': 'CGST (Central @ 50%):',
        'SGST (State @ 50%):': 'SGST (State @ 50%):',
        'Total GST Tax:': 'Total GST Tax:',
        'Festival Discount:': 'Festival Discount:',
        'Total Amount:': 'Total Amount:',
        'Send Invoice via WhatsApp': 'Send Invoice via WhatsApp',
        'Cash': 'Cash',
        'UPI/Card': 'UPI/Card',

        // Customer Page & Forms
        'All Customers': 'All Customers',
        'Add Customer': 'Add Customer',
        'Customer Name *': 'Customer Name *',
        'Phone Number': 'Phone Number',
        'GSTIN (Tax ID)': 'GSTIN (Tax ID)',
        'Email Address': 'Email Address',
        'Save Customer': 'Save Customer',
        'Delete Customer': 'Delete Customer',
        'Are you sure you want to delete': 'Are you sure you want to delete',
        'This operation is permanent.': 'This operation is permanent.',
        'Cancel': 'Cancel',
        'Delete': 'Delete',
        'Edit': 'Edit',

        // Inventory / Catalog Page
        'Search items...': 'Search items...',
        'Export': 'Export',
        'Add Item': 'Add Item',
        'Item Type': 'Item Type',
        'Name / Description': 'Name / Description',
        'Price (₹)': 'Price (₹)',
        'HSN/SAC Code': 'HSN/SAC Code',
        'GST Rate (%)': 'GST Rate (%)',
        'Initial Stock': 'Initial Stock',
        'Product Image (Optional)': 'Product Image (Optional)',
        'Save Item': 'Save Item',
        'Edit Product / Service': 'Edit Product / Service',
        'Update Item Details': 'Update Item Details',
        'Delete Confirmation': 'Delete Confirmation',
        'Are you absolutely sure you want to delete': 'Are you absolutely sure you want to delete',
        'This operation cannot be undone.': 'This operation cannot be undone.',
        'Confirm Delete': 'Confirm Delete',
        'Physical Product': 'Physical Product',
        'Service / Labor': 'Service / Labor',
        'Service': 'Service',
        'Product': 'Product',
        'In Stock': 'In Stock',
        'Low Stock': 'Low Stock',
        'Out of Stock': 'Out of Stock',
        'Active': 'Active',
        'Inactive': 'Inactive',
        'Type': 'Type',
        'HSN/SAC': 'HSN/SAC',
        'Price': 'Price',
        'Stock': 'Stock',
        'Status': 'Status',
        'Actions': 'Actions',

        // Dashboard
        'Live System Operational': 'Live System Operational',
        'Here is a quick breakdown of your business performance for': 'Here is a quick breakdown of your business performance for',
        'today': 'today',
        'vs yesterday': 'vs yesterday',
        'Total Sales Today': 'Total Sales Today',
        'Today\'s Revenue': 'Today\'s Revenue',
        'Festival Offer Mode': 'Festival Offer Mode',
        'Enabled': 'Enabled',
        'Disabled': 'Disabled',
        'Active Festival Offers': 'Active Festival Offers',
        'Valid until:': 'Valid until:',
        'No active festival offers found.': 'No active festival offers found.',
        'Create one in the Admin Panel.': 'Create one in the Admin Panel.',
        'Revenue Overview': 'Revenue Overview',

        // Ledger / Reports Page
        'Total Sales Revenue': 'Total Sales Revenue',
        'Income Stream': 'Income Stream',
        'Total Procurement': 'Total Procurement',
        'Capital Outflow': 'Capital Outflow',
        'Operational Balance': 'Operational Balance',
        'Net Margins': 'Net Margins',
        'Sales Ledger': 'Sales Ledger',
        'Purchase Ledger': 'Purchase Ledger',
        'GST Report': 'GST Report',
        'Add Purchase': 'Add Purchase',
        'Export PDF': 'Export PDF',
        'Outbound Customer Invoices': 'Outbound Customer Invoices',
        'Invoice ID': 'Invoice ID',
        'Date': 'Date',
        'Payment Mode': 'Payment Mode',
        'Invoice Total': 'Invoice Total',
        'Inbound Vendor Procurement': 'Inbound Vendor Procurement',
        'Reference': 'Reference',
        'Supplier / Vendor': 'Supplier / Vendor',
        'Bill Reference': 'Bill Reference',
        'Procured Items': 'Procured Items',
        'Total Cost': 'Total Cost',
        'Collections Summary': 'Collections Summary',
        'Total Net Sales (Taxable)': 'Total Net Sales (Taxable)',
        'CGST Collected': 'CGST Collected',
        'SGST Collected': 'SGST Collected',
        'Total Tax Payable': 'Total Tax Payable',
        'Live Tax Slab Breakdown': 'Live Tax Slab Breakdown',
        'Tax Slab Rate': 'Tax Slab Rate',
        'Taxable Net Value': 'Taxable Net Value',
        'Combined Tax': 'Combined Tax',
        'Detailed GSTR-1 Invoice Matrix': 'Detailed GSTR-1 Invoice Matrix',
        'Reference ID': 'Reference ID',
        'Billing Date': 'Billing Date',
        'Purchaser / GSTIN': 'Purchaser / GSTIN',
        'Gross Amount': 'Gross Amount',
        'Add Purchase Invoice': 'Add Purchase Invoice',
        'Record stock procurement and automatically increment inventory counts.': 'Record stock procurement and automatically increment inventory counts.',
        'Supplier Vendor': 'Supplier Vendor',
        'Bill Reference #': 'Bill Reference #',
        'Procurement Mode': 'Procurement Mode',
        'Procured Product': 'Procured Product',
        'Unit Cost (₹)': 'Unit Cost (₹)',
        'Quantity': 'Quantity',
        'Gross Outflow Total': 'Gross Outflow Total',
        'Post Procurement Invoice': 'Post Procurement Invoice',

        // Periodical Analytics Page
        'Monthly Sales': 'Monthly Sales',
        'Quarterly Sales': 'Quarterly Sales',
        'Yearly Sales': 'Yearly Sales',
        'Print PDF Report': 'Print PDF Report',
        'Monthly Revenue Velocity': 'Monthly Revenue Velocity',
        'Period-over-period gross billing performance': 'Period-over-period gross billing performance',
        'Historical Monthly Aggregates': 'Historical Monthly Aggregates',
        'Billing Period': 'Billing Period',
        'Invoice Volumes': 'Invoice Volumes',
        'Average Order Size (AOV)': 'Average Order Size (AOV)',
        'Total Value Collected': 'Total Value Collected',
        'Historical Quarterly Aggregates': 'Historical Quarterly Aggregates',
        'Historical Annual Aggregates': 'Historical Annual Aggregates',
        'Billing Year': 'Billing Year',

        // Tax & Profit Reporter Page
        'Gross Revenue': 'Gross Revenue',
        'Turnover Pool': 'Turnover Pool',
        'Operating Cost': 'Operating Cost',
        'GST Collected': 'GST Collected',
        'Outward Liability': 'Outward Liability',
        'Net Profit Margin': 'Net Profit Margin',
        'Net Retained Margin': 'Net Retained Margin',
        'Revenue vs Operating Cost Velocity': 'Revenue vs Operating Cost Velocity',
        'Historical comparative cashflow trend matrix': 'Historical comparative cashflow trend matrix',
        'Sales': 'Sales',
        'Cost': 'Cost',
        'Comprehensive Periodic Profit & Tax Grid': 'Comprehensive Periodic Profit & Tax Grid',
        'Print': 'Print',
        'Fiscal Month': 'Fiscal Month',
        'Gross Sales (Turnover)': 'Gross Sales (Turnover)',
        'Outward Tax (GST)': 'Outward Tax (GST)',
        'Operating Expenses': 'Operating Expenses',
        'Retained Net Profit': 'Retained Net Profit',
        'Profit Margin %': 'Profit Margin %',

        // Festival Offers Page
        'Global Festival Offer Mode': 'Global Festival Offer Mode',
        'When enabled, active offers will be automatically applied at the POS.': 'When enabled, active offers will be automatically applied at the POS.',
        'MODE ACTIVE': 'MODE ACTIVE',
        'MODE INACTIVE': 'MODE INACTIVE',
        'Available Offers': 'Available Offers',
        'Create New Offer': 'Create New Offer',
        'All Products': 'All Products',
        'Active Now': 'Active Now',
        'Scheduled / Expired': 'Scheduled / Expired',

        // Roles and general descriptions
        'Super Admin': 'Super Admin',
        'Admin': 'Admin',
        'Cashier': 'Cashier',
        'Manager': 'Manager',

        // Months (Full and short)
        'January': 'January', 'February': 'February', 'March': 'March', 'April': 'April',
        'May': 'May', 'June': 'June', 'July': 'July', 'August': 'August',
        'September': 'September', 'October': 'October', 'November': 'November', 'December': 'December',
        'Jan': 'Jan', 'Feb': 'Feb', 'Mar': 'Mar', 'Apr': 'Apr', 'Jun': 'Jun', 'Jul': 'Jul', 'Aug': 'Aug', 'Sep': 'Sep', 'Oct': 'Oct', 'Nov': 'Nov', 'Dec': 'Dec',

        // Insights / Intelligence App Additional Words
        'Settings': 'Settings',
        'Smart Insights & Predictions': 'Smart Insights & Predictions',
        'Shop Operations Intelligence': 'Shop Operations Intelligence',
        'Real-time alerts, sales trajectory trends, inventory velocity, and demand forecasts.': 'Real-time alerts, sales trajectory trends, inventory velocity, and demand forecasts.',
        'Manage Batches': 'Manage Batches',
        'Operations Alert Feed': 'Operations Alert Feed',
        'All operations are running smoothly. No active alerts found!': 'All operations are running smoothly. No active alerts found!',
        'Sales Performance Trajectory': 'Sales Performance Trajectory',
        'Total revenue collected this calendar month.': 'Total revenue collected this calendar month.',
        'Last Month': 'Last Month',
        'Stable': 'Stable',
        'Top Selling Items': 'Top Selling Items',
        'No sales recorded in the last 30 days.': 'No sales recorded in the last 30 days.',
        'Slow-Moving Stock': 'Slow-Moving Stock',
        'No slow-moving products. Inventory moving quickly!': 'No slow-moving products. Inventory moving quickly!',
        'Dead Stock Alerts': 'Dead Stock Alerts',
        'No dead stock recorded. Healthy product cycle.': 'No dead stock recorded. Healthy product cycle.',
        'Demand Forecast & Restocking Guide': 'Demand Forecast & Restocking Guide',
        'Product Name': 'Product Name',
        'Avg Daily Sales': 'Avg Daily Sales',
        'Expected next Week': 'Expected next Week',
        'Expected next Month': 'Expected next Month',
        'Current Stock': 'Current Stock',
        'Suggested Restock': 'Suggested Restock',
        'Demand Tag': 'Demand Tag',
        'No physical products found in the catalog to forecast demand.': 'No physical products found in the catalog to forecast demand.',
        'Actual vs. Forecasted Weekly Demand Trend': 'Actual vs. Forecasted Weekly Demand Trend',
        'Actual Weekly Demand': 'Actual Weekly Demand',
        'Forecasted Weekly Demand': 'Forecasted Weekly Demand',
        'Current Week': 'Current Week',
        'Sufficient': 'Sufficient',
        'High Velocity': 'High Velocity',
        'Normal': 'Normal',
        'Stock depletion alert': 'Stock depletion alert',
        'Low stock warning': 'Low stock warning',
        'Expired inventory': 'Expired inventory',
        'Expiry warning': 'Expiry warning',
        'Sales performance warning': 'Sales performance warning',
        'Smart Insights & Forecasting | Retail Billing': 'Smart Insights & Forecasting | Retail Billing',
        'Weekly Demand Trend': 'Weekly Demand Trend',
        'Weekly Demand': 'Weekly Demand',
        'Sold': 'Sold',
        'Sold (30d)': 'Sold (30d)',
        'Stock:': 'Stock:',
        'Value:': 'Value:',
        'Batch & Expiry Management | Retail Billing': 'Batch & Expiry Management | Retail Billing',
        'Batch & Expiry Tracking': 'Batch & Expiry Tracking',
        'Active Batches': 'Active Batches',
        'Expired Batches': 'Expired Batches',
        'Expiring Soon': 'Expiring Soon',
        'Add New Batch': 'Add New Batch',
        'Search batch number or SKU...': 'Search batch number or SKU...',
        'Pricing and checkout automatically select oldest unexpired batches first.': 'Pricing and checkout automatically select oldest unexpired batches first.',
        'Batch Number': 'Batch Number',
        'Mfg Date': 'Mfg Date',
        'Expiry Date': 'Expiry Date',
        'Sold Out': 'Sold Out',
        'Healthy': 'Healthy',
        'Delete Batch': 'Delete Batch',
        'Are you sure you want to remove batch': 'Are you sure you want to remove batch',
        'This will adjust the product\'s overall stock quantity accordingly.': 'This will adjust the product\'s overall stock quantity accordingly.',
        'Register Inventory Batch': 'Register Inventory Batch',
        'Select Product': 'Select Product',
        '-- Select Product --': '-- Select Product --',
        'Mfg Date (Optional)': 'Mfg Date (Optional)',
        'Initial Batch Stock Quantity': 'Initial Batch Stock Quantity',
        'Save Batch': 'Save Batch',
        'No batches currently loaded. Register a batch during purchase entries or click "Add New Batch".': 'No batches currently loaded. Register a batch during purchase entries or click "Add New Batch".',
        'Intelligence Settings | Retail Billing': 'Intelligence Settings | Retail Billing',
        'Intelligence & Dynamic Pricing Settings': 'Intelligence & Dynamic Pricing Settings',
        'Advanced Control Panel': 'Advanced Control Panel',
        'Enable features, modify alert thresholds, and customize dynamic pricing rules.': 'Enable features, modify alert thresholds, and customize dynamic pricing rules.',
        'Email Alert Digest Now': 'Email Alert Digest Now',
        'Save Configurations': 'Save Configurations',
        'Active Modules': 'Active Modules',
        'Calculates average daily sales velocity, predicts product stock-out dates, and warns about dead stock.': 'Calculates average daily sales velocity, predicts product stock-out dates, and warns about dead stock.',
        'Demand Forecasting': 'Demand Forecasting',
        'Predicts sales for next week and next month using historical sales data and weighted trends, then suggests restocking amounts.': 'Predicts sales for next week and next month using historical sales data and weighted trends, then suggests restocking amounts.',
        'Dynamic Pricing System': 'Dynamic Pricing System',
        'Automatically adjusts prices in the POS catalog based on low stock quantities, high sales demand levels, and near-expiry clearance rules.': 'Automatically adjusts prices in the POS catalog based on low stock quantities, high sales demand levels, and near-expiry clearance rules.',
        'Operation Thresholds': 'Operation Thresholds',
        'Alerts dashboard and triggers low stock price markup when stock drops below this value.': 'Alerts dashboard and triggers low stock price markup when stock drops below this value.',
        'Expiry Alert Threshold (Days)': 'Expiry Alert Threshold (Days)',
        'Generates warning alerts and applies clearance discount rules when a batch is within this expiry window.': 'Generates warning alerts and applies clearance discount rules when a batch is within this expiry window.',
        'Dynamic Pricing Rules (%)': 'Dynamic Pricing Rules (%)',
        'Increases pricing by this percentage when product stock is below your low stock threshold.': 'Increases pricing by this percentage when product stock is below your low stock threshold.',
        'Increases base price when average sales exceed 1.5 units per day over the last 7 days.': 'Increases base price when average sales exceed 1.5 units per day over the last 7 days.',
        'Deducts this percentage from standard pricing when the active stock batch is expiring soon.': 'Deducts this percentage from standard pricing when the active stock batch is expiring soon.',
        'Admin (Shop Owner)': 'Admin (Shop Owner)',
        'SHOP OWNER': 'SHOP OWNER',
        'Insights': 'Insights',
        'Batches': 'Batches',
        'units': 'units',
        'Units': 'Units'
    },
    'TA': {
        // Base / Sidebar / Navbar
        'Zenelait Infotech Billing System': 'ஜெனிலைட் இன்ஃபோடெக் பில்லிங் முறைமை',
        'Zenelait Infotech': 'ஜெனிலைட் இன்ஃபோடெக்',
        'Overview': 'மேலோட்டம்',
        'Console': 'கண்ட்ரோல் பேனல்',
        'Dashboard': 'முகப்பு பலகை',
        'Billing (POS)': 'பில்லிங் (POS)',
        'Catalog': 'இருப்புப் பட்டியல்',
        'Offers': 'சலுகைகள்',
        'Customers': 'வாடிக்கையாளர்கள்',
        'Staff': 'பணியாளர்கள்',
        'Ledger': 'கணக்குப்பேடு',
        'Analytics': 'பகுப்பாய்வு',
        'P&L / Tax': 'இலாப நட்ட / வரி',
        'EN': 'TA',
        'Logout': 'வெளியேறு',
        'Good day,': 'இனிய நாள்,',
        'Admin User': 'நிர்வாக பயனர்',
        'Staff Management': 'பணியாளர் மேலாண்மை',
        'New Staff Onboarding': 'புதிய பணியாளர் சேர்க்கை',
        'Super Admin Command Center': 'தலைமை நிர்வாக கட்டளை மையம்',
        'Products & Services': 'தயாரிப்புகள் மற்றும் சேவைகள்',
        'Tax & Profit Reporter': 'வரி மற்றும் லாப அறிக்கை',
        'Periodical Analytics': 'காலமுறை பகுப்பாய்வு',
        'Purchase & Sales Tracking': 'கொள்முதல் மற்றும் விற்பனை கண்காணிப்பு',
        'Point of Sale (POS)': 'விற்பனை புள்ளி (POS)',
        'Tax Invoice': 'வரி விலைப்பட்டியல்',
        'Festival Offer Management': 'திருவிழா சலுகை மேலாண்மை',
        'Customer Management': 'வாடிக்கையாளர் மேலாண்மை',

        // Login Page
        'Return Home': 'முகப்புக்குத் திரும்பு',
        'Unlock Secure ': 'பாதுகாப்பான ',
        'Console Access.': 'கன்சோல் அணுகல்.',
        'Unlock Secure Console Access.': 'பாதுகாப்பான கன்சோல் அணுகலைத் திறக்கவும்.',
        'Seamlessly manage point-of-sale invoicing, complete statutory ledger audit files, and monitor multi-agent performance metrics.': 'பாயிண்ட்-ஆஃப்-சேல் இன்வாய்சிங், சட்டப்பூர்வ கணக்குத் தணிக்கை கோப்புகள் மற்றும் பல முகவர் செயல்திறன் அளவீடுகளை தடையின்றி நிர்வகிக்கவும்.',
        'Operator Sign-In': 'ஆபரேட்டர் உள்நுறைவு',
        'Console Authentication Core v3.0': 'கன்சோல் அங்கீகார கோர் v3.0',
        'Access Identity': 'அணுகல் அடையாளம்',
        'Operator Username': 'ஆபரேட்டர் பயனர் பெயர்',
        'Security Key': 'பாதுகாப்பு சாவி',
        'Reset Path': 'மீட்டமைத்தல் பாதை',
        'SSL Encrypted Client-Session Node': 'SSL குறியாக்கப்பட்ட கிளையன்ட்-அமர்வு முனை',
        'Initialize Connection': 'இணைப்பைத் தொடங்கு',

        // POS
        'Search catalog by name...': 'பெயர் மூலம் இருப்புப் பட்டியலைத் தேடு...',
        'Scan/Type Barcode/SKU...': 'பார்கோடு அல்லது SKU-ஐ ஸ்கேன் செய்யவும்/உள்ளிடவும்...',
        'Open Camera Scan': 'கேமரா ஸ்கேனைத் திற',
        'Scan Product Barcode / QR': 'பொருள் பார்கோடு / QR-ஐ ஸ்கேன் செய்யவும்',
        'Add to Cart': 'கூடையில் சேர்',
        'Cart is empty': 'கூடை காலியாக உள்ளது',
        'Current Invoice': 'தற்போதைய விலைப்பட்டியல்',
        'Clear': 'நீக்கு',
        'Customer Name': 'வாடிக்கையாளர் பெயர்',
        'Phone Number': 'தொலைபேசி எண்',
        'Email': 'மின்னஞ்சல்',
        'GSTIN (B2B Only)': 'GSTIN எண் (B2B மட்டும்)',
        'Subtotal:': 'துணைத்தொகை:',
        'CGST (Central @ 50%):': 'CGST (மத்திய @ 50%):',
        'SGST (State @ 50%):': 'SGST (மாநில @ 50%):',
        'Total GST Tax:': 'மொத்த GST வரி:',
        'Festival Discount:': 'திருவிழா தள்ளுபடி:',
        'Total Amount:': 'மொத்த தொகை:',
        'Send Invoice via WhatsApp': 'WhatsApp மூலம் விலைப்பட்டியலை அனுப்புக',
        'Cash': 'ரொக்கம்',
        'UPI/Card': 'UPI / அட்டை',

        // Customer Page & Forms
        'All Customers': 'அனைத்து வாடிக்கையாளர்கள்',
        'Add Customer': 'வாடிக்கையாளரைச் சேர்',
        'Customer Name *': 'வாடிக்கையாளர் பெயர் *',
        'Phone Number': 'தொலைபேசி எண்',
        'GSTIN (Tax ID)': 'GSTIN (வரி ஐடி)',
        'Email Address': 'மின்னஞ்சல் முகவரி',
        'Save Customer': 'வாடிக்கையாளரைச் சேமி',
        'Delete Customer': 'வாடிக்கையாளரை நீக்கு',
        'Are you sure you want to delete': 'நீங்கள் நிச்சயமாக நீக்க விரும்புகிறீர்களா',
        'This operation is permanent.': 'இந்த நடவடிக்கை நிரந்தரமானது.',
        'Cancel': 'ரத்துசெய்',
        'Delete': 'நீக்கு',
        'Edit': 'திருத்து',

        // Inventory / Catalog Page
        'Search items...': 'பொருட்களைத் தேடு...',
        'Export': 'ஏற்றுமதி',
        'Add Item': 'பொருளைச் சேர்',
        'Item Type': 'பொருளின் வகை',
        'Name / Description': 'பெயர் / விளக்கம்',
        'Price (₹)': 'விலை (₹)',
        'HSN/SAC Code': 'HSN/SAC குறியீடு',
        'GST Rate (%)': 'GST வரி விகிதம் (%)',
        'Initial Stock': 'ஆரம்ப இருப்பு',
        'Product Image (Optional)': 'தயாரிப்பு படம் (விருப்பத்தேர்வு)',
        'Save Item': 'பொருளைச் சேமி',
        'Edit Product / Service': 'தயாரிப்பு / சேவையைத் திருத்து',
        'Update Item Details': 'பொருள் விவரங்களைப் புதுப்பி',
        'Delete Confirmation': 'நீக்குதல் உறுதிப்படுத்தல்',
        'Are you absolutely sure you want to delete': 'நீங்கள் நிச்சயமாக நீக்க விரும்புகிறீர்களா',
        'This operation cannot be undone.': 'இந்தச் செயல்பாட்டை மாற்ற முடியாது.',
        'Confirm Delete': 'நீக்குதலை உறுதிப்படுத்து',
        'Physical Product': 'உடல் தயாரிப்பு',
        'Service / Labor': 'சேவை / உழைப்பு',
        'Service': 'சேவை',
        'Product': 'தயாரிப்பு',
        'In Stock': 'இருப்பில் உள்ளது',
        'Low Stock': 'குறைந்த இருப்பு',
        'Out of Stock': 'இருப்பில்லை',
        'Active': 'செயலில் உள்ளது',
        'Inactive': 'செயலிழந்தது',
        'Type': 'வகை',
        'HSN/SAC': 'HSN/SAC',
        'Price': 'விலை',
        'Stock': 'இருப்பு',
        'Status': 'நிலை',
        'Actions': 'செயல்கள்',

        // Dashboard
        'Live System Operational': 'நேரடி கணினி செயல்பாட்டில் உள்ளது',
        'Here is a quick breakdown of your business performance for': 'இன்றைய உங்கள் வணிகச் செயல்பாட்டின் விரைவான விவரம் இதோ:',
        'today': 'இன்று',
        'vs yesterday': 'நேற்றைய ஒப்பிடுகையில்',
        'Total Sales Today': 'இன்றைய மொத்த விற்பனை',
        'Today\'s Revenue': 'இன்றைய வருவாய்',
        'Festival Offer Mode': 'திருவிழா சலுகை முறைமை',
        'Enabled': 'செயல்படுத்தப்பட்டது',
        'Disabled': 'செயலிழக்கச் செய்யப்பட்டது',
        'Active Festival Offers': 'செயலில் உள்ள திருவிழா சலுகைகள்',
        'Valid until:': 'வரை செல்லுபடியாகும்:',
        'No active festival offers found.': 'செயலில் உள்ள திருவிழா சலுகைகள் எதுவும் இல்லை.',
        'Create one in the Admin Panel.': 'நிர்வாகக் குழுவில் ஒன்றை உருவாக்கவும்.',
        'Revenue Overview': 'வருவாய் மேலோட்டம்',

        // Ledger / Reports Page
        'Total Sales Revenue': 'மொத்த விற்பனை வருவாய்',
        'Income Stream': 'வருவாய் ஓட்டம்',
        'Total Procurement': 'மொத்த கொள்முதல்',
        'Capital Outflow': 'மூலதன வெளியீடு',
        'Operational Balance': 'செயல்பாட்டு இருப்பு',
        'Net Margins': 'நிகர லாபம்',
        'Sales Ledger': 'விற்பனை பதிவேடு',
        'Purchase Ledger': 'கொள்முதல் பதிவேடு',
        'GST Report': 'GST அறிக்கை',
        'Add Purchase': 'கொள்முதலைச் சேர்',
        'Export PDF': 'PDF ஏற்றுமதி',
        'Outbound Customer Invoices': 'வெளிச்செல்லும் வாடிக்கையாளர் விலைப்பட்டியல்கள்',
        'Invoice ID': 'விலைப்பட்டியல் எண்',
        'Date': 'தேதி',
        'Payment Mode': 'பணம் செலுத்தும் முறை',
        'Invoice Total': 'விலைப்பட்டியல் மொத்தம்',
        'Inbound Vendor Procurement': 'உள்வரும் விற்பனையாளர் கொள்முதல்',
        'Reference': 'குறிப்பு எண்',
        'Supplier / Vendor': 'வழங்குநர் / விற்பனையாளர்',
        'Bill Reference': 'பில் குறிப்பு',
        'Procured Items': 'கொள்முதல் செய்யப்பட்ட பொருட்கள்',
        'Total Cost': 'மொத்த செலவு',
        'Collections Summary': 'வசூல் சுருக்கம்',
        'Total Net Sales (Taxable)': 'மொத்த நிகர விற்பனை (வரிக்குரியது)',
        'CGST Collected': 'CGST வசூலிக்கப்பட்டது',
        'SGST Collected': 'SGST வசூலிக்கப்பட்டது',
        'Total Tax Payable': 'மொத்த செலுத்த வேண்டிய வரி',
        'Live Tax Slab Breakdown': 'நேரடி வரி அடுக்கு விவரம்',
        'Tax Slab Rate': 'வரி அடுக்கு விகிதம்',
        'Taxable Net Value': 'வரிக்குரிய நிகர மதிப்பு',
        'Combined Tax': 'ஒருங்கிணைந்த வரி',
        'Detailed GSTR-1 Invoice Matrix': 'விரிவான GSTR-1 விலைப்பட்டியல் மேட்ரிக்ஸ்',
        'Reference ID': 'குறிப்பு ஐடி',
        'Billing Date': 'பில்லிங் தேதி',
        'Purchaser / GSTIN': 'வாங்குபவர் / GSTIN',
        'Gross Amount': 'மொத்த தொகை',
        'Add Purchase Invoice': 'கொள்முதல் விலைப்பட்டியலைச் சேர்',
        'Record stock procurement and automatically increment inventory counts.': 'இருப்பு கொள்முதலைப் பதிவுசெய்து தானாகவே சரக்கு எண்ணிக்கையை அதிகரிக்கவும்.',
        'Supplier Vendor': 'சப்ளையர் விற்பனையாளர்',
        'Bill Reference #': 'பில் குறிப்பு எண் #',
        'Procurement Mode': 'கொள்முதல் முறை',
        'Procured Product': 'கொள்முதல் செய்யப்பட்ட தயாரிப்பு',
        'Unit Cost (₹)': 'அலகு செலவு (₹)',
        'Quantity': 'அளவு',
        'Gross Outflow Total': 'மொத்த செலவுத் தொகை',
        'Post Procurement Invoice': 'கொள்முதல் விலைப்பட்டியலைச் சமர்ப்பி',

        // Periodical Analytics Page
        'Monthly Sales': 'மாதாந்திர விற்பனை',
        'Quarterly Sales': 'காலாண்டு விற்பனை',
        'Yearly Sales': 'ஆண்டிற்குரிய விற்பனை',
        'Print PDF Report': 'PDF அறிக்கையை அச்சிடு',
        'Monthly Revenue Velocity': 'மாதாந்திர வருவாய் வேகம்',
        'Period-over-period gross billing performance': 'காலத்திற்குரிய மொத்த பில்லிங் செயல்திறன்',
        'Historical Monthly Aggregates': 'வரலாற்று மாதாந்திர விவரங்கள்',
        'Billing Period': 'பில்லிங் காலம்',
        'Invoice Volumes': 'விலைப்பட்டியல் அளவுகள்',
        'Average Order Size (AOV)': 'சராசரி ஆர்டர் மதிப்பு (AOV)',
        'Total Value Collected': 'வசூலிக்கப்பட்ட மொத்த மதிப்பு',
        'Historical Quarterly Aggregates': 'வரலாற்று காலாண்டு விவரங்கள்',
        'Historical Annual Aggregates': 'வரலாற்று ஆண்டு விவரங்கள்',
        'Billing Year': 'பில்லிங் ஆண்டு',

        // Tax & Profit Reporter Page
        'Gross Revenue': 'மொத்த வருவாய்',
        'Turnover Pool': 'விற்பனைத் தொகுப்பு',
        'Operating Cost': 'இயக்கச் செலவு',
        'GST Collected': 'GST வசூலிக்கப்பட்டது',
        'Outward Liability': 'வெளிப்புறப் பொறுப்பு',
        'Net Profit Margin': 'நிகர லாப வரம்பு',
        'Net Retained Margin': 'நிகரத் தக்கவைக்கப்பட்ட லாபம்',
        'Revenue vs Operating Cost Velocity': 'வருவாய் மற்றும் இயக்கச் செலவு ஒப்பீடு',
        'Historical comparative cashflow trend matrix': 'வரலாற்று ஒப்பீட்டு பணப்புழக்கப் போக்கு மேட்ரிக்ஸ்',
        'Sales': 'விற்பனை',
        'Cost': 'செலவு',
        'Comprehensive Periodic Profit & Tax Grid': 'விரிவான காலமுறை லாப மற்றும் வரி விவரம்',
        'Print': 'அச்சிடு',
        'Fiscal Month': 'நிதியாண்டு மாதம்',
        'Gross Sales (Turnover)': 'மொத்த விற்பனை (விற்றுமுதல்)',
        'Outward Tax (GST)': 'வெளிப்புற வரி (GST)',
        'Operating Expenses': 'இயக்கச் செலவுகள்',
        'Retained Net Profit': 'தக்கவைக்கப்பட்ட நிகர லாபம்',
        'Profit Margin %': 'லாப வரம்பு %',

        // Festival Offers Page
        'Global Festival Offer Mode': 'ஒட்டுமொத்த திருவிழா சலுகை முறைமை',
        'When enabled, active offers will be automatically applied at the POS.': 'செயல்படுத்தப்படும்போது, செயலில் உள்ள சலுகைகள் POS-இல் தானாகவே பயன்படுத்தப்படும்.',
        'MODE ACTIVE': 'முறைமை செயலில் உள்ளது',
        'MODE INACTIVE': 'முறைமை செயலிழந்துள்ளது',
        'Available Offers': 'கிடைக்கக்கூடிய சலுகைகள்',
        'Create New Offer': 'புதிய சலுகையை உருவாக்கு',
        'All Products': 'அனைத்து தயாரிப்புகளும்',
        'Active Now': 'இப்போது செயலில் உள்ளது',
        'Scheduled / Expired': 'திட்டமிடப்பட்டது / காலாவதியானது',

        // Roles and general descriptions
        'Super Admin': 'தலைமை நிர்வாகி',
        'Admin': 'நிர்வாகி',
        'Cashier': 'காசாளர்',
        'Manager': 'மேலாளர்',

        // Months
        'January': 'ஜனவரி', 'February': 'பிப்ரவரி', 'March': 'மார்ச்', 'April': 'ஏப்ரல்',
        'May': 'மே', 'June': 'ஜூன்', 'July': 'ஜூலை', 'August': 'ஆகஸ்ட்',
        'September': 'செப்டம்பர்', 'October': 'அக்டோபர்', 'November': 'நவம்பர்', 'December': 'டிசம்பர்',
        'Jan': 'ஜன', 'Feb': 'பிப்', 'Mar': 'மார்', 'Apr': 'ஏப்', 'Jun': 'ஜூன்', 'Jul': 'ஜூலை', 'Aug': 'ஆக', 'Sep': 'செப்', 'Oct': 'அக்', 'Nov': 'நவ', 'Dec': 'டிச',

        // Insights / Intelligence App Additional Words Tamil
        'Settings': 'அமைப்புகள்',
        'Smart Insights & Predictions': 'புத்திசாலித்தனமான நுண்ணறிவு & கணிப்புகள்',
        'Shop Operations Intelligence': 'கடை செயல்பாடுகள் நுண்ணறிவு',
        'Real-time alerts, sales trajectory trends, inventory velocity, and demand forecasts.': 'நிகழ்நேர விழிப்பூட்டல்கள், விற்பனைப் போக்குகள், சரக்கு வேகம் மற்றும் தேவை கணிப்புகள்.',
        'Manage Batches': 'தொகுதிகளை நிர்வகி',
        'Operations Alert Feed': 'செயல்பாட்டு விழிப்பூட்டல் ஊட்டம்',
        'All operations are running smoothly. No active alerts found!': 'அனைத்து செயல்பாடுகளும் சீராக இயங்குகின்றன. செயலில் உள்ள விழிப்பூட்டல்கள் எதுவும் இல்லை!',
        'Sales Performance Trajectory': 'விற்பனை செயல்திறன் தடம்',
        'Total revenue collected this calendar month.': 'இந்த நடப்பு மாதத்தில் வசூலிக்கப்பட்ட மொத்த வருவாய்.',
        'Last Month': 'கடந்த மாதம்',
        'Stable': 'நிலையானது',
        'Top Selling Items': 'அதிகம் விற்பனையாகும் பொருட்கள்',
        'No sales recorded in the last 30 days.': 'கடந்த 30 நாட்களில் விற்பனை எதுவும் பதிவு செய்யப்படவில்லை.',
        'Slow-Moving Stock': 'மெதுவாக நகரும் இருப்பு',
        'No slow-moving products. Inventory moving quickly!': 'மெதுவாக நகரும் தயாரிப்புகள் எதுவும் இல்லை. சரக்கு வேகமாக நகர்கிறது!',
        'Dead Stock Alerts': 'தேக்கமடைந்த இருப்பு விழிப்பூட்டல்கள்',
        'No dead stock recorded. Healthy product cycle.': 'தேக்கமடைந்த இருப்பு எதுவும் இல்லை. ஆரோக்கியமான தயாரிப்பு சுழற்சி.',
        'Demand Forecast & Restocking Guide': 'தேவை கணிப்பு & மறுமதிப்பீட்டு வழிகாட்டி',
        'Product Name': 'தயாரிப்பு பெயர்',
        'Avg Daily Sales': 'சராசரி தினசரி விற்பனை',
        'Expected next Week': 'அடுத்த வாரம் எதிர்பார்க்கப்படுகிறது',
        'Expected next Month': 'அடுத்த மாதம் எதிர்பார்க்கப்படுகிறது',
        'Current Stock': 'தற்போதைய இருப்பு',
        'Suggested Restock': 'பரிந்துரைக்கப்பட்ட மறுமதிப்பீடு',
        'Demand Tag': 'தேவை குறிச்சொல்',
        'No physical products found in the catalog to forecast demand.': 'தேவையை கணிக்க இருப்புப் பட்டியலில் உடல் தயாரிப்புகள் எதுவும் இல்லை.',
        'Actual vs. Forecasted Weekly Demand Trend': 'உண்மையான மற்றும் கணிக்கப்பட்ட வாராந்திர தேவைப் போக்கு',
        'Actual Weekly Demand': 'உண்மையான வாராந்திர தேவை',
        'Forecasted Weekly Demand': 'கணிக்கப்பட்ட வாராந்திர தேவை',
        'Current Week': 'நடப்பு வாரம்',
        'Sufficient': 'போதுமானது',
        'High Velocity': 'அதிவேகம்',
        'Normal': 'சாதாரணமானது',
        'Stock depletion alert': 'இருப்பு குறைப்பு விழிப்பூட்டல்',
        'Low stock warning': 'குறைந்த இருப்பு எச்சரிக்கை',
        'Expired inventory': 'காலாவதியான இருப்பு',
        'Expiry warning': 'காலாவதி எச்சரிக்கை',
        'Sales performance warning': 'விற்பனை செயல்திறன் எச்சரிக்கை',
        'Smart Insights & Forecasting | Retail Billing': 'புத்திசாலித்தனமான நுண்ணறிவு & கணிப்பு | சில்லறை பில்லிங்',
        'Weekly Demand Trend': 'வாராந்திர தேவைப் போக்கு',
        'Weekly Demand': 'வாராந்திர தேவை',
        'Sold': 'விற்கப்பட்டது',
        'Sold (30d)': 'விற்கப்பட்டது (30நாட்கள்)',
        'Stock:': 'இருப்பு:',
        'Value:': 'மதிப்பு:',
        'Batch & Expiry Management | Retail Billing': 'தொகுதி & காலாவதி மேலாண்மை | சில்லறை பில்லிங்',
        'Batch & Expiry Tracking': 'தொகுதி & காலாவதி கண்காணிப்பு',
        'Active Batches': 'செயலில் உள்ள தொகுதிகள்',
        'Expired Batches': 'காலாவதியான தொகுதிகள்',
        'Expiring Soon': 'விரைவில் காலாவதியாகிறது',
        'Add New Batch': 'புதிய தொகுதியைச் சேர்',
        'Search batch number or SKU...': 'தொகுதி எண் அல்லது SKU மூலம் தேடு...',
        'Pricing and checkout automatically select oldest unexpired batches first.': 'பில்லிங் மற்றும் செக்அவுட் தானாகவே பழமையான காலாவதியாகாத தொகுதிகளை முதலில் தேர்ந்தெடுக்கும்.',
        'Batch Number': 'தொகுதி எண்',
        'Mfg Date': 'தயாரிப்பு தேதி',
        'Expiry Date': 'காலாவதி தேதி',
        'Sold Out': 'முழுவதும் விற்கப்பட்டது',
        'Healthy': 'ஆரோக்கியமானது',
        'Delete Batch': 'தொகுதியை நீக்கு',
        'Are you sure you want to remove batch': 'தொகுதியை நீக்க விரும்புகிறீர்களா',
        'This will adjust the product\'s overall stock quantity accordingly.': 'இது தயாரிப்பின் மொத்த இருப்பு அளவை அதற்கேற்ப சரிசெய்யும்.',
        'Register Inventory Batch': 'சரக்கு தொகுதியை பதிவு செய்',
        'Select Product': 'தயாரிப்பைத் தேர்ந்தெடு',
        '-- Select Product --': '-- தயாரிப்பைத் தேர்ந்தெடு --',
        'Mfg Date (Optional)': 'தயாரிப்பு தேதி (விருப்பத்தேர்வு)',
        'Initial Batch Stock Quantity': 'ஆரம்ப தொகுதி இருப்பு அளவு',
        'Save Batch': 'தொகுதியைச் சேமி',
        'No batches currently loaded. Register a batch during purchase entries or click "Add New Batch".': 'தற்போது தொகுதிகள் எதுவும் இல்லை. கொள்முதல் பதிவுகளின் போது தொகுதியை பதிவு செய்யவும் அல்லது "புதிய தொகுதியைச் சேர்" என்பதைக் கிளிக் செய்யவும்.',
        'Intelligence Settings | Retail Billing': 'நுண்ணறிவு அமைப்புகள் | சில்லறை பில்லிங்',
        'Intelligence & Dynamic Pricing Settings': 'நுண்ணறிவு & மாறும் விலை அமைப்புகள்',
        'Advanced Control Panel': 'மேம்பட்ட கட்டுப்பாட்டு பலகை',
        'Enable features, modify alert thresholds, and customize dynamic pricing rules.': 'அம்சங்களைச் செயல்படுத்தவும், எச்சரிக்கை வரம்புகளை மாற்றவும் மற்றும் மாறும் விலை விதிகளைத் தனிப்பயனாக்கவும்.',
        'Email Alert Digest Now': 'இப்போது மின்னஞ்சல் எச்சரிக்கை சுருக்கத்தை அனுப்பு',
        'Save Configurations': 'அமைப்புகளைச் சேமி',
        'Active Modules': 'செயலில் உள்ள தொகுதிகள்',
        'Calculates average daily sales velocity, predicts product stock-out dates, and warns about dead stock.': 'தினசரி சராசரி விற்பனை வேகத்தைக் கணக்கிடுகிறது, தயாரிப்பு இருப்பு காலியாகும் தேதிகளைக் கணித்து, தேக்கமடைந்த இருப்பைப் பற்றி எச்சரிக்கிறது.',
        'Demand Forecasting': 'தேவை கணிப்பு',
        'Predicts sales for next week and next month using historical sales data and weighted trends, then suggests restocking amounts.': 'வரலாற்று விற்பனை தரவு மற்றும் எடையுள்ள போக்குகளைப் பயன்படுத்தி அடுத்த வாரம் மற்றும் அடுத்த மாதத்திற்கான விற்பனையைக் கணிக்கிறது, பின்னர் இருப்பு நிரப்புதல் அளவுகளைப் பரிந்துரைக்கிறது.',
        'Dynamic Pricing System': 'மாறும் விலை முறைமை',
        'Automatically adjusts prices in the POS catalog based on low stock quantities, high sales demand levels, and near-expiry clearance rules.': 'குறைந்த இருப்பு அளவுகள், அதிக விற்பனைத் தேவை நிலைகள் மற்றும் காலாவதியாகும் நிலை ஆகியவற்றின் அடிப்படையில் POS பட்டியலில் விலைகளை தானாகவே சரிசெய்கிறது.',
        'Operation Thresholds': 'செயல்பாட்டு வரம்புகள்',
        'Low Stock Threshold': 'குறைந்த இருப்பு வரம்பு',
        'Alerts dashboard and triggers low stock price markup when stock drops below this value.': 'இருப்பு இந்த மதிப்புக்கு கீழே குறையும் போது கட்டுப்பாட்டு பலகையை எச்சரிக்கிறது மற்றும் குறைந்த இருப்பு விலை உயர்வை இயக்குகிறது.',
        'Expiry Alert Threshold (Days)': 'காலாவதி எச்சரிக்கை வரம்பு (நாட்கள்)',
        'Generates warning alerts and applies clearance discount rules when a batch is within this expiry window.': 'ஒரு தொகுதி இந்த காலாவதி சாளரத்திற்குள் இருக்கும்போது எச்சரிக்கைகளை உருவாக்குகிறது மற்றும் தள்ளுபடி விதிகளைப் பயன்படுத்துகிறது.',
        'Dynamic Pricing Rules (%)': 'மாறும் விலை விதிகள் (%)',
        'Increases pricing by this percentage when product stock is below your low stock threshold.': 'தயாரிப்பு இருப்பு உங்கள் குறைந்த இருப்பு வரம்பிற்கு கீழே இருக்கும்போது இந்த சதவீதத்தால் விலையை அதிகரிக்கிறது.',
        'Increases base price when average sales exceed 1.5 units per day over the last 7 days.': 'கடந்த 7 நாட்களில் சராசரி விற்பனை ஒரு நாளைக்கு 1.5 அலகுகளைத் தாண்டும்போது அடிப்படை விலையை அதிகரிக்கிறது.',
        'Deducts this percentage from standard pricing when the active stock batch is expiring soon.': 'செயலில் உள்ள இருப்பு தொகுதி விரைவில் காலாவதியாகும் போது நிலையான விலையிலிருந்து இந்த சதவீதத்தைக் கழிக்கிறது.',
        'Admin (Shop Owner)': 'நிர்வாகி (கடை உரிமையாளர்)',
        'SHOP OWNER': 'கடை உரிமையாளர்',
        'Insights': 'நுண்ணறிவு',
        'Batches': 'தொகுதிகள்',
        'units': 'அலகுகள்',
        'Units': 'அலகுகள்'
    }
};

let currentLang = localStorage.getItem('posLang') || 'EN';

function translateDOM() {
    const dict = translations[currentLang];
    if (!dict) return;
    
    // Sort keys based on length descending to translate longer multi-word phrases first
    const enDict = translations['EN'];
    const taDict = translations['TA'];
    let keys = Object.keys(enDict);
    
    if (currentLang === 'TA') {
        keys.sort((a, b) => b.length - a.length);
    } else {
        keys.sort((a, b) => (taDict[b] || '').length - (taDict[a] || '').length);
    }

    // Traverse and replace text nodes using tree walker
    const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
    let n;
    while (n = walk.nextNode()) {
        // Skip script, style and standard input areas to prevent breaking functional bindings
        if (n.parentElement && (
            n.parentElement.tagName === 'SCRIPT' || 
            n.parentElement.tagName === 'STYLE' || 
            n.parentElement.tagName === 'NOSCRIPT' || 
            n.parentElement.tagName === 'TEXTAREA'
        )) {
            continue;
        }

        let text = n.textContent;
        let originalText = text;

        if (currentLang === 'TA') {
            for (let key of keys) {
                if (key.trim() === '') continue;
                if (text.includes(key)) {
                    console.log('[Translation Engine] Match found! Replacing "' + key + '" with "' + taDict[key] + '"');
                    text = text.split(key).join(taDict[key]);
                }
            }
            
            // Dynamic alert matching for Operations Feed
            // 1. Expired warning
            if (text.includes("expired on")) {
                const match = text.match(/\s*Batch\s+'([^']+)'\s+of\s+'([^']+)'\s+expired\s+on\s+([^!]+)!\s*/);
                if (match) {
                    text = `தொகுதி '${match[1]}' (தயாரிப்பு: '${match[2]}') ${match[3]} அன்று காலாவதியானது!`;
                }
            }
            // 2. Expiring soon
            if (text.includes("expires in")) {
                const match = text.match(/\s*Batch\s+'([^']+)'\s+of\s+'([^']+)'\s+expires\s+in\s+(\d+)\s+days\s+\(([^)]+)\)\.\s*/);
                if (match) {
                    text = `தொகுதி '${match[1]}' (தயாரிப்பு: '${match[2]}') ${match[3]} நாட்களில் (${match[4]}) காலாவதியாகிறது.`;
                }
            }
            // 3. Stock runout prediction
            if (text.includes("will run out in approximately")) {
                const match = text.match(/\s*Product\s+'([^']+)'\s+will\s+run\s+out\s+in\s+approximately\s+(\d+)\s+days\s+based\s+on\s+sales\s+velocity\.\s*/);
                if (match) {
                    text = `தயாரிப்பு '${match[1]}' விற்பனை வேகத்தின் அடிப்படையில் சுமார் ${match[2]} நாட்களில் தீர்ந்துவிடும்.`;
                }
            }
            // 4. Low stock
            if (text.includes("is below low stock threshold")) {
                const match = text.match(/\s*Product\s+'([^']+)'\s+is\s+below\s+low\s+stock\s+threshold\.\s+Current\s+stock:\s+(\d+)\.\s*/);
                if (match) {
                    text = `தயாரிப்பு '${match[1]}' குறைந்த இருப்பு வரம்பிற்குக் கீழே உள்ளது. தற்போதைய இருப்பு: ${match[2]}.`;
                }
            }
        } else {
            for (let key of keys) {
                if (taDict[key].trim() === '') continue;
                if (text.includes(taDict[key])) {
                    console.log('[Translation Engine] Match found! Restoring "' + taDict[key] + '" to "' + key + '"');
                    text = text.split(taDict[key]).join(key);
                }
            }
        }

        if (text !== originalText) {
            console.log('[Translation Engine] DOM Update:', originalText.trim(), '->', text.trim());
            n.textContent = text;
        }
    }

    // Translate input placeholders
    document.querySelectorAll('input[placeholder]').forEach(input => {
        let ph = input.getAttribute('placeholder');
        if (!ph) return;

        let originalPh = ph;
        if (currentLang === 'TA') {
            for (let key of keys) {
                if (key.trim() === '') continue;
                ph = ph.split(key).join(taDict[key]);
            }
        } else {
            for (let key of keys) {
                if (taDict[key].trim() === '') continue;
                ph = ph.split(taDict[key]).join(key);
            }
        }

        if (ph !== originalPh) {
            input.setAttribute('placeholder', ph);
        }
    });

    const langText = document.getElementById('langText');
    if (langText) {
        langText.innerText = currentLang;
    }
}

function toggleLanguage() {
    currentLang = currentLang === 'EN' ? 'TA' : 'EN';
    localStorage.setItem('posLang', currentLang);
    translateDOM();
    
    if (currentLang === 'TA') {
        showToast('தமிழ் மொழி தேர்ந்தெடுக்கப்பட்டது', 'success');
    } else {
        showToast('English selected', 'success');
    }
}

// Trigger initial translation if stored preference is TA, avoiding race conditions
function initLanguage() {
    if (currentLang === 'TA') {
        setTimeout(translateDOM, 100); // Let dynamic content load a bit first
    }
}

if (document.readyState === 'interactive' || document.readyState === 'complete') {
    initLanguage();
} else {
    document.addEventListener('DOMContentLoaded', initLanguage);
}
