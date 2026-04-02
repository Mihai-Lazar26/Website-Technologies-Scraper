import pandas as pd
import requests
import re
import json
from concurrent.futures import ThreadPoolExecutor, as_completed


def load_domains(file_path):
    df = pd.read_parquet(file_path)
    return df["root_domain"].dropna().tolist()


def load_rules(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_html(domain):
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get("https://" + domain, headers=headers, timeout=5)
        return res.text.lower(), res.headers
    except:
        try:
            res = requests.get("http://" + domain, headers=headers, timeout=5)
            return res.text.lower(), res.headers
        except:
            return None, None


def normalize_name(name):
    # lowercase
    name = name.lower().strip()

    # elimină ce e între paranteze
    name = re.sub(r"\(.*?\)", "", name)

    # elimină versiuni: "ver: x.y.z", "v1.2.3", sau simplu "6.9.4"
    name = re.sub(r"\bver[: ]?\d+(\.\d+)*\b", "", name)
    name = re.sub(r"\bv\d+(\.\d+)*\b", "", name)
    name = re.sub(r"\s+\d+(\.\d+)*", "", name)

    # elimină ce e după ; sau - (descriere, detalii)
    name = re.split(r"[;-]", name)[0]

    name = re.sub(r"stt:.*$", "", name)  # elimină stt și ce urmează
    name = name.replace("powered by", "").strip()  # elimină powered by

    # whitespace cleanup
    name = name.strip()

    if "wix" in name:
        return "wix"

    return name


def detect_technologies(html, headers, rules):
    technologies = []

    if not html:
        return technologies

    for rule in rules:
        evidence = []

        for pattern in rule["patterns"]:
            if pattern in html:
                evidence.append(pattern)

        matches = len(evidence)
        total = len(rule["patterns"])

        confidence = matches / total if total > 0 else 0

        if matches >= rule.get("min_matches", 1) and confidence >= rule.get("min_confidence", 0):
            technologies.append({
                "name": rule["name"],
                "evidence": evidence,
                "confidence": round(confidence, 2)
            })

    generator = re.search(r'<meta name="generator" content="([^"]+)"', html)
    print("Generator: ", generator)
    if generator:
        technologies.append({
            "name": generator.group(1),
            "evidence": ["meta generator"],
            "confidence": 0.9
        })

    if headers:
        server = headers.get("server", "").lower()
        powered = headers.get("x-powered-by", "").lower()

        if "nginx" in server:
            technologies.append({
                "name": "Nginx",
                "evidence": ["server header"],
                "confidence": 0.9
            })

        if "apache" in server:
            technologies.append({
                "name": "Apache",
                "evidence": ["server header"],
                "confidence": 0.9
            })

        if "cloudflare" in server:
            technologies.append({
                "name": "Cloudflare",
                "evidence": ["server header"],
                "confidence": 0.9
            })

        if "express" in powered:
            technologies.append({
                "name": "Express",
                "evidence": ["x-powered-by"],
                "confidence": 0.9
            })

    return technologies


def process_domain(domain, rules):
    html, headers = fetch_html(domain)
    techs = detect_technologies(html, headers, rules)

    merged = {}

    for tech in techs:
        key = normalize_name(tech["name"])

        if key not in merged:
            merged[key] = {
                "name": tech["name"],
                "evidence": set(tech["evidence"]),
                "confidence": tech["confidence"]
            }
        else:
            merged[key]["evidence"].update(tech["evidence"])
            merged[key]["confidence"] = max(
                merged[key]["confidence"],
                tech["confidence"]
            )

    # convert set → list
    final_techs = [
        {
            "name": v["name"],
            "evidence": list(v["evidence"]),
            "confidence": v["confidence"]
        }
        for v in merged.values()
    ]

    return {
        "domain": domain,
        "technologies": final_techs
    }


def main():
    file_path = "part-00000-66e0628d-2c7f-425a-8f5b-738bcd6bf198-c000.snappy.parquet"

    domains = load_domains(file_path)

    rules = load_rules("rules.json")

    results = []

    all_technologies = set()

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_domain, d, rules) for d in domains]

        for future in as_completed(futures):
            result = future.result()
            print(result)

            for tech in result["technologies"]:
                normalized = normalize_name(tech["name"])
                if normalized:
                    all_technologies.add(normalized)

            results.append(result)

    print("\n--- UNIQUE TECHNOLOGIES ---")
    print(sorted(all_technologies))
    print(f"\nTotal unique technologies: {len(all_technologies)}")

    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    with open("technologies_summary.json", "w", encoding="utf-8") as f:
        json.dump({
            "unique_technologies": sorted(list(all_technologies)),
            "count": len(all_technologies)
        }, f, indent=2)


if __name__ == "__main__":
    main()
