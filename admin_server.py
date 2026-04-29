import http.server
import socketserver

PORT = 8080

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-body: #f3f4f6;
            --sidebar-bg: #1e40af; 
            --sidebar-hover: #2563eb;
            --primary: #3b82f6;
            --card-bg: #ffffff;
            --text-main: #f9fafb;
            --text-dark: #1f2937;
            --border: #e5e7eb;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: "Poppins", sans-serif; }
        body { background: var(--bg-body); color: var(--text-dark); height: 100vh; overflow-x: hidden; }

        /* --- LOADER (Fixed) --- */
        #loader-screen {
            position: fixed; left: 0; top: 0; width: 100%; height: 100%;
            background: var(--sidebar-bg); z-index: 9999;
            display: none; /* Default Hidden */
            justify-content: center; align-items: center; flex-direction: column;
        }
        .spinner {
            width: 50px; height: 50px; border: 5px solid rgba(255,255,255,0.3);
            border-radius: 50%; border-top-color: white;
            animation: spin 1s ease-in-out infinite; margin-bottom: 15px;
        }
        .loading-text { color: white; font-weight: 600; font-size: 16px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

        /* --- LOGIN --- */
        #login-section {
            height: 100vh; display: flex; align-items: center; justify-content: center;
            background: linear-gradient(135deg, #1e1b4b 0%, #4c1d95 100%); position: fixed; width: 100%; z-index: 1000;
        }
        .login-card { background: rgba(255,255,255, 0.1); backdrop-filter: blur(15px); padding: 45px; border-radius: 20px; width: 350px; text-align: center; color: white; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); border: 1px solid rgba(255,255,255,0.2); }
        .login-input { width: 100%; padding: 12px; margin: 10px 0; border-radius: 8px; border: 1px solid rgba(255,255,255,0.3); background: rgba(255,255,255,0.05); color: white; outline: none; }
        .login-btn { width: 100%; padding: 12px; margin-top: 20px; background: linear-gradient(to right, #4f46e5, #6366f1); border: none; border-radius: 8px; color: white; font-weight: bold; cursor: pointer; }
        .login-btn:disabled { opacity: 0.6; cursor: not-allowed; } /* Disable style */

        /* --- LAYOUT --- */
        #dashboard { display: none; } /* Default Hidden */
        .sidebar { width: 260px; background: var(--sidebar-bg); height: 100vh; position: fixed; left: 0; top: 0; display: flex; flex-direction: column; color: var(--text-main); z-index: 50; }
        .logo-area { padding: 30px 20px; font-size: 22px; font-weight: 700; color: white; border-bottom: 1px solid rgba(255,255,255,0.1); }
        .menu { padding: 20px 10px; flex: 1; }
        .menu-item { padding: 14px 20px; display: flex; align-items: center; gap: 12px; cursor: pointer; transition: 0.3s; border-radius: 8px; margin-bottom: 5px; color: #dbeafe; font-weight: 500; pointer-events: auto; }
        .menu-item:hover, .menu-item.active { background: rgba(255,255,255,0.15); color: white; padding-left: 25px; }
        
        .main-content { margin-left: 260px; padding: 30px; transition: 0.3s; width: calc(100% - 260px); }
        
        /* --- HEADER --- */
        .top-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
        .profile-btn { display: flex; align-items: center; gap: 10px; cursor: pointer; background: white; padding: 5px 15px; border-radius: 30px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
        .avatar { width: 40px; height: 40px; background: var(--primary); border-radius: 50%; display: flex; justify-content: center; align-items: center; color: white; font-weight: bold; font-size: 16px; }

        /* --- PAGES --- */
        .page-card { background: var(--card-bg); padding: 25px; border-radius: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid var(--border); }
        .search-box { width: 100%; padding: 12px 15px; border: 1px solid var(--border); border-radius: 8px; outline: none; margin-bottom: 20px; }
        .data-table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 14px; }
        .data-table th { text-align: left; padding: 15px; color: #64748b; font-weight: 600; border-bottom: 2px solid #f3f4f6; font-size: 13px; }
        .data-table td { padding: 15px; border-bottom: 1px solid #f3f4f6; color: var(--text-dark); }
        .data-table tr:hover { background: #f9fafb; }
        .table-responsive { overflow-x: auto; }

        /* Profile Page Styles */
        .profile-layout { display: flex; gap: 30px; flex-wrap: wrap; }
        .profile-avatar-box { flex: 1; min-width: 300px; text-align: center; }
        .avatar-xl { width: 150px; height: 150px; background: linear-gradient(135deg, var(--primary), var(--sidebar-hover)); border-radius: 50%; margin: 0 auto 20px; display: flex; justify-content: center; align-items: center; color: white; font-size: 50px; }
        .profile-info-box { flex: 2; min-width: 400px; }
        .info-row { display: flex; justify-content: space-between; padding: 15px 0; border-bottom: 1px solid #f3f4f6; }
        .info-label { color: #64748b; font-size: 14px; }
        .info-value { font-weight: 600; color: var(--text-dark); font-size: 15px; }

        /* Settings Grid */
        .settings-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .form-group { margin-bottom: 20px; }
        .form-label { display: block; font-size: 13px; font-weight: 600; margin-bottom: 8px; color: var(--text-dark); }
        .form-input { width: 100%; padding: 12px; border: 1px solid var(--border); border-radius: 6px; background: var(--bg-body); }
        .btn-primary { background: var(--primary); color: white; padding: 12px 25px; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; }
        
        /* Stats Overview */
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 25px; margin-bottom: 30px; }
        .stat-value { font-size: 28px; font-weight: 700; color: var(--text-dark); }
        .stat-label { color: #64748b; font-size: 14px; }

        /* Responsive */
        @media (max-width: 768px) {
            .sidebar { left: -260px; } .sidebar.active { left: 0; box-shadow: 0 0 50px rgba(0,0,0,0.5); }
            .main-content { margin-left: 0; width: 100%; padding: 15px; padding-top: 60px; }
        }
        .mobile-menu-btn { display: none; position: fixed; top: 15px; right: 15px; background: white; padding: 10px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); cursor: pointer; z-index: 100; }
        @media (max-width: 768px) { .mobile-menu-btn { display: block; } }

    </style>
</head>
<body>

    <!-- LOADING SCREEN -->
    <div id="loader-screen">
        <div class="spinner"></div>
        <div class="loading-text">Loading Dashboard...</div>
    </div>

    <!-- LOGIN -->
    <div id="login-section">
        <div class="login-card">
            <h2 style="margin-bottom: 10px;">Admin Login</h2>
            <p style="color: #d1d5db; margin-bottom: 20px;">Secure Access</p>
            <input type="text" id="username" class="login-input" placeholder="Username">
            <input type="password" id="password" class="login-input" placeholder="Password">
            <button id="login-btn" class="login-btn" onclick="login()">LOGIN</button>
            <div id="msg" style="color: #fca5a5; margin-top: 15px; font-size: 13px;"></div>
        </div>
    </div>

    <!-- DASHBOARD -->
    <div id="dashboard">
        <!-- Mobile Menu Button -->
        <div class="mobile-menu-btn" onclick="toggleMobile()">?</div>

        <div class="sidebar" id="sidebar">
            <div class="logo-area">Ride N Repair</div>
            <div class="menu">
                <div class="menu-item active" onclick="showPage('overview', this)">Overview</div>
                <div class="menu-item" onclick="showPage('customers', this)">Customers</div>
                <div class="menu-item" onclick="showPage('orders', this)">Orders</div>
                <div class="menu-item" onclick="showPage('profile', this)">My Profile</div>
                <div class="menu-item" onclick="showPage('settings', this)">Settings</div>
                <div class="menu-item" onclick="logout()" style="margin-top: 20px; color: #ef4444;">Logout</div>
            </div>
        </div>

        <div class="main-content">
            <div class="top-header">
                <div class="header-left">
                    <h2 id="page-title" style="font-size: 24px;">Overview</h2>
                </div>
                <div class="profile-btn" onclick="alert('Menu Feature')">
                    <div class="avatar">AD</div>
                    <span>Admin</span>
                </div>
            </div>

            <!-- OVERVIEW -->
            <div id="overview">
                <div class="stats-grid">
                    <div class="page-card"><div class="stat-label">Total Revenue</div><div class="stat-value">Rs 24.5L</div></div>
                    <div class="page-card"><div class="stat-label">Total Orders</div><div class="stat-value">1,245</div></div>
                    <div class="page-card"><div class="stat-label">Active Users</div><div class="stat-value">850</div></div>
                </div>
            </div>

            <!-- CUSTOMERS PAGE -->
            <div id="customers" style="display:none;">
                <div class="page-card">
                    <h3 style="margin-bottom: 15px;">Customer Management</h3>
                    <input type="text" class="search-box" placeholder="Search customers..." onkeyup="filterTable(1)">
                    <div class="table-responsive">
                        <table class="data-table">
                            <thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Phone</th><th>Status</th></tr></thead>
                            <tbody>
                                <tr><td>#001</td><td>Rajesh Kumar</td><td>rajesh@email.com</td><td>+91 98765 43210</td><td><span style="color:green; font-weight:600;">Active</span></td></tr>
                                <tr><td>#002</td><td>Anita Singh</td><td>anita@email.com</td><td>+91 88776 55443</td><td><span style="color:green; font-weight:600;">Active</span></td></tr>
                                <tr><td>#003</td><td>Prakash Verma</td><td>prakash@email.com</td><td>+91 77665 11223</td><td><span style="color:orange; font-weight:600;">Pending</span></td></tr>
                                <tr><td>#004</td><td>Vikram Malhotra</td><td>vikram@email.com</td><td>+91 96655 44332</td><td><span style="color:red; font-weight:600;">Inactive</span></td></tr>
                                <tr><td>#005</td><td>Suresh Reddy</td><td>suresh@email.com</td><td>+91 99887 77889</td><td><span style="color:green; font-weight:600;">Active</span></td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- ORDERS PAGE -->
            <div id="orders" style="display:none;">
                <div class="page-card">
                    <h3 style="margin-bottom: 15px;">Order Management</h3>
                    <div class="table-responsive">
                        <table class="data-table">
                            <thead><tr><th>Order ID</th><th>Service</th><th>Vehicle</th><th>Amount</th><th>Status</th><th>Date</th></tr></thead>
                            <tbody>
                                <tr><td>#ORD-4451</td><td>General Service</td><td>Maruti Swift</td><td>Rs 2,499</td><td><span style="color:green; font-weight:600;">Completed</span></td><td>28-Apr-2026</td></tr>
                                <tr><td>#ORD-4452</td><td>Audi A4 Repair</td><td>Audi A4</td><td>Rs 8,500</td><td><span style="color:orange; font-weight:600;">In Progress</span></td><td>27-Apr-2026</td></tr>
                                <tr><td>#ORD-4453</td><td>Oil Change</td><td>Honda City</td><td>Rs 1,200</td><td><span style="color:green; font-weight:600;">Completed</span></td><td>26-Apr-2026</td></tr>
                                <tr><td>#ORD-4454</td><td>Brake Repair</td><td>Hyundai Creta</td><td>Rs 3,500</td><td><span style="color:red; font-weight:600;">Cancelled</span></td><td>25-Apr-2026</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- PROFILE PAGE -->
            <div id="profile" style="display:none;">
                <div class="profile-layout">
                    <div class="profile-avatar-box">
                        <div class="avatar-xl">AD</div>
                        <h3 style="margin-top: 15px;">Admin User</h3>
                        <p style="color: #64748b;">Super Administrator</p>
                        <button class="btn-primary" style="width: 100%; margin-top: 20px;">Update Photo</button>
                    </div>
                    <div class="profile-info-box page-card">
                        <h3 style="margin-bottom: 20px; color: var(--primary);">Personal Details</h3>
                        <div class="info-row"><div class="info-label">Full Name</div><div class="info-value">Admin User</div></div>
                        <div class="info-row"><div class="info-label">User ID</div><div class="info-value">#RID-0012</div></div>
                        <div class="info-row"><div class="info-label">Email</div><div class="info-value">admin@ridenrepair.com</div></div>
                        <div class="info-row"><div class="info-label">Phone</div><div class="info-value">+91 98765 43210</div></div>
                        <div class="info-row"><div class="info-label">Role</div><div class="info-value" style="color: var(--primary);">Super Admin</div></div>
                        <div class="info-row"><div class="info-label">Location</div><div class="info-value">New Delhi, India</div></div>
                        <div class="info-row" style="border:none; margin-top: 20px;">
                            <button class="btn-primary" style="background: var(--sidebar-bg); margin-right: 10px;">Cancel</button>
                            <button class="btn-primary">Save Changes</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- SETTINGS PAGE -->
            <div id="settings" style="display:none;">
                <div class="settings-grid">
                    <div class="page-card">
                        <h3 style="margin-bottom: 20px;">Account</h3>
                        <div class="form-group">
                            <label class="form-label">Username</label>
                            <input type="text" class="form-input" value="admin" disabled style="opacity: 0.6;">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Email</label>
                            <input type="email" class="form-input" value="admin@ridenrepair.com">
                        </div>
                    </div>
                    <div class="page-card">
                        <h3 style="margin-bottom: 20px;">Security</h3>
                        <div class="form-group">
                            <label class="form-label">Current Password</label>
                            <input type="password" class="form-input" placeholder="Current">
                        </div>
                        <div class="form-group">
                            <label class="form-label">New Password</label>
                            <input type="password" class="form-input" placeholder="New">
                        </div>
                        <button class="btn-primary">Update Password</button>
                    </div>
                </div>
            </div>

        </div>
    </div>

    <script>
        function login() {
            var u = document.getElementById('username').value;
            var p = document.getElementById('password').value;
            var m = document.getElementById('msg');
            var btn = document.getElementById('login-btn');

            if(u === 'admin' && p === 'admin') {
                // FIX: Disable button so user cannot click again
                btn.disabled = true; 
                
                // Show Loader
                document.getElementById('loader-screen').style.display = 'flex';

                // Wait 1 second then login
                setTimeout(() => {
                    document.getElementById('loader-screen').style.display = 'none';
                    document.getElementById('login-section').style.display = 'none';
                    document.getElementById('dashboard').style.display = 'block';
                    // Re-enable button for logout scenario
                    btn.disabled = false; 
                }, 1000); 
            } else {
                m.innerText = 'Invalid Credentials';
            }
        }
        function logout() {
            location.reload(); // Reload page to reset everything
        }
        function showPage(id, el) {
            // Hide all pages
            var pages = ['overview', 'customers', 'orders', 'profile', 'settings'];
            pages.forEach(p => {
                var elPage = document.getElementById(p);
                if(elPage) elPage.style.display = 'none';
            });
            // Show selected
            document.getElementById(id).style.display = 'block';
            
            // Update Title
            var title = id.charAt(0).toUpperCase() + id.slice(1);
            document.getElementById('page-title').innerText = title;
            
            // Sidebar Active State
            var items = document.querySelectorAll('.menu-item');
            items.forEach(i => i.classList.remove('active'));
            if(el) el.classList.add('active');

            // Close sidebar on mobile
            if(window.innerWidth <= 768) document.getElementById('sidebar').classList.remove('active');
        }
        function toggleMobile() {
            document.getElementById('sidebar').classList.toggle('active');
        }
        function filterTable(colIndex) {
            var input, filter, table, tr, td, i, txtValue;
            input = event.target;
            filter = input.value.toUpperCase();
            table = document.querySelector('.data-table');
            tr = table.getElementsByTagName("tr");
            for (i = 1; i < tr.length; i++) {
                td = tr[i].getElementsByTagName("td")[colIndex];
                if (td) {
                    txtValue = td.textContent || td.innerText;
                    if (txtValue.toUpperCase().indexOf(filter) > -1) {
                        tr[i].style.display = "";
                    } else {
                        tr[i].style.display = "none";
                    }
                }       
            }
        }
    </script>
</body>
</html>
"""

class AdminHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if 'dashboard.html' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
        else:
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), AdminHandler) as httpd:
    print("Stable Loader Version running at http://localhost:8080/dashboard.html")
    httpd.serve_forever()
