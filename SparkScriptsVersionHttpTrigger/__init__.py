import logging
import requests
import json
import os
from urllib.parse import urlparse
from azure.data.tables import TableServiceClient
from azure.identity import DefaultAzureCredential
from azure.functions import HttpRequest, HttpResponse


tenant = os.environ["tenant"]
clientid = os.environ["clientid"]
secret = os.environ["secret"]

AZURE_TENANT_ID = os.environ["AZURE_TENANT_ID"]
AZURE_CLIENT_ID = os.environ["AZURE_CLIENT_ID"]
AZURE_CLIENT_SECRET = os.environ["AZURE_CLIENT_SECRET"]

def main(req: HttpRequest) -> HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    mondayScriptsVersion = ''
    version = ''
    tableName = 'sparkVersion'
    version = req.params.get('version')
    sa_name = req.params.get('saname')

    if not version:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            version = req_body.get('version')
            sa_name = req_body.get('saname')
            print(version, sa_name)

    sa_url = sa_name #"https://3softaudytmainsa.blob.core.windows.net/3softaudytmainsa"
    parsed_url = urlparse(sa_url)
    account_name = parsed_url.netloc
    sa_name = parsed_url.path.lstrip("/")
    print(sa_name)
    print("https://azurelabmainsa.table.core.windows.net")
    ta_url = "https://{}.table.core.windows.net".format(sa_name)
    print(ta_url)

    credential = DefaultAzureCredential()

    table = TableServiceClient(endpoint=ta_url, credential=credential)
    table2 = table.get_table_client(tableName)

    i = 0
    for entity in table2.list_entities():  # table_client.list_entities():
        mondayScriptsVersion = entity['compVersions']
        print(mondayScriptsVersion)
        i += 1
        if i % 100 == 0:
            print('wersja', i)
    
    print(table.list_tables)

    with TableServiceClient(
            endpoint=ta_url, credential=credential
    ) as table_service_client:
        table_client = table_service_client.create_table_if_not_exists(tableName)

    try:
        mondayUrl = "https://api.monday.com/v2"

        payload = json.dumps({
            "query": "query { boards(ids: 4756745720) { items_page {items { name column_values(ids: [\"text\",\"tekst\",\"text9\"]) { column { title } text } } } } }"
        })
        headers = {
            'Authorization': 'eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjMyMjE2ODc5NiwiYWFpIjoxMSwidWlkIjozOTUzNTMxNiwiaWFkIjoiMjAyNC0wMi0xNlQxOToxMDowNS40NDNaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MTI3NTcyNDIsInJnbiI6InVzZTEifQ.7nm_A6KgD8BWSJaEoxVN-mooRTABNkla6M06Iiq2kgo',
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", mondayUrl, headers=headers, data=payload)

        json_response = json.loads(response.text)
        version = '3.14'
        jsonMondayScriptsVersion = ''
        json_data = (json_response['data']['boards'][0]['items_page']['items'])

        for i in json_data:
            if i['name'] == version:
                jsonMondayScriptsVersion = i['column_values']
                break

        # mondayScriptsVersion = (list(filter(lambda x: x["name"] == version, json_data)))
        mondayScriptsVersion = json.dumps(jsonMondayScriptsVersion)

    except Exception:
        # list versions from SA
        with TableServiceClient(
                endpoint=ta_url, credential=credential
        ) as table_service_client:
            entity = table_service_client.get_table_client(tableName)
            i = 0
            for entity in entity.list_entities():  # table_client.list_entities():
                mondayScriptsVersion = entity['compVersions']
                i += 1
                if i % 100 == 0:
                    print('wersja', i)

    else:
        my_entity = {
            u'PartitionKey': 'versions',
            u'RowKey': version,
            u'compVersions': mondayScriptsVersion
        }

    # write version to SA
        with TableServiceClient(
                endpoint=ta_url, credential=credential
        ) as table_service_client:
            entity = table_service_client.get_table_client(tableName)
            try:
                entity = entity.update_entity(entity=my_entity)
            except Exception:
                entity = entity.create_entity(entity=my_entity)
                pass
            else:
                print('in else create new')

    # print('from global: ', mondayScriptsVersion)

    mondayScriptsVersionJson = json.loads(mondayScriptsVersion)
    print(mondayScriptsVersionJson)
    

    if version and sa_name:
        return HttpResponse(
            mondayScriptsVersion,
            headers={
                'content-type': "application/json"
            },
            status_code = 200
            )
    else:
        return HttpResponse(
            f"Please provide both 'version' and 'saname' parameters.",
            status_code = 400
            )
    # if version and saName:
    #     return HttpResponse(f"Hello, {version} {saName}. This HTTP triggered function executed successfully.")
    # else:
    #     return HttpResponse(
    #         "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
    #         status_code=200
    #     )
