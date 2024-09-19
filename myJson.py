import json

def get_float(msg):
    try:
        return float(input(msg))
    except:
        return 0

class openFile:

    def __init__(self, jsonfile):

        self.jsonfile = jsonfile
        try:
            with open(self.jsonfile, 'r') as file:
                pass
        except FileNotFoundError:    
            with open(self.jsonfile, 'w') as file:
                pass

    def appendData(self,data,is_list_already: bool):

        with open(self.jsonfile, 'w') as file:
            pass
        
        with open(self.jsonfile, 'r') as file:
            try:
                existingData = json.load(file)
            except:
                existingData = []

        if is_list_already:
            existingData = data
        else:
            existingData.append(data)

        with open(self.jsonfile, 'w') as file:
            json.dump(existingData, file, indent = 4)

    def removeData(self, property, value):
        with open(self.jsonfile, 'r') as file:
            try:
                self.existingData = json.load(file)
            except:
                self.existingData = []

        newData = []

        for item in range(len(self.existingData)):
            if self.existingData[item][property] != value:
                newData.append(self.existingData[item])

        with open(self.jsonfile, 'w') as file:
            json.dump(newData, file, indent = 4)

    def cleanData(self):
        with open(self.jsonfile, 'w') as file:
            json.dump([],file)

    def get(self):
        with open(self.jsonfile, 'r') as file:
            try:
                self.existingData = json.load(file)
            except json.decoder.JSONDecodeError:
                self.existingData = []
        return self.existingData