"""Campaign content — milestone definitions across 6 commercial families.

24 milestones that make a run legible. Not badge clutter — each represents
a real commercial achievement derived from actual business history.

Families:
  - Regional Foothold: becoming established somewhere
  - Lawful House: legitimacy and premium lawful commerce
  - Shadow Network: high-risk, high-margin gray commerce
  - Oceanic Reach: long-haul and distance power
  - Commercial Finance: mature capital management
  - Integrated House: fully formed multi-system operation
"""

from portlight.engine.campaign import MilestoneFamily, MilestoneSpec

# ---------------------------------------------------------------------------
# All milestone specs
# ---------------------------------------------------------------------------

MILESTONE_SPECS: list[MilestoneSpec] = [
    # ===== Regional Foothold (5) =====
    MilestoneSpec(
        id="foothold_first_warehouse",
        name="First Warehouse",
        family=MilestoneFamily.REGIONAL_FOOTHOLD,
        description="Leased your first warehouse — cargo can now be staged for timing plays.",
        evaluator="first_warehouse",
    ),
    MilestoneSpec(
        id="foothold_first_broker",
        name="First Broker Office",
        family=MilestoneFamily.REGIONAL_FOOTHOLD,
        description="Opened your first broker office — intelligence shapes the contract board.",
        evaluator="first_broker",
    ),
    MilestoneSpec(
        id="foothold_standing_established",
        name="Regional Standing",
        family=MilestoneFamily.REGIONAL_FOOTHOLD,
        description="Reached meaningful standing in one region through consistent commerce.",
        evaluator="standing_one_region",
    ),
    MilestoneSpec(
        id="foothold_strong_standing",
        name="Strong Regional Presence",
        family=MilestoneFamily.REGIONAL_FOOTHOLD,
        description="Achieved strong standing in one region — a known and respected operator.",
        evaluator="strong_standing_one_region",
    ),
    MilestoneSpec(
        id="foothold_two_regions",
        name="Two-Region Presence",
        family=MilestoneFamily.REGIONAL_FOOTHOLD,
        description="Established operations in two different regions.",
        evaluator="presence_two_regions",
    ),

    # ===== Lawful House (6) =====
    MilestoneSpec(
        id="lawful_credible_trust",
        name="Credible Operator",
        family=MilestoneFamily.LAWFUL_HOUSE,
        description="The market recognizes you as credible — new opportunities open.",
        evaluator="credible_trust",
    ),
    MilestoneSpec(
        id="lawful_reliable_trust",
        name="Reliable Operator",
        family=MilestoneFamily.LAWFUL_HOUSE,
        description="Reliable commercial trust — premium contracts and better credit terms.",
        evaluator="reliable_trust",
    ),
    MilestoneSpec(
        id="lawful_first_charter",
        name="First Regional Charter",
        family=MilestoneFamily.LAWFUL_HOUSE,
        description="Acquired your first regional trade charter — formal commercial standing.",
        evaluator="regional_charter",
    ),
    MilestoneSpec(
        id="lawful_high_rep_charter",
        name="High Reputation Charter",
        family=MilestoneFamily.LAWFUL_HOUSE,
        description="Earned the highest commercial charter — recognized across all regions.",
        evaluator="high_rep_charter",
    ),
    MilestoneSpec(
        id="lawful_contract_record",
        name="Proven Contract Record",
        family=MilestoneFamily.LAWFUL_HOUSE,
        description="Completed 5+ contracts — a track record of reliable delivery.",
        evaluator="lawful_contracts_completed",
    ),
    MilestoneSpec(
        id="lawful_low_heat_scaling",
        name="Clean Growth",
        family=MilestoneFamily.LAWFUL_HOUSE,
        description="Reached reliable trust while keeping heat low — growth without suspicion.",
        evaluator="low_heat_scaling",
    ),

    # ===== Shadow Network (4) =====
    MilestoneSpec(
        id="shadow_first_discreet",
        name="First Discreet Delivery",
        family=MilestoneFamily.SHADOW_NETWORK,
        description="Completed your first discreet luxury delivery — the shadow lane is open.",
        evaluator="first_discreet_success",
    ),
    MilestoneSpec(
        id="shadow_elevated_heat",
        name="Operating Under Scrutiny",
        family=MilestoneFamily.SHADOW_NETWORK,
        description="Sustained high heat while remaining profitable — the authorities watch, but you persist.",
        evaluator="elevated_heat_sustained",
    ),
    MilestoneSpec(
        id="shadow_profitability",
        name="Shadow Profitability",
        family=MilestoneFamily.SHADOW_NETWORK,
        description="Strong net profit despite elevated customs scrutiny.",
        evaluator="shadow_profitability",
    ),
    MilestoneSpec(
        id="shadow_seizure_recovery",
        name="Seizure Recovery",
        family=MilestoneFamily.SHADOW_NETWORK,
        description="Survived a cargo seizure and rebuilt — the business endures.",
        evaluator="seizure_recovery",
    ),

    # ===== Oceanic Reach (4) =====
    MilestoneSpec(
        id="oceanic_ei_access",
        name="East Indies Access",
        family=MilestoneFamily.OCEANIC_REACH,
        description="Acquired the East Indies Access Charter — the far trade routes are open.",
        evaluator="ei_access",
    ),
    MilestoneSpec(
        id="oceanic_ei_broker",
        name="East Indies Presence",
        family=MilestoneFamily.OCEANIC_REACH,
        description="Opened a broker office in the East Indies — local intelligence secured.",
        evaluator="ei_broker",
    ),
    MilestoneSpec(
        id="oceanic_galleon",
        name="Galleon Operator",
        family=MilestoneFamily.OCEANIC_REACH,
        description="Operating a Merchant Galleon — the long-haul workhorse.",
        evaluator="galleon_deployed",
    ),
    MilestoneSpec(
        id="oceanic_ei_standing",
        name="East Indies Reputation",
        family=MilestoneFamily.OCEANIC_REACH,
        description="Strong standing in the East Indies — a known operator in the spice quarter.",
        evaluator="ei_standing",
    ),

    # ===== Commercial Finance (4) =====
    MilestoneSpec(
        id="finance_first_insurance",
        name="First Insurance Payout",
        family=MilestoneFamily.COMMERCIAL_FINANCE,
        description="An insurance claim was paid — risk pricing proves its worth.",
        evaluator="first_insurance_success",
    ),
    MilestoneSpec(
        id="finance_credit_opened",
        name="First Credit Draw",
        family=MilestoneFamily.COMMERCIAL_FINANCE,
        description="Drew on a credit line — leverage is now part of the business.",
        evaluator="credit_opened",
    ),
    MilestoneSpec(
        id="finance_credit_clean",
        name="Clean Credit Record",
        family=MilestoneFamily.COMMERCIAL_FINANCE,
        description="Significant borrowing with no defaults — the market trusts your debt service.",
        evaluator="credit_clean",
    ),
    MilestoneSpec(
        id="finance_leveraged_expansion",
        name="Leveraged Expansion",
        family=MilestoneFamily.COMMERCIAL_FINANCE,
        description="Used credit to fund infrastructure growth — capital working for capital.",
        evaluator="leveraged_expansion",
    ),

    # ===== Integrated House (4) =====  [total: 27 milestones]
    # Actually we have 27, user spec said 20-28, this is in range.
    # But let's target ~25. Remove the "sustained_three_regions" to keep it at 26,
    # or add one more integrated house milestone. Let's keep all 27 — it's in range.
    MilestoneSpec(
        id="integrated_multi_region",
        name="Multi-Region Infrastructure",
        family=MilestoneFamily.INTEGRATED_HOUSE,
        description="Infrastructure assets across multiple regions — a commercial network.",
        evaluator="multi_region_infra",
    ),
    MilestoneSpec(
        id="integrated_major_contracts",
        name="Cross-Region Contract House",
        family=MilestoneFamily.INTEGRATED_HOUSE,
        description="5+ contracts completed with standing in 2+ regions.",
        evaluator="major_contracts_multi_region",
    ),
    MilestoneSpec(
        id="integrated_full_spectrum",
        name="Full-Spectrum Operation",
        family=MilestoneFamily.INTEGRATED_HOUSE,
        description="Using warehouses, brokers, licenses, insurance, and credit — a complete commercial toolkit.",
        evaluator="full_spectrum",
    ),
    MilestoneSpec(
        id="integrated_brigantine",
        name="Ship Upgrade",
        family=MilestoneFamily.INTEGRATED_HOUSE,
        description="Upgraded beyond the starting sloop — the business justified the investment.",
        evaluator="brigantine_acquired",
    ),
]


