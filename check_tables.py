import requests
from bs4 import BeautifulSoup

url = 'https://www.samcheok.go.kr/media/00084/00095.web?&cpage=1'
res = requests.get(url, verify=False)
soup = BeautifulSoup(res.text, 'html.parser')
tables = soup.select('table')

for i, table in enumerate(tables):
    print(f"Table #{i}: {len(table.find_all('tr'))} rows")
    
# Find announcement links
a_tags = soup.find_all('a')
announcement_links = []
for a in a_tags:
    text = a.get_text().strip()
    href = a.get('href', '')
    if text and href and len(text) > 10 and not any(nav in text.lower() for nav in ['메뉴', '로그인', '사이트맵']):
        announcement_links.append(f"- {text}")

if announcement_links:
    print("\nPotential announcement links:")
    for link in announcement_links[:15]:
        print(link)
