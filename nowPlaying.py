import gi
import asyncio
import websockets
import json
import threading
import tornado
import yaml
import re
import urllib.parse
import mimetypes
import time

gi.require_version("Playerctl", "2.0")
from gi.repository import Playerctl, GLib  # type: ignore

manager = Playerctl.PlayerManager()

connections = set()

with open("./widget.html", "r") as file:
    html = file.read()
with open("./config.yml", "r") as file:
    config = yaml.safe_load(file)

artMarginDirections = {
    "row": "right",
    "row-reverse": "left",
    "column": "bottom",
    "column-reverse": "top",
}

htmlPlaceholders = {
    "PLACEHOLDER_widgetBackground": config["widgetBackground"],
    "PLACEHOLDER_widgetPadding": config["widgetPadding"],
    "PLACEHOLDER_widgetRadius": config["widgetRadius"],
    "PLACEHOLDER_layout": config["layout"],
    "PLACEHOLDER_artWidth": config["artWidth"],
    "PLACEHOLDER_artHeight": config["artHeight"],
    "PLACEHOLDER_artRadius": config["artRadius"],
    "PLACEHOLDER_artMarginDirection": artMarginDirections[config["layout"]],
    "PLACEHOLDER_artMargin": config["artMargin"],
    "PLACEHOLDER_font": config["font"],
    "PLACEHOLDER_textAlign": config["textAlign"],
    "PLACEHOLDER_titleColor": config["titleColor"],
    "PLACEHOLDER_titleSize": config["titleSize"],
    "PLACEHOLDER_titleWeight": config["titleWeight"],
    "PLACEHOLDER_artistColor": config["artistColor"],
    "PLACEHOLDER_artistSize": config["artistSize"],
    "PLACEHOLDER_artistWeight": config["artistWeight"],
}
if " " in htmlPlaceholders["PLACEHOLDER_font"] and not (
    "'" in htmlPlaceholders["PLACEHOLDER_font"]
    or '"' in htmlPlaceholders["PLACEHOLDER_font"]
):
    htmlPlaceholders["PLACEHOLDER_font"] = '"{}"'.format(
        htmlPlaceholders["PLACEHOLDER_font"]
    )

htmlReplacePattern = re.compile(
    "|".join(re.escape(key) for key in htmlPlaceholders.keys())
)
html = htmlReplacePattern.sub(lambda match: htmlPlaceholders[match.group(0)], html)

art_path = ""


def send_useful_metadata(metadata):
    global art_path

    useful_metadata = {
        "title": metadata["xesam:title"],
        "artist": ", ".join(metadata["xesam:artist"]),
    }
    if (
        (not "mpris:artUrl" in metadata.keys())
        or metadata["mpris:artUrl"] == ""
        or metadata["mpris:artUrl"].startswith("file://")
    ):
        useful_metadata["artUrl"] = "/art?" + str(time.time())
        if not "mpris:artUrl" in metadata.keys() or metadata["mpris:artUrl"] == "":
            art_path = config["defaultArt"]
        else:
            art_path = urllib.parse.unquote(metadata["mpris:artUrl"]).removeprefix(
                "file://"
            )
    else:
        useful_metadata["artUrl"] = metadata["mpris:artUrl"]
    websockets.broadcast(
        connections,
        json.dumps(
            useful_metadata,
        ),
    )


def on_metadata(player, metadata, manager):
    send_useful_metadata(metadata)


def init_player(name):
    if name.name != config["player"]:
        return
    player = Playerctl.Player.new_from_name(name)
    player.connect("metadata", on_metadata, manager)
    send_useful_metadata(player.props.metadata)
    manager.manage_player(player)


def on_name_appeared(manager, name):
    init_player(name)


async def register_websocket(websocket):
    connections.add(websocket)
    if len(manager.props.players) > 0:
        send_useful_metadata(manager.props.players[0].props.metadata)
    try:
        await websocket.wait_closed()
    finally:
        connections.remove(websocket)


async def start_websocket_server():
    async with websockets.serve(
        register_websocket, "localhost", config["websocketServerPort"]
    ):
        await asyncio.Future()  # run forever


class WebServerHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(html)


class WebServerArtHandler(tornado.web.RequestHandler):

    def get(self):
        content_type, _ = mimetypes.guess_type(art_path)
        self.add_header("Content-Type", content_type)
        with open(art_path, "rb") as file:
            self.write(file.read())


def make_web_server():
    return tornado.web.Application(
        [
            (r"/", WebServerHandler),
            (
                r"/art",
                WebServerArtHandler,
            ),
        ]
    )


async def start_web_server():
    web_server = make_web_server()
    web_server.listen(config["webServerPort"])
    print("Web server running at http://localhost:{}".format(config["webServerPort"]))
    await asyncio.Event().wait()


async def main():
    manager.connect("name-appeared", on_name_appeared)
    for name in manager.props.player_names:
        init_player(name)

    loop = GLib.MainLoop()
    glib_thread = threading.Thread(target=loop.run)
    glib_thread.start()

    try:
        await asyncio.gather(start_websocket_server(), start_web_server())
    except asyncio.exceptions.CancelledError:
        print("\nStopping")
        loop.quit()
        glib_thread.join()


if __name__ == "__main__":
    asyncio.run(main())
