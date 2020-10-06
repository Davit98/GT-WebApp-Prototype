import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import json
import io
import base64
import requests
import os
import sys

# print('#######',os.getcwd())
# os.chdir(sys._MEIPASS)
# print('#######',os.getcwd())

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div(id='intermediate-value', style={'display': 'none'}),
    html.Div(
        children=[
            html.H1(children='Welcome to our study!', className='title'),
            html.P(children='Information about the process', className='proj_desc')
        ],
        className='welcome_block'
    ),
    html.Div(
        children=[
            html.H2(children='Step 1: Selecting the file'),
            html.P(children='Please upload the json file containing your Google search history.'),
            dcc.Upload(
                id='upload-data',
                children=html.Button(children='Upload File')
            ),
            html.P(id='display-file-name', style={'margin-top': '3px', 'color': 'green'})
        ],
        className='step1_block'
    ),
    html.Div(
        id='step2-text',
        className='step2_block'
    ),
    dcc.Loading(
        children=html.Div(id='filtering', className='search_bar'),
    ),
    html.Div(
        id='filtered-queries',
        className='query_checklist'
    ),
    html.Div(
        id='step3-text',
        className='step3_block'
    )
], id='root')


def parse_data(data_json, filename):
    type, content = data_json.split(',')
    decoded = base64.b64decode(content)
    try:
        if filename.endswith('.json'):
            global data
            data = json.load(io.StringIO(decoded.decode('utf-8')))
            searched_data = [e['title'][13:] for e in data if e['title'][0] == 'S']
            vocab = set(sub_e for e in searched_data for sub_e in e.split(' ') if len(sub_e) > 1)
            return sorted(vocab)
        else:
            pass  # TODO: Show that the uploaded file is not json
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])


@app.callback([Output('filtering', 'children'),
               Output('filtered-queries', 'children'),
               Output('step3-text', 'children')],
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename')])
def enable_filtering(data_json, filename):
    if data_json is not None:
        vocab = parse_data(data_json, filename)
        options_1 = [{'label': word, 'value': word} for word in vocab]
        options_2 = [{'label': e['time'][:10] + ', ' + e['time'][11:16] + ' : ' + e['title'][13:], 'value': str(i)}
                     for i, e in enumerate(data) if e['title'][0] == 'S']
        return (
            dcc.Dropdown(
                options=options_1,
                multi=True,
                id='drop-down'),
            dcc.Checklist(
                id='check-list',
                options=options_2,
                style={'fontSize': '17px'},
                labelStyle=dict(display='block')
            ),
            [
                html.H2(children='Step 3: Uploading the file'),
                html.P(
                    children='In this step, the list of issued search terms and the corresponding dates will be uploaded to our server. '
                             'When you are ready, please confirm that you have reviewed the search terms that you are comfortable sharing with us.'),
                html.Button(id='submit-btn',
                            children='I have reviewed my search queries and I am ready to proceed')
            ]
        )
    else:
        raise PreventUpdate


@app.callback([Output('filtered-queries', 'children'),
               Output('step3-text', 'children')],
              [Input('drop-down', 'value')],
              [State('intermediate-value', 'children')])
def display_queries(words, val):
    if words is not None:
        # print(words)
        # print(len(data))

        if len(words) == 0:
            options = [{'label': e['time'][:10] + ', ' + e['time'][11:16] + ' : ' + e['title'][13:], 'value': str(i)}
                       for i, e in enumerate(data) if e['title'][0] == 'S']
            return (dcc.Checklist(
                id='check-list',
                options=options,
                style={'fontSize': '17px'},
                labelStyle=dict(display='block')
            ), [
                        html.H2(children='Step 3: Uploading the file'),
                        html.P(
                            children='In this step, the list of issued search terms and the corresponding dates will be uploaded to our server. '
                                     'When you are ready, please confirm that you have reviewed the search terms that you are comfortable sharing with us.'),
                        html.Button(id='submit-btn',
                                    children='I have reviewed my search queries and I am ready to proceed')
                    ])

        else:
            val_2 = []
            if val is not None:
                val = eval(val)
                print('val:', val)
                for w in val:
                    w2 = w.rstrip('0123456789')
                    if w2[:-1] in words:
                        val_2.append(w)

            print('***', val_2)
            print('words', words)

            options = [
                {'label': e['time'][:10] + ', ' + e['time'][11:16] + ' : ' + e['title'][13:], 'value': w + '_' + str(i)}
                for w in words for i, e in enumerate(data) if e['title'][0] == 'S' and w in e['title'][13:].split(' ')]
            # print(options)
            return (dcc.Checklist(
                id='check-list',
                options=options,
                style={'fontSize': '17px'},
                value=val_2,
                labelStyle=dict(display='block')
            ), [
                        html.H2(children='Step 3: Uploading the file'),
                        html.P(
                            children='In this step, the list of issued search terms and the corresponding dates will be uploaded to our server. '
                                     'When you are ready, please confirm that you have reviewed the search terms that you are comfortable sharing with us.'),
                        html.Button(id='submit-btn',
                                    children='I have reviewed my search queries and I am ready to proceed')
                    ])
    else:
        raise PreventUpdate


@app.callback(Output('intermediate-value', 'children'),
              [Input('check-list', 'value')])
def save_checked_values(values):
    if values is not None:
        print('###', values)
        return str(values)


@app.callback([Output('display-file-name', 'children'),
               Output('step2-text', 'children')],
              [Input('upload-data', 'contents')],  # TODO: remove this if possible
              [State('upload-data', 'filename')])
def display_step2_instructions(data_json, filename):
    if data_json is not None:
        return (str(filename), [
            html.H2(children='Step 2: Filtering of undesirable search history with manual review'),
            html.P(children='The file is successfully loaded! You can now '
                            'select the queries that you don\'t wish to share with us using the search bar. '
                            'The search bar contains all unique words of your search queries.')
        ])
    else:
        raise PreventUpdate


@app.callback(Output('root', 'children'),
              [Input('submit-btn', 'n_clicks')],
              [State('intermediate-value', 'children')])
def submit_reviewed_data(n_clicks, checked_queries):
    if checked_queries is not None:
        checked_queries = eval(checked_queries)
        l = []
        for e in checked_queries:
            w = e.rstrip('0123456789')
            ind = int(e[len(w):])
            l.append(ind)
        print(l)
        final_data = [e for i, e in enumerate(data) if (e['title'][0] == 'S' and i not in l)]
    else:
        final_data = [e for e in data if e['title'][0] == 'S']

    r = requests.post('http://127.0.0.1:5000/', json=final_data)
    if r.text=='successful':
        with open('filtered_data.json', 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)

        return html.Div(children=[html.Img(src='/assets/submission_successful.png'),
                                  html.P(['Thank you!',
                                          html.Br(),
                                          'The file has been successfully uploaded.'],
                                         className='submitted')], className='submission_block')
    else:
        print(r.status_code)
        pass # TODO: Display error message


if __name__ == '__main__':
    app.run_server()
