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
import threading
from pathlib import Path
from datetime import date, datetime

import dash_bootstrap_components as dbc

# print('#######',os.getcwd())
# os.chdir(sys._MEIPASS)
# print('#######',os.getcwd())

app = dash.Dash(__name__)

app.title = 'Google Takeout'

app.layout = html.Div([
    html.Div(id='intermediate-value-0', style={'display': 'none'}),
    html.Div(id='intermediate-value-1', style={'display': 'none'}),
    html.Div(id='intermediate-value-2', style={'display': 'none'}),
    dcc.Store(id='whole-search-data-stored',storage_type='memory'),
    html.Div(
        children=[
            html.H1(children='Welcome to our study!', className='title'),
            html.P(children=[
                'We are a group of researchers interested in analysing and finding trends in people\'s search histories. Google Takeout provides ',
                html.Br(),
                'such data for each individual. With the use of this web app we would like to ask you to share your data with us for research purposes.',
                html.Br(),
                'We designed the app in such a way that you can remove the items that you do not wish to share with us from your search history. ',
                html.Br(),
                'We will not ask you for your identity and the process is completely anonymous.'
            ],
                className='proj_desc')
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
    html.Div(
        id='date-picker-container',
        className='date_picker_container'
    ),
    dcc.Loading(
        children=html.Div(id='search-bar', className='search_bar'),
    ),
    html.Div(
        id='black-list-of-words',
        className='black_list_words'
    ),
    html.Div(
        id='proceed-to-step3',
        className='proceed_to_step3'
    ),
    html.P(
        id='unmatched-words-notice',
        className='unmatched_words'
    ),
    html.Div(
        id='step3-text',
        className='step3_block'
    ),
    html.Div(
        id='filtered-queries',
        className='query_list_tbs'
    ),
    html.Div(
        id='proceed-to-step4',
        className='proceed_to_step4'
    ),
    html.Div(
        id='step4-text',
        className='step4_block'
    ),
    html.Div(
        children=[
            dcc.Loading(
                children=[html.Div(id='submission-loading')],
                type='circle'),
            html.P(id='please-wait-txt', className='submission_loading')]
    ),
    dcc.ConfirmDialog(
        id='confirm',
        message='Are you sure you want to submit the data?',
    )
], id='root')


def parse_data(data_json, filename):
    _, content = data_json.split(',')
    decoded = base64.b64decode(content)
    try:
        if filename.endswith('.json'):
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


@app.callback([Output('whole-search-data-stored','data'),
               Output('intermediate-value-0','children'),
               Output('date-picker-container', 'children'),
               Output('search-bar', 'children'),
               Output('black-list-of-words', 'children'),
               Output('proceed-to-step3', 'children')],
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename')])
def enable_filtering(data_json, filename):
    if data_json is not None:
        srch_data = parse_data(data_json, filename)
        if len(srch_data) > 0:
            options = [{'label': e['time'][:10] + ', ' + e['time'][11:16] + ' : ' + e['title'][13:],
                        'value': e['time'][:10] + ', ' + e['time'][11:16] + ' : ' + e['title'][13:] + '_' + str(i)}
                       for i, e in enumerate(srch_data)]

            min_year = int(srch_data[-1]['time'][:4])
            min_month = int(srch_data[-1]['time'][5:7])
            min_day = int(srch_data[-1]['time'][8:10])

            max_year = int(srch_data[0]['time'][:4])
            max_month = int(srch_data[0]['time'][5:7])
            max_day = int(srch_data[0]['time'][8:10])

            return (srch_data,
                    str(srch_data),
                [dcc.DatePickerSingle(
                    id='date-picker-start',
                    clearable=True,
                    day_size=32,
                    number_of_months_shown=1,
                    placeholder='Start date',
                    min_date_allowed=date(min_year, min_month, min_day),
                    max_date_allowed=date(max_year, max_month, max_day),
                    initial_visible_month=date(min_year, min_month, min_day),
                    date=date(min_year, min_month, min_day)),
                    dcc.DatePickerSingle(
                        id='date-picker-end',
                        clearable=True,
                        day_size=32,
                        number_of_months_shown=1,
                        placeholder='End date',
                        min_date_allowed=date(min_year, min_month, min_day),
                        max_date_allowed=date(max_year, max_month, max_day),
                        initial_visible_month=date(max_year, max_month, max_day),
                        date=date(max_year, max_month, max_day)),
                    html.Button('UPDATE DATES', id='update-dates-btn', className='update_dates_btn')],
                dcc.Dropdown(
                    options=options,
                    multi=True,
                    placeholder='Search and select...',
                    clearable=True,
                    id='drop-down'),
                [dcc.Textarea(
                    id='black-list-words-txt',
                    placeholder='Enter your black list of words (please separate them by comma)',
                    style={'width': '50%', 'height': '100px', 'fontSize': '15px'},
                    spellCheck=True
                ), html.Img(src='/assets/tooltip.png',
                            id='tltip1',
                            className='tltip'),
                    dbc.Tooltip('Please note that the queries containing your black-list of words '
                                'will still appear in the search bar but will be removed from the '
                                'final list.',
                                target='tltip1')],
                html.Button(id='to-step3-btn', className='to_step3_btn', children='Proceed to the next step')
            )
        else:
            raise PreventUpdate
    else:
        raise PreventUpdate


@app.callback([Output('search-bar', 'children'),
               Output('intermediate-value-0', 'children'),
               Output('to-step3-btn', 'children'),
               Output('unmatched-words-notice','children'),
               Output('step3-text', 'children'),
               Output('filtered-queries', 'children'),
               Output('proceed-to-step4', 'children'),
               Output('step4-text', 'children')],
              [Input('update-dates-btn', 'n_clicks')],
              [State('date-picker-start', 'date'),
               State('date-picker-end', 'date'),
               State('whole-search-data-stored','data'),
               State('intermediate-value-1','children'),
               State('intermediate-value-0','children')])
def display_date_picker_updates(_, start_date, end_date, whole_searched_data, srch_bar_selected, saved_data):
    if start_date is not None and end_date is not None:

        # print(start_date)
        # print(end_date)

        start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')

        if end_date_dt > start_date_dt:
            srch_date = [e for e in whole_searched_data
                         if start_date_dt <= datetime.strptime(e['time'][:10], '%Y-%m-%d') <= end_date_dt]

            options = [{'label': e['time'][:10] + ', ' + e['time'][11:16] + ' : ' + e['title'][13:],
                        'value': e['time'][:10] + ', ' + e['time'][11:16] + ' : ' + e['title'][13:] + '_' + str(i)}
                        for i, e in enumerate(srch_date)]

            # print(options)

            values = []
            if srch_bar_selected is not None and len(eval(srch_bar_selected))>0:
                ids = sorted(eval(srch_bar_selected))
                # print('IDS',ids)

                saved_data = eval(saved_data)

                k = 0
                thr = saved_data[0]['time'][:10]
                if len(srch_date)>0 and datetime.strptime(srch_date[0]['time'][:10], '%Y-%m-%d')>datetime.strptime(thr, '%Y-%m-%d'):
                    for elem in srch_date:
                        if elem['time'][:10]!=thr:
                            k+=1
                        else:
                            break

                j = 0

                for i, e in enumerate(saved_data):
                    if i == ids[j]:
                        j = min(j+1, len(ids)-1)
                        if start_date_dt <= datetime.strptime(e['time'][:10], '%Y-%m-%d') <= end_date_dt:
                            values.append(e['time'][:10] + ', ' + e['time'][11:16] + ' : ' + e['title'][13:] + '_' + str(k))
                            k+=1
                    else:
                        if start_date_dt <= datetime.strptime(e['time'][:10], '%Y-%m-%d') <= end_date_dt:
                            k+=1

            # print(values)
            return (dcc.Dropdown(
                        options=options,
                        multi=True,
                        placeholder='Search and select...',
                        value=values,
                        clearable=True,
                        id='drop-down'),
                    str(srch_date),
                    'Proceed to the next step',
                    None,
                    None,
                    None,
                    None,
                    None)
        else:
            raise PreventUpdate
    else:
        raise PreventUpdate


@app.callback(Output('intermediate-value-1', 'children'),
              [Input('drop-down', 'value')])
def save_search_bar_removed_queries(queries):
    if queries is not None:
        l1 = []
        for each in queries:
            e = each.rstrip('0123456789')
            l1.append(int(each[len(e):]))
        return str(l1)


@app.callback([Output('display-file-name', 'children'),
               Output('step2-text', 'children')],
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename')])
def display_step2_instructions(data_json, filename):
    if data_json is not None:
        if not filename.endswith('.json'):
            return ('Error! The uploaded file is not json. Please upload correct file.', [])
        srch_data = parse_data(data_json, filename)
        return (str(filename), [
            html.H2(children='Step 2: Filtering of undesirable search history with manual review'),
            html.P(children='Your file is successfully loaded! You can now use the search bar below to '
                            'select the queries that you don\'t wish to share with us. '
                            'The search bar contains all your search queries (in total ' + str(
                len(srch_data)) + ') sorted by date in descending order. '
                                  'You can manually scroll through the queries and select the ones you want to remove. '
                                  'In addition, the search bar allows you to type words/phrases (e.g. specific dates, keywords) and '
                                  'find the matching queries. Furthermore, you have the option to type your \'black list of words\' (see the box provided '
                                  'under the search bar) to remove all queries containing these words right away. '
                                  'Lastly, if for whatever reason you want to review and share only part of your search history data '
                                  'you can update the date range using the datepickers provided below (default range covers your whole search history).')
        ])
    else:
        raise PreventUpdate


@app.callback([Output('step3-text', 'children'),
               Output('filtered-queries', 'children'),
               Output('intermediate-value-2', 'children'),
               Output('to-step3-btn', 'children'),
               Output('proceed-to-step4', 'children'),
               Output('unmatched-words-notice', 'children')],
              [Input('to-step3-btn', 'n_clicks')],
              [State('intermediate-value-1', 'children'),
               State('black-list-words-txt', 'value'),
               State('intermediate-value-0','children'),
               State('whole-search-data-stored','data')])
def display_step3(n_clicks, queries_tbr, black_list_text, data, whole_searched_data):
    if n_clicks is not None:

        srch_data = eval(data)
        if len(srch_data)>0:
            indices = []
            queries_tbs = [(e['time'][:10] + ', ' + e['time'][11:16] + ' : ' + e['title'][13:] + '\n')
                           for e in srch_data]
            queries_tbs_dlc = queries_tbs.copy()

            if queries_tbr is not None:
                queries_tbr = eval(queries_tbr)
                indices += queries_tbr.copy()
                if len(queries_tbr) > 0:
                    queries_tbs = [e for i, e in enumerate(queries_tbs) if i not in queries_tbr]

            matched = set()
            unmatched = set()
            if black_list_text is not None:
                bl = set([e.strip().lower() for e in black_list_text.split(',') if e.strip().lower()])
                if len(bl) > 0:
                    for w in bl:
                        for q in queries_tbs:
                            if w in [e.strip('!"#$%&\'(),./:;<=>?@[\]^_`{|}~').lower() for e in q[20:-1].split(' ')]:
                                matched.add(w)
                                break

                    unmatched = bl - matched
                    queries_tbs = [q for q in queries_tbs
                                   if not any(
                            i in bl for i in
                            [e.strip('!"#$%&\'(),./:;<=>?@[\]^_`{|}~').lower() for e in q[20:-1].split(' ')])]
                    l = [j for j, q in enumerate(queries_tbs_dlc)
                         if any(
                            i in bl for i in
                            [e.strip('!"#$%&\'(),./:;<=>?@[\]^_`{|}~').lower() for e in q[20:-1].split(' ')])]
                    indices += l

            queries_tbs[-1] = queries_tbs[-1][:-1]
            n_removed = len(whole_searched_data) - len(queries_tbs)

            text = ''
            if len(unmatched) > 0:
                text = 'The word(s) {' + ",".join(list(unmatched)) + '} did not match any query.'

            return (
                [
                    html.H2(children='Step 3: Reviewing the list of queries to be submitted'),
                    dcc.Markdown('''Below is the filtered list of your queries after your manual review. In total, **''' +
                                 str(n_removed) + '''** queries have been removed resulting in **''' +  str(len(queries_tbs)) +
                                 '''** out of the original **''' + str(len(whole_searched_data)) + '''** queries. ''' +
                                 '''If you would like to remove some more queries, you can use the tools provided ''' +
                                 '''in Step 2 and then click on the "Update" button to see the new updated list of your queries.''')
                ],
                dcc.Textarea(
                    value=''.join(queries_tbs),
                    style={'width': '100%', 'height': '300px', 'fontSize': '15px'},
                    disabled=True,
                    id='queries-tbs-txtarea'
                ),
                str(list(set(indices))),
                'Update',
                html.Button(id='to-step4-btn', className='to_step4_btn', children='I am happy with my list'),
                text
            )
        else:
            pass # TODO: say that no data is selected
    else:
        raise PreventUpdate


@app.callback(Output('step4-text', 'children'),
              [Input('to-step4-btn', 'n_clicks')],
              [State('to-step4-btn', 'n_clicks')])
def display_step4(n_clicks, _):
    if n_clicks is not None:
        return [
            html.H2(children='Step 4: Submitting the file'),
            html.P(
                children='In this step, the list of selected queries and corresponding metadata will be uploaded to our server. '
                         'When you are done reviewing your search history and are comfortable to share it with us, please click the button below to confirm.'),
            html.Button(id='submit-btn',
                        children='I have reviewed my search history and I am ready to submit')
        ]
    else:
        raise PreventUpdate


@app.callback(Output('confirm', 'displayed'),
              [Input('submit-btn', 'n_clicks')],
              [State('submit-btn', 'n_clicks')])
def display_confirm(n_clicks, _):
    if n_clicks:
        return True
    raise PreventUpdate


@app.callback([Output('root', 'children'),
               Output('submission-loading', 'children'),
               Output('please-wait-txt', 'children')],
              [Input('confirm', 'submit_n_clicks')],
              [State('intermediate-value-2', 'children'),
               State('intermediate-value-0', 'children')])
def submit_reviewed_data(n_clicks, queries_tbr, data):
    if n_clicks is not None:
        srch_data = eval(data)
        if queries_tbr is not None:
            queries_tbr = eval(queries_tbr)
            final_data = [e for i, e in enumerate(srch_data) if i not in queries_tbr]
        else:
            final_data = srch_data

        r = requests.post('http://51.158.119.80:8080/', json=final_data)
        if r.text == 'successful':
            download_folder_path = str(os.path.join(Path.home(), "Downloads"))
            Path(download_folder_path).mkdir(parents=True, exist_ok=True)
            save_path = str(os.path.join(download_folder_path, "submitted_data.json"))
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(final_data, f, ensure_ascii=False, indent=4)

            return (html.Div(children=[html.Img(src='/assets/submission_successful.png'),
                                       html.P(['Thank you!',
                                               html.Br(),
                                               'The file has been successfully uploaded and saved to the downloads folder for your record.',
                                               ],
                                              className='submitted')], className='submission_block'), [], [])
        else:
            print(r.status_code)
            print(r.text)
            return (html.Div(children=[html.Img(src='/assets/smth_went_wrong.png'),
                                       html.P(['Oops!',
                                               html.Br(),
                                               'Something went wrong. Please try again.'],
                                              className='submitted')], className='submission_block'), [], [])
    else:
        raise PreventUpdate


if __name__ == '__main__':
    threading.Timer(1.25, lambda: webbrowser.open('http://127.0.0.1:7683/')).start()
    app.run_server(port=7683)