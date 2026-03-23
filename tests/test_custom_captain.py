"""Tests for the custom captain builder — the 9th character option."""

from portlight.engine.custom_captain import (
    CustomCaptainSpec,
    MAX_POINTS_PER_CATEGORY,
    TOTAL_SKILL_POINTS,
    build_custom_template,
    validate_spec,
)
from portlight.engine.captain_identity import CaptainType


class TestValidation:
    """Spec validation catches errors before building."""

    def test_valid_spec_passes(self):
        spec = CustomCaptainSpec(
            home_port_id="porto_novo", home_region="Mediterranean",
            trade_points=3, sailing_points=3, shadow_points=2, reputation_points=2,
        )
        errors = validate_spec(spec)
        assert errors == []

    def test_wrong_total_points(self):
        spec = CustomCaptainSpec(
            home_port_id="porto_novo", home_region="Mediterranean",
            trade_points=5, sailing_points=5, shadow_points=5, reputation_points=5,
        )
        errors = validate_spec(spec)
        assert any("exactly" in e.lower() or "allocated" in e.lower() for e in errors)

    def test_negative_points(self):
        spec = CustomCaptainSpec(
            home_port_id="porto_novo", home_region="Mediterranean",
            trade_points=-1, sailing_points=5, shadow_points=3, reputation_points=3,
        )
        errors = validate_spec(spec)
        assert any("negative" in e.lower() for e in errors)

    def test_exceeds_max_per_category(self):
        spec = CustomCaptainSpec(
            home_port_id="porto_novo", home_region="Mediterranean",
            trade_points=8, sailing_points=1, shadow_points=1, reputation_points=0,
        )
        errors = validate_spec(spec)
        assert any("exceed" in e.lower() for e in errors)

    def test_invalid_port(self):
        spec = CustomCaptainSpec(
            home_port_id="atlantis", home_region="Mediterranean",
            trade_points=3, sailing_points=3, shadow_points=2, reputation_points=2,
        )
        errors = validate_spec(spec)
        assert any("unknown home port" in e.lower() for e in errors)

    def test_port_region_mismatch(self):
        spec = CustomCaptainSpec(
            home_port_id="porto_novo", home_region="East Indies",
            trade_points=3, sailing_points=3, shadow_points=2, reputation_points=2,
        )
        errors = validate_spec(spec)
        assert any("not" in e.lower() for e in errors)

    def test_invalid_region(self):
        spec = CustomCaptainSpec(
            home_port_id="porto_novo", home_region="Narnia",
            trade_points=3, sailing_points=3, shadow_points=2, reputation_points=2,
        )
        errors = validate_spec(spec)
        assert any("unknown region" in e.lower() for e in errors)

    def test_invalid_bloc(self):
        spec = CustomCaptainSpec(
            home_port_id="porto_novo", home_region="Mediterranean",
            trade_points=3, sailing_points=3, shadow_points=2, reputation_points=2,
            bloc_alignment="fake_bloc",
        )
        errors = validate_spec(spec)
        assert any("unknown trade bloc" in e.lower() for e in errors)

    def test_invalid_faction(self):
        spec = CustomCaptainSpec(
            home_port_id="porto_novo", home_region="Mediterranean",
            trade_points=3, sailing_points=3, shadow_points=2, reputation_points=2,
            faction_alignment="fake_faction",
        )
        errors = validate_spec(spec)
        assert any("unknown pirate faction" in e.lower() for e in errors)

    def test_valid_bloc(self):
        spec = CustomCaptainSpec(
            home_port_id="porto_novo", home_region="Mediterranean",
            trade_points=3, sailing_points=3, shadow_points=2, reputation_points=2,
            bloc_alignment="exchange_alliance",
        )
        errors = validate_spec(spec)
        assert errors == []

    def test_valid_faction(self):
        spec = CustomCaptainSpec(
            home_port_id="corsairs_rest", home_region="Mediterranean",
            trade_points=3, sailing_points=3, shadow_points=2, reputation_points=2,
            faction_alignment="crimson_tide",
        )
        errors = validate_spec(spec)
        assert errors == []

    def test_mentor_wrong_port(self):
        spec = CustomCaptainSpec(
            home_port_id="porto_novo", home_region="Mediterranean",
            trade_points=3, sailing_points=3, shadow_points=2, reputation_points=2,
            mentor_npc_id="am_yasmin",  # Al-Manar NPC, not Porto Novo
        )
        errors = validate_spec(spec)
        assert any("not at your home port" in e.lower() for e in errors)

    def test_valid_mentor(self):
        spec = CustomCaptainSpec(
            home_port_id="porto_novo", home_region="Mediterranean",
            trade_points=3, sailing_points=3, shadow_points=2, reputation_points=2,
            mentor_npc_id="pn_marta",
        )
        errors = validate_spec(spec)
        assert errors == []


