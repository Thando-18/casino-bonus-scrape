import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import scraper  # noqa: E402

FIXTURE = (Path(__file__).parent / "fixtures" / "sample_page.html").read_text(encoding="utf-8")
URL = "https://example.test/page"


def fake_client(payload):
    msg = SimpleNamespace(content=json.dumps(payload))
    create = lambda **_: SimpleNamespace(choices=[SimpleNamespace(message=msg)])  # noqa: E731
    return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))


def test_scrape_rows_picks_targets_in_stable_order_and_dedupes():
    rows = scraper.scrape_rows(FIXTURE, URL)
    assert [r["casino_name"] for r in rows] == ["Hollywoodbets", "Supabets", "Playabets"]
    assert rows[0]["bonus_terms"] == "TEST bonus A"
    assert rows[0]["minimum_deposit_terms"] == "R50"
    assert all(r["source_url"] == URL for r in rows)


def test_scrape_rows_handles_reordered_columns():
    html = """<table><tr><th>Min Deposit</th><th>Casino</th><th>Wagering</th><th>Bonus</th></tr>
    <tr><td>R5</td><td>Hollywoodbets</td><td>2x</td><td>B</td></tr></table>"""
    row = scraper.scrape_rows(html, URL)[0]
    assert (row["minimum_deposit_terms"], row["bonus_terms"], row["wagering_terms"]) == ("R5", "B", "2x")


def test_scrape_rows_returns_empty_when_markup_changes():
    assert scraper.scrape_rows("<div>no tables</div>", URL) == []


def row(wager="TEST 5x wagering"):
    return {"casino_name": "Hollywoodbets", "bonus_terms": "b", "wagering_terms": wager,
            "minimum_deposit_terms": "R50", "source_url": URL}


def llm(**over):
    d = {"casino_name": "Hollywoodbets", "welcome_bonus": "b", "wagering_requirement": 5,
         "minimum_deposit": "R50", "source_url": "https://evil.test"}
    d.update(over)
    return d


def test_source_url_is_not_trusted_from_llm():
    assert scraper.normalize_with_llm(row(), fake_client(llm()))["source_url"] == URL


def test_hallucinated_wagering_is_nulled():
    out = scraper.normalize_with_llm(row(), fake_client(llm(wagering_requirement=35)))
    assert out["wagering_requirement"] is None


def test_non_numeric_and_bool_wagering_is_nulled():
    for bad in ("5x", True):
        assert scraper.normalize_with_llm(row(), fake_client(llm(wagering_requirement=bad)))["wagering_requirement"] is None


def test_missing_fields_raise():
    bad = llm()
    del bad["welcome_bonus"]
    with pytest.raises(ValueError):
        scraper.normalize_with_llm(row(), fake_client(bad))


def test_extra_keys_are_dropped():
    assert set(scraper.normalize_with_llm(row(), fake_client(llm(extra="x")))) == scraper.REQUIRED_KEYS


def test_main_offline_end_to_end(tmp_path, monkeypatch):
    html = tmp_path / "page.html"
    html.write_text(FIXTURE, encoding="utf-8")
    out = tmp_path / "out.json"
    monkeypatch.setattr(scraper, "load_dotenv", lambda *a, **k: None)
    assert scraper.main(["--html-file", str(html), "--no-llm", "--output", str(out)]) == 0
    data = json.loads(out.read_text())
    assert data["count"] == 3 and len(data["casinos"]) == 3 and data["scraped_at"]


def test_main_refuses_to_write_when_rows_missing(tmp_path, monkeypatch):
    html = tmp_path / "page.html"
    html.write_text("<p>nothing</p>", encoding="utf-8")
    out = tmp_path / "out.json"
    monkeypatch.setattr(scraper, "load_dotenv", lambda *a, **k: None)
    assert scraper.main(["--html-file", str(html), "--no-llm", "--output", str(out)]) == 1
    assert not out.exists()


class Resp:
    def __init__(self, status, text=""):
        self.status_code, self.text = status, text

    def raise_for_status(self):
        if self.status_code >= 400:
            raise scraper.requests.HTTPError(str(self.status_code))


@pytest.mark.parametrize("status,text,expected", [
    (404, "", True),
    (403, "", False),
    (200, "User-agent: *\nAllow: /", True),
    (200, "User-agent: *\nDisallow: /", False),
])
def test_robots(monkeypatch, status, text, expected):
    monkeypatch.setattr(scraper, "fetch", lambda *a, **k: Resp(status, text))
    assert scraper.allowed_by_robots(URL) is expected
