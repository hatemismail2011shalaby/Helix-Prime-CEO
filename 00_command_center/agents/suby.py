"""
SUBY - The Creator
Web app and platform generator with clean code principles.
Generates HTML/CSS/JS, creates interactive platforms, saves code to workspace.
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import os
from pathlib import Path
from datetime import datetime
from model_backend import get_model_backend
from memory_manager import get_memory_manager
from rag.retriever import get_retriever

class SUBYAgent:
    """SUBY: The Creator - Web app and platform generator"""
    
    def __init__(self):
        self.backend = get_model_backend()
        self.retriever = get_retriever()
        self.project_root = Path(__file__).resolve().parents[2]
        self.workspace_dir = self.project_root / "generated_apps"
        self.templates_dir = self.workspace_dir / "templates"
        self.projects_dir = self.workspace_dir / "projects"
        self.memory_dir = self.project_root / "06_memory"
        self.projects_log_file = self.memory_dir / "suby_projects.json"
        
        # Create directories
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Load projects log
        self.projects_log = self._load_projects_log()
    
    def _load_projects_log(self) -> list:
        """Load projects log or create new"""
        try:
            if self.projects_log_file.exists():
                with open(self.projects_log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️  Could not load projects log: {e}")
        return []
    
    def _save_projects_log(self) -> None:
        """Save projects log to disk"""
        try:
            with open(self.projects_log_file, 'w', encoding='utf-8') as f:
                json.dump(self.projects_log, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Failed to save projects log: {e}")
    
    def _save_file(self, filepath: Path, content: str) -> bool:
        """Save content to file safely"""
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"❌ Failed to save file: {e}")
            return False
    
    def execute_command(self, command: str, args: dict) -> str:
        """Main command dispatcher for SUBY"""
        
        if command == "create":
            app_type = args.get("type", "webapp")
            name = args.get("name", "New App")
            description = args.get("description", "")
            return self.create_webapp(name, description, app_type)
        
        elif command == "template":
            template_type = args.get("template_type", "crud")
            return self.generate_template(template_type)
        
        elif command == "preview":
            filename = args.get("filename", "")
            return self.preview_file(filename)
        
        elif command == "list":
            return self.list_projects()
        
        elif command == "generate":
            spec = args.get("spec", "")
            # Delegate to the data-generation path when the spec starts with
            # the DATAGEN: prefix — avoids polluting the web-app generator.
            if spec.startswith("DATAGEN:"):
                return self._generate_synthetic_data(spec.removeprefix("DATAGEN:"))
            return self.generate_from_spec(spec)
        
        elif command == "generate_data":
            spec = args.get("spec", "")
            return self._generate_synthetic_data(spec)
        
        elif command == "component":
            comp_type = args.get("component_type", "button")
            props = args.get("props", {})
            return self.generate_component(comp_type, props)
        
        else:
            return f"❌ Unknown SUBY command: {command}. Try 'create', 'template', 'preview', 'list', 'generate', or 'component'."
    
    def create_webapp(self, name: str, description: str, app_type: str = "webapp") -> str:
        """Generate a complete web app from scratch"""
        
        print(f"\n🎨 SUBY: Creating web app '{name}'...")
        
        # Sanitize app name for filesystem
        app_slug = name.lower().replace(' ', '_').replace('-', '_')
        project_dir = self.projects_dir / app_slug
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate app structure based on type
        if app_type == "crud":
            return self._create_crud_app(name, description, app_slug, project_dir)
        elif app_type == "dashboard":
            return self._create_dashboard_app(name, description, app_slug, project_dir)
        elif app_type == "landing":
            return self._create_landing_page(name, description, app_slug, project_dir)
        elif app_type == "form":
            return self._create_form_app(name, description, app_slug, project_dir)
        else:
            return self._create_generic_app(name, description, app_slug, project_dir)
    
    def _create_crud_app(self, name: str, description: str, slug: str, project_dir: Path) -> str:
        """Generate a CRUD (Create, Read, Update, Delete) application"""
        
        # Generate HTML
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="app-container">
        <header class="app-header">
            <h1>📱 {name}</h1>
            <p class="description">{description}</p>
        </header>
        
        <main class="app-main">
            <!-- Input Section -->
            <section class="section input-section">
                <h2>Create New Entry</h2>
                <form id="entryForm" class="form">
                    <div class="form-group">
                        <label for="itemName">Name:</label>
                        <input type="text" id="itemName" name="name" required placeholder="Enter item name...">
                    </div>
                    <div class="form-group">
                        <label for="itemDesc">Description:</label>
                        <textarea id="itemDesc" name="description" placeholder="Enter description..."></textarea>
                    </div>
                    <div class="form-group">
                        <label for="itemStatus">Status:</label>
                        <select id="itemStatus" name="status">
                            <option value="active">Active</option>
                            <option value="inactive">Inactive</option>
                            <option value="pending">Pending</option>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-primary">Create Entry</button>
                </form>
            </section>
            
            <!-- Display Section -->
            <section class="section display-section">
                <h2>Entries</h2>
                <div class="search-bar">
                    <input type="text" id="searchInput" placeholder="Search entries...">
                </div>
                <div id="entriesList" class="entries-list">
                    <p class="empty-state">No entries yet. Create one to get started!</p>
                </div>
            </section>
        </main>
        
        <footer class="app-footer">
            <p>Generated by SUBY • {datetime.now().strftime('%Y-%m-%d')}</p>
        </footer>
    </div>
    
    <script src="script.js"></script>
</body>
</html>"""
        
        # Generate CSS
        css_content = """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px;
}

.app-container {
    max-width: 1200px;
    margin: 0 auto;
    background: white;
    border-radius: 16px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    overflow: hidden;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}

.app-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 40px;
    text-align: center;
}

.app-header h1 {
    font-size: 2.5em;
    margin-bottom: 10px;
}

.description {
    font-size: 1.1em;
    opacity: 0.9;
}

.app-main {
    flex: 1;
    padding: 40px;
}

.section {
    margin-bottom: 40px;
}

.section h2 {
    font-size: 1.8em;
    color: #333;
    margin-bottom: 20px;
    border-bottom: 2px solid #667eea;
    padding-bottom: 10px;
}

.form {
    background: #f8f9fa;
    padding: 25px;
    border-radius: 12px;
    border: 1px solid #e0e0e0;
}

.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    font-weight: 600;
    color: #333;
    margin-bottom: 8px;
    font-size: 0.95em;
}

.form-group input,
.form-group textarea,
.form-group select {
    width: 100%;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 1em;
    font-family: inherit;
    transition: border-color 0.3s;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group textarea {
    resize: vertical;
    min-height: 100px;
}

.btn {
    padding: 12px 24px;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
    font-size: 1em;
}

.btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
}

.btn-danger {
    background: #ff6b6b;
    color: white;
}

.btn-danger:hover {
    background: #ee5a52;
}

.btn-warning {
    background: #ffa94d;
    color: white;
}

.btn-warning:hover {
    background: #ff922b;
}

.search-bar {
    margin-bottom: 20px;
}

.search-bar input {
    width: 100%;
    padding: 12px 16px;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    font-size: 1em;
    transition: border-color 0.3s;
}

.search-bar input:focus {
    outline: none;
    border-color: #667eea;
}

.entries-list {
    display: grid;
    gap: 20px;
}

.entry-card {
    background: #f8f9fa;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 20px;
    transition: all 0.3s;
}

.entry-card:hover {
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
}

.entry-card h3 {
    color: #333;
    margin-bottom: 8px;
    font-size: 1.3em;
}

.entry-card p {
    color: #666;
    margin-bottom: 12px;
    line-height: 1.5;
}

.entry-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 15px;
    padding-top: 15px;
    border-top: 1px solid #e0e0e0;
}

.status-badge {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.85em;
    font-weight: 600;
}

.status-active {
    background: #c3fae8;
    color: #0b7285;
}

.status-inactive {
    background: #ffe0e6;
    color: #862e2e;
}

.status-pending {
    background: #fff3bf;
    color: #7c5c00;
}

.entry-actions {
    display: flex;
    gap: 8px;
}

.entry-actions button {
    padding: 8px 12px;
    font-size: 0.85em;
}

.empty-state {
    text-align: center;
    color: #999;
    padding: 40px;
    font-size: 1.1em;
}

.app-footer {
    background: #f8f9fa;
    padding: 20px;
    text-align: center;
    color: #666;
    border-top: 1px solid #e0e0e0;
}

@media (max-width: 768px) {
    .app-header {
        padding: 20px;
    }
    
    .app-header h1 {
        font-size: 1.8em;
    }
    
    .app-main {
        padding: 20px;
    }
    
    .entries-list {
        grid-template-columns: 1fr;
    }
}
"""
        
        # Generate JavaScript
        js_content = """// CRUD App - Data Management
let entries = JSON.parse(localStorage.getItem('entries')) || [];

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    renderEntries();
});

function setupEventListeners() {
    document.getElementById('entryForm').addEventListener('submit', handleAddEntry);
    document.getElementById('searchInput').addEventListener('input', handleSearch);
}

function handleAddEntry(e) {
    e.preventDefault();
    
    const formData = new FormData(document.getElementById('entryForm'));
    const newEntry = {
        id: Date.now(),
        name: formData.get('name'),
        description: formData.get('description'),
        status: formData.get('status'),
        createdAt: new Date().toLocaleString()
    };
    
    entries.push(newEntry);
    saveEntries();
    document.getElementById('entryForm').reset();
    renderEntries();
    
    showNotification('✓ Entry created successfully!');
}

function handleDelete(id) {
    if (confirm('Are you sure you want to delete this entry?')) {
        entries = entries.filter(e => e.id !== id);
        saveEntries();
        renderEntries();
        showNotification('✓ Entry deleted.');
    }
}

function handleEdit(id) {
    const entry = entries.find(e => e.id === id);
    if (entry) {
        document.getElementById('itemName').value = entry.name;
        document.getElementById('itemDesc').value = entry.description;
        document.getElementById('itemStatus').value = entry.status;
        
        entries = entries.filter(e => e.id !== id);
        saveEntries();
        renderEntries();
    }
}

function handleSearch(e) {
    const query = e.target.value.toLowerCase();
    const filtered = entries.filter(entry =>
        entry.name.toLowerCase().includes(query) ||
        entry.description.toLowerCase().includes(query)
    );
    renderEntries(filtered);
}

function renderEntries(entriesToRender = entries) {
    const list = document.getElementById('entriesList');
    
    if (entriesToRender.length === 0) {
        list.innerHTML = '<p class="empty-state">No entries found.</p>';
        return;
    }
    
    list.innerHTML = entriesToRender.map(entry => `
        <div class="entry-card">
            <h3>${escapeHtml(entry.name)}</h3>
            <p>${escapeHtml(entry.description)}</p>
            <div class="entry-meta">
                <span class="status-badge status-${entry.status}">${entry.status.toUpperCase()}</span>
                <small>${entry.createdAt}</small>
            </div>
            <div class="entry-actions">
                <button class="btn btn-warning" onclick="handleEdit(${entry.id})">Edit</button>
                <button class="btn btn-danger" onclick="handleDelete(${entry.id})">Delete</button>
            </div>
        </div>
    `).join('');
}

function saveEntries() {
    localStorage.setItem('entries', JSON.stringify(entries));
}

function showNotification(message) {
    const div = document.createElement('div');
    div.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #51cf66;
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    div.textContent = message;
    document.body.appendChild(div);
    
    setTimeout(() => div.remove(), 3000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
"""
        
        # Save files
        html_path = project_dir / "index.html"
        css_path = project_dir / "styles.css"
        js_path = project_dir / "script.js"
        
        success = True
        success &= self._save_file(html_path, html_content)
        success &= self._save_file(css_path, css_content)
        success &= self._save_file(js_path, js_content)
        
        if success:
            # Log project
            self.projects_log.append({
                "name": name,
                "slug": slug,
                "type": "crud",
                "description": description,
                "created": datetime.now().isoformat(),
                "path": str(project_dir)
            })
            self._save_projects_log()
            
            return f"""✅ CRUD App Created: {name}
━━━━━━━━━━━━━━━━━━━━━━━━
📁 Location: {project_dir}
📄 Files:
   • index.html (structure)
   • styles.css (design)
   • script.js (logic)

🚀 Features:
   ✓ Add/Edit/Delete entries
   ✓ Search functionality
   ✓ Local storage persistence
   ✓ Responsive design
   ✓ Clean UI with gradients
   ✓ Status management

🔗 Open: {html_path.absolute().as_uri()}"""
        else:
            return f"❌ Failed to create CRUD app"
    
    def _create_dashboard_app(self, name: str, description: str, slug: str, project_dir: Path) -> str:
        """Generate a dashboard application"""
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} Dashboard</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="dashboard-container">
        <aside class="sidebar">
            <div class="logo">
                <h2>📊 DASH</h2>
            </div>
            <nav class="nav-menu">
                <a href="#" class="nav-item active" data-section="overview">Overview</a>
                <a href="#" class="nav-item" data-section="analytics">Analytics</a>
                <a href="#" class="nav-item" data-section="reports">Reports</a>
                <a href="#" class="nav-item" data-section="settings">Settings</a>
            </nav>
        </aside>
        
        <main class="dashboard-main">
            <header class="dashboard-header">
                <h1>{name}</h1>
                <div class="header-actions">
                    <input type="date" id="dateFilter">
                    <button class="btn btn-primary">Export</button>
                </div>
            </header>
            
            <div class="dashboard-content">
                <section id="overview" class="section active">
                    <h2>Overview</h2>
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <h3>1,234</h3>
                            <p>Total Users</p>
                        </div>
                        <div class="metric-card">
                            <h3>56.2%</h3>
                            <p>Growth Rate</p>
                        </div>
                        <div class="metric-card">
                            <h3>$45.2K</h3>
                            <p>Revenue</p>
                        </div>
                        <div class="metric-card">
                            <h3>92%</h3>
                            <p>Satisfaction</p>
                        </div>
                    </div>
                </section>
                
                <section id="analytics" class="section">
                    <h2>Analytics</h2>
                    <div class="chart-container">
                        <canvas id="analyticsChart"></canvas>
                    </div>
                </section>
                
                <section id="reports" class="section">
                    <h2>Reports</h2>
                    <p>Report generation section</p>
                </section>
                
                <section id="settings" class="section">
                    <h2>Settings</h2>
                    <p>Application settings</p>
                </section>
            </div>
        </main>
    </div>
    
    <script src="script.js"></script>
