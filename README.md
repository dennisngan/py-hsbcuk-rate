# py-hsbcuk-rate
A Python automation script that scrapes the latest mortgage rates from HSBC UK and SONIA rates from Chatham Financial, then uploads the data to a Google Sheet.
```
🔄 Schedule: Runs automatically Monday to Friday
```
🌍 Sources:
- HSBC UK Mortgage Rates : https://www.hsbc.co.uk/mortgages/buy-to-let/rates/

- Chatham Financial European Market Rates (SONIA) : https://www.chathamfinancial.com/technology/european-market-rates

📄 Destination: Google Sheet Link
- https://docs.google.com/spreadsheets/d/1C23itYzzSRZDkoG6wip35E7xptTZC8xwi2oFjeK-d-I/edit?gid=1394984308#gid=1394984308

Features

    Scrapes daily mortgage and SONIA rates

    Pushes the latest data to a shared Google Sheet

    Includes Telegram Bot support for optional notifications

Installation:

Clone the repository:
```
git clone https://github.com/dennisngan/py-hsbcuk-rate.git

cd py-hsbcuk-rate

Install dependencies:

pip install -r requirements.txt
```
Set up environment variables:
```
Copy .env.example to .env

Fill in the Token and Chat ID for Telegram and Google sheet URL (if needed)
```


Google Sheets Setup and credentials.json file:
```
Enable the Google Sheets API in your Google Cloud Console.

Create a service account and download the credentials.json file

Share your Google Sheet with the service account email.
```


Running the script manually:
```
python UkMortgageRateScrapper.py
```

Automation

You can schedule this script to run Monday to Friday using:
```
cron (Linux/macOS)

Task Scheduler (Windows)

GitHub Actions (if you want it cloud-hosted)
```


Example cronjob (run every weekday at 10 AM):

0 10 * * 1-5 /usr/bin/python3 /path/to/UkMortgageRateScrapper.py

Telegram Bot (Optional)
```
TelBot.py is included for Telegram notifications.

Configure the Telegram Bot Token and Chat ID in the .env file if you want to receive alerts.
```
File Structure

```
.
├── .github/workflows/         # GitHub Actions CI/CD workflows
├── .env.example               # Example env variables
├── UkMortgageRateScrapper.py   # Main script to scrape and upload rates
├── TelBot.py                   # Optional: Send notifications via Telegram
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

License

This project is licensed under the MIT License.