from __future__ import annotations

import argparse
import logging
import os
import sys
import types
from pathlib import Path

logging.basicConfig(level=logging.INFO)

import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
from dash import dcc, html
from huggingface_hub import hf_hub_download
from plotly.graph_objects import Figure

# Monkey patch / patch not required imports (from SelectZyme) as workaround to avoid module not found errors
sys.modules['taxoniq'] = types.SimpleNamespace()

import selectzyme
import selectzyme.pages.dimred as dimred
import selectzyme.pages.eda as eda
from selectzyme.backend.customizations import set_columns_of_interest
from selectzyme.frontend.mst_plotting import MinimumSpanningTree
from selectzyme.frontend.single_linkage_plotting import create_dendrogram
from selectzyme.frontend.visualizer import plot_2d
from selectzyme.pages.callbacks import register_callbacks

pages_folder = Path(selectzyme.__file__).parent / "pages"

app = dash.Dash(
    __name__,
    use_pages=True,
    pages_folder=str(pages_folder),
    suppress_callback_exceptions=True,
    external_stylesheets=["assets/bootstrap.min.css"],
)

server = app.server  # get the Flask server from dash for gunicorn


def import_results(dataset_name: str) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray]:
    """
    Imports and loads results from a dataset downloaded from Hugging Face Hub.
    Args:
        dataset_name (str): Name of the dataset to fetch from Hugging Face Hub.
    Returns:
        tuple: A tuple containing the following:
            - pd.DataFrame: DataFrame loaded from "df.parquet".
            - np.ndarray: Reduced feature matrix loaded from "x_red_mst_slc.npz".
            - np.ndarray: Minimum spanning tree (MST) loaded from "x_red_mst_slc.npz".
            - np.ndarray: Linkage matrix loaded from "x_red_mst_slc.npz".
    """
    # Download files from Hugging Face Hub
    df_path = hf_hub_download(repo_id="fmoorhof/selectzyme-app-data", 
                              filename=f"{dataset_name}/df.parquet", 
                              repo_type="dataset")
    npz_path = hf_hub_download(repo_id="fmoorhof/selectzyme-app-data", 
                               filename=f"{dataset_name}/x_red_mst_slc.npz", 
                               repo_type="dataset")

    # Load data
    df = pd.read_parquet(df_path)
    adata = np.load(npz_path)
    X_red = adata["X_red"]
    mst = adata["mst"]
    linkage = adata["linkage"]

    return df, X_red, mst, linkage


def main(app, dataset_name) -> None:
    legend_attribute = "cluster"
    df, X_red, mst_tree, linkage = import_results(dataset_name)
    columns = set_columns_of_interest(df.columns)

    SANE_LIMIT = 50000  # maximum safe recursion limit
    sys.setrecursionlimit(min(max(df.shape[0], 10000), SANE_LIMIT))

    # Perf: create DimRed and MST plot only once
    fig = plot_2d(df, X_red, legend_attribute=legend_attribute)
    fig_mst = Figure(fig)  # copy required else fig will be modified by mst creation
    # Create all plots
    mst_obj = MinimumSpanningTree(mst_tree, df, X_red, fig)
    fig_mst = mst_obj.plot_mst_in_dimred_landscape()
    fig_slc = create_dendrogram(Z=linkage, df=df, legend_attribute=legend_attribute)

    # Create page layouts
    dash.register_page(module="eda",
                       name="Explanatory Data Analysis", 
                       layout=eda.layout(df, file_path="assets/eda.html"))
    dash.register_page(
        module="dim",
        path="/",        
        name="Protein Landscape",
        layout=dimred.layout(columns, fig, dropdown=True),
    )
    dash.register_page(module="mst", name="Connectivity", layout=dimred.layout(columns, fig_mst))
    dash.register_page(module="slc", name="Phylogeny", layout=dimred.layout(columns, fig_slc))

    # Register callbacks
    register_callbacks(app, df, X_red)

    # App layout with navigation links and page container
    app.layout = dbc.Container(
        [
        # Header Row
        html.Div(
            [
                html.A("← Back to Home", 
                    href="/selectzyme/", 
                    style={
                        "fontSize": "16px",
                        "textDecoration": "none",
                        "color": "white",
                        "marginLeft": "15px"
                    }),

                html.Div(
                    f"Analysis results: {dataset_name}",
                    style={
                        "fontSize": "20px",
                        "color": "white",
                        "textAlign": "center",
                        "flex": "1"
                    }
                ),

                html.Img(
                    src="assets/ipb-logo.png",
                    style={
                        "height": "40px",
                        "marginRight": "15px"
                    },
                    alt="IPB Logo"
                )
            ],
            style={
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "space-between",
                "backgroundColor": "#0d6efd",  # Bootstrap primary
                "padding": "10px 0",
                "marginBottom": "15px",
                "borderRadius": "5px"
            }
        ),
        # Main content
        html.Div(
            [
                dcc.Store(
                    id="shared-data", data=[], storage_type="memory"
                ),  # !saves table data from layouts via callbacks defined in the page layouts
                dbc.Nav(
                    [
                        dbc.NavItem(dbc.NavLink(page["name"], 
                                                href=page["relative_path"]))  # fix: wrong redirect on server
                        for page in dash.page_registry.values()
                    ],
                    pills=True,
                ),
                html.Hr(),
                dash.page_container,  # causing 404 error blank page
                html.Footer(
                    html.Div(
                        [
                            html.A("Impressum", 
                                   href="https://www.ipb-halle.de/kontakt/impressum", 
                                   target="_blank", style={"marginRight": "15px"}),
                            html.A("Datenschutz (DSGVO)", 
                                   href="https://www.ipb-halle.de/kontakt/datenschutz", 
                                   target="_blank"),
                            html.A("Barrierefreiheit", 
                                   href="https://www.ipb-halle.de/kontakt/barrierefreiheit", 
                                   target="_blank"),                                   
                        ],
                        style={
                            "textAlign": "center",
                            "padding": "20px",
                            "fontSize": "14px",
                            "color": "#666",
                        },
                    )
                )
            ]
        ),
        ],
        fluid=True,
    )

    # Set language attribute for accessibility (screen readers)
    app.index_string = """
    <!DOCTYPE html>
    <html lang="en">
        <head>
            {%metas%}
            <title>{%title%}</title>
            {%favicon%}
            {%css%}
        </head>
        <body>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
    """


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Selectzyme Dash app")
    parser.add_argument("-d", 
                        "--dataset_name", 
                        type=str, default="demo", 
                        help="Name of the dataset to fetch from Hugging Face Hub (default: 'demo')")
    args = parser.parse_args()
    
    main(app, args.dataset_name)
    app.run(host="0.0.0.0", port=8050, debug=False)

else:
    main(app, os.environ.get("SELECTZYME_DATASET", "demo"))  # see docker-compose.yml
    # serve with gunicorn: gunicorn app:server --bind 0.0.0.0:8050 --workers 1  # Dockerfile
