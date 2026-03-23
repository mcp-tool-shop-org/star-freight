"""Star Freight content validation tests — Phase 5.

Every content unit must prove at least one system truth.
This file validates:
- Internal consistency (lanes connect to real stations, goods exist, etc.)
- System truth coverage (every station/lane/good/crew/contract proves something)
- Slice completeness (5 stations, 8 lanes, 5 goods, 2 crew, 3 contracts)
"""

from portlight.content.star_freight import (
    # Stations
    SLICE_STATIONS,
    Station,
    # Lanes
    SLICE_LANES,
    SpaceLane,
    # Goods
    SLICE_GOODS,
    TradeGood,
    # Crew
    create_thal,
    create_varek,
    create_sera,
    create_nera,
    create_ilen,
    # Contracts
    SLICE_CONTRACTS,
    ContractTemplate,
    # Ships
    SLICE_SHIPS,
    ShipClass,
    # Encounters
    SLICE_ENCOUNTERS,
    EncounterArchetype,
    # Validation
    validate_slice_content,
)
from portlight.engine.crew import (
    CrewRosterState,
    Civilization,
    LoyaltyTier,
    recruit,
    cultural_knowledge_level,
    get_ship_abilities,
    get_combat_abilities,
    get_narrative_hooks,
    crew_impact_report,
)


# ---------------------------------------------------------------------------
# 1. Internal consistency
# ---------------------------------------------------------------------------

class TestContentConsistency:
    def test_validate_slice_content_passes(self):
        """The built-in validator finds no errors."""
        errors = validate_slice_content()
        assert errors == [], f"Validation errors: {errors}"

    def test_station_count(self):
        assert len(SLICE_STATIONS) >= 5  # slice + expansion

    def test_lane_count(self):
        assert len(SLICE_LANES) >= 8  # slice + expansion

    def test_goods_count(self):
        assert len(SLICE_GOODS) >= 5  # 5 core + supporting goods for economy

    def test_contract_count(self):
        assert len(SLICE_CONTRACTS) >= 3  # slice + expansion

    def test_ship_count(self):
        assert len(SLICE_SHIPS) >= 3

    def test_encounter_count(self):
        assert len(SLICE_ENCOUNTERS) >= 3  # slice + expansion

    def test_all_civilizations_represented(self):
        civs = {s.civilization for s in SLICE_STATIONS.values()}
        assert civs == {"compact", "keth", "veshan", "orryn", "reach"}

    def test_all_stations_reachable(self):
        """Every station can be reached from every other station."""
        errors = validate_slice_content()
        reachability_errors = [e for e in errors if "not reachable" in e]
        assert reachability_errors == []

    def test_all_lane_endpoints_valid(self):
        for lane_id, lane in SLICE_LANES.items():
            assert lane.station_a in SLICE_STATIONS, f"Lane {lane_id}: bad station_a"
            assert lane.station_b in SLICE_STATIONS, f"Lane {lane_id}: bad station_b"

    def test_all_station_goods_valid(self):
        for station_id, station in SLICE_STATIONS.items():
            for good_id in station.produces:
                assert good_id in SLICE_GOODS, f"Station {station_id} produces unknown good {good_id}"
            for good_id in station.demands:
                assert good_id in SLICE_GOODS, f"Station {station_id} demands unknown good {good_id}"


# ---------------------------------------------------------------------------
# 2. System truth coverage
# ---------------------------------------------------------------------------

class TestStationsTruth:
    def test_every_station_has_cultural_rules(self):
        """Stations prove cultural logic truth."""
        for sid, station in SLICE_STATIONS.items():
            assert station.cultural_greeting, f"{sid}: no cultural greeting"
            assert station.cultural_restriction, f"{sid}: no cultural restriction"
            assert station.cultural_opportunity, f"{sid}: no cultural opportunity"

    def test_every_station_has_economic_role(self):
        """Stations prove economic truth."""
        for sid, station in SLICE_STATIONS.items():
            assert station.produces, f"{sid}: no produces"
            assert station.demands, f"{sid}: no demands"

    def test_stations_have_different_social_logic(self):
        """No two stations should feel the same."""
        greetings = [s.cultural_greeting for s in SLICE_STATIONS.values()]
        # All greetings should be unique
        assert len(set(greetings)) == len(greetings)

    def test_keth_station_has_seasonal_relevance(self):
        keth = SLICE_STATIONS["communion_relay"]
        assert "season" in keth.cultural_restriction.lower() or "harvest" in keth.cultural_opportunity.lower()

    def test_veshan_station_has_debt_relevance(self):
        veshan = SLICE_STATIONS["drashan_citadel"]
        assert "debt" in veshan.cultural_opportunity.lower() or "honor" in veshan.cultural_greeting.lower()

    def test_reach_station_has_faction_dynamics(self):
        reach = SLICE_STATIONS["ironjaw_den"]
        assert "faction" in reach.cultural_restriction.lower()


