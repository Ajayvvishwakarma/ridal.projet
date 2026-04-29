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
            /* NEW THEME COLORS */
            --bg-body: #f3f4f6;
            --sidebar-bg: #1e40af; /* Royal Blue Sidebar */
            --sidebar-hover: #2563eb;
            --primary: #3b82f6;
            --card-bg: #ffffff;
            --text-main: #ffffff;
            --text-dark: #1f2937;
            --text-light: #94a3b8;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: "Poppins", sans-serif; }
        body { background: var(--bg-body); color: var(--text-dark); height: 100vh; overflow-x: hidden; }

        /* --- LOGIN (Gradient Background Restored) --- */
        #login-section {
            height: 100vh; display: flex; align-items: center; justify-content: center;
            background: linear-gradient(135deg, #1e1b4b 0%, #4c1d95 100%); /* The Gradient You Liked */
            position: fixed; width: 100%; z-index: 1000;
        }
        .login-card {
            background: rgba(255, 255, 255, 0.1); /* Glass Effect */
            backdrop-filter: blur(15px);
            padding: 45px; border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            width: 350px; text-align: center; color: white;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }
        .login-card h2 { font-size: 24px; margin-bottom: 5px; }
        .login-card p { color: #d1d5db; font-size: 13px; margin-bottom: 25px; }
        .login-input {
            width: 100%; padding: 12px; margin: 10px 0; border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.3);
            background: rgba(255,255,255,0.05); color: white; outline: none;
            transition: 0.3s;
        }
        .login-input:focus { border-color: var(--primary); background: rgba(255,255,255,0.15); }
        .login-btn {
            width: 100%; padding: 12px; margin-top: 20px;
            background: linear-gradient(to right, #4f46e5, #6366f1);
            color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
            transition: 0.3s;
        }
        .login-btn:hover { transform: translateY(-2px); }
        .error-msg { color: #fca5a5; margin-top: 15px; font-size: 13px; font-weight: 600; }

        /* --- DASHBOARD LAYOUT --- */
        #dashboard { display: none; }
        .sidebar {
            width: 260px; background: var(--sidebar-bg); height: 100vh;
            position: fixed; left: 0; top: 0;
            display: flex; flex-direction: column;
            color: var(--text-main);
            transition: 0.3s;
        }
        .logo-area { padding: 30px 20px; font-size: 22px; font-weight: 700; color: white; border-bottom: 1px solid rgba(255,255,255,0.1); }
        .logo-area span { color: var(--sidebar-hover); }
        
        .menu { padding: 20px 10px; flex: 1; }
        .menu-item {
            padding: 14px 20px; display: flex; align-items: center; gap: 15px;
            cursor: pointer; transition: 0.3s; border-radius: 8px; margin-bottom: 5px;
            color: #dbeafe; /* Light Blue Text */
        }
        .menu-item:hover, .menu-item.active { background: rgba(255,255,255,0.15); color: white; padding-left: 25px; }
        
        .main-content { margin-left: 260px; padding: 30px; width: calc(100% - 260px); transition: 0.3s; }
        
        /* --- HEADER --- */
        .top-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
        .page-title h2 { font-size: 24px; font-weight: 600; color: var(--text-dark); }
        .profile-btn {
            display: flex; align-items: center; gap: 10px; cursor: pointer;
            background: white; padding: 5px 15px; border-radius: 30px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); transition: 0.2s;
        }
        .avatar { width: 40px; height: 40px; background: var(--primary); border-radius: 50%; display: flex; justify-content: center; align-items: center; color: white; font-weight: bold; }

        /* --- DROPDOWN --- */
        .dropdown-menu { display: none; position: absolute; top: 60px; right: 0; background: white; width: 200px; border-radius: 12px; box-shadow: 0 10px 15px rgba(0,0,0,0.1); padding: 10px 0; z-index: 100; border: 1px solid #e5e7eb; }
        .dropdown-menu.show { display: block; }
        .dd-item { padding: 10px 20px; cursor: pointer; font-size: 14px; color: var(--text-dark); transition: 0.2s; }
        .dd-item:hover { background: #f3f4f6; color: var(--primary); }
        .dd-divider { height: 1px; background: #e5e7eb; margin: 8px 0; }

        /* --- CARDS --- */
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 25px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 25px; border-radius: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #e5e7eb; }
        .stat-value { font-size: 28px; font-weight: 700; color: var(--text-dark); }
        .stat-label { color: #64748b; font-size: 14px; }

        /* --- TOAST --- */
        #toast { visibility: hidden; min-width: 250px; background: var(--sidebar-bg); color: #fff; text-align: center; border-radius: 8px; padding: 16px; position: fixed; z-index: 2000; left: 50%; bottom: 30px; transform: translateX(-50%); box-shadow: 0 10px 25px rgba(0,0,0,0.2); }
        #toast.show { visibility: visible; animation: fadein 0.5s, fadeout 0.5s 2.5s; }
        @keyframes fadein { from {bottom: 0; opacity: 0;} to {bottom: 30px; opacity: 1;} }
        @keyframes fadeout { from {bottom: 30px; opacity: 1;} to {bottom: 0; opacity: 0;} }
    </style>
</head>
<body>

    <!-- LOGIN -->
    <div id="login-section">
        <div class="login-card">
            <h2>Admin Login</h2>
            <p>Secure Access Portal</p>
            <input type="text" id="username" class="login-input" placeholder="Username">
            <input type="password" id="password" class="login-input" placeholder="Password">
            <button class="login-btn" onclick="login()">LOGIN DASHBOARD</button>
            <div id="msg" class="error-msg"></div>
        </div>
    </div>

    <!-- DASHBOARD -->
    <div id="dashboard">
        <div class="sidebar">
            <div class="logo-area">Ride<span>NRepair</span></div>
            <div class="menu">
                <div class="menu-item active" onclick="showPage('overview', this)">Overview</div>
                <div class="menu-item" onclick="showPage('customers', this)">Customers</div>
                <div class="menu-item" onclick="showPage('orders', this)">Orders</div>
                <div class="menu-item" onclick="showPage('settings', this)">Settings</div>
                <div class="menu-item" onclick="logout()" style="margin-top: 20px; color: #ef4444;">Logout</div>
            </div>
        </div>

        <div class="main-content">
            <div class="top-header">
                <div class="page-title"><h2 id="page-title">Overview</h2></div>
                <div class="profile-btn" onclick="toggleProfile()">
                    <div class="avatar">AD</div>
                    <span>Admin ?</span>
                    
                    <div class="dropdown-menu" id="profile-dropdown">
                        <div class="dd-item" onclick="showPage('settings', null)">Settings</div>
                        <div class="dd-item" onclick="showToast('My Profile')">My Profile</div>
                        <div class="dd-divider"></div>
                        <div class="dd-item" style="color:#ef4444;" onclick="logout()">Logout</div>
                    </div>
                </div>
            </div>

            <!-- Pages -->
            <div id="overview">
                <div class="stats-grid">
                    <div class="stat-card"><div class="stat-label">Revenue</div><div class="stat-value">Rs 24.5L</div></div>
                    <div class="stat-card"><div class="stat-label">Orders</div><div class="stat-value">1,245</div></div>
                    <div class="stat-card"><div class="stat-label">Users</div><div class="stat-value">850</div></div>
                </div>
            </div>

            <div id="customers" style="display:none;">
                <div class="stat-card" style="padding:20px;">Customers List Coming Soon...</div>
            </div>
            
            <div id="orders" style="display:none;">
                <div class="stat-card" style="padding:20px;">Orders List Coming Soon...</div>
            </div>

            <div id="settings" style="display:none;">
                <div class="stat-card" style="padding:20px;">Settings Panel Coming Soon...</div>
            </div>

        </div>
    </div>

    <div id="toast">Notification</div>

    <script>
        function login() {
            var u = document.getElementById('username').value;
            var p = document.getElementById('password').value;
            var m = document.getElementById('msg');
            
            // Check credentials
            if (u === 'admin' && p === 'admin') {
                document.getElementById('login-section').style.display = 'none';
                document.getElementById('dashboard').style.display = 'block';
            } else {
                m.innerText = 'Invalid Credentials';
                m.style.animation = 'shake 0.5s';
                setTimeout(() => m.style.animation = '', 500);
            }
        }
        function logout() {
            document.getElementById('dashboard').style.display = 'none';
            document.getElementById('login-section').style.display = 'flex';
            document.getElementById('profile-dropdown').classList.remove('show');
            document.getElementById('username').value = '';
            document.getElementById('password').value = '';
        }
        function showPage(id, el) {
            document.querySelectorAll('[id^="overview"], [id^="customers"], [id^="orders"], [id^="settings"]').forEach(p => {
                if(p.tagName === 'DIV') p.style.display = 'none';
            });
            document.getElementById(id).style.display = 'block';
            document.getElementById('page-title').innerText = id.charAt(0).toUpperCase() + id.slice(1);
            
            document.querySelectorAll('.menu-item').forEach(i => i.classList.remove('active'));
            if(el) el.classList.add('active');
            
            document.getElementById('profile-dropdown').classList.remove('show');
        }
        function toggleProfile() {
            document.getElementById('profile-dropdown').classList.toggle('show');
        }
        function showToast(msg) {
            var x = document.getElementById("toast");
            x.innerText = msg;
            x.className = "show";
            setTimeout(function(){ x.className = x.className.replace("show", ""); }, 3000);
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
    print("Restored Theme running at http://localhost:8080/dashboard.html")
    httpd.serve_forever()
