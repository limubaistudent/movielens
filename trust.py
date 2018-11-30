# -*- coding:utf8 -*-
import numpy as np
import pymysql
import random
import math


class Trust(object):
    diff = 0
    top = 20
    filmSet = 10
    count = 0
    tag = 0
    hit = 0
    def __init__(self,size):
        self.size = size
        self.db = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='limubai1991', db='movielens',
                                 charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.db.cursor()
        self.trust = np.zeros(shape=(size, size))
        self.average = {}
        self.userScoreInfoTrain = {}
        self.userScoreInfoTest = {}
        self.sqrt = 0
        self.ab = 0

    def run(self):
        for user in range(1, self.size+1):
            self.getUserInfo(user)

        #计算得到的其他用户信任度
        for userA in range(1, self.size+1):
            for userB in range(userA+1, self.size+1):
                keys = self.userScoreInfoTrain[userA].keys() & self.userScoreInfoTrain[userB].keys()
                self.getTrust(userA, userB, keys)

        #预测打分
        print("开始预测：")
        for userA in self.userScoreInfoTest:
            #如果有电影说明这个用户有测试数据，对这个用户进行预测
            #1.得到最相近的10个用户
            #2.10个用户对这个项目评分求平均值
            print(userA)
            if self.userScoreInfoTest[userA] != {}:
                userSet = self.getTopUser(userA)
                userStr = ','.join('%s' % id for id in userSet)
                for movieId in self.userScoreInfoTest[userA]:
                    averageA = self.average[userA]
                    scoreA = self.userScoreInfoTest[userA][movieId]
                    sql = "select * from ratings where `movie_id`= %d and `user_id` in (%s)" % (int(movieId), userStr)
                    movieSql = self.cursor.execute(sql)
                    infos = self.cursor.fetchall()
                    size = len(infos)
                    if size != 0:
                        self.hit += size
                        allScore = 0
                        for info in infos:
                            userB = info['user_id']
                            allScore += info['movie_score'] + averageA - self.average[int(userB)]
                        predictScore = allScore / size
                        self.sqrt += (predictScore - scoreA)*(predictScore - scoreA)
                        self.ab += abs(predictScore - scoreA)

        print(math.sqrt(self.sqrt/self.count), self.ab/self.count, self.hit/self.count)

    def getUserInfo(self, userId):
        trainId = {}
        testId = {}
        score = 0
        sql = "select `movie_id`,`movie_score` from ratings where user_id = %d" % (userId)
        movieSql = self.cursor.execute(sql)
        infos = self.cursor.fetchall()
        for row in infos:
            if random.random() < 0.8:
                score += row['movie_score']
                trainId[row['movie_id']] = row['movie_score']
            else:
                testId[row['movie_id']] = row['movie_score']
                self.count += 1
        self.average[userId] = score / len(trainId)
        self.userScoreInfoTrain[userId] = trainId
        self.userScoreInfoTest[userId] = testId


    def getTrust(self, userA, userB, keys):
        if keys:
            diff = self.average[userA] - self.average[userB]
            TrustAB = 0
            for movieId in keys:
                AScore = self.userScoreInfoTrain[userA][movieId]
                BScore = self.userScoreInfoTrain[userB][movieId]
                BPredict = AScore - diff
                TrustAB += 1 - abs(BPredict - BScore)/4
            TrustAB = TrustAB / len(keys)
            self.trust[userA-1][userB-1] = TrustAB
            self.trust[userB-1][userA-1] = TrustAB


    def getTopUser(self,user):
        userTrust = self.trust[user - 1].tolist()
        temp = []
        Inf = 0
        for i in range(self.top):
            temp.append(userTrust.index(max(userTrust)) + 1)
            userTrust[userTrust.index(max(userTrust))] = Inf
        return temp

if __name__ == '__main__':
    trust = Trust(610)
    trust.run()