</body>
</html>"""
        
        css_content = """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: #f5f5f5;
    height: 100vh;
    overflow: hidden;
}

.dashboard-container {
    display: flex;
    height: 100vh;
}

.sidebar {
    width: 250px;
    background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
    color: white;
    padding: 20px;
    overflow-y: auto;
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
}

.logo {
    margin-bottom: 30px;
    padding-bottom: 20px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.logo h2 {
    font-size: 1.5em;
}

.nav-menu {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.nav-item {
    display: block;
    padding: 12px 16px;
    color: white;
    text-decoration: none;
    border-radius: 8px;
    transition: all 0.3s;
    cursor: pointer;
}

.nav-item:hover {
    background: rgba(255, 255, 255, 0.1);
}

.nav-item.active {
    background: #3498db;
}

.dashboard-main {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
}

.dashboard-header {
    background: white;
    padding: 20px 30px;
    border-bottom: 1px solid #e0e0e0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.dashboard-header h1 {
    font-size: 1.8em;
    color: #333;
}

.header-actions {
    display: flex;
    gap: 15px;
}

.header-actions input {
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 6px;
}

.btn {
    padding: 8px 16px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s;
}

.btn-primary {
    background: #3498db;
    color: white;
}

.btn-primary:hover {
    background: #2980b9;
}

.dashboard-content {
    flex: 1;
    padding: 30px;
    overflow-y: auto;
}

.section {
    display: none;
}

.section.active {
    display: block;
}

.section h2 {
    font-size: 1.5em;
    color: #333;
    margin-bottom: 20px;
}

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.metric-card {
    background: white;
    padding: 25px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    border-left: 4px solid #3498db;
}

.metric-card h3 {
    font-size: 2em;
    color: #3498db;
    margin-bottom: 8px;
}

.metric-card p {
    color: #666;
    font-size: 0.95em;
}

.chart-container {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

@media (max-width: 768px) {
    .sidebar {
        display: none;
    }
    
    .dashboard-header {
        flex-direction: column;
        gap: 15px;
    }
}
"""
        
        js_content = """document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        
        // Remove active from all
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
        
        // Add active to clicked
        item.classList.add('active');
        const sectionId = item.dataset.section;
        document.getElementById(sectionId).classList.add('active');
    });
});
"""
        
        # Save files
        html_path = project_dir / "index.html"
        css_path = project_dir / "styles.css"
        js_path = project_dir / "script.js"
        
        success = True
        success &= self._save_file(html_path, html_content)
        success &= self._save_file(css_path, css_content)
        success &= self._save_file(js_path, js_content)
        
        if success:
            self.projects_log.append({
                "name": name,
                "slug": slug,
                "type": "dashboard",
                "description": description,
                "created": datetime.now().isoformat(),
                "path": str(project_dir)
            })
            self._save_projects_log()
            
            return f"""✅ Dashboard Created: {name}
