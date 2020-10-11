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
import webbrowser

# PORT = 8050
# ADDRESS = 127.0.0.1

# print('#######',os.getcwd())
# os.chdir(sys._MEIPASS)
# print('#######',os.getcwd())


# MacOS
chrome_path = 'open -a /Applications/Google\ Chrome.app %s'
webbrowser.get(chrome_path).open('http://127.0.0.1:8050/')

# Windows
# chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'

# Linux
# chrome_path = '/usr/bin/google-chrome %s'


app = dash.Dash(__name__)

app.title = 'Google Takeout'

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
    html.H4(id='to-be-removed-text', className='to_be_removed_header'),
    html.Div(
        id='filtered-queries',
        className='query_checklist'
    ),
    html.Div(
        id='step3-text',
        className='step3_block'
    ),
    dcc.ConfirmDialog(
        id='confirm',
        message='Are you sure you want to submit the data?',
    ),
], id='root')


def parse_data(data_json, filename):
    _, content = data_json.split(',')
    decoded = base64.b64decode(content)
    try:
        if filename.endswith('.json'):
            global searched_data
            data = json.load(io.StringIO(decoded.decode('utf-8')))
            searched_data = [e for e in data if e['title'][0] == 'S']
            return searched_data
        else:
            return []
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])


@app.callback([Output('filtering', 'children'),
               Output('to-be-removed-text', 'children'),
               Output('step3-text', 'children')],
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename')])
def enable_filtering(data_json, filename):
    if data_json is not None:
        srch_data = parse_data(data_json, filename)
        if len(srch_data)>0:
            options = [{'label': e['time'][:10] + ', ' + e['time'][11:16] + ' : ' + e['title'][13:],
                        'value': e['time'][:10] + ', ' + e['time'][11:16] + ' : ' + e['title'][13:] + '_' + str(i)}
                       for i, e in enumerate(srch_data)]

            return (
                dcc.Dropdown(
                    options=options,
                    multi=True,
                    clearable=True,
                    id='drop-down'),
                html.H4('Queries to be removed'),
                [
                    html.H2(children='Step 3: Submitting the file'),
                    html.P(
                        children='In this step, the list of unselected queries and corresponding metadata will be uploaded to our server. '
                                 'When you are done reviewing your search history and are comfortable to share it with us, please click the button below to confirm.'),
                    html.Button(id='submit-btn',
                                children='I have reviewed my search history and I am ready to submit')
                ]
            )
    else:
        raise PreventUpdate


@app.callback([Output('intermediate-value', 'children'),
               Output('filtered-queries', 'children')],
              [Input('drop-down', 'value')])
def display_to_be_removed(queries):
    if queries is not None:
        l1 = []
        l2 = []
        for each in queries:
            e = each.rstrip('0123456789')
            l1.append(int(each[len(e):]))
            l2.append(html.P(e[:-1]))
        return (str(l1), l2)
    else:
        raise PreventUpdate


@app.callback([Output('display-file-name', 'children'),
               Output('step2-text', 'children')],
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename')])
def display_step2_instructions(data_json, filename):
    if data_json is not None:
        if not filename.endswith('.json'):
            return ('Error! The uploaded file is not json. Please upload correct file.',[])
        return (str(filename), [
            html.H2(children='Step 2: Filtering of undesirable search history with manual review'),
            html.P(children='Your file is successfully loaded! You can now use the search bar below to '
                            'select the queries that you don\'t wish to share with us. '
                            'The search bar contains all your search queries sorted by date in descending order. '
                            'You can manually scroll through the queries and select the ones you want to remove. '
                            'In addition, the search bar allows you to type words/phrases (e.g. specific dates, keywords) and '
                            'find the matching queries.')
        ])
    else:
        raise PreventUpdate


@app.callback(Output('confirm', 'displayed'),
              [Input('submit-btn', 'n_clicks')])
def display_confirm(n_clicks):
    return True


@app.callback(Output('root', 'children'),
              [Input('confirm', 'submit_n_clicks')],
              [State('intermediate-value', 'children')])
def submit_reviewed_data(n_clicks, queries_tbr):
    if n_clicks is not None:
        # print('n_clicks: ',n_clicks)
        if queries_tbr is not None:
            queries_tbr = eval(queries_tbr)
            # print(queries_tbr)
            final_data = [e for i, e in enumerate(searched_data) if i not in queries_tbr]
        else:
            final_data = searched_data

        r = requests.post('http://127.0.0.1:5000/', json=final_data)
        if r.text == 'successful':
            with open('filtered_data.json', 'w', encoding='utf-8') as f:
                json.dump(final_data, f, ensure_ascii=False, indent=4)

            return html.Div(children=[html.Img(src='/assets/submission_successful.png'),
                                      html.P(['Thank you!',
                                              html.Br(),
                                              'The file has been successfully uploaded.'],
                                             className='submitted')], className='submission_block')
        else:
            print(r.status_code)
            return html.Div(children=[html.Img(src='/assets/smth_went_wrong.png'),
                                      html.P(['Oops!',
                                              html.Br(),
                                              'Something went wrong. Please try again.'],
                                             className='submitted')], className='submission_block')
    else:
        raise PreventUpdate


if __name__ == '__main__':
    app.run_server()
