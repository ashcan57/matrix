import xbmc
import xbmcaddon
import os
import zipfile
import shutil

USERDATA = xbmc.translatePath("special://userdata/")
FLAGFILE = os.path.join(USERDATA, "install.flag")

def install_build():
    if not os.path.exists(FLAGFILE):
        return

    with open(FLAGFILE, "r") as f:
        zip_path = f.read().strip()

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(USERDATA)

    os.remove(FLAGFILE)
    os.remove(zip_path)

xbmc.Monitor().waitForAbort(1)
install_build()