━━━━━━━━━━━━━━━━━━━━━━━━
📁 Location: {project_dir}
📄 Files: index.html, styles.css, script.js

🎯 Features:
   ✓ Sidebar navigation
   ✓ Metrics cards
   ✓ Analytics section
   ✓ Responsive layout
   ✓ Modern design

🔗 Open: {html_path.absolute().as_uri()}"""
        
        return "❌ Failed to create dashboard"
    
    def _create_landing_page(self, name: str, description: str, slug: str, project_dir: Path) -> str:
        """Generate a landing page"""
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <nav class="navbar">
        <div class="navbar-brand">{name}</div>
        <div class="navbar-links">
            <a href="#features">Features</a>
            <a href="#pricing">Pricing</a>
            <a href="#contact">Contact</a>
        </div>
    </nav>
    
    <section class="hero">
        <h1>{name}</h1>
        <p>{description}</p>
        <button class="btn btn-cta">Get Started</button>
    </section>
    
    <section id="features" class="features">
        <h2>Features</h2>
        <div class="features-grid">
            <div class="feature">
                <h3>⚡ Fast</h3>
                <p>Lightning quick performance</p>
            </div>
            <div class="feature">
                <h3>🎨 Beautiful</h3>
                <p>Stunning modern design</p>
            </div>
            <div class="feature">
                <h3>🔒 Secure</h3>
                <p>Enterprise-grade security</p>
            </div>
        </div>
    </section>
    
    <section id="pricing" class="pricing">
        <h2>Pricing</h2>
        <div class="pricing-grid">
            <div class="price-card">
                <h3>Starter</h3>
                <p class="price">$9/mo</p>
                <ul>
                    <li>✓ Feature 1</li>
                    <li>✓ Feature 2</li>
                </ul>
            </div>
            <div class="price-card featured">
                <h3>Professional</h3>
                <p class="price">$29/mo</p>
                <ul>
                    <li>✓ All Starter features</li>
                    <li>✓ Advanced features</li>
                </ul>
            </div>
        </div>
    </section>
    
    <section id="contact" class="contact">
        <h2>Get in Touch</h2>
        <form class="contact-form">
            <input type="email" placeholder="Your email" required>
            <textarea placeholder="Your message" required></textarea>
            <button type="submit" class="btn btn-primary">Send</button>
        </form>
    </section>
    
    <footer class="footer">
        <p>&copy; 2024 {name}. All rights reserved.</p>
    </footer>
    
    <script src="script.js"></script>
</body>
</html>"""
        
        css_content = """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
}

.navbar {
    background: white;
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    position: sticky;
    top: 0;
    z-index: 100;
}

.navbar-brand {
    font-weight: bold;
    font-size: 1.5em;
}

.navbar-links {
    display: flex;
    gap: 2rem;
}

.navbar-links a {
    text-decoration: none;
    color: #333;
    transition: color 0.3s;
}

.navbar-links a:hover {
    color: #3498db;
}

.hero {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 6rem 2rem;
    text-align: center;
}

.hero h1 {
    font-size: 3em;
    margin-bottom: 1rem;
}

.hero p {
    font-size: 1.3em;
    margin-bottom: 2rem;
    opacity: 0.9;
}

.btn {
    padding: 12px 30px;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
    font-size: 1em;
}

.btn-cta {
    background: white;
    color: #667eea;
}

.btn-cta:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.btn-primary {
    background: #3498db;
    color: white;
}

.btn-primary:hover {
    background: #2980b9;
}

section {
    padding: 4rem 2rem;
    max-width: 1200px;
    margin: 0 auto;
}

section h2 {
    font-size: 2.5em;
    margin-bottom: 3rem;
    text-align: center;
}

.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}

.feature {
    background: #f8f9fa;
    padding: 2rem;
    border-radius: 12px;
    text-align: center;
}

.feature h3 {
    font-size: 1.8em;
    margin-bottom: 1rem;
}

.pricing-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}

.price-card {
    background: white;
    border: 2px solid #e0e0e0;
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
    transition: all 0.3s;
}

.price-card:hover {
    transform: translateY(-10px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.price-card.featured {
    border-color: #3498db;
    box-shadow: 0 10px 30px rgba(52, 152, 219, 0.3);
}

.price {
    font-size: 2em;
    color: #3498db;
    margin: 1rem 0;
}

.price-card ul {
    list-style: none;
    margin: 1.5rem 0;
}

.price-card li {
    padding: 0.5rem;
}

.contact-form {
    max-width: 600px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.contact-form input,
.contact-form textarea {
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-family: inherit;
    font-size: 1em;
}

.contact-form textarea {
    min-height: 150px;
    resize: vertical;
}

.footer {
    background: #333;
    color: white;
    text-align: center;
    padding: 2rem;
}

@media (max-width: 768px) {
    .hero h1 {
        font-size: 2em;
    }
    
    .navbar-links {
        gap: 1rem;
    }
}
"""
        
        js_content = """document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const target = document.querySelector(link.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

document.querySelector('.contact-form').addEventListener('submit', (e) => {
    e.preventDefault();
    alert('Thank you for your message!');
});
"""
        
        # Save files
        html_path = project_dir / "index.html"
        css_path = project_dir / "styles.css"
        js_path = project_dir / "script.js"
        
        success = True
        success &= self._save_file(html_path, html_content)
        success &= self._save_file(css_path, css_content)
        success &= self._save_file(js_path, js_content)
        
        if success:
            self.projects_log.append({
                "name": name,
                "slug": slug,
                "type": "landing",
                "description": description,
                "created": datetime.now().isoformat(),
                "path": str(project_dir)
            })
            self._save_projects_log()
            
            return f"""✅ Landing Page Created: {name}
━━━━━━━━━━━━━━━━━━━━━━━━
📁 Location: {project_dir}

🎯 Features:
   ✓ Hero section
   ✓ Features showcase
   ✓ Pricing table
   ✓ Contact form
   ✓ Smooth scrolling
   ✓ Responsive design

🔗 Open: {html_path.absolute().as_uri()}"""
        
        return "❌ Failed to create landing page"
    
    def _create_form_app(self, name: str, description: str, slug: str, project_dir: Path) -> str:
        """Generate a form application"""
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="form-container">
        <div class="form-header">
            <h1>{name}</h1>
            <p>{description}</p>
        </div>
        
        <form id="mainForm" class="form">
            <div class="form-group">
                <label for="firstName">First Name *</label>
                <input type="text" id="firstName" name="firstName" required>
            </div>
            
            <div class="form-group">
                <label for="lastName">Last Name *</label>
                <input type="text" id="lastName" name="lastName" required>
            </div>
            
            <div class="form-group">
                <label for="email">Email *</label>
                <input type="email" id="email" name="email" required>
            </div>
            
            <div class="form-group">
                <label for="phone">Phone</label>
                <input type="tel" id="phone" name="phone">
            </div>
            
            <div class="form-group">
                <label for="message">Message *</label>
                <textarea id="message" name="message" required></textarea>
            </div>
            
            <div class="form-group">
                <label>
                    <input type="checkbox" name="agree" required>
                    I agree to the terms
                </label>
            </div>
            
            <button type="submit" class="btn btn-primary">Submit</button>
        </form>
        
        <div id="formStatus"></div>
    </div>
    
    <script src="script.js"></script>
