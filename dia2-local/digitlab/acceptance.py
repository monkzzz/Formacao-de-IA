"""Current professor criterion, separate from historical >=90% measurements."""

from .confidence_suite_browser import compare_predictions


POLICY = {
    "name": "professor-official-captcha-strict-v1",
    "source": "Participant's explicit report of professor requirements in the conversation",
    "required_cases": 10,
    "required_correct": 10,
    "minimum_score_exclusive": .9,
    "score_comparison": ">",
    "score_basis": "Unrounded original model score for the correct class; no display rescaling",
    "supplementary_training": "Acceptable as a separate, correctly documented extension",
    "mnist_only_model": "Preserve the required course model and its evidence separately",
    "official_inputs_for_training_or_selection": False,
}


def evaluate(records, expected):
    if len(records) != POLICY["required_cases"] or len(expected) != POLICY["required_cases"]:
        raise ValueError("The acceptance criterion requires exactly ten distinct cases")
    comparison = compare_predictions(records, expected)
    cases = [{"file": row["file"], "correct": row["correct"],
              "correct_class_score": row["expected_class_score"],
              "passes": bool(row["correct"] and row["expected_class_score"] > POLICY["minimum_score_exclusive"])}
             for row in comparison["cases"]]
    return {"policy": POLICY, "count": len(cases), "correct": comparison["correct"],
            "correct_above_90": sum(row["passes"] for row in cases),
            "accepted": all(row["passes"] for row in cases), "cases": cases}
