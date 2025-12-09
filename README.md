# flood-dataset-streamlit-app
Streamlit app for demoing flood dataset. See the main project repository [nicolejkeeney/emdat-modis-flood-dataset/](https://github.com/nicolejkeeney/emdat-modis-flood-dataset/) for more information on the methods for generating the dataset. 

## Layout & Design Decisions 
The app has 5 tabs with different visualizations or informative text. Each tab is controlled by its own set of options, such that **changing the data options in one tab doesn't impact the the visualizations in the other tabs**. I have found this to be a huge improvement for the speed of the app, because generating map visualizations with Streamlit is quite slow. This is controlled by `st.fragment`, a new feature in Streamlit version 1.37.0 (documentation [here](https://docs.streamlit.io/1.37.0/develop/api-reference/execution-flow/st.fragment#stexperimental_fragment)). 

Additionally, I **simplified the geometries** of the geospatial boundaries in order to speed up the map visualization using `geopandas.simplify()` (documentation [here](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoSeries.simplify.html)]. You'll see this in the data processing script, `data_processing.py`.  

## Streamlit Environment Shenanigans 
The `requirements.txt` file is used by Streamlit to create the environment for the app. If you have an `environment.yml` file in your repository, Streamlit will default to building the conda environment. Streamlit is finicky with conda environments, and providing it with a simple text file forces Streamlit to build a pip environment, which I've found to have much fewer conflicts in the Streamlit ecosystem (which seems to struggle with geospatial stacks). I do incude a conda environment, which I used for local development, called `conda_env.yml`. As long as it's not named "`environment.yml`", Streamlit will ignore it, and default to using the `requirements.txt` file. 

## Licenses

### Code
Licensed under the [MIT License](https://github.com/nicolejkeeney/is2-streamlit-app/blob/main/LICENSE).

### Data
Source of Administrative boundaries: The Global Administrative Unit Layers (GAUL) dataset, implemented by FAO within the CountrySTAT and Agricultural Market Information System (AMIS) projects. This data is used under the [GAUL 2015 Data License](https://developers.google.com/earth-engine/datasets/catalog/DataLicenseGAUL2015.pdf) for non-commercial purposes.
