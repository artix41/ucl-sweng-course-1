import json
import matplotlib.pyplot as plt


def merge_age_binning(age_binning1, age_binning2):
    min_ages = ([int(age_range.split("-")[0]) for age_range in age_binning1],
                [int(age_range.split("-")[0]) for age_range in age_binning2])

    idx = [0, 0]
    cur_idx = 0
    list_id1, list_id2 = [], []

    idx[cur_idx] += 1
    while idx[0] < len(min_ages[0]) and idx[1] < len(min_ages[1]):
        if min_ages[0][idx[0]] == min_ages[1][idx[1]]:
            list_id1.append(idx[0] - 1)
            list_id2.append(idx[1] - 1)
        elif min_ages[cur_idx][idx[cur_idx]] > min_ages[1-cur_idx][idx[1-cur_idx]]:
            cur_idx = 1 - cur_idx
        idx[cur_idx] += 1

    if len(list_id1) == 0:
        raise ValueError(f"The age binning {age_binning1} and {age_binning2} could not be merged")
    else:
        list_id1.append(len(age_binning1) - 1)
        list_id2.append(len(age_binning2) - 1)

    return list_id1, list_id2


def sum_sublists(l, indices):
    if max(indices) >= len(l):
        raise ValueError("'indices' contains elements greater than the size of 'l'")
    result = []
    subsum = 0
    for i in range(len(l)):
        subsum += l[i]
        if i in indices:
            result.append(subsum)
            subsum = 0
    return result


def get_new_age_binning(init_age_binning, indices):
    if max(indices) >= len(init_age_binning):
        raise ValueError("'indices' contains elements greater than the size of 'l'")

    cur_min = 0
    result = []
    change_cur_min = False
    for i, bin in enumerate(init_age_binning):
        if change_cur_min:
            cur_min = bin.split("-")[0]
            change_cur_min = False
        if i in indices:
            max_bin = "" if len(bin.split("-")) == 0 else bin.split("-")[1]
            result.append(f"{cur_min}-{max_bin}")
            change_cur_min = True
    return result


def load_covid_data(filepath):
    with open(filepath) as json_file:
        data = json.load(json_file)
    return data


def cases_per_population_by_age(input_data):
    total_population = input_data["region"]["population"]["age"]
    if None in total_population:
        raise ValueError("Missing data in 'region'->'population'->'age'")
    age_binning_population = input_data["metadata"]["age_binning"]["population"]
    age_binning_cases = input_data["metadata"]["age_binning"]["hospitalizations"]

    list_id1, list_id2 = merge_age_binning(age_binning_population, age_binning_cases)
    print(age_binning_population, age_binning_cases)
    new_total_population = sum_sublists(total_population, list_id1)
    new_age_binning = get_new_age_binning(age_binning_population, list_id1)

    result = {new_age_binning[i]: [] for i in range(len(new_age_binning))}
    for date in input_data["evolution"].keys():
        total_cases = input_data["evolution"][date]["epidemiology"]["confirmed"]["total"]["age"]
        if None in total_cases:
            raise ValueError(f"Missing data in 'evolution'->{date}->'epidemiology'->'confirmed'->'total'->'age'")

        new_total_cases = sum_sublists(total_cases, list_id2)

        for idx_age in range(len(new_total_cases)):
            percentage = new_total_cases[idx_age] / new_total_population[idx_age]
            result[new_age_binning[idx_age]].append((date, percentage))
    return result


def hospital_vs_confirmed(input_data):
    list_date = list(input_data["evolution"].keys())
    list_percentage_hosp = []
    for date in list_date:
        n_hospitalized = input_data["evolution"][date]["hospitalizations"]["hospitalized"]["new"]["all"]
        n_cases = input_data["evolution"][date]["epidemiology"]["confirmed"]["new"]["all"]
        list_percentage_hosp.append(n_hospitalized / n_cases)

    return list_date, list_percentage_hosp


