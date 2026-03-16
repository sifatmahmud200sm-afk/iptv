import requests
import os
import re
import subprocess
from rich.console import Console

console = Console()

# --- Config ---
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class SM_IPTV:
    def banner(self):
        os.system('clear')
        console.print("[bold cyan]⚡ SM IPTV CUSTOMIZE STABLE v11.0 ⚡[/bold cyan]")
        console.print("[white]Simple & Powerful | Category Wise | Auto-Sync[/white]\n")

    def github_sync(self):
        """Simple GitHub Push"""
        if os.path.exists(".git"):
            console.print("[dim][*] Syncing GitHub...[/dim]")
            os.system("git add . && git commit -m 'Update' && git push -u origin main")

    def fetch_m3u(self, urls_str):
        """Simple link fetching with fallback"""
        all_data = []
        urls = [u.strip() for u in urls_str.split(",") if u.strip()]
        
        headers = {'User-Agent': 'VLC/3.0.18 LibVLC/3.0.18'}
        
        for url in urls:
            try:
                console.print(f"[yellow][~] Loading: {url[:40]}...[/yellow]")
                r = requests.get(url, headers=headers, timeout=15)
                if r.status_code == 200:
                    # Regex for Category, Name, and Link
                    matches = re.findall(r'#EXTINF:.*?(?:group-title="(.*?)")?.*?,(.*?)\n(http.*?)(?:\n|$)', r.text)
                    for cat, name, link in matches:
                        category = cat if cat else "General"
                        # Filter Adult
                        if not any(x in name.lower() or x in category.lower() for x in ["adult", "sex", "xxx", "18+"]):
                            all_data.append({"cat": category.strip(), "name": name.strip(), "link": link.strip()})
                else:
                    console.print(f"[red][!] Server Error: {r.status_code}[/red]")
            except:
                console.print("[red][!] Connection Failed![/red]")
        return all_data

    # --- Option 1: All Channel ---
    def all_channel(self, urls):
        data = self.fetch_m3u(urls)
        if not data: return
        
        path = os.path.join(OUTPUT_DIR, "all_channels.m3u")
        # Direct write to avoid memory crash
        with open(path, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for ch in data:
                f.write(f"#EXTINF:-1,{ch['name']}\n{ch['link']}\n")
        
        console.print(f"[bold green]✔ Done! {len(data)} channels saved.[/bold green]")
        self.github_sync()

    # --- Option 2: Custom Category (Serial wise) ---
    def category_channel(self, urls):
        data = self.fetch_m3u(urls)
        if not data: return
        
        # Get unique categories
        categories = sorted(list(set([ch['cat'] for ch in data])))
        
        console.print("\n[bold yellow]Available Categories:[/bold yellow]")
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat}")
            
        choice = input("\nEnter Numbers (e.g., 125): ")
        # Convert choice string to indices
        try:
            indices = [int(i)-1 for i in choice if i.isdigit() and 0 < int(i) <= len(categories)]
        except: return

        for idx in indices:
            c_name = categories[idx]
            safe_file = c_name.replace(" ", "_").replace("/", "_") + ".m3u"
            cat_path = os.path.join(OUTPUT_DIR, safe_file)
            
            with open(cat_path, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                count = 0
                for ch in data:
                    if ch['cat'] == c_name:
                        f.write(f"#EXTINF:-1,{ch['name']}\n{ch['link']}\n")
                        count += 1
            console.print(f"[green]✔ {c_name} updated ({count} channels).[/green]")
        
        self.github_sync()

    def main(self):
        while True:
            self.banner()
            print("1. All Channel (Update)")
            print("2. Custom Category (Serial Selection)")
            print("0. Exit")
            
            opt = input("\n[>] Choice: ")
            if opt == "1":
                self.all_channel(input("\nEnter Links: "))
            elif opt == "2":
                self.category_channel(input("\nEnter Links: "))
            elif opt == "0": break
            input("\nPress Enter...")

if __name__ == "__main__":
    SM_IPTV().main()
