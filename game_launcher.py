import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import subprocess
import json
import sys
from pathlib import Path
import threading

# Check if running on Windows
if os.name != 'nt':
    print("This application is designed to run on Windows only.")
    sys.exit(1)

# Try to import winreg with error handling
try:
    import winreg
except ImportError as e:
    print(f"Error importing winreg: {e}")
    print("This module requires Windows. Make sure you're running on Windows.")
    sys.exit(1)

class ModernStyle:
    """Modern color scheme and styling constants"""
    # Dark theme colors
    BG_PRIMARY = '#1a1a1a'      # Main background
    BG_SECONDARY = '#2d2d2d'    # Secondary background
    BG_CARD = '#3a3a3a'         # Card background
    BG_HOVER = '#4a4a4a'        # Hover state
    
    # Accent colors
    ACCENT_BLUE = '#0078d4'     # Primary accent
    ACCENT_GREEN = '#107c10'    # Success/launch
    ACCENT_ORANGE = '#ff8c00'   # Warning/favorites
    ACCENT_RED = '#d13438'      # Delete/error
    ACCENT_PURPLE = '#881798'   # Special actions
    
    # Text colors
    TEXT_PRIMARY = '#ffffff'    # Main text
    TEXT_SECONDARY = '#b3b3b3'  # Secondary text
    TEXT_DIM = '#808080'        # Dimmed text
    
    # Fonts
    FONT_TITLE = ('Segoe UI', 24, 'bold')
    FONT_HEADER = ('Segoe UI', 14, 'bold')
    FONT_BODY = ('Segoe UI', 10)
    FONT_SMALL = ('Segoe UI', 9)
    FONT_BUTTON = ('Segoe UI', 9, 'bold')

