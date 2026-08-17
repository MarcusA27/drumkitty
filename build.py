"""Inject shared partials and generated markup into the static pages.

Injects the shared header into every page, the sample list (with waveform
peaks baked into inline SVG) into each kit page, and the kit grid into the
homepage. Run after editing partials/ or adding or renaming samples:

    python3 build.py

To add a kit: drop the renamed wavs in assets/kits/<slug>/, add an entry to
KITS below, and copy an existing kit page to kits/<slug>.html as a starting point.
"""

import re
import struct
import wave
from pathlib import Path

ROOT = Path(__file__).parent

KITS = [
    {
        "slug": "2am",
        "title": "2AM",
        "genre": "rnb rap",
        "art": "assets/cards/2am.webp",
        "in_grid": True,
        "groups": [
            ("808", "808", ["808-punchy-01", "808-punchy-02", "808-punchy-03", "808-punchy-04"]),
            ("Kick", "kick", ["kick-hiphop", "kick-hiphop-punchy", "kick-punchy-01", "kick-punchy-02"]),
            ("Snare", "snare", ["snare-hiphop", "snare-punchy-01", "snare-punchy-02", "snare-punchy-03"]),
            ("Clap", "clap", ["clap-hiphop", "clap-hiphop-smooth", "clap-oneshot-01", "clap-oneshot-02"]),
            ("Hat", "hat", ["hat-smooth-01", "hat-smooth-02", "hat-smooth-03", "hat-smooth-04"]),
            ("Perc", "perc", ["perc-modern-01", "perc-modern-02", "perc-sharp"]),
        ],
    },
    {
        "slug": "halo",
        "title": "Halo",
        "genre": "pluggnb",
        "art": "assets/cards/halo.webp",
        "in_grid": True,
        "groups": [
            ("808", "808", ["808-punchy-01", "808-punchy-02", "808-punchy-03", "808-deep"]),
            ("Kick", "kick", ["kick-plugg-01", "kick-plugg-02", "kick-plugg-03", "kick-punchy"]),
            ("Snare", "snare", ["snare-plugg-01", "snare-plugg-02", "snare-plugg-03", "snare-plugg-04"]),
            ("Clap", "clap", ["clap-crisp-01", "clap-crisp-02", "clap-oneshot-01", "clap-oneshot-02"]),
            ("Hat", "hat", ["hat-bright-01", "hat-bright-02", "hat-bright-03", "hat-plugg"]),
            ("Perc", "perc", ["perc-plugg-01", "perc-plugg-02", "perc-tight"]),
        ],
    },
    {
        "slug": "bando",
        "title": "Bando",
        "genre": "trap",
        "art": "assets/cards/bando.webp",
        "in_grid": True,
        "groups": [
            ("808", "808", ["808-punchy-01", "808-punchy-02", "808-punchy-03", "808-punchy-04"]),
            ("Kick", "kick", ["kick-punchy-01", "kick-punchy-02", "kick-trap-punchy", "kick-trappy"]),
            ("Snare", "snare", ["snare-trap-sharp-01", "snare-trap-sharp-02", "snare-oneshot-01", "snare-oneshot-02"]),
            ("Clap", "clap", ["clap-sharp-01", "clap-sharp-02", "clap-trap-sharp-01", "clap-trap-sharp-02"]),
            ("Hat", "hat", ["hat-sharp-01", "hat-sharp-02", "hat-oneshot-01", "hat-oneshot-02"]),
            ("Perc", "perc", ["perc-metallic-01", "perc-metallic-02", "perc-metallic-03", "perc-sharp"]),
        ],
    },
    {
        "slug": "redline",
        "title": "Redline",
        "genre": "rage trap",
        "art": "assets/cards/redline.webp",
        "in_grid": True,
        "groups": [
            ("808", "808", ["808-distorted-01", "808-distorted-02", "808-distorted-03", "808-distorted-04"]),
            ("Kick", "kick", ["kick-trap-01", "kick-trap-02", "kick-trap-03", "kick-trap-04"]),
            ("Snare", "snare", ["snare-agg-01", "snare-agg-02", "snare-oneshot-01", "snare-oneshot-02"]),
            ("Clap", "clap", ["clap-agg-01", "clap-agg-02", "clap-agg-03", "clap-agg-04"]),
            ("Hat", "hat", ["hat-agg-01", "hat-agg-02", "hat-oneshot-01", "hat-oneshot-02"]),
            ("Perc", "perc", ["perc-agg-01", "perc-agg-02", "perc-agg-03", "perc-agg-04"]),
        ],
    },
    {
        "slug": "drift",
        "title": "Drift",
        "genre": "ambient chill",
        "art": "assets/cards/drift.webp",
        "in_grid": True,
        "groups": [
            ("808", "808", ["808-deep-01", "808-deep-02", "808-deep-03", "808-ambient"]),
            ("Kick", "kick", ["kick-ambient-01", "kick-ambient-02", "kick-ambient-03", "kick-ambient-04"]),
            ("Snare", "snare", ["snare-ambient-01", "snare-ambient-02", "snare-oneshot-01", "snare-oneshot-02"]),
            ("Clap", "clap", ["clap-ambient-01", "clap-ambient-02", "clap-ambient-03", "clap-soft"]),
            ("Hat", "hat", ["hat-ambient", "hat-soft", "hat-oneshot-01", "hat-oneshot-02"]),
            ("Perc", "perc", ["perc-ambient-01", "perc-ambient-02", "perc-ambient-03", "perc-soft"]),
        ],
    },
    {
        "slug": "vhs",
        "title": "VHS",
        "genre": "vintage drums",
        "art": "assets/cards/vhs.webp",
        "in_grid": True,
        "groups": [
            ("Kick", "kick", ["bdr-01", "bdr-02", "bdr-04", "bdr-06", "bdr-09", "bdr-10", "bdr-101", "bdr-102", "bdr-103", "bdr-104", "bdr-107", "bdr-109", "bdr-201", "bdr-202", "bdr-204"]),
            ("Snare", "snare", ["sdr-01", "sdr-02", "sdr-03", "sdr-05", "sdr-07", "sdr-08", "sdr-09", "sdr-10", "sdr-101", "sdr-102", "sdr-103", "sdr-104", "sdr-105", "sdr-106", "sdr-107", "sdr-110", "sdr-200", "sdr-201", "sdr-202", "sdr-203", "sdr-204", "sdr-205"]),
            ("Hat", "hat", ["hcr-01", "hcr-02"]),
            ("Tom", "tom", ["tom-02", "tom-03"]),
            ("Perc", "perc", ["pcr-209", "pcr-210"]),
            ("Melodic / FX", "melodic-fx", ["hor-01"]),
            ("Other Drums", "drums", ["dr-04"]),
        ],
    },
]

