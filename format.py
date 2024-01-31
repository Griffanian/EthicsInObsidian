from itertools import chain
import os
import json
import time
import re


def mergeDicts(dict1: dict, dict2: dict) -> dict:
    result_dict = {}

    for key in set(dict1) | set(dict2):
        result_dict[key] = dict1.get(key, []) + dict2.get(key, [])

    return result_dict


def getKeyVals(schema: dict[str, list]) -> dict[str, list]:
    keyVals = {
        "keywords": [],
        "regExps": [],
    }

    for item in schema["sections"]:

        if "keyword" in item.keys():
            keyVals["keywords"].append(item["keyword"])

        elif "regex" in item.keys():
            keyVals["regExps"].append(item["regex"])

        if "subsections" in item.keys():
            keyVals = mergeDicts(keyVals, getKeyVals(item["subsections"]))

    return keyVals


def getKeyFromVals(my_dict: dict, search_value) -> str:
    for key, value in my_dict.items():
        if value == search_value:
            return key
    return None


def updateSubsections(obj: dict, val: str, valType: str, line_num: int, lastUpdatedParent=None):
    if "subsections" in obj.keys():
        subsectionVals = list(chain.from_iterable(
            list(getKeyVals(obj["subsections"]).values())))
        print(f"parent of updating {lastUpdatedParent}")
        if val in subsectionVals:
            updateObject(obj["subsections"], val, valType,
                         line_num, lastUpdatedParent=lastUpdatedParent)


def getNameFromLastUpdated(obj: dict, lastUpdated: str) -> str:
    for item in obj["sections"]:
        if lastUpdated in item.values():
            return (item["name"] if "name" in item.keys() else lastUpdated)


def updateObject(obj: dict, val: str, valType: str, line_num: int, lastUpdatedParent=None):

    type_mapping = {"keywords": "keyword", "regExps": "regex"}

    valTypeSelector = type_mapping.get(valType)

    if valTypeSelector is None:
        raise ValueError("value type must be keywords or regExps")

    objVals = list(chain.from_iterable(list(getKeyVals(obj).values())))

    if val not in objVals:
        raise KeyError(f"the val {val} is not in obj's keys")

    for item in obj["sections"]:
        if valTypeSelector in item.keys():
            if val == item[valTypeSelector]:
                if "lastUpdated" in obj.keys():
                    for thing in obj["sections"]:
                        key = getKeyFromVals(thing, obj["lastUpdated"])
                        if key and key in thing and thing[key] == obj["lastUpdated"]:
                            thing["occurrences"][-1]["end"] = line_num-1

                if "occurrences" not in item.keys():
                    item["occurrences"] = []

                item["occurrences"].append({
                    "name": f"{getNameFromLastUpdated(obj, val)} {len(item["occurrences"])+1}",
                    "start": line_num,
                    "end": None
                })

                # obj["currentlyIn"] = f"{name} {len(item["occurrences"])}"

                print(f"currently updating {getNameFromLastUpdated(obj, val)} {
                      len(item["occurrences"])}")

                time.sleep(1)

                obj["lastUpdated"] = val

            else:

                if "lastUpdated" in obj.keys():
                    parentOccurences = 0
                    for thing in obj["sections"]:
                        key = getKeyFromVals(thing, obj["lastUpdated"])
                        if key and key in thing and thing[key] == obj["lastUpdated"]:
                            parentOccurences = len(thing["occurrences"])

                    newUpdatedParent = f"{
                        getNameFromLastUpdated(obj, obj['lastUpdated'])} {parentOccurences}"

                    updateSubsections(item, val, valType, line_num,
                                      lastUpdatedParent=newUpdatedParent)
                else:
                    updateSubsections(item, val, valType, line_num,
                                      lastUpdatedParent=lastUpdatedParent)

        else:
            if "lastUpdated" not in obj:
                updateSubsections(item, val, valType, line_num,
                                  lastUpdatedParent=lastUpdatedParent)
                return

            parent_occurrences = 0

            for thing in obj.get("sections", []):
                key = getKeyFromVals(thing, obj["lastUpdated"])

                if key and key in thing and thing[key] == obj["lastUpdated"]:
                    parent_occurrences = len(thing.get("occurrences", []))

            newUpdatedParent = (
                f"{lastUpdatedParent} {getNameFromLastUpdated(obj, obj['lastUpdated'])} {
                    parent_occurrences}"
                if lastUpdatedParent
                else f"{getNameFromLastUpdated(obj, obj['lastUpdated'])} {parent_occurrences}"
            )
            updateSubsections(item, val, valType, line_num,
                              lastUpdatedParent=newUpdatedParent)


