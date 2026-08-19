# ============================================================
# NIFTY 100 SCREENER
# SPRINT 3 - DAY 16
# SIX PRESET SCREENERS
# ============================================================

from pathlib import Path
import sys

# Make sure project root is available
PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.screener.engine import apply_preset


# ============================================================
# PRESET NAMES
# ============================================================

PRESETS = {
    "quality_compounder": "Quality Compounder",
    "value_pick": "Value Pick",
    "growth_accelerator": "Growth Accelerator",
    "dividend_champion": "Dividend Champion",
    "debt_free_blue_chip": "Debt-Free Blue Chip",
    "turnaround_watch": "Turnaround Watch",
}


# ============================================================
# RUN ONE PRESET
# ============================================================

def run_preset(preset_key):

    if preset_key not in PRESETS:

        raise ValueError(
            f"Unknown preset: {preset_key}"
        )

    print()
    print("-" * 60)
    print(
        f"Running: {PRESETS[preset_key]}"
    )
    print("-" * 60)

    result = apply_preset(
        preset_key
    )

    print(
        f"Companies returned: {len(result)}"
    )

    return result


# ============================================================
# RUN ALL SIX PRESETS
# ============================================================

def run_all_presets():

    results = {}

    for preset_key in PRESETS:

        results[preset_key] = run_preset(
            preset_key
        )

    return results


# ============================================================
# CHECK PRESET RESULT COUNT
# ============================================================

def check_result_count(
    preset_key,
    result
):

    count = len(result)

    preset_name = PRESETS[
        preset_key
    ]

    # With the complete 92-company dataset,
    # the expected range is 5-50.
    #
    # Your current database is incomplete, so
    # this is only a warning at this stage.

    if 5 <= count <= 50:

        print(
            f"PASS: {preset_name} "
            f"returned {count} companies."
        )

        return True


    print(
        f"WARNING: {preset_name} "
        f"returned {count} companies."
    )

    print(
        "Expected range with the complete "
        "92-company dataset: 5-50."
    )

    return False


# ============================================================
# DISPLAY RESULT
# ============================================================

def display_result(
    preset_key,
    result
):

    preset_name = PRESETS[
        preset_key
    ]

    print()
    print(
        f"TOP RESULTS - {preset_name}"
    )

    if result.empty:

        print(
            "No companies matched "
            "this preset."
        )

        return


    display_columns = [
        "company_id",
        "year",
        "company_name",
        "return_on_equity_pct",
        "debt_to_equity",
        "free_cash_flow_cr",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "composite_quality_score",
    ]


    available_columns = [
        column
        for column in display_columns
        if column in result.columns
    ]


    print(
        result[
            available_columns
        ]
        .head(5)
        .to_string(
            index=False
        )
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print(
        "NIFTY 100 - DAY 16"
    )
    print(
        "SIX PRESET SCREENERS"
    )
    print("=" * 70)


    print()
    print(
        "Presets being tested:"
    )


    for key, name in PRESETS.items():

        print(
            f"  {key} -> {name}"
        )


    # --------------------------------------------------------
    # Run all
    # --------------------------------------------------------

    results = run_all_presets()


    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print(
        "PRESET SUMMARY"
    )
    print("=" * 70)


    passed = 0
    warnings = 0


    for preset_key, result in results.items():

        name = PRESETS[
            preset_key
        ]

        count = len(result)

        print(
            f"{name:<30} : {count} companies"
        )


        if 5 <= count <= 50:

            passed += 1

        else:

            warnings += 1


    # --------------------------------------------------------
    # Display top 5 from each preset
    # --------------------------------------------------------

    for preset_key, result in results.items():

        display_result(
            preset_key,
            result
        )


    # --------------------------------------------------------
    # Final status
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print(
        "DAY 16 SUMMARY"
    )
    print("=" * 70)

    print(
        f"Presets tested: {len(results)}"
    )

    print(
        f"Currently in expected range: {passed}"
    )

    print(
        f"Currently outside range: {warnings}"
    )

    print()

    print(
        "IMPORTANT:"
    )

    print(
        "The database currently contains only "
        "a small subset of the intended 92 companies."
    )

    print(
        "Therefore, result-count warnings are "
        "expected until the complete dataset is loaded."
    )

    print()

    print(
        "DAY 16 PRESET TEST COMPLETED."
    )