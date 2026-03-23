"""Tests for port institutional profiles — NPCs, institutions, relationships."""

from portlight.content.port_institutions import (
    ALL_INSTITUTIONS,
    ALL_NPCS,
    PORT_INSTITUTIONAL_PROFILES,
)
from portlight.content.ports import PORTS


class TestPortoNovoProfile:
    """Porto Novo must have a complete institutional profile."""

    def test_porto_novo_exists(self):
        assert "porto_novo" in PORT_INSTITUTIONAL_PROFILES

    def test_has_seven_institutions(self):
        profile = PORT_INSTITUTIONAL_PROFILES["porto_novo"]
        assert len(profile.institutions) == 7

    def test_has_seven_npcs(self):
        profile = PORT_INSTITUTIONAL_PROFILES["porto_novo"]
        assert len(profile.npcs) == 7

    def test_institution_types_complete(self):
        profile = PORT_INSTITUTIONAL_PROFILES["porto_novo"]
        types = {inst.institution_type for inst in profile.institutions}
        expected = {"harbor_master", "exchange", "shipyard", "broker", "tavern", "customs", "governor"}
        assert types == expected

    def test_every_institution_has_npc(self):
        profile = PORT_INSTITUTIONAL_PROFILES["porto_novo"]
        npc_ids = {npc.id for npc in profile.npcs}
        for inst in profile.institutions:
            assert inst.npc_id in npc_ids, f"Institution {inst.id} references missing NPC {inst.npc_id}"

    def test_power_structure_defined(self):
        profile = PORT_INSTITUTIONAL_PROFILES["porto_novo"]
        assert profile.power_structure
        assert profile.internal_tension

    def test_governor_title(self):
        profile = PORT_INSTITUTIONAL_PROFILES["porto_novo"]
        assert profile.governor_title == "Port Governor"


class TestAlManarProfile:
    """Al-Manar must have a complete institutional profile."""

    def test_al_manar_exists(self):
        assert "al_manar" in PORT_INSTITUTIONAL_PROFILES

    def test_has_seven_institutions(self):
        profile = PORT_INSTITUTIONAL_PROFILES["al_manar"]
        assert len(profile.institutions) == 7

    def test_has_seven_npcs(self):
        profile = PORT_INSTITUTIONAL_PROFILES["al_manar"]
        assert len(profile.npcs) == 7

    def test_has_apothecary(self):
        """Al-Manar uniquely has an apothecary institution."""
        profile = PORT_INSTITUTIONAL_PROFILES["al_manar"]
        types = {inst.institution_type for inst in profile.institutions}
        assert "apothecary" in types

    def test_no_shipyard(self):
        """Al-Manar has no shipyard — that's Porto Novo's advantage."""
        profile = PORT_INSTITUTIONAL_PROFILES["al_manar"]
        types = {inst.institution_type for inst in profile.institutions}
        assert "shipyard" not in types

    def test_governor_is_merchant_princess(self):
        profile = PORT_INSTITUTIONAL_PROFILES["al_manar"]
        assert profile.governor_title == "Merchant Princess"

    def test_hakim_is_yasmins_nephew(self):
        """Cross-NPC family relationship should be reflected."""
        hakim = ALL_NPCS["am_hakim"]
        yasmin = ALL_NPCS["am_yasmin"]
        assert "am_yasmin" in hakim.relationship_notes
        assert "am_hakim" in yasmin.relationship_notes
        assert "nephew" in yasmin.relationship_notes["am_hakim"].lower()

    def test_zara_connected_to_porto_novo(self):
        """Zara was poached from Porto Novo — her rumor should reference it."""
        zara = ALL_NPCS["am_inspector_zara"]
        assert "porto novo" in zara.rumor.lower() or "salva" in zara.rumor.lower()


class TestSilvaBayProfile:
    """Silva Bay — the shipwrights' republic."""

    def test_silva_bay_exists(self):
        assert "silva_bay" in PORT_INSTITUTIONAL_PROFILES

    def test_has_seven_institutions(self):
        profile = PORT_INSTITUTIONAL_PROFILES["silva_bay"]
        assert len(profile.institutions) == 7

    def test_has_seven_npcs(self):
        profile = PORT_INSTITUTIONAL_PROFILES["silva_bay"]
        assert len(profile.npcs) == 7

    def test_has_shipyard(self):
        profile = PORT_INSTITUTIONAL_PROFILES["silva_bay"]
        types = {inst.institution_type for inst in profile.institutions}
        assert "shipyard" in types

    def test_governed_by_council(self):
        profile = PORT_INSTITUTIONAL_PROFILES["silva_bay"]
        assert profile.governor_title == "Brotherhood Council"

    def test_no_single_governor_npc(self):
        """The 'governor' is a collective council, not an individual."""
        council = ALL_NPCS["sb_council"]
        assert council.personality == "collective"

    def test_pires_is_outsider(self):
        """Pires should reference Porto Novo / being an outsider."""
        pires = ALL_NPCS["sb_customs_pires"]
        assert "porto novo" in pires.description.lower() or "outsider" in pires.description.lower()

    def test_ana_grew_up_in_tavern(self):
        ana = ALL_NPCS["sb_broker_ana"]
        rosa = ALL_NPCS["sb_rosa"]
        assert "sb_rosa" in ana.relationship_notes
        assert "sb_broker_ana" in rosa.relationship_notes


