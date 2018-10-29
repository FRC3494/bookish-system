import asyncio
import cv_processing
from camera_opencv import Camera
import os
from flask import Flask, redirect, render_template, Response, send_from_directory
from disc import d as discerd

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


def gen(c):
    while True:
        d_frame = cv_processing.draw_debugs_jpegs(c.get_frame()[1])
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + d_frame + b"\r\n")


@app.route("/video_feed")
def feed():
    """Streaming route (img src)"""
    # g = cv_processing.gen_debugs_responses(Camera.frames()[1])
    return Response(gen(Camera()), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, "static"), "favicon.ico")


@app.template_filter()
def int_to_hexcolor(i) -> str:
    return "#" + (hex(i)[2:] if i != 0 else "FFFFFF")


@app.route("/d_test")
def discord_test():
    barcodes = cv_processing.scan_barcodes(Camera().get_frame()[1])
    if barcodes is not None and len(barcodes) >= 1:
        d_id = barcodes[0].data.decode("utf-8")
        user = discerd.get_guild_member(286174293006745601, d_id)
        r = [discerd.get_guild_role(286174293006745601, role) for role in user["roles"]]
        return render_template(
            "discord.html",
            nick=user["nick"],
            username=user["user"]["username"],
            discrim=user["user"]["discriminator"],
            roles=r,
            pfp=discerd.get_pfp_url(d_id),
        )
    else:
        return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0")
