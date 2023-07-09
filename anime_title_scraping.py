from playwright.sync_api import sync_playwright
import pandas as pd
import numpy as np
import sys, os

path = 'anime_title_extraction'
if not os.path.exists(path):
    os.makedirs(path)

def main(domain, type,pages):
    '''
    decide what website and type of popularity (all-time or current monthly top manga) to extract data
    '''
    if (domain == 'anime47.com') & (type == 'all_time'):
        extract47('https://anime47.com/tim-nang-cao/?status=&season=&year=&sort=popular&page=', type, pages)
    elif (domain == 'anime47.com') & (type == 'month'):
        extract47('https://anime47.com/danh-sach/xem-nhieu-trong-thang.html/', type, pages)
    elif (domain == 'animetvn'):
        extract_animetvn('https://animetvn.pro/bang-xep-hang.html?page=',type, pages)
    else:
        print(f'no function to process {domain} with type {type} yet')


def extract47(source, type,pages):
    print(f'start extrating: ',source, ', ', type)
    try:
        final_tasks = pd.read_csv(f'{path}/anime47_tasks_{type}.csv')
    except:
        links = []
        for page_no in range(pages):
            with sync_playwright() as p:
                browser = p.chromium.launch(headless = False, slow_mo = 50)
                page = browser.new_page()
                domain = 'https://anime47.com'
                if type == 'all_time':
                    page.goto(f'{source}{page_no+1}')
                    blocks = page.query_selector_all('//a[@class="movie-item m-block"]')
                else:
                    page.goto(f'{source}{page_no+1}.html')
                    blocks = page.query_selector_all('//div[@class="movie-item m-block"]/a')
                _link = [domain + l.get_attribute('href')[1:] for l in blocks]
                links = links + _link
                print(f'done additional {len(_link)}, total {len(links)} extracted')
                page.wait_for_timeout(2000)
                browser.close()
            
                # break

        final_tasks = pd.DataFrame(links, columns = ['link'])
        final_tasks['link']  = final_tasks['link'].str.strip()
        final_tasks.to_csv(f'{path}/anime47_tasks_{type}.csv', index=False)
    try:
        extraction = pd.read_csv(f'{path}/anime47_data_{type}.csv')
    except:
        extraction = final_tasks.copy()
    for i in ['title1','title2','genre']:
        if i not in extraction.columns:
            extraction[i] = None
    # task_list = final_tasks['link'].to_list()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless = False, slow_mo = 50)
        page = browser.new_page()
        for row in extraction[extraction['title1'].isna()].itertuples():
            link = row.link
            _i = row.Index
            count = _i+1
            try:
                page.goto(link)
                page.wait_for_timeout(2000)
                _titles_1 = page.query_selector('//span[@class="title-1"]')
                extraction.at[_i,'title1'] = _titles_1.text_content() if _titles_1 else ''
                _titles_2 = page.query_selector('//span[@class="title-2"]')
                extraction.at[_i,'title2'] = _titles_2.text_content() if _titles_2 else ''
                _genres = page.query_selector_all('//dd[@class="movie-dd dd-cat"]/a')
                _genres = [cat.text_content().lower().strip() for cat in _genres] if len(_genres) > 0 else []
                extraction.at[_i,'genre'] = _genres
                print(f'done {_titles_1}, total scraped {count}')
            except:
                print(f'skip {link}, total scraped {count}')
            
            # break

            if (count % 50==0)|(count == final_tasks.shape[0]):
                extraction.to_csv(f'{path}/anime47_data_{type}.csv',index=False)
        browser.close()

def extract_animetvn(source,type,pages):
    print(f'start extrating: ',source, ', ', type)
    try:
        final_tasks = pd.read_csv(f'{path}/animetvn_tasks_{type}.csv')
    except:
        links = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless = False, slow_mo = 50)
            page = browser.new_page()
            for page_no in range(pages):
                page.goto(f'{source}{page_no+1}')
                # if type == 'month':
                #     page.wait_for_selector('//div[@id="fbox-button"]')
                #     close_ads = page.query_selector('//div[@id="fbox-button"]')
                #     close_ads.click()
                #     month_tab = page.query_selector('//a[@aria-controls="rank-tab3"]')
                #     month_tab.click()
                page.wait_for_timeout(2000)
                _id = 'global' if type == 'all_time' else 'month'
                blocks = page.query_selector_all(f'//div[@id="list-rank-{_id}"]/ul/li[@class="item"]/a')
                _link = [l.get_attribute('href') for l in blocks]
                links = links + _link
                print(f'done additional {len(_link)}, total {len(links)} extracted')
            browser.close()
            
                # break

        final_tasks = pd.DataFrame(links, columns = ['link'])
        final_tasks['link']  = final_tasks['link'].str.strip()
        final_tasks.to_csv(f'{path}/animetvn_tasks_{type}.csv', index=False)
        # final_tasks.to_csv(f'animetvn_tasks_{type}.csv', mode = 'a',header=False,index=False)
    try:
        extraction = pd.read_csv(f'{path}/animetvn_data_{type}.csv')
    except:
        extraction = final_tasks.copy()
    for i in ['title1','title2','genre']:
        if i not in extraction.columns:
            extraction[i] = None
    with sync_playwright() as p:
        browser = p.chromium.launch(headless = False)
        page = browser.new_page()
        for row in extraction[extraction['title1'].isna()].itertuples():
            link = row.link
            _i = row.Index
            count = _i+1
            try:
                page.goto(link)
                page.wait_for_timeout(1000)
                _titles_1 = page.query_selector('//h2[@class="name-vi"]')
                extraction.at[_i,'title1'] = _titles_1.text_content() if _titles_1 else ''
                _titles_2 = page.query_selector('//h3[@class="name-eng"]')
                extraction.at[_i,'title2'] = _titles_2.text_content() if _titles_2 else ''
                _genres = page.query_selector_all('//li[@class="has-color" and span/text()=" Thể loại: "]/a')
                _genres = [cat.text_content().lower().strip() for cat in _genres] if len(_genres) > 0 else []
                extraction.at[_i,'genre'] = _genres
                print(f'done {_titles_1}, total scraped {count}')
            except:
                print(f'skip {link}, total scraped {count}')
            
            # break

            if (count % 50==0)|(count == final_tasks.shape[0]):
                extraction.to_csv(f'{path}/animetvn_data_{type}.csv',index=False)
        browser.close()

if __name__ == '__main__':
    domain = str(sys.argv[1])
    type = str(sys.argv[2])
    pages = int(sys.argv[3])
    print(domain,type,pages)
    main(domain,type,pages)