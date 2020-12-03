from pytest import raises, approx
from process_covid import *


def equality_list(list_actual, list_expected):
    assert len(list_actual) == len(list_expected)
    assert all([type(a) == type(b) for a, b in zip(list_actual, list_expected)])
    assert all([a == approx(b, 0.001) if isinstance(a, float) else a == b for a, b in zip(list_actual, list_expected)])


def test_compute_running_average():
    with raises(ValueError) as exception:
        compute_running_average([1, 2, 3], 2)

    equality_list(compute_running_average([0, 1, 5, 2, 2, 5], 3), [None, 2.0, 2.6666, 3.0, 3.0, None])
    equality_list(compute_running_average([2, None, 4], 3), [None, 3.0, None])
    equality_list(compute_running_average([2, None, 4], 5), [None, None, None])


def test_simple_derivative():
    equality_list(simple_derivative([None, 1, 2, None, 4]), [None, None, 1, None, None])


def test_sum_sublists():
    with raises(ValueError) as exception:
        sum_sublists([1., 2., 3., 5.], [1, 2, 4])
    equality_list(sum_sublists([1., 2., 3., 5.], [1, 3]), [3., 8.])


def test_merge_binning():
    with raises(ValueError) as exception:
        merge_age_binning(['0-14', '15-29', '30-44', '45-'], ['0-19', '20-39', '40-'])
    with raises(ValueError) as exception:
        merge_age_binning(['0-'], ['0-30', '30-'])
    with raises(ValueError) as exception:
        merge_age_binning(['0-'], ['0-'])


    list_id1, list_id2 = merge_age_binning(['0-14', '15-29', '20-44', '45-'], ['0-14', '15-29', '20-44', '45-'])
    equality_list(list_id1, [0, 1, 2, 3])
    equality_list(list_id2, [0, 1, 2, 3])

    list_id1, list_id2 = merge_age_binning(['0-19', '20-39', '40-'], ['0-9', '10-39', '40-49', '50-'])
    equality_list(list_id1, [1, 2])
    equality_list(list_id2, [1, 3])

    list_id1, list_id2 = merge_age_binning(['0-9', '10-39', '40-49', '50-'], ['0-19', '20-39', '40-'])
    equality_list(list_id1, [1, 3])
    equality_list(list_id2, [1, 2])

    list_id1, list_id2 = merge_age_binning(['0-19', '20-39', '40-59', '60-'], ['0-29', '30-59', '60-'])
    equality_list(list_id1, [2, 3])
    equality_list(list_id2, [1, 2])

    list_id1, list_id2 = merge_age_binning(['0-9', '10-19', '20-29', '30-39', '40-49', '50-'], ['0-19', '20-39', '40-'])
    equality_list(list_id1, [1, 3, 5])
    equality_list(list_id2, [0, 1, 2])


def test_get_new_age_binning():
    binning = get_new_age_binning(['0-9', '10-19', '20-29', '30-39', '40-49', '50-'], [1, 3, 5])
    equality_list(binning, ["0-19", "20-39", "40-"])
    binning = get_new_age_binning(['0-9', '10-19', '20-29', '30-39', '40-49', '50-'], [0, 5])
    equality_list(binning, ["0-9", "10-"])
    binning = get_new_age_binning(['0-9', '10-19', '20-29', '30-39', '40-49', '50-'], [0, 1, 2, 3, 4, 5])
    equality_list(binning, ['0-9', '10-19', '20-29', '30-39', '40-49', '50-'])
    binning = get_new_age_binning(['0-19', '20-39', '40-'], [1, 2])
    equality_list(binning, ['0-39', '40-'])


