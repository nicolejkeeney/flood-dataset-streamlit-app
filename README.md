# flood-dataset-streamlit-app
Streamlit app for demoing flood dataset. See the main project repository [nicolejkeeney/emdat-modis-flood-dataset/](https://github.com/nicolejkeeney/emdat-modis-flood-dataset/) for more information on the methods for generating the dataset. 

## Environment 
The `requirements.txt` file is used by Streamlit to create the environment for the app. Streamlit is finicky with conda environments, and providing it with a simple text file forces Streamlit to build a pip environment, which I've found to have much fewer conflicts in the Streamlit ecosystem (which seems to struggle with geospatial stacks).  

## Licenses

### Code
Licensed under the [MIT License](https://github.com/nicolejkeeney/is2-streamlit-app/blob/main/LICENSE).

### Data
Source of Administrative boundaries: The Global Administrative Unit Layers (GAUL) dataset, implemented by FAO within the CountrySTAT and Agricultural Market Information System (AMIS) projects. This data is used under the [GAUL 2015 Data License](https://developers.google.com/earth-engine/datasets/catalog/DataLicenseGAUL2015.pdf) for non-commercial purposes.
