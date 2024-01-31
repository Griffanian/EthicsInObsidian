import re
schema = {
    "sections": [
        {
            "keyword": "PART",
            "occurrences": [],
            "subsections": {
                "sections": [
                    {
                        "keyword": "PREFACE:",
                        "occurrences": [],
                    }, {
                        "keyword": "DEFINITIONS:",
                        "occurrences": [],
                        "subsections": {
                            "sections": [
                                {
                                    "regex": "^[IVXLCDM]+\\.",
                                    "name": "Def",
                                    "occurrences": [],
                                }, {
                                    "keyword": "Explanation--",
                                    "occurrences": [],
                                }
                            ]
                        },
                        "lastUpdated": None
                    }, {
                        "keyword": "AXIOMS:",
                        "occurrences": [],
                    }, {
                        "keyword": "PROPOSITIONS:",
                        "occurrences": [],
                    }
                ],
                "lastUpdated": None
            }
        }
    ],
    "lastUpdated": None
}


def getKeyVals(schema):
    keyVals = {
        "keywords": [],
        "regExps": [],
    }

    for item in schema["sections"]:

        if "keyword" in item.keys():
            print("keyword: " + item["keyword"])
            keyVals["keywords"].append(item["keyword"])

        elif "regex" in item.keys():
            print("regex: " + item["regex"])
            keyVals["regExps"].append(item["regex"])

        if "subsections" in item.keys():
            keyVals = merge_dicts(keyVals, getKeyVals(item["subsections"]))

    return keyVals


def updateSchema(schema, keyword, line_num):
    if keyword not in getKeywords(schema):
        raise KeyError

    for obj in schema:
        if keyword in [item["name"] for item in obj]:
            schema["occurrences"].append(line_num)
        elif keyword in getKeywords(obj):
            updateSchema(obj)
        else:
            continue

    print(schema)


def is_roman_line(line):
    # Define a regular expression pattern
    pattern = r'^[IVXLCDM]+\.'

    # Use re.match to check if the line matches the pattern
    match = re.match(pattern, line)

    return bool(match)


def merge_dicts(dict1, dict2):
    result_dict = {}

    for key in set(dict1) | set(dict2):
        result_dict[key] = dict1.get(key, []) + dict2.get(key, [])

    return result_dict


print(re.match(r'\s*\[\d\]\s*', ' [3]  '))
