from datetime import datetime
from scraper.scraper import check_class_openings
from notif.email_sender import gmail_send_message
from database.db import process_openings, get_all_recipients, cleanup_old_classes

##################################################################################
# main
#
# Orchestrates the process of checking for available Pilates class openings,
# notifying recipients via email, and cleaning up old class entries in the database.
#
# Inputs:
#   None
#
# Outputs:
#   None
#
# Notes:
#   - Retrieves the current timestamp and prints it for logging purposes.
#   - Calls check_class_openings() to retrieve available classes.
#   - Fetches all recipients from the database and filters class openings
#     for each recipient to avoid duplicate notifications.
#   - Sends an email to recipients who have not yet been notified about the
#     current class openings.
#   - Calls cleanup_old_classes() to remove outdated class entries from the database.
##################################################################################
def main():
    timestamp = datetime.now()
    print("Current Time:", timestamp, "\n")

    openings = check_class_openings()
    recipients = get_all_recipients()

    if openings:
        for recipient in recipients:
            filtered_openings = process_openings(openings, recipient)
            if filtered_openings:
                gmail_send_message(filtered_openings, recipient)
            else:
                print(recipient + " was already notified about all current openings")
    else:
        print("No class openings at this time")

    print("\n")
    cleanup_old_classes()

if __name__ == "__main__":
    main()
