"""Crew binding spine tests — Phase 1 thesis proof.

These tests prove that crew is a dependency system, not a bonus system.
One crew state change must produce visible effects in all three layers
without bespoke scripting for each case.

The acceptance bar:
  Phase 1 passes only if one crew state change produces visible effects
  in all three layers (trade/cultural, tactics, narrative).
"""

from portlight.engine.crew import (
    CrewMember,
    CrewRosterState,
    CrewRole,
    CrewStatus,
    Civilization,
    LoyaltyTier,
    # Roster management
    can_recruit,
    recruit,
    dismiss,
    active_crew,
    fit_crew,
    crew_by_role,
    crew_by_civ,
    MAX_CREW,
    # Ship binding
    get_ship_abilities,
    ship_ability_available,
    ship_ability_degraded,
    # Cultural binding
    cultural_knowledge_level,
    cultural_access_check,
    # Combat binding
    get_combat_abilities,
    combat_ability_available,
    # Narrative binding
    get_narrative_hooks,
    # Morale
    apply_morale_change,
    check_departures,
    DEPARTURE_THRESHOLD,
    DEPARTURE_STREAK_DAYS,
    # Injury
    injure,
    recover_day,
    # Loyalty
    add_loyalty_points,
    daily_loyalty_tick,
    LOYALTY_TRUSTED_THRESHOLD,
    LOYALTY_BONDED_THRESHOLD,
    # Pay
    calculate_crew_pay,
    apply_pay_result,
    # Thesis query
    crew_impact_report,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_dax() -> CrewMember:
    """Dax Maren — Keth engineer. The thesis demo crew member.

    - Ship ability: emergency_repair
    - Cultural domain: Keth (grants minimum level 1 knowledge)
    - 3 combat abilities (3rd locked until trusted)
    - Narrative hook: keth_medical_debt
    """
    return CrewMember(
        id="dax_maren",
        name="Dax Maren",
        civilization=Civilization.KETH,
        role=CrewRole.ENGINEER,
        hp=100,
        hp_max=100,
        speed=3,
        abilities=["field_patch", "hull_weld", "keth_stabilize"],
        ship_skill="emergency_repair",
        morale=45,
        loyalty_tier=LoyaltyTier.STRANGER,
        loyalty_points=0,
        pay_rate=60,
        narrative_hooks=["keth_medical_debt"],
        opinions={"violence": -5, "commerce": 3, "keth_customs": 8},
    )


def make_roster_with_dax() -> CrewRosterState:
    roster = CrewRosterState()
    recruit(roster, make_dax())
    return roster


# ---------------------------------------------------------------------------
# 1. Recruitment
# ---------------------------------------------------------------------------

class TestRecruitment:
    def test_recruit_adds_to_roster(self):
        roster = CrewRosterState()
        dax = make_dax()
        recruit(roster, dax)
        assert len(roster.members) == 1
        assert roster.members[0].name == "Dax Maren"

    def test_cannot_recruit_when_full(self):
        roster = CrewRosterState()
        for i in range(MAX_CREW):
            recruit(roster, CrewMember(id=f"crew_{i}", name=f"Crew {i}",
                                       civilization=Civilization.COMPACT,
                                       role=CrewRole.GUNNER))
        err = can_recruit(roster, "new_crew", 1000, 50)
        assert err is not None
        assert "full" in err.lower()

    def test_cannot_recruit_departed(self):
        roster = CrewRosterState()
        roster.departed.append("ghost")
        err = can_recruit(roster, "ghost", 1000, 50)
        assert err is not None
        assert "won't come back" in err.lower()

    def test_cannot_recruit_without_credits(self):
        roster = CrewRosterState()
        err = can_recruit(roster, "new_crew", 10, 50)
        assert err is not None
        assert "₡" in err

    def test_dismiss_marks_departed(self):
        roster = make_roster_with_dax()
        removed = dismiss(roster, "dax_maren")
        assert removed is not None
        assert removed.status == CrewStatus.DEPARTED
        assert "dax_maren" in roster.departed
        assert len(active_crew(roster)) == 0


# ---------------------------------------------------------------------------
# 2. Ship ability binding
# ---------------------------------------------------------------------------

class TestShipBinding:
    def test_active_crew_provides_ship_ability(self):
        roster = make_roster_with_dax()
        assert ship_ability_available(roster, "emergency_repair")

    def test_injured_crew_degrades_ship_ability(self):
        roster = make_roster_with_dax()
        injure(roster.members[0], recovery_days=5)
        assert not ship_ability_available(roster, "emergency_repair")
        assert ship_ability_degraded(roster, "emergency_repair")

    def test_departed_crew_removes_ship_ability(self):
        roster = make_roster_with_dax()
        dismiss(roster, "dax_maren")
        assert not ship_ability_available(roster, "emergency_repair")
        assert not ship_ability_degraded(roster, "emergency_repair")

    def test_get_ship_abilities_lists_all(self):
        roster = make_roster_with_dax()
        abilities = get_ship_abilities(roster)
        assert len(abilities) == 1
        assert abilities[0]["ability"] == "emergency_repair"
        assert abilities[0]["degraded"] is False

    def test_injury_shows_degraded_in_abilities(self):
        roster = make_roster_with_dax()
        injure(roster.members[0], recovery_days=5)
        abilities = get_ship_abilities(roster)
        assert len(abilities) == 1
        assert abilities[0]["degraded"] is True


# ---------------------------------------------------------------------------
# 3. Cultural knowledge binding
# ---------------------------------------------------------------------------

class TestCulturalBinding:
    def test_keth_crew_grants_minimum_level_1(self):
        roster = make_roster_with_dax()
        base = {"compact": 0, "keth": 0, "veshan": 0, "orryn": 0, "reach": 0}
        level = cultural_knowledge_level(roster, Civilization.KETH, base)
        assert level == 1

    def test_no_crew_means_base_knowledge_only(self):
        roster = CrewRosterState()
        base = {"keth": 0}
        level = cultural_knowledge_level(roster, Civilization.KETH, base)
        assert level == 0

    def test_crew_does_not_override_higher_base(self):
        roster = make_roster_with_dax()
        base = {"keth": 2}
        level = cultural_knowledge_level(roster, Civilization.KETH, base)
        assert level == 2

    def test_cultural_access_granted_by_crew(self):
        roster = make_roster_with_dax()
        base = {"keth": 0}
        ok, reason = cultural_access_check(roster, Civilization.KETH, base, required_level=1)
        assert ok
        assert "Dax Maren" in reason

    def test_cultural_access_denied_without_crew(self):
        roster = CrewRosterState()
        base = {"keth": 0}
        ok, reason = cultural_access_check(roster, Civilization.KETH, base, required_level=1)
        assert not ok
        assert "crew member" in reason.lower()

    def test_losing_keth_crew_loses_keth_access(self):
        """THE THESIS TEST: Losing Dax removes Keth cultural access."""
        roster = make_roster_with_dax()
        base = {"keth": 0}

        # Before: has access
        ok_before, _ = cultural_access_check(roster, Civilization.KETH, base, required_level=1)
        assert ok_before

        # Dismiss Dax
        dismiss(roster, "dax_maren")

        # After: no access
        ok_after, _ = cultural_access_check(roster, Civilization.KETH, base, required_level=1)
        assert not ok_after


# ---------------------------------------------------------------------------
# 4. Combat ability binding
# ---------------------------------------------------------------------------

class TestCombatBinding:
    def test_fit_crew_provides_combat_abilities(self):
        roster = make_roster_with_dax()
        abilities = get_combat_abilities(roster)
        assert len(abilities) == 1
        # Stranger tier: only first 2 abilities
        assert len(abilities[0]["abilities"]) == 2
        assert "field_patch" in abilities[0]["abilities"]
        assert "hull_weld" in abilities[0]["abilities"]

    def test_trusted_unlocks_third_ability(self):
        roster = make_roster_with_dax()
        roster.members[0].loyalty_tier = LoyaltyTier.TRUSTED
        abilities = get_combat_abilities(roster)
        assert len(abilities[0]["abilities"]) == 3
        assert "keth_stabilize" in abilities[0]["abilities"]

    def test_injured_crew_excluded_from_combat(self):
        roster = make_roster_with_dax()
        injure(roster.members[0], recovery_days=5)
        abilities = get_combat_abilities(roster)
        assert len(abilities) == 0

    def test_specific_ability_check(self):
        roster = make_roster_with_dax()
        assert combat_ability_available(roster, "field_patch")
        assert not combat_ability_available(roster, "keth_stabilize")  # locked

    def test_injury_removes_combat_ability(self):
        """THE THESIS TEST: Injuring Dax removes combat abilities."""
        roster = make_roster_with_dax()
        assert combat_ability_available(roster, "field_patch")
        injure(roster.members[0], recovery_days=5)
        assert not combat_ability_available(roster, "field_patch")


# ---------------------------------------------------------------------------
# 5. Narrative binding
# ---------------------------------------------------------------------------

class TestNarrativeBinding:
    def test_crew_narrative_hooks_visible(self):
        roster = make_roster_with_dax()
        hooks = get_narrative_hooks(roster)
        assert len(hooks) == 1
        assert "keth_medical_debt" in hooks[0]["hooks"]

    def test_loyalty_unlocks_personal_quest(self):
        roster = make_roster_with_dax()
        dax = roster.members[0]
        result = add_loyalty_points(dax, LOYALTY_TRUSTED_THRESHOLD, "shared danger")
        assert dax.personal_quest_available
        assert "personal_quest" in result["unlocks"]

    def test_departed_crew_loses_narrative(self):
        roster = make_roster_with_dax()
        dismiss(roster, "dax_maren")
        hooks = get_narrative_hooks(roster)
        assert len(hooks) == 0


# ---------------------------------------------------------------------------
# 6. Morale system
# ---------------------------------------------------------------------------

class TestMorale:
    def test_morale_clamped(self):
        dax = make_dax()
        apply_morale_change(dax, 200, "test")
        assert dax.morale == 100
        apply_morale_change(dax, -200, "test")
        assert dax.morale == 0

    def test_low_morale_tracks_streak(self):
        dax = make_dax()
        dax.morale = 20  # below threshold
        result = apply_morale_change(dax, -1, "bad day")
        assert dax.morale_streak >= 1
        assert result["departure_risk"] is False  # not yet 3 days

    def test_departure_after_sustained_low_morale(self):
        roster = make_roster_with_dax()
        dax = roster.members[0]
        dax.morale = 10
        dax.morale_streak = DEPARTURE_STREAK_DAYS  # simulating 3 bad days

        departures = check_departures(roster)
        assert len(departures) == 1
        assert departures[0]["crew_id"] == "dax_maren"
        assert dax.status == CrewStatus.DEPARTED

    def test_high_morale_resets_streak(self):
        dax = make_dax()
        dax.morale = 60
        apply_morale_change(dax, 5, "good day")
        assert dax.morale_streak == 0


# ---------------------------------------------------------------------------
# 7. Injury and recovery
# ---------------------------------------------------------------------------

class TestInjury:
    def test_injury_changes_status(self):
        dax = make_dax()
        result = injure(dax, recovery_days=5)
        assert dax.status == CrewStatus.INJURED
        assert result["effects"]["ground_combat"] == "unavailable"
        assert result["effects"]["ship_ability"] == "degraded"

    def test_recovery_restores_status(self):
        dax = make_dax()
        injure(dax, recovery_days=2)
        # Day 1
        recover_day(dax)
        # Day 2 (should recover)
        event = recover_day(dax)
        assert event is not None
        assert dax.status == CrewStatus.ACTIVE
        assert dax.hp == dax.hp_max

    def test_recovering_transition(self):
        dax = make_dax()
        injure(dax, recovery_days=5)
        # Advance to within 3 days of recovery
        for _ in range(2):
            recover_day(dax)
        event = recover_day(dax)  # Should hit recovering transition
        assert dax.status == CrewStatus.RECOVERING


# ---------------------------------------------------------------------------
# 8. Loyalty progression
# ---------------------------------------------------------------------------

class TestLoyalty:
    def test_loyalty_starts_at_stranger(self):
        dax = make_dax()
        assert dax.loyalty_tier == LoyaltyTier.STRANGER

    def test_trusted_threshold(self):
        dax = make_dax()
        add_loyalty_points(dax, LOYALTY_TRUSTED_THRESHOLD, "test")
        assert dax.loyalty_tier == LoyaltyTier.TRUSTED

    def test_bonded_threshold(self):
        dax = make_dax()
        add_loyalty_points(dax, LOYALTY_BONDED_THRESHOLD, "test")
        assert dax.loyalty_tier == LoyaltyTier.BONDED

    def test_loyalty_is_one_way(self):
        """Loyalty tiers cannot decrease — even if points hypothetically could."""
        dax = make_dax()
        add_loyalty_points(dax, LOYALTY_TRUSTED_THRESHOLD, "trust earned")
        assert dax.loyalty_tier == LoyaltyTier.TRUSTED
        # Loyalty points don't decrease in the current system,
        # but even if they did, tier wouldn't revert
        dax.loyalty_points = 0
        # Tier stays
        assert dax.loyalty_tier == LoyaltyTier.TRUSTED

    def test_daily_tick_builds_loyalty(self):
        dax = make_dax()
        dax.morale = 60  # above 50
        result = daily_loyalty_tick(dax)
        assert result is not None
        assert dax.loyalty_points == 1

    def test_daily_tick_no_progress_low_morale(self):
        dax = make_dax()
        dax.morale = 30  # below 50
        result = daily_loyalty_tick(dax)
        assert result is None


# ---------------------------------------------------------------------------
# 9. Pay system
# ---------------------------------------------------------------------------

class TestPay:
    def test_monthly_pay_calculation(self):
        roster = make_roster_with_dax()
        assert calculate_crew_pay(roster) == 60  # Dax's pay rate

    def test_paid_improves_morale(self):
        roster = make_roster_with_dax()
        old_morale = roster.members[0].morale
        results = apply_pay_result(roster, paid=True)
        assert roster.members[0].morale == old_morale + 2

    def test_missed_pay_tanks_morale(self):
        roster = make_roster_with_dax()
        old_morale = roster.members[0].morale
        results = apply_pay_result(roster, paid=False)
        assert roster.members[0].morale == old_morale - 8


# ---------------------------------------------------------------------------
# 10. THE THESIS TEST — Cross-system impact
# ---------------------------------------------------------------------------

class TestThesisBinding:
    """The acceptance bar: one crew state change produces visible effects
    in all three layers without bespoke scripting."""

    def test_injury_ripples_across_all_layers(self):
        """Injuring Dax simultaneously:
        - Removes combat abilities (tactics layer)
        - Degrades ship ability (tactics layer)
        - Does NOT remove cultural access (she's still present)
        - Keeps narrative hooks (she's still present)

        This tests that injury is a systemic state change, not per-system logic.
        """
        roster = make_roster_with_dax()
        base_knowledge = {"keth": 0}
        dax = roster.members[0]

        # Before injury: full capability
        report_before = crew_impact_report(roster, base_knowledge)
        assert report_before["combat_abilities_available"] == 2
        assert len(report_before["ship_abilities_active"]) == 1
        assert report_before["cultural_access"]["keth"]["level"] == 1

        # Injure Dax
        injure(dax, recovery_days=5)

        # After injury: combat gone, ship degraded, culture preserved
        report_after = crew_impact_report(roster, base_knowledge)
        assert report_after["combat_abilities_available"] == 0  # tactics: gone
        assert len(report_after["ship_abilities_active"]) == 0  # tactics: degraded
        assert len(report_after["ship_abilities_degraded"]) == 1  # still exists but weak
        assert report_after["cultural_access"]["keth"]["level"] == 1  # trade: preserved
        assert len(report_after["narrative_hooks"]) == 1  # plot: preserved

    def test_departure_ripples_across_all_layers(self):
        """Losing Dax simultaneously:
        - Removes ALL combat abilities (tactics)
        - Removes ship ability entirely (tactics)
        - Removes Keth cultural access (trade)
        - Removes narrative hooks (plot)

        One state change. Three layers affected. No scripting per system.
        """
        roster = make_roster_with_dax()
        base_knowledge = {"keth": 0}

        # Before: full
        report_before = crew_impact_report(roster, base_knowledge)
        assert report_before["crew_count"] == 1
        assert report_before["combat_abilities_available"] == 2
        assert len(report_before["ship_abilities_active"]) == 1
        assert report_before["cultural_access"]["keth"]["level"] == 1
        assert len(report_before["narrative_hooks"]) == 1

        # Dismiss Dax
        dismiss(roster, "dax_maren")

        # After: everything gone
        report_after = crew_impact_report(roster, base_knowledge)
        assert report_after["crew_count"] == 0
        assert report_after["combat_abilities_available"] == 0  # tactics: gone
        assert len(report_after["ship_abilities_active"]) == 0  # tactics: gone
        assert len(report_after["ship_abilities_degraded"]) == 0  # not even degraded
        assert report_after["cultural_access"]["keth"]["level"] == 0  # trade: gone
        assert len(report_after["narrative_hooks"]) == 0  # plot: gone

    def test_morale_neglect_leads_to_departure_leads_to_loss(self):
        """The full neglect chain:
        1. Miss pay → morale drops
        2. Sustained low morale → departure
        3. Departure → all three layers lose capability

        This is the 'feel the missing slot' test.
        """
        roster = make_roster_with_dax()
        base_knowledge = {"keth": 0}
        dax = roster.members[0]

        # Start: Dax is here, everything works
        assert ship_ability_available(roster, "emergency_repair")
        assert cultural_knowledge_level(roster, Civilization.KETH, base_knowledge) == 1
        assert combat_ability_available(roster, "field_patch")

        # Miss pay repeatedly
        for _ in range(4):
            apply_pay_result(roster, paid=False)

        # Morale should be tanked
        assert dax.morale < DEPARTURE_THRESHOLD

        # Force departure streak
        dax.morale_streak = DEPARTURE_STREAK_DAYS

        # Check departures
        departures = check_departures(roster)
        assert len(departures) == 1

        # Now everything is gone
        assert not ship_ability_available(roster, "emergency_repair")
        assert cultural_knowledge_level(roster, Civilization.KETH, base_knowledge) == 0
        assert not combat_ability_available(roster, "field_patch")

    def test_impact_report_shows_gaps(self):
        """The impact report shows what you're missing."""
        roster = CrewRosterState()
        base_knowledge = {}
        report = crew_impact_report(roster, base_knowledge)

        # All roles missing
        assert len(report["missing_roles"]) == len(CrewRole)
        # All cultural access missing
        assert len(report["missing_cultural_access"]) == len(Civilization)
        # No combat, no ship, no narrative
        assert report["combat_abilities_available"] == 0
        assert len(report["ship_abilities_active"]) == 0
        assert len(report["narrative_hooks"]) == 0

    def test_recovery_restores_combat_but_not_immediately(self):
        """Recovery is gradual — injured crew don't snap back."""
        roster = make_roster_with_dax()
        dax = roster.members[0]

        injure(dax, recovery_days=5)
        assert not combat_ability_available(roster, "field_patch")

        # Partial recovery
        for _ in range(3):
            recover_day(dax)
        # Still recovering, not fully fit
        assert dax.status in (CrewStatus.INJURED, CrewStatus.RECOVERING)
        assert not combat_ability_available(roster, "field_patch")

        # Full recovery
        for _ in range(3):
            recover_day(dax)
        assert dax.status == CrewStatus.ACTIVE
        assert combat_ability_available(roster, "field_patch")
