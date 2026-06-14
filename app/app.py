import os
import socket

import redis
from flask import Flask, render_template

app = Flask(__name__)

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    decode_responses=True,
)


@app.route("/")
def index():
    count = r.incr("visits")
    return render_template(
        "index.html",
        count=count,
        hostname=socket.gethostname(),
        app_name=os.getenv("APP_NAME", "Portainer Lab"),
    )


@app.route("/reset", methods=["POST"])
def reset():
    r.set("visits", 0)
    return {"status": "ok", "visits": 0}


@app.route("/health")
def health():
    try:
        r.ping()
        return {"status": "ok"}, 200
    except redis.RedisError as exc:
        return {"status": "error", "detail": str(exc)}, 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
