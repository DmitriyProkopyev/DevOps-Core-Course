from typing import Dict, Iterable, Any


class JSONAuditor:
    def __init__(self, template: Dict[str, Any]):
        self._template = template

    def as_pairs(self, actual: Dict[str, Any]):
        for (expected_value, actual_value) in self._traverse_dict(self._template, actual):
            yield expected_value, actual_value

    def _traverse_dict(self, expected: Dict[str, Any], actual: Dict[str, Any]) -> Iterable[Any]:
        actual_keys = actual.keys()
        for key in expected.keys():
            if key not in actual_keys:
                raise KeyError(f"The actual structure does not contain the necessary key {key}!")
        
            expected_value = expected[key]
            actual_value = actual[key]
            for element in self._traverse(expected_value, actual_value):
                yield element

    def _traverse(self, expected: Any, actual: Any) -> Iterable[Any]:
        if isinstance(expected, dict):
            if not isinstance(actual, dict):
                raise KeyError(f"The expected ({expected}) and actual ({actual}) structures diverge!")
            
            for element in self._traverse_dict(expected, actual):
                yield element

        elif isinstance(expected, list):
            if not isinstance(actual, list) or not len(expected) == len(actual):
                raise KeyError(f"The expected ({expected}) and actual ({actual}) structures diverge!")
            
            for i in range(0, len(expected)):
                for element in self._traverse(expected[i], actual[i]):
                    yield element
        
        elif isinstance(expected, str):
            yield (expected, actual)

        else:
            raise TypeError(f"Expected structure type {type(expected)} is not supported!")
