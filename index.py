import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkinter.font import Font
import mysql.connector
import requests
import hashlib
COLORS = {
    "background": "#2D2D2D",
    "primary": "#3A3A3A",
    "secondary": "#4A4A4A",
    "accent": "#1ABC9C",
    "text": "#FFFFFF",
    "warning": "#E74C3C"
}
def create_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="trackip",
            charset="utf8mb4",
            collation="utf8mb4_general_ci"
        )
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Unable to connect to the database: {err}")
        exit()
class IPTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IP Tracker & User Management")
        self.root.geometry("600x500")
        self.root.minsize(600, 500)
        self.root.configure(bg=COLORS["background"])
        self.title_font = Font(family="Helvetica", size=16, weight="bold")
        self.body_font = Font(family="Helvetica", size=12)
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background=COLORS["background"])
        self.style.configure("TLabel", background=COLORS["background"], foreground=COLORS["text"], font=self.body_font)
        self.style.configure("TButton", font=self.body_font, padding=6)
        self.style.map("TButton",
            background=[("active", COLORS["accent"]), ("!disabled", COLORS["primary"])],
            foreground=[("active", COLORS["text"]), ("!disabled", COLORS["text"])]
        )
        self.setup_login()
    def setup_login(self):
        """Create login & registration UI."""
        self.clear_window()
        main_frame = ttk.Frame(self.root)
        main_frame.pack(pady=40, padx=20, fill="both", expand=True)
        ttk.Label(main_frame, text="IP Tracker Login", font=self.title_font).pack(pady=20)
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(pady=10)
        ttk.Label(form_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.username_entry = ttk.Entry(form_frame, font=self.body_font)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5, ipady=4)
        ttk.Label(form_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.password_entry = ttk.Entry(form_frame, font=self.body_font, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5, ipady=4)
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Login", command=self.login_user, style="TButton").grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="Register", command=self.register_user).grid(row=0, column=1, padx=10)
        ttk.Button(button_frame, text="Exit", command=root.destroy).grid(row=0, column=2, padx=10)
    def register_user(self):
        """Handles user registration."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        errors = []
        if len(password) < 8:
            errors.append("• Password must be at least 8 characters long")
        if password.isalpha() or password.isdigit():
            errors.append("• Password must contain both letters and numbers")
        if password.islower() or password.isupper():
            errors.append("• Password must contain both uppercase and lowercase characters")
        if password.isalnum():
            errors.append("• Password must contain special characters")
        if not username or not password:
            errors.append("• Username and Password cannot be empty")
        if errors:
            messagebox.showerror("Registration Error", "\n".join(errors))
            return
        hashed_password = hashlib.md5(password.encode()).hexdigest()
        connection = create_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            connection.commit()
            messagebox.showinfo("Success", "Registration successful!")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Registration failed: {err}")
        finally:
            cursor.close()
            connection.close()
    def login_user(self):
        """Handles user login and stores user_id."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Username and Password cannot be empty!")
            return
        hashed_password = hashlib.md5(password.encode()).hexdigest()
        connection = create_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT id FROM users WHERE username = %s AND password = %s", (username, hashed_password))
            user = cursor.fetchone()
            if user:
                self.user_id = user[0]
                messagebox.showinfo("Success", "Login successful!")
                self.open_dashboard()
            else:
                messagebox.showerror("Error", "Invalid username or password.")
        finally:
            cursor.close()
            connection.close()
    def open_dashboard(self):
        """Opens the main application dashboard."""
        self.clear_window()
        main_frame = ttk.Frame(self.root)
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        ttk.Label(main_frame, text="IP Tracker Dashboard", font=self.title_font).pack(pady=20)
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        buttons = [
            ("Track IP Address", self.track_ip_gui, "#1ABC9C"),
            ("My Public IP", self.display_public_ip, "#3498DB"),
            ("Tracking History", self.view_tracking_history, "#F39C12"),
            ("Logout", self.setup_login, "#E74C3C")
        ]
        for idx, (text, command, color) in enumerate(buttons):
            btn = ttk.Button(button_frame, text=text, command=command, style="TButton")
            btn.grid(row=idx//2, column=idx%2, padx=10, pady=10, sticky="nsew")
            btn.configure(style=f"{color}.TButton")
    def track_ip_gui(self):
        """Opens a new window for IP tracking."""
        self.clear_window()
        main_frame = ttk.Frame(self.root)
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        ttk.Label(main_frame, text="Track IP Address", font=self.title_font).pack(pady=10)
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(pady=10)
        ttk.Label(input_frame, text="Enter IP Address:").pack(side="left", padx=5)
        self.ip_entry = ttk.Entry(input_frame, font=self.body_font, width=25)
        self.ip_entry.pack(side="left", padx=5, ipady=4)
        ttk.Button(input_frame, text="Track", command=self.track_ip, style="Accent.TButton").pack(side="left", padx=10)
        result_frame = ttk.Frame(main_frame)
        result_frame.pack(fill="both", expand=True)
        self.result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, font=self.body_font,
                                                    bg=COLORS["primary"], fg=COLORS["text"], insertbackground=COLORS["text"])
        self.result_text.pack(fill="both", expand=True, padx=5, pady=5)
        ttk.Button(main_frame, text="Back", command=self.open_dashboard, style="Warning.TButton").pack(pady=10)
    def track_ip(self):
        """Fetches detailed IP information and stores it in history."""
        ip_address = self.ip_entry.get().strip()
        if not ip_address:
            messagebox.showerror("Error", "Please enter a valid IP address.")
            return
        try:
            response = requests.get(f"http://ip-api.com/json/{ip_address}?fields=status,message,query,country,regionName,city,isp,org,timezone,reverse,lat,lon")
            ip_data = response.json()
        except requests.RequestException:
            messagebox.showerror("Error", "Failed to connect to IP API")
            return
        if ip_data.get("status") == "success":
            details = (
                f"IP Address: {ip_data.get('query')}\n"
                f"Location: {ip_data.get('city')}, {ip_data.get('regionName')}, {ip_data.get('country')}\n"
                f"Coordinates: {ip_data.get('lat')}, {ip_data.get('lon')}\n"
                f"ISP: {ip_data.get('isp')}\n"
                f"Organization: {ip_data.get('org')}\n"
                f"Time Zone: {ip_data.get('timezone')}\n"
                f"Domain Name: {ip_data.get('reverse', 'N/A')}\n"
                f"Latitude: {ip_data.get('lat')}\n"
                f"Longitude: {ip_data.get('lon')}\n"
                f"Map: https://www.google.com/maps?q={ip_data.get('lat')},{ip_data.get('lon')}"
            )
            self.result_text.config(state="normal")
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, details)
            self.result_text.config(state="disabled")
            connection = create_connection()
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "INSERT INTO history (ip_address, tracked_at, user_id) VALUES (%s, NOW(), %s)",
                    (ip_data.get('query'), self.user_id),
                )
                connection.commit()
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Unable to save history: {err}")
            finally:
                cursor.close()
                connection.close()
        else:
            messagebox.showerror("Error", f"Tracking failed: {ip_data.get('message', 'Unknown error')}")
    def display_public_ip(self):
        """Displays the user's public IP address."""
        try:
            ipv4 = requests.get("https://api.ipify.org").text
            ipv6 = requests.get("https://api64.ipify.org").text
        except requests.RequestException:
            messagebox.showerror("Error", "Failed to retrieve public IP")
            return
        
        info_window = tk.Toplevel(self.root)
        info_window.title("Public IP Information")
        info_window.configure(bg=COLORS["background"])
        ttk.Label(info_window, text="Public IP Addresses", font=self.title_font).pack(pady=10)
        content = ttk.Frame(info_window)
        content.pack(pady=10, padx=20)
        ttk.Label(content, text=f"IPv4: {ipv4}").pack(pady=5)
        ttk.Label(content, text=f"IPv6: {ipv6}").pack(pady=5)
        ttk.Button(info_window, text="Close", command=info_window.destroy).pack(pady=10)
    def view_tracking_history(self):
        """Displays tracking history in a table format with delete functionality."""
        self.clear_window()
        main_frame = ttk.Frame(self.root)
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        ttk.Label(main_frame, text="Tracking History", font=self.title_font).pack(pady=10)
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill="both", expand=True)
        
        columns = ("id", "ip", "time")
        self.history_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        
        # Configure columns
        self.history_tree.heading("id", text="ID", anchor="center")
        self.history_tree.heading("ip", text="IP Address", anchor="center")
        self.history_tree.heading("time", text="Tracking Time", anchor="center")
        
        # Hide ID column
        self.history_tree.column("id", width=0, stretch=tk.NO, minwidth=0)
        self.history_tree.column("ip", width=200, anchor="center")
        self.history_tree.column("time", width=250, anchor="center")
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=vsb.set)
        
        self.history_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        
        # Load data
        connection = create_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT id, ip_address, tracked_at FROM history WHERE user_id = %s ORDER BY tracked_at DESC", 
                        (self.user_id,))
            for row in cursor.fetchall():
                self.history_tree.insert("", "end", values=row)
        finally:
            cursor.close()
            connection.close()
        
        # Button container
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Delete Selected", command=self.delete_history_entry, 
                style="Warning.TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Back", command=self.open_dashboard).pack(side="left", padx=5)

    def delete_history_entry(self):
        """Deletes selected history entry from database and treeview."""
        selected_item = self.history_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an entry to delete")
            return
        
        # Get database ID from hidden column
        item_id = self.history_tree.item(selected_item[0])["values"][0]
        
        connection = create_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM history WHERE id = %s", (item_id,))
            connection.commit()
            
            # Remove from treeview
            self.history_tree.delete(selected_item[0])
            messagebox.showinfo("Success", "Entry deleted successfully")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to delete entry: {err}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()
    
    def clear_window(self):
        """Clears all widgets from the current window."""
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = IPTrackerApp(root)
    root.mainloop()