class TestCorsairsRestProfile:
    """Corsair's Rest — the lawless cove."""

    def test_corsairs_rest_exists(self):
        assert "corsairs_rest" in PORT_INSTITUTIONAL_PROFILES

    def test_has_seven_institutions(self):
        profile = PORT_INSTITUTIONAL_PROFILES["corsairs_rest"]
        assert len(profile.institutions) == 7

    def test_has_seven_npcs(self):
        profile = PORT_INSTITUTIONAL_PROFILES["corsairs_rest"]
        assert len(profile.npcs) == 7

    def test_governed_by_tide(self):
        profile = PORT_INSTITUTIONAL_PROFILES["corsairs_rest"]
        assert profile.governor_title == "The Tide's Voice"

    def test_has_apothecary_not_shipyard(self):
        """Corsair's Rest has a surgery but no shipyard."""
        profile = PORT_INSTITUTIONAL_PROFILES["corsairs_rest"]
        types = {inst.institution_type for inst in profile.institutions}
        assert "apothecary" in types
        assert "shipyard" not in types

    def test_little_fish_is_youngest(self):
        fish = ALL_NPCS["cr_little_fish"]
        assert "fourteen" in fish.description.lower() or "girl" in fish.description.lower()

    def test_mama_lucia_fled_porto_novo(self):
        mama = ALL_NPCS["cr_mama_lucia"]
        assert "porto novo" in mama.agenda.lower()

    def test_no_one_is_tide_representative(self):
        no_one = ALL_NPCS["cr_no_one"]
        assert "crimson tide" in no_one.description.lower()


class TestNPCQuality:
    """All NPCs must have complete personality data."""

    def test_all_npcs_have_name(self):
        for npc_id, npc in ALL_NPCS.items():
            assert npc.name, f"{npc_id} missing name"

    def test_all_npcs_have_description(self):
        for npc_id, npc in ALL_NPCS.items():
            assert npc.description, f"{npc_id} missing description"

    def test_all_npcs_have_agenda(self):
        for npc_id, npc in ALL_NPCS.items():
            assert npc.agenda, f"{npc_id} missing agenda"

    def test_all_npcs_have_three_greetings(self):
        for npc_id, npc in ALL_NPCS.items():
            assert npc.greeting_neutral, f"{npc_id} missing greeting_neutral"
            assert npc.greeting_friendly, f"{npc_id} missing greeting_friendly"
            assert npc.greeting_hostile, f"{npc_id} missing greeting_hostile"

    def test_all_npcs_have_rumor(self):
        for npc_id, npc in ALL_NPCS.items():
            assert npc.rumor, f"{npc_id} missing rumor"

    def test_all_npcs_have_relationship_notes(self):
        for npc_id, npc in ALL_NPCS.items():
            assert len(npc.relationship_notes) >= 3, (
                f"{npc_id} needs >= 3 relationship notes, has {len(npc.relationship_notes)}"
            )

    def test_relationship_notes_reference_valid_npcs(self):
        for npc_id, npc in ALL_NPCS.items():
            for ref_id in npc.relationship_notes:
                assert ref_id in ALL_NPCS, (
                    f"{npc_id} references unknown NPC '{ref_id}'"
                )

    def test_npc_port_ids_valid(self):
        for npc_id, npc in ALL_NPCS.items():
            assert npc.port_id in PORTS, f"{npc_id} references unknown port '{npc.port_id}'"


class TestInstitutionQuality:
    """All institutions must have complete data."""

    def test_all_institutions_have_description(self):
        for inst_id, inst in ALL_INSTITUTIONS.items():
            assert inst.description, f"{inst_id} missing description"

    def test_all_institutions_have_function(self):
        for inst_id, inst in ALL_INSTITUTIONS.items():
            assert inst.function, f"{inst_id} missing function"

    def test_all_institutions_have_political_leaning(self):
        for inst_id, inst in ALL_INSTITUTIONS.items():
            assert inst.political_leaning, f"{inst_id} missing political_leaning"

    def test_institution_port_ids_valid(self):
        for inst_id, inst in ALL_INSTITUTIONS.items():
            assert inst.port_id in PORTS, f"{inst_id} references unknown port '{inst.port_id}'"


class TestNPCRelationshipWeb:
    """Porto Novo NPCs should form a connected relationship web."""

    def test_no_npc_is_isolated(self):
        """Every NPC should be referenced by at least one other NPC."""
        referenced = set()
        for npc in ALL_NPCS.values():
            for ref_id in npc.relationship_notes:
                referenced.add(ref_id)
        for npc_id in ALL_NPCS:
            assert npc_id in referenced, f"{npc_id} is never referenced by another NPC"

    def test_key_tension_exists(self):
        """Marta and Costa should reference each other as rivals."""
        marta = ALL_NPCS["pn_marta"]
        costa = ALL_NPCS["pn_senhora_costa"]
        assert "pn_senhora_costa" in marta.relationship_notes
        assert "pn_marta" in costa.relationship_notes

    def test_enzo_feared_by_no_one_but_salva(self):
        """Enzo should fear Salva specifically."""
        enzo = ALL_NPCS["pn_old_enzo"]
        assert "pn_inspector_salva" in enzo.relationship_notes
        assert "fear" in enzo.relationship_notes["pn_inspector_salva"].lower()