</body>
</html>"""
        
        css_content = """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
}

.form-container {
    background: white;
    border-radius: 12px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    max-width: 500px;
    width: 100%;
    padding: 40px;
}

.form-header {
    margin-bottom: 30px;
    text-align: center;
}

.form-header h1 {
    color: #333;
    margin-bottom: 10px;
}

.form-header p {
    color: #666;
    font-size: 0.95em;
}

.form {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.form-group {
    display: flex;
    flex-direction: column;
}

.form-group label {
    font-weight: 600;
    color: #333;
    margin-bottom: 8px;
    font-size: 0.95em;
}

.form-group input,
.form-group textarea {
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-family: inherit;
    font-size: 1em;
    transition: border-color 0.3s;
}

.form-group input:focus,
.form-group textarea:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group input[type="checkbox"] {
    width: auto;
    margin-right: 8px;
}

.form-group textarea {
    resize: vertical;
    min-height: 120px;
}

.btn {
    padding: 12px 24px;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
    font-size: 1em;
}

.btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    margin-top: 10px;
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
}

.btn-primary:active {
    transform: translateY(0);
}

#formStatus {
    margin-top: 20px;
    padding: 15px;
    border-radius: 8px;
    text-align: center;
    display: none;
}

#formStatus.success {
    display: block;
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

