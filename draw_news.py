# draw_news.py — renders the 24 Nov 2026 world-news summary as a 1024x1024 PNG.
# Deterministic: same input -> same bytes. Run: python3 draw_news.py
# (build-time tool; the entry itself is entry.png + main.ts, which copies it.)
import textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

NAVY = (16, 36, 62)
INK = (20, 20, 20)
GREY = (90, 90, 90)
LIGHT = (191, 208, 228)
RED = (178, 34, 34)

# (region, accent colour, [(headline, summary, utc, caveat), ...])
REGIONS = [
    ("NORTH AMERICA", (31, 78, 121), [
        ("Trump pardons turkeys, vents on midterms", "At the Thanksgiving ceremony Trump pardons turkeys Freedom and Feathers, then rails about midterm losses.", "19:00", False),
        ("Trump backs ban on paid pardon lobbying", "Trump backs bills to make pardon brokers register after the Alina Habba lobbying scandal.", "18:00", False),
        ("Trump taps defeated prosecutor for judgeship", "Trump nominates Jim O'Neill, a North Carolina prosecutor who lost re-election, to a federal judgeship.", "17:00", False),
        ("Trump gives Giuliani Medal of Freedom", "Trump awards the nation's top civilian honour to Rudy Giuliani in a private Oval Office ceremony.", "18:30", False),
        ("Two states sue SpaceX over Grok deepfakes", "Virginia and Oregon, the first states to sue, say Grok made sexual images of real people, including children.", "10:00", True),
        ("Measles claims ninth life in Pennsylvania", "Pennsylvania reports a ninth measles death as the outbreak spreads across dozens of counties.", "12:00", False),
    ]),
    ("LATIN AMERICA", (46, 125, 50), [
        ("Colombia marks 10 years of peace deal", "UN chief hails a decade of the FARC peace accord but says its promises must still be fully kept.", "10:00", False),
        ("Car bomb blast hits Colombian city", "A car bomb outside a government office in Villavicencio damages buildings; officials dispute casualties.", "15:00", False),
        ("Drone strike hits Colombia police base", "A drone attack on a police base in Colombia injures civilians, including an infant, Al Jazeera reports.", "20:00", False),
        ("Mexico to try 'El Chapo Isidro' itself", "Mexico will prosecute cartel figure 'El Chapo Isidro' at home despite a US extradition request.", "18:00", False),
        ("WHO chief pledges $2m for Cuba vaccines", "WHO director-general Tedros visits Cuba's strained health system and pledges $2m for vaccinations.", "20:00", False),
        ("Lula snubs Milei over vote doubts", "Brazil's Lula will not invite Argentina's Milei to his January inauguration after doubts cast on his win.", "14:00", False),
    ]),
    ("EUROPE", (106, 27, 154), [
        ("Russian drone slips into Polish airspace", "A Russian jet drone flies eight minutes over Poland near Dorohusk; Warsaw clears a shootdown but holds fire.", "08:00", True),
        ("96 Russian drones rain on Ukraine", "Overnight barrage hits 13 sites; a Zaporizhzhia apartment strike kills two and wounds 40, incl. four children.", "06:00", False),
        ("Russia warns Estonia over border moves", "Moscow accuses NATO member Estonia of hostile acts 'on the verge of triggering open war'.", "13:00", False),
        ("700,000 Russian troops killed, study says", "A new analysis puts Russian military deaths above 700,000 in nearly five years of war.", "12:00", False),
        ("Germany gets access to Ukraine's Delta", "Berlin signs a letter of intent for Ukraine's Delta battlefield system, a first for any ally.", "14:00", False),
        ("Latvia sees Ukraine war tipping point", "Latvia's president says Russia's worsening economy may force it to end the war next year.", "11:00", False),
        ("COP31 collapses with no climate pact", "The Antalya summit ends without a deal as fossil-fuel language splits nations; Guterres calls it a setback.", "20:00", True),
    ]),
    ("MIDDLE EAST", (184, 92, 0), [
        ("Israel kills Hamas security chief in Gaza", "Israeli strikes kill Hamas internal security director Naeem Abu Nahel and six others in Gaza.", "12:00", False),
        ("Iran vows to fight US naval blockade", "Tehran calls the reinstated US blockade 'military aggression' and vows to use every tool against it.", "09:00", True),
        ("Iran lashes singer Parastoo Ahmadi", "Iran inflicts 74 lashes on singer Parastoo Ahmadi and four bandmates over a 2024 concert without hijab.", "09:00", True),
        ("Netanyahu pushes Trump to hit Iran again", "Israel's PM presses Trump to resume strikes on Iran as tensions over the blockade mount.", "16:00", False),
        ("Iraq moves to take over Kurdish oilfields", "Iraq's PM orders the oil ministry to manage fields in Kurdish-held areas, risking a new row.", "11:00", False),
        ("US weighs training Syrian deminers", "Washington is discussing training Syrian soldiers to clear landmines, Reuters reports.", "12:00", False),
        ("Huckabee doubts Israel aid cut will happen", "US envoy Huckabee says the $3.8bn annual military aid to Israel is set to run two more years.", "15:00", False),
    ]),
    ("AFRICA", (141, 110, 0), [
        ("Ebola teams trapped in Congo hospital", "WHO and Ebola responders shelter in an Ituri hospital maternity ward as fighting rages outside.", "10:00", False),
        ("Senegal gets AFCON title back in court", "Sport's top court overturns the forfeit ruling, restoring Senegal's Africa Cup title over Morocco.", "18:00", False),
        ("AU launches maternal health roadmap", "African leaders launch the AU's 2026-2030 maternal health roadmap in Addis Ababa.", "09:00", True),
        ("Gavi to buy 1.5m Ebola vaccine doses", "The vaccine alliance will buy 1.5 million doses of a new shot against the Bundibugyo Ebola strain.", "12:00", False),
        ("Madagascar seeks ex-president's arrest", "Madagascar seeks arrest warrants for ex-president Andry Rajoelina and a former PM.", "16:00", False),
        ("Amnesty: Tigray shelling may be war crimes", "Amnesty says Ethiopian artillery strikes on Tigray towns should be probed as possible war crimes.", "11:00", False),
        ("Ukraine says it sank Russian ship off Libya", "Kyiv confirms naval drones sank the Russian corvette Merkury in a Libyan port on Sunday.", "09:00", True),
    ]),
    ("SOUTH ASIA", (0, 105, 92), [
        ("5.6 quake rattles Nepal near China", "A magnitude 5.6 earthquake strikes Nepal's Koshi province near the Chinese border.", "08:00", False),
        ("India gives Nepal $1.62bn flood aid", "India pledges a $1.62bn package - its largest ever to Nepal - after August's deadly floods.", "09:00", True),
        ("WHO hails India's 10m HPV jabs", "WHO congratulates India on 10 million HPV doses for teen girls, a milestone against cervical cancer.", "09:00", True),
        ("Hasina plans return; Dhaka vows arrest", "Ousted PM Sheikh Hasina plans a Dec 16 return; Bangladesh says she will come back 'in handcuffs'.", "13:00", False),
        ("Teen smashes 204 off 53 balls for India A", "Vaibhav Sooryavanshi's 204 off 53 powers India A past UAE and into the Rising Stars semis.", "15:00", False),
        ("14 nations back Rohingya genocide ruling", "The UK, Spain, Canada, Australia and 10 others endorse the ICJ's genocide ruling on Myanmar.", "09:00", True),
    ]),
    ("EAST ASIA & ASIA-PACIFIC", (173, 20, 87), [
        ("Nvidia brings back Jensen Huang as CEO", "Nvidia reinstates Jensen Huang 11 days after he quit; Trump says he 'made the deal' with the board.", "23 Nov", True),
        ("Russian jets enter S. Korea defence zone", "Seoul scrambles jets and summons Moscow's attache after Russian aircraft enter its defence zone.", "02:00", False),
        ("S. Korea pays $375k to catch AI cheats", "Seoul offers up to $375,000 for tips on students using AI to cheat in the college entrance exam.", "10:00", False),
        ("China opens space station to Pakistani", "Pakistan's Zeeshan Ali will be the first foreign astronaut aboard China's Tiangong station.", "07:00", False),
        ("Solomons to drop China security pact", "The Solomon Islands will let its 2022 security pact with China lapse and sign a treaty with Australia.", "05:00", False),
        ("Indonesia factory fire toll hits 26", "Officials confirm 26 dead and 8 missing in the Banten candy factory fire; DNA tests to identify victims.", "06:00", True),
    ]),
]

