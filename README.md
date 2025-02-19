# Pilates Class Notifier

This project automates the process of monitoring Pilates class openings and sending email notifications to subscribed users when there are class openings.

## Features

- Automated web scraping to check for class availability
- Email notifications sent to subscribed users
- Database storage to track notified recipients
- Command-line tools for managing the recipient mailing list

## Installation

### Prerequisites

- Python 3.x
- Google Cloud SDK (if running on a cloud VM)
- A configured Gmail API OAuth2 setup for sending emails

### Setup

1. Clone the repository:
   ```sh
   git clone <repository-url>
   cd pilates-notifier
   ```
2. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate   # On macOS/Linux
   venv\Scripts\activate      # On Windows
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

### Running the Scraper

To check for class openings and send notifications, run:

```sh
python main.py
```

### Managing the Mailing List

Add a recipient:

```sh
python -c 'from database.db import add_recipient; add_recipient("recipient@example.com")'
```

Remove a recipient:

```sh
python -c 'from database.db import delete_recipient; delete_recipient("recipient@example.com")'
```

## Deployment on Google Cloud VM

1. Transfer the project files:
   ```sh
   gcloud compute scp pilates-scraper.tar.gz <vm-instance>:~
   ```
2. SSH into the VM and extract the files:
   ```sh
   gcloud compute ssh <vm-instance>
   tar -xzf pilates-scraper.tar.gz
   cd pilates-notifier
   ```
3. Set up the virtual environment and install dependencies:
   ```sh
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. Run the scraper on the VM:
   ```sh
   python main.py
   ```

## License

This project is open-source and available under the MIT License.

