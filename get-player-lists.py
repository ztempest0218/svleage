import re
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = "https://www.svleague.jp"
LIST_URL = "https://www.svleague.jp/ja/sv_men/team/list"

headers = {
    "User-Agent": "Mozilla/5.0"
}

def get_soup(url):
    print(f"データを取得中: {url}", flush=True)
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")

def clean_text(x):
    return re.sub(r"\s+", " ", x).strip()

soup = get_soup(LIST_URL)

team_links = []
for a in soup.select("a[href*='/ja/sv_men/team/detail/']"):
    team_name = clean_text(a.get_text())
    team_url = urljoin(BASE, a["href"])
    if team_name:
        team_links.append((team_name, team_url))

# 重複をチェック 10チーム
team_links = list(dict(team_links).items())[:10]
team_links = [(name, url) for name, url in team_links]

rows = []

for team_name, team_url in team_links:
    team_soup = get_soup(team_url)

    for a in team_soup.select("a[href*='/ja/sv_men/player/detail/']"):
        txt = clean_text(a.get_text())

        # 例: #2 OH 中道 優斗
        m = re.match(r"#?(\d+)\s+([A-Z]+)\s+(.+)", txt)
        if m:
            number, position, player_name = m.groups()
        else:
            number, position, player_name = "", "", txt

        rows.append({
            "team": team_name,
            "number": number,
            "position": position,
            "player_name": player_name,
            "player_text": txt,
            "team_url": team_url,
            "player_url": urljoin(BASE, a["href"])
        })

    time.sleep(1)

df = pd.DataFrame(rows)
df.to_csv("sv_men_players.csv", index=False, encoding="utf-8-sig")

print(f"完了：合計 {len(team_links)} チーム、{len(df)} 選手のデータを取得しました")
print("保存済み: sv_men_players.csv")