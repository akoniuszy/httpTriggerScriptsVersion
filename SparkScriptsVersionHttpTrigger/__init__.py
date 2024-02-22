import logging
import requests
import json
import os
from azure.data.tables import TableServiceClient
from azure.identity import DefaultAzureCredential
from azure.identity import ClientSecretCredential
from azure.identity import EnvironmentCredential
from azure.functions import HttpRequest, HttpResponse


tenant = os.environ["tenant"]
clientid = os.environ["clientid"]
secret = os.environ["secret"]

# os.environ['AZURE_CLIENT_ID'] = '9a7cd346-ef97-424d-9fee-d322956cb859'
# os.environ['AZURE_CLIENT_SECRET'] = 'w9g8Q~R7FL28-KsJ2NyI_MrF5gRVRaUwNn1Cqbri'
# os.environ['AZURE_TENANT_ID'] = '01e46bc7-d681-41c9-9fa9-fd069ca52e21'

AZURE_TENANT_ID = os.environ["AZURE_TENANT_ID"]
AZURE_CLIENT_ID = os.environ["AZURE_CLIENT_ID"]
AZURE_CLIENT_SECRET = os.environ["AZURE_CLIENT_SECRET"]

def main(req: HttpRequest) -> HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    mondayScriptsVersion = ''
    version = ''
    tableName = 'sparkVersion'

    # credential = ClientSecretCredential(
    # tenant_id=tenant,
    # client_id=clientid,
    # client_secret=secret,
    # )
    # print(credential)

    # credential2 = EnvironmentCredential()

    # token = credential.get_token(".default")

    # default_credential = DefaultAzureCredential(exclude_interactive_browser_credential=False,
    # exclude_shared_token_cache_credential=True,
    # exclude_visual_studio_code_credential=True,
    # exclude_managed_identity_credential=True,
    # exclude_environment_credential=True,
    # exclude_cli_credential=True,
    # exclude_powershell_credential=True)

    version = req.params.get('version')
    if not version:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            version = req_body.get('version')

    with TableServiceClient(
            endpoint="https://azurelabmainsa.table.core.windows.net", credential=EnvironmentCredential()
    ) as table_service_client:
        table_client = table_service_client.create_table_if_not_exists(tableName)

    # try:
    #     mondayUrl = "https://api.monday.com/v2"

    #     payload = json.dumps({
    #         "query": "query { boards(ids: 4756745720) { items_page {items { name column_values(ids: [\"text\",\"tekst\",\"text9\"]) { column { title } text } } } } }"
    #     })
    #     headers = {
    #         'Authorization': 'eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjMyMjE2ODc5NiwiYWFpIjoxMSwidWlkIjozOTUzNTMxNiwiaWFkIjoiMjAyNC0wMi0xNlQxOToxMDowNS40NDNaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MTI3NTcyNDIsInJnbiI6InVzZTEifQ.7nm_A6KgD8BWSJaEoxVN-mooRTABNkla6M06Iiq2kgo',
    #         'Content-Type': 'application/json'
    #     }

    #     response = requests.request("GET", mondayUrl, headers=headers, data=payload)

    #     json_response = json.loads(response.text)
    #     version = '3.14'
    #     jsonMondayScriptsVersion = ''
    #     json_data = (json_response['data']['boards'][0]['items_page']['items'])

    #     for i in json_data:
    #         if i['name'] == version:
    #             jsonMondayScriptsVersion = i['column_values']
    #             break

    #     # mondayScriptsVersion = (list(filter(lambda x: x["name"] == version, json_data)))
    #     mondayScriptsVersion = json.dumps(jsonMondayScriptsVersion)

    # except Exception:
    #     # list versions from SA
    #     with TableServiceClient(
    #             endpoint="https://azurelabmainsa.table.core.windows.net", credential=credential
    #     ) as table_service_client:
    #         entity = table_service_client.get_table_client(tableName)
    #         i = 0
    #         for entity in entity.list_entities():  # table_client.list_entities():
    #             mondayScriptsVersion = entity['compVersions']
    #             i += 1
    #             if i % 100 == 0:
    #                 print('wersja', i)

    # else:
    #     my_entity = {
    #         u'PartitionKey': 'versions',
    #         u'RowKey': version,
    #         u'compVersions': mondayScriptsVersion
    #     }

    # # write version to SA
    #     with TableServiceClient(
    #             endpoint="https://azurelabmainsa.table.core.windows.net", credential=credential
    #     ) as table_service_client:
    #         entity = table_service_client.get_table_client(tableName)
    #         try:
    #             entity = entity.update_entity(entity=my_entity)
    #         except Exception:
    #             entity = entity.create_entity(entity=my_entity)
    #             pass
    #         else:
    #             print('in else create new')

    # # print('from global: ', mondayScriptsVersion)

    # mondayScriptsVersionJson = json.loads(mondayScriptsVersion)
    # print(mondayScriptsVersionJson)
    

    if version:
        return HttpResponse(f"Hello, {version}. This HTTP triggered function executed successfully.")
    else:
        return HttpResponse(
            "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
            status_code=200
        )