# Convenience: spec lookup by ID
MILESTONE_BY_ID: dict[str, MilestoneSpec] = {s.id: s for s in MILESTONE_SPECS}


def get_milestone_spec(milestone_id: str) -> MilestoneSpec | None:
    """Get a milestone spec by ID."""
    return MILESTONE_BY_ID.get(milestone_id)


# ---------------------------------------------------------------------------
# Career profile scoring weights
# ---------------------------------------------------------------------------
# Each tag has: base scoring weights for session-truth signals,
# and milestone families that contribute to it.
# Tunable here so balance changes don't require engine edits.

# Which milestone families feed each profile tag (tag -> list of families).
# Milestones in these families add to the tag's lifetime score.
PROFILE_MILESTONE_FAMILIES: dict[str, list[str]] = {
    "Lawful House": ["lawful_house", "regional_foothold"],
    "Shadow Operator": ["shadow_network"],
    "Oceanic Carrier": ["oceanic_reach"],
    "Contract Specialist": ["regional_foothold", "integrated_house"],
    "Infrastructure Builder": ["integrated_house", "commercial_finance"],
    "Leveraged Trader": ["commercial_finance"],
    "Risk-Managed Merchant": ["commercial_finance"],
}

# Points awarded per milestone completed in an aligned family.
MILESTONE_WEIGHT: float = 8.0