class GameLauncher:
    def __init__(self, root):
        self.root = root
    
    # Data storage
        self.games = []
        self.favorites = []
        self.deleted_games = []
        self.filtered_games = []
        self.favorites_file = "favorites.json"
        self.deleted_file = "deleted_games.json"
        self.scanning = False
    
    # Load data
        self.load_favorites()
        self.load_deleted_games()
    
    # Setup window and styles
        self.setup_window()
        self.setup_styles()
    
    # Create GUI
        self.create_widgets()
    
    # Auto-scan on startup
        self.root.after(500, self.scan_games_thread)
    
    def setup_window(self):
        """Configure main window with modern styling"""
        self.root.title("🎮 Game Launcher Pro")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)
        self.root.configure(bg=ModernStyle.BG_PRIMARY)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"1200x800+{x}+{y}")
    
    def setup_styles(self):
        """Configure ttk styles for modern appearance"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure notebook style
        style.configure('Custom.TNotebook', 
                       background=ModernStyle.BG_PRIMARY,
                       borderwidth=0)
        style.configure('Custom.TNotebook.Tab',
                       background=ModernStyle.BG_SECONDARY,
                       foreground=ModernStyle.TEXT_SECONDARY,
                       padding=[20, 10],
                       font=ModernStyle.FONT_BODY)
        style.map('Custom.TNotebook.Tab',
                 background=[('selected', ModernStyle.ACCENT_BLUE),
                           ('active', ModernStyle.BG_HOVER)],
                 foreground=[('selected', ModernStyle.TEXT_PRIMARY)])
    
    def create_widgets(self):
        """Create modern UI components"""
        # Main container with padding
        main_container = tk.Frame(self.root, bg=ModernStyle.BG_PRIMARY)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header section
        self.create_header(main_container)
        
        # Search and controls section
        self.create_controls(main_container)
        
        # Main content area with tabs
        self.create_content_area(main_container)
        
        # Status bar
        self.create_status_bar(main_container)
    
    def create_header(self, parent):
        """Create modern header with title and stats"""
        header_frame = tk.Frame(parent, bg=ModernStyle.BG_PRIMARY, height=80)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Title with gradient effect simulation
        title_frame = tk.Frame(header_frame, bg=ModernStyle.BG_PRIMARY)
        title_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        title_label = tk.Label(title_frame, text="🎮 Game Launcher Pro", 
                              font=ModernStyle.FONT_TITLE,
                              fg=ModernStyle.TEXT_PRIMARY, 
                              bg=ModernStyle.BG_PRIMARY)
        title_label.pack(anchor=tk.W, pady=(10, 0))
        
        subtitle_label = tk.Label(title_frame, text="Discover and launch your games", 
                                 font=ModernStyle.FONT_SMALL,
                                 fg=ModernStyle.TEXT_DIM, 
                                 bg=ModernStyle.BG_PRIMARY)
        subtitle_label.pack(anchor=tk.W)
        
        # Stats panel
        self.stats_frame = tk.Frame(header_frame, bg=ModernStyle.BG_SECONDARY, relief=tk.FLAT, bd=1)
        self.stats_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(20, 0))
        
        self.stats_label = tk.Label(self.stats_frame, text="📊 Loading...", 
                                   font=ModernStyle.FONT_BODY,
                                   fg=ModernStyle.TEXT_SECONDARY, 
                                   bg=ModernStyle.BG_SECONDARY)
        self.stats_label.pack(expand=True, padx=15, pady=5)
    
    def create_controls(self, parent):
        """Create search and control buttons"""
        controls_frame = tk.Frame(parent, bg=ModernStyle.BG_PRIMARY)
        controls_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Search section
        search_frame = tk.Frame(controls_frame, bg=ModernStyle.BG_PRIMARY)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        search_label = tk.Label(search_frame, text="🔍 Search Games", 
                               font=ModernStyle.FONT_HEADER,
                               fg=ModernStyle.TEXT_PRIMARY, 
                               bg=ModernStyle.BG_PRIMARY)
        search_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Search entry with modern styling
        search_container = tk.Frame(search_frame, bg=ModernStyle.BG_SECONDARY, relief=tk.FLAT, bd=1)
        search_container.pack(fill=tk.X, ipady=8)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_games)
        
        self.search_entry = tk.Entry(search_container, textvariable=self.search_var,
                                    font=ModernStyle.FONT_BODY,
                                    fg=ModernStyle.TEXT_PRIMARY,
                                    bg=ModernStyle.BG_SECONDARY,
                                    insertbackground=ModernStyle.TEXT_PRIMARY,
                                    relief=tk.FLAT, bd=0)
        self.search_entry.pack(fill=tk.X, padx=15, pady=5)
        
        # Control buttons
        buttons_frame = tk.Frame(controls_frame, bg=ModernStyle.BG_PRIMARY)
        buttons_frame.pack(fill=tk.X)
        
        self.create_modern_button(buttons_frame, "🔄 Scan Games", ModernStyle.ACCENT_BLUE, 
                                 self.refresh_games).pack(side=tk.LEFT, padx=(0, 10))
        
        self.create_modern_button(buttons_frame, "📁 Add Custom Path", ModernStyle.ACCENT_PURPLE, 
                                 self.add_custom_path).pack(side=tk.LEFT, padx=(0, 10))
        
                                 
        
        # Quick stats
        self.quick_stats = tk.Label(buttons_frame, text="Ready to scan", 
                                   font=ModernStyle.FONT_SMALL,
                                   fg=ModernStyle.TEXT_DIM, 
                                   bg=ModernStyle.BG_PRIMARY)
        self.quick_stats.pack(side=tk.RIGHT, pady=5)
    
    def create_modern_button(self, parent, text, color, command):
        """Create a modern styled button"""
        button = tk.Button(parent, text=text, font=ModernStyle.FONT_BUTTON,
                          bg=color, fg=ModernStyle.TEXT_PRIMARY,
                          relief=tk.FLAT, bd=0, padx=20, pady=8,
                          cursor='hand2', command=command)
        
        # Hover effects
        def on_enter(e):
            button.config(bg=self.lighten_color(color))
        def on_leave(e):
            button.config(bg=color)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        return button
    
    def lighten_color(self, color):
        """Lighten a hex color for hover effects"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        lighter_rgb = tuple(min(255, int(c * 1.2)) for c in rgb)
        return '#%02x%02x%02x' % lighter_rgb
    
    def create_content_area(self, parent):
        """Create tabbed content area"""
        # Notebook with custom styling
        self.notebook = ttk.Notebook(parent, style='Custom.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Tab frames
        self.all_games_frame = tk.Frame(self.notebook, bg=ModernStyle.BG_PRIMARY)
        self.favorites_frame = tk.Frame(self.notebook, bg=ModernStyle.BG_PRIMARY)
        self.deleted_frame = tk.Frame(self.notebook, bg=ModernStyle.BG_PRIMARY)
        
        # Add tabs with icons
        self.notebook.add(self.all_games_frame, text="🎮 All Games")
        self.notebook.add(self.favorites_frame, text="⭐ Favorites")
        self.notebook.add(self.deleted_frame, text="🗑️ Deleted")
        
        # Create scrollable game lists
        self.create_modern_game_list(self.all_games_frame, "all")
        self.create_modern_game_list(self.favorites_frame, "favorites")
        self.create_modern_game_list(self.deleted_frame, "deleted")
    
    def create_modern_game_list(self, parent, list_type):
        """Create modern scrollable game list"""
        # Container for the scrollable area
        container = tk.Frame(parent, bg=ModernStyle.BG_PRIMARY)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas and scrollbar
        canvas = tk.Canvas(container, bg=ModernStyle.BG_PRIMARY, 
                          highlightthickness=0, bd=0)
        
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=ModernStyle.BG_PRIMARY)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Modern scrolling with mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        
        # Pack components
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Store references
        setattr(self, f"{list_type}_canvas", canvas)
        setattr(self, f"{list_type}_scrollable", scrollable_frame)
    
    def create_status_bar(self, parent):
        """Create modern status bar"""
        status_frame = tk.Frame(parent, bg=ModernStyle.BG_SECONDARY, height=40)
        status_frame.pack(fill=tk.X)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="Ready - Click 'Scan Games' to discover your games", 
                                   font=ModernStyle.FONT_SMALL,
                                   fg=ModernStyle.TEXT_SECONDARY, 
                                   bg=ModernStyle.BG_SECONDARY)
        self.status_label.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Progress indicator (initially hidden)
        self.progress_var = tk.StringVar()
        self.progress_label = tk.Label(status_frame, textvariable=self.progress_var,
                                     font=ModernStyle.FONT_SMALL,
                                     fg=ModernStyle.ACCENT_BLUE,
                                     bg=ModernStyle.BG_SECONDARY)
        self.progress_label.pack(side=tk.RIGHT, padx=15, pady=10)
    
    def refresh_games(self):
        """Manually refresh the games list"""
        if not self.scanning:
            self.scan_games_thread()
    
    def add_custom_path(self):
        """Add custom game directory"""
        directory = filedialog.askdirectory(title="Select Game Directory")
        if directory:
            self.status_label.config(text=f"📁 Scanning custom directory: {directory}")
            # Scan the custom directory
            games = []
            try:
                self.scan_directory_deep(directory, games)
                if games:
                    # Remove duplicates and deleted games
                    deleted_paths = [g['path'] for g in self.deleted_games]
                    new_games = [g for g in games if g['path'] not in deleted_paths]
                    
                    # Add to main games list
                    existing_paths = [g['path'] for g in self.games]
                    for game in new_games:
                        if game['path'] not in existing_paths:
                            self.games.append(game)
                    
                    self.games = sorted(self.games, key=lambda x: x['name'].lower())
                    self.filtered_games = self.games.copy()
                    self.update_game_lists()
                    self.status_label.config(text=f"✅ Added {len(new_games)} games from custom directory")
                else:
                    self.status_label.config(text="No games found in selected directory")
            except Exception as e:
                self.status_label.config(text=f"❌ Error scanning directory: {e}")
    
    def restore_game(self, game):
        """Restore a game from deleted list"""
        self.deleted_games = [g for g in self.deleted_games if g['path'] != game['path']]
        self.games.append(game)
        self.games = sorted(self.games, key=lambda x: x['name'].lower())
        
        # Update filtered games if search is active
        if hasattr(self, 'filtered_games'):
            self.filtered_games = self.games.copy()
            self.filter_games()  # Re-apply current filter
        
        self.save_deleted_games()
        self.update_game_lists()
        self.status_label.config(text=f"↩️ Restored: {game['name']}")
    
    # File management methods
    def load_favorites(self):
        """Load favorites from JSON file"""
        try:
            if os.path.exists(self.favorites_file):
                with open(self.favorites_file, 'r', encoding='utf-8') as f:
                    self.favorites = json.load(f)
        except Exception as e:
            print(f"Error loading favorites: {e}")
            self.favorites = []
    
    def save_favorites(self):
        """Save favorites to JSON file"""
        try:
            with open(self.favorites_file, 'w', encoding='utf-8') as f:
                json.dump(self.favorites, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save favorites:\n{str(e)}")
    
    def load_deleted_games(self):
        """Load deleted games from JSON file"""
        try:
            if os.path.exists(self.deleted_file):
                with open(self.deleted_file, 'r', encoding='utf-8') as f:
                    self.deleted_games = json.load(f)
        except Exception as e:
            print(f"Error loading deleted games: {e}")
            self.deleted_games = []
    
    def save_deleted_games(self):
        """Save deleted games to JSON file"""
        try:
            with open(self.deleted_file, 'w', encoding='utf-8') as f:
                json.dump(self.deleted_games, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save deleted games:\n{str(e)}")
    
    def scan_games_thread(self):
        """Run game scanning in a separate thread"""
        if self.scanning:
            return
        
        self.scanning = True
        self.root.after(0, lambda: self.status_label.config(text="🔍 Scanning for games..."))
        self.root.after(0, lambda: self.progress_var.set("Initializing..."))
        
        thread = threading.Thread(target=self.scan_for_games, daemon=True)
        thread.start()
    
    def scan_for_games(self):
        """Enhanced game scanning with better progress feedback"""
        try:
            games = []
            
            game_dirs = [
                r"C:\Users\GIGABYTE\Downloads\games",
                r"D:\games",
                "C:\\Program Files (x86)\\Steam\\steamapps\\common",
                "C:\\Program Files\\Steam\\steamapps\\common",
                "C:\\Program Files\\Epic Games",
                "C:\\Program Files (x86)\\Epic Games",
                "C:\\Program Files\\Origin Games",
                "C:\\Program Files (x86)\\Origin Games",
                "C:\\Program Files\\EA Games",
                "C:\\Program Files (x86)\\EA Games",
                "C:\\Program Files\\Ubisoft",
                "C:\\Program Files (x86)\\Ubisoft",
                "C:\\Riot Games",
                "C:\\Program Files (x86)\\Battle.net",
                "C:\\Program Files\\Battle.net",
                "C:\\GOG Games",
                "C:\\Program Files\\GOG Galaxy\\Games",
                "C:\\XboxGames",
                "C:\\Program Files\\Rockstar Games",
                "C:\\Program Files (x86)\\Rockstar Games",
                os.path.expanduser("~\\Desktop"),
            ]
            
            total_dirs = len(game_dirs)
            
            for i, directory in enumerate(game_dirs):
                progress_text = f"Scanning {os.path.basename(directory)}... ({i+1}/{total_dirs})"
                self.root.after(0, lambda p=progress_text: self.progress_var.set(p))
                self.root.after(0, lambda: self.root.update_idletasks())  # Add this line
                
                try:
                    if os.path.exists(directory):
                        if any(platform in directory.lower() for platform in ['steam', 'epic', 'origin', 'ubisoft', 'riot', 'battle.net', 'gog', 'games']):
                            self.scan_directory_deep(directory, games)
                        else:
                            self.scan_directory_shallow(directory, games)
                except (PermissionError, OSError):
                    continue
            
            self.root.after(0, lambda: self.progress_var.set("Checking registry..."))
            try:
                registry_games = self.get_registry_games()
                games.extend(registry_games)
            except Exception:
                pass
            
            # Remove duplicates and deleted games
            seen = set()
            unique_games = []
            for game in games:
                key = game['name'].lower().replace(' ', '')
                if key not in seen:
                    seen.add(key)
                    unique_games.append(game)
            
            deleted_paths = [g['path'] for g in self.deleted_games]
            filtered_games = [g for g in unique_games if g['path'] not in deleted_paths]
            
            self.games = sorted(filtered_games, key=lambda x: x['name'].lower())
            self.filtered_games = self.games.copy()
            
            self.root.after(0, self.update_game_lists)
            
        except Exception as e:
            self.root.after(0, lambda: self.status_label.config(text=f"❌ Error: {e}"))
        finally:
            self.scanning = False
            self.root.after(0, lambda: self.progress_var.set(""))
    
    # Game scanning methods
    def scan_directory_deep(self, directory, games):
        """Deep scan for game directories"""
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith('.exe') and self.is_likely_game(file, root):
                        full_path = os.path.join(root, file)
                        name = self.get_game_name_from_path(root, file)
                        games.append({'name': name, 'path': full_path})
                
                # Limit depth to avoid infinite scanning
                if root.count(os.sep) - directory.count(os.sep) > 2:
                    dirs[:] = []
        except (PermissionError, OSError):
            pass
    
    def scan_directory_shallow(self, directory, games):
        """Shallow scan for general directories"""
        try:
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path) and self.is_likely_game_directory(item):
                    try:
                        for file in os.listdir(item_path):
                            if file.lower().endswith('.exe') and self.is_likely_game(file, item_path):
                                full_path = os.path.join(item_path, file)
                                name = self.get_game_name_from_path(item_path, file)
                                games.append({'name': name, 'path': full_path})
                                break
                    except (PermissionError, OSError):
                        continue
        except (PermissionError, OSError):
            pass
    
    def get_game_name_from_path(self, directory, filename):
        """Extract game name from directory path and filename"""
        dir_name = os.path.basename(directory)
        name = dir_name
        
        # Remove common suffixes
        for suffix in [' - Copy', ' (1)', ' (2)', ' (3)', ' - Shortcut']:
            if name.endswith(suffix):
                name = name[:-len(suffix)]
        
        # If directory name is generic, use filename
        if name.lower() in ['bin', 'game', 'common', 'games', 'steamapps']:
            name = os.path.splitext(filename)[0]
        
        return name
    
    def is_likely_game_directory(self, dirname):
        """Check if directory name suggests it contains a game"""
        skip_words = [
            'system', 'windows', 'program', 'files', 'data', 'temp', 'cache', 'log', 'config',
            'backup', 'bin', 'lib', 'common', 'shared', 'runtime', 'framework', 'microsoft',
            'adobe', 'google', 'mozilla', 'chrome', 'nodejs', 'python', 'git', 'docker',
            'office', 'visual', 'studio', 'code', 'notepad', 'calculator', 'paint', 'vlc',
            'skype', 'discord', 'obs', 'zoom'
        ]
        
        dirname_lower = dirname.lower().replace(' ', '').replace('-', '').replace('_', '')
        return not any(skip_word in dirname_lower for skip_word in skip_words)
    
    def is_likely_game(self, filename, path):
        """Enhanced game detection logic"""
        filename_clean = filename.lower().replace(' ', '').replace('-', '').replace('_', '')
        path_clean = path.lower().replace(' ', '').replace('-', '').replace('_', '')
        
        # Blacklist - files that are definitely not games
        blacklist = [
            'uninstall', 'install', 'setup', 'config', 'update', 'patch', 'launcher_',
            'bootstrap', 'updater', 'patcher', 'installer', 'unins000', 'repair',
            'redist', 'vcredist', 'directx', 'dotnet', 'runtime', 'framework', 'debug',
            'test', 'system32', 'msi', 'dll', 'editor', 'tool', 'utility', 'crash'
        ]
        
        if any(blocked in filename_clean for blocked in blacklist):
            return False
        
        # Popular games - high confidence
        popular_games = {
            'fortnite', 'apex', 'valorant', 'csgo', 'dota', 'minecraft', 'skyrim', 'witcher',
            'gtav', 'rdr2', 'forza', 'fifa', 'nba2k', 'doom', 'halo', 'metro', 'bioshock',
            'portal', 'halflife', 'amongus', 'hades', 'stardewvalley', 'eldenring', 'cyberpunk'
        }
        
        if any(game in filename_clean for game in popular_games) or \
           any(game in path_clean for game in popular_games):
            return True
        
        # Platform directories - medium confidence
        platform_paths = [
            'steamapps/common', 'epic games', 'origin games', 'ubisoft', 'riot games',
            'battle.net', 'gog games', 'xbox games', 'rockstar games'
        ]
        
        is_in_platform = any(platform.replace('/', '\\') in path_clean for platform in platform_paths)
        if is_in_platform and not any(blocked in filename_clean for blocked in ['setup', 'launcher', 'updater', 'uninstall']):
            return True
        
        # Custom game directories
        custom_paths = ['downloads\\games', 'd:\\games', 'c:\\games']
        if any(custom in path_clean for custom in custom_paths):
            if not any(blocked in filename_clean for blocked in ['setup', 'installer', 'config']):
                parent_dir = os.path.basename(path).lower()
                if len(parent_dir) > 2 and parent_dir not in ['bin', 'game', 'common']:
                    return True
        
        return False
    
    def get_registry_games(self):
        """Get games from Windows registry (Steam)"""
        games = []
        try:
            # Try to find Steam installation
            steam_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam")
            install_path = winreg.QueryValueEx(steam_key, "InstallPath")[0]
            winreg.CloseKey(steam_key)
            
            steamapps_path = os.path.join(install_path, "steamapps", "common")
            if os.path.exists(steamapps_path):
                for game_dir in os.listdir(steamapps_path):
                    game_path = os.path.join(steamapps_path, game_dir)
                    if os.path.isdir(game_path):
                        # Find the main executable
                        for file in os.listdir(game_path):
                            if file.lower().endswith('.exe') and self.is_likely_game(file, game_path):
                                full_path = os.path.join(game_path, file)
                                games.append({'name': game_dir, 'path': full_path})
                                break
        except Exception:
            pass
        
        return games
    
    def update_game_lists(self):
        """Update all game lists with modern cards"""
        self.populate_modern_game_list(self.all_scrollable, self.filtered_games, "all")
        self.populate_favorites_list()
        self.populate_deleted_list()
        
        # Update stats
        total_games = len(self.games)
        favorites_count = len(self.favorites)
        deleted_count = len(self.deleted_games)
        
        stats_text = f"📊 {total_games} Games | ⭐ {favorites_count} Favorites | 🗑️ {deleted_count} Deleted"
        self.stats_label.config(text=stats_text)
        self.status_label.config(text=f"✅ Found {total_games} games")
    
    def populate_modern_game_list(self, parent, games, list_type):
        # Disable updates during population
        parent.update_idletasks()
        """Populate list with modern game cards"""
        # Clear existing widgets
        for widget in parent.winfo_children():
            widget.destroy()
        
        if not games:
            self.create_empty_state(parent, list_type)
            return
        
        for game in games:
            self.create_modern_game_card(parent, game, list_type)
    
    def create_empty_state(self, parent, list_type):
        """Create modern empty state"""
        empty_frame = tk.Frame(parent, bg=ModernStyle.BG_PRIMARY)
        empty_frame.pack(expand=True, fill=tk.BOTH, pady=50)
        
        if list_type == "all":
            icon = "🎮"
            message = "No games found"
            subtitle = "Click 'Scan Games' to discover your games"
        elif list_type == "favorites":
            icon = "⭐"
            message = "No favorites yet"
            subtitle = "Star your favorite games to see them here"
        else:
            icon = "🗑️"
            message = "No deleted games"
            subtitle = "Games you remove will appear here"
        
        tk.Label(empty_frame, text=icon, font=('Segoe UI', 48),
                fg=ModernStyle.TEXT_DIM, bg=ModernStyle.BG_PRIMARY).pack(pady=(0, 10))
        tk.Label(empty_frame, text=message, font=ModernStyle.FONT_HEADER,
                fg=ModernStyle.TEXT_SECONDARY, bg=ModernStyle.BG_PRIMARY).pack()
        tk.Label(empty_frame, text=subtitle, font=ModernStyle.FONT_SMALL,
                fg=ModernStyle.TEXT_DIM, bg=ModernStyle.BG_PRIMARY).pack(pady=(5, 0))
    
    def create_modern_game_card(self, parent, game, list_type):
        """Create modern game card with hover effects"""
        # Main card frame
        card_frame = tk.Frame(parent, bg=ModernStyle.BG_CARD, relief=tk.FLAT, bd=1)
        card_frame.pack(fill=tk.X, padx=5, pady=3)
        
        # Hover effects
        def on_enter(e):
            card_frame.config(bg=ModernStyle.BG_HOVER)
            info_frame.config(bg=ModernStyle.BG_HOVER)
            name_label.config(bg=ModernStyle.BG_HOVER)
            path_label.config(bg=ModernStyle.BG_HOVER)
            buttons_frame.config(bg=ModernStyle.BG_HOVER)
        
        def on_leave(e):
            card_frame.config(bg=ModernStyle.BG_CARD)
            info_frame.config(bg=ModernStyle.BG_CARD)
            name_label.config(bg=ModernStyle.BG_CARD)
            path_label.config(bg=ModernStyle.BG_CARD)
            buttons_frame.config(bg=ModernStyle.BG_CARD)
        
        card_frame.bind("<Enter>", on_enter)
        card_frame.bind("<Leave>", on_leave)
        
        # Game info section
        info_frame = tk.Frame(card_frame, bg=ModernStyle.BG_CARD)
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=12)
        
        name_label = tk.Label(info_frame, text=game['name'], 
                             font=ModernStyle.FONT_HEADER,
                             fg=ModernStyle.TEXT_PRIMARY, 
                             bg=ModernStyle.BG_CARD)
        name_label.pack(anchor=tk.W)
        
        # Truncate long paths
        path_text = game['path']
        if len(path_text) > 80:
            path_text = "..." + path_text[-77:]
        
        path_label = tk.Label(info_frame, text=path_text, 
                             font=ModernStyle.FONT_SMALL,
                             fg=ModernStyle.TEXT_DIM, 
                             bg=ModernStyle.BG_CARD)
        path_label.pack(anchor=tk.W, pady=(2, 0))
        
        # Buttons section
        buttons_frame = tk.Frame(card_frame, bg=ModernStyle.BG_CARD)
        buttons_frame.pack(side=tk.RIGHT, padx=15, pady=8)
        
        # Launch button
        launch_btn = tk.Button(buttons_frame, text="▶ Launch", 
                              font=ModernStyle.FONT_BUTTON,
                              bg=ModernStyle.ACCENT_GREEN, 
                              fg=ModernStyle.TEXT_PRIMARY,
                              relief=tk.FLAT, bd=0, padx=15, pady=6,
                              cursor='hand2',
                              command=lambda: self.launch_game(game['path']))
        launch_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Favorite button
        is_favorite = any(f['name'] == game['name'] for f in self.favorites)
        fav_text = "⭐" if is_favorite else "☆"
        fav_btn = tk.Button(buttons_frame, text=fav_text, 
                           font=('Segoe UI', 12),
                           bg=ModernStyle.ACCENT_ORANGE, 
                           fg=ModernStyle.TEXT_PRIMARY,
                           relief=tk.FLAT, bd=0, padx=8, pady=6,
                           cursor='hand2',
                           command=lambda: self.toggle_favorite(game))
        fav_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Delete/Restore button
        if list_type == "deleted":
            action_btn = tk.Button(buttons_frame, text="↩", 
                                  font=('Segoe UI', 12),
                                  bg=ModernStyle.ACCENT_BLUE, 
                                  fg=ModernStyle.TEXT_PRIMARY,
                                  relief=tk.FLAT, bd=0, padx=8, pady=6,
                                  cursor='hand2',
                                  command=lambda: self.restore_game(game))
            action_btn.pack(side=tk.RIGHT, padx=(5, 0))
        else:
            delete_btn = tk.Button(buttons_frame, text="🗑", 
                                  font=('Segoe UI', 12),
                                  bg=ModernStyle.ACCENT_RED, 
                                  fg=ModernStyle.TEXT_PRIMARY,
                                  relief=tk.FLAT, bd=0, padx=8, pady=6,
                                  cursor='hand2',
                                  command=lambda: self.delete_game(game))
            delete_btn.pack(side=tk.RIGHT, padx=(5, 0))
    
    def filter_games(self, *args):
        """Filter games based on search query"""
        query = self.search_var.get().lower()
        if not query:
            self.filtered_games = self.games.copy()
        else:
            self.filtered_games = [g for g in self.games if query in g['name'].lower()]
        
        self.populate_modern_game_list(self.all_scrollable, self.filtered_games, "all")
        
        # Update quick stats
        if query:
            self.quick_stats.config(text=f"Found {len(self.filtered_games)} games matching '{query}'")
        else:
            self.quick_stats.config(text=f"{len(self.games)} games total")
    
    # [Rest of the methods remain the same - launch_game, toggle_favorite, delete_game, etc.]
    # I'll include the key ones that might need updates:
    
    def populate_favorites_list(self):
        """Update favorites list"""
        # Remove deleted games from favorites
        self.favorites = [f for f in self.favorites if f['path'] not in [d['path'] for d in self.deleted_games]]
        self.populate_modern_game_list(self.favorites_scrollable, self.favorites, "favorites")
    
    def populate_deleted_list(self):
        """Update deleted games list"""
        self.populate_modern_game_list(self.deleted_scrollable, self.deleted_games, "deleted")
    
    def show_deleted_games(self):
        """Switch to deleted games tab"""
        self.notebook.select(2)  # Select deleted tab
    
    def launch_game(self, game_path):
        """Launch game with better feedback"""
        try:
            if os.path.exists(game_path):
                os.startfile(game_path)
                game_name = os.path.basename(game_path)
                self.status_label.config(text=f"🚀 Launched: {game_name}")
            else:
                messagebox.showerror("Game Not Found", f"The game executable was not found:\n{game_path}")
                self.status_label.config(text="❌ Game not found")
        except Exception as e:
            messagebox.showerror("Launch Error", f"Failed to launch game:\n{str(e)}")
            self.status_label.config(text="❌ Launch failed")
    
    def toggle_favorite(self, game):
        """Toggle favorite status with better feedback"""
        favorite_names = [f['name'] for f in self.favorites]
        
        if game['name'] in favorite_names:
            self.favorites = [f for f in self.favorites if f['name'] != game['name']]
            self.status_label.config(text=f"💔 Removed from favorites: {game['name']}")
        else:
            self.favorites.append(game)
            self.status_label.config(text=f"⭐ Added to favorites: {game['name']}")
        
        self.save_favorites()
        self.update_game_lists()
        
    def delete_game(self, game):
        """Move game to deleted list"""
        result = messagebox.askyesno("Delete Game", 
                                   f"Remove '{game['name']}' from the games list?\n\n"
                                   f"This won't delete the actual game files, just hide it from the launcher.")
        if result:
            self.deleted_games.append(game)
            self.games = [g for g in self.games if g['path'] != game['path']]
            self.favorites = [f for f in self.favorites if f['path'] != game['path']]
            
            # Update filtered games if search is active
            if hasattr(self, 'filtered_games'):
                self.filtered_games = [g for g in self.filtered_games if g['path'] != game['path']]
            
            self.save_deleted_games()
            self.save_favorites()
            self.update_game_lists()
            self.status_label.config(text=f"🗑️ Deleted: {game['name']}")
if __name__ == "__main__":
    root = tk.Tk()
    app = GameLauncher(root)
    root.mainloop()