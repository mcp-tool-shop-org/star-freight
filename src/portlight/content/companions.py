"""Companion catalog — recruitable first mates and officers.

Each companion has a role that provides specific bonuses, a morale
that reacts to player decisions, and a personality that shapes their
dialogue and departure triggers.

Roles (maritime-specific):
  marine      — combat bonus, duel interception, boarding power
  navigator   — speed bonus at sea, danger reduction, route knowledge
  surgeon     — injury healing at sea, crew health, medicine efficiency
  smuggler    — contraband handling, underworld connections, inspection evasion
  quartermaster — trade bonuses, cargo efficiency, silver management

Max 2 companions at a time. Quality over quantity.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CompanionRole:
    """Static role definition with mechanical bonuses."""
    id: str
    name: str
    description: str
    # Passive bonuses (always active while companion is in party)
    combat_damage_bonus: int = 0
    combat_interception_chance: float = 0.0  # chance to take a hit for player
    speed_bonus: float = 0.0
    danger_reduction: float = 0.0
    heal_rate_bonus: float = 0.0             # injury healing multiplier at sea
    inspection_evasion: float = 0.0          # reduce inspection chance
    trade_bonus: float = 0.0                 # sell price improvement


ROLES: dict[str, CompanionRole] = {r.id: r for r in [
    CompanionRole(
        id="marine",
        name="Marine",
        description="A trained fighter who stands at your side in combat.",
        combat_damage_bonus=1,
        combat_interception_chance=0.25,
    ),
    CompanionRole(
        id="navigator",
        name="Navigator",
        description="Reads the stars and currents. Gets you there faster and safer.",
        speed_bonus=0.5,
        danger_reduction=0.03,
    ),
    CompanionRole(
        id="surgeon",
        name="Surgeon",
        description="Keeps crew alive and your wounds clean.",
        heal_rate_bonus=1.0,  # doubles injury healing at sea
    ),
    CompanionRole(
        id="smuggler",
        name="Smuggler",
        description="Knows every hidden compartment and customs loophole.",
        inspection_evasion=0.30,
    ),
    CompanionRole(
        id="quartermaster",
        name="Quartermaster",
        description="Manages cargo, negotiates prices, and counts every coin.",
        trade_bonus=0.05,  # 5% better sell prices
    ),
]}


@dataclass(frozen=True)
class CompanionDef:
    """A recruitable NPC companion."""
    id: str
    name: str
    role_id: str
    home_port_id: str
    region: str
    description: str
    personality: str              # lawful, pragmatic, reckless, gentle
    hire_cost: int
    required_standing: int        # regional standing to recruit
    greeting: str                 # what they say when you meet them
    hire_dialog: str              # what they say when recruited
    loyalty_line: str             # high morale
    warning_line: str             # low morale
    departure_line: str           # when they leave


# ---------------------------------------------------------------------------
# Companion catalog — 10 companions (2 per role)
# ---------------------------------------------------------------------------

COMPANIONS: dict[str, CompanionDef] = {c.id: c for c in [
    # === MARINES ===
    CompanionDef(
        id="iron_marta",
        name="Iron Marta",
        role_id="marine",
        home_port_id="ironhaven",
        region="North Atlantic",
        description="A former garrison soldier who deserted for the sea. Fights like she has nothing to lose.",
        personality="reckless",
        hire_cost=80,
        required_standing=5,
        greeting="A woman in a soldier's coat sits alone at the bar, sharpening a boarding axe.",
        hire_dialog="\"I've been looking for a captain worth fighting for. Pay's secondary. Show me you're not a coward.\"",
        loyalty_line="\"Best decision I ever made, signing on with you.\"",
        warning_line="\"Captain... I'm starting to wonder if this ship is heading anywhere worth going.\"",
        departure_line="\"I didn't leave the garrison to follow another fool. I'm done.\"",
    ),
    CompanionDef(
        id="red_tomas",
        name="Red Tomas",
        role_id="marine",
        home_port_id="corsairs_rest",
        region="Mediterranean",
        description="A pirate-turned-bodyguard with a face full of scars and a code of honor.",
        personality="pragmatic",
        hire_cost=60,
        required_standing=0,
        greeting="A scarred man watches you from the corner. His hand never leaves the cutlass at his belt.",
        hire_dialog="\"I protect. You pay. Simple arrangement. Betray me and you'll wish the pirates found you first.\"",
        loyalty_line="\"You're straight with me, Captain. That's rare on these waters.\"",
        warning_line="\"This isn't what I signed up for. We need to talk.\"",
        departure_line="\"The deal's off. Don't look for me.\"",
    ),

    # === NAVIGATORS ===
    CompanionDef(
        id="star_lila",
        name="Star Lila",
        role_id="navigator",
        home_port_id="crosswind_isle",
        region="East Indies",
        description="A Javanese navigator who reads the stars like others read books. She's never been lost.",
        personality="gentle",
        hire_cost=100,
        required_standing=10,
        greeting="A young woman sits on the dock, sketching star charts on palm bark with quiet concentration.",
        hire_dialog="\"The stars brought me here. Perhaps they brought you too. I'll navigate — you decide where.\"",
        loyalty_line="\"The stars say we're on the right path. I believe them.\"",
        warning_line="\"The currents are wrong, Captain. Not the sea — this ship's course.\"",
        departure_line="\"The stars say it's time to part. I wish you fair winds.\"",
    ),
    CompanionDef(
        id="old_henry",
        name="Old Henry",
        role_id="navigator",
        home_port_id="thornport",
        region="North Atlantic",
        description="Fifty years at sea. He's sailed every route twice and remembers every reef.",
        personality="pragmatic",
        hire_cost=70,
        required_standing=5,
        greeting="An old man mends nets by the harbor, humming a tune you don't recognize. His eyes are sharp.",
        hire_dialog="\"I'm too old to captain my own ship, but I'm not too old to keep yours off the rocks. Deal?\"",
        loyalty_line="\"Reminds me of the old days. Good captain, good ship, good sea.\"",
        warning_line="\"I've seen captains make these mistakes before. It doesn't end well.\"",
        departure_line="\"I'm retiring. For real this time. Good luck, Captain.\"",
    ),

    # === SURGEONS ===
    CompanionDef(
        id="dr_amara",
        name="Dr. Amara",
        role_id="surgeon",
        home_port_id="sun_harbor",
        region="West Africa",
        description="A healer trained in both Western and African medicine. She's saved more lives than most doctors dream of.",
        personality="gentle",
        hire_cost=120,
        required_standing=10,
        greeting="A woman in a clean apron tends to a sailor's wound at the dockside clinic. Efficient, gentle hands.",
        hire_dialog="\"I go where people need healing. Your crew looks like they could use it. I have conditions — no unnecessary cruelty.\"",
        loyalty_line="\"Your crew trusts you. That's the best medicine there is.\"",
        warning_line="\"I became a healer to save lives, Captain. Not to watch them wasted.\"",
        departure_line="\"I cannot stay on a ship that causes more harm than it heals. Goodbye, Captain.\"",
    ),
    CompanionDef(
        id="patches",
        name="Patches",
        role_id="surgeon",
        home_port_id="typhoon_anchorage",
        region="South Seas",
        description="A ship's surgeon who earned his nickname from the number of wounds he's stitched. Drinks too much, but his hands are steady.",
        personality="reckless",
        hire_cost=50,
        required_standing=0,
        greeting="A man with rum-stained fingers and a surgeon's kit sits at the bar. He's stitching his own thumb.",
        hire_dialog="\"I can keep your crew alive. Mostly. I charge cheap because I drink the medicine budget. Fair warning.\"",
        loyalty_line="\"Best gig I've had in years. The rum's flowing and nobody's dying.\"",
        warning_line="\"I'm a doctor, not a miracle worker. This ship needs better luck — or a better captain.\"",
        departure_line="\"I'm finding a quieter ship. One where I can drink in peace.\"",
    ),

    # === SMUGGLERS ===
    CompanionDef(
        id="shadow_kai",
        name="Shadow Kai",
        role_id="smuggler",
        home_port_id="spice_narrows",
        region="East Indies",
        description="Nobody knows his real name. He makes contraband disappear and reappear wherever it needs to be.",
        personality="pragmatic",
        hire_cost=90,
        required_standing=5,
        greeting="A man you didn't notice before is suddenly standing beside you. \"Looking for someone discreet?\"",
        hire_dialog="\"I have skills. You have cargo holds. Let's make each other rich. Just don't ask where things go.\"",
        loyalty_line="\"Good captain. Doesn't ask stupid questions. My kind of arrangement.\"",
        warning_line="\"You're drawing too much heat. That's bad for business — and for my neck.\"",
        departure_line="\"The arrangement is over. You'll never see me again. That's the point.\"",
    ),
    CompanionDef(
        id="rosa_the_fence",
        name="Rosa the Fence",
        role_id="smuggler",
        home_port_id="corsairs_rest",
        region="Mediterranean",
        description="A woman who knows the price of everything and the customs schedule of every port.",
        personality="pragmatic",
        hire_cost=70,
        required_standing=0,
        greeting="A woman with too many rings counts coins at a corner table. She's been watching you since you walked in.",
        hire_dialog="\"Every captain needs someone who knows where the inspectors aren't. That's me. Fifty-fifty on the extras.\"",
        loyalty_line="\"We're making good silver together. Long may it last.\"",
        warning_line="\"The margins are getting thin and the heat's getting thick. Watch yourself.\"",
        departure_line="\"Bad for business, Captain. I'm moving on before your luck runs out on both of us.\"",
    ),

    # === QUARTERMASTERS ===
    CompanionDef(
        id="coin_mariam",
        name="Coin Mariam",
        role_id="quartermaster",
        home_port_id="al_manar",
        region="Mediterranean",
        description="A merchant's daughter who can appraise cargo by smell and negotiate prices in seven languages.",
        personality="lawful",
        hire_cost=100,
        required_standing=10,
        greeting="A well-dressed woman inspects cargo manifests at the harbormaster's office. She spots errors in seconds.",
        hire_dialog="\"Your books are a mess. Your cargo holds are inefficient. Your pricing is amateur. Hire me and I'll fix all three.\"",
        loyalty_line="\"The ledgers are clean, the holds are full, and the silver is flowing. My kind of ship.\"",
        warning_line="\"The numbers don't lie, Captain. We're heading for a loss if you keep this up.\"",
        departure_line="\"I don't serve captains who ignore the ledger. Find another quartermaster.\"",
    ),
    CompanionDef(
        id="dockhand_pete",
        name="Dockhand Pete",
        role_id="quartermaster",
        home_port_id="palm_cove",
        region="West Africa",
        description="Knows every dock, every scale, and every harbormaster's weakness on the West African coast.",
        personality="reckless",
        hire_cost=40,
        required_standing=0,
        greeting="A wiry man balances on a cargo crate, juggling oranges. He catches all three without looking.",
        hire_dialog="\"I know cargo. I know ports. I know who's cheating on the scales. Hire me and you'll never overpay for grain again.\"",
        loyalty_line="\"Good ship, good captain, good cargo. Life's good!\"",
        warning_line="\"Captain, I'm starting to feel like ballast. Use me or lose me.\"",
        departure_line="\"I need a ship that's actually going somewhere. No hard feelings.\"",
    ),
]}


# ---------------------------------------------------------------------------
# Morale reaction table
# ---------------------------------------------------------------------------

# trigger -> {role_id: morale_delta}
MORALE_REACTIONS: dict[str, dict[str, int]] = {
    "combat_won":       {"marine": 5, "navigator": 1, "surgeon": -1, "smuggler": 0, "quartermaster": 0},
    "combat_lost":      {"marine": -3, "navigator": -2, "surgeon": -2, "smuggler": -1, "quartermaster": -2},
    "crew_killed":      {"marine": -2, "navigator": -1, "surgeon": -5, "smuggler": 0, "quartermaster": -1},
    "profitable_trade": {"marine": 0, "navigator": 0, "surgeon": 0, "smuggler": 2, "quartermaster": 5},
    "losing_trade":     {"marine": 0, "navigator": 0, "surgeon": 0, "smuggler": -1, "quartermaster": -3},
    "contraband_trade": {"marine": -2, "navigator": -1, "surgeon": -3, "smuggler": 5, "quartermaster": -1},
    "spared_enemy":     {"marine": 2, "navigator": 1, "surgeon": 5, "smuggler": 0, "quartermaster": 0},
    "took_all":         {"marine": 1, "navigator": -1, "surgeon": -3, "smuggler": 3, "quartermaster": 2},
    "fled_combat":      {"marine": -5, "navigator": 2, "surgeon": 2, "smuggler": 1, "quartermaster": 0},
    "injury_sustained": {"marine": -1, "navigator": -2, "surgeon": -1, "smuggler": -2, "quartermaster": -2},
    "long_voyage":      {"marine": -1, "navigator": 2, "surgeon": -1, "smuggler": -1, "quartermaster": -1},
    "port_arrival":     {"marine": 1, "navigator": 1, "surgeon": 1, "smuggler": 1, "quartermaster": 2},
    "nemesis_defeated": {"marine": 8, "navigator": 3, "surgeon": 2, "smuggler": 3, "quartermaster": 3},
}


# Personality modifiers: personality -> global morale modifier
PERSONALITY_MODIFIERS: dict[str, dict[str, int]] = {
    "lawful":    {"contraband_trade": -3, "spared_enemy": 2, "took_all": -2},
    "pragmatic": {},  # no extra modifiers — baseline
    "reckless":  {"combat_won": 2, "fled_combat": -3, "long_voyage": -2},
    "gentle":    {"crew_killed": -3, "spared_enemy": 3, "took_all": -3, "combat_won": -1},
}


def get_companions_at_port(port_id: str) -> list[CompanionDef]:
    """Get companions available for recruitment at a port."""
    return [c for c in COMPANIONS.values() if c.home_port_id == port_id]
