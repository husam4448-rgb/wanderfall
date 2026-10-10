# Wanderfall
> **Project-wide chat-first AI engineering standard:** [docs/AI_ENGINEERING_CHAT_FIRST_PROTOCOL.md](docs/AI_ENGINEERING_CHAT_FIRST_PROTOCOL.md). For new development sessions, read this before implementing changes. User-facing workflow requires only ChatGPT chat on Android; GitHub Actions may run tests and builds as infrastructure. The current production queue lives on the active development branch: `docs/PRODUCTION_TASK_QUEUE.json`. No separate AI agent, PC, Work mode or Cloud Browser required.


Phase 16 Android build candidate source checkpoint.

## Step 2 source bundle

The exact game/source package is stored as Base64 text chunks under `source_parts/`. No GitHub Actions workflow has been added yet; CI is intentionally reserved for the next step.

Reconstruct the source archive on Linux/GitHub Actions:

```bash
cat source_parts/part_*.b64 | base64 -d > Wanderfall_Phase16_Game_Source.tar.xz
echo "ae4eff17e5f281f5867ac2d82207fcf96e6c8b649432acd48816aebab76fa308  Wanderfall_Phase16_Game_Source.tar.xz" | sha256sum -c -
tar -xJf Wanderfall_Phase16_Game_Source.tar.xz
```

Expected reconstructed archive SHA-256:

`ae4eff17e5f281f5867ac2d82207fcf96e6c8b649432acd48816aebab76fa308`

See `source_parts/SOURCE_BUNDLE_INFO.txt` for part sizes, per-part SHA-256 hashes, order, and included source paths.
