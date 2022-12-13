import os
import requests
import json
import datetime
from datetime import datetime
from datetime import date
import pprint
import numpy as np
from multiprocessing import Process
import time
import glob
import logging


logging.basicConfig(filename="log.log", level=logging.INFO, format="%(asctime)s  -  %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")
logging.info("------------------------------------------------------------------------------------------")
pp = pprint.PrettyPrinter(indent=4)

SIZE : int = 60 ## Means that there will be 60 bus stops per process, as we can handle a little bit more than 1/second
## SIZE time references:
##      SIZE = 60 -> time = 1:17
##      SIZE = 40 -> time = 0:53

SLEEPTIME = 222  ## approximately 3:30 minutes waiting
ACCESS_ID = "e57f91f7-0a5d-4d9b-a333-566839963579"
LANG = "fr"
FORMAT = "json"

BUS_STOPS_FILE = "data/bus_stops_python.json"
TEMP_TOTAL_DIR = "data/temp/total/"
TEMP_AVERAGE_DIR = "data/temp/average/"
TIMEFORMAT = "%H:%M:%S"

SAVE_LATE_BUSSES_TO = "data/buslines/temp/"
SAVE_IF_LATE = 5

SAVE_BUS_TO = "data/buslines/all/"

FEATURES_TOTAL = []
FEATURES_AVERAGE = []

SAVE_DICT = {}

with open(BUS_STOPS_FILE, "r", encoding="utf-8") as file:
    bus_stops_geojson = json.load(file)

BUS_STOPS : list = bus_stops_geojson["features"]
BUS_STOPS_LEN = len(BUS_STOPS)


