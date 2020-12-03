import json


def recursive_check(dict_schema, dict_data):
    if not isinstance(dict_schema, dict):
        return True
    if not isinstance(dict_data, dict):
        return False

    if list(dict_schema.keys())[0] == "<date>":
        for key in dict_data.keys():
            if not recursive_check(dict_schema["<date>"], dict_data[key]):
                return False
        return True
    if "<various_parameters>" in dict_schema.keys():
        return 'stringency_index' in dict_data.keys()

    if dict_schema.keys() != dict_data.keys():
        return False

    for key in dict_schema.keys():
        if not recursive_check(dict_schema[key], dict_data[key]):
            return False
    return True


def validate_schema(schema_filepath, json_filepath):
    with open(schema_filepath) as schema_file:
        schema = json.load(schema_file)
    with open(json_filepath) as json_file:
        json_data = json.load(json_file)

    return recursive_check(schema, json_data)


if __name__ == "__main__":
    print(validate_schema("covid_data/schema.json", "covid_data/ER-Mi-EV_2020-03-16_2020-04-24.json"))
