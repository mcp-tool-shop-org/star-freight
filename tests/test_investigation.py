"""Investigation system tests — Phase 4 thesis proof.

Acceptance bar:
  - A lead surfaces through normal play, not quest handout
  - Same thread progresses from at least two different source types
  - Journal records fragments with source and implication, not tasks
  - New knowledge changes trade, encounter, and narrative readings
  - Delaying a thread produces real world consequences
  - Crew presence changes what can be understood or pursued
  - Partial truth can be acted on but carries risk

The bar: "I learned something dangerous by living this life."
Not: "I unlocked the next story quest."
"""

from portlight.engine.investigation import (
    # Types
    EvidenceGrade,
    Fragment,
    SourceType,
    LeadSource,
    ThreadState,
    InvestigationThread,
    InvestigationState,
    # Core operations
    discover_fragment,
    check_corroboration,
    upgrade_corroborated,
    check_lead_sources,
    check_delay_consequences,
    # Campaign impact
    investigation_trade_impact,
    investigation_encounter_impact,
    investigation_narrative_impact,
    # Journal
    get_journal_view,
    # Thread factory
    create_medical_cargo_thread,
    get_medical_cargo_fragments,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_state_with_thread() -> InvestigationState:
    """Create investigation state with the medical cargo thread."""
    thread = create_medical_cargo_thread()
    return InvestigationState(threads={thread.id: thread})


def make_fragment(fragment_id: str, day: int = 10) -> Fragment:
    """Get a pre-defined fragment with a specific acquisition day."""
    frags = get_medical_cargo_fragments()
    frag = frags[fragment_id]
    frag.day_acquired = day
    return frag


# ---------------------------------------------------------------------------
# 1. Evidence grade model
# ---------------------------------------------------------------------------

class TestEvidenceGrade:
    def test_weight_ordering(self):
        assert EvidenceGrade.RUMOR.weight < EvidenceGrade.CLUE.weight
        assert EvidenceGrade.CLUE.weight < EvidenceGrade.CORROBORATED.weight
        assert EvidenceGrade.CORROBORATED.weight < EvidenceGrade.ACTIONABLE.weight
        assert EvidenceGrade.ACTIONABLE.weight < EvidenceGrade.LOCKED.weight

    def test_grade_values(self):
        assert EvidenceGrade.RUMOR.weight == 1
        assert EvidenceGrade.LOCKED.weight == 5


# ---------------------------------------------------------------------------
# 2. Fragment discovery
# ---------------------------------------------------------------------------

class TestFragmentDiscovery:
    def test_first_fragment_activates_thread(self):
        state = make_state_with_thread()
        frag = make_fragment("med_dock_rumor", day=15)
        result = discover_fragment(state, "medical_cargo", frag)

        assert result["thread_state_changed"]
        assert result["new_state"] == "active"
        assert state.threads["medical_cargo"].state == ThreadState.ACTIVE

    def test_duplicate_fragment_rejected(self):
        state = make_state_with_thread()
        frag = make_fragment("med_dock_rumor", day=15)
        discover_fragment(state, "medical_cargo", frag)

        # Try adding same fragment again
        frag2 = make_fragment("med_dock_rumor", day=20)
        result = discover_fragment(state, "medical_cargo", frag2)
        assert result.get("duplicate") is True

    def test_multiple_fragments_advance_thread(self):
        state = make_state_with_thread()
        discover_fragment(state, "medical_cargo", make_fragment("med_dock_rumor", day=10))
        discover_fragment(state, "medical_cargo", make_fragment("med_price_anomaly", day=15))

        # Two fragments from different sources → ADVANCED
        assert state.threads["medical_cargo"].state == ThreadState.ADVANCED

    def test_actionable_evidence_reaches_critical(self):
        state = make_state_with_thread()
        discover_fragment(state, "medical_cargo", make_fragment("med_dock_rumor", day=10))
        discover_fragment(state, "medical_cargo", make_fragment("med_personal_connection", day=20))

        # Personal connection is ACTIONABLE grade
        assert state.threads["medical_cargo"].state == ThreadState.CRITICAL

    def test_fragment_recorded_in_all_fragments(self):
        state = make_state_with_thread()
        frag = make_fragment("med_dock_rumor", day=15)
        discover_fragment(state, "medical_cargo", frag)
        assert len(state.all_fragments) == 1
        assert state.all_fragments[0].id == "med_dock_rumor"


# ---------------------------------------------------------------------------
# 3. Multiple paths (same thread, different sources)
# ---------------------------------------------------------------------------

class TestMultiplePaths:
    def test_trade_path(self):
        """Thread can advance from trade source."""
        state = make_state_with_thread()
        frag = make_fragment("med_price_anomaly", day=10)
        result = discover_fragment(state, "medical_cargo", frag)
        assert result["source"] == "trade"
        assert state.threads["medical_cargo"].state == ThreadState.ACTIVE

    def test_combat_path(self):
        """Thread can advance from combat source."""
        state = make_state_with_thread()
        frag = make_fragment("med_manifest", day=10)
        result = discover_fragment(state, "medical_cargo", frag)
        assert result["source"] == "combat"
        assert state.threads["medical_cargo"].state == ThreadState.ACTIVE

    def test_cultural_path(self):
        """Thread can advance from cultural source (requires crew)."""
        state = make_state_with_thread()
        frag = make_fragment("med_seasonal_mismatch", day=10)
        result = discover_fragment(state, "medical_cargo", frag)
        assert result["source"] == "cultural"
        assert frag.crew_interpreter == "thal_communion"

    def test_trade_plus_combat_corroborate(self):
        """Two different source types with shared connections corroborate."""
        state = make_state_with_thread()
        discover_fragment(state, "medical_cargo", make_fragment("med_price_anomaly", day=10))
        discover_fragment(state, "medical_cargo", make_fragment("med_manifest", day=15))

        thread = state.threads["medical_cargo"]
        pairs = check_corroboration(thread)
        assert len(pairs) > 0  # trade + combat corroborate

    def test_same_source_type_does_not_corroborate(self):
        """Two fragments from the same source type don't corroborate each other."""
        state = make_state_with_thread()
        # Both are different fragments but let's create a scenario
        # where we test the rule: same source type = no corroboration
        thread = state.threads["medical_cargo"]
        f1 = Fragment(
            id="test_a", thread_id="medical_cargo", content="A",
            source_type="trade", source_detail="source A",
            grade=EvidenceGrade.CLUE, day_acquired=10,
            connections=["test_b"],
        )
        f2 = Fragment(
            id="test_b", thread_id="medical_cargo", content="B",
            source_type="trade", source_detail="source B",
            grade=EvidenceGrade.CLUE, day_acquired=15,
            connections=["test_a"],
        )
        thread.fragments = [f1, f2]
        pairs = check_corroboration(thread)
        assert len(pairs) == 0  # same source type


# ---------------------------------------------------------------------------
# 4. Corroboration upgrade
# ---------------------------------------------------------------------------

class TestCorroboration:
    def test_corroboration_upgrades_grade(self):
        state = make_state_with_thread()
        discover_fragment(state, "medical_cargo", make_fragment("med_price_anomaly", day=10))
        discover_fragment(state, "medical_cargo", make_fragment("med_manifest", day=15))

        thread = state.threads["medical_cargo"]
        upgraded = upgrade_corroborated(thread)
        assert len(upgraded) > 0

        # Both should now be at least CORROBORATED
        for frag in thread.fragments:
            if frag.id in upgraded:
                assert frag.grade.weight >= EvidenceGrade.CORROBORATED.weight


# ---------------------------------------------------------------------------
# 5. Source matching (game events → leads)
# ---------------------------------------------------------------------------

class TestSourceMatching:
    def test_trade_event_matches_source(self):
        thread = create_medical_cargo_thread()
        matches = check_lead_sources(
            thread,
            event_type="trade",
            event_trigger="trade_medical_at_keth",
            crew_ids=["dax_maren"],
            cultural_knowledge={"keth": 0},
            reputation={"compact": 0},
        )
        assert len(matches) == 1
        assert matches[0].fragment_id == "med_price_anomaly"

    def test_crew_required_source_fails_without_crew(self):
        thread = create_medical_cargo_thread()
        matches = check_lead_sources(
            thread,
            event_type="cultural",
            event_trigger="keth_medical_analysis",
            crew_ids=[],  # no Thal
            cultural_knowledge={"keth": 1},
            reputation={},
        )
        assert len(matches) == 0

    def test_crew_required_source_succeeds_with_crew(self):
        thread = create_medical_cargo_thread()
        matches = check_lead_sources(
            thread,
            event_type="cultural",
            event_trigger="keth_medical_analysis",
            crew_ids=["thal_communion"],
            cultural_knowledge={"keth": 1},
            reputation={},
        )
        assert len(matches) == 1
        assert matches[0].fragment_id == "med_seasonal_mismatch"

    def test_knowledge_gate_blocks_source(self):
        thread = create_medical_cargo_thread()
        matches = check_lead_sources(
            thread,
            event_type="cultural",
            event_trigger="keth_medical_analysis",
            crew_ids=["thal_communion"],
            cultural_knowledge={"keth": 0},  # not enough knowledge
            reputation={},
        )
        assert len(matches) == 0

    def test_already_found_fragment_not_matched(self):
        """Once a fragment is found, its source stops matching."""
        thread = create_medical_cargo_thread()
        # Pre-add the fragment
        frag = make_fragment("med_price_anomaly", day=5)
        thread.fragments.append(frag)

        matches = check_lead_sources(
            thread,
            event_type="trade",
            event_trigger="trade_medical_at_keth",
            crew_ids=[],
            cultural_knowledge={},
            reputation={},
        )
        assert len(matches) == 0  # already found


# ---------------------------------------------------------------------------
# 6. Delay consequences
# ---------------------------------------------------------------------------

class TestDelayConsequences:
    def test_no_consequence_within_window(self):
        state = make_state_with_thread()
        discover_fragment(state, "medical_cargo", make_fragment("med_dock_rumor", day=10))

        consequences = check_delay_consequences(state, current_day=30)
        assert len(consequences) == 0  # within 45-day window

    def test_consequence_after_delay(self):
        state = make_state_with_thread()
        discover_fragment(state, "medical_cargo", make_fragment("med_dock_rumor", day=10))

        consequences = check_delay_consequences(state, current_day=70)
        assert len(consequences) == 1
        assert consequences[0]["thread_id"] == "medical_cargo"
        assert consequences[0]["consequence_tag"] == "medical_evidence_destroyed"

    def test_delay_severity_escalates(self):
        state = make_state_with_thread()
        discover_fragment(state, "medical_cargo", make_fragment("med_dock_rumor", day=10))

        # 60 days stale = mild
        c1 = check_delay_consequences(state, current_day=70)
        assert c1[0]["severity"] == "mild"

        # Reset warnings for next check
        state.delay_warnings_issued.clear()

        # 90 days stale = serious
        c2 = check_delay_consequences(state, current_day=100)
        assert c2[0]["severity"] == "serious"

    def test_dormant_threads_have_no_delay(self):
        state = make_state_with_thread()
        # Thread is dormant — no fragments yet
        consequences = check_delay_consequences(state, current_day=100)
        assert len(consequences) == 0

    def test_resolved_threads_have_no_delay(self):
        state = make_state_with_thread()
        state.threads["medical_cargo"].state = ThreadState.RESOLVED
        state.threads["medical_cargo"].last_progress_day = 10
        consequences = check_delay_consequences(state, current_day=200)
        assert len(consequences) == 0


# ---------------------------------------------------------------------------
# 7. Campaign impact
# ---------------------------------------------------------------------------

class TestCampaignImpact:
    def test_trade_impact_from_fragments(self):
        state = make_state_with_thread()
        discover_fragment(state, "medical_cargo", make_fragment("med_price_anomaly", day=10))

        impact = investigation_trade_impact(state)
        assert len(impact["price_anomalies_flagged"]) > 0

    def test_encounter_impact_from_advanced_thread(self):
        state = make_state_with_thread()
        discover_fragment(state, "medical_cargo", make_fragment("med_dock_rumor", day=10))
        discover_fragment(state, "medical_cargo", make_fragment("med_price_anomaly", day=15))
        # Now ADVANCED

        impact = investigation_encounter_impact(state)
        assert impact["threat_level_modifier"] > 0  # knowing more = more dangerous

    def test_encounter_impact_critical_gives_awareness(self):
        state = make_state_with_thread()
        discover_fragment(state, "medical_cargo", make_fragment("med_dock_rumor", day=10))
        discover_fragment(state, "medical_cargo", make_fragment("med_personal_connection", day=20))
        # Now CRITICAL

        impact = investigation_encounter_impact(state)
        assert impact["ambush_awareness"] is True

    def test_narrative_impact_crew_interpreter(self):
        state = make_state_with_thread()
        discover_fragment(state, "medical_cargo", make_fragment("med_seasonal_mismatch", day=10))

        impact = investigation_narrative_impact(state)
        assert "thal_communion" in impact["crew_loyalty_threads"]

    def test_overall_progress_tracking(self):
        state = make_state_with_thread()
        assert state.total_progress == 0

        discover_fragment(state, "medical_cargo", make_fragment("med_dock_rumor", day=10))
        discover_fragment(state, "medical_cargo", make_fragment("med_price_anomaly", day=15))
        assert state.total_progress >= 1  # ADVANCED = 1


# ---------------------------------------------------------------------------
# 8. Journal view
# ---------------------------------------------------------------------------

class TestJournal:
    def test_dormant_thread_not_in_journal(self):
        state = make_state_with_thread()
        journal = get_journal_view(state)
        assert len(journal) == 0  # dormant = invisible

    def test_active_thread_shows_fragments(self):
        state = make_state_with_thread()
        discover_fragment(state, "medical_cargo", make_fragment("med_dock_rumor", day=10))

        journal = get_journal_view(state)
        assert len(journal) == 1
        entry = journal[0]
        assert entry["title"] == "The Medical Shipment"
        assert entry["state"] == "active"
        assert len(entry["fragments"]) == 1

    def test_journal_fragment_has_source_not_task(self):
        """Fragments are records, not objectives."""
        state = make_state_with_thread()
        discover_fragment(state, "medical_cargo", make_fragment("med_dock_rumor", day=10))

        journal = get_journal_view(state)
        frag_entry = journal[0]["fragments"][0]
        assert "source" in frag_entry
        assert frag_entry["source"] != ""
        assert "grade" in frag_entry
        # No "objective" or "task" fields


# ---------------------------------------------------------------------------
# 9. THE THESIS TESTS
# ---------------------------------------------------------------------------

class TestThesisInvestigation:
    def test_lead_from_normal_play(self):
        """A lead surfaces through trade, not a quest giver."""
        thread = create_medical_cargo_thread()
        matches = check_lead_sources(
            thread,
            event_type="trade",
            event_trigger="trade_medical_at_keth",
            crew_ids=[],
            cultural_knowledge={},
            reputation={},
        )
        assert len(matches) == 1
        # The trigger is "trade_medical_at_keth" — a normal trade action

    def test_multiple_source_types_progress_same_thread(self):
        """THE THESIS TEST: Same thread advances from trade AND combat."""
        state = make_state_with_thread()

        # Trade source
        discover_fragment(state, "medical_cargo", make_fragment("med_price_anomaly", day=10))
        assert state.threads["medical_cargo"].state == ThreadState.ACTIVE

        # Combat source
        discover_fragment(state, "medical_cargo", make_fragment("med_manifest", day=20))
        assert state.threads["medical_cargo"].state == ThreadState.ADVANCED

        # Two different source types, same thread
        sources = {f.source_type for f in state.threads["medical_cargo"].fragments}
        assert len(sources) >= 2

    def test_crew_gates_cultural_interpretation(self):
        """THE THESIS TEST: Thal is needed to interpret the Keth angle."""
        thread = create_medical_cargo_thread()

        # Without Thal: can't access cultural source
        no_crew = check_lead_sources(
            thread, "cultural", "keth_medical_analysis",
            crew_ids=[], cultural_knowledge={"keth": 1}, reputation={},
        )
        assert len(no_crew) == 0

        # With Thal: cultural source opens
        with_crew = check_lead_sources(
            thread, "cultural", "keth_medical_analysis",
            crew_ids=["thal_communion"], cultural_knowledge={"keth": 1}, reputation={},
        )
        assert len(with_crew) == 1

    def test_knowledge_changes_trade_and_encounters_and_narrative(self):
        """THE THESIS TEST: Investigation feeds all three layers."""
        state = make_state_with_thread()

        # Start: no impact
        trade_0 = investigation_trade_impact(state)
        encounter_0 = investigation_encounter_impact(state)
        narrative_0 = investigation_narrative_impact(state)

        # Add fragments to reach CRITICAL
        discover_fragment(state, "medical_cargo", make_fragment("med_price_anomaly", day=10))
        discover_fragment(state, "medical_cargo", make_fragment("med_seasonal_mismatch", day=15))
        discover_fragment(state, "medical_cargo", make_fragment("med_personal_connection", day=20))

        # After: all three layers changed
        trade_1 = investigation_trade_impact(state)
        encounter_1 = investigation_encounter_impact(state)
        narrative_1 = investigation_narrative_impact(state)

        # Trade: price anomalies now visible
        assert len(trade_1["price_anomalies_flagged"]) > len(trade_0["price_anomalies_flagged"])

        # Encounters: threat awareness changed
        assert encounter_1["ambush_awareness"] != encounter_0["ambush_awareness"]

        # Narrative: crew loyalty thread opened
        assert len(narrative_1["crew_loyalty_threads"]) > len(narrative_0["crew_loyalty_threads"])

    def test_delay_produces_real_consequence(self):
        """THE THESIS TEST: Ignoring the plot has a cost."""
        state = make_state_with_thread()
        discover_fragment(state, "medical_cargo", make_fragment("med_dock_rumor", day=10))

        # 60+ days later, no progress
        consequences = check_delay_consequences(state, current_day=70)
        assert len(consequences) == 1
        assert consequences[0]["consequence_tag"] == "medical_evidence_destroyed"
        assert "cold" in consequences[0]["warning"].lower() or "moving" in consequences[0]["warning"].lower()

    def test_partial_truth_is_distinguishable(self):
        """The player can tell rumor from proof."""
        state = make_state_with_thread()

        # Add a rumor
        discover_fragment(state, "medical_cargo", make_fragment("med_dock_rumor", day=10))
        journal = get_journal_view(state)
        assert journal[0]["fragments"][0]["grade"] == "rumor"

        # Add an actionable lead
        discover_fragment(state, "medical_cargo", make_fragment("med_personal_connection", day=20))
        journal = get_journal_view(state)
        grades = [f["grade"] for f in journal[0]["fragments"]]
        assert "rumor" in grades
        assert "actionable" in grades
        # Player can see the difference

    def test_full_thread_resolution(self):
        """THE THESIS TEST: A complete investigation resolves the thread."""
        state = make_state_with_thread()

        # Discover enough fragments to resolve
        discover_fragment(state, "medical_cargo", make_fragment("med_price_anomaly", day=10))
        discover_fragment(state, "medical_cargo", make_fragment("med_manifest", day=15))
        discover_fragment(state, "medical_cargo", make_fragment("med_seasonal_mismatch", day=20))
        discover_fragment(state, "medical_cargo", make_fragment("med_personal_connection", day=25))

        # Corroborate
        upgrade_corroborated(state.threads["medical_cargo"])

        # Check resolution
        thread = state.threads["medical_cargo"]
        total_weight = sum(f.grade.weight for f in thread.fragments)
        assert total_weight >= thread.resolution_threshold
        assert thread.state == ThreadState.RESOLVED

        # Resolution opens endgame path
        impact = investigation_narrative_impact(state)
        assert "medical_cargo" in impact["endgame_paths_available"]
