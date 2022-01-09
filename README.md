# PagerDuty Event Handler
This repo contains source code and a Docker Compose environment for a middleware PagerDuty Event Handler.  
It allows organisations to send alert/event data into PagerDuty with the following capabilities:
* Rate limit queuing to ensure events are not being dropped due to API rate limits
* Horizontal scaling of PagerDuty event routing keys to support higher event ingestion rates

We strongly recommend that this application be used with meaningful alert data [(see PD-CEF)](https://support.pagerduty.com/docs/pd-cef), rather than sending noisy/unhelpful alert data structures. 

## Disclaimer

> **:warning: This open-source solution is not officially supported by PagerDuty - please use this at your own risk.  
> PagerDuty also reserves the right to suspend accounts per [ToS](https://www.pagerduty.com/terms-of-service/) where appropriate.**

## Contents
* [Solution Architecture](#solution-architecture)
* [Prerequisites](#prerequisites)
* [Setup](#setup)
* [Deployment](#deployment)
* [License](#license)

## Solution Architecture

![PagerDuty Event Handler - Architecture](https://user-images.githubusercontent.com/20474443/148664005-a66c35d0-54fb-4087-9a0d-2b149163f181.png)

## Prerequisites

#### PagerDuty

- Access to a domain: https://www.pagerduty.com/sign-up/
- Valid event routing keys [(Global Rulesets preferred)](https://support.pagerduty.com/docs/rulesets#section-global-rulesets)

#### Docker Compose

- Docker Desktop: https://docs.docker.com/get-docker/
- Compose: https://docs.docker.com/compose/install/
- The machine hosting Docker should be accessible over TCP Port `8080` for incoming monitoring alerts

## Setup

1. Clone repo (via SSH) into appropriate location and enter directory.

    ```bash
    $ git clone git@github.com:giranm/pd-event-handler.git
    ```

    ```bash
    $ cd pd-event-handler
    ```
   
2. Update `flask/pd_routing_keys.txt` with valid PagerDuty event routing keys; at least 1 is required.
    > NB: If using Global Ruleset keys, please ensure consistent [event rules](https://support.pagerduty.com/docs/rulesets#create-event-rules) have been configured/replicated

   ```bash
   $ cat flask/pd_routing_keys.txt
   ```
   ```
   R0*********REDACTED************0
   R0*********REDACTED************2
   ```

   
3. Build Docker image for Flask application via `docker-compose`

   ```bash
   $ docker-compose build
   ```
   ```     
    nginx uses an image, skipping
    Building flask
    [+] Building 11.7s (10/10) FINISHED                                                                                 
     => [internal] load build definition from Dockerfile                                                           0.0s
     => => transferring dockerfile: 203B                                                                           0.0s
     => [internal] load .dockerignore                                                                              0.0s
     => => transferring context: 2B                                                                                0.0s
     => [internal] load metadata for docker.io/library/python:3.7-alpine3.14                                       1.4s
     => [1/5] FROM docker.io/library/python:3.7-alpine3.14@sha256:a111a535393420437b3641a734ef94bda66805e70424303  3.2s
     => => resolve docker.io/library/python:3.7-alpine3.14@sha256:a111a535393420437b3641a734ef94bda66805e70424303  0.0s
     => => sha256:a111a535393420437b3641a734ef94bda66805e70424303d61302b4b1c23c371 1.65kB / 1.65kB                 0.0s
     => => sha256:feafb9716a22e3ff6ec6d395b718e199c23cb781f9eab57b2dffe6c7484b2290 1.37kB / 1.37kB                 0.0s
     => => sha256:f0c1a69798c72da2158634b7133f6cc6fd9f569f5fc8591d2117ce6a6f745364 8.10kB / 8.10kB                 0.0s
     => => sha256:97518928ae5f3d52d4164b314a7e73654eb686ecd8aafa0b79acd980773a740d 2.82MB / 2.82MB                 0.5s
     => => sha256:8f1c01f59fcc7f7c93b7819b80102de4622e5b448ebf68120a07bc88366cc08a 281.96kB / 281.96kB             0.7s
     => => sha256:464d4fea566338069e77ee2a8d393d2bd5b3aa0a603031b9e486745b03bb6683 10.58MB / 10.58MB               2.0s
     => => extracting sha256:97518928ae5f3d52d4164b314a7e73654eb686ecd8aafa0b79acd980773a740d                      0.2s
     => => sha256:cc898d47eef320ac619094e3a9e88f8d7d453a69658756fd21e31b59678a6161 229B / 229B                     0.9s
     => => extracting sha256:8f1c01f59fcc7f7c93b7819b80102de4622e5b448ebf68120a07bc88366cc08a                      0.1s
     => => sha256:07c63eb0033be3783382a2bd43503b60f18ad87c147322a72fab1922adf75370 2.35MB / 2.35MB                 1.9s
     => => extracting sha256:464d4fea566338069e77ee2a8d393d2bd5b3aa0a603031b9e486745b03bb6683                      0.6s
     => => extracting sha256:cc898d47eef320ac619094e3a9e88f8d7d453a69658756fd21e31b59678a6161                      0.0s
     => => extracting sha256:07c63eb0033be3783382a2bd43503b60f18ad87c147322a72fab1922adf75370                      0.3s
     => [internal] load build context                                                                              0.0s
     => => transferring context: 6.64kB                                                                            0.0s
     => [2/5] WORKDIR /opt                                                                                         0.3s
     => [3/5] COPY requirements.txt ./                                                                             0.0s
     => [4/5] COPY app.py ./                                                                                       0.0s
     => [5/5] RUN pip install --no-cache-dir -r requirements.txt                                                   6.4s
     => exporting to image                                                                                         0.3s
     => => exporting layers                                                                                        0.3s
     => => writing image sha256:7e45c58d7bf528c17beb4675fb414959e356f89433c4618bcc648375d88f1e10                   0.0s
     => => naming to docker.io/library/pd-event-handler_flask
   ```
   
4. Update monitoring tools to send alerts/events via Webhook to the host machine via `http://HOST_HERE:8080`  
The alert JSON structure should ideally conform to [PagerDuty's Common Event Format (PD-CEF)](https://support.pagerduty.com/docs/pd-cef).
   
## Deployment

Once you have set up the environment above, you can use the helper script `start.sh` to bootstrap the environment. This will also pull the [NGINX](https://www.nginx.com/resources/glossary/nginx/) Docker image if it's not available locally.

> NB: Ensure the right volume is mounted for the Flask service under `docker-compose.yaml` (OS Dependent)

### Start Event Handler

`start.sh` will verify the number of routing keys available and generate the relevant NGINX configuration.  
It also deploys the relevant Docker containers and provides an entrypoint on `localhost:8080` to accept incoming events.
```bash
$ ./start.sh
```

```
Creating network "pd-event-handler_default" with the default driver
Pulling nginx (nginx:1.20-alpine)...
1.20-alpine: Pulling from library/nginx
97518928ae5f: Already exists
a15dfa83ed30: Pull complete
acae0b19bbc1: Pull complete
fd4282442678: Pull complete
b521ea0d9e3f: Pull complete
b3282d03aa58: Pull complete
Digest: sha256:74694f2de64c44787a81f0554aa45b281e468c0c58b8665fafceda624d31e556
Status: Downloaded newer image for nginx:1.20-alpine
Creating pd-event-handler_flask_1 ... done
Creating pd-event-handler_flask_2 ... done
```

If `flask/pd_routing_keys.txt` is not populated, the script will exit with the following message:
```
No routing keys detected under flask/pd_routing_keys.txt - terminating script
```

### Verify Status of Event Handler

The following Docker commands can be used to check the status of the event handler:
- `$ docker ps -a`
- `$ docker logs <container name>`
- `$ docker stats`

#### Example: `$ docker ps -a`

```
CONTAINER ID   IMAGE                    COMMAND                  CREATED          STATUS          PORTS                                               NAMES
47174793f685   nginx:1.20-alpine        "/docker-entrypoint.…"   37 minutes ago   Up 37 minutes   80/tcp, 0.0.0.0:8080->8080/tcp, :::8080->8080/tcp   nginx
d8301cdf2272   pd-event-handler_flask   "python app.py"          37 minutes ago   Up 37 minutes   5000/tcp                                            pd-event-handler_flask_1
b1df3b666bd0   pd-event-handler_flask   "python app.py"          37 minutes ago   Up 37 minutes   5000/tcp                                            pd-event-handler_flask_2
```

Failed containers will exit, such as an invalid routing key provided for the Flask application:
```
CONTAINER ID   IMAGE                    COMMAND                  CREATED          STATUS                      PORTS      NAMES
ce9b02632506   pd-event-handler_flask   "python app.py"          38 seconds ago   Exited (1) 37 seconds ago   5000/tcp   pd-event-handler_flask_1
```

#### Example: `$ docker logs nginx`

Initialisation:
```
/docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will attempt to perform configuration
/docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/
/docker-entrypoint.sh: Launching /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh
10-listen-on-ipv6-by-default.sh: info: Getting the checksum of /etc/nginx/conf.d/default.conf
10-listen-on-ipv6-by-default.sh: info: Enabled listen on IPv6 in /etc/nginx/conf.d/default.conf
/docker-entrypoint.sh: Launching /docker-entrypoint.d/20-envsubst-on-templates.sh
/docker-entrypoint.sh: Launching /docker-entrypoint.d/30-tune-worker-processes.sh
/docker-entrypoint.sh: Configuration complete; ready for start up
```

Processed alert:
```
192.168.144.1 - - [08/Jan/2022:19:20:45 +0000] "POST / HTTP/1.1" 202 308 "-" "PostmanRuntime/7.28.4"
```

Upstream Flask container offline/unreachable; event routed to next available container: 
```
2022/01/09 19:08:41 [error] 33#33: *2 connect() failed (113: Host is unreachable) while connecting to upstream, client: 192.168.160.1, server: , request: "POST / HTTP/1.1", upstream: "http://192.168.160.3:5000/", host: "localhost:8080"
192.168.160.1 - - [09/Jan/2022:19:08:41 +0000] "POST / HTTP/1.1" 202 308 "-" "PostmanRuntime/7.28.4"
```

#### Example: `$ docker logs pd-event-handler_flask_1`

Initialisation:
```
2022-01-08T18:37:50.249805+00:00 | INFO | app | Running on container pd-event-handler_flask_1 (ID: d8301cdf2272)
2022-01-08T18:37:50.253252+00:00 | INFO | app | Using Routing Key: R0*********REDACTED************0
2022-01-08T18:37:51.078887+00:00 | INFO | app | Routing key verified
2022-01-08T18:37:51.081539+00:00 | INFO | app | Queue is empty - currently awaiting requests
2022-01-08T18:37:51.125738+00:00 | INFO | wasyncore | Serving on http://0.0.0.0:5000
```

Processed alert:
```
2022-01-08T19:20:45.460663+00:00 | INFO | app | Enqueued event: {'payload': {'summary': 'Server ldn-p3476z offline', 'severity': 'critical', 'component': 'ldn-p3476z', 'source': 'Elastic', 'group': 'london', 'class': 'alert', 'custom_details': {'health': '0'}}, 'dedup_key': '', 'event_action': 'trigger'}
2022-01-08T19:20:45.461489+00:00 | INFO | app | Current queue size: 1
2022-01-08T19:20:45.461843+00:00 | INFO | app | Sending PD event: {'payload': {'summary': 'Server ldn-p3476z offline', 'severity': 'critical', 'component': 'ldn-p3476z', 'source': 'Elastic', 'group': 'london', 'class': 'alert', 'custom_details': {'health': '0'}}, 'dedup_key': '', 'event_action': 'trigger', 'routing_key': 'R0*********REDACTED************0'}
2022-01-08T19:20:46.267280+00:00 | INFO | app | PD server response: {'status': 'success', 'message': 'Event processed', 'dedup_key': 'f9d383d1282c4987b5ea0e8830d862da'}
2022-01-08T19:20:46.267463+00:00 | INFO | app | Queue is empty - currently awaiting requests
```

Invalid routing key:
```
2022-01-09T18:59:55.249805+00:00 | INFO | app | Running on container pd-event-handler_flask_1 (ID: ce9b02632506)
2022-01-09T18:59:55.253252+00:00 | INFO | app | Using Routing Key: INVALID_KEY
2022-01-09T18:59:56.194389+00:00 | CRITICAL | app | Invalid routing key provided - terminating server
```

In the unlikely case of a race condition/API limit reached, the failed event will be put back to the queue to be redispatched once the API becomes available:
```
2022-01-09T19:18:58.491274+00:00 | INFO | app | Current queue size: 22
2022-01-09T19:18:58.491340+00:00 | INFO | app | Sending PD event: {'payload': {'summary': 'Server ldn-p3476z offline', 'severity': 'critical', 'component': 'ldn-p3476z', 'source': 'Elastic', 'group': 'london', 'class': 'alert', 'custom_details': {'health': '0'}}, 'dedup_key': '', 'event_action': 'trigger', 'routing_key': 'R02ERJS86INW82CV5KOAPRNFA0YLSOA0'}
2022-01-09T19:18:58.674458+00:00 | WARNING | app | Unable to process request - pushing to the back of the queue
```

#### Example: `$ docker stats`
This is an interactive shell command which shows live stats of your Docker runtime.
> High CPU (~100%) is expected behaviour for *idle* Flask instances; this drops when events are being processed.

```
CONTAINER ID   NAME                       CPU %     MEM USAGE / LIMIT    MEM %     NET I/O           BLOCK I/O     PIDS
47174793f685   nginx                      0.00%     6.395MiB / 11.7GiB   0.05%     3.59kB / 2.25kB   0B / 8.19kB   9
d8301cdf2272   pd-event-handler_flask_1   100.50%   23.25MiB / 11.7GiB   0.19%     6.76kB / 2kB      0B / 0B       6
b1df3b666bd0   pd-event-handler_flask_2   100.70%   23.73MiB / 11.7GiB   0.20%     12.7kB / 5kB      0B / 0B       6
```

### Stop Event Handler

```bash
$ docker-compose down
```

```
Stopping nginx                    ... done
Stopping pd-event-handler_flask_1 ... done
Stopping pd-event-handler_flask_2 ... done
Removing nginx                    ... done
Removing pd-event-handler_flask_1 ... done
Removing pd-event-handler_flask_2 ... done
Removing network pd-event-handler_default
```

No containers should be running (see below output)
```bash
$ docker ps -a
```

```
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

## License
```
MIT License

Copyright (c) 2022 Giran Moodley

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```