BARS = 120


def read_mono(path):
    with wave.open(str(path), "rb") as w:
        channels, width, rate, frames = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        raw = w.readframes(frames)

    if width == 2:
        vals = struct.unpack("<%dh" % (len(raw) // 2), raw)
        scale = 32768.0
    elif width == 3:
        vals = []
        for i in range(0, len(raw), 3):
            v = raw[i] | (raw[i + 1] << 8) | (raw[i + 2] << 16)
            if v & 0x800000:
                v -= 0x1000000
            vals.append(v)
        scale = 8388608.0
    else:
        raise SystemExit("unhandled sample width %d in %s" % (width, path))

    if channels > 1:
        vals = [max(vals[i:i + channels], key=abs) for i in range(0, len(vals) - channels + 1, channels)]
    return [v / scale for v in vals], frames / float(rate)


def peaks(samples, bars=BARS):
    if not samples:
        return [0.0] * bars
    step = len(samples) / float(bars)
    out = []
    for i in range(bars):
        chunk = samples[int(i * step):max(int((i + 1) * step), int(i * step) + 1)]
        out.append(max(abs(v) for v in chunk) if chunk else 0.0)
    top = max(out) or 1.0
    # gentle curve so the quiet tail of a decay stays visible
    return [(v / top) ** 0.65 for v in out]


def svg(vals):
    # one vertical stroke per bar; 2 units wide on a 4-unit pitch
    segs = []
    for i, v in enumerate(vals):
        half = max(round(v * 46), 1)
        segs.append("M%d %dV%d" % (i * 4, 50 - half, 50 + half))
    return (
        '<svg class="sample__wave" viewBox="0 0 %d 100" preserveAspectRatio="none" aria-hidden="true">'
        '<path d="%s"/></svg>' % (BARS * 4 - 2, "".join(segs))
    )


def sample_rows(kit):
    rows = []
    for label, folder, names in kit["groups"]:
        rows.append('        <p class="samples__group">%s</p>' % label)
        rows.append('        <ul class="samples__list">')
        for name in names:
            path = ROOT / "assets/kits" / kit["slug"] / folder / ("%s.wav" % name)
            if not path.exists():
                raise SystemExit("missing sample: %s" % path.relative_to(ROOT))
            mono, seconds = read_mono(path)
            rows.append(
                '          <li><button class="sample" type="button" data-src="../assets/kits/%s/%s/%s.wav">'
                '<span class="sample__icon" aria-hidden="true"></span>'
                '<span class="sample__name">%s</span>%s'
                '<span class="sample__time">%.2fs</span></button></li>'
                % (kit["slug"], folder, name, name, svg(peaks(mono)), seconds)
            )
        rows.append("        </ul>")
    return "\n".join(rows)


def grid_cards():
    cards = []
    for kit in KITS:
        if not kit["in_grid"]:
            continue
        card_class = "kit-card kit-card--featured" if kit.get("featured") else "kit-card"
        label = '            <span class="kit-card__label">Featured kit</span>\n' if kit.get("featured") else ""
        cards.append(
            '        <li class="%s">\n'
            '          <a class="kit-card__link" href="kits/%s.html">\n'
            '%s'
            '            <img class="kit-card__art" src="%s" alt="%s %s drum kit cover art" loading="lazy" decoding="async">\n'
            '            <span class="kit-card__name">%s</span>\n'
            '            <span class="kit-card__genre">%s</span>\n'
            "          </a>\n"
            "        </li>"
            % (card_class, kit["slug"], label, kit["art"], kit["title"], kit["genre"], kit["title"], kit["genre"])
        )
    return "\n".join(cards)


def splice(html, marker, body, page):
    pattern = r"(<!-- %s:start -->).*?(\n\s*<!-- %s:end -->)" % (marker, marker)
    if not re.search(pattern, html, flags=re.S):
        raise SystemExit("marker %r not found in %s" % (marker, page.name))
    return re.sub(pattern, lambda m: m.group(1) + "\n" + body + m.group(2), html, flags=re.S)


def render(partial, tokens):
    text = (ROOT / "partials" / partial).read_text().rstrip("\n")
    for key, value in tokens.items():
        text = text.replace("{{%s}}" % key, value)
    left = re.findall(r"{{(\w+)}}", text)
    if left:
        raise SystemExit("unreplaced tokens in %s: %s" % (partial, ", ".join(sorted(set(left)))))
    return text


def masthead(base, home):
    return (
        '  <header class="masthead">\n'
        '    <button class="menu-toggle" type="button" aria-label="Open menu" aria-controls="site-menu" aria-expanded="false">\n'
        '      <span aria-hidden="true"></span>\n'
        '      <span aria-hidden="true"></span>\n'
        '    </button>\n'
        '    <a class="brand" href="%s">\n'
        '      <img class="brand__mark" src="%sassets/drumkitty.png" alt="">\n'
        '      <span class="brand__name">drumkitty</span>\n'
        '    </a>\n'
        '  </header>'
    ) % (home, base)


index = ROOT / "index.html"
html = index.read_text()
html = splice(html, "header", render("header.html", {"base": "", "masthead": masthead("", "/")}), index)
html = splice(html, "footer", render("footer.html", {"base": "", "home": "/"}), index)
html = splice(html, "kits", grid_cards(), index)
index.write_text(html)
print("built index.html")

about = ROOT / "about.html"
html = about.read_text()
html = splice(html, "header", render("header.html", {"base": "", "masthead": masthead("", "/")}), about)
html = splice(html, "footer", render("footer.html", {"base": "", "home": "/"}), about)
about.write_text(html)
print("built about.html")

for kit in KITS:
    page = ROOT / "kits" / ("%s.html" % kit["slug"])
    if not page.exists():
        raise SystemExit("missing page for kit %r: %s" % (kit["slug"], page.relative_to(ROOT)))
    html = page.read_text()
    html = splice(html, "header", render("header.html", {"base": "../", "masthead": masthead("../", "../")}), page)
    html = splice(html, "footer", render("footer.html", {"base": "../", "home": "../"}), page)
    html = splice(html, "samples", sample_rows(kit), page)
    page.write_text(html)
    print("built kits/%s.html (%d samples)" % (kit["slug"], sum(len(g[2]) for g in kit["groups"])))
