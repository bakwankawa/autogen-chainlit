import json
import ssl
import aiohttp
import asyncio
import certifi
from typing import Annotated
from app.config import apify_client, SERPER_API_KEY

# Function for google search
async def google_search(
    search_keyword: Annotated[str, "the keyword to search information by google api"]
) -> Annotated[dict, "the json response from the google search api"]:
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": search_keyword})
    headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}

    ssl_context = ssl.create_default_context(cafile=certifi.where())

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=payload, ssl=ssl_context) as response:
            response_text = await response.text()
            response_json = json.loads(response_text)
            
            # Extracting only the 'answerBox' and 'organic' fields
            filtered_response = {
                "answerBox": response_json.get("answerBox"),
                "organic": response_json.get("organic")
            }

            # Save the filtered response to a local JSON file
            with open("filtered_google_search_response.json", "w") as filtered_file:
                json.dump(filtered_response, filtered_file, indent=4)

            return filtered_response

# Function for web scraping
async def scrape_page(url: Annotated[str, "The URL of the web page to scrape"]) -> Annotated[str, "Scraped content"]:
    run_input = {
        "startUrls": [{"url": url}],
        "useSitemaps": False,
        "crawlerType": "playwright:firefox",
        "includeUrlGlobs": [],
        "excludeUrlGlobs": [],
        "ignoreCanonicalUrl": False,
        "maxCrawlDepth": 0,
        "maxCrawlPages": 1,
        "initialConcurrency": 0,
        "maxConcurrency": 200,
        "initialCookies": [],
        "proxyConfiguration": {"useApifyProxy": True},
        "maxSessionRotations": 10,
        "maxRequestRetries": 5,
        "requestTimeoutSecs": 60,
        "dynamicContentWaitSecs": 10,
        "maxScrollHeightPixels": 5000,
        "removeElementsCssSelector": """nav, footer, script, style, noscript, svg,
    [role=\"alert\"],
    [role=\"banner\"],
    [role=\"dialog\"],
    [role=\"alertdialog\"],
    [role=\"region\"][aria-label*=\"skip\" i],
    [aria-modal=\"true\"]""",
        "removeCookieWarnings": True,
        "clickElementsCssSelector": '[aria-expanded="false"]',
        "htmlTransformer": "readableText",
        "readableTextCharThreshold": 100,
        "aggressivePrune": False,
        "debugMode": True,
        "debugLog": True,
        "saveHtml": True,
        "saveMarkdown": True,
        "saveFiles": False,
        "saveScreenshots": False,
        "maxResults": 9999999,
        "clientSideMinChangePercentage": 15,
        "renderingTypeDetectionPercentage": 10,
    }

    run = apify_client.actor("aYG0l9s7dbB7j3gbS").call(run_input=run_input)

    if run.get("status") == "SUCCEEDED":
        text_data = ""
        # Use a regular for loop instead of async for
        for item in apify_client.dataset(run["defaultDatasetId"]).iterate_items():
            text_data += item.get("text", "") + "\n"

        average_token = 0.75
        max_tokens = 20000
        text_data = text_data[: int(average_token * max_tokens)]
    else:
        print(f"HTTP request failed with status code {run.get('status')}") 

    return text_data

# Running the async function
async def main():
    search_keyword = "credit rating bank rakyat indonesia"
    result = await google_search(search_keyword)

    # search_keyword = "https://investor.id/market/370872/saham-goto-mendadak-lompat"
    # result = await scrape_page(search_keyword)

    print(result)

if __name__ == "__main__":
    asyncio.run(main())