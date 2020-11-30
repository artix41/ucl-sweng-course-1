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
    raise NotImplementedError


def create_confirmed_plot(input_data, sex=False, max_ages=[], status=..., save=...):
    # FIXME check that only sex or age is specified.
    fig = plt.figure(figsize=(10, 10))
    # FIXME change logic so this runs only when the sex plot is required
    for sex in ['male', 'female']:
        # FIXME need to change `changeme` so it uses generate_data_plot_confirmed
        plt.plot('date', 'value', changeme)
    # FIXME change logic so this runs only when the age plot is required
    for age in max_ages:
        # FIXME need to change `changeme` so it uses generate_data_plot_confirmed
        plt.plot('date', 'value', changeme)
    fig.autofmt_xdate()  # To show dates nicely
    # TODO add title with "Confirmed cases in ..."
    # TODO Add x label to inform they are dates
    # TODO Add y label to inform they are number of cases
    # TODO Add legend
    # TODO Change logic to show or save it into a '{region_name}_evolution_cases_{type}.png'
    #      where type may be sex or age
    plt.show()


def compute_running_average(data, window):
    raise NotImplementedError


def simple_derivative(data):
    raise NotImplementedError


def count_high_rain_low_tests_days(input_data):
    raise NotImplementedError
