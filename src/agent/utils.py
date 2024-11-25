# utils.py
import logging
import asyncio
from typing import Optional, Literal
from nodriver.cdp.input_ import TouchPoint, dispatch_touch_event
from nodriver import Tab

logger = logging.getLogger(__name__)

async def dismiss_app_banner(tab: Tab) -> None:
    """
    Dismisses the 'Not Now' prompt for the application download if present.

    :param tab: The page tab containing the dismiss button.
    """
    dismiss_button = await tab.find('*[data-e2e*="alt-middle-cta-cancel-btn"], *[data-e2e*="bottom-cta-cancel-btn"]')
    if dismiss_button:
        await dismiss_button.click()
        logging.info("Dismissed app banner")

async def get_video_current_time(tab: Tab) -> float:
    """
    Retrieves the current playback position of a video in seconds using CDP (Chrome DevTools Protocol).
    
    :param tab: The tab containing the video element.
    :return: The current playback position of the video, or 0.0 if the position cannot be retrieved.
    """
    current_time_script = """
    (function() {
        var video = document.querySelector('video');
        if (video) {
            return video.currentTime;
        } else {
            return 0.0;
        }
    })();
    """
    current_time = await tab.evaluate(current_time_script)
    if current_time is None:
        logger.warning("Could not retrieve currentTime for video. Assuming currentTime = 0.")
        current_time = 0.0
    return float(current_time)

def calculate_time_to_watch(duration: float, current_time: float, remaining_time: float, default: int = 5) -> float:
    """
    Calculate the time left to watch a video.

    :param duration: Total duration of the video.
    :param current_time: Current time of the video.
    :param remaining_time: Remaining time in the video playback (optional).
    :param default: Default value if there's no valid time information.
    :return: Time left to watch as a float, or the default value if not applicable.
    """
    time_to_watch = max(0.0, duration - current_time)
    if time_to_watch > 0:
        return min(time_to_watch, remaining_time)
    return default

def get_video_duration(video: dict) -> float:
    """
    Get the duration of a video.

    :param video: Video metadata as a dictionary.
    :return: Duration of the video as a float, or 0.0 if not found.
    """
    try:
        container = video.get('video', {})
        duration = container.get('duration', 0.0)
        return float(duration)
    except (TypeError, ValueError) as e:
        logger.info("Failed to get video duration", e)
    return 0.0

async def send_touch_event(
    tab,
    event_type: str,
    x: float,
    y: float,
    force: Optional[float] = 1.0,
    radius_x: Optional[float] = 1.0,
    radius_y: Optional[float] = 1.0,
    modifiers: Optional[int] = 0,
) -> None:
    """
    Dispatch a touch event (touchStart, touchMove, touchEnd) to the page.

    :param tab: The CDP session or tab instance.
    :param event_type: Type of touch event ('touchStart', 'touchMove', 'touchEnd').
    :param x: X coordinate of the touch point in CSS pixels.
    :param y: Y coordinate of the touch point in CSS pixels.
    :param force: *(Optional)* The force of the touch (default: 1.0).
    :param radius_x: *(Optional)* X radius of the touch area (default: 1.0).
    :param radius_y: *(Optional)* Y radius of the touch area (default: 1.0).
    :param id_: *(Optional)* Unique identifier for the touch point (default: 1.0).
    :param modifiers: *(Optional)* Bit field representing pressed modifier keys (default: 0).
    """
    touch_point = TouchPoint(
        x=x,
        y=y,
        force=force,
        radius_x=radius_x,
        radius_y=radius_y,
    )

    await tab.send(
        dispatch_touch_event(
            type_=event_type,
            touch_points=[touch_point]
        )
    )

async def swipe(
    tab,
    x: float,
    y: float,
    size: float,
    direction: Literal['up', 'down', 'left', 'right'],
    steps: int = 10,
    duration: int = 100,
) -> None:
    """
    Perform a swipe action on the page in the specified direction.

    :param tab: The CDP session or tab instance.
    :param x: Starting X coordinate of the swipe.
    :param y: Starting Y coordinate of the swipe.
    :param size: Size of the swipe movement in pixels.
    :param direction: Direction of the swipe ('up', 'down', 'left', 'right').
    :param steps: Number of steps in the swipe (default: 10).
    :param duration: Total duration of the swipe in milliseconds (default: 250).
    """
    interval = duration / steps / 1000  # Convert interval to seconds

    # Determine the delta for each direction
    delta_x = 0
    delta_y = 0

    if direction == 'up':
        delta_y = -size / steps
    elif direction == 'down':
        delta_y = size / steps
    elif direction == 'left':
        delta_x = -size / steps
    elif direction == 'right':
        delta_x = size / steps
    else:
        raise ValueError("Invalid direction. Use 'up', 'down', 'left', or 'right'.")

    logger.info(f"Swipe {direction}: delta_x:{delta_x} delta_y: {delta_y} interval:{interval}")
    # Start the swipe action
    await send_touch_event(tab, "touchStart", x, y)
    # Perform the swipe movement
    current_x = x
    current_y = y
    for _ in range(steps):
        current_x += delta_x
        current_y += delta_y
        await send_touch_event(tab, "touchMove", current_x, current_y)
        await asyncio.sleep(interval)

    # End the swipe action
    await send_touch_event(tab, "touchEnd", current_x, current_y)

async def swipe_down(
    tab,
    start_x: float,
    start_y: float,
    end_y: float,
    steps: int = 5,
    duration: int = 250,
) -> None:
    """
    Perform a swipe down action on the page.

    :param tab: The CDP session or tab instance.
    :param start_x: Starting X coordinate of the swipe.
    :param start_y: Starting Y coordinate of the swipe.
    :param end_y: Ending Y coordinate of the swipe.
    :param steps: Number of steps in the swipe (default: 5).
    :param duration: Total duration of the swipe in milliseconds (default: 250).
    """
    interval = duration / steps / 1000  # Convert interval to seconds
    delta_y = (end_y - start_y) / steps

    # Dispatch touchStart event
    await send_touch_event(tab, "touchStart", start_x, start_y)

    # Dispatch touchMove events
    for i in range(1, steps + 1):
        current_y = start_y - delta_y * i
        await send_touch_event(tab, "touchMove", start_x, current_y)
        await asyncio.sleep(interval)

    # Dispatch touchEnd event
    await send_touch_event(tab, "touchEnd", start_x, end_y)

async def tap_on_element(tab, x: float, y: float) -> None:
    """ 
    Simulate a tap action by dispatching touchStart and touchEnd events
    
    :param x: X coordinate of the touch point in CSS pixels.
    :param y: Y coordinate of the touch point in CSS pixels.
    """ 
    await send_touch_event(tab, "touchStart", x, y)
    await send_touch_event(tab, "touchEnd", x, y)