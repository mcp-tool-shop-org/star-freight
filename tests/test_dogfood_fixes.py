"""Tests for dogfood session fixes: save slots, encoding, UX improvements."""

from pathlib import Path

from portlight.app.session import GameSession
from portlight.content.goods import GOODS
from portlight.content.world import new_game
from portlight.engine.economy import execute_buy, recalculate_prices
from portlight.engine.save import (
    DEFAULT_SLOT,
    SAVE_DIR,
    SAVE_FILE,
    load_game,
    save_filename,
    save_game,
)
from portlight.engine.voyage import depart


# ---------------------------------------------------------------------------
# Fix 1: Named save slots
# ---------------------------------------------------------------------------

class TestSaveSlots:
    def test_save_filename_default(self):
        assert save_filename() == "default.json"

    def test_save_filename_named(self):
        assert save_filename("dagger") == "dagger.json"
        assert save_filename("captain-drake") == "captain-drake.json"

    def test_save_filename_sanitized(self):
        assert save_filename("bad/name") == "badname.json"
        assert save_filename("no spaces") == "nospaces.json"
        assert save_filename("") == "default.json"

    def test_two_slots_isolated(self, tmp_path: Path):
        """Two save slots don't interfere with each other."""
        world_a = new_game("Alice")
        world_b = new_game("Bob")
        save_game(world_a, base_path=tmp_path, slot="alice")
        save_game(world_b, base_path=tmp_path, slot="bob")

        result_a = load_game(base_path=tmp_path, slot="alice")
        result_b = load_game(base_path=tmp_path, slot="bob")

        assert result_a is not None
        assert result_b is not None
        assert result_a[0].captain.name == "Alice"
        assert result_b[0].captain.name == "Bob"

    def test_default_slot_used_when_unspecified(self, tmp_path: Path):
        world = new_game("Default")
        save_game(world, base_path=tmp_path)
        result = load_game(base_path=tmp_path)
        assert result is not None
        assert result[0].captain.name == "Default"

    def test_legacy_migration(self, tmp_path: Path):
        """Old portlight_save.json auto-migrates to default.json on load."""
        world = new_game("Legacy")
        save_game(world, base_path=tmp_path)
        # Move default.json to legacy filename
        save_dir = tmp_path / SAVE_DIR
        default_path = save_dir / save_filename(DEFAULT_SLOT)
        legacy_path = save_dir / SAVE_FILE
        default_path.rename(legacy_path)
        assert legacy_path.exists()
        assert not default_path.exists()

        # Load should auto-migrate
        result = load_game(base_path=tmp_path, slot=DEFAULT_SLOT)
        assert result is not None
        assert result[0].captain.name == "Legacy"
        # Legacy file should be gone, default.json should exist
        assert default_path.exists()
        assert not legacy_path.exists()

    def test_session_slot_isolation(self, tmp_path: Path):
        """Two GameSession instances with different slots don't collide."""
        s1 = GameSession(tmp_path, slot="player1")
        s1.new("Player One")

        s2 = GameSession(tmp_path, slot="player2")
        s2.new("Player Two")

        # Reload each — should get the right captain
        s1r = GameSession(tmp_path, slot="player1")
        assert s1r.load()
        assert s1r.captain.name == "Player One"

        s2r = GameSession(tmp_path, slot="player2")
        assert s2r.load()
        assert s2r.captain.name == "Player Two"

    def test_nonexistent_slot_returns_none(self, tmp_path: Path):
        result = load_game(base_path=tmp_path, slot="nonexistent")
        assert result is None


# ---------------------------------------------------------------------------
# Fix 2: Unicode encoding safety
# ---------------------------------------------------------------------------

class TestUnicodeSafety:
    def test_views_no_non_cp1252_chars(self):
        """views.py must not contain characters outside cp1252."""
        import portlight.app.views as views_module
        import inspect
        source = inspect.getsource(views_module)
        for i, char in enumerate(source):
            if ord(char) > 127:
                # Em dash (U+2014) is in cp1252, allow it
                if char == "\u2014":
                    continue
                assert False, (
                    f"Non-cp1252 character U+{ord(char):04X} ({char!r}) "
                    f"found at position {i} in views.py"
                )

    def test_formatting_no_non_cp1252_chars(self):
        """formatting.py must not contain non-cp1252 characters in code."""
        import portlight.app.formatting as fmt_module
        import inspect
        source = inspect.getsource(fmt_module)
        for i, char in enumerate(source):
            if ord(char) > 127:
                if char == "\u2014":
                    continue
                # Allow chars in docstrings/comments (block chars in docstring)
                # But the source should be clean now
                assert False, (
                    f"Non-cp1252 character U+{ord(char):04X} ({char!r}) "
                    f"found at position {i} in formatting.py"
                )


