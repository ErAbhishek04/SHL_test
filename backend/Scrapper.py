import time
import pandas as pd
import asyncio
import aiohttp
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Headless Chrome setup
options = Options()
options.headless = True
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Base URL
base_url = "https://www.shl.com/solutions/products/product-catalog/"
driver.get(base_url)
time.sleep(5)  # Allow time for the page to load

# Get total pages from pagination
soup = BeautifulSoup(driver.page_source, "lxml")
pagination_links = soup.select(".pagination__link")
pages = [int(link.text.strip()) for link in pagination_links if link.text.strip().isdigit()]
max_page = max(pages) if pages else 1  # Fallback to 1 if no pages found

# Function to parse a page and return product links + base data
def parse_page(html):
    soup = BeautifulSoup(html, "lxml")
    product_rows = []
    parsed_rows = []

    rows = soup.select("tr[data-course-id], tr[data-entity-id]")
    for row in rows:
        title_tag = row.select_one(".custom__table-heading__title a")
        if not title_tag:
            continue
        title = title_tag.text.strip()
        link = "https://www.shl.com" + title_tag["href"].strip()

        keys = [span.text.strip() for span in row.select(".product-catalogue__key")]
        keys_str = ", ".join(keys)

        general_tds = row.select("td.custom__table-heading__general")
        remote_testing = "Yes" if len(general_tds) > 0 and general_tds[0].select_one(".catalogue__circle.-yes") else "No"
        adaptive_irt = "Yes" if len(general_tds) > 1 and general_tds[1].select_one(".catalogue__circle.-yes") else "No"

        product_rows.append((title, link))
        parsed_rows.append({
            "Product Name": title,
            "Link": link,
            "Keys": keys_str,
            "Remote Testing": remote_testing,
            "Adaptive/IRT": adaptive_irt,
        })

    return product_rows, parsed_rows

# Async fetch for detail pages
async def fetch_product_detail(session, product):
    title, link = product
    try:
        async with session.get(link, timeout=10) as res:
            text = await res.text()
            soup = BeautifulSoup(text, "lxml")

            duration = "N/A"
            test_type = []
            description = "N/A"
            job_levels = "N/A"
            language = "N/A"

            for row in soup.select(".product-catalogue-training-calendar__row"):
                heading = row.select_one("h4")
                if not heading:
                    continue
                heading_text = heading.text.strip().lower()

                if "assessment length" in heading_text:
                    dur_tag = row.select_one("p")
                    if dur_tag:
                        duration = dur_tag.text.strip()
                    span_tags = row.select(".product-catalogue__key")
                    test_type = [span.text.strip() for span in span_tags if span.text.strip()]

                elif "description" in heading_text:
                    desc_tag = row.select_one("p")
                    if desc_tag:
                        description = desc_tag.text.strip()

                elif "job levels" in heading_text:
                    job_tag = row.select_one("p")
                    if job_tag:
                        job_levels = job_tag.text.strip()

                elif "languages" in heading_text:
                    lang_tag = row.select_one("p")
                    if lang_tag:
                        language = lang_tag.text.strip()

            test_type_str = ", ".join(test_type) if test_type else "N/A"
            return title, link, duration, test_type_str, description, job_levels, language
        
    except:
        return title, link, "N/A", "N/A", "N/A", "N/A", "N/A"

async def fetch_all_product_details(products):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_product_detail(session, p) for p in products]
        return await asyncio.gather(*tasks)

# Scrape all pages
all_data = []
product_details = []

for page in range(0, max_page * 12, 12):  # 12 items per page
    paginated_url = f"{base_url}?start={page}&type=2" if page != 0 else base_url
    driver.get(paginated_url)
    time.sleep(2)  # Wait for the page to load
    product_links, partial_data = parse_page(driver.page_source)
    product_details.extend(product_links)
    all_data.extend(partial_data)

driver.quit()

# Fetch durations, test types, and more concurrently
results = asyncio.run(fetch_all_product_details(product_details))

# Merge the results
for i, (title, link, duration, test_type, description, job_levels, language) in enumerate(results):
    all_data[i]["Duration"] = duration
    all_data[i]["Test Type"] = test_type
    all_data[i]["Link"] = link
    all_data[i]["Description"] = description
    all_data[i]["Job Levels"] = job_levels
    all_data[i]["Language"] = language

# Save to CSV
df = pd.DataFrame(all_data)
df.to_csv("shl_product_catalog.csv", index=False)
print("✅ Data saved to 'shl_product_catalog.csv'")
