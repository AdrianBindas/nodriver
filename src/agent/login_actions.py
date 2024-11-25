import asyncio
import logging
from nodriver import core
from typing import Optional

from config import USE_PROXY

logger = logging.getLogger(__name__)

async def find_and_click(
    tab: core.tab, selector: str, best_match: bool = True, timeout: int = 30, action_name: Optional[str] = None
) -> bool:
    """Find an element by selector and click on it."""
    try:
        element = await tab.find(selector, best_match=best_match, timeout=timeout)
        if element:
            await element.click()
            logger.info(f"Clicked on {action_name or selector}")
            return True
        else:
            logger.error(f"Element not found: {action_name or selector}")
            return False
    except Exception as e:
        logger.error(f"Error clicking {action_name or selector}: {e}")
        return False


async def wait_for_proxy_delay() -> None:
    """Apply delay based on whether a proxy is used."""
    delay = 10 if USE_PROXY else 3
    await asyncio.sleep(delay)


async def send_keys_to_input(
    element: core.ElementHandle, value: str, field_name: str
) -> None:
    """Send keys to an input field."""
    try:
        await element.send_keys(value)
        logger.info(f"Entered value for {field_name}")
    except Exception as e:
        logger.error(f"Failed to input value for {field_name}: {e}")


async def log_in_email(tab: core.tab, email: str, password: str) -> None:
    """
    Log in to TikTok using email and password.
    
    :param tab: The tab instance to perform actions on.
    :param email: The email address for login.
    :param password: The password for login.
    """
    try:
        # Click 'Log in' button
        if not await find_and_click(tab, "Log in", best_match=True, timeout=120, action_name="Log in button"):
            return
        await asyncio.sleep(10)

        # Click 'Use phone / email / username' option
        if not await find_and_click(tab, "Use phone / email / username", best_match=True, timeout=120, action_name="Email/Username option"):
            return

        # Click 'Log in with email or username'
        if not await find_and_click(tab, "Log in with email or username", best_match=True, timeout=60, action_name="Log in with email option"):
            return

        # Fill email and password fields
        email_input = await tab.select("input[type=text]", timeout=30)
        password_input = await tab.select("input[type=password]", timeout=30)
        if email_input and password_input:
            await send_keys_to_input(email_input, email, "Email")
            await send_keys_to_input(password_input, password, "Password")
        else:
            logger.error("Email or password input fields not found.")
            return

        # Click the submit button
        if not await find_and_click(tab, "button[data-e2e='login-button']", timeout=60, action_name="Submit button"):
            return
        await asyncio.sleep(120 if USE_PROXY else 10)

        logger.info("Login process completed successfully.")
    except Exception as e:
        logger.error(f"Error during TikTok login process: {e}")
