import json
import matplotlib.pyplot as plt


def load_covid_data(filepath):
    with open(filepath) as json_file:
        data = json.load(json_file)
    return data


def cases_per_population_by_age(input_data):
    total_population = input_data["region"]["population"]["age"]
    age_binning = input_data["metadata"]["age_binning"]["population"]
    result = {age_binning[i]: [] for i in range(len(age_binning))}
    for date in input_data["evolution"].keys():
        for idx_age in range(4):
            cases = input_data["evolution"][date]["epidemiology"]["confirmed"]["total"]["age"][idx_age]
            percentage = cases / total_population[idx_age]
            result[age_binning[idx_age]].append((date, percentage))
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
