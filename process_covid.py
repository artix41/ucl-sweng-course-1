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
    if sex is not None:
        if sex not in ["male", "female"]:
            raise ValueError("The argument 'sex' should be either 'male' or 'female'")

        for date in list_dates:
            n_confirmed_cases = input_data["evolution"][date]["epidemiology"]["confirmed"][status][sex]
            list_confirmed_cases.append(n_confirmed_cases)

    return list_dates, list_confirmed_cases


def create_confirmed_plot(input_data, sex=False, max_ages=[], status="total", save=...):
    color = {"male": "#00C4AA",
             "female": "#8700F9"}

    if sex and len(max_ages) > 0:
        raise ValueError("'sex' and 'max_ages' cannot be specified at the same time")
    if not sex and len(max_ages) == 0:
        raise ValueError("Either sex or max_ages should be specified")

    fig = plt.figure(figsize=(10, 10))

    if sex:
        for sex_type in ['male', 'female']:
            list_dates, list_confirmed_cases = generate_data_plot_confirmed(input_data, sex_type, None, status)
            plt.plot(list_dates, list_confirmed_cases, label=f"{status} {sex_type}", color=color[sex_type])
    # else:
        # for age in max_ages:
            # FIXME need to change `changeme` so it uses generate_data_plot_confirmed
            # plt.plot('date', 'value', changeme)

    fig.autofmt_xdate()  # To show dates nicely
    # TODO add title with "Confirmed cases in ..."
    # TODO Add x label to inform they are dates
    # TODO Add y label to inform they are number of cases
    # TODO Add legend
    # TODO Change logic to show or save it into a '{region_name}_evolution_cases_{type}.png'
    #      where type may be sex or age
    plt.xlabel("Date")
    plt.ylabel("# Cases")
    plt.legend()
    plt.show()


def compute_running_average(data, window):
    raise NotImplementedError


def simple_derivative(data):
    raise NotImplementedError


def count_high_rain_low_tests_days(input_data):
    raise NotImplementedError
