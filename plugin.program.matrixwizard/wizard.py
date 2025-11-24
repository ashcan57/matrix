import xbmc
import xbmcgui
import xbmcaddon
import os
import urllib.request
import zipfile

ADDON = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo('path')
USERDATA = xbmc.translatePath("special://userdata/")
FLAGFILE = os.path.join(USERDATA, "install.flag")

ZIP_URL = "https://www.dropbox.com/scl/fi/glc4wagx7mmdvso88jmiu/encore.zip?rlkey=836o6k19xlppx2ab9ek0zvcbt&dl=1"
ZIP_DEST = os.path.join(USERDATA, "encore.zip")

def download_build():
    dialog = xbmcgui.Dialog()
    dialog.notification("Matrix Wizard", "Downloading build...", xbmcgui.NOTIFICATION_INFO, 3000)

    urllib.request.urlretrieve(ZIP_URL, ZIP_DEST)

    dialog.notification("Matrix Wizard", "Build downloaded", xbmcgui.NOTIFICATION_INFO, 3000)

    with open(FLAGFILE, "w") as f:
        f.write(ZIP_DEST)

    xbmc.executebuiltin("Quit")

if __name__ == "__main__":
    download_build()
