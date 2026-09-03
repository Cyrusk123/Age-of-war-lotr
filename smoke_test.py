"""Drive a complete deterministic match without pygame."""

from __future__ import annotations

from lotr_war.simulation import GameSimulation


def main() -> int:
    game = GameSimulation(seed=17)
    keys = ("orc", "orc_archer", "orc", "uruk")
    next_order = 0.0
    order_index = 0
    dt = 1 / 30
    max_seconds = 360
    for frame in range(max_seconds * 30):
        if game.elapsed >= next_order:
            if game.recruit("mordor", keys[order_index % len(keys)]):
                order_index += 1
            next_order = game.elapsed + 1.25
        game.update(dt)
        if game.state != "playing":
            break
    healthy = (
        game.state in ("victory", "defeat")
        and 0 <= game.mordor.base_health <= 1800
        and 0 <= game.gondor.base_health <= 1800
        and game.elapsed < max_seconds
    )
    print(
        f"SMOKE {'OK' if healthy else 'FAILED'}: {game.state} after {game.elapsed:.1f}s, "
        f"Mordor={game.mordor.base_health:.0f}, Gondor={game.gondor.base_health:.0f}, "
        f"units={len(game.units)}"
    )
    return 0 if healthy else 1


if __name__ == "__main__":
    raise SystemExit(main())