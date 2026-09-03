# War of the Ring: Mordor's Assault

A single-player, side-scrolling lane battle inspired by the gameplay loop of
*Age of War*. You command **Mordor** against an adaptive **Gondor** AI: recruit
troops, build a formation, earn bounty gold, and destroy the enemy fortress.

This is a high-level MVP built in Python and pygame-ce. Artwork is drawn from
code at runtime; the repository does not contain external art or audio assets.

## Features

- Mordor player versus Gondor AI in a complete win/lose match
- Automatic movement, target acquisition, melee attacks, ranged projectiles,
  formation spacing, deaths, and bounty rewards
- Passive gold income, training queue, costs, and 12-unit population cap
- Three distinct units for each faction
- Automated defensive towers and destructible 1,800-health fortresses
- Gondor AI that responds to pressure and army composition
- Title, battle, help, pause, victory, and defeat screens
- Frame-rate-independent pure-Python simulation with automated tests
- Data-driven unit definitions designed to accommodate future factions

## Requirements and installation

- Python 3.10 or newer
- `pygame-ce` 2.5 or newer

From `C:\Users\khorr\OneDrive\Desktop\VSCODE\Age-of-war-lotr`:

```powershell
python -m pip install -r requirements.txt
python -m lotr_war
```

`pygame-ce` exposes the normal `pygame` import, so no source change is needed.

## Controls

| Input | Action |
|---|---|
| `Enter` or `Space` | Start from the title screen |
| `1` | Train an Orc Warrior |
| `2` | Train an Orc Archer |
| `3` | Train an Uruk-hai |
| Left mouse button | Select a recruitment card |
| `P` or `Esc` | Pause/resume |
| `F1` | Open/close the commander's guide |
| `R` | Restart after victory or defeat |

## Unit roster

### Mordor

| Unit | Cost | Role |
|---|---:|---|
| Orc Warrior | 60 | Cheap, quick frontline infantry |
| Orc Archer | 95 | Fragile ranged support |
| Uruk-hai | 170 | Slow, durable heavy infantry |

### Gondor

| Unit | Cost | Role |
|---|---:|---|
| Gondor Soldier | 65 | Balanced frontline infantry |
| Gondor Archer | 100 | Ranged counter to massed melee troops |
| Tower Guard | 180 | Durable heavy defender |

## Rules

Gold accumulates continuously. Recruiting immediately pays a unit's cost and
adds it to the queue; only the first queued unit trains at a time. Live and
queued troops both count toward the population cap. Units advance and fight
automatically. Killing an enemy awards its bounty. A fortress is attacked when
a unit reaches the far edge of the lane. Reduce Gondor's fortress to zero
health before Gondor destroys the Black Gate.

After three minutes, **siege pressure** activates to prevent an indefinite
midfield stalemate. Each surviving unit occupying enemy territory contributes
gradual damage to that enemy fortress; opposing pressure cancels it. This makes
territorial control decisive while preserving the normal unit and base rules.

## Validation

Run all deterministic unit tests, a complete headless battle, and a rendering
check:

```powershell
python -m unittest discover -s tests -v
python smoke_test.py
python render_check.py
```

The render check uses SDL's dummy video driver and writes ignored screenshots
to `render_output/` for visual inspection.

## Architecture

```text
lotr_war/config.py      Balance constants and unit definitions
lotr_war/models.py      Units, projectiles, armies, and recruitment orders
lotr_war/simulation.py  Economy, queues, movement, combat, towers, victory
lotr_war/ai.py          Gondor composition and recruitment decisions
lotr_war/renderer.py    Procedural pygame artwork and user interface
lotr_war/app.py         Window, events, controls, and screen states
```

The simulation has no pygame dependency, keeping combat testable and allowing
another client to be added later. To introduce another race, define its
`UnitDef` records in `config.py`, add faction presentation data, and supply a
controller (human input or AI) that calls `GameSimulation.recruit`. A broader
faction registry would be the natural next refactor when the third race is
introduced.

## MVP limitations / possible next steps

- Add heroes, abilities, upgrades, and age/technology progression
- Add Rohan, Isengard, Elves, and Dwarves through a faction selection screen
- Add animation and original sound/music
- Add difficulty presets and campaign scenarios
- Add multiple lanes, siege units, and formation commands

This project is a fan-made programming prototype and is not affiliated with or
endorsed by the owners of *The Lord of the Rings* or *Age of War*.