def test_cases_per_population_by_age():
    input_data = {"metadata": {"age_binning": {"population": ['0-19', '20-39', '40-'],
                                               "hospitalizations": ['0-9', '10-39', '40-49', '50-']}},
                  "region": {"population": {"age": [100, 200, 800]}},
                  "evolution": {"01-01-2020":
                                    {"epidemiology": {"confirmed": {"total": {"age": [10, 50, 20, 60]}}}},
                                "01-02-2020":
                                    {"epidemiology": {"confirmed": {"total": {"age": [20, 100, 20, 60]}}}}}}
    result = cases_per_population_by_age(input_data)

    assert result == {'0-39': [("01-01-2020", 0.2), ("01-02-2020", 0.4)],
                      '40-': [("01-01-2020", 0.1), ("01-02-2020", 0.1)]}

    input_data = {"metadata": {"age_binning": {"population": ['0-19', '20-39', '40-'],
                                               "hospitalizations": ['0-9', '10-39', '40-49', '50-']}},
                  "region": {"population": {"age": [None, None, None]}},
                  "evolution": {"01-01-2020":
                                    {"epidemiology": {"confirmed": {"total": {"age": [10, 50, 20, 60]}}}},
                                "01-02-2020":
                                    {"epidemiology": {"confirmed": {"total": {"age": [20, 100, 20, 60]}}}}}}
    with raises(ValueError) as exception:
        cases_per_population_by_age(input_data)

    input_data = {"metadata": {"age_binning": {"population": ['0-19', '20-39', '40-'],
                                               "hospitalizations": ['0-9', '10-39', '40-49', '50-']}},
                  "region": {"population": {"age": [100, 200, 800]}},
                  "evolution": {"01-01-2020":
                                    {"epidemiology": {"confirmed": {"total": {"age": [None, None, None, None]}}}},
                                "01-02-2020":
                                    {"epidemiology": {"confirmed": {"total": {"age": [None, None, None, None]}}}}}}
    with raises(ValueError) as exception:
        cases_per_population_by_age(input_data)


def test_load_covid_data():
    input_data = {"metadata": {"age_binning": {"population": ['0-19', '20-39', '40-'],
                                               "hospitalizations": ['0-9', '10-39', '40-49', '50-']}},
                  "region": {"population": {"age": [100, 200, 800]}},
                  "evolution": {"01-01-2020":
                                    {"epidemiology": {"confirmed": {"total": {"age": [10, 50, 20, 60]}}}},
                                "01-02-2020":
                                    {"epidemiology": {"confirmed": {"total": {"age": [20, 100, 20, 60]}}}}}}

    with open('fake_data.json', 'w') as fake_datafile:
        json.dump(input_data, fake_datafile)

    with raises(ValueError) as exception:
        load_covid_data("fake_data.json")


def test_hospital_vs_confirmed():
    input_data = {"evolution": {"01-01-2020": {"hospitalizations": {"hospitalized": {"new": {"all": 2}}},
                                               "epidemiology": {"confirmed": {"new": {"all": 20}}}},
                                "01-02-2020": {"hospitalizations": {"hospitalized": {"new": {"all": 20}}},
                                               "epidemiology": {"confirmed": {"new": {"all": 100}}}}}}

    assert hospital_vs_confirmed(input_data) == (["01-01-2020", "01-02-2020"], [0.1, 0.2])

    input_data = {"evolution": {"01-01-2020": {"hospitalizations": {"hospitalized": {"new": {"all": 20}}},
                                               "epidemiology": {"confirmed": {"new": {"all": 200}}}},
                                "01-02-2020": {"hospitalizations": {"hospitalized": {"new": {"all": None}}},
                                               "epidemiology": {"confirmed": {"new": {"all": 20}}}}}}

    assert hospital_vs_confirmed(input_data) == (["01-01-2020"], [0.1])

    input_data = {"evolution": {"01-01-2020": {"hospitalizations": {"hospitalized": {"new": {"all": 20}}},
                                               "epidemiology": {"confirmed": {"new": {"all": None}}}},
                                "01-02-2020": {"hospitalizations": {"hospitalized": {"new": {"all": 20}}},
                                               "epidemiology": {"confirmed": {"new": {"all": 100}}}}}}
    assert hospital_vs_confirmed(input_data) == (["01-02-2020"], [0.2])


def test_generate_data_plot_confirmed():
    input_data = {"evolution": {"01-01-2020": {"hospitalizations": {"hospitalized": {"new": {"all": 2}}},
                                               "epidemiology": {"confirmed": {"new": {"all": 20}}}},
                                "01-02-2020": {"hospitalizations": {"hospitalized": {"new": {"all": 20}}},
                                               "epidemiology": {"confirmed": {"new": {"all": 100}}}}}}

    with raises(ValueError) as exception:
        generate_data_plot_confirmed(input_data, sex=4, max_age=None, status="new")

    with raises(ValueError) as exception:
        generate_data_plot_confirmed(input_data, sex="male", max_age=None, status=5)

    with raises(ValueError) as exception:
        generate_data_plot_confirmed(input_data, sex="male", max_age=12, status="new")

    with raises(ValueError) as exception:
        generate_data_plot_confirmed(input_data, sex=None, max_age="infinity", status="new")
