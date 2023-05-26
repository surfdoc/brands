# Django Reference Application for the HL7 Connectathon

This is a Django reference application built for the HL7 Connectathon, specifically for the event on May 31, 2023. The application aims to demonstrate the integration of FHIR brand resources and CHSS backend.

## Features

- Accepts a base URI from the user as input.
- Retrieves the `patientAccessBrandBundle` URL from the `.well-known/smart-configuration` endpoint.
- Fetches the FHIR bundle from the provided URL.
- Parses the FHIR bundle and displays the necessary data in the user interface.
- Allows users to add a source with logo and brand information to the CHSS backend.

## Setup and Installation

To set up and run the Django reference application, follow these steps:

1. Clone the repository:

2. Install the required dependencies:

3. Configure the Django project by updating the necessary settings such as database connection and security.

4. Run the database migrations:

5. Start the development server:

6. Access the application in your web browser at `http://localhost:8000` (or another specified port).

## Usage

1. Open the application in your web browser.

2. Enter the base URI provided by the user in the designated input field.

3. Click the "Retrieve Data" button to initiate the retrieval of the `patientAccessBrandBundle` URL from the `.well-known/smart-configuration` endpoint.

4. The application will fetch the FHIR bundle from the retrieved URL and parse the necessary data.

5. The parsed data, including logo and brand information, will be displayed in the user interface.

6. Users can utilize the provided data to add a source with logo and brand information to the CHSS backend.

## Contributing

We welcome contributions to enhance the functionality and features of this Django reference application. If you would like to contribute, please follow these steps:

1. Fork the repository.

2. Create a new branch for your feature or bug fix:

3. Commit your changes and push to the new branch:

4. Submit a pull request, and we will review your changes.

Please ensure that your contributions adhere to the coding standards, include necessary tests, and provide a detailed description of the changes.

## License

This Django reference application is released under the [MIT License](LICENSE).
