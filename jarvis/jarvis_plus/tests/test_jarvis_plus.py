from datetime import datetime

import pytest

from jarvis_plus import customers, garmin, phone, profile, stress, whoop
from jarvis_plus.watcher import in_quiet_hours

WHOOP_RECOVERY = {
    "created_at": "2026-11-09T06:00:00.000Z",
    "score": {
        "recovery_score": 28,
        "resting_heart_rate": 62,
        "hrv_rmssd_milli": 41.3,
        "spo2_percentage": 96.5,
        "skin_temp_celsius": 33.4,
    },
}
WHOOP_SLEEP = {
    "end": "2026-11-09T06:30:00.000Z",
    "nap": False,
    "score": {
        "stage_summary": {
            "total_in_bed_time_milli": 6 * 3_600_000,
            "total_awake_time_milli": 900_000,
            "total_slow_wave_sleep_time_milli": 3_600_000,
            "total_rem_sleep_time_milli": 5_400_000,
        },
        "sleep_performance_percentage": 70,
    },
}


def test_whoop_summaries():
    rec = whoop.summarize_recovery(WHOOP_RECOVERY)
    assert rec["recovery_prozent"] == 28
    assert rec["hrv_ms"] == 41.3
    sleep = whoop.summarize_sleep(WHOOP_SLEEP)
    assert sleep["schlaf_stunden"] == 5.75
    assert sleep["tiefschlaf_stunden"] == 1.0
    cycle = whoop.summarize_cycle({"score": {"strain": 14.23, "kilojoule": 10460}})
    assert cycle == {
        "start": "",
        "strain": 14.2,
        "kcal": 2500,
        "durchschnittspuls": None,
        "maxpuls": None,
    }


def test_whoop_baseline_ignores_missing():
    base = whoop.baseline([{"hrv_ms": 60, "ruhepuls": 55}, {"hrv_ms": None, "ruhepuls": 57}])
    assert base == {"hrv_ms": 60.0, "ruhepuls": 56.0}


def test_stress_high():
    w = {
        "heute": {
            "recovery": whoop.summarize_recovery(WHOOP_RECOVERY),
            "schlaf": whoop.summarize_sleep(WHOOP_SLEEP),
        },
        "baseline": {"hrv_ms": 62.0, "ruhepuls": 55.0},
    }
    g = {"tag": garmin.summarize_stats({"averageStressLevel": 55, "bodyBatteryMostRecentValue": 18})}
    result = stress.assess(w, g)
    assert result.level == "hoch"
    assert any("HRV" in r for r in result.gruende)
    assert result.tipps


def test_stress_low_and_unknown():
    w = {
        "heute": {"recovery": {"recovery_prozent": 85, "hrv_ms": 70, "ruhepuls": 52}},
        "baseline": {"hrv_ms": 65, "ruhepuls": 53},
    }
    assert stress.assess(w, None).level == "niedrig"
    assert stress.assess(None, None).level == "unbekannt"


def test_garmin_negative_stress_ignored():
    # Garmin meldet -1/-2 wenn keine Messung vorliegt
    g = {"tag": {"stress_durchschnitt": -1}}
    assert stress.assess(None, g).level == "unbekannt"


def test_twiml_escapes_text():
    xml = phone.build_twiml("Termin <heute> & morgen", "Polly.Daniel-Neural", "de-DE")
    assert "&lt;heute&gt; &amp; morgen" in xml
    assert xml.startswith("<Response><Say")


def test_customers_roundtrip(tmp_path):
    db = tmp_path / "k.db"
    customers.save("Max Muster", kontakt="max@x.de", db_path=db)
    customers.save("max muster", status="angebot", faellig_am="2026-11-01", db_path=db)
    customers.add_note("Max Muster", "Will Angebot für 3 Monate", db_path=db)
    info = customers.get("Max Muster", db_path=db)
    assert info["kontakt"] == "max@x.de"
    assert info["status"] == "angebot"
    assert info["notizen"][0]["text"] == "Will Angebot für 3 Monate"
    assert [c["name"] for c in customers.due("2026-11-09", db_path=db)] == ["Max Muster"]
    with pytest.raises(ValueError):
        customers.save("X", status="quatsch", db_path=db)
    with pytest.raises(ValueError):
        customers.save("X", faellig_am="morgen", db_path=db)


def test_profile_append(tmp_path):
    path = tmp_path / "ueber-mich.md"
    path.write_text("# Über mich\n\n## Ziele\n- Fit werden\n\n## Business\n- Agentur\n")
    profile.append("Ziele", "75 kg bis Juni", path=path)
    profile.append("Musik", "Hört gern Rap", path=path)
    text = path.read_text()
    ziele = text.split("## Ziele")[1].split("## Business")[0]
    assert "75 kg bis Juni" in ziele
    assert "## Musik" in text


def test_quiet_hours():
    assert in_quiet_hours(datetime(2026, 1, 1, 23), 22, 7)
    assert in_quiet_hours(datetime(2026, 1, 1, 3), 22, 7)
    assert not in_quiet_hours(datetime(2026, 1, 1, 12), 22, 7)


