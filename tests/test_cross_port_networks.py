"""Tests for cross-port NPC networks — merchants, taverns, brokers, inspectors."""

from portlight.content.cross_port_networks import (
    ALL_CROSS_PORT_RELATIONSHIPS,
    BROKER_NETWORK,
    INSPECTOR_NETWORK,
    MERCHANT_RELATIONSHIPS,
    TAVERN_NETWORK,
    get_network_relationships,
    get_relationships_for_npc,
    get_relationships_for_port,
)
from portlight.content.ports import PORTS


class TestNetworkCoverage:
    """All four networks must have meaningful content."""

    def test_merchant_network_exists(self):
        assert len(MERCHANT_RELATIONSHIPS) >= 6

    def test_tavern_network_exists(self):
        assert len(TAVERN_NETWORK) >= 5

    def test_broker_network_exists(self):
        assert len(BROKER_NETWORK) >= 5

    def test_inspector_network_exists(self):
        assert len(INSPECTOR_NETWORK) >= 4

    def test_total_relationships(self):
        assert len(ALL_CROSS_PORT_RELATIONSHIPS) >= 20


class TestRelationshipIntegrity:
    """All relationships must reference valid NPCs and ports."""

    def test_all_ports_valid(self):
        for r in ALL_CROSS_PORT_RELATIONSHIPS:
            assert r.npc_a_port in PORTS, f"Unknown port '{r.npc_a_port}' in {r.npc_a_name}'s relationship"
            assert r.npc_b_port in PORTS, f"Unknown port '{r.npc_b_port}' in {r.npc_b_name}'s relationship"

    def test_cross_port_not_same_port(self):
        for r in ALL_CROSS_PORT_RELATIONSHIPS:
            assert r.npc_a_port != r.npc_b_port, (
                f"{r.npc_a_name} and {r.npc_b_name} are at the same port ({r.npc_a_port})"
            )

    def test_all_have_description(self):
        for r in ALL_CROSS_PORT_RELATIONSHIPS:
            assert r.description, f"Missing description: {r.npc_a_name} ↔ {r.npc_b_name}"
            assert r.player_impact, f"Missing player_impact: {r.npc_a_name} ↔ {r.npc_b_name}"

    def test_dispositions_valid(self):
        valid = {"allied", "rival", "professional", "personal", "respected"}
        for r in ALL_CROSS_PORT_RELATIONSHIPS:
            assert r.disposition in valid, f"Invalid disposition '{r.disposition}'"

    def test_networks_valid(self):
        valid = {"merchant", "tavern", "broker", "inspector"}
        for r in ALL_CROSS_PORT_RELATIONSHIPS:
            assert r.network in valid, f"Invalid network '{r.network}'"


class TestNetworkLookups:
    """Lookup helpers work correctly."""

    def test_get_merchant_network(self):
        merchants = get_network_relationships("merchant")
        assert len(merchants) == len(MERCHANT_RELATIONSHIPS)

    def test_get_relationships_for_port(self):
        porto_novo_rels = get_relationships_for_port("porto_novo")
        assert len(porto_novo_rels) >= 3, "Porto Novo should have multiple cross-port relationships"

    def test_get_relationships_for_npc(self):
        salva_rels = get_relationships_for_npc("pn_inspector_salva")
        assert len(salva_rels) >= 2, "Inspector Salva should have multiple cross-port connections"


class TestKeyRelationships:
    """Verify critical cross-port threads exist."""

    def test_iron_rivalry_exists(self):
        """Henrik vs. Kofi should be in the merchant network."""
        iron_rivals = [r for r in MERCHANT_RELATIONSHIPS
                       if ("ih_forge_master" in (r.npc_a_id, r.npc_b_id)
                           and "ip_foreman_kofi" in (r.npc_a_id, r.npc_b_id))]
        assert len(iron_rivals) == 1

    def test_salva_zara_exists(self):
        """Salva and Zara should be in the inspector network."""
        pairs = [r for r in INSPECTOR_NETWORK
                 if ("pn_inspector_salva" in (r.npc_a_id, r.npc_b_id)
                     and "am_inspector_zara" in (r.npc_a_id, r.npc_b_id))]
        assert len(pairs) == 1

    def test_fernanda_tariq_rivalry(self):
        """The broker war should exist."""
        rivals = [r for r in BROKER_NETWORK
                  if ("pn_broker_reis" in (r.npc_a_id, r.npc_b_id)
                      and "am_broker_tariq" in (r.npc_a_id, r.npc_b_id))]
        assert len(rivals) == 1

    def test_mama_lucia_mama_smoke(self):
        """Shadow port mothers connection."""
        mamas = [r for r in TAVERN_NETWORK
                 if ("cr_mama_lucia" in (r.npc_a_id, r.npc_b_id)
                     and "sn_mama_smoke" in (r.npc_a_id, r.npc_b_id))]
        assert len(mamas) == 1

    def test_shadow_broker_pipeline(self):
        """Ghost and Ghost Broker connection."""
        ghosts = [r for r in BROKER_NETWORK
                  if ("cr_ghost" in (r.npc_a_id, r.npc_b_id)
                      and "sn_ghost_broker" in (r.npc_a_id, r.npc_b_id))]
        assert len(ghosts) == 1
