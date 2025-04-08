from __future__ import annotations

import logging
import sys
import types

logging.basicConfig(level=logging.INFO)

import dash
import dash_bootstrap_components as dbc
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


def main(app, G, Gsl, df, X_red):
    export_path = "data/"
    legend_attribute = "cluster"

    # Perf: create DimRed and MST plot only once
    fig = plot_2d(df, X_red, legend_attribute=legend_attribute)
    fig_mst = Figure(fig)  # copy required else fig will be modified by mst creation

    # Create page layouts
    dash.register_page("eda", name="Explanatory Data Analysis", layout=eda.layout(df, out_file=export_path + "_eda.html"))
    dash.register_page(
        "dim",
        name="Protein Landscape",
        layout=dimred.layout(df, fig),
    )
    dash.register_page(
        "mst", name="Connectivity", layout=mst.layout(G, df, X_red, fig_mst)
    )
    dash.register_page("slc", name="Phylogeny", layout=sl.layout(G=Gsl, df=df, legend_attribute=legend_attribute, out_file=export_path + "_slc.html"))

    # Register callbacks
    register_callbacks(app, df, X_red)


    # App layout with navigation links and page container
    app.layout = dbc.Container(
        [
            dbc.NavbarSimple(
                brand="Analysis results",
                color="primary",
                dark=True,
            ),
            html.Div(
                [
                    dcc.Store(
                        id="shared-data", data=[], storage_type="memory"
                    ),  # !saves table data from layouts via callbacks defined in the page layouts
                    dbc.Nav(
                        [
                            dbc.NavItem(dbc.NavLink(page["name"], href=page["path"]))
                            for page in dash.page_registry.values()
                        ],
                        pills=True,
                    ),
                    html.Hr(),
                    dash.page_container,  # Displays the content of the current page
                ]
            ),
        ],
        fluid=True,
    )


if __name__ == "__main__":
    import pandas as pd

    app = dash.Dash(
        __name__,
        use_pages=True,
        pages_folder="external/selectzyme/src/pages",
        suppress_callback_exceptions=True,
        external_stylesheets=[dbc.themes.BOOTSTRAP],  # Optional for styling
    )
    server = app.server  # this line is only needed when deployed on a public server
    
    # Manual file parsing
    df = None
    G = None
    Gsl = None
    X_red = None

    main(app, G, Gsl, df, X_red)
    app.run_server(host="127.0.0.1", port=8051, debug=False)
