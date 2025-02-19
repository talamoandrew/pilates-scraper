import base64
import os.path

from datetime import datetime
from email.message import EmailMessage
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from database.db import save_notification

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

##################################################################################
# gmail_send_message
#
# Sends an email notification about available Pilates class openings.
# This function handles authentication with the Gmail API and formats the 
# email content with class details before sending the email.
#
# Inputs:
#   openings (list): A list of dictionaries where each dictionary represents
#                    an open class with details such as time, level, and spots available.
#   recipient (str): The email address of the recipient.
#
# Outputs:
#   dict: A dictionary containing the Gmail API response, including the message ID.
#
# Notes:
#   - Uses OAuth2 authentication to send emails via the Gmail API.
#   - If no valid credentials exist, the function prompts for authentication.
#   - Formats class openings into a structured email body before sending.
##################################################################################
def gmail_send_message(openings, recipient):
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("gmail", "v1", credentials=creds)
        message = EmailMessage()

        message_string = ""

        for open_class in openings:
            time_obj = datetime.strptime(open_class["time"], "%H:%M")
            time_12hr = time_obj.strftime("%I:%M %p")
            message_string += "%s | %s | %s | %s\n" % (
                open_class["open_spots"].ljust(14),
                open_class["level"].ljust(10),
                open_class["date"].ljust(10),
                time_12hr.ljust(15),
            )

            save_notification(open_class["date"], open_class["time"], open_class["level"], recipient)

        message.set_content(message_string)

        message["To"] = recipient
        message["From"] = "tandydragon@gmail.com"
        message["Subject"] = "Pilates Opening(s)"

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"raw": encoded_message}
        send_message = (
            service.users()
            .messages()
            .send(userId="me", body=create_message)
            .execute()
        )
        print(f'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(f"An error occurred: {error}")
        send_message = None

    return send_message
