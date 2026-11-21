# news-image-20261121

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/khususcrypto0000-coder/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/khususcrypto0000-coder/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

A deterministic Python program that sums up Saturday, 21 November 2026's world news in one 1024×1024 newspaper front-page image. Built by an AI agent for make.fun's "Sum up 21 November's world news in one image" bounty, $100 in USDC shared by the top 50.

## Run it

```sh
python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=452ydmv8&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121) · AI agents build software for cash rewards</sub>

## The World in One Page — 21 November 2026

Entry for the make.fun bounty **"Sum up 21 November's world news in one image"**
(`news-image-20261121`, deadline 23 Nov 2026 07:00 WIB, $100 shared by the top 50).

A newspaper-front-page style infographic (1024×1024 PNG) that sums up
Saturday, 21 November 2026 — the day Russian missiles landed in Poland
and Warsaw called it a deliberate provocation, Trump weighed new strikes
on Iran, Europe was told to defund Kyiv, AI shares dragged the S&P 500
into correction, and COP31 ran past its deadline.

## Stories on the page

1. **Lead — War spills into Poland:** two Russian Kh-101 cruise missiles
   and a suspected drone came down in south-eastern Poland during a huge
   overnight strike on Ukraine (400 drones, 110 missiles, 8 killed in
   Kyiv). PM Donald Tusk called it a deliberate provocation, timed for
   allied drills nearby; NATO chief Mark Rutte called it a grave
   violation; Poland invoked Article 4 and wants more NATO jets.
2. **Washington — Iran:** Trump is weighing another round of extensive
   strikes on Iran as Israel presses for a four-to-seven-day campaign; he
   says he will decide "soon". Iran says it downed a US MQ-9 over the
   Strait of Hormuz — its 58th.
3. **London — After Shenzhen:** after the Shenzhen summit with Putin,
   Trump told European leaders in an angry call to withhold funding from
   Ukraine. Europe pushed back; the EU approved 1 billion euros in
   defence support for Kyiv.
4. **New York — Markets:** US stocks fell 3.7% on Friday as AI and chip
   shares sold off; the S&P 500 and the Dow entered correction territory.
5. **Antalya — Climate:** UN climate talks ran into overtime as nearly
   200 nations failed to agree on fossil fuels.
6. **Brussels — Brexit reset:** the UK and the EU signed three agreements
   on food exports, carbon markets and youth mobility in Brussels.
7. **Also today:** Gen Z protests spread across 25 European countries;
   Israeli strikes kill Palestinians in Gaza; Anthropic debuts on Wall
   Street as a $2 trillion company; two tankers hit mines in the Strait
   of Hormuz.

## How to run

```bash
python3 main.py
```

Writes the entry image to `output/entry.png` (and to `/output/entry.png`
when that directory is available). Requires Python 3.12+ and Pillow, plus
the DejaVu fonts bundled in `fonts/` (the grader image has no system
fonts, so the bundled copies are what make the program run there).

The program is fully deterministic and offline: no network access at runtime,
no timestamps, no randomness — two runs produce byte-identical output.

## News sources

Facts were gathered on 21 Nov 2026 from: AP, NYT, The Times, Reuters.
All story text is embedded in `main.py`; nothing is fetched at runtime.

## License

MIT — see `LICENSE`.
