import mysql.connector
import getpass
import requests
import re
import webbrowser
import hashlib
import ipaddress

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
        print(f"[Error] Unable to connect to the database: {err}")
        exit()

def register_user():
    while True:
        username = input("Enter username: ").strip()
        if not username:
            print("[Error] Username cannot be empty.")
            continue
        break

    while True:
        password = getpass.getpass("Enter password: ").strip()
        if not password:
            print("[Error] Password cannot be empty.")
            continue
        break

    # Encrypt password using MD5
    hashed_password = hashlib.md5(password.encode()).hexdigest()

    connection = create_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        connection.commit()
        print("[Success] User registered successfully!")
    except mysql.connector.Error as err:
        if err.errno == 1062:
            print("[Error] Username already exists. Please choose a different username.")
        elif err.errno == 1406:
            print("[Error] Data too long for the 'password' column. Please check database schema.")
        else:
            print(f"[Error] {err}")
    finally:
        cursor.close()
        connection.close()

def login_user():
    while True:
        username = input("Enter username: ").strip()
        if not username:
            print("[Error] Username cannot be empty.")
            continue
        break

    while True:
        password = getpass.getpass("Enter password: ").strip()
        if not password:
            print("[Error] Password cannot be empty.")
            continue
        break

    hashed_password = hashlib.md5(password.encode()).hexdigest()

    connection = create_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, hashed_password))
        user = cursor.fetchone()
        if user:
            print("[Success] Login successful!")
            start_ip_tracker()
        else:
            print("[Error] Invalid username or password.")
    except mysql.connector.Error as err:
        print(f"[Error] {err}")
    finally:
        cursor.close()
        connection.close()

def start_ip_tracker():
    tracker = AdvancedIPTracker()
    while True:
        print("\n--- Advanced IP Tracker ---")
        print("1. Track an IP Address")
        print("2. Display My Public IP")
        print("3. View IP Tracking History")
        print("4. Logout")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            track_ip(tracker)
        elif choice == "2":
            my_ip = fetch_my_ip()
            if my_ip:
                track_ip(tracker, my_ip)
        elif choice == "3":
            view_tracking_history()
        elif choice == "4":
            print("Logging out. Goodbye!")
            break
        else:
            print("[Error] Invalid choice. Please try again.")

def fetch_my_ip():
    try:
        response = requests.get("https://api64.ipify.org?format=json")
        if response.status_code == 200:
            my_ip = response.json().get("ip", "")
            print(f"Your Public IP Address: {my_ip}")
            return my_ip
        else:
            print("[Error] Unable to fetch your public IP address.")
    except requests.RequestException:
        print("[Error] Unable to fetch your public IP address.")
    return None

def view_tracking_history():
    connection = create_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT ip_address, tracked_at FROM history ORDER BY tracked_at DESC")
        history = cursor.fetchall()
        if history:
            print("\n--- IP Tracking History ---")
            for record in history:
                print(f"IP: {record[0]} - Tracked At: {record[1]}")
        else:
            print("[Info] No tracking history found.")
    except mysql.connector.Error as err:
        print(f"[Error] {err}")
    finally:
        cursor.close()
        connection.close()

class AdvancedIPTracker:
    def fetch_ip_data(self, ip_address):
        try:
            response = requests.get(f"http://ip-api.com/json/{ip_address}?fields=66846719")
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "fail", "message": "Unable to fetch IP details."}
        except requests.RequestException as e:
            return {"status": "fail", "message": str(e)}

def track_ip(tracker, ip_address=None):
    if not ip_address:
        ip_address = input("Enter the IP address to track: ").strip()

    ip_data = tracker.fetch_ip_data(ip_address)
    if ip_data.get("status") == "success":
        print(f"IP Address: {ip_data.get('query')}")
        print(f"Country: {ip_data.get('country')}")
        print(f"Region: {ip_data.get('regionName')}")
        print(f"City: {ip_data.get('city')}")
        print(f"ISP: {ip_data.get('isp')}")
        print(f"Organization: {ip_data.get('org')}")
        print(f"Time Zone: {ip_data.get('timezone')}")
        print(f"Domain Name: {ip_data.get('reverse', 'N/A')}")
        print(f"Latitude: {ip_data.get('lat')}")
        print(f"Longitude: {ip_data.get('lon')}")
        print(f"Google Maps Link: https://www.google.com/maps?q={ip_data.get('lat')},{ip_data.get('lon')}")

        # Store IP in the tracking history
        connection = create_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("INSERT INTO history (ip_address, tracked_at) VALUES (%s, NOW())", (ip_data.get('query'),))
            connection.commit()
            print("[Success] IP tracking information saved.")
        except mysql.connector.Error as err:
            print(f"[Error] Unable to save IP tracking history: {err}")
        finally:
            cursor.close()
            connection.close()

    else:
        print("[Error] Unable to track the IP address.")

def main_menu():
    while True:
        print("\n--- User Management System ---")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            register_user()
        elif choice == "2":
            login_user()
        elif choice == "3":
            print("Exiting. Goodbye!")
            break
        else:
            print("[Error] Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()