class TestLanesTruth:
    def test_lanes_have_varying_danger(self):
        """Not all lanes are equal — danger creates route decisions."""
        dangers = [l.danger for l in SLICE_LANES.values()]
        assert min(dangers) < 0.10  # some safe
        assert max(dangers) >= 0.25  # some dangerous

    def test_lanes_have_varying_distance(self):
        """Distance creates opportunity cost."""
        distances = [l.distance_days for l in SLICE_LANES.values()]
        assert min(distances) <= 2
        assert max(distances) >= 4

    def test_contraband_lanes_exist(self):
        """Some lanes have inspection risk — creates smuggling decisions."""
        has_contraband_risk = any(l.contraband_risk > 0 for l in SLICE_LANES.values())
        assert has_contraband_risk

    def test_terrain_variety(self):
        """Different terrain types exist — combat tactical variety."""
        terrains = {l.terrain for l in SLICE_LANES.values()}
        assert len(terrains) >= 3  # at least open, asteroid, nebula


class TestGoodsTruth:
    def test_cultural_goods_require_knowledge(self):
        """Some goods are culturally gated — proves cultural + crew dependency."""
        gated = [g for g in SLICE_GOODS.values() if g.cultural_restriction]
        assert len(gated) >= 2  # at least bio-crystal and weapons

    def test_contraband_goods_exist(self):
        """Some goods are contraband somewhere — creates risk decisions."""
        contraband = [g for g in SLICE_GOODS.values() if g.contraband_in]
        assert len(contraband) >= 2

    def test_price_range_creates_trade_opportunities(self):
        """Price spread must be wide enough for profitable routes."""
        prices = [g.base_price for g in SLICE_GOODS.values()]
        assert max(prices) / min(prices) >= 5  # at least 5x spread


class TestCrewTruth:
    def test_thal_proves_all_four_truths(self):
        """Thal proves crew dep, cultural logic, investigation, and combat."""
        thal = create_thal()
        roster = CrewRosterState()
        recruit(roster, thal)
        base = {}

        report = crew_impact_report(roster, base)

        # Crew dependency: has ship ability
        assert len(report["ship_abilities_active"]) == 1

        # Cultural logic: grants Keth level 1
        assert report["cultural_access"]["keth"]["level"] == 1

        # Combat: has abilities
        assert report["combat_abilities_available"] >= 2

        # Investigation: has narrative hooks
        assert len(report["narrative_hooks"]) == 1
        assert "keth_medical_debt" in report["narrative_hooks"][0]["hooks"]

    def test_varek_proves_all_four_truths(self):
        """Varek proves crew dep, cultural logic, combat, and investigation."""
        varek = create_varek()
        roster = CrewRosterState()
        recruit(roster, varek)
        base = {}

        report = crew_impact_report(roster, base)

        # Crew dependency: has ship ability
        assert len(report["ship_abilities_active"]) == 1

        # Cultural logic: grants Veshan level 1
        assert report["cultural_access"]["veshan"]["level"] == 1

        # Combat: has abilities
        assert report["combat_abilities_available"] >= 2

        # Narrative: has hooks
        assert len(report["narrative_hooks"]) == 1

    def test_thal_and_varek_cover_different_civilizations(self):
        """Two crew members open two different cultural doors."""
        thal = create_thal()
        varek = create_varek()
        roster = CrewRosterState()
        recruit(roster, thal)
        recruit(roster, varek)
        base = {}

        report = crew_impact_report(roster, base)
        assert report["cultural_access"]["keth"]["level"] == 1
        assert report["cultural_access"]["veshan"]["level"] == 1
        assert report["cultural_access"]["compact"]["level"] == 0  # no compact crew
        assert report["cultural_access"]["orryn"]["level"] == 0   # no orryn crew

    def test_losing_both_crew_closes_both_doors(self):
        """Without crew, cultural access reverts to base."""
        from portlight.engine.crew import dismiss

        thal = create_thal()
        varek = create_varek()
        roster = CrewRosterState()
        recruit(roster, thal)
        recruit(roster, varek)
        base = {}

        # Before
        report_before = crew_impact_report(roster, base)
        assert report_before["cultural_access"]["keth"]["level"] == 1
        assert report_before["cultural_access"]["veshan"]["level"] == 1

        dismiss(roster, "thal_communion")
        dismiss(roster, "varek_drashan")

        # After
        report_after = crew_impact_report(roster, base)
        assert report_after["cultural_access"]["keth"]["level"] == 0
        assert report_after["cultural_access"]["veshan"]["level"] == 0


