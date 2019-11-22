簡易ptt爬蟲

- STEP 1: clone到本機
```
$ git clone 
```

- STEP 2: 進到 scraptt/ 資料夾
```
$ cd scraptt
```

- STEP 3: 安裝必要套件

```
$ pip3 install -r requirements.txt
```

- STEP 4: 修改 scraptt/settings.py 中最下方的 DATA_DIR

```
DATA_DIR = "data"  # 爬下來的網頁所要儲存的資料夾名稱，預設為"data"
```

- STEP 5: 在 terminal 中執行
```
$ scrapy crawl ptt_article -a boards=<輸入版名英文> -a index_from=<起始index值> -a index_to=<目標index值> 
```

- STEP 6: log 檔案在 scraptt.log
