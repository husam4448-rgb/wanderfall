# B2B source-reference archive inventory

Status: **REFERENCE BINARY NOT PRESENT IN REPOSITORY** (2026-10-16).
Prior user upload filename: `B2B Apocalypse_com,dawinstone,b2ba_3,4,1.apks`.

Previously inspected container:
- `base.apk`
- `split_UnityDataAssetPack.apk`
- `split_config.arm64_v8a.apk`

Previously identified Unity asset pack data:
- `datapack.unity3d` (~157.4 MB)
- `resources.resource` (~30.2 MB)
- Spine `character_tex.skel` (reported Spine 4.0.25, 99 bones, 85 slots, 8 IK constraints).

**Evidence status:** The full APKS archive was analyzed in an earlier conversation, but its raw bytes were not uploaded to this GitHub repository and are not available in this conversation's mounted runtime. The verified extracted structural findings are stored separately in `pc49-original-human-rig/REFERENCE_AND_VISUAL_QA.md` and `pc56/b2b_reference_rig_contract.json`.

## Storage rule
Do not commit or publish the unmodified third-party proprietary game APK, asset pack, or extracted textures to a public repository. Retain source binaries only in a private, access-controlled reference location when lawfully permitted. Do not package them into distributable Survival Paradise builds or game resources.

## Recovery
Restore the original user-supplied `.apks` file as a conversation attachment, or provide an accessible private source location, before undertaking pixel-accurate rig/texture comparisons. This inventory **is not a substitute for the source archive**.

## Verified re-upload — 2026-10-16

- Exact attachment: `B2B Apocalypse_com,dawinstone,b2ba_3,4,1.apks`
- Verified SHA-256: `e4cfbe350c0020aa3a97543d90f150c5cdfd61501888b9b52b54c19bfd7a1eb7`
- Archive ZIP validated locally (226 MB apparent size).
- `base.apk`: 23,656,564 bytes, 714 entries.
- `split_UnityDataAssetPack.apk`: 187,671,207 bytes, 9 entries.
- `split_config.arm64_v8a.apk`: 25,535,963 bytes.
- Inside asset-pack split: `assets/bin/Data/datapack.unity3d` (157,403,450 bytes); `assets/bin/Data/resources.resource` (30,245,792 bytes).

**Storage decision:** The user's APKS is available in the current conversation's working sandbox, but is **not uploaded to GitHub**. A public repository must not host the third-party commercial APK or extracted proprietary textures. The checksum and reference manifest are committed; full binary retention requires a verified private access-controlled location with appropriate rights. This manifest deliberately does not claim the raw binary is in GitHub.
