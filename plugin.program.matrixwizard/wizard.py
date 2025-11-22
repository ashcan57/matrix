#!/usr/bin/env python3
# plugin.program.matrixwizard - wizard.py
import sys
import os
import urllib.request
import zipfile
import shutil
import xbmc
import xbmcgui

# Dropbox Encore build direct download (user-provided)
DROPBOX_URL = (
    "https://www.dropbox.com/scl/fi/glc4wagx7mmdvso88jmiu/encore.zip"
    "?rlkey=836o6k19xlppx2ab9ek0zvcbt&dl=1"
)

def download_file(url, dest, dialog=None):
    try:
        urllib.request.urlretrieve(url, dest)
        return True, None
    except Exception as e:
        return False, str(e)

def extract_zip(zip_path, target_dir):
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(target_dir)
        return True, None
    except Exception as e:
        return False, str(e)

def install_build(zip_path):
    # Install path: Kodi home (special://home/) which is the userdata folder
    target = xbmc.translatePath("special://home/")
    dialog = xbmcgui.Dialog()
    xbmc.executebuiltin("ActivateWindow(busydialog)")
    ok, err = extract_zip(zip_path, target)
    xbmc.executebuiltin("Dialog.Close(busydialog)")
    if ok:
        dialog.ok("Matrix Wizard", "Encore build installed successfully.\nRestart Kodi to apply changes if necessary.")
        return True
    else:
        dialog.ok("Matrix Wizard - Error", "Failed to install build:\n%s" % err)
        return False

def run_install_flow():
    dialog = xbmcgui.Dialog()
    dest = xbmc.translatePath("special://home/encore.zip")

    # Confirm
    if not dialog.yesno("Matrix Wizard", "Download Encore build and install it to Kodi home?\nThis will replace files in your Kodi home folder. Continue?"):
        return

    xbmc.executebuiltin("ActivateWindow(busydialog)")
    success, err = download_file(DROPBOX_URL, dest)
    xbmc.executebuiltin("Dialog.Close(busydialog)")

    if not success:
        xbmcgui.Dialog().ok("Download failed", f"Failed to download Encore build:\n{err}")
        return

    # Ask user whether to extract/install now
    if dialog.yesno("Matrix Wizard", "Download complete.\nInstall the build now?"):
        install_build(dest)
    else:
        xbmcgui.Dialog().ok("Matrix Wizard", f"Build saved to:\n{dest}\nYou can install it later manually.")

def show_menu():
    handle = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    list_item = xbmcgui.ListItem("Install Encore Build (Download & Install)")
    xbmcplugin.addDirectoryItem(handle, url=DROPBOX_URL, listitem=list_item, isFolder=False)
    list_item2 = xbmcgui.ListItem("Run Installer Now")
    # Use the plugin itself with a special action parameter
    run_url = "%s?action=install" % sys.argv[0]
    xbmcplugin.addDirectoryItem(handle, run_url, list_item2, isFolder=False)
    xbmcplugin.endOfDirectory(handle)

def main():
    # Check if called with action=install
    params = ""
    if len(sys.argv) > 2:
        params = sys.argv[2]

    if "action=install" in params:
        run_install_flow()
    else:
        show_menu()

if __name__ == "__main__":
    main()
