# Website Technologies Scraper

## 📌 Overview

This project is a Python-based tool that detects technologies used by websites.
It processes a list of domains, fetches their HTML and headers, and identifies technologies such as CMS, frameworks, analytics tools, and servers.

The final output includes:

* Technologies detected per domain
* A global list of unique technologies
* Total number of distinct technologies

---

## 🚀 Features

* Detects 20+ technologies (WordPress, React, Angular, etc.)
* Uses multiple detection strategies:

  * HTML pattern matching
  * Meta tags (e.g. generator)
  * HTTP headers
* Removes duplicates per domain
* Normalizes technology names (e.g. "WordPress 6.9.4" → "wordpress")
* Aggregates unique technologies across all domains
* Parallel processing for faster execution
* Outputs results in JSON format

---

## 🧩 Production Considerations

* Handles HTTP/HTTPS fallback and request failures
* Uses timeouts to prevent blocking requests
* Modular structure for easy extension (rules, normalization, detection)
* Scalable through parallel processing

---

## 🛠️ Tech Stack

* Python 3
* pandas (for reading parquet files)
* requests (for HTTP requests)
* concurrent.futures (for parallelism)
* re (regex for parsing and normalization)

---

## 📂 Project Structure

```
.
├── tech_scraper.py        # Main script
├── rules.json             # Detection rules
├── output.json            # Per-domain results
├── technologies_summary.json  # Unique technologies + count
└── README.md
```

---

## ⚙️ How It Works

### 1. Load Domains

Reads a `.parquet` file containing domain names.

### 2. Fetch Data

For each domain:

* Tries HTTPS, then HTTP
* Extracts HTML and headers

### 3. Detect Technologies

Uses:

* Pattern matching from `rules.json`
* Meta tags (e.g. `<meta name="generator">`)
* HTTP headers (`Server`, `X-Powered-By`)

### 4. Normalize & Deduplicate

* Removes versions and extra metadata
* Merges duplicate detections per domain

### 5. Aggregate Results

* Builds a global set of unique technologies
* Counts total distinct technologies

---

## ▶️ How to Run

### 1. Create virtual environment

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows
```

### 2. Install dependencies

```bash
pip install pandas requests pyarrow
```

### 3. Run script

```bash
python tech_scraper.py
```

---

## 📊 Output

### Per-domain results (`output.json`)

```json
{
  "domain": "example.com",
  "technologies": [
    {
      "name": "WordPress",
      "evidence": ["wp-content"],
      "confidence": 1.0
    }
  ]
}
```

### Global summary (`technologies_summary.json`)

```json
{
  "unique_technologies": [
    "wordpress",
    "react",
    "nginx"
  ],
  "count": 3
}
```

---

## 🧠 Design Decisions

* **Multi-signal detection**: Combines HTML, meta tags, and headers for better accuracy
* **Normalization**: Ensures consistent naming (e.g. removes versions and noise)
* **Deduplication**: Prevents counting the same technology multiple times
* **Parallelism**: Improves performance when processing many domains

---

## ⚖️ Discussion / Trade-offs

During development, several trade-offs were considered in order to balance simplicity, performance, and accuracy:

* **Accuracy vs Simplicity**
  The detection is based on heuristic rules (pattern matching, meta tags, headers).
  This keeps the implementation simple and fast, but may miss some technologies or introduce false positives.

* **Multiple Signals vs Noise**
  Combining HTML, meta tags, and headers improves detection coverage.
  However, it can also introduce redundant or noisy detections, which required additional deduplication logic.

* **Normalization vs Detail**
  Technology names are normalized (e.g. removing versions like "WordPress 6.9.4")
  to ensure consistent aggregation across domains.
  This improves counting accuracy but removes detailed information such as versions.

* **Performance vs Reliability**
  Parallel processing significantly speeds up execution when analyzing many domains.
  However, some requests may fail due to timeouts or server restrictions.

* **Heuristic Detection Limits**
  Some technologies (especially backend ones) may not be detectable from HTML or headers alone,
  making the results best-effort rather than exhaustive.

---

## ⚠️ Limitations

* Some technologies may not be detectable if hidden
* Detection is based on heuristics (may produce false positives)
* Normalization rules are simplified and can be improved further

---

## 🔮 Future Improvements

* More advanced normalization (mapping aliases)
* Technology version extraction
* Frequency statistics (top technologies)
* Export to CSV
* Improved detection rules

---
