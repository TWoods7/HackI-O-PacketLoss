"""Data pipeline (owner: TA). Run from repo root after scripts/get_data.sh:

    .venv/bin/python -m pipeline.build

Writes data/processed/ (gitignored). Starter loaders are done; TODO(TA) marks the feature work.
"""
from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
EXTRACTED = ROOT / "data" / "extracted"
PROCESSED = ROOT / "data" / "processed"
H3_RES = 8
UNREPAIRED_PLACEHOLDER = pd.Timestamp("2025-10-24")

LAYERS = {
    "customers": "Data1/Customer_Clip.shp",
    "damage": "Data1/arcos_prod_damage_09_28_Clip.shp",
    "poles": "Data1/Pole_Clip.shp",
    "primary": "Data1/Primary_ExportFeatures.shp",
    "fuses": "Data1/Fuse_Bank_Clip.shp",
    "hospitals": "Data1/Hospitals_Medic_Pairwis_Clip.shp",
    "fire": "Data1/Fire_Stations_E_Pairwis_Clip.shp",
    "ambulance": "Data1/Ambulance_Servi_Pairwis_Clip.shp",
    "secondary": "Data2/Secondary_ExportFeatures.shp",
    "transformers": "Data2/Transformer_Clip.shp",
    "switches": "Data2/Switch_Clip.shp",
    "reclosers": "Data2/Recloser_Bank_Clip.shp",
}


def load(name: str) -> gpd.GeoDataFrame:
    return gpd.read_file(EXTRACTED / LAYERS[name], engine="pyogrio")


def circuit_map() -> dict[str, str]:
    """Customer-style circuit_id ('0000060') -> damage-style alias ('CIR60')."""
    pairs = pd.concat(
        [load(n)[["circuit_id", "aep_circui"]] for n in ("fuses", "switches", "reclosers", "transformers")]
    ).dropna().drop_duplicates()
    return dict(zip(pairs["circuit_id"], pairs["aep_circui"]))


def parse_upstream() -> pd.DataFrame:
    """matched_upstream.txt -> one row per (premise, hop), hop 0 = transformer, last = circuit breaker."""
    rows = []
    with open(EXTRACTED / "matched_upstream" / "matched_upstream.txt") as f:
        for line in f:
            premise, *hops = line.rstrip("\n").split("\t")
            for i, hop in enumerate(hops):
                table, obj_id, kind, location = (hop.split("*") + ["", "", "", ""])[:4]
                rows.append((premise, i, table, obj_id, kind, location))
    return pd.DataFrame(rows, columns=["premise_nu", "hop", "table", "object_id", "device_kind", "location_n"])


def damage_events(damage: gpd.GeoDataFrame, gap_days: int = 2) -> gpd.GeoDataFrame:
    """Cluster report dates into storm events and compute repair duration in days."""
    d = damage.copy()
    d["report"] = pd.to_datetime(d["Report_Tim"])
    d["repaired"] = pd.to_datetime(d["Repaired_D"])
    d.loc[(d["Repaired"] == "No") | (d["repaired"] == UNREPAIRED_PLACEHOLDER), "repaired"] = pd.NaT
    d["duration_days"] = (d["repaired"] - d["report"]).dt.days
    days = d["report"].drop_duplicates().sort_values()
    event_of = (days.diff().dt.days.fillna(gap_days + 1) > gap_days).cumsum()
    d["event"] = d["report"].map(dict(zip(days, "E" + event_of.astype(str))))
    return d


def main():
    PROCESSED.mkdir(parents=True, exist_ok=True)
    cmap = circuit_map()
    print(f"circuit map: {len(cmap)} circuits")

    up = parse_upstream()
    up.to_parquet(PROCESSED / "upstream.parquet")
    print(f"upstream: {up['premise_nu'].nunique()} premises, {len(up)} hops")

    dmg = damage_events(load("damage"))
    dmg.drop(columns="geometry").to_parquet(PROCESSED / "damage_events.parquet")
    print(dmg.groupby("event")["report"].agg(["min", "max", "count"]).sort_values("count", ascending=False).head(8))

    # TODO(TA): per-H3 features (premises, % overhead, pole age, OH primary length, upstream depth,
    #           damage per event) -> data/processed/hex_features.parquet
    # TODO(TA): anonymized premise map (premise_nu -> P-ID, h3) using backend.privacy.anon_premise


if __name__ == "__main__":
    main()
