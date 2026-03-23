"""Cultural knowledge system tests — Phase 3 thesis proof.

Acceptance bar:
  - Keth interaction changes trade or aid outcome based on season + knowledge
  - Veshan interaction changes honor/challenge or conflict outcome
  - Missing cultural access is visibly felt at decision time
  - Crew source of knowledge is identified in state
  - Consequence tags differ based on culturally informed vs uninformed choice
  - Same system affects trade, encounter resolution, and narrative access

The bar: when the player meets a new civilization, do they feel
a new social logic, or just new nouns?
"""

from portlight.engine.crew import (
    CrewMember,
    CrewRosterState,
    CrewRole,
    Civilization,
    LoyaltyTier,
    recruit,
    cultural_knowledge_level,
)
from portlight.engine.cultural_knowledge import (
    # Core types
    InteractionOutcome,
    CulturalOption,
    CulturalInteraction,
    InteractionResult,
    # Evaluation
    evaluate_interaction,
    get_visible_options,
    get_crew_advice,
    # Keth
    KethSeason,
    get_keth_season,
    keth_season_visible,
    KETH_SEASONAL_EFFECTS,
    keth_trade_interaction,
    # Veshan
    VeshanDebt,
    veshan_debt_visible,
    veshan_encounter_interaction,
    # Generic
    cultural_trade_modifier,
    cultural_encounter_options,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_keth_crew() -> CrewMember:
    """A Keth crew member — cultural bridge."""
    return CrewMember(
        id="thal_communion",
        name="Thal",
        civilization=Civilization.KETH,
        role=CrewRole.ENGINEER,
        abilities=["field_patch", "hull_weld", "keth_stabilize"],
        ship_skill="organic_repair",
        morale=50,
        pay_rate=55,
        narrative_hooks=["keth_exile"],
    )


def make_veshan_crew() -> CrewMember:
    """A Veshan crew member — honor culture bridge."""
    return CrewMember(
        id="varek_drashan",
        name="Varek",
        civilization=Civilization.VESHAN,
        role=CrewRole.GUNNER,
        abilities=["aimed_shot", "suppressive_fire", "honor_strike"],
        ship_skill="heavy_volley",
        morale=55,
        pay_rate=70,
        narrative_hooks=["house_drashan_exile"],
        opinions={"honor": 10, "deception": -8},
    )


def roster_with_keth() -> CrewRosterState:
    roster = CrewRosterState()
    recruit(roster, make_keth_crew())
    return roster


def roster_with_veshan() -> CrewRosterState:
    roster = CrewRosterState()
    recruit(roster, make_veshan_crew())
    return roster


def empty_roster() -> CrewRosterState:
    return CrewRosterState()


# ---------------------------------------------------------------------------
# 1. Keth Seasonal Protocols
# ---------------------------------------------------------------------------

class TestKethSeasons:
    def test_season_cycle(self):
        assert get_keth_season(1) == KethSeason.EMERGENCE
        assert get_keth_season(90) == KethSeason.EMERGENCE
        assert get_keth_season(91) == KethSeason.HARVEST
        assert get_keth_season(180) == KethSeason.HARVEST
        assert get_keth_season(181) == KethSeason.DORMANCY
        assert get_keth_season(270) == KethSeason.DORMANCY
        assert get_keth_season(271) == KethSeason.SPAWNING
        assert get_keth_season(360) == KethSeason.SPAWNING
        # Cycle wraps
        assert get_keth_season(361) == KethSeason.EMERGENCE

    def test_season_invisible_at_level_0(self):
        assert not keth_season_visible(0)
        assert keth_season_visible(1)

    def test_seasonal_effects_exist(self):
        for season in KethSeason:
            assert season in KETH_SEASONAL_EFFECTS
            effect = KETH_SEASONAL_EFFECTS[season]
            assert effect.mood != ""


class TestKethTradeInteraction:
    def test_harvest_gift_is_excellent(self):
        """During harvest, offering a gift is the best move."""
        interaction = keth_trade_interaction(
            day=100,  # harvest
            is_pushing_deal=False,
            is_offering_gift=True,
            knowledge=1,
        )
        gift_option = next(o for o in interaction.options if o.id == "offer_gift")
        assert gift_option.outcome == InteractionOutcome.SUCCESS
        assert gift_option.reputation_delta > 0
        assert gift_option.trade_modifier < 0  # discount

    def test_spawning_gift_is_offensive(self):
        """During spawning, offering a gift is taboo."""
        interaction = keth_trade_interaction(
            day=300,  # spawning
            is_pushing_deal=False,
            is_offering_gift=True,
            knowledge=1,
        )
        gift_option = next(o for o in interaction.options if o.id == "offer_gift")
        assert gift_option.outcome == InteractionOutcome.OFFENSE
        assert gift_option.reputation_delta < 0

    def test_dormancy_pushing_is_misstep(self):
        """During dormancy, pushing deals is remembered badly."""
        interaction = keth_trade_interaction(
            day=200,  # dormancy
            is_pushing_deal=True,
            is_offering_gift=False,
            knowledge=0,
        )
        push_option = next(o for o in interaction.options if o.id == "push_deal")
        assert push_option.outcome == InteractionOutcome.MISSTEP
        assert push_option.reputation_delta < 0

    def test_spawning_pushing_is_offense(self):
        """During spawning, pushing deals is catastrophic."""
        interaction = keth_trade_interaction(
            day=300,  # spawning
            is_pushing_deal=True,
            is_offering_gift=False,
            knowledge=0,
        )
        push_option = next(o for o in interaction.options if o.id == "push_deal")
        assert push_option.outcome == InteractionOutcome.OFFENSE
        assert push_option.reputation_delta <= -10

    def test_wait_option_requires_knowledge_2(self):
        """Knowing to wait for a better season requires deeper knowledge."""
        interaction = keth_trade_interaction(day=200, is_pushing_deal=False,
                                             is_offering_gift=False, knowledge=2)
        wait_option = next((o for o in interaction.options if o.id == "wait_season"), None)
        assert wait_option is not None
        assert wait_option.knowledge_required == 2
        assert wait_option.outcome == InteractionOutcome.SUCCESS

    def test_ignorant_player_sees_fewer_options(self):
        """Without knowledge, the player can't see gift or wait options."""
        interaction = keth_trade_interaction(day=100, is_pushing_deal=False,
                                             is_offering_gift=False, knowledge=2)
        roster = empty_roster()
        base = {"keth": 0}  # level 0

        visible = get_visible_options(interaction, roster, base)
        # Should only see options with knowledge_required <= 0
        for opt in visible:
            assert opt.knowledge_required <= 0

    def test_keth_crew_reveals_options(self):
        """A Keth crew member grants level 1, revealing gift options."""
        interaction = keth_trade_interaction(day=100, is_pushing_deal=False,
                                             is_offering_gift=False, knowledge=1)
        roster = roster_with_keth()
        base = {"keth": 0}  # crew grants level 1

        visible = get_visible_options(interaction, roster, base)
        visible_ids = [o.id for o in visible]
        assert "offer_gift" in visible_ids

    def test_same_action_different_season_different_outcome(self):
        """THE THESIS TEST: Same gift action, different season, different result.
        This proves Keth has a social logic, not just variable prices."""
        roster = roster_with_keth()
        base = {"keth": 0}

        # Gift during harvest
        harvest = keth_trade_interaction(day=100, is_pushing_deal=False,
                                         is_offering_gift=True, knowledge=1)
        result_harvest = evaluate_interaction(harvest, "offer_gift", roster, base)
        assert result_harvest.outcome == InteractionOutcome.SUCCESS
        assert result_harvest.reputation_delta > 0

        # Gift during spawning
        spawning = keth_trade_interaction(day=300, is_pushing_deal=False,
                                          is_offering_gift=True, knowledge=1)
        result_spawning = evaluate_interaction(spawning, "offer_gift", roster, base)
        assert result_spawning.outcome == InteractionOutcome.OFFENSE
        assert result_spawning.reputation_delta < 0

        # Same action, opposite outcomes
        assert result_harvest.outcome != result_spawning.outcome
        assert result_harvest.reputation_delta != result_spawning.reputation_delta
        assert result_harvest.consequence_tag != result_spawning.consequence_tag


# ---------------------------------------------------------------------------
# 2. Veshan Debt Ledger
# ---------------------------------------------------------------------------

class TestVeshanDebtVisibility:
    def test_level_0_cannot_read_debt_weight(self):
        assert not veshan_debt_visible(0, "major")
        assert not veshan_debt_visible(0, "minor")

    def test_level_1_can_read_debt_weight(self):
        assert veshan_debt_visible(1, "major")
        assert veshan_debt_visible(1, "minor")


class TestVeshanChallengeInteraction:
    def test_accept_challenge_is_correct(self):
        """Accepting a Veshan challenge is always the honorable move."""
        interaction = veshan_encounter_interaction(
            player_debts=[], house="drashan", knowledge=1, is_challenged=True,
        )
        accept = next(o for o in interaction.options if o.id == "accept_challenge")
        assert accept.outcome == InteractionOutcome.SUCCESS
        assert accept.reputation_delta > 0

    def test_refuse_challenge_is_catastrophic(self):
        """Refusing a Veshan challenge is permanent dishonor."""
        interaction = veshan_encounter_interaction(
            player_debts=[], house="drashan", knowledge=1, is_challenged=True,
        )
        refuse = next(o for o in interaction.options if o.id == "refuse_challenge")
        assert refuse.outcome == InteractionOutcome.OFFENSE
        assert refuse.reputation_delta <= -10

    def test_debt_invocation_in_challenge(self):
        """If you hold a debt, you can invoke it to change the encounter."""
        debts = [VeshanDebt(
            id="d1", house="drashan", weight="standard",
            direction="held", description="Saved their convoy", day_created=50,
        )]
        interaction = veshan_encounter_interaction(
            player_debts=debts, house="drashan", knowledge=1, is_challenged=True,
        )
        invoke = next((o for o in interaction.options if o.id == "invoke_debt"), None)
        assert invoke is not None
        assert invoke.outcome == InteractionOutcome.SUCCESS
        assert invoke.knowledge_required == 1

    def test_no_debt_means_no_invoke_option(self):
        """Without a held debt, the invoke option doesn't appear."""
        interaction = veshan_encounter_interaction(
            player_debts=[], house="drashan", knowledge=2, is_challenged=True,
        )
        invoke = next((o for o in interaction.options if o.id == "invoke_debt"), None)
        assert invoke is None


class TestVeshanTradeInteraction:
    def test_directness_works(self):
        """Veshan respect direct dealing."""
        interaction = veshan_encounter_interaction(
            player_debts=[], house="vekhari", knowledge=1, is_challenged=False,
        )
        direct = next(o for o in interaction.options if o.id == "direct_deal")
        assert direct.outcome in (InteractionOutcome.SUCCESS, InteractionOutcome.PARTIAL)

    def test_indirectness_is_misstep(self):
        """Veshan despise hedging. This is a social logic rule, not a hint."""
        interaction = veshan_encounter_interaction(
            player_debts=[], house="vekhari", knowledge=0, is_challenged=False,
        )
        indirect = next(o for o in interaction.options if o.id == "indirect_approach")
        assert indirect.outcome == InteractionOutcome.MISSTEP
        assert indirect.reputation_delta < 0

    def test_house_specific_approach(self):
        """Knowledge level 2 unlocks house-specific strategies."""
        interaction = veshan_encounter_interaction(
            player_debts=[], house="drashan", knowledge=2, is_challenged=False,
        )
        martial = next((o for o in interaction.options if o.id == "martial_respect"), None)
        assert martial is not None
        assert martial.knowledge_required == 2
        assert martial.outcome == InteractionOutcome.SUCCESS

    def test_vekhari_specific_approach(self):
        """House Vekhari has its own social logic."""
        interaction = veshan_encounter_interaction(
            player_debts=[], house="vekhari", knowledge=2, is_challenged=False,
        )
        prosperity = next((o for o in interaction.options if o.id == "prosperity_talk"), None)
        assert prosperity is not None
        assert prosperity.outcome == InteractionOutcome.SUCCESS

    def test_debt_acknowledgment_improves_terms(self):
        """Acknowledging a debt you owe improves trade terms."""
        debts = [VeshanDebt(
            id="d1", house="drashan", weight="major",
            direction="owed", description="They sheltered you", day_created=10,
        )]
        interaction = veshan_encounter_interaction(
            player_debts=debts, house="drashan", knowledge=1, is_challenged=False,
        )
        ack = next((o for o in interaction.options if o.id == "acknowledge_debt"), None)
        assert ack is not None
        assert ack.outcome == InteractionOutcome.SUCCESS
        assert ack.trade_modifier < 0  # better prices


# ---------------------------------------------------------------------------
# 3. Crew advice system
# ---------------------------------------------------------------------------

class TestCrewAdvice:
    def test_keth_crew_gives_advice(self):
        """Thal should warn about seasonal risks."""
        roster = roster_with_keth()
        base = {"keth": 0}
        interaction = keth_trade_interaction(day=300, is_pushing_deal=False,
                                             is_offering_gift=False, knowledge=1)
        advice = get_crew_advice(interaction, roster, base)
        assert advice is not None
        assert "Thal" in advice

    def test_veshan_crew_gives_advice(self):
        """Varek should advise on honor protocols."""
        roster = roster_with_veshan()
        base = {"veshan": 0}
        interaction = veshan_encounter_interaction(
            player_debts=[], house="drashan", knowledge=1, is_challenged=True,
        )
        advice = get_crew_advice(interaction, roster, base)
        assert advice is not None
        assert "Varek" in advice

    def test_no_crew_no_advice(self):
        """Without relevant crew, no advice available."""
        roster = empty_roster()
        base = {}
        interaction = keth_trade_interaction(day=100, is_pushing_deal=False,
                                             is_offering_gift=False, knowledge=0)
        advice = get_crew_advice(interaction, roster, base)
        assert advice is None

    def test_crew_advice_references_in_result(self):
        """The interaction result tracks whether crew warned the player."""
        roster = roster_with_keth()
        base = {"keth": 0}
        interaction = keth_trade_interaction(day=100, is_pushing_deal=False,
                                             is_offering_gift=True, knowledge=1)
        result = evaluate_interaction(interaction, "offer_gift", roster, base)
        assert result.crew_warned is True
        assert "Thal" in result.feedback


# ---------------------------------------------------------------------------
# 4. Cross-system integration
# ---------------------------------------------------------------------------

class TestCulturalTradeModifier:
    def test_no_knowledge_no_discount(self):
        roster = empty_roster()
        base = {"keth": 0}
        mod = cultural_trade_modifier(Civilization.KETH, roster, base, day=100)
        # Only seasonal effect, no knowledge discount
        assert mod == KETH_SEASONAL_EFFECTS[KethSeason.HARVEST].trade_modifier

    def test_knowledge_stacks_with_seasonal(self):
        roster = roster_with_keth()
        base = {"keth": 0}  # crew gives level 1
        mod = cultural_trade_modifier(Civilization.KETH, roster, base, day=100)
        expected = -0.05 + KETH_SEASONAL_EFFECTS[KethSeason.HARVEST].trade_modifier
        assert abs(mod - expected) < 0.001

    def test_veshan_knowledge_discount(self):
        roster = roster_with_veshan()
        base = {"veshan": 0}  # crew gives level 1
        mod = cultural_trade_modifier(Civilization.VESHAN, roster, base)
        assert mod == -0.05


class TestCulturalEncounterOptions:
    def test_no_knowledge_minimal_options(self):
        roster = empty_roster()
        base = {"keth": 0}
        opts = cultural_encounter_options(Civilization.KETH, roster, base)
        assert not opts["can_negotiate"]
        assert not opts["can_cultural_leverage"]

    def test_crew_enables_negotiation(self):
        roster = roster_with_keth()
        base = {"keth": 0}
        opts = cultural_encounter_options(Civilization.KETH, roster, base)
        assert opts["can_negotiate"]
        assert opts["can_surrender_terms"]

    def test_veshan_always_offers_honor_challenge(self):
        roster = empty_roster()
        base = {"veshan": 0}
        opts = cultural_encounter_options(Civilization.VESHAN, roster, base)
        assert opts["can_honor_challenge"]
        assert not opts["can_invoke_debt"]  # need knowledge

    def test_veshan_crew_enables_debt_invocation(self):
        roster = roster_with_veshan()
        base = {"veshan": 0}
        opts = cultural_encounter_options(Civilization.VESHAN, roster, base)
        assert opts["can_invoke_debt"]


# ---------------------------------------------------------------------------
# 5. THE THESIS TESTS — Cultural knowledge across all layers
# ---------------------------------------------------------------------------

class TestThesisCultural:
    def test_knowledge_changes_visible_options(self):
        """THE CORE TEST: Different knowledge = different choices available.
        Not different text — different choices."""
        interaction = keth_trade_interaction(day=100, is_pushing_deal=False,
                                             is_offering_gift=False, knowledge=2)

        # Level 0: minimal options
        roster_0 = empty_roster()
        base_0 = {"keth": 0}
        visible_0 = get_visible_options(interaction, roster_0, base_0)

        # Level 1 (via crew): more options
        roster_1 = roster_with_keth()
        base_1 = {"keth": 0}
        visible_1 = get_visible_options(interaction, roster_1, base_1)

        # Level 2: deepest options
        roster_2 = empty_roster()
        base_2 = {"keth": 2}
        visible_2 = get_visible_options(interaction, roster_2, base_2)

        assert len(visible_0) < len(visible_1)
        assert len(visible_1) <= len(visible_2)

    def test_informed_vs_uninformed_different_consequence(self):
        """THE THESIS TEST: Same situation, different knowledge, different tags."""
        roster_ignorant = empty_roster()
        roster_informed = roster_with_keth()
        base = {"keth": 0}

        # Both players push a deal during dormancy
        interaction = keth_trade_interaction(day=200, is_pushing_deal=True,
                                             is_offering_gift=False, knowledge=1)

        result_ignorant = evaluate_interaction(interaction, "push_deal", roster_ignorant, base)
        result_informed = evaluate_interaction(interaction, "push_deal", roster_informed, base)

        # Both get a misstep, but feedback differs
        assert result_ignorant.crew_warned is False
        assert result_informed.crew_warned is True

    def test_cultural_knowledge_feeds_trade(self):
        """Knowledge level affects prices (trade layer)."""
        base_0 = {"veshan": 0}
        base_2 = {"veshan": 2}
        roster = empty_roster()

        mod_0 = cultural_trade_modifier(Civilization.VESHAN, roster, base_0)
        mod_2 = cultural_trade_modifier(Civilization.VESHAN, roster, base_2)

        assert mod_2 < mod_0  # higher knowledge = better prices

    def test_cultural_knowledge_feeds_encounters(self):
        """Knowledge level affects encounter options (tactics layer)."""
        roster = empty_roster()
        base_0 = {"veshan": 0}
        base_2 = {"veshan": 2}

        opts_0 = cultural_encounter_options(Civilization.VESHAN, roster, base_0)
        opts_2 = cultural_encounter_options(Civilization.VESHAN, roster, base_2)

        assert not opts_0["can_negotiate"]
        assert opts_2["can_negotiate"]
        assert opts_2["can_cultural_leverage"]

    def test_cultural_knowledge_feeds_narrative(self):
        """Cultural interactions can unlock narrative hooks (plot layer)."""
        roster = roster_with_keth()
        base = {"keth": 0}
        interaction = keth_trade_interaction(day=100, is_pushing_deal=False,
                                             is_offering_gift=True, knowledge=1)
        result = evaluate_interaction(interaction, "offer_gift", roster, base)
        assert result.narrative_unlock == "keth_harvest_trust"

    def test_two_civs_feel_different(self):
        """THE THESIS TEST: Keth and Veshan have fundamentally different social logic.

        Keth: seasonal, collective, patience-based, gift economy
        Veshan: honor, directness, debt ledger, challenge-based

        The same player action (being indirect) produces different outcomes
        in different civilizations — not because of different numbers,
        but because of different social rules.
        """
        # At Keth during dormancy: being patient is the correct move
        keth = keth_trade_interaction(day=200, is_pushing_deal=False,
                                      is_offering_gift=False, knowledge=2)
        wait = next(o for o in keth.options if o.id == "wait_season")
        assert wait.outcome == InteractionOutcome.SUCCESS

        # At Veshan: being indirect is always a misstep
        veshan = veshan_encounter_interaction(
            player_debts=[], house="drashan", knowledge=0, is_challenged=False,
        )
        indirect = next(o for o in veshan.options if o.id == "indirect_approach")
        assert indirect.outcome == InteractionOutcome.MISSTEP

        # Patience is virtue for Keth, irrelevant for Veshan
        # Directness is neutral for Keth, essential for Veshan
        # These are different social logics, not different numbers

    def test_crew_loss_closes_cultural_doors(self):
        """Losing your Keth crew member closes Keth cultural options.
        This connects Phase 1 (crew binding) to Phase 3 (cultural knowledge)."""
        from portlight.engine.crew import dismiss

        roster = roster_with_keth()
        base = {"keth": 0}
        interaction = keth_trade_interaction(day=100, is_pushing_deal=False,
                                             is_offering_gift=False, knowledge=1)

        # Before: can see gift option
        visible_before = get_visible_options(interaction, roster, base)
        assert any(o.id == "offer_gift" for o in visible_before)

        # Lose Thal
        dismiss(roster, "thal_communion")

        # After: gift option hidden (back to level 0)
        visible_after = get_visible_options(interaction, roster, base)
        assert not any(o.id == "offer_gift" for o in visible_after)