class TestContractsTruth:
    def test_contracts_have_different_risk_types(self):
        """Three contracts, three different risk shapes."""
        risk_types = {c.risk_type for c in SLICE_CONTRACTS.values()}
        assert len(risk_types) == 3  # economic, political, combat

    def test_cultural_contract_requires_knowledge(self):
        cultural = SLICE_CONTRACTS["cultural_cargo"]
        assert cultural.cultural_knowledge_required.get("keth", 0) >= 1

    def test_bounty_contract_requires_reputation(self):
        bounty = SLICE_CONTRACTS["bounty_contract"]
        assert bounty.reputation_required  # has faction requirements

    def test_every_contract_has_consequences(self):
        for cid, contract in SLICE_CONTRACTS.items():
            assert contract.consequence_on_success, f"{cid}: no success consequence"
            assert contract.consequence_on_failure, f"{cid}: no failure consequence"

    def test_every_contract_documents_what_it_proves(self):
        for cid, contract in SLICE_CONTRACTS.items():
            assert contract.proves, f"{cid}: doesn't document which truth it proves"


class TestEncountersTruth:
    def test_encounters_have_cultural_options(self):
        """Every encounter has a cultural knowledge dimension."""
        for eid, enc in SLICE_ENCOUNTERS.items():
            assert enc.cultural_option, f"{eid}: no cultural option"

    def test_encounters_have_three_consequences(self):
        """Victory, retreat, and defeat all have distinct consequences."""
        for eid, enc in SLICE_ENCOUNTERS.items():
            assert enc.victory_consequence, f"{eid}: no victory consequence"
            assert enc.retreat_consequence, f"{eid}: no retreat consequence"
            assert enc.defeat_consequence, f"{eid}: no defeat consequence"

    def test_encounter_behaviors_vary(self):
        """Different civilizations fight differently."""
        behaviors = {e.behavior for e in SLICE_ENCOUNTERS.values()}
        assert len(behaviors) >= 3


# ---------------------------------------------------------------------------
# 3. No Portlight remnants
# ---------------------------------------------------------------------------

class TestNoPortlightRemnants:
    def test_no_maritime_language_in_stations(self):
        """No ocean/sailing references in station content."""
        maritime_words = ["sail", "harbor", "port_fee", "anchor", "sea ", "ocean",
                         "ship_class", "sloop", "brigantine", "galleon", "cutlass"]
        for sid, station in SLICE_STATIONS.items():
            text = f"{station.description} {station.cultural_greeting} {station.cultural_restriction}"
            for word in maritime_words:
                assert word not in text.lower(), f"Station {sid} contains maritime word: {word}"

    def test_no_maritime_language_in_lanes(self):
        maritime_words = ["sail", "harbor", "sea ", "ocean", "wind", "current"]
        for lid, lane in SLICE_LANES.items():
            for word in maritime_words:
                assert word not in lane.description.lower(), f"Lane {lid} contains: {word}"

    def test_no_silver_currency(self):
        """Star Freight uses credits, not silver."""
        for sid, station in SLICE_STATIONS.items():
            assert "silver" not in station.description.lower(), f"Station {sid} mentions silver"


# ---------------------------------------------------------------------------
# 4. Phase 7A: Working Lives Pack
# ---------------------------------------------------------------------------

