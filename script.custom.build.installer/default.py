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

def fresh_install():
    if not xbmcgui.Dialog().yesno(ADDON_NAME, "Fresh install Encore build?[CR][CR]This will wipe everything!"):
        return

    progress = xbmcgui.DialogProgress()
    progress.create(ADDON_NAME, "Starting fresh install...")

    try:
        # 0-30% Download
        progress.update(0, "Downloading Encore build...")
        resp = urlopen(DROPBOX_URL)
        total = int(resp.headers.get('content-length', 0)) or 1
        downloaded = 0
        chunk = 1024 * 1024

        with open(TEMP_ZIP, 'wb') as f:
            while True:
                if progress.iscanceled():
                    raise Exception("Cancelled")
                data = resp.read(chunk)
                if not data: break
                downloaded += len(data)
                f.write(data)
                pc = int(downloaded * 30 / total)          # ← exactly 0-30%
                progress.update(pc, f"Downloading... {downloaded//(1024*1024)} MB")

        # 30-60% Extract
        progress.update(30, "Extracting files...")
        import zipfile
        with zipfile.ZipFile(TEMP_ZIP, 'r') as z:
            files = z.namelist()
            for i, file in enumerate(files):
                if progress.iscanceled():
                    raise Exception("Cancelled")
                z.extract(file, TEMP_EXTRACT)
                pc = 30 + int((i + 1) * 30 / len(files))   # ← exactly 30-60%
                progress.update(pc, f"Extracting... {i+1}/{len(files)}")

        # 60-90% Install userdata + addons (with file counter)
        progress.update(60, "Installing userdata & addons...")

        total_files = sum(len(f) for _r, _d, f in os.walk(TEMP_EXTRACT))
        copied = 0

        def copy_with_progress(src, dst):
            nonlocal copied
            for item in os.listdir(src):
                s = os.path.join(src, item)
                d = os.path.join(dst, item)
                if os.path.isdir(s):
                    os.makedirs(d, exist_ok=True)
                    copy_with_progress(s, d)
                else:
                    shutil.copy2(s, d)
                copied += 1
                pc = 60 + int(copied * 30 / max(total_files, 1))   # ← exactly 60-90%
                progress.update(pc, f"Installing files... {copied}/{total_files}")

        for folder in ['userdata', 'addons']:
            src = os.path.join(TEMP_EXTRACT, folder)
            dst = os.path.join(KODI_HOME, folder)
            if os.path.exists(src):
                if os.path.exists(dst):
                    shutil.rmtree(dst, ignore_errors=True)
                copy_with_progress(src, dst)

        # 90-100% Cleanup
        progress.update(90, "Cleaning up temporary files...")
        if os.path.exists(TEMP_ZIP): os.remove(TEMP_ZIP)
        if os.path.exists(TEMP_EXTRACT): shutil.rmtree(TEMP_EXTRACT, ignore_errors=True)

        progress.update(100, "Installation complete!")
        progress.close()

        xbmcgui.Dialog().ok(ADDON_NAME, "Encore build installed perfectly![CR][CR]Kodi will restart.")
        xbmc.executebuiltin('RestartApp')

    except Exception as e:
        progress.close()
        xbmcgui.Dialog().ok("Error", str(e))
    finally:
        if progress.iscanceled():
            cleanup()

if __name__ == '__main__':
    main_menu()        # This opens the wizard menu