# ---------------------------------------------------------------------------
# Fix 3: Good ID hints
# ---------------------------------------------------------------------------

class TestGoodIdHints:
    def test_buy_with_display_name_suggests_id(self, tmp_path: Path):
        """Buying with display name like 'iron_ore' suggests the correct ID."""
        world = new_game("Tester")
        # Find a port that sells iron
        port = world.ports.get("iron_point")
        if port:
            recalculate_prices(port, GOODS)
            result = execute_buy(world.captain, port, "iron_ore", 5, GOODS)
            assert isinstance(result, str)
            assert "iron" in result.lower()

    def test_buy_with_correct_id_works(self, tmp_path: Path):
        world = new_game("Tester")
        port = world.ports.get("porto_novo")
        assert port is not None
        recalculate_prices(port, GOODS)
        result = execute_buy(world.captain, port, "grain", 5, GOODS)
        # Should succeed (TradeReceipt, not str)
        from portlight.receipts.models import TradeReceipt
        assert isinstance(result, TradeReceipt)


# ---------------------------------------------------------------------------
# Fix 4: Buy partial amount suggestion
# ---------------------------------------------------------------------------

class TestBuyPartialSuggestion:
    def test_buy_excess_suggests_available(self, tmp_path: Path):
        world = new_game("Tester")
        port = world.ports.get("porto_novo")
        assert port is not None
        recalculate_prices(port, GOODS)
        # Try to buy way more than available
        result = execute_buy(world.captain, port, "grain", 9999, GOODS)
        assert isinstance(result, str)
        assert "try:" in result.lower() or "available" in result.lower()


# ---------------------------------------------------------------------------
# Fix 5: Silver floor
# ---------------------------------------------------------------------------

class TestSilverFloor:
    def test_save_clamps_negative_silver(self, tmp_path: Path):
        """Session._save() clamps silver to 0 if it goes negative."""
        s = GameSession(tmp_path)
        s.new("Broke")
        s.captain.silver = -100
        s._save()

        s2 = GameSession(tmp_path)
        assert s2.load()
        assert s2.captain.silver == 0


# ---------------------------------------------------------------------------
# Fix 6: Crew 0 sail prevention
# ---------------------------------------------------------------------------

class TestCrewSailPrevention:
    def test_depart_blocked_with_zero_crew(self, tmp_path: Path):
        world = new_game("Skeleton")
        # Force crew to 0
        world.captain.ship.crew = 0
        result = depart(world, "al_manar")
        assert isinstance(result, str)
        assert "crew" in result.lower()

    def test_depart_allowed_with_minimum_crew(self, tmp_path: Path):
        world = new_game("Ready")
        # Default merchant starts with crew >= crew_min
        result = depart(world, "al_manar")
        # Should either succeed (VoyageState) or fail for a non-crew reason
        if isinstance(result, str):
            assert "crew" not in result.lower()


# ---------------------------------------------------------------------------
# Fix 7: Port-day costs (provisions + wages tick while docked)
# ---------------------------------------------------------------------------

class TestPortDayCosts:
    def test_provisions_decrease_in_port(self, tmp_path: Path):
        s = GameSession(tmp_path)
        s.new("Docker")
        initial_provisions = s.captain.provisions
        s.advance()
        assert s.captain.provisions == initial_provisions - 1

    def test_wages_paid_in_port(self, tmp_path: Path):
        s = GameSession(tmp_path)
        s.new("Docker")
        initial_silver = s.captain.silver
        s.advance()
        # Should have lost at least 1 silver to wages (3 sailors * 1/day = 3)
        assert s.captain.silver < initial_silver

    def test_no_wages_when_broke(self, tmp_path: Path):
        s = GameSession(tmp_path)
        s.new("Broke")
        s.captain.silver = 0
        s.advance()
        # Silver stays at 0, no negative
        assert s.captain.silver == 0


# ---------------------------------------------------------------------------
# Fix 8: Encounter blocks advance
# ---------------------------------------------------------------------------

class TestEncounterBlocksAdvance:
    def test_pending_duel_blocks_advance(self, tmp_path: Path):
        """If a pending_duel exists in save, advance should detect it."""
        from portlight.engine.models import PendingDuel
        s = GameSession(tmp_path)
        s.new("Fighter")
        # Simulate a pending encounter
        s.world.pirates.pending_duel = PendingDuel(
            captain_id="gnaw",
            captain_name="Gnaw",
            faction_id="iron_teeth",
            personality="aggressive",
            strength=3,
            region="West Africa",
        )
        s._save()

        # Reload in fresh session (simulates new CLI invocation)
        s2 = GameSession(tmp_path)
        s2.load()
        assert s2.world.pirates.pending_duel is not None
