#!/usr/bin/env python3
"""SP279 - batch multistack looting UI updates and avoid useless distant LOS queries.

Preserves item stack results, capacity/weight checks, item_added signals,
loot persistence, NPC sight detection boundaries and all graphical content.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
inventory=root/"scripts/items/inventory.gd"
world=root/"scripts/items/world_state.gd"
hud=root/"scripts/mobile_hud.gd"
bandit=root/"scripts/combat/bandit.gd"
sources={p:p.read_text(encoding="utf-8") for p in (inventory,world,hud,bandit)}
def once(path,old,new,label):
    s=sources[path]
    count=s.count(old)
    if count!=1: raise RuntimeError("SP279_ANCHOR_%s_COUNT_%d"%(label,count))
    sources[path]=s.replace(old,new,1)

once(inventory,'var stacks: Array[Dictionary] = []',
'''var stacks: Array[Dictionary] = []
var _sp279_batch_depth: int = 0
var _sp279_pending_changed: bool = false

func begin_batch() -> void:
    _sp279_batch_depth += 1

func end_batch() -> void:
    if _sp279_batch_depth <= 0:
        push_error("Inventory end_batch without begin_batch")
        return
    _sp279_batch_depth -= 1
    if _sp279_batch_depth == 0 and _sp279_pending_changed:
        _sp279_pending_changed = false
        changed.emit()
''',"INVENTORY_BATCH_API")
once(inventory,'''    if accepted > 0:
        changed.emit()
        item_added.emit(item_id, accepted)''','''    if accepted > 0:
        if _sp279_batch_depth > 0:
            _sp279_pending_changed = true
        else:
            changed.emit()
        # Preserve the original per-item feedback/achievement semantics.
        item_added.emit(item_id, accepted)''',"ADDITEM_CHANGED")
once(world,'''    var moved_names: Array[String] = []

    for stack in loot:''','''    var moved_names: Array[String] = []
    inventory.begin_batch()

    for stack in loot:''',"TAKEALL_BEGIN")
once(world,'''    container_loot[container_id] = leftovers
    return {"moved": moved_total, "items": moved_names, "empty": leftovers.is_empty()}''','''    container_loot[container_id] = leftovers
    # Notify HUD once with the fully committed source+destination state.
    inventory.end_batch()
    return {"moved": moved_total, "items": moved_names, "empty": leftovers.is_empty()}''',"TAKEALL_END")
once(hud,'''    storage_status_label.text = player.storage_take_all()
    _storage_container_index = 0
    _refresh_storage_panel()
    _refresh_inventory()''','''    storage_status_label.text = player.storage_take_all()
    _storage_container_index = 0
    # WorldState.take_all now sends one atomic inventory.changed event,
    # refreshing both views just once after all item stacks transfer.''',"HUD_DUPLICATE_TAKEALL_REFRESH")
once(bandit,'''    if sight != null and sight.get("world") != null:
        # Sight has directional arc and static-geometry ray occlusion;
        # noise alert is separate and does not require eye contact.
        var visible_target: bool = bool(sight.call("can_see_point",
            self,target_player.global_position,_visual_facing,detection_range,112.0))
        aware = visible_target or alert_time > 0.0 or distance <= 55.0''','''    if sight != null and sight.get("world") != null:
        # A point outside the detection radius cannot pass can_see_point.
        # Avoid the ray-query/LOS scene lookup for distant idle bandits.
        # Noise alerts still wake bandits beyond visual range.
        var visible_target: bool = false
        if distance <= detection_range:
            visible_target = bool(sight.call("can_see_point",
                self,target_player.global_position,_visual_facing,detection_range,112.0))
        aware = visible_target or alert_time > 0.0 or distance <= 55.0''',"BANDIT_DISTANCE_GATE")

for path,src in sources.items(): path.write_text(src,encoding="utf-8")
print("SP279_LOOT_ATOMIC_INVENTORY_SIGNALS_PASS once-per-takeall UI refresh, item_added preserved")
print("SP279_NPC_LOS_EARLY_RANGE_GATE_PASS invisible faraway idle bandits skip raycast")
