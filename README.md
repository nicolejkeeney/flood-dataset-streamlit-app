# Global Flood Analysis Dashboard

An interactive Streamlit application for exploring a spatially and temporally disaggregated 21st century flood impact dataset (2000-2024).

**Live App:** [flood-dataset-dashboard.streamlit.app](https://flood-dataset-dashboard.streamlit.app/)
*Note: The app may take 1-2 minutes to load if it hasn't been accessed recently.*

**Dataset & Methods:** [nicolejkeeney/emdat-modis-flood-dataset](https://github.com/nicolejkeeney/emdat-modis-flood-dataset/)
*Full documentation on data processing, satellite analysis, and methodology.*

## Local Development

**Prerequisites:**
- Python 3.x
- Conda (recommended) or pip

**Setup:**

1. Clone the repository:
```bash
git clone https://github.com/nicolejkeeney/flood-dataset-streamlit-app.git
cd flood-dataset-streamlit-app
```

2. Create the conda environment:
```bash
conda env create -f conda_env.yml
conda activate flood-app
```

3. Run the app:
```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`.

**Deployment:** Changes pushed to `main` automatically update the live Streamlit app.

## App Design

### Interface Overview

The app features 5 interactive tabs, each with independent controls for optimal performance:

**Global Annual Trends**
Track annual trends in flood damages, affected populations, and flooded areas from 2000-2024.

![global_annual_trends](https://github.com/nicolejkeeney/flood-dataset-streamlit-app/blob/main/images/global_annual_trends.png "Annual trends in flood damages")

**Map View**
Visualize flood impacts at country, state/province, or UN subregion levels with customizable color scales and statistics.

![flooded_area_map](https://github.com/nicolejkeeney/flood-dataset-streamlit-app/blob/main/images/flooded_area_map.png "Geographic distribution of flooded area")

**Top Regions**
Identify and compare the most impacted regions using customizable statistics (mean, median, max, sum).

**Methods**
Detailed documentation of data processing, satellite analysis, and methodology.

**About**
Project overview and background information.

The app supports multiple flood impact variables including economic damages, population affected, flooded area, flood count, and precipitation metrics. Users can select different aggregation methods (mean, median, maximum, or sum) depending on the variable and analysis needs.

### Performance Optimizations

**Independent Tab Controls**: Each tab maintains its own state using Streamlit's `st.fragment` feature (v1.37.0+). This prevents slow map renders from affecting other visualizations when changing parameters.

**Simplified Geometries**: Administrative boundaries are simplified using `geopandas.simplify()` to significantly reduce map rendering time. See `preprocess_data.py` for implementation details.

## Deployment Notes

The app uses `requirements.txt` for dependency management on Streamlit Cloud rather than a conda environment file. Streamlit Cloud can be finicky with conda environments, particularly for geospatial packages. Using pip requirements has proven more reliable.

For local development, the conda environment (`conda_env.yml`) is provided and recommended. The file is intentionally not named `environment.yml` to prevent Streamlit Cloud from attempting to use it.

## License

**Code:** Licensed under the [MIT License](https://github.com/nicolejkeeney/flood-dataset-streamlit-app/blob/main/LICENSE).

**Data:** Source of Administrative boundaries: The Global Administrative Unit Layers (GAUL) dataset, implemented by FAO within the CountrySTAT and Agricultural Market Information System (AMIS) projects. This data is used under the [GAUL 2015 Data License](https://developers.google.com/earth-engine/datasets/catalog/DataLicenseGAUL2015.pdf) for non-commercial purposes.
