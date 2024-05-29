import winreg

def get_onedrive_path():
    key_path = r'Software\Microsoft\OneDrive'
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            # The value name might vary, commonly it's 'UserFolder'
            onedrive_path = winreg.QueryValueEx(key, 'UserFolder')[0]
            return onedrive_path
    except FileNotFoundError:
        return "OneDrive path not found in registry."

onedrive_path = get_onedrive_path()
print(onedrive_path)
