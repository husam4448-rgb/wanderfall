extends SceneTree
## SP279 native inventory + loot transaction regression.
func _initialize() -> void:
    call_deferred("_run")
func _fail(msg: String) -> void:
    push_error("SP279_NATIVE_LOOT_FAIL " + msg)
    quit(89)
func _run() -> void:
    var manager: Node = root.get_node_or_null("WorldState")
    if manager == null:
        _fail("WorldState singleton missing")
        return
    var inv_script: GDScript = load("res://scripts/items/inventory.gd")
    var inv: Node = inv_script.new()
    root.add_child(inv)
    inv.set("slot_capacity", 60)
    var signal_counts: Dictionary = {"changed":0, "added":0}
    inv.changed.connect(func(): signal_counts["changed"] += 1)
    inv.item_added.connect(func(_id: String, _qty: int): signal_counts["added"] += 1)
    var container_id: String = "sp279_native_bandit_bag"
    var initial: Array = manager.call("get_container_loot", container_id, 98716, "bandit")
    if initial.size() < 2:
        _fail("Bandit source should have multiple item stacks")
        return
    var expected: int = 0
    for stack in initial:
        expected += int(stack.get("quantity", 0))
    var result: Dictionary = manager.call("take_all", container_id, inv)
    if int(result.get("moved", -1)) != expected:
        _fail("quantity changed by batching")
        return
    if int(signal_counts["changed"]) != 1:
        _fail("take all produced "+str(signal_counts["changed"])+" changed signals, expected exactly one")
        return
    if int(signal_counts["added"]) != initial.size():
        _fail("per-stack item_added signals not preserved")
        return
    var after: Array = manager.call("get_container_loot", container_id, 98716, "bandit")
    if not after.is_empty():
        _fail("Loot source not emptied after all items transferred")
        return
    var total: int = 0
    for stack in inv.get("stacks"):
        total += int(stack.get("quantity", 0))
    if total != expected:
        _fail("destination inventory quantity mismatch")
        return
    var second: Dictionary = manager.call("take_all", container_id, inv)
    if int(second.get("moved", -1)) != 0 or int(signal_counts["changed"]) != 1:
        _fail("looting empty bag re-emits changed signal")
        return
    inv.call("add_item", "water_bottle", 1)
    if int(signal_counts["changed"]) != 2:
        _fail("ordinary item gain must still signal immediately")
        return
    inv.call("begin_batch")
    inv.call("begin_batch")
    inv.call("add_item", "bandage", 1)
    inv.call("add_item", "canned_beans", 1)
    if int(signal_counts["changed"]) != 2:
        _fail("inventory emitted UI refresh from inside nested batch")
        return
    inv.call("end_batch")
    if int(signal_counts["changed"]) != 2:
        _fail("nested batch flushed before outer end")
        return
    inv.call("end_batch")
    if int(signal_counts["changed"]) != 3:
        _fail("nested batch did not flush once")
        return
    print("SP279_NATIVE_LOOT_PASS bandit loot count="+str(expected)+" stack_count="+str(initial.size())+" exactly one HUD change event; normal + nested batch signals intact; empty bag idempotent")
    quit(0)
