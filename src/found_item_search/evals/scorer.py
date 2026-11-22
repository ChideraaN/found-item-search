from found_item_search.evals.cases import CASES
from found_item_search.bag_description_extractor import check_stop_reason_and_parse_result
from found_item_search.models import clean, ExtractionResult
import math

def text_match(actual: str | None, expected: str | None) -> bool:
    if actual is None or expected is None:
        return actual == expected

    value_a = clean(actual).lower()
    value_b = clean(expected).lower()

    return value_a == value_b


def weight_match(actual: float | None, expected: float | None) -> bool:
    if actual is None or expected is None:
        return actual == expected

    return math.isclose(actual, expected, abs_tol=0.01)


def compare(expected, comparison_item):
    for key, expected_value in expected.items():
        actual_value = comparison_item.get(key)

        if key != "weight_kg":
            print(text_match(actual_value, expected_value))
        else:
            print(weight_match(actual_value, expected_value))


results: list = []


for case in CASES[:3]:
    results.append({"test": case, "result" : check_stop_reason_and_parse_result(case['text'])})

for res in results:
    actual = res.get("result")
    expected = res.get("test").get("expected")
    expected_failure = res.get("test").get("expected_failure")

    if expected_failure is None:
        if actual.bag is not None:
            comparison_item = actual.bag.model_dump()
            print(compare(expected, comparison_item))
        else:
            print(False)
    else:
        print(actual.failure_reason == expected_failure)
