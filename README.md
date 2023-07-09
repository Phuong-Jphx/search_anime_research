# search_anime_research
## Problem statement
Hypothesis: Search users love to use our search engine to find and watch manga, anime. We need to develop a function to support this group of user.

## Sample extraction
- Date: 2022-11-01 to 2022-11-20
- Type: search queries

## How-to
- Find popular anime sites
- Crawl top popular anime form sites (popular all time + popular of month)
- Matching anime name with search queries and giving a matching scoring, the higher the score, the more likely that query is a anime title
- Choosing a threshold for anime definition
- Estimate the number of anime queries and their genres accordingly

## Result
- The number of queries about anime are considerable and worth developing a function
- For default mode, it is best to make it about action and comedy
- Chinese anime is developing to be its own branch and can be consider separate for future development
> Query would be classified with a flag: 0 - not anime query, 1 - anime query
![image](https://github.com/Phuong-Jphx/search_anime_research/assets/79634273/7b910b4a-0ac7-4189-b796-2a6def0ef47c)
> Number of query anime by genrest combination
![image](https://github.com/Phuong-Jphx/search_anime_research/assets/79634273/6969915f-4ec7-4c2c-b4b9-c69f06075c06)
> Number of query by singular genre
![image](https://github.com/Phuong-Jphx/search_anime_research/assets/79634273/e5c69647-7708-4542-9b94-319063ddc5f2)

