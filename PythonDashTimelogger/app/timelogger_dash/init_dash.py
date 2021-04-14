from logging import exception
import dash, os, datetime, random, time
from dash_core_components.Interval import Interval
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from numpy.core import records
from pandas.core.frame import DataFrame
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
from flask_user import login_required

from app.timelogger_dash.dash_layout import html_layout

HOURS_DEFAULT = 10

# Protect the dash by adding login_requried to the view functions - this forbids unatuthorized users accessing the dash
def protect_dashviews(dashapp):
    for view_func in dashapp.server.view_functions:
        if view_func.startswith(dashapp.config.routes_pathname_prefix):
            dashapp.server.view_functions[view_func] = login_required(
                dashapp.server.view_functions[view_func])


# Get the number of records from the table
def getMaxRecordsFromTable(db):
    table_status = getTableStatus(db)
    if(table_status is not None):
        max_records = table_status['Rows'][4]
    else:
        max_records = 0
    return max_records

# Execute SQL 'SHOW TABLE STATUS;', this provides information about the table name, number of records etc.
# Refer to: https://dev.mysql.com/doc/refman/8.0/en/show-table-status.html
def getTableStatus(db):
    try:
        db_table_status_raw = db.session.execute('SHOW TABLE STATUS;')
    except exc.SQLAlchemyError as e:
        print(e)
        return None
    else:
        return dict(zip(db_table_status_raw.keys(), db_table_status_raw.fetchall()))

def init_dashboard(server, db):
    """Create a Plotly Dash dashboard."""
    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix='/dashapp/',
        external_stylesheets=[
            '/static/reset.css',
            '/static/dist/css/styles.css',
        ]
    )

    dash_app.server.static_folder = 'static'
    dash_app.index_string = html_layout

    protect_dashviews(dash_app)
    
    # Change to read it from config
    engine = create_engine(
        server.config['SQLALCHEMY_DATABASE_URI'],
        pool_recycle=3600, echo=True)

    Session = sessionmaker(bind=engine)

    init_callbacks(dash_app, db)
    max_records = getMaxRecordsFromTable(db)

    # Create Dash Layout
    dash_app.layout = html.Div(children=[
        html.B(id='interval_output'),
        dcc.Interval(id='interval', interval=5000, n_intervals=0),
        html.Div(
        [
            html.B("Select timeframe:"),
            dcc.Dropdown(
                id='time_dropdown',
                options=[
                    {'label': 'Minute', 'value': 'Minute'},
                    {'label': 'Hourly', 'value': 'Hourly'},
                    {'label': 'Daily', 'value': 'Daily'},
                    {'label': 'Monthly', 'value': 'Monthly'},
                    {'label': 'Yearly', 'value': 'Yearly'}
                ],
                value='Minute',
                clearable=False,
                style={'width' : '50%'}
            ),
        ],
    style=dict(display='flex')
    ),
        html.Div(id='controls',
                 style={'display': 'inline-block'},
                 children=[
                    html.Div(children=[
                        html.B(id='text-1',
                               children='Show records from the last:'),
                        dcc.Input(id="input_number",
                                  type='number',
                                  placeholder="input type number",
                                  value='10',
                                  min='1'
                                  ),
                        html.B(children=' hours'),
                    ])

                 ]),
        html.Div(id="number_output"),
        html.B(id='h2_jobs_output', children='Number of jobs: '),
        dcc.Graph(
            id='graph_main'
        ),
        html.Div(children=[
            html.B(id='text-lasthours',
                   children='Show records from last: '),
            dcc.Input(id="input_lasthour",
                      type='number',
                      placeholder="input type number",
                      value='50',
                      min='1'
                      ),
            html.B(id='text-hourslast',
                   children=' hours'),
        ]),

        dash_table.DataTable(
            id='datatable-last-hours',
            columns=[{"name": i, "id": i, } for i in (['jobId', 'currentStatus', 'recordAdded'])]),
        dcc.Graph(
            id='graph-last-hours'
        )]
    )
    return dash_app.server


