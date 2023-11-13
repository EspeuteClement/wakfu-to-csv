import urllib.request
import json
import os
import sys

db_path = "db/"

def get_version():
    VERSION_URL = "https://wakfu.cdn.ankama.com/gamedata/config.json"
    version_json = json.loads(urllib.request.urlopen(VERSION_URL).read())
    print(version_json)
    return version_json["version"]

def get_json(version):
    os.makedirs(db_path + version, exist_ok=True)
    fetch_page(version, "items")
    fetch_page(version, "equipmentItemTypes")
    fetch_page(version, "actions")
    fetch_page(version, "itemProperties")


def fetch_page(version, page):
    path = db_path + version + "/" + page + ".json"
    if not os.path.exists(path):
        REQUEST_URL = "https://wakfu.cdn.ankama.com/gamedata/{version}/{type}.json"
        PAGE_URL = REQUEST_URL.format(version=version, type=page)
        print("fetching %s" % PAGE_URL)
        data = urllib.request.urlopen(PAGE_URL).read()
        with open(path, "wb") as f:
            f.write(data)

def load_data(version):
    data = {}
    data["items"] = load_data_page(version, "items")
    data["equipmentItemTypes"] = load_data_page(version, "equipmentItemTypes")
    data["actions"] = load_data_page(version, "actions")
    data["itemProperties"] = load_data_page(version, "itemProperties")
    return data

def load_data_page(version, page):
    with open(db_path + version + "/" + page + ".json", "rb") as f:
        return json.load(f)


params = {
    20: {'name': "PV", 'formula': [0]},
    21: {'name': "PV", 'formula': [-1]},

    31: {'name': "PA", 'formula': [0]},
    41: {'name': "PM", 'formula': [0]},
    160: {'name': "PO", 'formula': [0]},
    191: {'name': "PW", 'formula': [0]},
    192: {'name': "PW", 'formula': [-1]},
    194: {'name': "PW", 'formula': [-1]},


    56: {'name': "PA", 'formula': [-1]},
    
    57: {'name': "PM", 'formula': [-1]},


    173: {'name': "Tacle", 'formula': [0]},
    174: {'name': "Tacle", 'formula': [-1]},

    176: {'name': "Esquive", 'formula': [0]},
    177: {'name': "Esquive", 'formula': [-1]},


    26: {'name': "Maitrise soin", 'formula': [0]},
    149: {'name': "Maitrise CC", 'formula': [0]},

    150: {'name': "CC", 'formula': [0]},
    168: {'name': "CC", 'formula': [-1]},

    180: {'name': "Maitrise Dos", 'formula': [0]},
    181: {'name': "Maitrise Dos", 'formula': [-1]},

    875: {'name': "Parade", 'formula': [0]},
    876: {'name': "Parade", 'formula': [-1]},



    1052: {'name': "Maitrise Mélee", 'formula': [0]},
    1053: {'name': "Maitrise Distance", 'formula': [0]},
    1055: {'name': "Maitrise Berserk", 'formula': [0]},

    -1: {'name': "Maitrise Elem"},
    -2: {'name': "NB Elements"},
}

def parse_data(data):
    with open("out.csv", "wb") as file:
        line = ""
        line += "Nom;"
        line += "Level;"
        line += "Raretée;"
        line += "Type;"

        param_names = set()
        for p in params:
            param_names.add(params[p]["name"])

        for p in param_names:
            line += p + ";"

        line += "\n"
        
        file.write(line.encode('utf8'))

        itemTypes = {}
        for t in data["equipmentItemTypes"]:
            itemTypes[t["definition"]["id"]] = t["title"]["fr"]

        for value in data["items"]:
            if "item" in value["definition"]:
                line = ""
                line += value["title"]["fr"] + ";"
                level = value["definition"]["item"]["level"]
                line += str(level) + ";"
                
                line += str(value["definition"]["item"]["baseParameters"]["rarity"]) + ";"

                if value["definition"]["item"]["baseParameters"]["itemTypeId"] > 647:
                    continue

                line += itemTypes[value["definition"]["item"]["baseParameters"]["itemTypeId"]] + ";"


                effects = {}
                for p in param_names:
                    effects[p] = 0
                
                for effect in value["definition"]["equipEffects"]:
                    effect = effect["effect"]
                    t = effect["definition"]["actionId"]
                    # maitrise multi elem
                    if t == 1068:
                        effects["Maitrise Elem"] = int(effect["definition"]["params"][0] + level * effect["definition"]["params"][1])
                        effects["NB Elements"] = int(effect["definition"]["params"][2] + level * effect["definition"]["params"][3])
                    elif t == 120:
                        effects["Maitrise Elem"] = int(effect["definition"]["params"][0] + level * effect["definition"]["params"][1])
                        effects["NB Elements"] = 4
                    elif t in params:
                        tt = params[t]
                        v = 0
                        for f in tt["formula"]:
                            mult = 1
                            if f < 0:
                                f = f * -1 - 1
                                mult = -1
                            v += mult * (effect["definition"]["params"][0 + f * 2] + level * effect["definition"]["params"][1 + f * 2]) 
                        effects[tt["name"]] = int(v)

                for effect in effects:
                    line += str(effects[effect]) + ";" 

                line += "\n"

                file.write(line.encode('utf8'))
        
version = "1.81.1.15"

#version = get_version()
get_json(version)
data = load_data(version)
parse_data(data)


