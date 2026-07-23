from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings

from .models import UserProfile
from .models import BlogArticle

from .forms import UserProfileForm

from datetime import date

import trafilatura

from openai import OpenAI
import requests


client = OpenAI(
    api_key=settings.OPENAI_API_KEY
)

def home(request):

    if request.user.is_authenticated:
        return render(request, 'mypage.html')

    return render(request, 'top.html')

@login_required
def mypage(request):

    return render(request, 'mypage.html')

####################################################
# 設定画面
####################################################

@login_required
def blog_settings(request):

    profile, created = UserProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        form = UserProfileForm(
            request.POST,
            instance=profile
        )

        if form.is_valid():

            form.save()

            return redirect("/blog/")

    else:

        form = UserProfileForm(
            instance=profile
        )

    return render(

        request,

        "blog_settings.html",

        {

            "form": form

        }

    )


####################################################
# RSS取得
####################################################

def get_news(keyword):

    url = "https://newsapi.org/v2/everything"

    params = {

        "q": keyword,
        "language": "jp",
        "sortBy": "publishedAt",
        "pageSize": 5,
        "apiKey": settings.NEWS_API_KEY,

    }

    response = requests.get(url, params=params, timeout=15)

    data = response.json()

    news = []

    for article in data.get("articles", []):

        news.append({

            "title": article.get("title", ""),

            "description": article.get("description", ""),

            "link": article.get("url", ""),

            "published": article.get("publishedAt", "")

        })

    return news


####################################################
# URL・タイトル重複削除
####################################################

def remove_duplicate_news(news):

    result = []

    title_set = set()

    url_set = set()

    for item in news:

        title = item["title"].strip()

        url = item["link"].strip()

        if title in title_set:
            continue

        if url in url_set:
            continue

        title_set.add(title)

        url_set.add(url)

        result.append(item)

    return result


####################################################
# 本文取得
####################################################
def get_article_text(url):

    try:

        downloaded = trafilatura.fetch_url(url)

        if downloaded is None:

            return ""

        text = trafilatura.extract(

            downloaded,

            include_comments=False,

            include_tables=False

        )

        if text is None:

            return ""

        text = text.strip()

        if len(text) < 300:

            return ""

        return text[:1000]

    except Exception as e:

        print(e)

        return ""


####################################################
# キーワードごとに記事収集
####################################################

def collect_news(keyword):

    news = get_news(keyword)

    print("RSS件数:", len(news))

    news = remove_duplicate_news(news)

    articles = []

    for item in news:

        print(item["title"])
        print(item["link"])

        body = get_article_text(item["link"])

        if body == "":

            body = item["description"]

        if body == "":

            continue

        articles.append({

            "keyword": keyword,

            "title": item["title"],

            "url": item["link"],

            "body": body

        })

        if len(articles) >= 2:
            break

    print("取得記事:", len(articles))

    return articles


####################################################
# 全キーワードの記事取得
####################################################

def get_all_articles(profile):

    result = []

    keywords = []

    if profile.keyword1:

        keywords.append(profile.keyword1)

    if profile.keyword2:

        keywords.append(profile.keyword2)

    if profile.keyword3:

        keywords.append(profile.keyword3)

    for keyword in keywords:

        result.extend(

            collect_news(keyword)

        )

    return result

####################################################
# GPTへ渡すプロンプト作成
####################################################

def build_prompt(articles):

    prompt = """
あなたはプロのニュースライターです。

以下の記事を参考にしてください。

同じ内容の記事はまとめてください。

記事をそのままコピーしてはいけません。

読者が5分程度で読めるブログ記事を書いてください。

構成

・タイトル

・今日のニュース

・キーワードごとに見出し

・最後にまとめ

文章量は2000文字程度。

難しい専門用語はできるだけ分かりやすく説明してください。

============================

"""

    for article in articles:

        prompt += f"""

【キーワード】

{article["keyword"]}

【タイトル】

{article["title"]}

【本文】

{article["body"]}

============================

"""

    return prompt


####################################################
# GPT記事生成
####################################################

def generate_blog(articles):

    prompt = build_prompt(articles)

    response = client.chat.completions.create(

        model="gpt-5-mini",

        messages=[

            {

                "role": "system",

                "content":
                "あなたは優秀なニュースブロガーです。"

            },

            {

                "role": "user",

                "content": prompt

            }

        ]

    )

    return response.choices[0].message.content


####################################################
# ブログ画面
####################################################

@login_required
def blog(request):

    today = date.today()

    article = BlogArticle.objects.filter(

        user=request.user,

        date=today

    ).first()

    if article:

        return render(

            request,

            "blog.html",

            {

                "title": article.title,

                "body": article.body

            }

        )

    ################################################
    # 初回のみ生成
    ################################################

    profile = UserProfile.objects.get(

        user=request.user

    )

    articles = get_all_articles(profile)

    if len(articles) == 0:

        return render(

            request,

            "blog.html",

            {

                "title": "ニュースが取得できませんでした",

                "body": "しばらくしてからもう一度お試しください。"

            }

        )

    blog_text = generate_blog(

        articles

    )

    lines = blog_text.split("\n")

    title = ""

    body = ""

    for line in lines:

        if line.strip():

            title = line.strip()

            break

    body = blog_text.replace(

        title,

        "",

        1

    ).strip()

    BlogArticle.objects.create(

        user=request.user,

        date=today,

        title=title,

        body=body

    )

    return render(

        request,

        "blog.html",

        {

            "title": title,

            "body": body

        }

    )