def init_callbacks(app, db):
    @app.callback(
        Output('h2_jobs_output', 'children'),
        [Input('interval', 'n_intervals')])
    def display_max_jobs(n):
        return 'Number of jobs: ' + str(getMaxRecordsFromTable(db))

    @app.callback(
        Output("datatable-last-hours", "data"),
        Output("graph-last-hours", "figure"),
        [Input('interval', 'n_intervals')],
        [Input('input_lasthour', 'value')])
    def display_data_figure(n, hours):
        recordsLastHours = getRecordsLastHours(hours, db)
        
        return recordsLastHours.to_dict('records'), updateGraphLastHours(recordsLastHours)

    @app.callback(
        Output('interval_output', 'children'),
        Output("graph_main", "figure"),
        Input('time_dropdown', 'value'),
        Input('interval', 'n_intervals'),
        Input("input_number", "value"))
    def display_output(time_dropdown_value, interval_n_intervals, input_number_value):
        return 'Last update: ' + str(getCurrentDateTime()), updateGraph(input_number_value, time_dropdown_value, db)


def getCurrentDateTime():
    dateTimeNow = datetime.datetime.now()
    return '{}-{}-{} {}:{}:{}  '.format(
        dateTimeNow.year,
        dateTimeNow.month,
        dateTimeNow.day,
        dateTimeNow.hour,
        dateTimeNow.minute,
        dateTimeNow.second)


def updateGraphLastHours(dataFrame):
    if(dataFrame.empty):
        return emptyLayout()

    dfg = pd.DataFrame({
        'x': dataFrame['currentStatus'],
        'customdata': dataFrame['jobId'],
        'recordAdded': dataFrame['recordAdded']
    })
    fig = px.bar(dfg, x='x', hover_name='recordAdded')

    return fig


def getRecordsLastHours(hours, db):
    if hours == None or int(hours) <= 0:
        hours = HOURS_DEFAULT
    hours = str(hours)
    result = db.session.execute(
        'SELECT jobId, currentStatus, recordAdded FROM work_tracking.jobs WHERE recordAdded >= DATE_SUB(NOW(),INTERVAL ' + hours + ' HOUR);')
    if result.rowcount == 0:
        df = pd.DataFrame(data=[], columns=[
                          'jobId', 'currentStatus', 'recordAdded'])
    else:
        jobs = np.asarray(result.fetchall())
        df = pd.DataFrame(jobs, columns=result.keys())
    return df

def emptyLayout():
        return {
            "layout": {
                "xaxis": {
                    "visible": False
                },
                "yaxis": {
                    "visible": False
                },
                "annotations": [
                    {
                        "text": "No matching data found",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {
                            "size": 34
                        }
                    }
                ]
            }
        }

def updateGraph(max_records, date_format, db):
    df = getRecordsLastHours(max_records, db)
    if(df.empty):
        return emptyLayout()
    dfg = pd.DataFrame()
    df['rad'] = None
    xLabel = 'x'
    if date_format == 'Minute':
        df['rad'] = df['recordAdded'].dt.strftime("%Y %B %d %H:%M")
        dfg = df.groupby('rad')['rad'].count()
        xLabel = date_format
    elif date_format == 'Hourly':
        df['rad'] = df['recordAdded'].dt.strftime("%Y %B %d %H%p")
        dfg = df.groupby('rad')['rad'].count()
        xLabel = date_format
    elif date_format == 'Daily':
        df['rad'] = df['recordAdded'].dt.strftime("%Y %B %d")
        dfg = df.groupby('rad')['rad'].count()
        xLabel = date_format
    elif date_format == 'Monthly':
        df['rad'] = df['recordAdded'].dt.strftime("%Y %B")
        dfg = df.groupby('rad')['rad'].count()
        xLabel = date_format
    elif date_format == 'Yearly':
        df['rad'] = df['recordAdded'].dt.strftime("%Y")
        dfg = df.groupby('rad')['rad'].count()
        xLabel = date_format

    fig = px.line(dfg, y=dfg, title='Number of jobs')

    fig.data[0].mode = 'lines+markers'
    fig.update_xaxes(rangeslider_visible=True)
    fig.update_layout(uirevision='true', xaxis_title=xLabel,
                      yaxis_title='jobs')

    return fig
