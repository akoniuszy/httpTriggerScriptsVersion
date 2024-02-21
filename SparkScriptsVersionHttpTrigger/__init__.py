import logging

from azure.functions import HttpRequest, HttpResponse


def main(req: HttpRequest) -> HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    version = req.params.get('version')
    if not version:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            version = req_body.get('version')

    if version:
        return HttpResponse(f"Hello, {version}. This HTTP triggered function executed successfully.")
    else:
        return HttpResponse(
            "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
            status_code=200
        )
