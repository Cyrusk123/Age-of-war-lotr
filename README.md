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
- Passive gold income, instant recruitment, costs, and 12-unit population cap
- Five distinct units and an Era 1 hero for each faction
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
| `1`–`5` | Train one of Mordor's regular units |
| `6` | Recruit Lurtz, Mordor's Era 1 hero |
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
| Warg Rider | 145 | Fast shock cavalry |
| Olog-hai | 240 | Mighty siege infantry |
| **Lurtz (Hero, Era 1)** | **380** | **Powerful unique ranged commander** |

### Gondor

| Unit | Cost | Role |
|---|---:|---|
| Gondor Soldier | 65 | Balanced frontline infantry |
| Gondor Archer | 100 | Ranged counter to massed melee troops |
| Tower Guard | 180 | Durable heavy defender |
| Gondor Ranger | 135 | Elite long-range support |
| Knight of Gondor | 225 | Fast, durable cavalry |
| **Boromir (Hero, Era 1)** | **400** | **Powerful unique frontline commander** |

## Rules

Gold accumulates continuously. Recruiting immediately pays a unit's cost and
spawns it at its faction's fortress with no training delay. Live troops count
toward the population cap. Units advance and fight automatically. Killing an
enemy awards its bounty. A fortress is attacked when a unit reaches the far
edge of the lane. Reduce Gondor's fortress to zero health before Gondor
destroys the Black Gate. Heroes also count toward the cap, and only one living
copy of each hero can be deployed at once.

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
lotr_war/models.py      Units, projectiles, armies, and combat events
lotr_war/simulation.py  Economy, recruitment, movement, combat, and victory
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

- Add hero abilities, upgrades, and age/technology progression beyond Era 1
- Add Rohan, Isengard, Elves, and Dwarves through a faction selection screen
- Add animation and original sound/music
- Add difficulty presets and campaign scenarios
- Add multiple lanes, siege units, and formation commands

This project is a fan-made programming prototype and is not affiliated with or
endorsed by the owners of *The Lord of the Rings* or *Age of War*.