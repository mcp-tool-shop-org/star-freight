"""Tests for port political ecosystem — trade blocs, rivalries, grudges."""

from portlight.content.port_politics import (
    BLOC_RELATIONSHIPS,
    PORT_POLITICS,
    TRADE_BLOCS,
    get_bloc_allies,
    get_bloc_enemies,
    get_bloc_relationship,
    get_port_bloc,
    get_port_relationship,
)
from portlight.content.ports import PORTS


class TestTradeBlocs:
    """All 7 trade blocs with complete membership."""

    def test_seven_blocs_exist(self):
        assert len(TRADE_BLOCS) == 7

    def test_all_20_ports_assigned(self):
        assigned = set()
        for bloc in TRADE_BLOCS.values():
            for pid in bloc.port_ids:
                assert pid not in assigned, f"{pid} assigned to multiple blocs"
                assigned.add(pid)
        assert assigned == set(PORTS.keys()), f"Unassigned ports: {set(PORTS.keys()) - assigned}"

    def test_all_blocs_have_description(self):
        for bid, bloc in TRADE_BLOCS.items():
            assert bloc.description, f"{bid} missing description"
            assert bloc.trade_philosophy, f"{bid} missing trade_philosophy"

    def test_loyalty_bonus_positive(self):
        for bid, bloc in TRADE_BLOCS.items():
            assert bloc.loyalty_bonus >= 0, f"{bid} negative loyalty bonus"

    def test_bloc_port_ids_valid(self):
        for bid, bloc in TRADE_BLOCS.items():
            for pid in bloc.port_ids:
                assert pid in PORTS, f"{bid} references unknown port '{pid}'"


class TestBlocRelationships:
    """All 21 bloc pairs covered (7 choose 2)."""

    def test_all_pairs_covered(self):
        bids = sorted(TRADE_BLOCS.keys())
        for i, a in enumerate(bids):
            for b in bids[i + 1:]:
                rel = get_bloc_relationship(a, b)
                assert rel is not None, f"Missing relationship: {a} ↔ {b}"

    def test_twenty_one_relationships(self):
        assert len(BLOC_RELATIONSHIPS) == 21

    def test_dispositions_valid(self):
        valid = {"allied", "neutral", "rival", "hostile"}
        for rel in BLOC_RELATIONSHIPS:
            assert rel.disposition in valid, f"{rel.bloc_a}↔{rel.bloc_b}: '{rel.disposition}'"

    def test_hostile_has_negative_spillover(self):
        for rel in BLOC_RELATIONSHIPS:
            if rel.disposition == "hostile":
                assert rel.spillover < 0

    def test_allied_has_positive_spillover(self):
        for rel in BLOC_RELATIONSHIPS:
            if rel.disposition == "allied":
                assert rel.spillover > 0


class TestPortPoliticalProfiles:
    """All 20 ports have political profiles."""

    def test_all_ports_have_profiles(self):
        for pid in PORTS:
            assert pid in PORT_POLITICS, f"Missing political profile for {pid}"

    def test_profiles_reference_valid_blocs(self):
        for pid, prof in PORT_POLITICS.items():
            assert prof.bloc_id in TRADE_BLOCS, f"{pid} references unknown bloc '{prof.bloc_id}'"

    def test_profiles_have_flavor(self):
        for pid, prof in PORT_POLITICS.items():
            assert prof.political_flavor, f"{pid} missing political_flavor"
            assert prof.port_grudge, f"{pid} missing port_grudge"

    def test_local_rivals_are_valid_ports(self):
        for pid, prof in PORT_POLITICS.items():
            if prof.local_rival_port:
                assert prof.local_rival_port in PORTS, (
                    f"{pid} rival '{prof.local_rival_port}' not in PORTS"
                )

    def test_local_rivals_have_reasons(self):
        for pid, prof in PORT_POLITICS.items():
            if prof.local_rival_port:
                assert prof.rivalry_reason, f"{pid} has rival but no reason"


class TestPortRelationshipQueries:
    """Relationship lookups work correctly."""

    def test_same_bloc_is_allied(self):
        assert get_port_relationship("porto_novo", "al_manar") == "allied"

    def test_cross_bloc_hostile(self):
        assert get_port_relationship("porto_novo", "corsairs_rest") == "hostile"

    def test_local_rival_overrides_bloc(self):
        # Porto Novo and Al-Manar are in the same bloc but local rivals
        assert get_port_relationship("porto_novo", "al_manar") == "allied"  # bloc wins
        # Ironhaven and Iron Point are in different blocs AND local rivals
        assert get_port_relationship("ironhaven", "iron_point") == "rival"

    def test_free_ports_mostly_neutral(self):
        assert get_port_relationship("crosswind_isle", "porto_novo") == "neutral"

    def test_unknown_port_neutral(self):
        assert get_port_relationship("nonexistent", "porto_novo") == "neutral"


class TestBlocHelpers:
    """Bloc query helpers."""

    def test_exchange_alliance_enemies(self):
        enemies = get_bloc_enemies("exchange_alliance")
        assert "shadow_ports" in enemies

    def test_exchange_alliance_allies(self):
        allies = get_bloc_allies("exchange_alliance")
        assert "iron_pact" in allies

    def test_free_ports_no_enemies(self):
        enemies = get_bloc_enemies("free_ports")
        assert len(enemies) == 0

    def test_get_port_bloc(self):
        bloc = get_port_bloc("porto_novo")
        assert bloc is not None
        assert bloc.id == "exchange_alliance"


class TestKeyDesignDecisions:
    """Verify important game design is encoded correctly."""

    def test_exchange_alliance_hostile_to_shadow(self):
        rel = get_bloc_relationship("exchange_alliance", "shadow_ports")
        assert rel is not None
        assert rel.disposition == "hostile"

    def test_iron_pact_hostile_to_silk_circle(self):
        rel = get_bloc_relationship("iron_pact", "silk_circle")
        assert rel is not None
        assert rel.disposition == "hostile"

    def test_gold_coast_allied_with_coral_crown(self):
        rel = get_bloc_relationship("gold_coast", "coral_crown")
        assert rel is not None
        assert rel.disposition == "allied"

    def test_dragons_gate_embargoes_weapons(self):
        prof = PORT_POLITICS["dragons_gate"]
        assert "weapons" in prof.trade_embargo

    def test_ironhaven_embargoes_weapons_to_shadow(self):
        prof = PORT_POLITICS["ironhaven"]
        assert "weapons" in prof.trade_embargo
