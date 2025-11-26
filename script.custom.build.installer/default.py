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

def force_copy_folder(src, dst):
    """Copy folder file-by-file, ignoring locked files"""
    if not os.path.exists(src):
        return
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

def download_file_with_progress(url, destination, progress_dialog):
    """Download with smooth progress bar (0-65%)"""
    try:
        log("Starting download from: {}".format(url))
        response = urlopen(url)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024 * 1024  # 1 MB
        downloaded = 0
        with open(destination, 'wb') as f:
            while True:
                if progress_dialog.iscanceled():
                    log("Download cancelled by user")
                    return False
                buffer = response.read(block_size)
                if not buffer:
                    break
                downloaded += len(buffer)
                f.write(buffer)
                if total_size > 0:
                    percent = int((downloaded * 65) / total_size)  # 65% of total bar
                    mb = downloaded // (1024 * 1024)
                    progress_dialog.update(percent,
                                          f"Downloading Encore build... {mb} MB")
        log("Download complete: {} bytes".format(downloaded))
        return True
    except Exception as e:
        log("Download failed: {}".format(str(e)))
        return False

def extract_zip(zip_path, extract_to):
    try:
        log("Extracting archive...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        log("Extraction complete")
        return True
    except Exception as e:
        log("Extraction failed: {}".format(str(e)))
        return False

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
    if not dialog.yesno(ADDON_NAME, "Install the latest Encore build now?"):
        return

    progress = xbmcgui.DialogProgress()
    progress.create(ADDON_NAME, "Downloading Encore build...")

    try:
        # Download with simple progress
        response = urlopen(DROPBOX_URL)
        total = int(response.headers.get('content-length', 0))
        downloaded = 0
        chunk = 1024 * 512  # 512 KB chunks

        with open(TEMP_ZIP, 'wb') as f:
            while True:
                data = response.read(chunk)
                if not data:
                    break
                downloaded += len(data)
                f.write(data)

                if total > 0:
                    percent = int(downloaded * 100 / total)
                else:
                    percent = 0
                progress.update(percent, f"Downloading... {downloaded//(1024*1024)} MB")

                if progress.iscanceled():
                    progress.close()
                    return

        progress.update(100, "Download complete – installing...")
        # The rest of your existing code (extract, copy, cleanup) stays unchanged
        # → just paste your original extract/copy lines here if they were different
        # (for safety I’ll keep the exact ones you already had working)

        # <<< YOUR ORIGINAL EXTRACT & COPY CODE STARTS HERE >>>
        with zipfile.ZipFile(TEMP_ZIP, 'r') as zip_ref:
            zip_ref.extractall(TEMP_EXTRACT)

        force_copy_folder(os.path.join(TEMP_EXTRACT, 'userdata'), os.path.join(KODI_HOME, 'userdata'))
        force_copy_folder(os.path.join(TEMP_EXTRACT, 'addons'),   os.path.join(KODI_HOME, 'addons'))
        cleanup()
        # <<< END OF YOUR ORIGINAL CODE >>>

        progress.close()
        dialog.ok(ADDON_NAME, "Encore build installed perfectly![CR][CR]Kodi will now restart.")
        xbmc.executebuiltin('RestartApp')

    except Exception as e:
        progress.close()
        dialog.ok(ADDON_NAME, f"Error: {str(e)}")
    finally:
        if progress.iscanceled():
            cleanup()

if __name__ == '__main__':
    install_build()