#formStatus.error {
    display: block;
    background: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}

@media (max-width: 600px) {
    .form-container {
        padding: 25px;
    }
}
"""
        
        js_content = """document.getElementById('mainForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    // Validate form
    if (!validateForm(data)) {
        showStatus('Please fill all required fields correctly', 'error');
        return;
    }
    
    // Simulate form submission
    const button = form.querySelector('button[type="submit"]');
    const originalText = button.textContent;
    button.disabled = true;
    button.textContent = 'Sending...';
    
    try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Save to localStorage as demo
        const submissions = JSON.parse(localStorage.getItem('formSubmissions')) || [];
        submissions.push({
            ...data,
            timestamp: new Date().toLocaleString()
        });
        localStorage.setItem('formSubmissions', JSON.stringify(submissions));
        
        form.reset();
        showStatus('✓ Form submitted successfully!', 'success');
    } catch (error) {
        showStatus('❌ Error submitting form. Please try again.', 'error');
    } finally {
        button.disabled = false;
        button.textContent = originalText;
    }
});

function validateForm(data) {
    if (!data.firstName?.trim()) return false;
    if (!data.lastName?.trim()) return false;
    if (!data.email?.trim() || !isValidEmail(data.email)) return false;
    if (!data.message?.trim()) return false;
    return true;
}