class TestWorkingLives:
    """Validate that every 7A unit reinforces existing truths without drift."""

    def test_mourning_quay_exists(self):
        assert "mourning_quay" in SLICE_STATIONS
        mq = SLICE_STATIONS["mourning_quay"]
        assert mq.civilization == "keth"

    def test_mourning_quay_has_cultural_logic(self):
        mq = SLICE_STATIONS["mourning_quay"]
        assert "patience" in mq.cultural_opportunity.lower() or "cadence" in mq.cultural_opportunity.lower()
        assert mq.cultural_restriction  # has restrictions
        assert mq.knowledge_required_for_restricted >= 1

    def test_mourning_quay_differs_from_communion_relay(self):
        """Two Keth stations must feel different."""
        mq = SLICE_STATIONS["mourning_quay"]
        cr = SLICE_STATIONS["communion_relay"]
        assert mq.cultural_greeting != cr.cultural_greeting
        assert mq.produces != cr.produces  # different economic role
        assert mq.repair_cost_per_point != cr.repair_cost_per_point  # hospice is cheaper

    def test_pilgrims_ribbon_is_safe_but_scrutinized(self):
        pr = SLICE_LANES["pilgrims_ribbon"]
        assert pr.danger < 0.05  # very safe
        assert pr.contraband_risk >= 0.15  # but scrutinized

    def test_cinder_span_is_dangerous_but_unmonitored(self):
        cs = SLICE_LANES["cinder_span"]
        assert cs.danger >= 0.20  # dangerous
        assert cs.contraband_risk < 0.05  # unmonitored
        assert cs.terrain == "debris_field"

    def test_new_lanes_create_different_route_decisions(self):
        """Pilgrim's Ribbon and Cinder Span must be opposite risk profiles."""
        pr = SLICE_LANES["pilgrims_ribbon"]
        cs = SLICE_LANES["cinder_span"]
        assert pr.danger < cs.danger  # ribbon is safer
        assert pr.contraband_risk > cs.contraband_risk  # ribbon is more scrutinized

    def test_brood_silk_is_culturally_loaded(self):
        bs = SLICE_GOODS["brood_silk"]
        assert bs.origin_civ == "keth"
        assert bs.cultural_restriction  # not freely tradeable

    def test_black_seal_resin_is_politically_loaded(self):
        bsr = SLICE_GOODS["black_seal_resin"]
        assert bsr.origin_civ == "veshan"
        assert bsr.cultural_restriction

    def test_sera_proves_all_four_truths(self):
        """Sera must affect trade, combat, culture, and plot."""
        sera = create_sera()
        roster = CrewRosterState()
        recruit(roster, sera)
        base = {}

        report = crew_impact_report(roster, base)

        # Crew dependency: ship ability
        assert len(report["ship_abilities_active"]) == 1

        # Cultural logic: Compact knowledge
        assert report["cultural_access"]["compact"]["level"] >= 1

        # Combat: has abilities
        assert report["combat_abilities_available"] >= 2

        # Narrative: has hooks
        assert len(report["narrative_hooks"]) == 1
        assert "buried_ledger" in report["narrative_hooks"][0]["hooks"]

    def test_sera_contrasts_with_existing_crew(self):
        """Sera opens Compact doors that Thal and Varek can't."""
        sera = create_sera()
        thal = create_thal()
        roster = CrewRosterState()
        recruit(roster, sera)

        report = crew_impact_report(roster, {})
        assert report["cultural_access"]["compact"]["level"] >= 1
        assert report["cultural_access"]["keth"]["level"] == 0  # Sera is not Keth

    def test_witness_run_is_political_risk(self):
        wr = SLICE_CONTRACTS["witness_run"]
        assert wr.risk_type == "political"
        assert wr.consequence_on_failure  # failure has consequences
        assert wr.proves  # documents what it proves

    def test_cold_lantern_is_culturally_gated(self):
        cl = SLICE_CONTRACTS["cold_lantern_freight"]
        assert cl.cultural_knowledge_required.get("keth", 0) >= 1
        assert cl.risk_type == "political"

    def test_hearth_right_is_honor_encounter(self):
        hr = SLICE_ENCOUNTERS["hearth_right"]
        assert hr.behavior == "honor"
        assert hr.cultural_option  # has cultural dimension
        assert "knowledge" in hr.cultural_option.lower()

    def test_hearth_right_differs_from_veshan_challenge(self):
        """Hearth Right is lane dispute, not generic challenge."""
        hr = SLICE_ENCOUNTERS["hearth_right"]
        vc = SLICE_ENCOUNTERS["veshan_challenge"]
        assert hr.description != vc.description
        assert hr.ship_hull != vc.ship_hull  # different combat shape

    def test_ghost_tonnage_thread_exists(self):
        from portlight.engine.investigation import create_ghost_tonnage_thread
        thread = create_ghost_tonnage_thread()
        assert thread.id == "ghost_tonnage"
        assert len(thread.sources) >= 4  # multiple discovery paths

    def test_ghost_tonnage_has_multi_source_paths(self):
        from portlight.engine.investigation import create_ghost_tonnage_thread, SourceType
        thread = create_ghost_tonnage_thread()
        source_types = {s.source_type for s in thread.sources}
        assert len(source_types) >= 4  # trade, combat, cultural, crew, station

    def test_ghost_tonnage_differs_from_medical_cargo(self):
        """Ghost Tonnage is logistics fraud, not tech smuggling."""
        from portlight.engine.investigation import create_ghost_tonnage_thread, create_medical_cargo_thread
        gt = create_ghost_tonnage_thread()
        mc = create_medical_cargo_thread()
        assert gt.premise != mc.premise
        assert gt.delay_consequence_tag != mc.delay_consequence_tag

    def test_ghost_tonnage_requires_different_crew(self):
        """Ghost Tonnage benefits from Sera (documents) where Medical needs Thal."""
        from portlight.engine.investigation import create_ghost_tonnage_thread
        thread = create_ghost_tonnage_thread()
        crew_sources = [s for s in thread.sources if s.crew_required]
        crew_ids = {s.crew_required for s in crew_sources}
        assert "sera_vale" in crew_ids  # Sera opens document angles
        assert "thal_communion" in crew_ids  # Thal opens cultural angles

    def test_expanded_content_still_validates(self):
        """All content including 7A passes the structural validator."""
        errors = validate_slice_content()
        assert errors == [], f"Validation errors: {errors}"


