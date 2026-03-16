import requests
import os
import re
import concurrent.futures
import threading
import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# --- Configurations ---
OUTPUT_DIR = "output"
ALL_SOURCE_TXT = "allsource.txt"
ALL_SOURCE_M3U = "allsource.m3u"
CRACK_FILE = "crack.txt"
COMBO_FILE = "iptv_combo.txt"
GIT_REPO = "YOUR_GITHUB_REPO_URL" # Ekhane ekbar link diye dile auto update hobe

# Categories with Keywords
CAT_MAP = {
    "1": ("News", ["news", "somoy", "jamuna", "bbc", "cnn"]),
    "2": ("Sports", ["sport", "t sports", "willow", "sony", "star sports", "ipl"]),
    "3": ("Islamic", ["islamic", "quran", "madani", "makkah", "peace tv"]),
    "4": ("Cartoons", ["kids", "cartoon", "nick", "disney", "pogo"]),
    "5": ("Movies", ["movie", "cinema", "film", "hbo", "star movies"])
}

BLOCKLIST = ["adult", "sex", "porn", "xxx", "18+", "nsfw"]

class SM_IPTV_Pro:
    def __init__(self):
        self.hits = 0
        self.checked = 0
        self.lock = threading.Lock()
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def banner(self):
        os.system('clear')
        console.print(Panel.fit("[bold cyan]SM IPTV CUSTOMIZE v6.0[/bold cyan]\n[white]The Most Powerful IPTV Tool for Termux[/white]", border_style="blue"))

    def github_sync(self):
        """Auto updates to GitHub every time a change is made"""
        console.print("[dim][*] Syncing with GitHub...[/dim]")
        os.system("git add . && git commit -m 'Auto-Update SM IPTV' && git push -u origin main --force > /dev/null 2>&1")

    def is_safe(self, name):
        return not any(word in name.lower() for word in BLOCKLIST)

    # 1. All Channel
    def all_channel(self, urls):
        channels = []
        for url in urls:
            try:
                r = requests.get(url.strip(), timeout=10).text
                matches = re.findall(r'(#EXTINF.*?,(.*?)\n(http.*?))', r)
                for full, name, link in matches:
                    if self.is_safe(name):
                        channels.append((name, link))
            except: continue
        
        # Save to same file every time
        path = os.path.join(OUTPUT_DIR, "all_channels.m3u")
        with open(path, "w") as f:
            f.write("#EXTM3U\n")
            for n, l in channels: f.write(f"#EXTINF:-1,{n}\n{l}\n")
        
        # Also Update Source Code Copy (Option 3)
        with open(ALL_SOURCE_TXT, "a") as f:
            for n, l in channels: f.write(f"{n} : {l}\n")
        
        console.print(f"[green]✔ All Channels Updated. Total: {len(channels)}[/green]")
        self.github_sync()

    # 2. Custom Channel Folder
    def custom_folder(self, urls):
        console.print("\n[bold yellow]Select Categories (e.g., 123 for News, Sports, Islamic):[/bold yellow]")
        for k, v in CAT_MAP.items():
            print(f"{k}. {v[0]}")
        
        choice = input("\nEnter Choice: ")
        all_found = []

        for url in urls:
            try:
                r = requests.get(url.strip(), timeout=10).text
                matches = re.findall(r'(#EXTINF.*?,(.*?)\n(http.*?))', r)
                for char in choice:
                    if char in CAT_MAP:
                        cat_name, keys = CAT_MAP[char]
                        filtered = [f"#EXTINF:-1,{n}\n{l}" for full, n, l in matches if any(k in n.lower() for k in keys)]
                        
                        # Save in same category file (No separate name)
                        cat_file = os.path.join(OUTPUT_DIR, f"{cat_name}.m3u")
                        with open(cat_file, "w") as f:
                            f.write("#EXTM3U\n" + "\n".join(filtered))
                        console.print(f"[green]✔ {cat_name} Updated.[/green]")
            except: continue
        self.github_sync()

    # 5. Crack IPTV
    def check_worker(self, combo):
        try:
            base = combo.split("/get.php")[0]
            api = f"{base}/player_api.php?{combo.split('?')[1]}"
            res = requests.get(api, timeout=7).json()
            
            if res.get("user_info", {}).get("status") == "Active":
                ch_count = len(requests.get(f"{base}/player_api.php?{combo.split('?')[1]}&action=get_live_categories", timeout=5).json())
                info = f"URL: {combo} | Channels: {ch_count} | Status: Active"
                with self.lock:
                    self.hits += 1
                    with open(CRACK_FILE, "a") as f: f.write(info + "\n")
                console.print(f"[bold green][HIT] {info}[/bold green]")
        except: pass

    # 6. Combo Maker
    def combo_maker_menu(self):
        print("\n1. Auto Make (Scrape from Web)")
        print("2. Custom (Manual M3U to Combo)")
        c = input("Choice: ")
        
        if c == "2":
            path = input("Enter M3U File Path: ")
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = f.read()
                    matches = re.findall(r'(http://[^\s/:]+:\d+)/get\.php\?username=([^\s&]+)&password=([^\s&]+)', data)
                    with open(COMBO_FILE, "w") as out:
                        for h, u, p in set(matches):
                            out.write(f"{h}/get.php?username={u}&password={p}&type=m3u_plus\n")
                console.print(f"[green]✔ Combo Created: {COMBO_FILE}[/green]")
            
            console.print("\n[bold cyan]How to make Custom Combo?[/bold cyan]")
            print("1. Collect M3U files from Telegram/GitHub.\n2. Ensure they have 'username' and 'password' in the link.\n3. Put the path here, tool will format it for cracking.")

    def main(self):
        while True:
            self.banner()
            print("1. All Channel (Clean)")
            print("2. Custom Channel Folder (Serial)")
            print("3. Source Code Copy (allsource.txt)")
            print("4. Source All (GitHub Upload)")
            print("5. Crack IpTv (Scan & Validate)")
            print("6. Combo Maker")
            print("0. Exit")
            
            opt = input("\n[>] Option: ")
            
            if opt in ["1", "2"]:
                u = input("Enter M3U Links (comma separated): ").split(",")
                if opt == "1": self.all_channel(u)
                else: self.custom_folder(u)
            
            elif opt == "3":
                console.print(f"[green]✔ All sources saved in {ALL_SOURCE_TXT}[/green]")
            
            elif opt == "4":
                # Direct GitHub Upload for .m3u source
                os.system(f"cp {os.path.join(OUTPUT_DIR, 'all_channels.m3u')} {ALL_SOURCE_M3U}")
                self.github_sync()
                console.print("[green]✔ Uploaded to GitHub as allsource.m3u[/green]")

            elif opt == "5":
                path = input("Enter Combo File Path: ")
                if os.path.exists(path):
                    with open(path, "r") as f: links = f.read().splitlines()
                    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
                        ex.map(self.check_worker, links)

            elif opt == "6": self.combo_maker_menu()
            elif opt == "0": break
            input("\nPress Enter...")

if __name__ == "__main__":
    SM_IPTV_Pro().main()
