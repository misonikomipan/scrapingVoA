import requests
from bs4 import BeautifulSoup
import markdown
import pdfkit
from path import path_wkhtmltopdf, outDIR

# 上記モジュールのインストールとは別にwkhtmltopdfをインストールする必要があります
# wkhtmltopdfインストール後，pathを通し，path.pyのpath_wkhtmltopdfに文字列として格納してください

URL = "https://learningenglish.voanews.com/"
genre = {
    "health": "z/955",
    "science": "z/1579",
    "art": "z/986",
}

# オプションを指定
options = {
    'page-size': 'A4',
    'minimum-font-size': "20",
    'zoom': "0.1",
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': "UTF-8"
}

for g in genre:
    # URLにリクエストを送り，HTMLを取得
    res = requests.get(URL + genre[g])

    # 取得したHTMLからbeautifulsoupオブジェクトを作成
    soup = BeautifulSoup(res.text, 'html.parser')

    # titleタグの文字列を取得
    titleText = soup.find('title').get_text()
    print(titleText)

    # ページに含まれるリンクを全取得
    links = [
        url.get('href') for url in soup.find_all(
            'a', {'class': 'img-wrap img-wrap--t-spac img-wrap--size-3'})
    ]

    # 各リンクについてタイトルと本文を取得
    for link in links:
        print("")
        # いつもの
        res = requests.get(URL + link)
        soup = BeautifulSoup(res.text, 'html.parser')

        # タイトルの取得
        titleText = soup.find('title').get_text()
        print("title:", titleText)
        print("")

        # ファイル名に使用できない文字は除去
        titleText = titleText.replace(':', ' ').replace('\\', ' ').replace('>', ' ').replace(
            '<', ' ').replace('?', ' ').replace('"', ' ').replace('|', ' ').replace('/', ' ')

        # 本文の取得
        body = soup.find('div', {'class': 'wsw'})

        # 音声限定記事ならスルー
        if body is None:
            continue

        pElements = list(body.stripped_strings)
        for index, value in enumerate(pElements):
            if value == "Pop-out player":
                manuStart = index

            if value.startswith("I’m"):
                manuEnd = index
            if value == 'Words in This Story':
                vocabStart = index
        manuscript = pElements[manuStart + 1:manuEnd + 1]
        manuscript = " ".join(manuscript)
        manuscript = manuscript.replace('.”', '”.')
        manuscript = manuscript.replace('."', '".')
        vocab = pElements[vocabStart:]

        # 本文を文ごとに区切る
        sentences = manuscript.split(". ")

        # 主要単語の取得
        """ vocabraly = set([
            strong.get_text()
            if not (strong.get_text().startswith("_")) else "Words in This Story"
            for strong in soup.find_all('strong')
        ])
        vocabraly.add('Words in This Story')
        vocabraly.remove('Words in This Story')
        print(vocabraly) """

        # mdの作成
        title = "# " + titleText + "\n"
        manuscript = ""
        for sentence in sentences:
            manuscript += "* " + sentence + "." + "\n"
            manuscript += "* " + "\n"
        text = title + manuscript

        md = markdown.Markdown()
        body = md.convert(text)

        # HTML出力用のヘッダを足す
        html = '<html lang="ja"><meta charset="utf-8"><body>'
        html += '<style> body { font-size: 8em; } </style>'
        html += body + '</body></html>'
        # PDF出力
        outPath = outDIR + g + "/" + titleText + ".pdf"
        if "?" in outPath:
            outPath = outPath[:-6] + outPath[-4:]
        print(outPath)
        config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
        pdfkit.from_string(
            html, outPath, configuration=config, options=options)
