import requests
import os
import re
import subprocess
from rich.console import Console
from rich.panel import Panel

console = Console()
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class SM_IPTV_Final:
    def __init__(self):
        # Professional Headers to bypass blocking
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) VLC/3.0.18',
            'Accept': '*/*',
            'Connection': 'keep-alive'
        }

    def banner(self):
        os.system('clear')
        console.print(Panel.fit("[bold cyan]⚡ SM IPTV SUPREME v12.0 ⚡[/bold cyan]\n[white]Xtream Parser | Multi-Category | Bypass Fixed[/white]"))

    def github_sync(self):
        """Siddho GitHub Push logic"""
        if os.path.exists(".git"):
            console.print("[dim][*] Updating GitHub...[/dim]")
            os.system("git add . && git commit -m 'Auto-Update' && git push -u origin main")

    def get_xtream_data(self, url):
        """Extracts Category and Channels from Xtream/M3U Links"""
        channels = []
        try:
            console.print(f"[yellow][~] Bypassing & Fetching: {url[:40]}...[/yellow]")
            # Session use korle connection reset error kome jay
            with requests.Session() as s:
                r = s.get(url, headers=self.headers, timeout=20, verify=False)
                if r.status_code == 200:
                    # Robust Regex to capture group-title, name, and link
                    # It checks for both group-title="" and #EXTGRP:
                    pattern = r'#EXTINF:.*?(?:group-title="(.*?)")?.*?,(.*?)\n(?:#EXTGRP:(.*?)\n)?(http.*?)(?:\n|$)'
                    matches = re.findall(pattern, r.text)
                    
                    for g1, name, g2, link in matches:
                        cat = g1 or g2 or "General"
                        # Filtering Adult
                        if not any(x in name.lower() or x in cat.lower() for x in ["adult", "sex", "porn", "xxx"]):
                            channels.append({"cat": cat.strip(), "name": name.strip(), "link": link.strip()})
                else:
                    console.print(f"[red][!] Server Denied (Status: {r.status_code})[/red]")
        except Exception as e:
            console.print(f"[red][!] Connection Failed: Server is busy or blocking IP.[/red]")
        return channels

    def process_links(self, urls_str):
        all_ch = []
        urls = [u.strip() for u in urls_str.split(",") if u.strip()]
        for u in urls:
            data = self.get_xtream_data(u)
            all_ch.extend(data)
        return all_ch

    # --- Option 1: All Channel ---
    def option_one(self, urls):
        data = self.process_links(urls)
        if not data: return
        
        path = os.path.join(OUTPUT_DIR, "all_channels.m3u")
        with open(path, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for ch in data:
                f.write(f"#EXTINF:-1,{ch['name']}\n{ch['link']}\n")
        
        console.print(f"[bold green]✔ Total {len(data)} Valid Channels Saved![/bold green]")
        self.github_sync()

    # --- Option 2: Custom Category ---
    def option_two(self, urls):
        data = self.process_links(urls)
        if not data: return
        
        # Unique categories detect kora
        categories = sorted(list(set([ch['cat'] for ch in data])))
        
        console.print("\n[bold yellow]Available Categories:[/bold yellow]")
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat}")
            
        choice = input("\nEnter Serial (e.g., 125): ")
        try:
            indices = [int(i)-1 for i in choice if i.isdigit() and 0 < int(i) <= len(categories)]
        except: return

        for idx in indices:
            cat_name = categories[idx]
            safe_name = cat_name.replace(" ", "_").replace("/", "_")
            file_path = os.path.join(OUTPUT_DIR, f"{safe_name}.m3u")
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                count = 0
                for ch in data:
                    if ch['cat'] == cat_name:
                        f.write(f"#EXTINF:-1,{ch['name']}\n{ch['link']}\n")
                        count += 1
            console.print(f"[green]✔ {cat_name} Updated ({count} channels).[/green]")
        
        self.github_sync()

    def menu(self):
        while True:
            self.banner()
            print("1. All Channel (Deep Scan)\n2. Custom Category (Serial wise)\n0. Exit")
            opt = input("\n[>] Choice: ")
            if opt == "1":
                self.option_one(input("\nEnter M3U Links: "))
            elif opt == "2":
                self.option_two(input("\nEnter M3U Links: "))
            elif opt == "0": break
            input("\nPress Enter...")

if __name__ == "__main__":
    SM_IPTV_Final().menu()