def finishObject(obj: dict, totalLength: int):
    if "lastUpdated" in obj.keys():
        for item in obj["sections"]:
            if obj["lastUpdated"] in item.values():
                key = getKeyFromVals(item, obj["lastUpdated"])
                if item[key] == obj["lastUpdated"]:
                    item["occurrences"][-1]["end"] = totalLength
            if "subsections" in item.keys():
                finishObject(item["subsections"], totalLength)


def processLine(line: str, schema: dict, keyVals: dict[str, list], line_num: int):
    words = line.split()
    keywords_present = set(keyVals["keywords"]) & set(words)

    if keywords_present:
        val = list(keywords_present)[0]
        val_type = "keywords"
        updateObject(schema, val, val_type, line_num)
    else:
        for regex in keyVals["regExps"]:
            if re.search(regex, line):
                val = regex
                val_type = "regExps"
                updateObject(schema, val, val_type, line_num)


def processFile(txtPath: str, schemaPath: str, newSchemaPath: str):

    with open(schemaPath, 'r') as file:
        schema = json.load(file)

    with open(txtPath, 'r', encoding='utf-8-sig') as file:

        keyVals = getKeyVals(schema)
        totalLineNum = 0
        for line_num, line in enumerate(file):
            processLine(line, schema, keyVals, line_num)

        finishObject(schema, totalLineNum)

        with open(newSchemaPath, 'w') as file:
            json.dump(schema, file, indent=4)


schemaPath = '/Users/milesbloom/Ethics_Project/schema1.json'
txtPath = '/Users/milesbloom/Ethics_Project/Ethics.txt'
newSchemaPath = '/Users/milesbloom/Ethics_Project/schema2.json'

processFile(txtPath, schemaPath, newSchemaPath)


# print(json.dumps(schema, indent=2))

# print(schema)
# if not latestSection:
#     labelValsDict[curKeyword].append({
#         "name": f"{curKeyword} 1",
#         "start": line_num,
#         "end": None
#     })
# else:
#     labelValsDict[latestSection]["end"] = line_num -1

# if not labelValsDict[curKeyword]:
#     labelValsDict[curKeyword].append({
#         "name": f"{curKeyword} 1",
#         "start": line_num,
#         "end": None
#     })
# else:

#     if "PART" in words:
#         if len(chapter_nums) == 0:
#             chapter_nums.append({
#                 "name": "Part 1",
#                 "start": line_num,
#                 "end": None
#             })

#         elif len(chapter_nums) > 0:
#             chapter_nums[-1]["end"] = line_num
#             chapter_nums.append({
#                 "name": f"Part {len(chapter_nums)+1}",
#                 "start": line_num,
#                 "end": None
#             })

#     if "PREFACE:" in words:
#         preface_nums.append({
#             "name": f"Part {len(chapter_nums)+1}",
#             "start": line_num,
#             "end": None
#         })

#     elif "DEFINITIONS:" in words:
#         defintion_nums.append(line_num)

#     elif "AXIOMS:" in words:
#         axiom_nums.append(line_num)

#     elif "PROPOSITIONS:" in words:
#         proposition_nums.append(line_num)
#         appendix_nums.append(line_num)

# if chapter_nums[-1]["end"] == None:
#     chapter_nums[-1]["end"] = line_num+1

# print(chapter_nums)

# print(chapter_nums)
# with open(file_path, 'r') as file:
# print(chapter_nums)
# for line_num, line in enumerate(file):
# print(line_num)
# if line_num > chapter_nums[0] and line_num < chapter_nums[1]:
#     print(line_num)

# if line_num-2 in chapter_nums:
#     part_name = f'{
#         file_path}/Part {int_to_roman(chapter_nums.index(line_num-2)+1)}'

#     os.makedirs(part_name, exist_ok=True)
#     chapter_file_name = f'{part_name}/{new_line}.md'

#     with open(chapter_file_name, 'w') as new_file:
#         new_file.write(f'# {new_line}')

#     os.remove(chapter_file_name)
#     os.removedirs(part_name)

# if line_num-2 in appendix_nums:
#     print([new_line])
