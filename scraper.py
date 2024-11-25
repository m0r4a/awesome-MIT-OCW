from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from typing import List


URL = "https://ocw.mit.edu/search/?d=Electrical%20Engineering%20and%20Computer%20Science&l=Undergraduate&t=Computer%20Science&t=Algorithms%20and%20Data%20Structures&t=Systems%20Engineering&t=Software%20Design%20and%20Engineering&t=Programming%20Languages&t=Computer%20Design%20and%20Engineering&t=Computer%20Networks&t=Telecommunications&t=Signal%20Processing&t=Operating%20Systems&t=Systems%20Design&t=Systems%20Optimization&type=course"


def scrape_courses(url: str) -> str:
    """
    Function that scrapes the MIT courses page

    Arg:
        url (str): The URL of the courses, preferably with the filters already applied

    Returns:
        str: The full HTML of the webpage
    """
    # Web browser config
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)

    try:
        # Loads the webpage
        driver.get(url)

        # Wait for the first content to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "learning-resource-card")))

        # When you enter the courses page they are not all loaded by default
        # so this part of the code scrolls to the end to load all the courses.
        last_height = driver.execute_script(
            "return document.body.scrollHeight")
        while True:
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # This gets the full html
        html = driver.page_source

    finally:
        driver.quit()

    return html


def parse_courses(html: str) -> List[str]:
    """
    Function for parsing MIT courses

    Arg:
        html (str): The html parsed by the scrape courses function

    Returns:
        List[str]: A list with the courses and its links
    """

    soup = BeautifulSoup(html, "html.parser")
    courses = []
    for article in soup.find_all("article"):
        title_tag = article.find("div", class_="course-title").find("a")
        if title_tag:
            title = title_tag.text.strip()
            link = "https://ocw.mit.edu" + title_tag['href']
            courses.append({"title": title, "link": link})

    return courses


def save_to_markdown(courses, filename="list.md"):
    """
    Function to create an .md file with the scrapped courses.
    """
    with open(filename, "w", encoding="utf-8") as f:
        for i, course in enumerate(courses, start=1):
            f.write(f"{i}. [{course['title']}]({course['link']})\n")


def main(URL):
    print("Scraping courses...")
    html = scrape_courses(URL)
    print("Parsing courses...")
    courses = parse_courses(html)
    print(f"Found {len(courses)} courses. Saving to Markdown...")
    save_to_markdown(courses)
    print("Saved courses to 'list.md'.")


if __name__ == "__main__":
    main(URL)
