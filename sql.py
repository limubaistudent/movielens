# -*- coding:utf8 -*-
import pymysql

fileRatings = r"D:\\study\\my\\ml-latest-small\\ratings.csv"
fileMovies = r"D:\\study\\my\\ml-latest-small\\movies.csv"
N = 50
movieDict = {}

ratingFile = open(fileRatings)
next(ratingFile)
db = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='limubai1991', db='movielens',
                          charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
cursor = db.cursor()
for line in ratingFile:
    userId = line.strip().split(',')[0]
    movieId = line.strip().split(',')[1]
    movieScore = line.split(',')[2]
    timestamp = line.split(',')[3].replace("\n", "")
    sql = "INSERT INTO ratings" + " (user_id,movie_id,movie_score,scoretime)" + " VALUES(%s,%s,%s,%s)"
    cursor.execute(sql, (userId, movieId, movieScore, timestamp))
    db.commit()

ratingFile.close()



