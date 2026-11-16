from __future__ import annotations


def f2(x) -> str:
    return f"{x:.2f}"


def km2(x) -> str:
    return f"{x:,.0f}".replace("-", "−")


def signed(x) -> str:
    return f"{x:+.2f}".replace("-", "−")


def line1(res: dict) -> str:
    v = res["claim2"]["vegetation"]
    lo, hi = v["ci95"]
    if v["passes"]:
        return (f"On low ground under trees, NISAR flagged {km2(v['excess_km2'])} km² (95% interval {km2(lo)} to "
                f"{km2(hi)} km²) more flooding than in the 12 days before, where Sentinel-1 saw dry land "
                f"(evidence, not verified).")
    return (f"On low ground under trees where Sentinel-1 saw dry land, NISAR's flooded-vegetation flags changed by "
            f"{km2(v['excess_km2'])} km² against the 12 days before (95% interval {km2(lo)} to {km2(hi)} km²), "
            f"which is not clear evidence of hidden water.")


def line2(res: dict) -> str:
    """Page line 2 (change-log row 9 wording), then the paired difference against the margin."""
    c = res["claim1"]
    lo, hi = c["ci95"]
    verdict = "within" if c["noninferior"] else "below"
    margin = signed(c["margin"])
    return (f"{claim1_short(res)} The difference, NISAR minus Sentinel-1, is {signed(c['diff'])} "
            f"(95% interval {signed(lo)} to {signed(hi)}), {verdict} our non-inferiority margin of {margin}.")


def claim1_short(res: dict) -> str:
    c = res["claim1"]
    n, s = c["nisar_twosided"]["f1"], c["s1_twosided"]["f1"]
    if c["noninferior"]:
        return f"On open water it keeps up with Sentinel-1 (F1 {f2(n)} vs {f2(s)}). Checked against optical satellites."
    return f"On open water: F1 {f2(n)} for NISAR and {f2(s)} for Sentinel-1, checked against optical satellites."


def line1a(res: dict) -> str:
    a = res["claim1a"]
    lo, hi = a["nisar_twosided"]["ci95"]
    dlo, dhi = a["ci95"]
    verdict = ("a small but consistent gain from adding HV" if a["passes"]
               else "so adding HV did not clearly help")
    return (f"NISAR alone, checked against the 29 Sep optical map in the western frame: F1 {f2(a['nisar_twosided']['f1'])} "
            f"(95% interval {f2(lo)} to {f2(hi)}); against HH alone the difference is {a['diff']:+.3f} "
            f"(95% interval {dlo:+.3f} to {dhi:+.3f}), {verdict}.").replace("+-", "-")


def caption_claim1(res: dict) -> str:
    """Video caption 5. Team decision of 15 Nov (logged after results): when Sentinel-1 is better on open
    water with an interval wholly below zero, say so plainly with the same numbers."""
    c = res["claim1"]
    n, s = c["nisar_twosided"]["f1"], c["s1_twosided"]["f1"]
    if not c["noninferior"] and c["ci95"][1] < 0:
        return f"Checked against optical satellites: on open water, Sentinel-1 did better (F1 {f2(s)} vs {f2(n)})."
    return claim1_short(res)


def captions(res: dict) -> list[tuple[float, float, str]]:
    """The overview's storyboard, numbers from results.json."""
    v = res["claim2"]["vegetation"]
    if v["passes"]:
        c3 = f"NISAR's L-band SAR (synthetic aperture radar) sees through: evidence of {km2(v['excess_km2'])} km² of flooding Sentinel-1 called dry."
    else:
        c3 = "NISAR's L-band SAR (synthetic aperture radar) sees more under trees, but here the signal is not clear."
    return [
        (0.0, 5.0, "Every monsoon the Gandak dances across Bihar. In 2026 it broke its record."),
        (5.0, 11.0, "The world's flood maps use C-band radar. Under trees, it largely misses the water."),
        (11.0, 19.0, c3),
        (19.0, 25.0, "Tap any field and hear its radar change as the water arrives."),
        (25.0, 30.0, caption_claim1(res)),
    ]
