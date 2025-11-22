#!/usr/bin/env python3
# plugin.video.matrix - main.py
import sys
import urllib.parse
import xbmcplugin
import xbmcgui

HANDLE = int(sys.argv[1]) if len(sys.argv) > 1 else 0

# Dropbox Encore build direct download (user-provided)
DROPBOX_BUILD_URL = (
    "https://www.dropbox.com/scl/fi/glc4wagx7mmdvso88jmiu/encore.zip"
    "?rlkey=836o6k19xlppx2ab9ek0zvcbt&dl=1"
)

# Example streams (replace with your real streams)
STREAMS = [
    {"title": "Example Stream 1", "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"},
    {"title": "Example Stream 2", "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4"},
]

def add_item(title, url, is_folder=False, info=None):
    li = xbmcgui.ListItem(label=title)
    if info:
        li.setInfo("video", info)
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=li, isFolder=is_folder)

def root_menu():
    # Add the streams
    for s in STREAMS:
        add_item(s["title"], s["url"], is_folder=False, info={"title": s["title"]})

    # Add an entry to run the wizard program add-on (installer)
    wizard_run_url = "RunPlugin(plugin://plugin.program.matrixwizard/?action=install)"
    add_item("Install Encore Build (Run Wizard)", wizard_run_url, is_folder=False)

    # Add the direct Dropbox download link
    add_item("Download Encore Build (Dropbox)", DROPBOX_BUILD_URL, is_folder=False)

    xbmcplugin.endOfDirectory(HANDLE)

if __name__ == "__main__":
    # No parameter parsing required for the simple root menu
    root_menu()
