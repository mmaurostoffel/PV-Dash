import numpy as np
import pandas as pd


def getBaseData(batMax, batterieEffDropdownList):
    '''
    Receive Main Data from API and generate additional Lines for better Handling
    '''
    url = "https://iten-web.ch/batteriespeicher/api/data_as_json.php"
    main_data = pd.read_json(url)

    # Generate Additional Data
    main_data = main_data[pd.to_numeric(main_data['PVErtrag'], errors='coerce').notnull()]
    main_data = main_data.astype(
        {"Datum": "string", "PVErtrag": "Int64", "Netz": "Int32", "Bezug": "Int32", "Einspeisung": "Int32",
         "Verbrauch": "Int32"})
    main_data.insert(1, "10 kWh Linie", 10000, False)
    main_data.insert(1, "Produktion", main_data['Netz'] > 0, False)
    main_data.insert(1, "Sum Erzeugung", main_data['Einspeisung'].cumsum(), False)
    main_data.insert(1, "Sum Verbrauch", main_data['Verbrauch'].cumsum(), False)
    realDatetime = pd.to_datetime(main_data['Datum'])
    main_data.insert(1, "realDatum", realDatetime, False)
    realDate = pd.to_datetime(main_data['Datum'])
    main_data.insert(1, "realDatumOnlyDate", pd.to_datetime(main_data['realDatum']).dt.date, False)
    main_data.insert(1, "batData", generateBatData(main_data, batMax[0], batterieEffDropdownList[-3] / 100), False)

    return main_data


def getBatteryData():
    '''
    Receive Battery Data from API and reformat into the 3 lists batCaption, batMax, batPrice
    '''
    batCaption = []
    batMax = []
    batPrice = []

    url = "https://iten-web.ch/batteriespeicher/api/batteries"
    batdata = pd.read_json(url)

    batData = batdata['response']
    for data in batData:
        batCaption.append((data['caption'] + " ( " + str(data['max'] / 1000) + "kWh )"))
        batMax.append(data['max'])
        batPrice.append(data['price'])
    return batCaption, batMax, batPrice


    batData = batdata['response']
    for data in batData:
        data = eval(data)

        batCaption.append(data['caption'])
        batMax.append(data['max'])
        batPrice.append(data['price'])
    return batCaption, batMax, batPrice


def generateBatData(json_data, batLimit, batEff):
    '''
    Generate the battery data from the given parameters and filtered json_data
    '''
    lastVal = 0
    batData = []
    for val in json_data['Netz']:
        if val <0:
            curr = (lastVal + val*-1 * batEff) * 0.01
        else:
            curr = (lastVal + val * -1) * 0.01

        if curr > batLimit:
            curr = batLimit
        elif curr < 0:
            curr = 0
        lastVal = curr
        batData.append(np.round(curr, 2))
    return batData