# Recent window: milestones completed within the last N days count
# toward recent_score as well as lifetime.
RECENT_WINDOW_DAYS: int = 20

# Recent milestone bonus (on top of lifetime credit).
RECENT_MILESTONE_BONUS: float = 5.0

# Lifetime vs recent blend for combined_score.
LIFETIME_WEIGHT: float = 0.6
RECENT_WEIGHT: float = 0.4

# Confidence thresholds (on combined_score).
CONFIDENCE_THRESHOLDS: dict[str, float] = {
    "Defining": 60.0,
    "Strong": 35.0,
    "Moderate": 15.0,
    # Below Moderate -> Forming
}

# Minimum combined_score to appear as a secondary trait.
SECONDARY_THRESHOLD: float = 15.0

# Minimum recent_score for an emerging tag (must not already be primary).
EMERGING_MIN_RECENT: float = 12.0


# ---------------------------------------------------------------------------
# Victory path thresholds
# ---------------------------------------------------------------------------
# Each path has tunable thresholds for its requirements.
# Keeps calibration out of engine logic.

LAWFUL_THRESHOLDS = {
    "trust_rank": 4,                  # trusted tier
    "high_rep_charter": True,
    "regional_licenses_or_standing": 2,  # 2+ regional licenses or 2+ regions at standing 15+
    "contracts_completed": 8,
    "max_heat_cap": 5,
    "silver_min": 2000,
}

SHADOW_THRESHOLDS = {
    "discreet_completions": 2,        # luxury/discreet contract successes
    "heat_floor": 10,                 # must have operated under meaningful heat
    "heat_ceiling": 40,               # not catastrophic — still functioning
    "profit_under_heat": 2000,        # net profit while sustaining heat
    "silver_min": 1500,
    "trades_under_heat": 8,           # trade volume with heat >= 10
}

OCEANIC_THRESHOLDS = {
    "ei_access_charter": True,
    "ei_foothold": True,              # broker or warehouse in East Indies
    "ei_standing": 15,
    "ship_class_min": "brigantine",   # brigantine or galleon
    "contracts_completed": 5,
    "silver_min": 2000,
}

EMPIRE_THRESHOLDS = {
    "infra_regions": 3,               # infrastructure footprint breadth
    "trust_rank": 3,                  # reliable+
    "finance_used": True,             # both insurance and credit
    "contracts_completed": 10,
    "silver_min": 3000,
    "licenses_min": 3,
}

# ---------------------------------------------------------------------------
# Victory path completion summaries
# ---------------------------------------------------------------------------

COMPLETION_SUMMARIES: dict[str, str] = {
    "lawful_house": (
        "Your company earned trust across multiple regions, secured premium "
        "charters, and scaled lawful commerce without surrendering discipline "
        "to heat."
    ),
    "shadow_network": (
        "Your operation survived scrutiny, moved sensitive luxury cargo "
        "profitably, and built a resilient gray-market network under pressure."
    ),
    "oceanic_reach": (
        "Your house established East Indies access, commercialized long-haul "
        "routes, and proved that distant trade could be run at serious scale."
    ),
    "commercial_empire": (
        "You built an integrated trade concern with infrastructure, access, "
        "finance, and multi-region business power beyond a single ship or route."
    ),
}

# ---------------------------------------------------------------------------
# Candidate-strength boost/penalty factors
# ---------------------------------------------------------------------------
# Each factor adds or subtracts from raw completion ratio.
# Positive = behavioral coherence, negative = contradiction.

CANDIDATE_BOOSTS: dict[str, dict[str, float]] = {
    "lawful_house": {
        "trust_rank_bonus_per": 5.0,       # per trust rank above 2
        "standing_breadth_bonus": 8.0,     # 2+ regions with standing 10+
        "low_heat_bonus": 10.0,            # max heat <= 3
        "seizure_penalty": -15.0,          # per seizure
        "high_heat_penalty_per": -3.0,     # per point of max heat above 5
        "default_penalty": -20.0,          # any credit default
    },
    "shadow_network": {
        "discreet_bonus_per": 6.0,         # per discreet completion
        "heat_resilience_bonus": 10.0,     # profitable under heat
        "seizure_survival_bonus": 8.0,     # survived seizure, still operating
        "zero_heat_penalty": -20.0,        # never operated under pressure
        "collapse_penalty": -25.0,         # silver < 100
    },
    "oceanic_reach": {
        "ei_standing_bonus_per": 2.0,      # per point of EI standing
        "galleon_bonus": 15.0,             # operating galleon
        "ei_infra_bonus": 10.0,            # broker + warehouse in EI
        "local_only_penalty": -15.0,       # no EI standing at all
    },
    "commercial_empire": {
        "infra_breadth_bonus_per": 5.0,    # per infra region
        "finance_maturity_bonus": 10.0,    # credit + insurance both used
        "contract_breadth_bonus": 8.0,     # 10+ contracts
        "narrow_penalty": -10.0,           # only 1 region with infra
        "default_penalty": -15.0,          # credit defaults
    },
}
