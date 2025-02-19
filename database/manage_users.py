import argparse
from db import add_recipient, remove_recipient

##################################################################################
# main
#
# This script manages a mailing list for class notifications. It provides command-line
# functionality for adding and removing recipients from the list.
#
# Inputs:
#   None (parsed from command-line arguments)
#
# Outputs:
#   None 
#
# Command-line Usage:
#   - To add a recipient: 
#     python script.py add <email>
#   - To delete a recipient:
#     python script.py delete <email>
#
# Example:
#   python manage_users.py add recipient@example.com  # Adds email to the list
#   python manage_users.py delete recipient@example.com  # Removes email from the list
##################################################################################

def main():
    parser = argparse.ArgumentParser(description="Manage the mailing list for class notifications.")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Add recipient command
    add_parser = subparsers.add_parser("add", help="Add a recipient to the mailing list")
    add_parser.add_argument("email", type=str, help="Email address of the recipient")

    # Delete recipient command
    delete_parser = subparsers.add_parser("delete", help="Remove a recipient from the mailing list")
    delete_parser.add_argument("email", type=str, help="Email address of the recipient")

    args = parser.parse_args()

    if args.command == "add":
        add_recipient(args.email)
    elif args.command == "delete":
        remove_recipient(args.email)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
