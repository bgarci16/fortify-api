# importing the requests library 
import requests
import json

def get_version_ids(HEADS):
    idList = []
    id_Dict = {}
    URL = SSC + "/ssc/api/v1/projectVersions?start=0&limit=0&fulltextsearch=false&includeInactive=false&myAssignedIssues=false&onlyIfHasIssues=false"
    r = requests.get(url=URL, headers=HEADS, verify=False)
    resp = r.json()

    ind = 0

    for i in resp['data']:
        if i['serverVersion'] == 19.1 or i['serverVersion'] == 18.2:
            temp_dict = {}
            temp_dict['name'] = i['project']['name']
            temp_dict['id'] = i['id']
            idList.append(temp_dict)
            id_Dict[ind] = temp_dict.items()

    return idList

    r.close()

def get_metrics(result, HEADS, id, index):
    # api-endpoint
    URL = SSC + "/ssc/api/v1/projectVersions/" + str(id['id']) + "/performanceIndicatorHistories?start=0&limit=0"
    # sending get request and saving the response as response object
    r = requests.get(url=URL, headers=HEADERS, proxies=PROXIES, verify=False)
    result = r.json()
    total_issues = result['data']

    temp_list = []
    temp_result = {}
    for i in total_issues:
        temp_result['Application Name'] = id['name']
        if i['name'] == "Total_Issues":
            temp_result["Total Issues"] = i['value']
        if i['name'] == "Unaudited":
            temp_result["Unaudited"] = i['value']
        if i['name'] == "Audited":
            temp_result["Audited"] = i['value']
        if i['name'] == "Percent_Audited":
            temp_result["Percent_Audited"] = i['value']
        if i['name'] == "Percent_NAI":
            temp_result["Percent_NAI"] = i['value']
        if i['name'] == "Percent_Suppressed":
            temp_result["Percent_Suppressed"] = i['value']
        if i['name'] == "Suppressed":
            temp_result["Suppressed"] = i['value']
        if i['name'] == "Total_Audited":
            temp_result["Total_Audited"] = i['value']
        if i['name'] == "Total_NAI":
            temp_result["Total_NAI"] = i['value']
        if i['name'] == "Exploitable":
            temp_result["True_Positive"] = i['value']

    if temp_result:
        temp_list.append(temp_result)

    return temp_list

    r.close()

def get_scan_times():
    URL= SSC + "/ssc/api/v1/cloudjobs?hideProgress=true&limit=0"
    r = requests.get(url=URL, headers=HEADERS, verify=False)
    result = r.json()
    tempDict = {}
    for value in result['data']:
        if value['jobState'] == "UPLOAD_COMPLETED" and value['projectName'] not in tempDict.values():
            tempDict[value['projectName']] = value['scanDuration']

    r.close()

    return tempDict

authString = ""
AUTH_URL = SSC + "/ssc/api/v1/tokens"

AUTH_HEADERS = {
    'accept': 'application/json',
    'Content-Type': 'application/json;charset=UTF-8',
    'Authorization': 'Basic ' + authString
}

AUTH_DATA = json.dumps({
    "type": "UnifiedLoginToken"
})

PROXIES = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080',
}

# sending get request and saving the response as response object
r = requests.post(url=AUTH_URL, headers=AUTH_HEADERS, proxies=PROXIES, data=AUTH_DATA, verify=False)
jsonAuth = r.json()
token = jsonAuth['data']['token']

r.close()


HEADERS = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': "FortifyToken " + token
}


id_Dict2 = get_version_ids(HEADERS)

index = 0
total_result = {}
scanTimes = get_scan_times()

for id in id_Dict2:
    total_result[index] = get_metrics(r.json(), HEADERS, id, index)

    if not total_result[index]:
        total_result[index].clear()
        index -= 1
    index += 1


totalIndex = 0
for result in total_result:
    for value in total_result.__getitem__(result):
        print(value['Application Name'])
        if 'Total Issues' in value.keys():
            print("Total Issues ", value['Total Issues'])
        else:
            print("Total Issues ", "Not Available")
        if 'Total_Audited' in value.keys():
            print("Total Audited ", value['Total_Audited'])
        else:
            print("Total Audited ", "Not Available")
        if 'Percent_Audited' in value.keys():
            print("Percent Audited ", value['Percent_Audited'], "%")
        else:
            print("Percent Audited ", "Not Available")
        if 'Unaudited' in value.keys():
            print("Unaudited ", value['Unaudited'])
        else:
            print("Unaudited ", "Not Available")
        if 'Suppressed' in value.keys():
            print("Suppressed ", value['Suppressed'])
        else:
            print("Suppressed ", "Not Available")
        if 'Percent_Suppressed' in value.keys():
            print("Percent Suppressed ", value['Percent_Suppressed'], "%")
        else:
            print("Percent Suppressed ", "Not Available")
        if 'Total_NAI' in value.keys():
            print("Total Not An Issue ", value['Total_NAI'])
        else:
            print("Total Not An Issue ", "Not Available")
        if 'Percent_NAI' in value.keys():
            print("Percent Not An Issue ", value['Percent_NAI'], "%")
        else:
            print("Percent Not An Issue ", "Not Available")
        if 'True_Positive' in value.keys():
            print("True Positive ", value['True_Positive'])
        else:
            print("True Positive ", "Not Available")
        if value['Application Name'] in scanTimes.keys():
            if scanTimes[value['Application Name']] > 59 and scanTimes[value['Application Name']] < 3600:
                print("Scan time ", int(round(scanTimes[value['Application Name']] / 60)), " minutes")
            elif scanTimes[value['Application Name']] >= 3600:
                print("Scan time ", int(round(scanTimes[value['Application Name']] / 3600)), " hours")
            else:
                print("Scan time ", scanTimes[value['Application Name']], " seconds")
        else:
            print("Scan time ", "Not Available")
    print("\n")


# Clean up tokens
DEL_TOK_URL = AUTH_URL + "?all=true"
r = requests.delete(url=DEL_TOK_URL, headers=AUTH_HEADERS, proxies=PROXIES, verify=False)

r.close()
