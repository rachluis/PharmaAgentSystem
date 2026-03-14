import sqlite3

def check_users():
    try:
        conn = sqlite3.connect('pharma.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, full_name, phone FROM users")
        users = cursor.fetchall()
        print("Users in database:")
        for user in users:
            print(f"- ID: {user[0]}, Username: {user[1]}, Email: {user[2]}, Name: {user[3]}, Phone: {user[4]}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_users()
