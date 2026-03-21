import requests
import zipfile
import os
import time
import subprocess

CURRENT_VERSION = "3.1.1"
API_URL = "https://api.github.com/repos/AllensTechChannel/EazyOS/releases/latest"

print("Fetching latest release...")
response = requests.get(API_URL)
response.raise_for_status()
release = response.json()

latest_version = release.get("tag_name", "").lstrip("v")
print(f"Current version: {CURRENT_VERSION}")
print(f"Latest version:  {latest_version}")

if latest_version == CURRENT_VERSION:
    print(f"You are already on the latest version ({CURRENT_VERSION}). No updates available.")
    time.sleep(3)
else:
    assets = release.get("assets", [])
    if not assets:
        raise Exception("No release assets found.")

    # Pick the first asset (or you can filter by name)
    asset = assets[0]
    download_url = asset["browser_download_url"]
    file_name = asset["name"]

    print(f"Downloading: {file_name}")
    with requests.get(download_url, stream=True) as r:
        r.raise_for_status()
        with open(file_name, "wb") as f:
            for chunk in r.iter_content(8192):
                if chunk:
                    f.write(chunk)

    print(f"Downloaded latest release: {file_name}")
    time.sleep(2)

    result = subprocess.run(["setup3.2.bat"], shell=True, capture_output=True, text=True)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    time.sleep(3)