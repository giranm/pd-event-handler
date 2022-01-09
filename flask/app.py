#!/usr/bin/env python3
import sys
import os
import csv
import threading
import logging
import json
import datetime

import requests
import requests_unixsocket
import ratelimitqueue
from flask import Flask, request, jsonify
from waitress import serve

# Global constants
PD_EVENTS_API = "https://events.pagerduty.com/v2/enqueue"
PD_RATE_LIMIT_CALLS_PER_MINUTE = 120

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(module)s | %(message)s"
)
logging.Formatter.formatTime = (
    lambda self, record, datefmt: datetime.datetime.fromtimestamp(
        record.created, datetime.timezone.utc
    )
    .astimezone()
    .isoformat()
)


class PDEventHandler:
    def __init__(self):
        self.logger = logging.getLogger()
        self.hostname = os.environ.get("HOSTNAME")
        self.container_idx = 1
        self.routing_key = ""
        self.session = requests.Session()
        self.rlq = ratelimitqueue.RateLimitQueue(
            calls=PD_RATE_LIMIT_CALLS_PER_MINUTE, per=60
        )
        self.rlq_thread = threading.Thread(
            name="ratelimitqueue", target=self.__process_queue
        )

        # Additional initialisation routines
        self.__get_container_index()
        self.__assign_routing_key()
        self.__verify_routing_key()

    # Identify container hostname index based on Docker API (via mounted socket)
    def __get_container_index(self):
        with requests_unixsocket.Session() as session:
            try:
                res = session.get(
                    f"http+unix://%2Frun%2Fdocker.sock/containers/{self.hostname}/json"
                )
                res_json = res.json()
                container_name = res_json["Name"]
                container_id = res_json["Config"]["Hostname"]
                self.container_idx = int(
                    container_name.split("/pd-event-handler_flask_")[1]
                )
                self.logger.info(
                    "Running on container pd-event-handler_flask_%s (ID: %s)",
                    self.container_idx,
                    container_id,
                )
            except (KeyError, requests.exceptions.ConnectionError):
                # This occurs when container can't be found or if running script on local dev machine
                self.logger.warning(
                    "Unable to determine container name - defaulting to first routing key available"
                )
                self.container_idx = 1

    # Dynamically get routing key from file depending on index of container
    def __assign_routing_key(self):
        with open("pd_routing_keys.txt", "r") as file:
            reader = csv.reader(file)
            routing_keys = [row[0] for row in reader]
            try:
                self.routing_key = routing_keys[self.container_idx - 1]
                self.logger.info("Using Routing Key: %s", self.routing_key)
            except IndexError:
                self.logger.critical("Routing key unavailable - terminating server")
                sys.exit(1)

    # Verify if PD routing key is valid via dummy resolve message; exit application if invalid
    def __verify_routing_key(self):
        try:
            res = self.session.post(
                url=PD_EVENTS_API,
                json={
                    "routing_key": self.routing_key,
                    "dedup_key": "pd_event_handler",
                    "event_action": "resolve",
                },
            )
            if res.status_code != 202:
                raise RuntimeError()
            else:
                self.logger.info("Routing key verified")
        except RuntimeError:
            self.logger.critical("Invalid routing key provided - terminating server")
            sys.exit(1)

    # Function to send queued events via PD Events v2 API
    def __pd_send_event(self, pd_event_data):
        # Take existing payload and dynamically update the correct routing key
        pd_event_data["routing_key"] = self.routing_key
        self.logger.info("Sending PD event: %s", pd_event_data)

        # Attempt sending event to PD; failed requests will be sent back to top of queue
        res = None
        try:
            res = self.session.post(url=PD_EVENTS_API, json=pd_event_data)
            self.logger.info("PD server response: %s", res.json())
        except json.decoder.JSONDecodeError:
            self.logger.warning(
                "Unable to process request (Events API Status Code: %s) - pushing to the back of the queue",
                res.status_code,
            )
            self.rlq.put(pd_event_data)

    # Internal function to handle RLQ using background thread
    def __process_queue(self):
        awaiting_requests = True
        while True:
            # Process non-empty queue
            if self.rlq.qsize() > 0:
                self.logger.info("Current queue size: %s", self.rlq.qsize())

                pd_event_data = self.rlq.get()
                self.__pd_send_event(pd_event_data)

                awaiting_requests = True
                self.rlq.task_done()

            # Handle when queue is empty
            elif self.rlq.qsize() == 0:
                self.logger.info(
                    "Queue is empty - currently awaiting requests"
                ) if awaiting_requests else None
                awaiting_requests = False

    # Handler entrypoint
    def start(self):
        # Initialise Flask server
        app = Flask(__name__)

        # Default route for enqueuing requests
        @app.route("/", methods=["POST"])
        def __enqueue_request():
            pd_event_data = request.get_json()
            self.rlq.put(pd_event_data)
            self.logger.info("Enqueued event: %s", pd_event_data)
            return (
                jsonify(
                    {
                        "status": "enqueued",
                        "data": pd_event_data,
                        "target_routing_key": self.routing_key,
                    },
                ),
                202,
            )

        # Start RLQ and Flask server (under WSGI framework)
        self.rlq_thread.start()
        serve(app, host="0.0.0.0", port=5000)


# Application entrypoint
if __name__ == "__main__":
    pd_event_handler = PDEventHandler()
    pd_event_handler.start()
