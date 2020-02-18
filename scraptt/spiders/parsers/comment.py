# -*- coding: utf-8 -*-
"""PTT COMMENT parsers."""
import re
from collections import defaultdict
from .post import extract_author
def parse_comments(html_pq):
    """
    處理下方回文，將之結構化。
    
    input: PyQuery 物件
    
    Output: 
        如果沒有回文，回傳 dict {
            "comments": [],
            "post_vote": {
                "positive": <int>,
                "negative": <int>,
                "neutral": <int>
            }
        
        }
        
        如果有，則回傳 dict {
            "comments": [
                {
                    "author": <str>,
                    "type": <str: "neg", "pos", "neu">,
                    "content": <str>,
                    "order": <int>
                },
            ]
        }
    """
    comments = []
    post_vote = {
        "pos": 0,
        "neg": 0,
        "neu": 0
    }
    
    type_table = {
        "推": "pos",
        "噓": "neg",
        "→": "neu"
    }
    
    for i, _ in enumerate(html_pq('.push').items()):
        comment_type = _('.push-tag').text()
        
        # 總結
        if comment_type == "推":
            post_vote["pos"] += 1
        elif comment_type == "噓":
            post_vote["neg"] += 1
        elif comment_type == "→":
            post_vote["neu"] += 1
        else:
            continue

        comment = {
            'type': type_table[comment_type],
            'author': extract_author(_('.push-userid').text()),
            'content': _('.push-content').text().lstrip(' :'),
            'order': i+1
        }

        comments.append(comment)


    return {
        "comments": comments,
        "post_vote": post_vote
    }

def comment_counter(comments):
    """
    Function: 計算一篇文章的三種回文的數量
    Input: list of comments <List>
    Output: <DefaultDict>

    Example Input: 
        [
            {"type": "讚", },
            {"type": "讚", },
            {"type": "噓", },
            {"type": "->", },
        ]

    Example Output: 
        {
            "讚": 2,
            "噓": 1,
            "->": 1
        }
    """
    counter = defaultdict(int)
    for comment in comments:
        counter[comment['type']] += 1
    return counter


def split_ip_and_publish_time(ip_and_datetime_str):
    """
    pttbbs.cc 上的回文者的 ip 和 發表日期是放在同一個tag中 (.push-ipdatetime)
    例如: " 111.71.127.174 11/06 22:04"
    所以此函數目的在於將上述的字串分成 ip 與 發表時間

    ### 20191117 更新:
    ### 其實數字不會那麼漂亮 不見得每則回文後面三個資訊都有
    ### 例1: 218.166.4.106 06/22
    ### 例2: 05/30 18:28

    Input: <Str>
    Output: tuple (publish_time, ip)
    """
    ips = re.findall(r'\d{,3}\.\d{,3}\.\d{,3}\.\d{,3}', ip_and_datetime_str)
    if ips:
        # 可能會有多個 ip，只要取最後一個
        ip = ips[-1]
        publish_time = ip_and_datetime_str.replace(ip, '')
    else:
        ip = None
        publish_time = ip_and_datetime_str

    return publish_time, ip
