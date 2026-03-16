import requests
import os
import re
import concurrent.futures
import threading
import subprocess
from rich.console import Console
from rich.panel import Panel

console = Console()

# --- Configurations ---
OUTPUT_DIR = "output"

class SM_IPTV_Advance:
    def __init__(self):
        self.lock = threading.Lock()
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def banner(self):
        os.system('clear')
        console.print(Panel.fit("[bold cyan]⚡ SM IPTV CUSTOMIZE PRO ⚡[/bold cyan]\n[white]Option 1 & 2 | Ultra Advance | Live Validation[/white]"))

    def check_link(self, channel):
        """Channel playable kina check korbe"""
        try:
            # 5 second er moddhe response na ashle dead
            r = requests.get(channel['link'], timeout=5, stream=True)
            if r.status_code == 200:
                return channel
        except:
            return None
        return None

    def github_sync(self):
        """Automatic update to GitHub repository"""
        if os.path.exists(".git"):
            console.print("[dim][*] Syncing with GitHub...[/dim]")
            subprocess.run("git add . && git commit -m 'Auto-Update' && git push -u origin main", shell=True)

    def parse_links(self, urls_str):
        """Multiple link theke channel, category r name extract kora"""
        all_raw_channels = []
        urls = [u.strip() for u in urls_str.split(",") if u.strip()]
        
        for url in urls:
            try:
                console.print(f"[yellow][~] Fetching M3U from link...[/yellow]")
                r = requests.get(url, timeout=15).text
                # Category extract korar regex (group-title, EXTGRP etc)
                matches = re.findall(r'#EXTINF:.*?(?:group-title="(.*?)")?.*?,(.*?)\n(?:#EXTGRP:(.*?)\n)?(http.*?)(?:\n|$)', r)
                
                for group1, name, group2, link in matches:
                    cat = group1 or group2 or "General"
                    # Adult content filter
                    if any(x in name.lower() or x in cat.lower() for x in ["adult", "sex", "xxx", "porn", "18+"]):
                        continue
                    all_raw_channels.append({"cat": cat.strip(), "name": name.strip(), "link": link.strip()})
            except:
                console.print(f"[red][!] Error loading link: {url[:30]}...[/red]")
        
        # Validating only working channels (Fast Multi-threading)
        console.print(f"[cyan][*] Validating {len(all_raw_channels)} channels. Please wait...[/cyan]")
        valid_channels = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            results = list(executor.map(self.check_link, all_raw_channels))
            valid_channels = [ch for ch in results if ch is not None]
        
        return valid_channels

    # --- Option 1: All Channel (Clean & Valid) ---
    def process_all_channels(self, urls_str):
        channels = self.parse_links(urls_str)
        if not channels:
            console.print("[red][!] No valid channels found.[/red]")
            return

        path = os.path.join(OUTPUT_DIR, "all_channels.m3u")
        with open(path, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for ch in channels:
                f.write(f"#EXTINF:-1,{ch['name']}\n{ch['link']}\n")
        
        console.print(f"[bold green]✔ Done! {len(channels)} valid channels saved in all_channels.m3u[/bold green]")
        self.github_sync()

    # --- Option 2: Custom Category (Serial wise) ---
    def process_categories(self, urls_str):
        channels = self.parse_links(urls_str)
        if not channels: return

        # Unique category list banano
        categories = sorted(list(set([ch['cat'] for ch in channels])))
        
        console.print("\n[bold yellow]Available Categories (Select Numbers):[/bold yellow]")
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat}")
        
        choice = input("\nEnter Serial (e.g., 125 for News, Cartoon, Sports): ")
        selected_indices = [int(i)-1 for i in choice if i.isdigit() and 0 < int(i) <= len(categories)]

        for idx in selected_indices:
            cat_name = categories[idx]
            safe_file_name = "".join([c for c in cat_name if c.isalnum() or c in (' ', '_')]).strip().replace(' ', '_')
            cat_path = os.path.join(OUTPUT_DIR, f"{safe_file_name}.m3u")
            
            with open(cat_path, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                count = 0
                for ch in channels:
                    if ch['cat'] == cat_name:
                        f.write(f"#EXTINF:-1,{ch['name']}\n{ch['link']}\n")
                        count += 1
            console.print(f"[green]✔ {cat_name}: {count} channels added.[/green]")
        
        self.github_sync()

    def main_menu(self):
        while True:
            self.banner()
            console.print("1. All Channel (Validate & Auto-Update)")
            console.print("2. Custom Category (Serial Choice & Validation)")
            console.print("0. Exit")
            
            choice = input("\n[>] Select: ")
            if choice == "1":
                self.process_all_channels(input("\nEnter M3U Links (Comma separated): "))
            elif choice == "2":
                self.process_categories(input("\nEnter M3U Links (Comma separated): "))
            elif choice == "0":
                break
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    SM_IPTV_Advance().main_menu()
