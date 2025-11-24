import xbmcplugin
import xbmcgui
import sys

def main():
    url = sys.argv[0]
    handle = int(sys.argv[1])
    
    li = xbmcgui.ListItem(label="Hello Matrix")
    xbmcplugin.addDirectoryItem(handle, url, li)
    xbmcplugin.endOfDirectory(handle)

if __name__ == "__main__":
    main()
