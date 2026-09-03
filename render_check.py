"""Render all important screens without opening a visible window."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

from lotr_war import config as C  # noqa: E402
from lotr_war.renderer import Renderer  # noqa: E402
from lotr_war.simulation import GameSimulation  # noqa: E402


def main() -> int:
    pygame.init()
    screen = pygame.display.set_mode((C.SCREEN_WIDTH, C.SCREEN_HEIGHT))
    renderer = Renderer()
    output = Path(__file__).with_name("render_output")
    output.mkdir(exist_ok=True)

    renderer.draw_title(screen, 1.0)
    pygame.image.save(screen, output / "title.png")

    game = GameSimulation(enable_ai=False)
    for index, kind in enumerate(C.MORDOR_ROSTER):
        game.spawn(kind.key, 230 + index * 70)
    for index, kind in enumerate(C.GONDOR_ROSTER):
        game.spawn(kind.key, 1030 - index * 70)
    renderer.draw_game(screen, game)
    pygame.image.save(screen, output / "battle.png")
    renderer.draw_game(screen, game, paused=True)
    pygame.image.save(screen, output / "pause.png")
    renderer.draw_game(screen, game, show_help=True)
    pygame.image.save(screen, output / "help.png")
    game.state = "victory"
    renderer.draw_game(screen, game)
    pygame.image.save(screen, output / "victory.png")
    game.state = "defeat"
    renderer.draw_game(screen, game)
    pygame.image.save(screen, output / "defeat.png")

    expected = {"title.png", "battle.png", "pause.png", "help.png", "victory.png", "defeat.png"}
    actual = {path.name for path in output.glob("*.png") if path.stat().st_size > 10_000}
    pygame.quit()
    if not expected <= actual:
        print(f"RENDER FAILED: missing or undersized images: {sorted(expected - actual)}")
        return 1
    print(f"RENDER OK: {len(expected)} screens written to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())