# event_handlers.py
import asyncio
import base64
import json
import logging
from typing import Any
from nodriver import cdp, Tab

logger = logging.getLogger(__name__)

class EventHandlers:
    def __init__(self, context: Any) -> None:
        self.context = context

    async def auth_challenge_handler(self, event: cdp.fetch.AuthRequired, connection: Tab) -> None:
        logger.debug("Auth challenge handler called")
        username = self.context.config.proxy.get('username')
        password = self.context.config.proxy.get('password')
        await connection.send(
            cdp.fetch.continue_with_auth(
                request_id=event.request_id,
                auth_challenge_response=cdp.fetch.AuthChallengeResponse(
                    response="ProvideCredentials",
                    username=username,
                    password=password,
                ),
            )
        )

    async def req_paused(self, event: cdp.fetch.RequestPaused, connection: Tab) -> None:
        logger.debug(f"Request paused with request ID: {event.request_id}.")
        # Continue with the request
        await connection.send(cdp.fetch.continue_request(request_id=event.request_id))

    async def response_received_handler(self, event: cdp.network.ResponseReceived, connection: Tab) -> None:
        url = event.response.url
        request_id = event.request_id
        if url.startswith(self.context.TARGET_ENDPOINT):
            if request_id in self.context.processed_request_ids:
                logger.info(f"Already processed request ID: {request_id}, skipping.")
                return
            self.context.pending_request_ids.add(request_id)
            logger.info(f"Added request ID to pending: {request_id}")

    async def loading_finished_handler(self, event: cdp.network.LoadingFinished, connection: Tab) -> None:
        request_id = event.request_id
        if request_id in self.context.pending_request_ids:
            logger.info(f"Loading finished for request ID: {request_id}")
            self.context.pending_request_ids.remove(request_id)
            self.context.processed_request_ids.add(request_id)
            asyncio.create_task(self.handle_response(request_id, connection))

    async def handle_response(self, request_id: cdp.network.RequestId, connection: Tab) -> None:
        logger.info(f"Handling response for request ID: {request_id}")
        try:
            response = await connection.send(cdp.network.get_response_body(request_id=request_id))
            if response is None:
                logger.error(f"Failed to retrieve response body; received None for request ID: {request_id}")
                return
            body, is_base64_encoded = response
            if is_base64_encoded:
                body = base64.b64decode(body)
            else:
                body = body.encode('utf-8')
            json_data = body.decode('utf-8')

            # Parse the JSON data
            data = json.loads(json_data)
            if "itemList" in data:
                videos = data["itemList"]
                logger.info(f"Number of videos in response: {len(videos)}")
            else:
                logger.info("No videos found in the JSON data.")
                return

            # Add new videos to the queue
            for video in videos:
                await self.context.video_batches_queue.put(video)
        except Exception as e:
            logger.error(f"Error in handle_response: {e}")


    async def add_proxy_user_authorization(self, tab: Tab) -> None:
        if self.context.config.proxy and self.context.config.proxy.get('username'):
            logger.info(f"Setup proxy: {self.context.config.proxy}")
            # Add handlers for fetch events
            tab.add_handler(
                cdp.fetch.RequestPaused, lambda event: asyncio.create_task(self.req_paused(event, tab))
            )
            tab.add_handler(
                cdp.fetch.AuthRequired,
                lambda event: asyncio.create_task(self.auth_challenge_handler(event, tab)),
            )
            await tab.send(cdp.fetch.enable(handle_auth_requests=True))

    def recommendation_request_tracking(self, tab: Tab) -> None:
        tab.add_handler(cdp.network.ResponseReceived, self.response_received_handler)
        tab.add_handler(cdp.network.LoadingFinished, self.loading_finished_handler)

    async def add_network_handles(self, tab:Tab) -> None:
        """This functions should add network handling of requests, like proxy and recommendations"""
        self.recommendation_request_tracking(tab)
        await self.add_proxy_user_authorization(tab)