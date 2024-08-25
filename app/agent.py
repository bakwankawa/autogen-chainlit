import asyncio
from app.agent_wrapper import ChainlitAssistantAgent, ChainlitUserProxyAgent
from config import admin_system_message, manager_system_message, spokesman_system_message, researcher_internal_system_message, researcher_external_system_message, analyst_system_message, gpt4_config, SELECTED_VALUE
from app.utils import get_nama_rm, google_search, google_maps_search, scrape_page, gather_internal_kpi_data, gather_internal_pipeline_data, get_today_date
from autogen import register_function

# Run the async function synchronously to get the RM name
admin_system_message = admin_system_message.replace("{rm_name}", asyncio.run(get_nama_rm(SELECTED_VALUE)))
researcher_external_system_message = researcher_external_system_message.replace("{date}", asyncio.run(get_today_date()))

admin = ChainlitUserProxyAgent(
    name="Admin",
    system_message=admin_system_message,
    code_execution_config=False,
)

manager = ChainlitAssistantAgent(
    name="Manager",
    system_message=manager_system_message,
    llm_config=gpt4_config,
)

spokesman = ChainlitAssistantAgent(
    name="Spokesman",
    system_message=spokesman_system_message,
    llm_config=gpt4_config,
    description="Can only be called after Analyst or Manager or Admin. Handling small talk is spokesman responsibility."
)

researcher_internal = ChainlitAssistantAgent(
    name="Researcher_Internal",
    system_message=researcher_internal_system_message,
    llm_config=gpt4_config,
)

researcher_external = ChainlitAssistantAgent(
    name="Researcher_External",
    system_message=researcher_external_system_message,
    llm_config=gpt4_config,
    description="A helpful and general-purpose AI assistant that has capability to gather information from public data including Google Search, Google Maps Search, and Web Scraping."
)

analyst = ChainlitAssistantAgent(
    name="Analyst",
    system_message=analyst_system_message,
    llm_config=gpt4_config,
)

executor = ChainlitUserProxyAgent(
    name="Executor",
    system_message="Executor. Execute the web browsing google map, web scrapping, get current date, and get relevant data from internal database",
    human_input_mode="NEVER"
)

register_function(
    google_search,
    caller=researcher_external,
    executor=executor,
    name="google_search",
    description="Useful tool for searching information about anything on the internet."
)

register_function(
    google_maps_search,
    caller=researcher_external,
    executor=executor,
    name="google_maps_search",
    description="Useful tool for searching locations via the Google Maps API."
)

register_function(
    scrape_page,
    caller=researcher_external,
    executor=executor,
    name="scrap_page",
    description="Useful tool for web scraping."
)

register_function(
    gather_internal_pipeline_data,
    caller=researcher_internal,
    executor=executor,
    name="gather_internal_pipeline_data",
    description="Useful tool for getting internal pipeline data to provide recommendations."
)

register_function(
    gather_internal_kpi_data,
    caller=researcher_internal,
    executor=executor,
    name="gather_internal_kpi_data",
    description="Useful tool for getting internal KPI targets to provide recommendations."
)

# register_function(
#     get_today_date,
#     caller=researcher_external,
#     executor=executor,
#     name="get_today_date",
#     description="Useful tool for getting current date"
# )