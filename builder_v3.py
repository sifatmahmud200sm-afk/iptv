import requests
import os
import re
import subprocess
import urllib3
import random
from rich.console import Console
from rich.panel import Panel

# SSL Warnings disable kora holo stability-r jonno
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

console = Console()
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class SM_IPTV_Ultimate:
    def __init__(self):
        # Apnar dewa Proxy List (Pool)
        self.proxy_pool = [
            "206.220.175.2:4145", "98.175.31.222:4145", "119.148.61.241:22122", 
            "72.207.33.64:4145", "46.146.204.175:1080", "119.148.1.222:22122",
            "119.148.47.166:22122", "107.152.98.5:4145", "208.65.90.21:4145",
            "174.75.211.222:4145", "192.252.220.89:4145", "184.181.217.201:4145",
            "98.191.0.47:4145", "216.68.128.121:4145", "192.252.209.155:14455",
            "208.102.51.6:58208", "68.1.210.163:4145", "89.167.118.3:1080",
            "68.71.249.158:4145", "184.170.249.65:4145", "199.102.106.94:4145",
            "72.205.0.93:4145", "142.54.235.9:4145", "192.252.209.158:4145",
            "104.37.135.145:4145", "199.116.114.11:4145", "185.21.141.238:1080",
            "192.252.220.92:17328", "142.54.239.1:4145", "199.58.185.9:4145",
            "116.118.18.41:443", "68.71.249.153:48606", "213.159.68.227:1080",
            "66.42.224.229:41679", "174.77.111.198:49547", "68.71.245.206:4145",
            "119.148.4.10:22122", "85.175.219.236:1080", "98.170.57.249:4145",
            "184.185.2.12:4145", "199.102.107.145:4145", "199.102.104.70:4145",
            "184.170.248.5:4145", "72.37.217.3:4145", "184.182.240.211:4145",
            "104.200.152.30:4145", "72.223.188.92:4145", "184.181.217.210:4145",
            "77.41.167.137:1080", "198.8.94.170:4145", "72.37.216.68:4145",
            "174.77.111.196:4145", "142.54.226.214:4145", "98.170.57.241:4145",
            "72.207.109.5:4145", "185.202.236.78:1080", "174.64.199.79:4145",
            "184.178.172.28:15294", "192.111.137.35:4145", "192.252.215.2:4145",
            "184.178.172.5:15303", "192.111.129.145:16894", "68.71.254.6:4145",
            "184.178.172.17:4145", "107.181.161.81:4145", "98.181.137.80:4145",
            "47.238.203.170:50000", "72.195.34.58:4145", "192.252.215.5:16137",
            "72.195.114.169:4145", "184.181.217.213:4145", "199.187.210.54:4145",
            "192.111.135.18:18301", "192.252.216.86:4145", "68.71.240.210:4145",
            "67.201.35.145:4145", "45.59.117.163:8080", "20.120.230.121:1080",
            "103.189.218.158:1080", "70.166.167.38:57728", "199.102.105.242:4145",
            "192.252.214.20:15864", "192.252.211.193:4145", "174.77.111.197:4145",
            "192.252.208.67:14287", "119.148.3.84:22122", "142.54.228.193:4145",
            "195.19.48.251:1080", "142.54.237.34:4145", "193.32.178.160:57329",
            "199.116.112.6:4145", "142.54.232.6:4145", "184.170.245.148:4145",
            "119.148.63.13:22122", "199.229.254.129:4145", "192.111.139.163:19404",
            "68.71.242.118:4145", "98.190.239.3:4145", "142.54.236.97:4145",
            "174.75.211.193:4145", "74.119.144.60:4145", "69.61.200.104:36181",
            "198.177.252.24:4145", "104.219.236.127:1080", "98.182.147.97:4145",
            "107.181.168.145:4145", "192.111.135.17:18302", "192.111.137.34:18765",
            "68.71.243.14:4145", "192.111.138.29:4145", "134.199.159.23:1080",
            "192.111.137.37:18762", "142.54.229.249:4145", "67.201.58.190:4145",
            "68.71.252.38:4145", "192.252.208.70:14282", "72.195.114.184:4145",
            "72.195.34.42:4145", "70.166.167.55:57745", "176.28.201.76:1080",
            "174.64.199.82:4145", "67.201.33.10:25283", "198.8.84.3:4145",
            "184.181.217.194:4145", "104.200.135.46:4145", "67.201.39.14:4145",
            "98.182.171.161:4145", "192.104.242.158:4145", "154.94.238.147:50161",
            "208.65.90.3:4145", "199.58.184.97:4145", "192.252.216.81:4145",
            "178.216.223.147:1080", "51.15.20.32:1088", "103.76.149.140:1080",
            "98.188.47.132:4145", "144.124.227.90:21074", "95.80.103.216:1080",
            "193.122.105.251:65535", "72.214.108.67:4145", "67.201.59.70:4145",
            "162.253.68.97:4145", "184.178.172.18:15280", "198.177.254.131:4145",
            "195.19.50.2:1080", "193.233.254.82:1080", "188.235.142.248:1080",
            "198.177.254.157:4145", "184.182.240.12:4145", "119.148.28.141:22122",
            "31.129.147.102:1080", "188.128.86.74:1080", "68.71.241.33:4145",
            "184.178.172.3:4145", "119.148.25.170:22122", "198.177.253.13:4145",
            "192.111.134.10:4145", "192.111.129.150:4145", "74.119.147.209:4145",
            "184.178.172.13:15311", "98.178.72.30:4145", "103.113.70.189:1081",
            "142.54.237.38:4145", "192.252.210.233:4145", "192.252.214.17:4145",
            "103.75.118.84:1080", "192.111.130.5:17002", "68.71.251.134:4145",
            "142.54.231.38:4145", "198.8.94.174:39078", "192.111.139.162:4145",
            "213.35.110.67:10808", "192.111.139.165:4145", "192.111.130.2:4145",
            "192.252.211.197:14921", "184.170.251.30:11288", "68.71.247.130:4145",
            "176.117.105.226:10820", "72.195.34.35:27360"
        ]
        self.user_agents = [
            'VLC/3.0.18 LibVLC/3.0.18',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'OTT-Player/1.1.5 (Android 12)'
        ]

    def banner(self):
        os.system('clear')
        # api.ipify.org logic to show current working IP
        try:
            current_ip = requests.get('https://api.ipify.org', timeout=5).text
        except:
            current_ip = "Unknown/Local"
            
        console.print(Panel.fit(
            f"[bold cyan]⚡ SM IPTV ULTIMATE v16.0 ⚡[/bold cyan]\n"
            f"[white]Active IP: {current_ip} | Proxy Pool: Loaded[/white]\n"
            f"[dim]Deep Scan | Anti-Reset | Professional Bypass[/dim]"
        ))

    def github_sync(self):
        """Standard GitHub Push logic"""
        if os.path.exists(".git"):
            console.print("[dim][*] Syncing GitHub...[/dim]")
            subprocess.run("git config --global credential.helper store", shell=True)
            os.system("git add . && git commit -m 'Auto-Update' && git push -u origin main")

    def get_content(self, url):
        """Fetch using Identity rotation and Proxy rotation from pool"""
        headers = {'User-Agent': random.choice(self.user_agents)}
        
        # Try different proxies from the pool if direct fails
        for _ in range(5): # Try 5 random proxies
            proxy = random.choice(self.proxy_pool)
            proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
            try:
                # Use stream for large M3U files
                res = requests.get(url, headers=headers, proxies=proxies, timeout=15, verify=False)
                if res.status_code == 200:
                    return res.text
            except:
                continue
        
        # Final fallback: direct attempt
        try:
            res = requests.get(url, headers=headers, timeout=15, verify=False)
            if res.status_code == 200: return res.text
        except:
            return None

    def deep_parse(self, urls_str):
        all_channels = []
        # Support for comma/space/newline separated links
        urls = [u.strip() for u in re.split(r'[,\s\n]+', urls_str) if u.strip()]
        
        for url in urls:
            console.print(f"[yellow][~] Bypassing & Scanning: {url[:45]}...[/yellow]")
            content = self.get_content(url)
            
            if content:
                # Professional Regex for group-title and #EXTGRP
                pattern = r'#EXTINF:.*?(?:group-title="(.*?)")?.*?,(.*?)\n(?:#EXTGRP:(.*?)\n)?(http.*?)(?:\n|$)'
                matches = re.findall(pattern, content)
                
                for g1, name, g2, link in matches:
                    category = g1 or g2 or "General"
                    # Filter Adult Content
                    if not any(x in name.lower() or x in category.lower() for x in ["adult", "sex", "porn", "xxx"]):
                        all_channels.append({"cat": category.strip().title(), "name": name.strip(), "link": link.strip()})
                console.print(f"[green]✔ Successfully parsed {len(matches)} channels.[/green]")
            else:
                console.print(f"[red][!] Connection Aborted for: {url[:30]}[/red]")
                
        return all_channels

    def process_all(self, urls):
        data = self.deep_parse(urls)
        if not data: return
        
        path = os.path.join(OUTPUT_DIR, "all_channels.m3u")
        with open(path, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for ch in data:
                f.write(f"#EXTINF:-1,{ch['name']}\n{ch['link']}\n")
        
        console.print("[bold green]✔ Final list updated on output/all_channels.m3u[/bold green]")
        self.github_sync()

    def process_categories(self, urls):
        data = self.deep_parse(urls)
        if not data: return
        
        categories = sorted(list(set([ch['cat'] for ch in data])))
        console.print("\n[bold yellow]Available Categories (Select Serial):[/bold yellow]")
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat}")
            
        choice = input("\nEnter Numbers (e.g. 125): ")
        indices = [int(i)-1 for i in choice if i.isdigit() and 0 < int(i) <= len(categories)]

        for idx in indices:
            cat_name = categories[idx]
            safe_name = "".join([c for c in cat_name if c.isalnum() or c in (' ', '_')]).replace(' ', '_')
            with open(os.path.join(OUTPUT_DIR, f"{safe_name}.m3u"), "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                for ch in data:
                    if ch['cat'] == cat_name:
                        f.write(f"#EXTINF:-1,{ch['name']}\n{ch['link']}\n")
            console.print(f"[green]✔ {cat_name} updated.[/green]")
        
        self.github_sync()

    def main(self):
        while True:
            self.banner()
            console.print("1. All Channel (Pool Proxy Scan)\n2. Category Wise (Deep Serial)\n0. Exit")
            opt = input("\n[>] Choice: ")
            if opt == "1":
                self.process_all(input("\nEnter Links: "))
            elif opt == "2":
                self.process_categories(input("\nEnter Links: "))
            elif opt == "0": break
            input("\nPress Enter...")

if __name__ == "__main__":
    SM_IPTV_Ultimate().main()