# ---------------------------------------------------------------------------
# 5. Phase 7B: Houses, Audits, and Seizures
# ---------------------------------------------------------------------------

class TestHousesAuditsSeizures:
    """Validate that 7B units express institutional pressure through existing truths."""

    def test_registry_spindle_exists(self):
        assert "registry_spindle" in SLICE_STATIONS
        rs = SLICE_STATIONS["registry_spindle"]
        assert rs.civilization == "compact"

    def test_registry_spindle_is_jurisdiction_not_market(self):
        """Registry Spindle should feel like a jurisdiction, not another shop."""
        rs = SLICE_STATIONS["registry_spindle"]
        assert "jurisdiction" in rs.description.lower() or "administrative" in rs.description.lower()
        assert rs.docking_fee > SLICE_STATIONS["meridian_exchange"].docking_fee  # more expensive
        assert rs.knowledge_required_for_restricted >= 2

    def test_registry_spindle_differs_from_meridian_exchange(self):
        """Two Compact stations must feel fundamentally different."""
        rs = SLICE_STATIONS["registry_spindle"]
        me = SLICE_STATIONS["meridian_exchange"]
        assert rs.cultural_greeting != me.cultural_greeting
        assert rs.description != me.description
        assert set(rs.produces) != set(me.produces)

    def test_white_corridor_is_monitored(self):
        wc = SLICE_LANES["white_corridor"]
        assert wc.danger < 0.05  # very safe from pirates
        assert wc.contraband_risk >= 0.25  # heavily monitored

    def test_grain_eclipse_is_ambiguous(self):
        ge = SLICE_LANES["grain_eclipse"]
        assert ge.terrain == "nebula"  # cover for ambiguity
        assert ge.danger > 0.10  # some danger
        assert ge.contraband_risk < wc_risk()  # less monitored than White Corridor

    def test_bond_plate_makes_legitimacy_portable(self):
        bp = SLICE_GOODS["bond_plate"]
        assert bp.origin_civ == "compact"
        assert "legitimacy" in bp.description.lower() or "certification" in bp.description.lower()

    def test_reserve_grain_is_politically_governed(self):
        rg = SLICE_GOODS["reserve_grain"]
        assert "politically" in rg.description.lower() or "authorization" in rg.description.lower()

    def test_nera_proves_all_four_truths(self):
        nera = create_nera()
        roster = CrewRosterState()
        recruit(roster, nera)
        base = {}

        report = crew_impact_report(roster, base)

        # Ship ability
        assert len(report["ship_abilities_active"]) == 1

        # Cultural: Compact knowledge
        assert report["cultural_access"]["compact"]["level"] >= 1

        # Combat: has abilities
        assert report["combat_abilities_available"] >= 2

        # Narrative: has hooks
        assert len(report["narrative_hooks"]) == 1
        assert "falsified_seizure" in report["narrative_hooks"][0]["hooks"]

    def test_nera_differs_from_sera(self):
        """Nera is institutional power. Sera is cargo law. Must be distinct."""
        nera = create_nera()
        sera = create_sera()
        assert nera.role != sera.role
        assert nera.ship_skill != sera.ship_skill
        assert set(nera.abilities) != set(sera.abilities)
        assert nera.narrative_hooks != sera.narrative_hooks
        assert nera.pay_rate != sera.pay_rate  # different value proposition

    def test_bonded_relief_run_is_administratively_fragile(self):
        br = SLICE_CONTRACTS["bonded_relief_run"]
        assert br.risk_type == "political"
        assert "fragility" in br.description.lower() or "seal" in br.description.lower()

    def test_claim_courier_is_legal_race(self):
        cc = SLICE_CONTRACTS["claim_courier"]
        assert cc.deadline_days <= 5  # tight deadline
        assert "arrival order" in cc.description.lower() or "truth" in cc.description.lower()

    def test_seizure_notice_is_defensive_encounter(self):
        """Seizure Notice should be institutional, not predatory."""
        sn = SLICE_ENCOUNTERS["seizure_notice"]
        assert sn.behavior == "defensive"  # they wait for you to resist
        assert sn.civilization == "compact"
        assert "paperwork" in sn.description.lower() or "institutional" in sn.description.lower()

    def test_seizure_notice_has_crew_dependent_options(self):
        sn = SLICE_ENCOUNTERS["seizure_notice"]
        assert "nera" in sn.cultural_option.lower() or "sera" in sn.cultural_option.lower()

    def test_paper_fleet_thread_exists(self):
        from portlight.engine.investigation import create_paper_fleet_thread
        thread = create_paper_fleet_thread()
        assert thread.id == "paper_fleet"
        assert len(thread.sources) >= 4

    def test_paper_fleet_differs_from_ghost_tonnage(self):
        from portlight.engine.investigation import create_paper_fleet_thread, create_ghost_tonnage_thread
        pf = create_paper_fleet_thread()
        gt = create_ghost_tonnage_thread()
        assert pf.premise != gt.premise
        assert pf.delay_consequence_tag != gt.delay_consequence_tag

    def test_paper_fleet_requires_nera(self):
        """Paper Fleet should benefit from Nera's institutional knowledge."""
        from portlight.engine.investigation import create_paper_fleet_thread
        thread = create_paper_fleet_thread()
        crew_sources = {s.crew_required for s in thread.sources if s.crew_required}
        assert "nera_quill" in crew_sources

    def test_paper_fleet_connects_to_disgrace(self):
        """Paper Fleet should tie back to the player's discharge."""
        from portlight.engine.investigation import get_paper_fleet_fragments
        frags = get_paper_fleet_fragments()
        # At least one fragment should reference the player's discharge
        discharge_refs = [f for f in frags.values() if "discharge" in f.content.lower()]
        assert len(discharge_refs) >= 1

    def test_all_7b_content_validates(self):
        errors = validate_slice_content()
        assert errors == [], f"Validation errors: {errors}"


