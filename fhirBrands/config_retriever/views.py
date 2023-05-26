# retrieve_config/views.py

from django.shortcuts import render
from .forms import UriForm
import requests
import logging
logger = logging.getLogger('django')
import base64
import json
from bs4 import BeautifulSoup
from markdown import markdown
import re


def markdown_to_text(markdown_string):
    """Converts a markdown string to plaintext"""

    # md -> html -> text since BeautifulSoup can extract text cleanly
    html = markdown(markdown_string)
    # remove code snippets
    html = re.sub(r'<pre>(.*?)</pre>', ' ', html)
    html = re.sub(r'<code>(.*?)</code>', ' ', html)
    # replace unusual newlines with <br/>
    html = html.replace("\\n", "<br/>")
    # extract text
    soup = BeautifulSoup(html, "html.parser")
    text = ''.join(soup.findAll(text=True))
    return text


def process_endpoint_data(data,org_dict):
    # If data is a string, load it as json
    if isinstance(data, str):
        data = json.loads(data)
    for entry in data['entry']:
        endpoint_data = entry.get('resource')
        if endpoint_data and endpoint_data.get("resourceType") == "Endpoint":
            endpoint_id = endpoint_data["id"]
            endpoint_name = endpoint_data["name"]
            endpoint_status = endpoint_data["status"]
            endpoint_connection_type = endpoint_data["connectionType"]["code"]
            endpoint_uri = endpoint_data["address"]
            managing_organization = endpoint_data["managingOrganization"]["reference"].rsplit(':')[-1]  # Extracting just the ID

            # Process extension data
            extensions = []
            for extension in endpoint_data.get("extension", []):
                ext_url = extension["url"]
                ext_value = extension.get("valueCode")  # Assuming valueCode is always present, otherwise use .get() 
                extensions.append({
                    "url": ext_url,
                    "valueCode": ext_value
                })
                
            endpoint_info = {
                "id": endpoint_id,
                "name": endpoint_name,
                "status": endpoint_status,
                "connectionType": endpoint_connection_type,
                "uri": endpoint_uri,
                "extensions": extensions,
            }

            # If the organization already exists in the dictionary, just update the endpoint data
            if managing_organization in org_dict.keys():
                org_dict[managing_organization]["endpoint"] = endpoint_info
                # logger.info(org_dict[managing_organization]["endpoint"])
            
            for outer_key in org_dict.keys():
                if managing_organization in org_dict[outer_key]["sites"].keys():
                    org_dict[outer_key]["sites"][managing_organization]["endpoint"] = endpoint_info
      
    return org_dict


def parse_json(data):
    # Loading JSON into a Python dictionary
    # data = json_str
    # Initializing an empty dictionary to store the parsed data
    org_dict = {}

    for entry in data['entry']:
        org_data = entry.get('resource')
        org_id = org_data.get('id')
        if org_data and org_data.get("resourceType") == "Organization":
            # Decode Base64 Image
            extension = org_data.get('extension', [])
            for ext in extension:
                if "http://hl7.org/fhir/smart-app-launch/StructureDefinition/brand-logo" in ext.get('url'):
                    # Get the base64 string, remove the prefix if necessary
                    base64_str = ext.get('valueUrl', '').replace('data:image/svg+xml;base64,', '')
                    try:
                        # Decode the base64 string and re-encode it for HTML
                        decoded_img = base64.b64decode(base64_str).decode('utf-8')
                        ext['valueUrl'] = 'data:image/svg+xml;base64,' + base64.b64encode(decoded_img.encode()).decode('utf-8')
                    except:
                        # Image could not be decoded and re-encoded, leave as is
                        pass
                # Convert markdown to html
                if "http://hl7.org/fhir/smart-app-launch/StructureDefinition/patient-access-description" in ext.get('url'):
                    ext['valueMarkdown'] = markdown_to_text(ext['valueMarkdown'])
            # If "partOf" is in the organization's data, it's considered a child
            if 'partOf' in org_data:
                parent_id = org_data['partOf']['reference'].rsplit(':')[-1]

                # Checking if parent exists in dictionary
                if parent_id in org_dict:
                    # Adding child organization to parent
                    if 'sites' not in org_dict[parent_id]:
                        org_dict[parent_id]['sites'] = {}
                    org_dict[parent_id]['sites'][org_id] = org_data
                else:
                    # If parent does not exist in the dictionary, adding it
                    org_dict[parent_id] = {'sites': {org_id: org_data}}
            else:
                # If organization is not a child, adding it directly to the dictionary
                org_dict[org_id] = org_data
    
    org_dict = process_endpoint_data(data, org_dict)
    # logger.info(org_dict)
    return org_dict

def retrieve_config(request):
    if request.method == 'POST':
        form = UriForm(request.POST)
        if form.is_valid():
            base_uri = form.cleaned_data['base_uri']
            config_uri = f"{base_uri.rstrip('/')}/.well-known/smart-configuration"
            response = requests.get(config_uri)
            response.raise_for_status()  # Raise HTTPError if the request failed
            data = response.json()

            patient_access_brand_bundle = data.get('patientAccessBrandBundle')
            if patient_access_brand_bundle:
                # Perform a GET request to the patientAccessBrandBundle URL
                # logger.info(f'url: {patient_access_brand_bundle}')
                response = requests.get(patient_access_brand_bundle)
                # logger.info(f'bundle: {response}')
                response.raise_for_status()
                data = parse_json(response.json())
                # logger.info(f'data: {response.json()}')
                # Display the response
                return render(request, 'config_retriever/config.html', {'data': data})

            else:
                return render(request, 'config_retriever/error.html', {'message': 'No patientAccessBrandBundle found in the config.'})

    else:  # This covers the 'GET' request case.
        form = UriForm()

    return render(request, 'config_retriever/home.html', {'form': form})