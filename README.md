# Kodi Custom Build Installer

A simple Kodi add-on that downloads and installs a custom build from Dropbox, distributed via GitHub Pages.

## What It Does

-   Downloads your custom build zip from Dropbox
-   Backs up existing `userdata` and `addons` directories
-   Installs your custom build
-   Prompts to restart Kodi

## Setup

### 1. Configure Dropbox URL

Edit `script.custom.build.installer/default.py` and find the `DROPBOX_URL` line (around line 17):

```python
DROPBOX_URL = "PASTE_YOUR_DROPBOX_LINK_HERE"
```

Replace with your actual Dropbox direct download link.

⚠️ **URL must end with `?dl=1`** (not `?dl=0`)

### 2. Configure Repository URLs

Edit `repository.custom.build/addon.xml` lines 6-8:

-   Replace `YOUR-GITHUB-USERNAME` with your GitHub username
-   Replace `YOUR-REPO-NAME` with your repository name

### 3. Generate Repository Files

```bash
python3 create_zips.py
python3 generate_repository.py
```

### 4. Deploy to GitHub Pages

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
git push -u origin main
```

Enable GitHub Pages:

-   Go to repository **Settings → Pages**
-   Source: Branch `main`, Folder `/ (root)`
-   Save

Your repository will be live at: `https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/`

## User Installation

Users can install via two methods:

**Method 1: Install Repository Zip**

1. Download `repository.custom.build-1.0.0.zip` from your GitHub Pages
2. Kodi → Settings → Add-ons → Install from zip file
3. Install from repository → Custom Build Repository → Custom Build Installer
4. Run the installer

**Method 2: Add Source**

1. Kodi → Settings → File Manager → Add source
2. Enter: `https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/`
3. Settings → Add-ons → Install from zip file → Select your source
4. Install repository, then installer add-on

## Your Custom Build Zip Structure

Your Dropbox zip must contain:

```
custom-build.zip
├── userdata/    (your custom userdata files)
└── addons/      (your custom add-ons)
```

These will **completely replace** the user's directories after backing them up.

## Updating

To release a new version:

1. Update version in `script.custom.build.installer/addon.xml`
2. Run: `python3 create_zips.py && python3 generate_repository.py`
3. Commit and push: `git add . && git commit -m "v1.0.1" && git push`

Users will get automatic update notifications in Kodi.

## File Structure

```
kodi-addon/
├── repository.custom.build/          Repository add-on
│   └── addon.xml
├── script.custom.build.installer/    Installer add-on
│   ├── addon.xml
│   ├── default.py
│   └── settings.xml
├── create_zips.py                    Generates addon zips
├── generate_repository.py            Generates addons.xml
└── README.md
```

## Troubleshooting

**Download fails**: Check Dropbox URL ends with `?dl=1`  
**Repository not found**: Wait 2-3 minutes after enabling GitHub Pages  
**Installation fails**: Verify zip structure has `userdata/` and `addons/` at root

## Requirements

-   Kodi 19+ (Matrix or higher)
-   Python 3 (for generating repository files)
-   GitHub account (for hosting)
-   Dropbox account (for custom build storage)

All free!(for me)
