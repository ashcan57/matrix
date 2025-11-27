import xbmc, xbmcgui, xbmcaddon, xbmcvfs
import os, shutil
from urllib.request import urlopen
import zipfile

ADDON       = xbmcaddon.Addon()
ADDON_NAME  = ADDON.getAddonInfo('name')
KODI_HOME   = xbmcvfs.translatePath('special://home')
TEMP_ZIP    = xbmcvfs.translatePath('special://temp/encore_build.zip')
TEMP_EXTRACT= xbmcvfs.translatePath('special://temp/encore_build/')
DROPBOX_URL = "https://www.dropbox.com/scl/fi/glc4wagx7mmdvso88jmiu/encore.zip?rlkey=836o6k19xlppx2ab9ek0zvcbt&dl=1"

# ====================== FRESH INSTALL WITH PERFECT PROGRESS ======================
def fresh_install():
    if not xbmcgui.Dialog().yesno(ADDON_NAME, "Fresh install Encore build?[CR][CR]This will wipe everything!"):
        return

    progress = xbmcgui.DialogProgress()
    progress.create(ADDON_NAME, "Starting...")

    try:
        # 0-30% Download
        progress.update(0, "Downloading...")
        resp = urlopen(DROPBOX_URL)
        total = int(resp.headers.get('content-length', 0)) or 1
        down = 0
        chunk = 1024*1024
        with open(TEMP_ZIP, 'wb') as f:
            while True:
                if progress.iscanceled(): raise Exception("Cancelled")
                data = resp.read(chunk)
                if not data: break
                down += len(data)
                f.write(data)
                pc = int(down * 30 / total)
                progress.update(pc, f"Downloading... {down//(1024*1024)} MB")

        # 30-60% Extract
        progress.update(30, "Extracting...")
        with zipfile.ZipFile(TEMP_ZIP, 'r') as z:
            files = z.namelist()
            for i, f in enumerate(files):
                if progress.iscanceled(): raise Exception("Cancelled")
                z.extract(f, TEMP_EXTRACT)
                pc = 30 + int((i+1) * 30 / len(files))
                progress.update(pc, f"Extracting... {i+1}/{len(files)}")

        # 60-90% Copy userdata + addons
        progress.update(60, "Installing userdata & addons...")
        total_files = sum(len(f) for _r, _d, f in os.walk(TEMP_EXTRACT))
        copied = 0
        def copy(src, dst):
            nonlocal copied
            for item in os.listdir(src):
                s = os.path.join(src, item)
                d = os.path.join(dst, item)
                if os.path.isdir(s):
                    os.makedirs(d, exist_ok=True)
                    copy(s, d)
                else:
                    shutil.copy2(s, d)
                copied += 1
                pc = 60 + int(copied * 30 / max(total_files, 1))
                progress.update(pc, f"Installing... {copied}/{total_files}")

        for folder in ['userdata', 'addons']:
            src = os.path.join(TEMP_EXTRACT, folder)
            dst = os.path.join(KODI_HOME, folder)
            if os.path.exists(src):
                if os.path.exists(dst): shutil.rmtree(dst, ignore_errors=True)
                copy(src, dst)

        # 90-100% Cleanup
        progress.update(90, "Cleaning up...")
        if os.path.exists(TEMP_ZIP): os.remove(TEMP_ZIP)
        if os.path.exists(TEMP_EXTRACT): shutil.rmtree(TEMP_EXTRACT, ignore_errors=True)

        progress.update(100, "Complete!")
        progress.close()
        xbmcgui.Dialog().ok(ADDON_NAME, "Encore installed! Restarting...")
        xbmc.executebuiltin('RestartApp')

    except Exception as e:
        progress.close()
        xbmcgui.Dialog().ok("Error", str(e))

# ====================== MAINTENANCE TOOLS ======================
def clear_cache():     [shutil.rmtree(p, ignore_errors=True) for p in [os.path.join(KODI_HOME,'userdata','cache'), os.path.join(KODI_HOME,'userdata','temp')]]; xbmcgui.Dialog().ok(ADDON_NAME,"Cache cleared")
def clear_thumbnails(): shutil.rmtree(os.path.join(KODI_HOME,'userdata','Thumbnails'), ignore_errors=True); xbmcgui.Dialog().ok(ADDON_NAME,"Thumbnails cleared")
def clear_packages():   shutil.rmtree(os.path.join(KODI_HOME,'addons','packages'), ignore_errors=True); xbmcgui.Dialog().ok(ADDON_NAME,"Packages cleared")
def force_close():      xbmc.executebuiltin('Quit')

# ====================== MAIN MENU ======================
def main_menu():
    items = [
        ("Fresh Install Encore", fresh_install),
        ("Clear Cache", clear_cache),
        ("Clear Thumbnails", clear_thumbnails),
        ("Clear Packages", clear_packages),
        ("Force Close Kodi", force_close),
    ]
    while True:
        choice = xbmcgui.Dialog().select("Ashcan57 Wizard", [n for n,_ in items])
        if choice < 0: break
        items[choice][1]()

if __name__ == '__main__':
    main_menu()      # ← THIS IS THE LINE THAT MUST BE THERE