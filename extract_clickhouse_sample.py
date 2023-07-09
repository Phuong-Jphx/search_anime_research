import pandas as pd
# import numpy as np
import clickhouse_connect
import sys
import datetime as dt
import os


def main(start, end, STEP, source):
    START_DATE = dt.datetime.strptime(start,'%Y-%m-%d').date()
    END_DATE = dt.datetime.strptime(end,'%Y-%m-%d').date()
    HOST = os.environ.get('clickhouse_stats')
    PORT = os.environ.get('clickhouse_user')
    print (START_DATE, END_DATE)
    name = os.environ.get('CH_USER')
    pw = os.environ.get('CH_PW')
    # print(name, pw)
    client = clickhouse_connect.get_client(HOST=HOST, PORT=PORT, username=name, password = pw, query_limit = 100000)

    path = f'search_data_extraction'
    if not os.path.exists(path):
        os.makedirs(path)
    
    i = 0
    retry = 0
    # data = pd.DataFrame()
    while True:
        from_date = START_DATE + dt.timedelta(days = STEP*i)
        to_date = from_date + dt.timedelta(days = STEP-1)
        if to_date > END_DATE:
            to_date = END_DATE
        if (from_date <= END_DATE) & (to_date <= END_DATE):
            if os.path.isfile(f'{path}\{source}_{from_date}_{to_date}.csv'): 
                print(from_date, to_date, 'already extracted -----> skip')
                i += 1
            else:
                try:
                    print(from_date, to_date, 'start extracting from CH')
                    if source == 'cc':
                        query = f'''
                                --{retry*'-'}
                                SELECT 
                                    reqid,
                                    user_id,
                                    device,
                                    query, 
                                    probabilities,
                                    groupArray(category_id) as category_ids,
                                    groupArray(category_name) as category_name
                                FROM (
                                    SELECT reqid, query,probabilities, categories, if(browser_id !='', browser_id, vid) as user_id, device
                                    FROM coccoc_search.classified
                                        Array join categories
                                    WHERE event_date BETWEEN '{from_date}' AND '{to_date}'
                                    ORDER BY rand()
                                    LIMIT 30000
                                    ) queries
                                LEFT JOIN (
                                        SELECT distinct category_id, lower(category_name) as category_name
                                        FROM dmp.user_categories_name
                                        ) ucn ON ucn.category_id = queries.categories
                                GROUP BY 1,2,3,4,5
                                    '''
                    elif source == 'gg': 
                        query = f'''
                                --{retry*'-'}
                                select 
                                        if(browser_id !='', browser_id, vid) as user_id, 
                                        request,
                                        request_id,
                                        replace(decodeURLComponent(extractURLParameter(url,'q')), '+',' ') as query
                                    from browser_clicks.data
                                    where event_date BETWEEN '2022-01-11' AND '2022-01-11'
                                        AND match(URLDomain,'[\/w]\.google\.com')
                                        AND match(path(request),'/search')
                                        AND match(request, '\?q=')
                                        AND extractURLParameter(url,'tbm') != 'isch'
                                    ORDER BY rand()
                                    LIMIT 2000
                                    '''
                    else:
                        print('this source is not exist')
                    result = client.query(query)
                    t = pd.DataFrame(data = result.result_set, columns = result.column_names)
                    t['date']  = from_date
                    # data = pd.concat([data, t], axis = 0).reset_index(drop=True)
                    i += 1
                    print(f'done loop {i}: ', from_date, to_date)
                    t.to_csv(f'{path}/{source}_{from_date}_{to_date}.csv', index = False)
                except:
                    retry += 1
                    print(f'fail loop {i}: ', from_date, to_date,'----> retry')
                    pass
        else:
            break
    

if __name__ == '__main__':
    start = str(sys.argv[1])
    end = str(sys.argv[2])
    STEP = int(sys.argv[3])
    source = str(sys.argv[4])
    print(start, end, STEP, source)
    main(start, end, STEP, source)