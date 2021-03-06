#!/usr/bin/env bash

# Verify if routing keys have been populated
NUM_ROUTING_KEYS="$(grep -c ^ flask/pd_routing_keys.txt)"
if [ "${NUM_ROUTING_KEYS}" -eq 0 ]
then
    echo "No routing keys detected under flask/pd_routing_keys.txt - terminating script"
    exit 1
fi

# Dynamically populate NGINX config with assumed number of hosts (aka routing keys)
SERVER_LIST=$(for ((i=1; i<="${NUM_ROUTING_KEYS}"; i++))
do
   echo \
"        server pd-event-handler_flask_$i:5000 fail_timeout=600s;"
done)

cat <<EOF > nginx/nginx.conf
# This file is automatically generated from start.sh
worker_processes 8;

events { worker_connections 1024; }

http {
    upstream flask {
${SERVER_LIST}
    }
    server {
        listen 8080;
        location / {
            proxy_pass          http://flask;
            proxy_set_header    X-Forwarded-Proto \$scheme;
            proxy_set_header    X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header    X-Forwarded-Host \$host:\$server_port;
            proxy_set_header    X-Forwarded-Port \$server_port;
            proxy_redirect      off;
        }
    }
}
EOF

# Start Docker environment
docker-compose up -d --scale flask="${NUM_ROUTING_KEYS}"