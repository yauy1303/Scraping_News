import requests
from bs4 import BeautifulSoup
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import schedule
import time
import traceback


def fetch_top_article():
    """
    Fetches the top article from the specified website.
    Returns:
        dict: A dictionary containing the article title, link, and publication date.
    """
    url = "https://forest.watch.impress.co.jp/"
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Locate the top article
    top_article = soup.find("ul", id="daily-block-1")
    if not top_article:
        raise Exception("Top article section not found. Verify the website structure.")

    title_tag = top_article.find("p", class_="title")
    link_tag = title_tag.find("a") if title_tag else None
    date_tag = top_article.find("p", class_="date")

    title = title_tag.text.strip() if title_tag else "No title found"
    link = (
        "https://forest.watch.impress.co.jp/" + link_tag["href"]
        if link_tag
        else "No link found"
    )
    published_date = date_tag.text.strip() if date_tag else "No date found"

    return {"title": title, "link": link, "published_date": published_date}


def update_google_sheet(data):
    """
    Updates the Google Spreadsheet with the fetched data.

    Args:
        data (dict): A dictionary containing the article title, link, and publication date.
    """
    # Google Sheets authentication
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_file(
        "python-scraping-project-444410-71f30189848b.json",
        scopes=scopes,
    )
    client = gspread.authorize(credentials)

    # Open the spreadsheet and select the first worksheet
    spreadsheet = client.open_by_url(
        "https://docs.google.com/spreadsheets/d/1uEyjZnNkg6jUhcRZVx2_2gi2sBIDnjkVSvb-PCQJOuY/edit"
    )
    worksheet = spreadsheet.sheet1

    # Add a new row with the current data
    worksheet.append_row(
        [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data["title"],
            data["link"],
            data["published_date"],
        ]
    )


def monitor_and_update():
    """
    Fetches the top article and updates the Google Sheet.
    """
    try:
        top_article_data = fetch_top_article()
        update_google_sheet(top_article_data)
    except Exception as e:
        print("An error occurred:")
        traceback.print_exc()  # 詳細なエラー情報を表示


# Schedule the task to run daily at 9:00 AM
# schedule.every().day.at("09:00").do(monitor_and_update)

# テスト、一分おき
schedule.every().minute.do(monitor_and_update)

# Keep the script running
if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)
