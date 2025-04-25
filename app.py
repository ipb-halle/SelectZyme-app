from __future__ import annotations

import argparse
import logging
import os
import sys
import types

logging.basicConfig(level=logging.INFO)

import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
from dash import dcc, html
from plotly.graph_objects import Figure

# Monkey patch / patch not required imports (from SelectZyme) as workaround to avoid module not found errors
sys.modules['taxoniq'] = types.SimpleNamespace()

import external.selectzyme.src.pages.dimred as dimred
import external.selectzyme.src.pages.eda as eda
import external.selectzyme.src.pages.mst as mst
import external.selectzyme.src.pages.single_linkage as sl
from external.selectzyme.src.pages.callbacks import register_callbacks
from external.selectzyme.src.selectzyme.visualizer import plot_2d


def import_results(input_dir: str = "data/") -> tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray]:
    """
    Imports and loads results from specified input directory.
    Args:
        input_dir (str): Path to the directory containing the input files. Defaults to "data/".
    Returns:
        tuple: A tuple containing the following:
            - pd.DataFrame: DataFrame loaded from "df.parquet".
            - np.ndarray: Reduced feature matrix loaded from "X_red.npz".
            - np.ndarray: Minimum spanning tree (MST) loaded from "hdbscan_structures.npz".
            - np.ndarray: Linkage matrix loaded from "hdbscan_structures.npz".
    """
    df = pd.read_parquet(os.path.join(input_dir, "df.parquet"))
    X_red = np.load(os.path.join(input_dir, "X_red.npz"))["X_red"]
    structures = np.load(os.path.join(input_dir, "hdbscan_structures.npz"))
    mst = structures["mst"]
    linkage = structures["linkage"]

    return df, X_red, mst, linkage


def main(app, input_dir) -> None:
    legend_attribute = "cluster"
    df, X_red, mst_tree, linkage = import_results(input_dir)

    SANE_LIMIT = 50000  # maximum safe recursion limit
    sys.setrecursionlimit(min(max(df.shape[0], 10000), SANE_LIMIT))

    # Perf: create DimRed and MST plot only once
    fig = plot_2d(df, X_red, legend_attribute=legend_attribute)
    fig_mst = Figure(fig)  # copy required else fig will be modified by mst creation

    # Create page layouts
    dash.register_page(module="eda",
                       name="Explanatory Data Analysis", 
                       layout=eda.layout(df))
    dash.register_page(
        module="dim",
        name="Protein Landscape",
        layout=dimred.layout(df, fig),
    )
    dash.register_page(
        module="mst", name="Connectivity", layout=mst.layout(mst_tree, df, X_red, fig_mst)
    )
    dash.register_page("slc", name="Phylogeny", layout=sl.layout(_linkage=linkage, 
                                                                 df=df, 
                                                                 legend_attribute=legend_attribute))

    # Register callbacks
    register_callbacks(app, df, X_red)


    # App layout with navigation links and page container
    app.layout = dbc.Container(
        [
        # Header Row
        html.Div(
            [
                html.A("← Back to Home", 
                    href="/selectzyme-demo/", 
                    style={
                        "fontSize": "16px",
                        "textDecoration": "none",
                        "color": "white",
                        "marginLeft": "15px"
                    }),

                html.Div(
                    f"Analysis results for {input_dir.split('/')[-1]}",
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
                    }
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Selectzyme Dash app")
    parser.add_argument("-i", 
                        "--input_dir", 
                        type=str, default="data/blast_psi", 
                        help="Path to input directory (default: 'data/blast_psi')")
    args = parser.parse_args()

    app = dash.Dash(
        __name__,
        use_pages=True,
        pages_folder="external/selectzyme/src/pages",
        suppress_callback_exceptions=True,
        external_stylesheets=[dbc.themes.BOOTSTRAP],  # Optional for styling
    )
    
    main(app, args.input_dir)
    # server = app.server  # serve with gunicorn: gunicorn app:server --bind 0.0.0.0:8050 --workers 1
    app.run(host="0.0.0.0", port=8050, debug=False)
