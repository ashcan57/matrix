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
# Your Dropbox direct download link (MUST end with ?dl=1)
# Example: "https://www.dropbox.com/s/abc123xyz/custom-build.zip?dl=1"
DROPBOX_URL = "https://www.dropbox.com/scl/fi/glc4wagx7mmdvso88jmiu/encore.zip?rlkey=836o6k19xlppx2ab9ek0zvcbt&dl=1"
# ============================================================================

# Get addon info
ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_NAME = ADDON.getAddonInfo('name')
KODI_HOME = xbmcvfs.translatePath('special://home/')
TEMP_ZIP = xbmcvfs.translatePath('special://temp/custom_build.zip')
TEMP_EXTRACT = xbmcvfs.translatePath('special://temp/custom_build/')

def log(message):
    """Log messages to Kodi log"""
    xbmc.log("[{}] {}".format(ADDON_NAME, message), level=xbmc.LOGINFO)

def show_notification(title, message, time=5000):
    """Show notification to user"""
    xbmcgui.Dialog().notification(title, message, xbmcgui.NOTIFICATION_INFO, time)

def download_file(url, destination):
    """Download file from URL"""
    try:
        log("Downloading from: {}".format(url))
        response = urlopen(url)
        with open(destination, 'wb') as f:
            f.write(response.read())
        log("Download complete: {}".format(destination))
        return True
    except Exception as e:
        log("Download error: {}".format(str(e)))
        return False

def extract_zip(zip_path, extract_to):
    """Extract zip file"""
    try:
        log("Extracting: {}".format(zip_path))
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        log("Extraction complete")
        return True
    except Exception as e:
        log("Extraction error: {}".format(str(e)))
        return False

def backup_directory(directory):
    """Create backup of directory"""
    backup_path = directory + '_backup'
    try:
        if os.path.exists(backup_path):
            shutil.rmtree(backup_path)
        if os.path.exists(directory):
            log("Backing up: {}".format(directory))
            shutil.copytree(directory, backup_path)
            return True
    except Exception as e:
        log("Backup error: {}".format(str(e)))
    return False

def copy_directory(src, dst):
    """Copy directory contents, overwriting destination"""
    try:
        log("Copying {} to {}".format(src, dst))
        if os.path.exists(dst):
            # Remove existing directory
            shutil.rmtree(dst)
        # Copy new directory
        shutil.copytree(src, dst)
        log("Copy complete")
        return True
    except Exception as e:
        log("Copy error: {}".format(str(e)))
        return False

def cleanup():
    """Clean up temporary files"""
    try:
        if os.path.exists(TEMP_ZIP):
            os.remove(TEMP_ZIP)
        if os.path.exists(TEMP_EXTRACT):
            shutil.rmtree(TEMP_EXTRACT)
        log("Cleanup complete")
    except Exception as e:
        log("Cleanup error: {}".format(str(e)))

def install_build():
    """Main installation function"""
    dialog = xbmcgui.Dialog()
    
    # Confirm installation
    if not dialog.yesno(ADDON_NAME, 
                        "This will overwrite your current userdata and addons.[CR]"
                        "A backup will be created first.[CR][CR]"
                        "Do you want to continue?"):
        return
    
    # Show progress dialog
    progress = xbmcgui.DialogProgress()
    progress.create(ADDON_NAME, "Installing Custom Build...")
    
    try:
        # Step 1: Download
        progress.update(10, "Downloading build from Dropbox...")
        if not download_file(DROPBOX_URL, TEMP_ZIP):
            dialog.ok(ADDON_NAME, "Download failed. Check your internet connection and Dropbox URL.")
            return
        
        # Step 2: Extract
        progress.update(30, "Extracting archive...")
        if not extract_zip(TEMP_ZIP, TEMP_EXTRACT):
            dialog.ok(ADDON_NAME, "Extraction failed. The zip file may be corrupted.")
            return
        
        # Step 3 & 4 combined – NO BACKUP, FORCE COPY (Windows-proof)
        progress.update(60, "Installing fresh build – no backup needed...")

        userdata_path = os.path.join(KODI_HOME, 'userdata')
        addons_path   = os.path.join(KODI_HOME, 'addons')
        new_userdata  = os.path.join(TEMP_EXTRACT, 'userdata')
        new_addons    = os.path.join(TEMP_EXTRACT, 'addons')

        # Force-delete userdata (ignores locked files)
        if os.path.exists(userdata_path):
            shutil.rmtree(userdata_path, ignore_errors=True)

        # Force-delete addons (ignores locked files)
        if os.path.exists(addons_path):
            shutil.rmtree(addons_path, ignore_errors=True)

        # Copy userdata file-by-file (never fails on Windows)
        if os.path.exists(new_userdata):
            os.makedirs(userdata_path, exist_ok=True)
            for item in os.listdir(new_userdata):
                s = os.path.join(new_userdata, item)
                d = os.path.join(userdata_path, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)

        # Copy addons file-by-file
        if os.path.exists(new_addons):
            os.makedirs(addons_path, exist_ok=True)
            for item in os.listdir(new_addons):
                s = os.path.join(new_addons, item)
                d = os.path.join(addons_path, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)

        progress.update(95, "Cleaning up...")
        cleanup()
        addons_path = os.path.join(KODI_HOME, 'addons')
        new_addons = os.path.join(TEMP_EXTRACT, 'addons')
        
        if os.path.exists(new_addons):
            if os.path.exists(addons_path):
                shutil.rmtree(addons_path, ignore_errors=True)
            os.makedirs(addons_path, exist_ok=True)
            for item in os.listdir(new_addons):
                s = os.path.join(new_addons, item)
                d = os.path.join(addons_path, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)p        progress.update(85, "Force-installing addons...")
        addons_path = os.path.join(KODI_HOME, 'addons')
        new_addons = os.path.join(TEMP_EXTRACT, 'addons')
        
        if os.path.exists(new_addons):
            if os.path.exists(addons_path):
                shutil.rmtree(addons_path, ignore_errors=True)
            os.makedirs(addons_path, exist_ok=True)
            for item in os.listdir(new_addons):
                s = os.path.join(new_addons, item)
                d = os.path.join(addons_path, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)
        
        # Prompt to restart Kodi
        if dialog.yesno(ADDON_NAME, 
                       "Installation complete![CR]"
                       "Kodi needs to restart to apply changes.[CR][CR]"
                       "Restart now?"):
            xbmc.executebuiltin('RestartApp')
        
    except Exception as e:
        progress.close()
        log("Installation error: {}".format(str(e)))
        dialog.ok(ADDON_NAME, "Installation failed: {}".format(str(e)))
    finally:
        cleanup()

if __name__ == '__main__':
    install_build()

