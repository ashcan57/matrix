import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import os
import shutil
import zipfile
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

# ============================================================================
# CONFIGURATION - UPDATE THIS WITH YOUR DROPBOX LINK
# ============================================================================
DROPBOX_URL = "https://www.dropbox.com/scl/fi/glc4wagx7mmdvso88jmiu/encore.zip?rlkey=836o6k19xlppx2ab9ek0zvcbt&dl=1"

# ============================================================================
ADDON = xbmcaddon.Addon()
ADDON_NAME = ADDON.getAddonInfo('name')
KODI_HOME = xbmcvfs.translatePath('special://home/')
TEMP_ZIP = xbmcvfs.translatePath('special://temp/custom_build.zip')
TEMP_EXTRACT = xbmcvfs.translatePath('special://temp/custom_build/')

def log(message):
    xbmc.log("[{}] {}".format(ADDON_NAME, message), level=xbmc.LOGINFO)

def show_notification(title, message, time=5000):
    xbmcgui.Dialog().notification(title, message, xbmcgui.NOTIFICATION_INFO, time)

def download_file(url, destination):
    try:
        log("Downloading build from Dropbox...")
        response = urlopen(url)
        with open(destination, 'wb') as f:
            f.write(response.read())
        log("Download complete")
        return True
    except Exception as e:
        log("Download failed: {}".format(str(e)))
        return False

def extract_zip(zip_path, extract_to):
    try:
        log("Extracting zip...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        log("Extraction complete")
        return True
    except Exception as e:
        log("Extraction failed: {}".format(str(e)))
        return False

def force_copy_folder(src, dst):
    """Copy folder file-by-file, ignoring locked files"""
    if not os.path.exists(src):
        return False
    if os.path.exists(dst):
        shutil.rmtree(dst, ignore_errors=True)
    os.makedirs(dst, exist_ok=True)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        try:
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
        except Exception as e:
            log("Copy error (ignored): {} → {}".format(s, e))
    return True

def cleanup():
    try:
        if os.path.exists(TEMP_ZIP):
            os.remove(TEMP_ZIP)
        if os.path.exists(TEMP_EXTRACT):
            shutil.rmtree(TEMP_EXTRACT, ignore_errors=True)
        log("Cleanup complete")
    except:
        pass

def install_build():
    dialog = xbmcgui.Dialog()
    if not dialog.yesno(ADDON_NAME,
                        "This will completely replace your current addons and settings.[CR][CR]"
                        "Continue with fresh install?"):
        return

    progress = xbmcgui.DialogProgress()
    progress.create(ADDON_NAME, "Installing Custom Build...")

    try:
        progress.update(10, "Downloading build...")
        if not download_file(DROPBOX_URL, TEMP_ZIP):
            dialog.ok(ADDON_NAME, "Download failed. Check your internet or Dropbox link.")
            return

        progress.update(30, "Extracting...")
        if not extract_zip(TEMP_ZIP, TEMP_EXTRACT):
            dialog.ok(ADDON_NAME, "Extraction failed. ZIP may be corrupted.")
            return

        progress.update(60, "Installing userdata...")
        new_userdata = os.path.join(TEMP_EXTRACT, 'userdata')
        userdata_path = os.path.join(KODI_HOME, 'userdata')
        if os.path.exists(new_userdata):
            force_copy_folder(new_userdata, userdata_path)
        else:
            dialog.ok(ADDON_NAME, "userdata folder not found in build!")
            return

        progress.update(80, "Installing addons...")
        new_addons = os.path.join(TEMP_EXTRACT, 'addons')
        addons_path = os.path.join(KODI_HOME, 'addons')
        if os.path.exists(new_addons):
            force_copy_folder(new_addons, addons_path)

        progress.update(95, "Finalizing...")
        cleanup()

        progress.update(100, "Build installed successfully!")
        progress.close()

        if dialog.yesno(ADDON_NAME, "Installation complete![CR][CR]Restart Kodi now?"):
            xbmc.executebuiltin('RestartApp')

    except Exception as e:
        progress.close()
        log("Unexpected error: {}".format(str(e)))
        dialog.ok(ADDON_NAME, "Installation failed: {}".format(str(e)))
    finally:
        if progress.iscanceled():
            cleanup()

if __name__ == '__main__':
    install_build()