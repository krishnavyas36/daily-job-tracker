# daily-job-tracker
# 📊 Daily Job Tracker

A Python-based GitHub Actions workflow that scrapes job listings daily from RemoteOK and USAJobs.gov for data and AI-related roles. The matched jobs are automatically pushed to a connected Google Sheet for easy tracking.

---

## 🔍 What It Does

- Scrapes the latest remote-friendly jobs from:
  - [RemoteOK](https://remoteok.com/)
  - [USAJobs.gov](https://www.usajobs.gov/)
- Filters by specific job titles:
  - `Data Analyst`
  - `Business Intelligence Analyst`
  - `Data Scientist`
  - `BI Developer`
  - `Data Engineer`
  - `AI Engineer`
  - `Machine Learning Engineer`
  - `NLP Engineer`
  - `Applied Scientist`
- Pushes the results to a Google Sheet
- Runs daily at **5 PM PST** via GitHub Actions

---

## 📋 Requirements

### 1. Google Service Account

- Create a service account with access to Google Sheets API.
- Download the `.json` credentials file.

### 2. Google Sheet

- Create a Google Sheet with edit access granted to the service account email.
- Copy the **spreadsheet ID** from the URL.

---

## 🔐 Repository Secrets

Go to **Settings → Secrets → Actions** and add the following:

| Secret Name          | Description                                                    |
|----------------------|----------------------------------------------------------------|
| `GOOGLE_SHEET_CREDS` | Full content of the Google service account `.json` file       |
| `SHEET_ID`           | Your target Google Sheet ID (e.g., `1aBcdEfGh...`)            |
| `USAJOBS_USER_AGENT` | Email used to register at [developer.usajobs.gov](https://developer.usajobs.gov) |
| `USAJOBS_API_KEY`    | API Key from your USAJobs developer profile                   |

---

## 🛠 How to Use

### ✅ Option 1: Manual Run

- Go to **Actions** tab
- Select `Daily Job Scraper`
- Click **Run workflow**

### 🕒 Option 2: Scheduled Daily Run

This workflow is scheduled to run automatically every day at 5 PM PST.

You can modify the time in `.github/workflows/job.yml`:

```yaml
schedule:
  - cron: "0 1 * * *"  # 5 PM PST / 1 AM UTC
