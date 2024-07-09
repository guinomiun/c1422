from flask import Flask, jsonify, request
import pandas as pd
from demographic_filtering import output
from content_filtering import get_recommendations

articles_data = pd.read_csv('articles.csv')
all_articles = articles_data[['url' , 'title' , 'text' , 'lang' , 'total_events']]
liked_articles = []
not_liked_articles = []

app = Flask(__name__)

def assign_val():
    m_data = {
        "url": all_articles.iloc[0,0],
        "title": all_articles.iloc[0,1],
        "text": all_articles.iloc[0,2] or "N/A",
        "lang": all_articles.iloc[0,3],
        "total_events": all_articles.iloc[0,4]/2
    }
    return m_data

@app.route("/get-article")
def get_article():

    article_info = assign_val()
    return jsonify({
        "data": article_info,
        "status": "success"
    })

@app.route("/liked-article")
def liked_article():
    global all_articles
    article_info = assign_val()
    liked_articles.append(article_info)
    all_articles.drop([0], inplace=True)
    all_articles = all_articles.reset_index(drop=True)
    return jsonify({
        "status": "success"
    })

@app.route("/unliked-article")
def unliked_article():
    global all_articles
    article_info = assign_val()
    not_liked_articles.append(article_info)
    all_articles.drop([0], inplace=True)
    all_articles = all_articles.reset_index(drop=True)
    return jsonify({
        "status": "success"
    })

# API para retornar os artigos mais populares.
@app.route("/popular-articles")
def popular_articles():
    
    popular_article_data = []
    for index, row in output.iterrows():
        _p = {#para ser um dicionario depois da variavel tem de ter sinal de igualdade e chave
            "original_title":row['original_title'],
            "poster_link":row['poster_link'],
            "release_date":row['release_date'] or "n/a",
            "duration":row['runtime'],
            "rating":row['weighted_rating']/2, 
        }
        popular_article_data.append(_p)
        
    return jsonify({
        "data": popular_article_data,
        "status": "success"
    })

# API para retornar os 10 principais artigos semelhantes usando o método de filtragem baseado em conteúdo.
@app.route("/recommended-articles")
def recommended_articles():
    
    global liked_article
    column_names = ['original_title','poster_link','release_date','runtime','weighted_raiting']
    all_recommended = pd.DataFrame(columns = column_names)
    for liked_article in liked_article:
        output =  get_recommendations(liked_article["original_title"])
        all_recommended = all_recommended.append(output)
    all_recommended.drop_duplicates(subset=["original_title"], inplace=True)#inplace mostra que tem que acontecer ou seja autoriza
    
    recommended_articles_data = []
    for index, row in all_recommended.iterrows():
        _p = {#para ser um dicionario depois da variavel tem de ter sinal de igualdade e chave
            "original_title":row['original_title'],
            "poster_link":row['poster_link'],
            "release_date":row['release_date'] or "n/a",
            "duration":row['runtime'],
            "rating":row['weighted_rating']/2, 
        }
        recommended_articles_data.append(_p)#append para aparecer qualquer variavel dentro da matrix que pedirmos
    return jsonify({
        "data":recommended_articles_data,
        "status":"sucess"
    })    
if __name__ == "__main__":
    app.run()