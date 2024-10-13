# RSS News Fetcher

## Overview
This project automates the process of fetching news from the BBC RSS feed every three hours using a cron job. It checks for duplicate news articles based on their GUID, saves new articles in a structured JSON format, and sends email notifications for each new article. Additionally, it logs execution details and errors for monitoring purposes.

## Features
- **Scheduled Execution**: Runs every three hours using `crontab`.
- **Duplicate Detection**: Uses GUID to check if an article has already been processed.
- **Data Storage**: Saves articles as JSON files organized by date in `/var/log/py_report/`.
- **Email Notifications**: Sends emails with the title, link, and description of new articles.
- **Error Handling**: Implements retry logic for network requests and logs errors.
- **Execution Logging**: Records execution times and logs steps in `/var/log/py_log/`.

## Requirements
- Python 3.x
- Libraries: `requests`, `feedparser`, `smtplib`, `logging`, `redis`
- Access to a Redis database
- Root privileges to create directories in `/var/log/`

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/FarnoodID/RSS.git
   ```
2. Navigate to the project directory:
   ```bash
   cd RSS
   ```
3. Install required libraries:
   ```bash
   pip install requests feedparser redis
   ```
## Configuration
1. Clone the repository:
   ```python
   email = "your_email@gmail.com"
   Epassword = "your_email_password"
   emailTo = "recipient_email@gmail.com"
   ```
2. Ensure that Redis is running on your machine.

### Cron Job Setup
To run the script every three hours, add the following line to your crontab:
  ```bash
  0 */3 * * * /usr/bin/python3 /path/to/your/script.py
  ```
## Usage
Run the script manually for the first time to set up directories and test functionality:
sudo python3 script.py

## Logging
Logs are stored in ``/var/log/py_log/`` with filenames formatted as ``yyyymmddhhMMss.log``. The logs include execution times, errors, and notifications about processed articles.

## Challenges Faced
- Finding an appropriate parser for RSS feeds.
- Configuring ``crontab`` to run scripts with sudo privileges without requiring a password.
   
