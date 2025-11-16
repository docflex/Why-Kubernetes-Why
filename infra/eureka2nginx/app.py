import requests
import time
import os

EUREKA_URL = os.getenv("EUREKA_URL", "http://host.docker.internal:8761/eureka/apps")
NGINX_CONF_DIR = "/etc/nginx/conf.d"
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "10"))

def generate_upstream(app_name, instances):
    upstream = "\n".join([
        f"    server {i['ipAddr']}:{i['port']['$']};" for i in instances
    ])
    return f"upstream {app_name.lower()} {{\n{upstream}\n}}\n"


def generate_location_block(app_name, instances):
    app = app_name.lower()
    return f"""
location /{app}/ {{
    rewrite ^/{app}/?(.*)$ /$1 break;
    proxy_pass http://{app};  # <-- use upstream!
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}}
""".strip()


def refresh_nginx_config():
    """Poll Eureka and update NGINX location fragments."""
    try:
        headers = {"Accept": "application/json"}
        response = requests.get(EUREKA_URL, headers=headers)
        response.raise_for_status()
        payload = response.json()

        apps = payload.get("applications", {}).get("application", [])
        if not isinstance(apps, list):
            apps = [apps]

        for app in apps:
            app_name = app["name"].lower()
            instances = app.get("instance", [])
            if not isinstance(instances, list):
                instances = [instances]
            instances = [i for i in instances if i.get("status") == "UP"]
            if not isinstance(instances, list):
                instances = [instances]

            upstream_path = f"{NGINX_CONF_DIR}/upstreams/{app_name}.conf"
            location_path = f"{NGINX_CONF_DIR}/servers/{app_name}.conf"

            os.makedirs(os.path.dirname(upstream_path), exist_ok=True)
            os.makedirs(os.path.dirname(location_path), exist_ok=True)

            with open(upstream_path, "w") as f:
                f.write(generate_upstream(app_name, instances))
            with open(location_path, "w") as f:
                f.write(generate_location_block(app_name, instances))

            print(f"[INFO] Updated {upstream_path} and {location_path}", flush=True)

    except Exception as e:
        print(f"[WARN] Failed to refresh NGINX config: {e}", flush=True)

if __name__ == "__main__":
    print(f"[INFO] Polling {EUREKA_URL} every {POLL_INTERVAL}s", flush=True)
    while True:
        refresh_nginx_config()
        time.sleep(POLL_INTERVAL)