# (hour, short label) for the timeline strip at the bottom
TIMELINE = [
    (2, "Russian jets enter S. Korea zone"),
    (5, "Solomons to drop China pact"),
    (6, "96 drones hit Ukraine"),
    (8, "Nepal quake 5.6"),
    (9, "Iran vows to fight blockade"),
    (12, "Gaza: Hamas security chief killed"),
    (15, "Teen hits 204 off 53"),
    (18, "Giuliani Medal of Freedom"),
    (19, "Trump pardons turkeys"),
    (20, "COP31 collapses"),
]


def sort_key(s):
    # † items (true date 22-23 Nov, led 24 Nov morning coverage) first, then by UTC hour
    utc = s[2]
    if utc == "23 Nov":
        return -60
    try:
        h, m = utc.split(":")
        return int(h) * 60 + int(m)
    except ValueError:
        return 0


def trunc(draw, text, font, width):
    if draw.textlength(text, font=font) <= width:
        return text
    while text and draw.textlength(text + "…", font=font) > width:
        text = text[:-1]
    return text + "…"


def main():
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    f_title = ImageFont.truetype(FONTB, 38)
    f_sub = ImageFont.truetype(FONT, 17)
    f_reg = ImageFont.truetype(FONTB, 12)
    f_head = ImageFont.truetype(FONTB, 12)
    f_sum = ImageFont.truetype(FONT, 10)
    f_time = ImageFont.truetype(FONTB, 9)
    f_foot = ImageFont.truetype(FONT, 10)

    # ---- header ----
    d.rectangle([0, 0, W, 96], fill=NAVY)
    d.rectangle([0, 96, W, 100], fill=RED)
    d.text((24, 12), "THE WORLD IN ONE DAY", font=f_title, fill="white")
    d.text((24, 62), "Tuesday, 24 November 2026  ·  45 stories from 7 regions  ·  Times UTC",
           font=f_sub, fill=LIGHT)

    # ---- body: two columns, regions in geographic order ----
    margin, gutter = 24, 20
    col_w = (W - 2 * margin - gutter) // 2
    col_x = [margin, margin + col_w + gutter]
    body_top = 108
    # A = NA, LatAm, Europe (19 stories); B = ME, Africa, SA, EA (26 stories)
    cols = [[0, 1, 2], [3, 4, 5, 6]]
    for ci, members in enumerate(cols):
        x = col_x[ci]
        y = body_top
        for ri in members:
            name, colour, stories = REGIONS[ri]
            stories = sorted(stories, key=sort_key)
            d.rectangle([x, y, x + col_w, y + 20], fill=colour)
            d.text((x + 8, y + 4), "%s  ·  %d" % (name, len(stories)), font=f_reg, fill="white")
            y += 20 + 3
            for (headline, summary, utc, caveat) in stories:
                hl = trunc(d, headline + ("  †" if caveat else ""), f_head, col_w - 46)
                sm = trunc(d, summary, f_sum, col_w - 46)
                d.text((x, y + 1), utc, font=f_time, fill=GREY)
                d.text((x + 44, y), hl, font=f_head, fill=INK)
                d.text((x + 44, y + 15), sm, font=f_sum, fill=GREY)
                y += 30
            y += 6

    # ---- footer ----
    d.text((margin, 1004), "Sources: Reuters · AP · BBC · Al Jazeera · UN News · WSJ · CNN  —  † = event from 22–23 Nov that led 24 Nov coverage.",
           font=f_foot, fill=GREY)

    img.save("entry.png", optimize=True)
    print("saved entry.png")


if __name__ == "__main__":
    main()
