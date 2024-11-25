# scraper_context.py
import asyncio
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional, Set

import pandas as pd
from nodriver import Tab

from .config import config
from .utils import (
    get_video_current_time,
    calculate_time_to_watch,
    get_video_duration,
    swipe,
    tap_on_element,
)

logger = logging.getLogger(__name__)

class ScraperContext:
    def __init__(self) -> None:
        self.pending_request_ids: Set[str] = set()
        self.processed_request_ids: Set[str] = set()
        self.processed_video_ids: Set[str] = set()
        self.video_batches_queue: asyncio.Queue = asyncio.Queue()
        self.viewed_videos: List[Dict[str, Any]] = []
        self.start_time: float = time.time()
        self.end_time: float = self.start_time + config.loop_duration
        self.TARGET_ENDPOINT = "https://www.tiktok.com/api/recommend/item_list"
        self.load_processed_video_ids()
        self.config = config

    async def browse_fyp(self, tab: Tab) -> None:
        logger.info("Browsing the For You page...")
        try:
            # Navigate to the For You page
            await self.navigate(tab, "https://www.tiktok.com/foryou")
            await asyncio.sleep(5)
            await self.dismiss_cookie_banner(tab)

            global_video_index = 0

            while time.time() < self.end_time:
                remaining_time = self.end_time - time.time()
                if remaining_time <= 0:
                    logger.info("LOOP_DURATION reached. Stopping browsing.")
                    break
                try:
                    # Get next video
                    video = await self.get_next_video(remaining_time)
                    if video is None:
                        continue
                    # Process the video
                    await self.process_video(tab, video, global_video_index, remaining_time)
                    global_video_index += 1
                except asyncio.TimeoutError:
                    logger.info("No new videos available.")
                    await asyncio.sleep(1)
                    continue
        except Exception as e:
            logger.error(f"Error in browse_fyp: {e}")
        finally:
            # After loop ends or in case of error, store the viewed data
            filename = f'{config.user_name}_{int(self.start_time)}__{int(time.time())}'
            await self.store_viewed_data(filename)
            logger.info("Collected viewed data stored.")

    async def get_next_video(self, remaining_time: float) -> Optional[Dict[str, Any]]:
        timeout = min(remaining_time, 60)
        try:
            video = await asyncio.wait_for(self.video_batches_queue.get(), timeout=timeout)
            return video
        except asyncio.TimeoutError:
            return None

    async def process_video(self, tab: Tab, video: Dict[str, Any], video_index: int, remaining_time: float) -> None:
        video_id = video.get("id", "Unknown ID")
        logger.info(f"Processing video {video_id} at index {video_index}")

        # Check if video has been viewed before
        if self.is_video_viewed(video_id):
            logger.info(f"Video {video_id} has been viewed before. Skipping.")
            await self.swipe_to_next_video(tab)
            return

        # Scroll to the video
        article_selector = f"article[data-index='{video_index}']"
        current_video_element = await tab.select(article_selector, timeout=60)
        if not current_video_element:
            logger.warning(f"No video found at index {video_index}")
            return

        await current_video_element.scroll_into_view()
        await asyncio.sleep(1)

        # Get the video element
        video_element = await current_video_element.query_selector("video")
        if not video_element:
            logger.warning("Video element not found.")
            return

        # Get currentTime and duration
        current_time = await get_video_current_time(tab)
        duration = get_video_duration(video)
        # Calculate time to watch
        time_to_watch = calculate_time_to_watch(duration, current_time, remaining_time)
        logger.info(f"Current Time: {current_time}, Duration: {duration}, Watching for: {time_to_watch} seconds")

        # Watch the video
        await asyncio.sleep(time_to_watch)
        # Collect the viewed video data
        self.viewed_videos.append(video)
        # Mark video as processed
        self.processed_video_ids.add(video_id)

        # Swipe up to the next video
        await self.swipe_to_next_video(tab)

    async def swipe_to_next_video(self, tab: Tab) -> None:
        await swipe(tab, 300, 700, 600, 'up')
        await asyncio.sleep(1)

    async def navigate(self, tab: Tab, page_url: str) -> None:
        page = await tab.get(page_url)
        if page_url in page.url:
            logger.info(f"Browsing: {page_url}")
        else:
            logger.info(f"Retry: {page.url} is not {page_url}")
            await tab.browser.update_targets()
            await page.reload()
            page = await tab.get(page_url)

    def is_video_viewed(self, video_id: str) -> bool:
        return video_id in self.processed_video_ids

    def load_processed_video_ids(self) -> None:
        try:
            filepath = os.path.join(config.scenario_name, 'processed_video_ids.json')
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    self.processed_video_ids = set(json.load(f))
                logger.info(f"Loaded {len(self.processed_video_ids)} processed video IDs.")
            else:
                logger.info("No processed video IDs file found.")
        except Exception as e:
            logger.error(f"Error loading processed video IDs: {e}")
            self.processed_video_ids = set()

    def save_processed_video_ids(self) -> None:
        try:
            filepath = os.path.join(config.storage_path, 'processed_video_ids.json')
            with open(filepath, 'w') as f:
                json.dump(list(self.processed_video_ids), f)
            logger.info(f"Saved {len(self.processed_video_ids)} processed video IDs.")
        except Exception as e:
            logger.error(f"Error saving processed video IDs: {e}")

    async def dismiss_cookie_banner(self, tab: Tab) -> None:
        cookie_banner = await tab.find('tiktok-cookie-banner')
        if cookie_banner:
            await tap_on_element(tab, 270, 710)
            logger.info("Dismissed cookie banner")

    async def store_viewed_data(self, filename: str) -> None:
        df = pd.DataFrame(self.viewed_videos)
        os.makedirs(config.storage_path, exist_ok=True)
        filepath = os.path.join(config.storage_path, f"{filename}.parquet")
        df.to_parquet(filepath)
        logger.info(f"Collected viewed data stored to: {filepath}")
        self.save_processed_video_ids()
