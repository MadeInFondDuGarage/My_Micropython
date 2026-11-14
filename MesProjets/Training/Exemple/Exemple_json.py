#json exemple

import json

data = {
    "president": {
        "name": "Zaphod Beeblebrox",
        "species": "Betelgeusian",
        "Real":True
    }
}

with open("data_file.json", "w") as write_file:
    json.dump(data, write_file)


with open("data_file.json", "rb") as read_file:
    mesDatas=json.load(read_file)
    
print(mesDatas)