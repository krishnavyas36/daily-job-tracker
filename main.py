import gspread
from google.oauth2.service_account import Credentials
import requests
from bs4 import BeautifulSoup
import os, json
from datetime import datetime

# === Scrape RemoteOK ===
def scrape_remoteok_jobs(limit=50):
    url = "https://remoteok.com/remote-data-jobs"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"RemoteOK error: {response.status_code}")
        return []
    soup = BeautifulSoup(response.text, "html.parser")
    jobs = []
    for row in soup.find_all("tr", class_="job"):
        title = row.find("h2")
        company = row.find("h3")
        link = row.get("data-href")
        if not title or not company or not link:
            continue
        jobs.append({
            "Job Title": title.text.strip(),
            "Company": company.text.strip(),
            "Location": "Remote",
            "Remote": "Yes",
            "Visa Sponsor": "Unknown",
            "Experience Level": "Entry-level",
            "Posted Time": "Recent",
            "Job Link": "https://remoteok.com" + link,
            "Status": "Not Applied",
            "Source": "RemoteOK"
        })
        if len(jobs) >= limit:
            break
    return jobs

# === Scrape USAJobs for multiple keywords ===
def scrape_usajobs(keywords, location="California", limit=10):
    headers = {
        "Host": "data.usajobs.gov",
        "User-Agent": os.environ["USAJOBS_USER_AGENT"],
        "Authorization-Key": os.environ["USAJOBS_API_KEY"]
    }
    jobs = []
    for keyword in keywords:
        url = f"https://data.usajobs.gov/api/search?Keyword={keyword}&LocationName={location}&ResultsPerPage={limit}"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"USAJobs error for '{keyword}': {response.status_code}")
            continue
        data = response.json()
        for item in data["SearchResult"]["SearchResultItems"]:
            pos = item["MatchedObjectDescriptor"]
            post_date = pos.get("PublicationStartDate", "")
            readable_date = datetime.strptime(post_date, "%Y-%m-%dT%H:%M:%S").strftime("%b %d, %Y") if post_date else "Recent"
            jobs.append({
                "Job Title": pos.get("PositionTitle", "N/A"),
                "Company": pos.get("OrganizationName", "USAJobs"),
                "Location": pos.get("PositionLocationDisplay", "N/A"),
                "Remote": "Yes" if "Remote" in pos.get("PositionLocationDisplay", "") else "No",
                "Visa Sponsor": "No",
                "Experience Level": "Entry-level",
                "Posted Time": readable_date,
                "Job Link": pos.get("PositionURI", ""),
                "Status": "Not Applied",
                "Source": "USAJobs"
            })
    return jobs

# === Push to Google Sheet ===
def push_to_sheet(jobs):
    creds_dict = json.loads(os.environ["GOOGLE_SHEET_CREDS"])
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(os.environ["SHEET_ID"]).sheet1
    if not jobs:
        print("No jobs to update.")
        return
    sheet.clear()
    sheet.append_row(list(jobs[0].keys()))
    for job in jobs:
        sheet.append_row(list(job.values()))
    print(f"✅ Uploaded {len(jobs)} jobs to Google Sheet.")

# === Main Script ===
def main():
    keywords = [
        "data analyst", "business intelligence", "data scientist",
        "bi developer", "data engineer", "ai engineer",
        "machine learning", "nlp engineer", "applied scientist"
    ]

    def is_match(title):
        title = title.lower()
        return any(k in title for k in keywords)

    remoteok_jobs = scrape_remoteok_jobs(limit=50)
    usajobs_jobs = scrape_usajobs(keywords, location="California", limit=10)

    all_jobs = remoteok_jobs + usajobs_jobs
    matched_jobs = [job for job in all_jobs if is_match(job["Job Title"])]

    print(f"✅ {len(matched_jobs)} jobs matched your keywords.")
    push_to_sheet(matched_jobs)

if __name__ == "__main__":
    main()