# ---------------------------------------------------------------- neue Bausteine
import json as _json

from jarvis_plus import activity, autostart, connectors, websites
from jarvis_plus.hud_server import choose_model, trim_history
from jarvis_plus.settings import Settings


def test_model_routing_cheap_by_default():
    s = Settings({})
    assert choose_model("Wie war mein Schlaf?", s)[0] == "claude-haiku-5-5"
    assert choose_model("Bau mir eine Landingpage für einen Maler", s)[0] == "claude-sonnet-5-5"
    assert choose_model("Schreib eine Offerte für Kunde X", s)[0] == "claude-sonnet-5-5"
    model, text = choose_model("/smart Erklär mir Zinseszins", s)
    assert model == "claude-sonnet-5-5" and text == "Erklär mir Zinseszins"
    assert choose_model("/schnell Website-Idee?", s)[0] == "claude-haiku-5-5"
    custom = Settings({"JARVIS_MODEL_FAST": "fast-x"})
    assert choose_model("hallo", custom)[0] == "fast-x"


def test_trim_history_limits_tokens():
    hist = [{"role": "user", "content": "x" * 9000}] + [
        {"role": "assistant" if i % 2 else "user", "content": str(i)} for i in range(30)
    ] + [{"role": "system", "content": "ignorieren"}]
    out = trim_history(hist, keep=10)
    assert len(out) == 9  # system-Nachricht fliegt raus
    assert all(m["role"] in ("user", "assistant") for m in out)
    assert len(trim_history([{"role": "user", "content": "y" * 9000}])[0]["content"]) == 4000


def test_websites_save_and_safety(tmp_path):
    import os

    os.environ["JARVIS_SITES_DIR"] = str(tmp_path)
    try:
        res = websites.save("Müller Malerei!", {"index.html": "<h1>Hi</h1>", "css/a.css": "h1{}"})
        assert res["name"] == "mueller-malerei"
        assert (tmp_path / "mueller-malerei" / "css" / "a.css").exists()
        assert websites.list_sites()[0]["vorschau"] == "/sites/mueller-malerei/"
        with pytest.raises(ValueError):
            websites.save("x", {"index.html": "a", "../../evil.txt": "b"})
        with pytest.raises(ValueError):
            websites.save("x", {"style.css": "a"})
    finally:
        del os.environ["JARVIS_SITES_DIR"]


def test_activity_log_roundtrip(tmp_path):
    import jarvis_plus.activity as act

    orig = act.log_file
    act.log_file = lambda: tmp_path / "a.jsonl"
    try:
        act.log("tool", "whoop_daten", status="start")
        events, off = act.read_from(0)
        assert [e["title"] for e in events] == ["whoop_daten"]
        act.log("tool", "whoop_daten", status="ok", dauer=0.4)
        new, off2 = act.read_from(off)
        assert len(new) == 1 and new[0]["status"] == "ok" and off2 > off
        assert len(act.recent(10)) == 2
    finally:
        act.log_file = orig


def test_connectors_keep_existing_entries(tmp_path):
    orig = connectors.servers_file
    connectors.servers_file = lambda: tmp_path / "mcp-servers.json"
    try:
        (tmp_path / "mcp-servers.json").write_text(_json.dumps([{"name": "eigener", "url": "http://x"}]))
        connectors.add("higgsfield", Settings({}))
        connectors.add("21st", Settings({"TWENTYFIRST_API_KEY": "k123"}))
        data = _json.loads((tmp_path / "mcp-servers.json").read_text())
        names = [d["name"] for d in data]
        assert names == ["eigener", "higgsfield", "21st"]
        assert "https://mcp.higgsfield.ai/mcp" in data[1]["args"]
        assert "x-api-key:k123" in data[2]["args"]
        with pytest.raises(RuntimeError):
            connectors.add("21st", Settings({}))  # Key fehlt → klare Meldung
        connectors.remove("higgsfield")
        assert [c["name"] for c in connectors.listing() if c["aktiv"]] == ["21st"]
    finally:
        connectors.servers_file = orig


def test_autostart_files():
    plist = autostart.launchd_plist("jarvis-hud", ["/u/bin/jarvis-plus", "hud"], Path("/tmp/logs"))
    assert "<string>/u/bin/jarvis-plus</string>" in plist and "<key>KeepAlive</key><true/>" in plist
    unit = autostart.systemd_unit("jarvis-watch", ["/u/bin/jarvis-plus", "watch"])
    assert "ExecStart=/u/bin/jarvis-plus watch" in unit and "Restart=always" in unit
    assert "After=openjarvis.service" in unit
    cmd = autostart.windows_command([r"C:\Users\b\.local\bin\jarvis.exe", "serve"])
    assert "-WindowStyle Hidden" in cmd and r"'C:\Users\b\.local\bin\jarvis.exe' serve" in cmd


from pathlib import Path  # noqa: E402
