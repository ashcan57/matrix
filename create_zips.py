#!/usr/bin/env python3
"""
Create zip files for all addons in the repository
Each addon gets zipped as: addon-id/addon-id-version.zip
"""

import os
import zipfile
import xml.etree.ElementTree as ET
import shutil

def get_addon_info(addon_path):
    """Extract addon ID and version from addon.xml"""
    addon_xml = os.path.join(addon_path, 'addon.xml')
    if not os.path.exists(addon_xml):
        return None, None
    
    tree = ET.parse(addon_xml)
    root = tree.getroot()
    addon_id = root.get('id')
    version = root.get('version')
    
    return addon_id, version

def create_addon_zip(addon_path, addon_id, version, output_dir):
    """Create a zip file for an addon"""
    zip_filename = f"{addon_id}-{version}.zip"
    zip_path = os.path.join(output_dir, addon_id, zip_filename)
    
    # Create addon directory if it doesn't exist
    os.makedirs(os.path.join(output_dir, addon_id), exist_ok=True)
    
    # Create zip file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(addon_path):
            # Skip __pycache__ and other unwanted directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                if file.startswith('.'):
                    continue
                
                file_path = os.path.join(root, file)
                arcname = os.path.join(addon_id, os.path.relpath(file_path, addon_path))
                zipf.write(file_path, arcname)
    
    print(f"Created: {zip_path}")
    return zip_path

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("Creating addon zip files...\n")
    
    # Find all addon directories
    for item in os.listdir(script_dir):
        item_path = os.path.join(script_dir, item)
        
        # Skip non-directories and script files
        if not os.path.isdir(item_path):
            continue
        if item.startswith('.') or item == '__pycache__':
            continue
        
        # Check if it's an addon directory
        addon_id, version = get_addon_info(item_path)
        if addon_id and version:
            create_addon_zip(item_path, addon_id, version, script_dir)
    
    print("\n✅ All addon zips created successfully!")
    print("\nNext step: Run generate_repository.py to create addons.xml")

if __name__ == '__main__':
    main()

