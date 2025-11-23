#!/usr/bin/env python3
"""
Generate Kodi repository files (addons.xml and addons.xml.md5)
Run this script after making changes to any addon
"""

import os
import hashlib
import xml.etree.ElementTree as ET
from xml.dom import minidom

def get_addon_xml_files(repo_path):
    """Find all addon.xml files in the repository"""
    addon_xmls = []
    
    # Look for addon.xml in subdirectories
    for item in os.listdir(repo_path):
        item_path = os.path.join(repo_path, item)
        if os.path.isdir(item_path):
            addon_xml = os.path.join(item_path, 'addon.xml')
            if os.path.exists(addon_xml):
                addon_xmls.append(addon_xml)
    
    return addon_xmls

def prettify_xml(elem):
    """Return a pretty-printed XML string"""
    rough_string = ET.tostring(elem, encoding='utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ", encoding="utf-8").decode('utf-8')

def generate_addons_xml(repo_path):
    """Generate addons.xml from all addon.xml files"""
    root = ET.Element('addons')
    
    addon_xmls = get_addon_xml_files(repo_path)
    
    if not addon_xmls:
        print("No addon.xml files found!")
        return None
    
    for addon_xml_path in addon_xmls:
        try:
            tree = ET.parse(addon_xml_path)
            addon = tree.getroot()
            root.append(addon)
            print(f"Added: {addon.get('id')} v{addon.get('version')}")
        except Exception as e:
            print(f"Error parsing {addon_xml_path}: {e}")
    
    # Write addons.xml
    addons_xml_path = os.path.join(repo_path, 'addons.xml')
    with open(addons_xml_path, 'w', encoding='utf-8') as f:
        f.write(prettify_xml(root))
    
    print(f"\nGenerated: {addons_xml_path}")
    return addons_xml_path

def generate_md5(file_path):
    """Generate MD5 checksum file"""
    with open(file_path, 'rb') as f:
        content = f.read()
        md5_hash = hashlib.md5(content).hexdigest()
    
    md5_path = file_path + '.md5'
    with open(md5_path, 'w') as f:
        f.write(md5_hash)
    
    print(f"Generated: {md5_path}")
    return md5_path

def main():
    # Get the repository root (parent of this script)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("Generating Kodi repository files...\n")
    
    # Generate addons.xml
    addons_xml = generate_addons_xml(script_dir)
    
    if addons_xml:
        # Generate addons.xml.md5
        generate_md5(addons_xml)
        print("\n✅ Repository files generated successfully!")
        print("\nNext steps:")
        print("1. Commit and push these files to your GitHub repository")
        print("2. Enable GitHub Pages in repository settings")
        print("3. Share the repository zip with users")
    else:
        print("❌ Failed to generate repository files")

if __name__ == '__main__':
    main()

