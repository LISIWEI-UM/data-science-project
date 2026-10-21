"""Analyze the attributed source table; create two portable, original charts.

Python 3.10+; Pillow is the only external dependency. No credentials required.
"""
import argparse
import csv
import hashlib
import io
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'https://messixronaldo.com/calendar-year-stats'
FIELDS = ['year', 'messi_goals', 'messi_assists', 'messi_apps',
          'ronaldo_goals', 'ronaldo_assists', 'ronaldo_apps']
COLORS = {'Messi': '#167d9a', 'Ronaldo': '#bf562f'}


class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows, self.row, self.cell = [], [], None

    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            self.row = []
        elif tag in ('td', 'th'):
            self.cell = ''

    def handle_data(self, data):
        if self.cell is not None:
            self.cell += data

    def handle_endtag(self, tag):
        if tag in ('td', 'th') and self.cell is not None:
            self.row.append(self.cell.strip())
            self.cell = None
        elif tag == 'tr' and len(self.row) == 7:
            self.rows.append(self.row)


def download():
    parser = TableParser()
    request = Request(SOURCE, headers={'User-Agent': 'CISC7204-Educational-Analysis/1.0'})
    with urlopen(request, timeout=30) as response:
        parser.feed(response.read().decode('utf-8'))
    rows = []
    for cells in parser.rows:
        if cells[0].isdigit() and 2002 <= int(cells[0]) <= 2025:
            values = [int(v) if v.isdigit() else None for v in cells]
            rows.append(dict(zip(FIELDS, values)))
    return rows


def validate(rows):
    rows.sort(key=lambda row: row['year'])
    if [row['year'] for row in rows] != list(range(2002, 2026)):
        raise ValueError('Expected exactly one row per year, 2002–2025.')
    for row in rows:
        for who in ('messi', 'ronaldo'):
            values = [row[f'{who}_{key}'] for key in ('goals', 'assists', 'apps')]
            if who == 'messi' and row['year'] < 2004:
                if values != [None, None, None]:
                    raise ValueError('Expected missing pre-debut Messi observations.')
            elif any(not isinstance(v, int) or v < 0 for v in values) or values[2] == 0:
                raise ValueError(f'Invalid observation: {row}')


def font(size):
    for name in ('DejaVuSans.ttf', 'C:/Windows/Fonts/segoeui.ttf'):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def canvas(title, subtitle):
    image = Image.new('RGB', (1500, 960), '#fcfbf7')
    d = ImageDraw.Draw(image)
    d.text((80, 45), title, fill='#142a33', font=font(42))
    d.text((80, 112), subtitle, fill='#52646b', font=font(23))
    d.text((80, 859), 'Source: messixronaldo.com/calendar-year-stats | 2002–2025 source snapshot', fill='#52646b', font=font(20))
    d.text((80, 899), 'Descriptive source-table analysis; not independently audited career totals.', fill='#52646b', font=font(20))
    return image, d


def charts(rows, summary):
    image, d = canvas('Change the metric. Change the leader.', 'Totals across the source table; each player’s available years. G+A = goals + assists.')
    left, scale = 320, 1040 / 1400
    for i, (key, label) in enumerate([('goals', 'Goals'), ('assists', 'Assists'), ('ga', 'Goals + assists')]):
        y = 218 + i * 192
        d.text((80, y + 22), label, fill='#142a33', font=font(26))
        for j, who in enumerate(COLORS):
            yy, value = y + j * 66, summary[who][key]
            d.rectangle((left, yy, left + value * scale, yy + 43), fill=COLORS[who])
            d.text((left + value * scale + 14, yy + 5), str(value), fill='#142a33', font=font(23))
    d.text((320, 170), 'Messi (teal)  /  Ronaldo (orange)', fill='#142a33', font=font(22))
    image.save(ROOT / 'figures' / 'metric_comparison.png')
    image, d = canvas('A peak and a plateau', 'Goals per calendar year; missing pre-debut Messi years are left blank.')
    x0, y0, width, height = 115, 735, 1280, 500
    for value in (0, 20, 40, 60, 80, 100):
        y = y0 - value * height / 100
        d.line((x0, y, x0 + width, y), fill='#d9e0df', width=2)
        d.text((60, y - 12), str(value), fill='#52646b', font=font(22))
    for who in COLORS:
        points = [(x0 + (row['year'] - 2002) * width / 23, y0 - row[f'{who.lower()}_goals'] * height / 100)
                  for row in rows if row[f'{who.lower()}_goals'] is not None]
        d.line(points, fill=COLORS[who], width=6)
        for x, y in points:
            d.ellipse((x-5, y-5, x+5, y+5), fill=COLORS[who])
    for year in (2002, 2006, 2010, 2014, 2018, 2022, 2025):
        x = x0 + (year - 2002) * width / 23
        d.text((x - 25, y0 + 15), str(year), fill='#52646b', font=font(22))
    d.text((115, 178), 'Messi: 91 goals in 2012     |     Ronaldo: 69 goals in 2013', fill='#142a33', font=font(24))
    d.text((900, 785), 'Messi (teal) / Ronaldo (orange)', fill='#142a33', font=font(22))
    image.save(ROOT / 'figures' / 'annual_goals.png')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=Path, help='Optional local CSV with the documented schema')
    args = parser.parse_args()
    if args.data:
        with args.data.open(encoding='utf-8-sig', newline='') as fh:
            rows = [{key: int(value) if value.strip() else None for key, value in row.items()}
                    for row in csv.DictReader(fh)]
    else:
        rows = download()
    validate(rows)
    canonical = json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()
    digest = hashlib.sha256(canonical).hexdigest()
    expected = 'bb4fff0129c81656889772206fb58e40acb6456d27db8ddec052483d47d1de3f'
    if digest != expected:
        raise ValueError(f'Source has changed: {digest}. Review the source before updating the documented snapshot.')
    summary = {}
    for who in COLORS:
        prefix = who.lower()
        active = [r for r in rows if r[f'{prefix}_goals'] is not None]
        result = {key: sum(r[f'{prefix}_{key}'] for r in active) for key in ('goals', 'assists', 'apps')}
        result['ga'] = result['goals'] + result['assists']
        result['ga_per_app'] = round(result['ga'] / result['apps'], 3)
        result['years_40_plus'] = sum(r[f'{prefix}_goals'] >= 40 for r in active)
        summary[who] = result
    (ROOT / 'figures').mkdir(exist_ok=True)
    charts(rows, summary)
    output = {'source': SOURCE, 'window': '2002–2025', 'sha256': digest, 'players': summary}
    (ROOT / 'results.json').write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
