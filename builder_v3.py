import requests
import os

print("Enter M3U playlist links (comma separated):")
links = input().split(",")

channels = []
seen = set()

print("Downloading playlists...")

for link in links:
    try:
        data = requests.get(link.strip(), timeout=20).text.splitlines()

        for i in range(len(data)):
            if data[i].startswith("#EXTINF"):
                name = data[i]
                url = data[i+1]

                if url not in seen:
                    seen.add(url)
                    channels.append((name, url))

        print("Loaded:", link)

    except:
        print("Failed:", link)

categories = {
"sports": ["sport","cricket","football","espn","bein"],
"news": ["news","cnn","bbc","aljazeera"],
"movies": ["movie","cinema","film"],
"kids": ["kids","cartoon","nick","disney"],
"music": ["music","song"],
"entertainment": ["tv","show"]
}

result = {k: [] for k in categories}
result["others"] = []

for name, url in channels:

    lname = name.lower()
    placed = False

    for cat, words in categories.items():

        if any(w in lname for w in words):
            result[cat].append((name, url))
            placed = True
            break

    if not placed:
        result["others"].append((name, url))

os.makedirs("output", exist_ok=True)

for cat, data in result.items():

    with open(f"output/{cat}.m3u", "w", encoding="utf8") as f:
        f.write("#EXTM3U\n")

        for n, u in data:
            f.write(n+"\n")
            f.write(u+"\n")

with open("output/all_channels.m3u", "w", encoding="utf8") as f:

    f.write("#EXTM3U\n")

    for n, u in channels:
        f.write(n+"\n")
        f.write(u+"\n")

print("All playlists created inside output folder")

mode = input("Custom filter? (yes/no): ")

if mode == "yes":

    keyword = input("Enter keyword: ").lower()

    filtered = [c for c in channels if keyword in c[0].lower()]

    with open(f"output/{keyword}.m3u", "w", encoding="utf8") as f:

        f.write("#EXTM3U\n")

        for n, u in filtered:
            f.write(n+"\n")
            f.write(u+"\n")

    print("Custom playlist created:", keyword+".m3u")