def update(_list, number:int):
    features_list_total = []
    features_list_average = []
    bus_stops = list(_list)
    all_list = []
    i=0
    for stop in bus_stops: ## For each bus stop in the list get its name, location, etc.
        stop = dict(stop)
        stop_id = stop["properties"]["id"]
        stop_id = str(stop_id)
        stop_coords = stop["geometry"]["coordinates"]
        stop_name = stop["properties"]["name"]

    
        #stop_id = "200426002"
        ## Get the departures from the stop in json format
        url = str("https://cdt.hafas.de/opendata/apiserver/departureBoard?accessId=" + ACCESS_ID + "&lang=" + LANG + "&id=" + stop_id + "&format=" + FORMAT)
        response = requests.get(url)
        data = response.json()

        if "Departure" in data: ## If there are departures from this stop get the departures as list
            journeys = data["Departure"]

            late = 0 ## set the value of the total minutes busses are late at this stop to 0
            amount_busses = 0 ## set the amount of busses at this station to 0 to later be able to divide the latenes by the amount of busses for the average lateness
            for journey in journeys: ## for each bus that will arrive here, get the time it should arrive and the time it will arrive
                journey = dict(journey)
                time = journey["time"] ## Get the time it should arrive as a string
                if "rtTime" in journey: ## if the time it will arrive is already known (= if the bus is already driving), get the arrival time as a string
                    rttime = journey["rtTime"]

                    t1 = datetime.strptime(time, TIMEFORMAT) ## convert the times to timeformat to be able to calculate the difference (=how late the bus is)
                    t2 = datetime.strptime(rttime, TIMEFORMAT)

                    l = t2 - t1
                    add_to_late = int(l.seconds / 60)
                    late += add_to_late ## If this returns 0, the bus is on time, if it returns > 0, bus is late. (The API does not return seconds, only minutes. So t1 could be=17:52:00 and t2=17:54:00, which means the bus is 2 minutes late)
                    amount_busses += 1

                    
                    
                    ## Now if bus is more than x minutes late write to a separate file
                    if add_to_late > SAVE_IF_LATE:
                        print(add_to_late)
                        name = journey["name"]
                        _date = journey["date"]
                        direction = journey["direction"]
                        print(f"BEFORE OPERATOR: Station id={stop_id}")
                        operator = journey["Product"]["operator"]
                        unique_id = journey["Product"]["num"]
                        print(unique_id)
                        date_now = str(date.today())
                        file_save_to = str(SAVE_LATE_BUSSES_TO + str(number) + ".json")

                        if os.path.isfile(file_save_to):
                            with open(file_save_to, "r", encoding="utf-8") as file:
                                old_dict = json.load(file)

                            if unique_id in old_dict.keys() and int(old_dict[unique_id]["late"]) < int(add_to_late) or unique_id not in old_dict.keys():
                                old_dict[unique_id] = {"name":name, "late":add_to_late,"time":time, "stop":stop_name, "direction":direction, "operator":operator, "date":_date}

                            
                            with open(file_save_to, "w", encoding="utf-8") as file:
                                json.dump(old_dict, file, ensure_ascii=False)
                                                            
                        if not os.path.isfile(file_save_to):
                            new_dict = {}
                            new_dict[unique_id] = {"name":name,"late":add_to_late,"time":time, "stop":stop_name,"direction":direction,"operator":operator,"date":_date}

                            with open(file_save_to, "w", encoding="utf-8") as file:
                                json.dump(new_dict, file, ensure_ascii=False)
                    
                    all_list.append(journey["Product"]["num"]) ## append all busses to list
                    
                elif "rtTime" not in journey: ## if there is no realtime (= real arrival time) available, usually if journey hasn't started yet
                    late += 0
                    amount_busses += 0

            _file = str(SAVE_BUS_TO + str(number) + ".json")
            with open(_file, "w", encoding="utf-8") as file:
                json.dump(all_list, file, ensure_ascii=False)
                

        #LIVE_DATA[stop_id] = data
            stop_data_total = {"type":"Feature", "geometry":{"type":"Point","coordinates":stop_coords}, "properties":{"id":int(stop_id),"name":stop_name, "late":late}} ## return the stop and add how late it is to change the color on the map
            if amount_busses < 1:
                amount_busses = 1
            stop_data_average = {"type":"Feature", "geometry":{"type":"Point", "coordinates":stop_coords}, "properties":{"id":int(stop_id), "name":stop_name, "late":int(late/amount_busses)}}
        
            #print(i)
            i += 1 ## Counter to see how many stations have already been done

            




        elif "Departure" not in data and "TechnicalMessages" in data:
            ## Means that there are no current departures from this station
            stop_data_total = {"type":"Feature", "geometry":{"type":"Point", "coordinates":stop_coords}, "properties":{"id":int(stop_id), "name":stop_name, "late":0}} ## Set late to 0 because if there is no bus driving to that stop, there is no bus that can be late there
            stop_data_average = {"type":"Feature", "geometry":{"type":"Point", "coordinates":stop_coords}, "properties":{"id":int(stop_id), "name":stop_name, "late":0}}

        elif "Departure" not in data and "errorText" in data:
            ## Means there is an error like "Quota exceeded" or "stop location unknown/wrong"
            if not "quota exceeded" in data["errorText"]:
                #print("[ERROR]: " + data["errorText"])
                #print("STATION ID: " + stop_id)
                logging.warning(f"[ERROR]: {data['errorText']}")
                logging.info(f"STATION ID: {stop_id}")

            stop_data_total = {"type":"Feature", "geometry":{"type":"Point", "coordinates":stop_coords}, "properties":{"id":int(stop_id), "name":stop_name, "late":"ERROR"}} ## Set late to "ERROR" so that we can see on the map that smth didn't work with that station
            stop_data_average = {"type":"Feature", "geometry":{"type":"Point", "coordinates":stop_coords}, "properties":{"id":int(stop_id), "name":stop_name, "late":"ERROR"}}

        features_list_total.append(stop_data_total) ## Add the station to a list containing all already done stations, which will then be added to the "feature" list in the geojson(/results) file
        features_list_average.append(stop_data_average)

        ## Write features_list to file to retrieve it outside the process
        new_file_total = str(TEMP_TOTAL_DIR + str(number) + ".txt")
        with open(new_file_total, "w", encoding="utf-8") as file:
            json.dump(features_list_total, file, ensure_ascii=False)
        
        new_file_average = str(TEMP_AVERAGE_DIR + str(number) + ".txt")
        with open(new_file_average, "w", encoding="utf-8") as file:
            json.dump(features_list_average, file, ensure_ascii=False)



    


sliced_bus_stops_list = np.array_split(BUS_STOPS, SIZE)



while __name__ == "__main__":
    FEATURES_TOTAL = []
    FEATURES_AVERAGE = []
    date_now = str(date.today())

################## For Total lateness #########################
    _temp_dir_total = str(TEMP_TOTAL_DIR + "*")
    files = glob.glob(_temp_dir_total)
    for file in files:
        os.remove(file)
    logging.info("Finished cleaning temp/total directory")
    logging.info(TEMP_TOTAL_DIR)

    for file in glob.glob(str(TEMP_AVERAGE_DIR + "*")): ## Same as for total lateness but for average
        os.remove(file)
    logging.info("Finished cleaning temp/average directory")
    logging.info(TEMP_AVERAGE_DIR)

    for file in glob.glob(str(SAVE_LATE_BUSSES_TO + "*")): ## Same as for total lateness but for average
        os.remove(file)
    logging.info("Finished cleaning save late busses to directory")
    logging.info(SAVE_LATE_BUSSES_TO)

    delete_all_files = [SAVE_BUS_TO, SAVE_LATE_BUSSES_TO, TEMP_AVERAGE_DIR, TEMP_TOTAL_DIR]
    for folder in delete_all_files:
        _folder = str(folder + "*")
        files_in_folder = glob.glob(_folder)
        for file in files_in_folder:
            os.remove(file)
        logging.info(f"Finished cleaning directory: {folder}")