function isValidEmail(email) {
    return /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(email);
}

function showStatus(message, type) {
    const statusDiv = document.getElementById('formStatus');
    statusDiv.textContent = message;
    statusDiv.className = type;
    
    if (type === 'success') {
        setTimeout(() => {
            statusDiv.classList.remove('success');
        }, 4000);
    }
}
"""
        
        # Save files
        html_path = project_dir / "index.html"
        css_path = project_dir / "styles.css"
        js_path = project_dir / "script.js"
        
        success = True
        success &= self._save_file(html_path, html_content)
        success &= self._save_file(css_path, css_content)
        success &= self._save_file(js_path, js_content)
        
        if success:
            self.projects_log.append({
                "name": name,
                "slug": slug,
                "type": "form",
                "description": description,
                "created": datetime.now().isoformat(),
                "path": str(project_dir)
            })
            self._save_projects_log()
            
            return f"""✅ Form App Created: {name}
━━━━━━━━━━━━━━━━━━━━━━━━
📁 Location: {project_dir}

🎯 Features:
   ✓ Multi-field form
   ✓ Input validation
   ✓ Error handling
   ✓ Success feedback
   ✓ LocalStorage persistence
   ✓ Beautiful design

🔗 Open: {html_path.absolute().as_uri()}"""
        
        return "❌ Failed to create form app"
    
    def _create_generic_app(self, name: str, description: str, slug: str, project_dir: Path) -> str:
        """Generate a generic web app"""
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="app-wrapper">
        <header class="app-header">
            <h1>🚀 {name}</h1>
            <p>{description}</p>
        </header>
        
        <main class="app-content">
            <p>Welcome to {name}!</p>
        </main>
        
        <footer class="app-footer">
            <p>Generated by SUBY</p>
        </footer>
    </div>
    
    <script src="script.js"></script>
</body>
</html>"""
        
        css_content = """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}

.app-wrapper {
    max-width: 1200px;
    margin: 0 auto;
    background: white;
    border-radius: 12px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    overflow: hidden;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}

.app-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 40px;
    text-align: center;
}

.app-header h1 {
    font-size: 2.5em;
    margin-bottom: 10px;
}

.app-header p {
    font-size: 1.1em;
    opacity: 0.9;
}

.app-content {
    flex: 1;
    padding: 40px;
}

.app-footer {
    background: #f8f9fa;
    padding: 20px;
    text-align: center;
    color: #666;
    border-top: 1px solid #e0e0e0;
}
"""
        
        js_content = """console.log('App loaded successfully!');
"""
        
        # Save files
        html_path = project_dir / "index.html"
        css_path = project_dir / "styles.css"
        js_path = project_dir / "script.js"
        
        success = True
        success &= self._save_file(html_path, html_content)
        success &= self._save_file(css_path, css_content)
        success &= self._save_file(js_path, js_content)
        
        if success:
            self.projects_log.append({
                "name": name,
                "slug": slug,
                "type": "generic",
                "description": description,
                "created": datetime.now().isoformat(),
                "path": str(project_dir)
            })
            self._save_projects_log()
            
            return f"""✅ Web App Created: {name}
━━━━━━━━━━━━━━━━━━━━━━━━
📁 Location: {project_dir}
📄 Files: index.html, styles.css, script.js

🔗 Open: {html_path.absolute().as_uri()}"""
        
        return "❌ Failed to create web app"
    
    def generate_template(self, template_type: str) -> str:
        """Generate a template for common patterns"""
        
        templates = {
            "crud": "CRUD (Create, Read, Update, Delete) application",
            "dashboard": "Analytics dashboard with metrics",
            "landing": "Landing page with hero section",
            "form": "Contact/registration form",
            "navbar": "Navigation bar component",
            "card": "Reusable card component",
            "modal": "Modal dialog component",
            "table": "Data table with sorting"
        }
        
        if template_type not in templates:
            return f"❌ Unknown template: {template_type}\nAvailable: {', '.join(templates.keys())}"
        
        # Generate template code
        template_content = self._get_template_code(template_type)
        
        # Save template
        template_file = self.templates_dir / f"{template_type}_template.html"
        self._save_file(template_file, template_content)
        
        return f"""✓ Template Generated: {template_type}
━━━━━━━━━━━━━━━━━━━━━━━━
📄 File: {template_file}

📝 Description: {templates.get(template_type, '')}

You can copy this template to start your project."""
    
    def _get_template_code(self, template_type: str) -> str:
        """Get template HTML code"""
        
        templates = {
            "navbar": """<!-- Navbar Template -->
<nav class="navbar">
    <div class="navbar-brand">Brand</div>
    <ul class="navbar-nav">
        <li><a href="#home">Home</a></li>
        <li><a href="#about">About</a></li>
        <li><a href="#contact">Contact</a></li>
    </ul>
</nav>

<style>
    .navbar {
        background: #333;
        color: white;
        padding: 1rem 2rem;
        display: flex;
        justify-content: space-between;
    }
    .navbar-nav {
        list-style: none;
        display: flex;
        gap: 2rem;
    }
    .navbar-nav a {
        color: white;
        text-decoration: none;
    }
</style>""",
            
            "card": """<!-- Card Component Template -->
<div class="card">
    <img src="image.jpg" alt="Card image">
    <div class="card-body">
        <h3>Card Title</h3>
        <p>Card description goes here</p>
        <button class="btn">Action</button>
    </div>
</div>

<style>
    .card {
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        overflow: hidden;
        max-width: 300px;
    }
    .card img {
        width: 100%;
        height: 200px;
        object-fit: cover;
    }
    .card-body {
        padding: 20px;
    }
</style>""",
            
            "modal": """<!-- Modal Template -->
<div id="modal" class="modal">
    <div class="modal-content">
        <span class="close">&times;</span>
        <h2>Modal Title</h2>
        <p>Modal content goes here</p>
        <button class="btn">Action</button>
    </div>
</div>

<style>
    .modal {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        z-index: 1000;
    }
    .modal-content {
        background: white;
        margin: 10% auto;
        padding: 20px;
        border-radius: 8px;
        max-width: 500px;
    }
    .close {
        cursor: pointer;
        float: right;
    }
</style>

<script>
    const modal = document.getElementById('modal');
    document.querySelector('.close').onclick = () => modal.style.display = 'none';
</script>""",
            
            "table": """<!-- Data Table Template -->
<table class="data-table">
    <thead>
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Status</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>1</td>
            <td>John Doe</td>
            <td>john@example.com</td>
            <td><span class="badge active">Active</span></td>
        </tr>
    </tbody>
</table>

<style>
    .data-table {
        width: 100%;
        border-collapse: collapse;
    }
    .data-table th {
        background: #333;
        color: white;
        padding: 12px;
        text-align: left;
    }
    .data-table td {
        padding: 12px;
        border-bottom: 1px solid #ddd;
    }
    .badge {
        padding: 4px 8px;
        border-radius: 4px;
    }
    .badge.active {
        background: #51cf66;
        color: white;
    }
</style>"""
        }
        
        return templates.get(template_type, "<!-- Template not found -->")
    
    def preview_file(self, filename: str) -> str:
        """Generate preview of saved file"""
        
        if not filename:
            return "❌ Please specify a filename to preview"
        
        # Search for file
        file_path = None
        for project_dir in self.projects_dir.rglob("*"):
            if project_dir.name == filename or project_dir.name.startswith(filename):
                if project_dir.is_file():
                    file_path = project_dir
                    break
        
        if not file_path:
            return f"❌ File not found: {filename}"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Show first 500 chars
            preview = content[:500] + "..." if len(content) > 500 else content
            
            return f"""📄 File Preview: {file_path.name}
━━━━━━━━━━━━━━━━━━━━━━━━
{preview}

📍 Location: {file_path}"""
        
        except Exception as e:
            return f"❌ Could not read file: {e}"
    
    def list_projects(self) -> str:
        """List all created projects"""
        
        if not self.projects_log:
            return "📁 No projects created yet"
        
        output = "📚 Your Projects:\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for i, project in enumerate(self.projects_log, 1):
            output += f"""{i}. {project['name']} ({project['type']})
   📝 {project['description']}
   📁 {project['path']}
   📅 {project['created']}
"""
        
        return output
    
    def _generate_synthetic_data(self, spec: str) -> str:
        """Generate synthetic BPO / call-centre data from a structured spec.

        This method is the Stage-2 entry point for the TP Onboarding
        Simulation.  It builds a domain-specific prompt (not the general
        HTML/CSS/JS prompt that ``generate_from_spec`` uses) and returns
        structured text the caller can parse into CSV / JSON files.

        The spec should describe what kind of data to generate (call
        volumes, SLA contracts, etc.) and include formatting instructions.
        """
        if not spec:
            return "❌ Please provide a data-generation specification"

        try:
            context = self.retriever.retrieve(spec, top_k=3)
        except Exception:
            context = []

        context_block = ""
        if context:
            context_block = "Relevant context:\n" + "\n".join(context) + "\n\n"

        prompt = (
            f"{context_block}"
            f"Generate synthetic BPO/call-centre operational data according "
            f"to the specification below.\n\n"
            f"**IMPORTANT**: Output the raw data only — no HTML, no CSS, no "
            f"JavaScript wrapper.  Use clear section markers so a parser can "
            f"extract each piece.\n\n"
            f"---SPECIFICATION---\n{spec}\n"
        )

        raw = self.backend.chat(prompt)

        try:
            self.retriever.index_text(
                source_id=f"suby_data_{datetime.now().isoformat()}",
                text=f"Data spec: {spec}\nGenerated: {raw}",
            )
        except Exception:
            pass

        return raw.strip()

    def generate_from_spec(self, spec: str) -> str:
        """Generate code from specification"""
        
        if not spec:
            return "❌ Please provide a specification"
        
        # Retrieve relevant context from RAG
        try:
            context = self.retriever.retrieve(spec, top_k=3)
        except Exception:
            context = []
        
        context_block = ""
        if context:
            context_block = "Relevant past generations:\n" + "\n".join(context) + "\n\n"
        
        # Use model to understand spec and generate code
        prompt = f"""{context_block}Based on this specification, generate clean HTML/CSS/JS code:

{spec}

Requirements:
1. Follow best practices
2. Include comments
3. Make it responsive
4. Use modern CSS
5. Include error handling

Provide the complete working code."""
        
        generated_code = self.backend.chat(prompt)
        
        # Index this generation for future retrieval
        try:
            self.retriever.index_text(
                source_id=f"suby_generation_{datetime.now().isoformat()}",
                text=f"Spec: {spec}\nCode: {generated_code}",
            )
        except Exception:
            pass
        
        return f"""✓ Code Generated from Spec:
━━━━━━━━━━━━━━━━━━━━━━━━
{generated_code}

To save this, create a new webapp and paste this code."""
    
    def generate_component(self, comp_type: str, props: dict) -> str:
        """Generate a specific component"""
        
        prompt = f"""Generate a reusable {comp_type} component with these properties:
{json.dumps(props, indent=2)}

Include:
- HTML structure
- CSS styling
- JavaScript functionality
- Comments

Make it clean and production-ready."""
        
        component = self.backend.chat(prompt)
        
        return f"""✓ Component Generated: {comp_type}
━━━━━━━━━━━━━━━━━━━━━━━━
{component}"""


def run():
    """Main entry point for SUBY agent"""
    try:
        data = json.loads(sys.stdin.read())
        command = data.get("command", "create")
        args = data.get("args", {})
        
        suby = SUBYAgent()
        response = suby.execute_command(command, args)
        print(response)
        
        # Log accomplishment to memory
        try:
            memory_mgr = get_memory_manager()
            app_name = args.get("name", args.get("template_type", "web-component"))
            memory_mgr.add_accomplishment(
                "SUBY",
                f"{command}: {app_name}",
                {"command": command, "app_type": args.get("type", "generic")}
            )
        except Exception as e:
            pass  # Silent fail for memory logging
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON input: {e}")
    except Exception as e:
        print(f"❌ SUBY Error: {e}")


if __name__ == "__main__":
    run()