def wc_risk() -> float:
    """Helper: get White Corridor contraband risk."""
    return SLICE_LANES["white_corridor"].contraband_risk


# ---------------------------------------------------------------------------
# 6. Phase 7C: Shortages, Sanctions, and Convoys
# ---------------------------------------------------------------------------

class TestShortagesSanctionsConvoys:
    """Validate that 7C units express managed scarcity through existing truths."""

    def test_queue_of_flags_exists(self):
        assert "queue_of_flags" in SLICE_STATIONS
        qf = SLICE_STATIONS["queue_of_flags"]
        assert qf.civilization == "orryn"

    def test_queue_of_flags_is_relief_choked(self):
        qf = SLICE_STATIONS["queue_of_flags"]
        assert "queue" in qf.cultural_greeting.lower() or "priority" in qf.cultural_restriction.lower()
        assert qf.fuel_cost_per_day > 20  # scarcity premium

    def test_queue_of_flags_differs_from_grand_drift(self):
        """Two Orryn stations must feel different."""
        qf = SLICE_STATIONS["queue_of_flags"]
        gd = SLICE_STATIONS["grand_drift"]
        assert qf.cultural_greeting != gd.cultural_greeting
        assert qf.fuel_cost_per_day != gd.fuel_cost_per_day

    def test_mercy_track_is_convoy_protected(self):
        mt = SLICE_LANES["mercy_track"]
        assert mt.danger <= 0.02  # almost no pirate risk
        assert mt.contraband_risk >= 0.30  # extreme scrutiny

    def test_red_wake_is_unpoliced(self):
        rw = SLICE_LANES["red_wake"]
        assert rw.danger >= 0.20  # dangerous
        assert rw.contraband_risk <= 0.02  # nobody watching
        assert rw.terrain == "debris_field"

    def test_mercy_and_red_wake_are_opposite(self):
        """Convoy lane vs chaos lane — opposite pressure profiles."""
        mt = SLICE_LANES["mercy_track"]
        rw = SLICE_LANES["red_wake"]
        assert mt.danger < rw.danger
        assert mt.contraband_risk > rw.contraband_risk

    def test_ration_grain_is_political(self):
        rg = SLICE_GOODS["ration_grain"]
        assert "political" in rg.description.lower() or "profiteer" in rg.description.lower()

    def test_coolant_ampoules_cascade(self):
        ca = SLICE_GOODS["coolant_ampoules"]
        assert "cascade" in ca.description.lower() or "shortage" in ca.description.lower()

    def test_ilen_proves_all_four_truths(self):
        ilen = create_ilen()
        roster = CrewRosterState()
        recruit(roster, ilen)
        base = {}
        report = crew_impact_report(roster, base)
        assert len(report["ship_abilities_active"]) == 1
        assert report["cultural_access"]["orryn"]["level"] >= 1
        assert report["combat_abilities_available"] >= 2
        assert len(report["narrative_hooks"]) == 1

    def test_ilen_differs_from_sera_and_nera(self):
        """Ilen is supply politics. Sera is cargo law. Nera is institutional power."""
        ilen = create_ilen()
        sera = create_sera()
        nera = create_nera()
        assert ilen.role != sera.role
        assert ilen.role != nera.role
        assert ilen.civilization != sera.civilization  # Ilen is Orryn
        assert ilen.ship_skill != sera.ship_skill
        assert ilen.ship_skill != nera.ship_skill

    def test_priority_relief_is_time_pressure(self):
        pr = SLICE_CONTRACTS["priority_relief"]
        assert pr.deadline_days <= 5
        assert pr.risk_type == "economic"

    def test_embargo_slip_is_moral_divergence(self):
        es = SLICE_CONTRACTS["embargo_slip"]
        assert "moral" in es.description.lower() or "forbidden" in es.description.lower()
        assert es.risk_type == "political"

    def test_convoy_refusal_is_bureaucratic_not_predatory(self):
        cr = SLICE_ENCOUNTERS["convoy_refusal"]
        assert cr.behavior == "defensive"
        assert cr.civilization == "orryn"
        assert "priority" in cr.cultural_option.lower() or "schedule" in cr.cultural_option.lower()

    def test_dry_ledger_thread_exists(self):
        from portlight.engine.investigation import create_dry_ledger_thread
        thread = create_dry_ledger_thread()
        assert thread.id == "dry_ledger"
        assert len(thread.sources) >= 4

    def test_dry_ledger_differs_from_other_threads(self):
        from portlight.engine.investigation import (
            create_dry_ledger_thread, create_ghost_tonnage_thread, create_paper_fleet_thread,
        )
        dl = create_dry_ledger_thread()
        gt = create_ghost_tonnage_thread()
        pf = create_paper_fleet_thread()
        assert dl.premise != gt.premise
        assert dl.premise != pf.premise
        assert dl.delay_consequence_tag != gt.delay_consequence_tag
        assert dl.delay_consequence_tag != pf.delay_consequence_tag

    def test_dry_ledger_requires_ilen(self):
        from portlight.engine.investigation import create_dry_ledger_thread
        thread = create_dry_ledger_thread()
        crew_sources = {s.crew_required for s in thread.sources if s.crew_required}
        assert "ilen_marr" in crew_sources

    def test_all_7c_content_validates(self):
        errors = validate_slice_content()
        assert errors == [], f"Validation errors: {errors}"
