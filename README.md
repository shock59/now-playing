# now-playing

now-playing is a Python script for Linux systems which displays the name, artist and album artwork of the track which is currently playing in OBS Studio or anywhere else where you can embed a web page. It is fairly customisable using the config.yml file.

## Installation

You will need Python 3 installed, as well as packages PyGObject, PyYAML, Tornado, and websockets. PyGObject should be installed using the [official instructions](https://pygobject.gnome.org/getting_started.html) for your Distro. On most distros you will be able to install the other packages by running `pip install pyyaml tornado websockets` in the terminal, but some distros such as Arch Linux may require you to install them from the system package manager. You will also need Playerctl which is available in the package managers for most distros and also provides .deb and .rpm files on [GitHub Releases](https://github.com/altdesktop/playerctl/releases/latest).

Download the latest version of now-playing using `git clone https://github.com/shock59/now-playing` and use `cd now-playing` to enter the directory.

## Usage

The default player is Spotify so if you are using that then it should work out of the box, but if you are using a different media player you will have to set it in config.yml. Make sure your media player is running and run `playerctl --list-all` to find the name of the player. Replace `spotify` with the correct player name in config.yml.

To run now-playing use `python3 nowPlaying.py` when in the now-playing directory. To display the widget in OBS, add a Browser source with the URL `http://localhost:4640/`. (Some Linux distros don't include the Browser source feature in OBS, you can look for a fix for this or install the official [Flatpak](https://flathub.org/apps/com.obsproject.Studio) which works on all distros and includes the Browser.) When using the default configuration, the source's height should be 64. To stop the program press Ctrl+C in the terminal window.

## Configuration

There are many configuration options which can all be set in config.yml. If you change any of them while the program is running you will need to restart it and refresh the Browser source in OBS.

|                    Option | Description                                                                                                                                                                 |
| ------------------------: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|              **`player`** | The media player you want to use                                                                                                                                            |
|       **`webServerPort`** | Port the web server will run on (the number after `localhost:` in the URL)                                                                                                  |
| **`websocketServerPort`** | Port the websocket server will run on                                                                                                                                       |
|    **`widgetBackground`** | Background for the widget, can be a colour name, hex code or anything else which can be a background in CSS                                                                 |
|        **`widgetRadius`** | Radius for rounded corners on the widget                                                                                                                                    |
|       **`widgetPadding`** | Amount of padding for the widget (empty space between the edge of the widget and the content)                                                                               |
|              **`layour`** | The layout of the widget, can be `row` (art to the left of text), `row-reverse` (art to the right of text), `column` (art above text), or `column-reverse` (art below text) |
|          **`defaultArt`** | Path to the image which will display if there is no album art for the current track                                                                                         |
|            **`artWidth`** | Width of the album art                                                                                                                                                      |
|           **`artHeight`** | Height of the album art                                                                                                                                                     |
|           **`artRadius`** | Radius for rounded corners on the album art                                                                                                                                 |
|           **`artMargin`** | Amount of empty space between the album art and the text                                                                                                                    |
|                **`font`** | Font name for the text in the widget                                                                                                                                        |
|           **`textAlign`** | Alignment for the text, can be `start`, `center`, or `end`                                                                                                                  |
|           **`titleSize`** | Font size for the track title                                                                                                                                               |
|          **`titleColor`** | Colour for the track title, can be a colour name, hex code or anything else which can be a text colour in CSS                                                               |
|         **`titleWeight`** | Font weight for the track title, can be `normal`, `bold`, `bolder`, `lighter` or a [custom number](https://developer.mozilla.org/en-US/docs/Web/CSS/font-weight)            |
|           **`titleSize`** | Font size for the track artist                                                                                                                                              |
|          **`titleColor`** | Colour for the track artist                                                                                                                                                 |
|         **`titleWeight`** | Font weight for the track artist                                                                                                                                            |
