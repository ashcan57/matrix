# Ashcan57 Wizard 2.0.0
import xbmc, xbmcgui, xbmcaddon, xbmcvfs
import os, shutil, glob
from urllib.request import urlopen

ADDON       = xbmcaddon.Addon()
ADDON_NAME  = ADDON.getAddonInfo('name')
ADDON_PATH  = ADDON.getAddonInfo('path')
KODI_HOME   = xbmcvfs.translatePath('special://home')
TEMP_ZIP    = xbmcvfs.translatePath('special://temp/encore_build.zip')
TEMP_EXTRACT= xbmcvfs.translatePath('special://temp/encore_build/')
DROPBOX_URL = "https://www.dropbox.com/scl/fi/glc4wagx7mmdvso88jmiu/encore.zip?rlkey=836o6k19xlppx2ab9ek0zvcbt&dl=1"

def fresh_install():
    if not xbmcgui.Dialog().yesno(ADDON_NAME, "This will erase all addons & settings and install Encore.[CR][CR]Continue?"):
        return

    progress = xbmcgui.DialogProgress()
    progress.create(ADDON_NAME, "Downloading Encore build...")

    try:
        # Download
        resp = urlopen(DROPBOX_URL)
        total = int(resp.headers.get('content-length', 0))
        down = 0
        with open(TEMP_ZIP, 'wb') as f:
            while True:
                if progress.iscanceled(): raise Exception("Cancelled")
                chunk = resp.read(1024*1024)
                if not chunk: break
                down += len(chunk)
                f.write(chunk)
                pc = int(down * 70 / total) if total else 0
                progress.update(pc, f"Downloading... {down//(1024*1024)} MB")

        # Extract
        progress.update(70, "Extracting...")
        import zipfile
        with zipfile.ZipFile(TEMP_ZIP, 'r') as z:
            files = z.namelist()
            for i, f in enumerate(files):
                if progress.iscanceled(): raise Exception("Cancelled")
                z.extract(f, TEMP_EXTRACT)
                pc = 70 + int((i+1) * 20 / len(files))
                progress.update(pc, f"Extracting... {i+1}/{len(files)}")

        # Copy
        progress.update(90, "Installing files...")
        def copy(src, dst):
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
        for folder in ['userdata', 'addons']:
            src = os.path.join(TEMP_EXTRACT, folder)
            dst = os.path.join(KODI_HOME, folder)
            if os.path.exists(src):
                if os.path.exists(dst): shutil.rmtree(dst, ignore_errors=True)
                copy(src, dst)

        progress.update(100, "Complete!")
        progress.close()
        xbmcgui.Dialog().ok(ADDON_NAME, "Encore installed! Kodi will restart.")
        xbmc.executebuiltin('RestartApp')
    except Exception as e:
        progress.close()
        xbmcgui.Dialog().ok("Error", str(e))

def clear_cache():
    for folder in ['cache', 'temp', 'Database']:
        path = os.path.join(KODI_HOME, 'userdata', folder)
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)
    xbmcgui.Dialog().ok(ADDON_NAME, "Cache cleared!")

def clear_thumbnails():
    path = os.path.join(KODI_HOME, 'userdata', 'Thumbnails')
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)
    xbmcgui.Dialog().ok(ADDON_NAME, "Thumbnails cleared!")

def clear_packages():
    path = os.path.join(KODI_HOME, 'addons', 'packages')
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)
    xbmcgui.Dialog().ok(ADDON_NAME, "Packages folder cleared!")

def wipe_addons():
    if xbmcgui.Dialog().yesno(ADDON_NAME, "Delete ALL addons? This cannot be undone!"):
        path = os.path.join(KODI_HOME, 'addons')
        for item in os.listdir(path):
            if item not in ['packages', 'temp', ADDON.getAddonInfo('id')]:
                p = os.path.join(path, item)
                if os.path.isdir(p):
                    shutil.rmtree(p, ignore_errors=True)
                else:
                    os.remove(p)
        xbmcgui.Dialog().ok(ADDON_NAME, "Addons folder wiped!")

def force_close():
    xbmc.executebuiltin('Quit')

def show_log():
    log_path = xbmcvfs.translatePath('special://logpath/kodi.log')
    xbmc.executebuiltin(f'ActivateWindow(10025,"{log_path}")')

def main_menu():
    options = [
        ("Fresh Install Encore", fresh_install),
        ("Clear Cache", clear_cache),
        ("Clear Thumbnails", clear_thumbnails),
        ("Clear Packages", clear_packages),
        ("Wipe Addons Folder", wipe_addons),
        ("Force Close Kodi", force_close),
        ("View Log", show_log),
    ]
    while True:
        choice = xbmcgui.Dialog().select("Ashcan57 Wizard", [name for name, _ in options])
        if choice == -1: break
        options[choice][1]()

if __name__ == '__main__':
    main_menu()