# dmrid_download

A Python script that downloads the global DMR ID contact database from [RadioID.net](https://radioid.net) and reformats it for import into the **Radtel RT-4D** radio's CPS address book.

---

## Inspiration and Credit

This script was directly inspired by the excellent guide published by **W1AEX** at:

> **https://www.w1aex.com/dmrid/dmrid.html**

W1AEX identified the problem, worked out every transformation step by hand using tools like CSVed and Notepad++, and documented the entire process clearly for the RT-4D community. This script simply automates what W1AEX described — all credit for the underlying method belongs to him. Thank you, W1AEX, for doing the hard work of figuring this out and sharing it!

---

## The Problem

The Radtel RT-4D is a capable DMR handheld, but its display and address book have strict constraints:

- **3 display lines**, each limited to **18 characters**
- The address book has a maximum capacity of **12,289 KB**

The raw contact database from RadioID.net is far too large and poorly structured to load directly onto the radio. Field values are long and unabbreviated, unnecessary columns waste space, and the name fields are split across two columns in a way the RT-4D cannot use efficiently.

The goal of this script is to shrink and reshape the data so it fits within the radio's limits while still displaying cleanly on those three small lines.

---

## The Data Source — RadioID.net

[RadioID.net](https://radioid.net) is the definitive community-maintained registry of **DMR IDs** (Digital Mobile Radio identifiers) for amateur radio operators worldwide.

### What is a DMR ID?

DMR is a digital voice mode widely used in amateur radio. Every licensed operator who wants to use DMR networks (such as Brandmeister, DMR-MARC, or TGIF) needs a unique numeric ID — their **DMR ID** or **Radio ID**. These IDs are issued and recorded at RadioID.net after verification against official amateur radio licence databases.

### The `user.csv` data dump

RadioID.net publishes a full export of its user database at:

```
https://radioid.net/static/user.csv
```

This file is updated regularly and contains one row per registered DMR operator, with the following columns:

| Column | Description |
|---|---|
| `RADIO_ID` | Unique numeric DMR ID assigned to the operator |
| `CALLSIGN` | The operator's amateur radio callsign |
| `FIRST_NAME` | First name |
| `LAST_NAME` | Last/family name |
| `CITY` | City of registration |
| `STATE` | State, province, or region |
| `COUNTRY` | Country of registration |

The database covers **hundreds of thousands of operators across more than 150 countries**, making it one of the most comprehensive amateur radio operator datasets publicly available. Because it is community-driven and tied to real licence verification, it reflects the actual active DMR population on air at any given time.

---

## What the Script Does

The following transformations are applied, exactly as described in W1AEX's guide:

1. **Downloads** `user.csv` via streaming (the file is large — typically several hundred MB)
2. **Validates** that the column structure matches the expected format, failing loudly if RadioID.net changes its schema
3. **Merges** `FIRST_NAME` and `LAST_NAME` into a single field, truncated to **18 characters**
4. **Clears** the `LAST_NAME` column (left blank in the output)
5. **Removes** the `CITY` column entirely
6. **Abbreviates** long country names to 2–3 letter codes (see table below)
7. **Truncates** the `STATE` field to **14 characters**
8. **Adds** an empty trailing column (as required by the RT-4D CPS format)
9. **Writes** the result to `user_rt4d.csv`
10. **Reports** the output file size and warns if it exceeds the RT-4D's 12,289 KB address book limit

### Output column order

```
RADIO_ID | CALLSIGN | FIRST_NAME | LAST_NAME | STATE | COUNTRY | (empty)
```

### Country abbreviations applied

| Original name | Code |
|---|---|
| United States | USA |
| Netherlands | NLD |
| Czech Republic | CZE |
| United Kingdom | GBR |
| Germany | DEU |
| Korea Republic of | ROK |
| Australia | AUS |
| Philippines | PHL |
| New Zealand | NZL |
| Argentina Republic | ARG |
| Slovenia | SVN |
| Bosnia and Hercegovina | BIH |
| Greece | GRC |
| Belgium | BEL |
| France | FRA |
| Denmark | DNK |
| Portugal | PRT |
| Türkiye | TUR |

Any country not in this table is passed through unchanged.

---

## Requirements

- Python 3.8+
- [`requests`](https://pypi.org/project/requests/)

Install the dependency:

```bash
pip install requests
```

---

## Usage

```bash
# Basic usage — writes user_rt4d.csv in the current directory
python dmrid_download.py

# Specify a custom output path
python dmrid_download.py --output /path/to/my_contacts.csv

# Keep the raw downloaded file for inspection
python dmrid_download.py --keep-download
```

### Options

| Flag | Default | Description |
|---|---|---|
| `--output` | `user_rt4d.csv` | Path for the reformatted output file |
| `--keep-download` | off | Retain the raw downloaded CSV instead of deleting it after processing |

---

## Importing into the RT-4D CPS

1. Open the RT-4D CPS software
2. Navigate to **Address Book**
3. Use the **Import** function and select the generated `user_rt4d.csv`
4. Write to radio

---

## License

MIT
