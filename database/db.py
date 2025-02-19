import sqlite3
import datetime

##################################################################################
# init_db
#
# Initializes the database and creates the required tables (`sent_notifications`
# and `recipients`) if they don't already exist.
#
# Inputs:
#   None
#
# Outputs:
#   None
##################################################################################
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create the sent_notifications table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sent_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_date TEXT,
            class_time TEXT, 
            class_level TEXT, 
            recipient_email TEXT, 
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create the recipients table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE
        )
    """)

    conn.commit()
    conn.close()

##################################################################################
# get_db_connection
#
# Establishes and returns a connection to the SQLite database.
# This function is designed to manage the database connection for other database
# operations, such as querying, inserting, or updating records in the database.
#
# Inputs:
#   None
#
# Outputs:
#   sqlite3.Connection: A connection object to the SQLite database.
#
# Notes:
#   - The connection is opened to the "notifications.db" SQLite database.
#   - The caller is responsible for closing the connection after use.
##################################################################################
def get_db_connection():
    conn = sqlite3.connect("notifications.db")
    return conn

##################################################################################
# was_notified
#
# Checks if a recipient has already been notified about a specific class
# opening (by class date and time).
#
# Inputs:
#   class_date (str): The date of the class.
#   class_time (str): The time of the class.
#   recipient_email (str): The recipient's email address.
#
# Outputs:
#   bool: Returns True if the recipient has been notified about the
#         specific class, False otherwise.
##################################################################################
def was_notified(class_date, class_time, recipient_email):

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 1 FROM sent_notifications
        WHERE class_date = ? AND class_time = ? AND recipient_email = ?
    """, (class_date, class_time, recipient_email))
    result = cursor.fetchone()
    conn.close()

    return result is not None

##################################################################################
# save_notification
#
# Saves a record of a sent notification to the database for tracking purposes.
#
# Inputs:
#   class_date (str): The date of the class.
#   class_time (str): The time of the class.
#   class_level (str): The difficulty level of the class.
#   recipient_email (str): The email address of the recipient.
#
# Outputs:
#   None
##################################################################################
def save_notification(class_date, class_time, class_level, recipient_email):
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sent_notifications (class_date, class_time, class_level, recipient_email)
        VALUES (?, ?, ?, ?)
    """, (class_date, class_time, class_level, recipient_email))
    conn.commit()
    conn.close()

##################################################################################
# process_openings
#
# Filters out class openings that the recipient has already been notified about.
#
# Inputs:
#   openings (list): A list of dictionaries where each dictionary represents
#                    an open class.
#   recipient_email (str): The email address of the recipient.
#
# Outputs:
#   list: A filtered list of openings, excluding those that the recipient
#         has already been notified about.
##################################################################################
def process_openings(openings, recipient_email):
   
    new_openings = []
    
    for open_class in openings:
        if not was_notified(open_class["date"], open_class["time"], recipient_email):
            new_openings.append(open_class)

    return new_openings

##################################################################################
# delete_class_entries
#
# Deletes all rows from the sent_notifications table that match the given 
# class_date and class_time.
#
# Inputs:
#   class_date (str): The date of the class to delete.
#   class_time (str): The time of the class to delete.
#
# Outputs:
#   None
##################################################################################
def delete_class_entries(class_date, class_time):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM sent_notifications 
        WHERE class_date = ? AND class_time = ?
    """, (class_date, class_time))

    conn.commit()
    conn.close()

##################################################################################
# cleanup_old_classes
#
# Removes class entries from the sent_notifications table that have already 
# started, based on the current date and time.
#
# Inputs:
#   None
#
# Outputs:
#   None
##################################################################################
def cleanup_old_classes():
    conn = get_db_connection()
    cursor = conn.cursor()

    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute("""
        DELETE FROM sent_notifications WHERE class_date || ' ' || class_time < ?
    """, (current_time,))

    conn.commit()
    conn.close()    

##################################################################################
# add_recipient
#
# Adds a new recipient email to the recipients table in the database.
#
# Inputs:
#   email (str): The email address of the recipient to be added.
#
# Outputs:
#   None
##################################################################################
def add_recipient(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO recipients (email) VALUES (?)", (email,))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Recipient {email} is already in the database.")
    
    conn.close()

##################################################################################
# remove_recipient
#
# Removes a recipient email from the recipients table in the database.
#
# Inputs:
#   email (str): The email address of the recipient to be removed.
#
# Outputs:
#   None
##################################################################################
def remove_recipient(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM recipients WHERE email = ?", (email,))
    conn.commit()
    print(f"Removed {email} from the database.")
    conn.close()

##################################################################################
# recipient_exists
#
# Checks if a recipient email exists in the recipients table.
#
# Inputs:
#   email (str): The email address of the recipient to be checked.
#
# Outputs:
#   bool: Returns True if the recipient exists in the database, False
#         otherwise.
##################################################################################
def recipient_exists(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT 1 FROM recipients WHERE email = ?", (email,))
    result = cursor.fetchone()
    
    conn.close()
    return result is not None

##################################################################################
# get_all_recipients
#
# Retrieves all recipient emails from the recipients table.
#
# Inputs:
#   None
#
# Outputs:
#   list: A list of all recipient emails stored in the database.
##################################################################################
def get_all_recipients():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT email FROM recipients")
    recipients = cursor.fetchall()
    
    conn.close()
    return [email[0] for email in recipients]


if __name__ == "__main__":
    init_db()