def generate_data_plot_confirmed(input_data, sex, max_age, status):
    """
    At most one of sex or max_age allowed at a time.
    sex: only 'male' or 'female'
    max_age: sums all bins below this value, including the one it is in.
    status: 'new' or 'total' (default: 'total')
    """

    # if sex is not None and max_age is not None:
    #     raise ValueError("'sex' and 'max_age' cannot be specified at the same time")
    # if not sex and not max_age:
    #     raise ValueError("Either sex or max_ages should be specified")

    list_dates = list(input_data["evolution"].keys())
    list_confirmed_cases = []
    if sex is not None and sex is not False:
        if sex not in ["male", "female"]:
            raise ValueError("The argument 'sex' should be either 'male' or 'female'")

        for date in list_dates:
            n_conf_cases = input_data["evolution"][date]["epidemiology"]["confirmed"][status][sex]
            list_confirmed_cases.append(n_conf_cases)

        return list_dates, list_confirmed_cases
    else:
        age_binning = input_data["metadata"]["age_binning"]["population"]
        min_ages_available = [int(age_range.split("-")[0]) for age_range in age_binning]

        selected_age_idx = 0
        for idx_age, age in enumerate(min_ages_available):
            if max_age >= age:
                selected_age_idx = idx_age
        if selected_age_idx == len(age_binning) - 1:
            actual_max_age = "infinity"
        else:
            actual_max_age = age_binning[selected_age_idx].split("-")[1]

        for date in list_dates:
            n_conf_cases = sum(
                [input_data["evolution"][date]["epidemiology"]["confirmed"][status]["age"][idx_age]
                 for idx_age in range(selected_age_idx+1)]
            )
            list_confirmed_cases.append(n_conf_cases)

        return list_dates, list_confirmed_cases, actual_max_age


def create_confirmed_plot(input_data, sex=False, max_ages=[], status="total", save=False):
    color = {"male": "#00C4AA",
             "female": "#8700F9"}
    linestyle = {"total": "-",
                 "new": "--"}

    if sex and len(max_ages) > 0:
        raise ValueError("'sex' and 'max_ages' cannot be specified at the same time")
    if not sex and len(max_ages) == 0:
        raise ValueError("Either sex or max_ages should be specified")

    fig = plt.figure(figsize=(10, 10))

    if sex:
        type_plot = "sex"
        for sex_type in ['male', 'female']:
            list_dates, list_confirmed_cases = generate_data_plot_confirmed(input_data, sex_type, None, status)
            plt.plot(list_dates, list_confirmed_cases,
                     linestyle=linestyle[status], label=f"{status} {sex_type}", color=color[sex_type])
    else:
        type_plot = "age"
        for age in max_ages:
            list_dates, list_confirmed_cases, actual_age = generate_data_plot_confirmed(input_data, None, age, status)
            plt.plot(list_dates, list_confirmed_cases,
                     linestyle=linestyle[status], label=f"{status} younger than {actual_age}")

    fig.autofmt_xdate()  # To show dates nicely
    region_name = input_data["region"]["name"]
    plt.title(f"Confirmed cases in {region_name}")

    plt.xlabel("Date")
    plt.ylabel("# Cases")
    plt.legend()

    if save:
        plt.savefig(f"{region_name}_evolution_cases_{type_plot}.png")
    else:
        plt.show()


def compute_running_average(data, window):
    if window % 2 == 0:
        raise ValueError("'window' should be an odd integer")
    result = []
    shift = int((window - 1) / 2)
    for i in range(len(data)):
        if i < shift or i >= len(data) - shift:
            result.append(None)
        else:
            sum_window, n_values = 0, 0
            for j in range(i-shift, i+shift+1):
                if data[j] is not None:
                    sum_window += data[j]
                    n_values += 1
            avg = None if n_values == 0 else sum_window / n_values
            result.append(avg)

    return result


def simple_derivative(data):
    result = [None]
    for i in range(1, len(data)):
        if data[i] is None or data[i-1] is None:
            result.append(None)
        else:
            result.append(data[i] - data[i-1])
    return result


def count_high_rain_low_tests_days(input_data):
    list_dates = input_data["evolution"].keys()
    rain_data = [input_data["evolution"][date]["weather"]["rainfall"] for date in list_dates]
    test_data = [input_data["evolution"][date]["epidemiology"]["tested"]["new"]["all"] for date in list_dates]
    smooth_rain_data = compute_running_average(rain_data, 7)
    smooth_test_data = compute_running_average(test_data, 7)
    deriv_rain_data = simple_derivative(smooth_rain_data)
    deriv_test_data = simple_derivative(smooth_test_data)
    print(deriv_test_data)
    print(deriv_rain_data)
    total_days_rain_increased = sum([int(a is not None and a > 0) for a in deriv_rain_data])
    n = len(list_dates)
    total_days_rain_increased_test_decreased = sum([int(deriv_rain_data[i] is not None and deriv_rain_data[i] > 0
                                                        and deriv_test_data[i] is not None and deriv_test_data[i] < 0)
                                                    for i in range(n)])

    return total_days_rain_increased_test_decreased / total_days_rain_increased
