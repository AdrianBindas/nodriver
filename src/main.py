import logging

from agent.config import config
from agent.scraper_context import ScraperContext
from agent.event_handlers import EventHandlers
from nodriver import cdp, loop, start

# Configure logging
logging.basicConfig(
    filename=config.log_file,
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)
logger = logging.getLogger(__name__)

# Monkey-patch parse_json_event, for handling current buggy behavior in nodriver
original_parse_json_event = cdp.util.parse_json_event

def patched_parse_json_event(json_message):
    try:
        return original_parse_json_event(json_message)
    except KeyError:
        return None

cdp.util.parse_json_event = patched_parse_json_event

async def initiate_browser():
    browser = await start(
        browser_args=config.browser_options,
        lang=config.lang,
    )
    try:
        context = ScraperContext()
        handlers = EventHandlers(context)
        tab = browser.main_tab
        tab.inspector_open()
        await handlers.add_network_handles(tab)
        await context.browse_fyp(tab)
    finally:
        await tab.close()

if __name__ == '__main__':
    loop().run_until_complete(initiate_browser())
