from pytest import raises, approx
from process_covid import compute_running_average


def equality_list(list_actual, list_expected):
    assert len(list_actual) == len(list_expected)
    assert all([type(a) == type(b) for a, b in zip(list_actual, list_expected)])
    assert all([a == approx(b, 0.001) if isinstance(a, float) else True for a, b in zip(list_actual, list_expected)])


def test_compute_running_average():
    with raises(ValueError) as exception:
        compute_running_average([1, 2, 3], 2)

    equality_list(compute_running_average([0, 1, 5, 2, 2, 5], 3), [None, 2.0, 2.6666, 3.0, 3.0, None])
    equality_list(compute_running_average([2, None, 4], 3), [None, 3.0, None])