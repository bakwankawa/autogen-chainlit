import aiohttp
import json
from typing_extensions import Annotated
from config import cosmos_client, SERPER_API_KEY, apify_client, SELECTED_VALUE

# Function to get the name associated with a specific 'pn_rm'
async def get_nama_rm(selected_value) -> str:
    database_name = 'rm_kpi'
    container_name = selected_value

    # Reference to the database and container
    database = cosmos_client.get_database_client(database_name)
    container = database.get_container_client(container_name)

    # Query to get all items and filter in Python
    query = "SELECT c.pn_rm, c.nama_rm FROM c"
    all_items = list(container.query_items(query=query, enable_cross_partition_query=True))

    # Filter the result in Python to find the specific 'pn_rm'
    for item in all_items:
        if str(item.get('pn_rm')) == str(selected_value):
            return item.get('nama_rm', "Unknown")
    return "Unknown"

# Function for google search
async def google_search(
    search_keyword: Annotated[str, "the keyword to search information by google api"]) -> Annotated[dict, "the json response from the google search api"]:
    """
    Perform a Google search using the provided search keyword.

    Args:
    search_keyword (str): The keyword to search on Google.

    Returns:
    str: The response text from the Google search API.
    """
    url = "https://google.serper.dev/search"

    payload = json.dumps({
        "q": search_keyword
    })

    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=payload) as response:
            response_text = await response.text()
            print("RESPONSE:", response_text)
            return response_text

# Function for google search for spokesman
async def google_search_for_spokesman(
    search_keyword: Annotated[str, "the keyword to search information by google api"]) -> Annotated[dict, "the json response from the google search api"]:
    """
    Perform a Google search using the provided search keyword.

    Args:
    search_keyword (str): The keyword to search on Google.

    Returns:
    str: The response text from the Google search API.
    """
    url = "https://google.serper.dev/search"

    payload = json.dumps({
        "q": search_keyword
    })

    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=payload) as response:
            response_text = await response.text()
            print("RESPONSE:", response_text)
            return response_text

# Function for google maps search
async def google_maps_search(
    keyword: Annotated[str, "the keyword to search location"]) -> Annotated[dict, "the json response from the google maps api"]:
    """
    Perform a Google search using the provided search keyword.

    Args:
    search_keyword (str): The keyword to search on Google.

    Returns:
    str: The response text from the Google search API.
    """
    url = "https://google.serper.dev/maps"

    payload = json.dumps({
        "q": keyword
    })

    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=payload) as response:
            response_text = await response.text()
            print("RESPONSE:", response_text)
            return response_text

# Function for web scraping
async def scrape_page(url: Annotated[str, "The URL of the web page to scrape"]) -> Annotated[str, "Scraped content"]:
    """
    Scrape the content from a specified web page URL using Apify's scraping capabilities.

    Args:
    url (str): The URL of the web page to scrape.

    Returns:
    str: The scraped content from the page.
    """
    # Prepare the Actor input
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

    # Run the Actor and wait for it to finish
    run = await apify_client.actor("aYG0l9s7dbB7j3gbS").call(run_input=run_input)

    if run.get("status") == "SUCCEEDED":

        # Fetch and print Actor results from the run's dataset (if there are any)
        text_data = ""
        async for item in apify_client.dataset(run["defaultDatasetId"]).iterate_items():
            text_data += item.get("text", "") + "\n"

        average_token = 0.75
        max_tokens = 20000  # slightly less than max to be safe 32k
        text_data = text_data[: int(average_token * max_tokens)]
    else:
        print(f"HTTP request failed with status code {run.get('status')}") 

    return text_data

# Function for getting internal pipeline data
async def gather_internal_pipeline_data() -> str:
    """
    Function to be used by the ResearcherPipeline agent to gather data from Cosmos DB.

    Args:
    None

    Returns:
    str: A JSON string of the pipeline data for 'pn_rm' = selected_value.
    """
    database_name = 'rm_pipeline'
    container_name = SELECTED_VALUE

    # Mendapatkan referensi ke database dan kontainer
    database = cosmos_client.get_database_client(database_name)
    container = database.get_container_client(container_name)

    # Mengambil semua data dari kontainer
    all_items = list(container.query_items(
        query="SELECT c.pn_rm, c.nama_rm, c.jenis_pipeline, c.pipeline_group, c.nama_calon_nasabah, c.no_telepon_nasabah, c.alamat, c.nilai_potensi, c.jenis_potensi, c.potensi_sales_volume, c.potensi_casa, c.potensi_freq_transaksi, c.day_last_trx, c.rating, c.keterangan_potensi, c.date ,c.action_plan ,c.program FROM c",
        enable_cross_partition_query=True
    ))[:50]

    # Convert the clean data to a JSON string
    result = json.dumps(all_items, separators=(',', ':'))
    
    # Format the result with the required sentence and two new lines
    formatted_result = f"Result from relevant pipeline data: \n\n{result}"
    
    return formatted_result

# Function for getting internal kpi data
async def gather_internal_kpi_data() -> str:
    """
    Function to be used by the ResearcherKPI agent to gather data from Cosmos DB.

    Args:
    None

    Returns:
    str: A JSON string of the KPI data with unmet targets for 'pn_rm' = selected_value.
    """
    database_name = 'rm_kpi'
    container_name = SELECTED_VALUE

    # Mendapatkan referensi ke database dan kontainer
    database = cosmos_client.get_database_client(database_name)
    container = database.get_container_client(container_name)

    # Mengambil semua data dari kontainer
    all_items = list(container.query_items(
        query="SELECT c.pn_rm, c.nama_rm, c['key_performance_index (KPI)'], c.target_KPI, c.pencapaian_KPI FROM c",
        enable_cross_partition_query=True
    ))

    # Convert the clean data to a JSON string
    result = json.dumps(all_items, separators=(',', ':'))
    
    # Format the result with the required sentence and two new lines
    formatted_result = f"Result from relevant target KPI data: \n\n{result}"
    
    return formatted_result