class TestBuilding:
    """Build creates valid CaptainTemplates."""

    def test_basic_build(self):
        spec = CustomCaptainSpec(
            home_port_id="porto_novo", home_region="Mediterranean",
            trade_points=3, sailing_points=3, shadow_points=2, reputation_points=2,
        )
        template = build_custom_template(spec)
        assert template.id == CaptainType.CUSTOM
        assert template.home_port_id == "porto_novo"
        assert template.starting_silver == 500  # Mediterranean rate

    def test_trade_focused_build(self):
        spec = CustomCaptainSpec(
            home_port_id="al_manar", home_region="Mediterranean",
            trade_points=7, sailing_points=1, shadow_points=1, reputation_points=1,
        )
        template = build_custom_template(spec)
        assert template.pricing.buy_price_mult < 1.0, "Trade focus should give cheaper buys"
        assert template.pricing.sell_price_mult > 1.0, "Trade focus should give better sells"
        assert template.pricing.luxury_sell_bonus > 0.1, "Trade focus should give luxury bonus"

    def test_sailing_focused_build(self):
        spec = CustomCaptainSpec(
            home_port_id="silva_bay", home_region="Mediterranean",
            trade_points=1, sailing_points=7, shadow_points=1, reputation_points=1,
        )
        template = build_custom_template(spec)
        assert template.voyage.speed_bonus > 1.5, "Sailing focus should give high speed"
        assert template.voyage.provision_burn < 0.8, "Sailing focus should give low provision burn"
        assert template.voyage.storm_resist_bonus > 0.05, "Sailing focus should give storm resist"

    def test_shadow_focused_build(self):
        spec = CustomCaptainSpec(
            home_port_id="corsairs_rest", home_region="Mediterranean",
            trade_points=1, sailing_points=1, shadow_points=7, reputation_points=1,
            faction_alignment="crimson_tide",
        )
        template = build_custom_template(spec)
        assert template.inspection.inspection_chance_mult < 0.7, "Shadow focus should reduce inspections"
        assert "crimson_tide" in template.faction_alignment
        assert template.faction_alignment["crimson_tide"] >= 25, "Shadow focus + faction should give high standing"

    def test_reputation_focused_build(self):
        spec = CustomCaptainSpec(
            home_port_id="jade_port", home_region="East Indies",
            trade_points=1, sailing_points=1, shadow_points=1, reputation_points=7,
        )
        template = build_custom_template(spec)
        assert template.reputation_seed.commercial_trust >= 10, "Reputation focus should give high trust"
        assert template.reputation_seed.east_indies >= 10, "Reputation focus should give regional standing"

    def test_balanced_build(self):
        spec = CustomCaptainSpec(
            home_port_id="crosswind_isle", home_region="East Indies",
            trade_points=2, sailing_points=3, shadow_points=2, reputation_points=3,
        )
        template = build_custom_template(spec)
        # Should have some of everything, nothing extreme
        assert 0.95 <= template.pricing.buy_price_mult <= 1.0
        assert template.voyage.speed_bonus > 0
        assert template.inspection.inspection_chance_mult < 1.0
        assert template.reputation_seed.commercial_trust > 0

    def test_region_affects_silver(self):
        med_spec = CustomCaptainSpec(
            home_port_id="porto_novo", home_region="Mediterranean",
            trade_points=3, sailing_points=3, shadow_points=2, reputation_points=2,
        )
        ss_spec = CustomCaptainSpec(
            home_port_id="coral_throne", home_region="South Seas",
            trade_points=3, sailing_points=3, shadow_points=2, reputation_points=2,
        )
        med = build_custom_template(med_spec)
        ss = build_custom_template(ss_spec)
        assert med.starting_silver > ss.starting_silver, "Mediterranean should give more starting silver"

    def test_backstory_stored(self):
        spec = CustomCaptainSpec(
            home_port_id="porto_novo", home_region="Mediterranean",
            trade_points=3, sailing_points=3, shadow_points=2, reputation_points=2,
            backstory="I was born under a falling star.",
        )
        template = build_custom_template(spec)
        assert "falling star" in template.backstory

    def test_default_backstory(self):
        spec = CustomCaptainSpec(
            home_port_id="porto_novo", home_region="Mediterranean",
            trade_points=3, sailing_points=3, shadow_points=2, reputation_points=2,
        )
        template = build_custom_template(spec)
        assert template.backstory  # should have a default

    def test_strengths_reflect_allocation(self):
        spec = CustomCaptainSpec(
            home_port_id="porto_novo", home_region="Mediterranean",
            trade_points=5, sailing_points=5, shadow_points=0, reputation_points=0,
        )
        template = build_custom_template(spec)
        assert any("trade" in s.lower() for s in template.strengths)
        assert any("sail" in s.lower() for s in template.strengths)
        assert any("underworld" in s.lower() or "shadow" in s.lower() for s in template.weaknesses)

    def test_modifier_ranges_sane(self):
        """No modifier should be extreme regardless of allocation."""
        for trade in range(0, 8):
            remaining = TOTAL_SKILL_POINTS - trade
            for sailing in range(0, min(8, remaining + 1)):
                left = remaining - sailing
                for shadow in range(0, min(8, left + 1)):
                    rep = left - shadow
                    if rep < 0 or rep > MAX_POINTS_PER_CATEGORY:
                        continue
                    spec = CustomCaptainSpec(
                        home_port_id="porto_novo", home_region="Mediterranean",
                        trade_points=trade, sailing_points=sailing,
                        shadow_points=shadow, reputation_points=rep,
                    )
                    t = build_custom_template(spec)
                    # Buy price never below 0.9 or above 1.1
                    assert 0.89 <= t.pricing.buy_price_mult <= 1.1
                    # Provision burn never below 0.5
                    assert t.voyage.provision_burn >= 0.5
                    # Inspection mult never below 0.3
                    assert t.inspection.inspection_chance_mult >= 0.3
                    # Speed never above 2.5
                    assert t.voyage.speed_bonus <= 2.5


class TestCustomGameCreation:
    """Custom captain can create a valid game."""

    def test_custom_creates_game(self):
        from portlight.content.world import new_game
        from portlight.engine.captain_identity import CAPTAIN_TEMPLATES

        spec = CustomCaptainSpec(
            name="Test Captain", title="Custom Trader",
            home_port_id="jade_port", home_region="East Indies",
            trade_points=3, sailing_points=3, shadow_points=2, reputation_points=2,
            bloc_alignment="silk_circle",
            mentor_npc_id="jp_master_chen",
            backstory="Born in the porcelain quarter.",
        )
        template = build_custom_template(spec)

        # Register the custom template temporarily
        CAPTAIN_TEMPLATES[CaptainType.CUSTOM] = template
        try:
            world = new_game(captain_name="Test Captain", captain_type=CaptainType.CUSTOM)
            assert world.captain.captain_type == "custom"
            assert world.voyage.destination_id == "jade_port"
            assert world.captain.silver == 400  # East Indies rate
        finally:
            # Clean up
            del CAPTAIN_TEMPLATES[CaptainType.CUSTOM]
