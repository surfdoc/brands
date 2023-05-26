# retrieve_config/views.py

from django.shortcuts import render
from .forms import UriForm
import requests
import logging
logger = logging.getLogger('django')
import base64

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
                response.raise_for_status()
                patient_data = response.json()

                # Prepare entries for display
                entries = patient_data.get('entry', [])

                for entry in entries:
                    resource = entry.get('resource', {})
                    extension = resource.get('extension', [])

                    for ext in extension:
                        if ext.get('url') == "http://fhir.org/argonaut/StructureDefinition/brand-logo":
                            # Get the base64 string, remove the prefix if necessary
                            base64_str = ext.get('valueUrl', '').replace('data:image/svg+xml;base64,', '')
                            
                            try:
                                # Decode the base64 string and re-encode it for HTML
                                decoded_img = base64.b64decode(base64_str).decode('utf-8')
                                ext['valueUrl'] = 'data:image/svg+xml;base64,' + base64.b64encode(decoded_img.encode()).decode('utf-8')
                            except:
                                # Image could not be decoded and re-encoded, leave as is
                                pass
                # logger.info(f'patient_data: {patient_data}')
                # Display the response
                return render(request, 'config_retriever/config.html', {'entries': entries})

            else:
                return render(request, 'config_retriever/error.html', {'message': 'No patientAccessBrandBundle found in the config.'})

    else:  # This covers the 'GET' request case.
        form = UriForm()

    return render(request, 'config_retriever/home.html', {'form': form})