################# Start Processes ###############################
    logging.info("Starting processes")
    logging.info(f"{SIZE} processes are being started")
    process_number = 0
    for small_bus_stops_list in sliced_bus_stops_list:
        p = Process(target=update, args=(small_bus_stops_list, process_number,)) ## We are using multiprocessing to be able to run multiple requests at the same time, which wouldn't be possible otherwise and we would need around 48 minutes to update the data once
        p.start()
        print("[START][PROCESS]: ID = ", process_number)
        process_number += 1
        

    logging.info("Finished all processes")
    logging.info(f"Sleeping for {SLEEPTIME} seconds")
    print("SLEEPING")
    time.sleep(SLEEPTIME) ## Sleep now to avoid losing data

    files = [f for f in os.listdir(TEMP_TOTAL_DIR) if os.path.isfile(os.path.join(TEMP_TOTAL_DIR, f))] ##Returns list with all the filenames ("0.txt") in the folder
    for file in files:
        file = str(TEMP_TOTAL_DIR + file)
        with open(file, "r", encoding="utf-8") as _file:
            try:
                content = json.load(_file)
            except:
                #print(file)
                logging.warning(f"[ERROR]: Could not read file {file}")
        for item in content:
            FEATURES_TOTAL.append(item)

    

#################### For Average lateness ###########################################
    files = [f for f in os.listdir(TEMP_AVERAGE_DIR) if os.path.isfile(os.path.join(TEMP_TOTAL_DIR, f))]
    for file in files:
        file = str(TEMP_AVERAGE_DIR + file)
        with open(file, "r", encoding="utf-8") as _file:
            try:
                content = json.load(_file)
            except:
                logging.warning(f"[ERROR]: Could not read file {file}")
        for item in content:
            FEATURES_AVERAGE.append(item)


    #### CREATE NEW FILE FOR EACH PROCESS WITH NUMBER AND OS SCANDIR TO GET ALL
    new_dict =  {"type":"FeatureCollection", "features":FEATURES_TOTAL}
    new_dict_average = {"type":"FeatureCollection", "features":FEATURES_AVERAGE}
    new_data = str("var stops = " + str(new_dict) + ";" + "var stops_average = " + str(new_dict_average) + ";")
    with open("data/bus_stops.json", "w", encoding="utf-8") as file:
        file.write(new_data)



    ################# Save busses that are x minutes late ####################
    file_today = str("data/buslines/" + date_now + ".json")
    if os.path.isfile(file_today):
        with open(file_today, "r", encoding="utf-8") as file:
            old_dict = json.load(file)
    elif not os.path.isfile(file_today):
        old_dict = {}

    for file in [f for f in os.listdir(SAVE_LATE_BUSSES_TO) if os.path.isfile(os.path.join(SAVE_LATE_BUSSES_TO, f))]:
        file = str(SAVE_LATE_BUSSES_TO + file)
        with open(file, "r", encoding="utf-8") as _file:
            content = json.load(_file)

        for item in content.keys():
            if item in old_dict.keys() and content[item]["late"] > old_dict[item]["late"] or item not in old_dict.keys():
                old_dict[item] = content[item]

    with open(file_today, "w", encoding="utf-8") as file:
        json.dump(old_dict, file, ensure_ascii=False)


    ####### Total ########
    file_today = str("data/buslines/" + date_now + "_all.json")
    if os.path.isfile(file_today):
        with open(file_today, "r", encoding="utf-8") as file:
            old_list = json.load(file)
    elif not os.path.isfile(file_today):
        old_list = []

    for file in [f for f in os.listdir(SAVE_BUS_TO) if os.path.isfile(os.path.join(SAVE_BUS_TO, f))]:
        _file = str(SAVE_BUS_TO + file)
        with open(_file, "r", encoding="utf-8") as file:
            content = json.load(file)

        for item in content:
            old_list.append(item)
    
    with open(file_today, "w", encoding="utf-8") as file:
        json.dump(old_list, file, ensure_ascii=False)


    