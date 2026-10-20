# Survival Paradise — World Asset Production Index

**Source of truth for asset planning and status in future ChatGPT sessions.**

## Production rules
- One environmental asset per separate, centered transparent PNG; no contact sheets as final deliverables.
- Shared gritty handcrafted 2D, oblique/top-down art style; consistent lighting, silhouette, scale and alpha edges.
- Each biome has its **own nature library** alongside its structures/props; do not reuse forest vegetation as a substitute for other biome nature.
- Naming: `SP_[Biome]_[Category]_[Subtype]_[Variant].png`.
- Keep prototype visual review separate from validated in-engine scaling and production release.
- Preserve approved art. Do not replace or count rejected renders.

## Current state — 2026-10-20

| Biome | Nature assets | Structures/props | Notes |
| --- | --- | --- | --- |
| Forest | 84 accepted; **39 PNGs uploaded, 45 pending** | Not catalogued here | Wood 12/12, Rocks 17/17, Trees 10/20; remaining trees, bushes, ground clutter still awaiting binary upload |
| Desert | 26 prototype PNGs; **2 PNGs uploaded, 24 pending** | 0 | Two tree PNGs uploaded; 10 tree and 14 shrub PNGs still to upload. Other 92 planned desert assets not yet generated |
| Grassland | Not started | Not started | Needs distinct biome-specific vegetation |
| Swamp / wetland | Not started | Not started | Needs distinct biome-specific vegetation |
| Rocky highland | Not started | Not started | Needs distinct biome-specific vegetation |
| Coastal | Not started | Not started | Needs distinct biome-specific vegetation |
| Arid scrubland | Not started | Not started | Needs distinct biome-specific vegetation |
| City / small urban | Not started | Not started | Needs both urban nature (courtyard trees, weeds, vines) **and** houses, markets, roads, utilities, etc. |

## Verified GitHub binary asset checkpoint
- Original PNGs byte-for-byte verified against the source ZIPs: **41 / 110 uploaded** (Forest 39/84; Desert 2/26). 69 remain.
- [Per-file upload state / SHA-256 source ledger](ASSET_UPLOAD_STATUS.json), [full binary transfer plan](ASSET_BINARY_TRANSFER_PLAN.json).
- **Upload sequence before new asset generation:** finish Forest Trees, Bushes and GroundClutter; finish Desert Tree and Shrub; re-verify Git tree. Update this index after each completed batch.
- All other biomes require **their own** Nature assets and Structures/Props, including City / small urban vegetation, homes, markets and utilities.

## Desert — authoritative inventory
- [118-asset production checklist](desert/SP_Desert_Biome_Production_Checklist.md)
- [118-row asset manifest and QA status](desert/SP_Desert_Biome_Asset_Manifest.csv)
- 68 nature and 50 structures planned; 26 are provisional/prototype approved; 92 remain.
- **Next unchecked category:** `Desert/Nature/Grass/` (10 different sprites), then Rock (12), Ground (12), Wood (8), followed by Structures.
- Only treat PNGs as available if their actual files were uploaded and verified. A checklist entry is not a binary asset.

## Future sessions
1. Read this index and the linked checklist/CSV from GitHub.
2. Produce one asset per transparent image, visually QA the output, and keep filename and category accurate.
3. Commit actual image PNGs and update the per-file upload status/checklists after each verified batch; store both Nature and Structures/Props for each biome.
4. Do not mark an asset integrated, production ready, or in GitHub unless independently verified.
