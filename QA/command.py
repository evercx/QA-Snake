#coding:utf8

import aiml
import os
import sys
import json

from QA.QACrawler import baike
from QA.Tools import Html_Tools as QAT
from QA.Tools import TextProcess as T
from QACrawler import search_summary


if __name__ == '__main__':

    responseAnswer = {}
    try:

        input_message = sys.argv[1]
        fileName = sys.argv[2]


        # input_message = "王菲的老公"
        # fileName = "answer.json"

        #初始化jb分词器
        T.jieba_initialize()

        #切换到语料库所在工作目录
        mybot_path = './'
        os.chdir(mybot_path)

        mybot = aiml.Kernel()
        mybot.learn(os.path.split(os.path.realpath(__file__))[0]+"/resources/std-startup.xml")
        mybot.learn(os.path.split(os.path.realpath(__file__))[0] + "/resources/bye.aiml")
        mybot.learn(os.path.split(os.path.realpath(__file__))[0] + "/resources/tools.aiml")
        mybot.learn(os.path.split(os.path.realpath(__file__))[0] + "/resources/bad.aiml")
        mybot.learn(os.path.split(os.path.realpath(__file__))[0] + "/resources/funny.aiml")
        mybot.learn(os.path.split(os.path.realpath(__file__))[0] + "/resources/OrdinaryQuestion.aiml")
        mybot.learn(os.path.split(os.path.realpath(__file__))[0] + "/resources/Common conversation.aiml")
        mybot.respond('Load Doc Snake')


        reply = ''


        message = T.wordSegment(input_message)
        words = T.postag(input_message)


        response = mybot.respond(message)

        print("=======")
        p = os.path.expanduser('~')+'/answer.json'
        print(p)
        print(response)
        print("=======")


        if response == "":
            ans = mybot.respond('找不到答案')
            # print('Eric：' + ans)
            reply = mybot.respond('找不到答案')
            responseAnswer["status"] = "success"
            responseAnswer["answer"] = reply
        # 百科搜索
        elif response[0] == '#':
            # 匹配百科
            if response.__contains__("searchbaike"):
                print("searchbaike")
                print(response)
                res = response.split(':')
                #实体
                entity = str(res[1]).replace(" ","")
                #属性
                attr = str(res[2]).replace(" ","")
                print(entity+'<---->'+attr)

                ans = baike.query(entity, attr)
                # 如果命中答案
                if type(ans) == list:
                    print('Eric：' + QAT.ptranswer(ans,False))
                    reply = QAT.ptranswer(ans,False)
                    responseAnswer["status"] = "success"
                    responseAnswer["answer"] = reply
                    # continue
                elif ans.decode('utf-8').__contains__(u'::找不到'):
                    #百度摘要+Bing摘要
                    print("通用搜索")
                    ans = search_summary.kwquery(input_message)

            # 匹配不到模版，通用查询
            elif response.__contains__("NoMatchingTemplate"):
                print "NoMatchingTemplate"
                ans = search_summary.kwquery(input_message)


            if len(ans) == 0:
                ans = mybot.respond('找不到答案')
                print('Eric：' + ans)
                reply = ans
                responseAnswer["status"] = "success"
                responseAnswer["answer"] = reply

            elif len(ans) >1:
                print("不确定候选答案")
                print('Eric: ')
                for a in ans:
                    print(a)
                    print(a.encode("utf8"))
                    reply += a.encode("utf8")+'\n'
                responseAnswer["status"] = "success"
                responseAnswer["answer"] = reply
            else:
                print('Eric：' + ans[0].encode("utf8"))
                reply = ans[0].encode("utf8")
                responseAnswer["status"] = "success"
                responseAnswer["answer"] = reply

        # 匹配模版
        else:
            print('Eric：' + response)
            reply = response
            responseAnswer["status"] = "success"
            responseAnswer["answer"] = reply

    except Exception as e:
        print(e)
        responseAnswer["status"] = "failed"
        answer = "系统出了点偏差 请重试"
        responseAnswer["answer"] = answer

    finally:
        print(responseAnswer)
        print(responseAnswer["answer"])

        path = os.path.expanduser('~')+'/' + fileName
        with open(path,'w') as json_file:
            json_file.write(json.dumps(responseAnswer,ensure_ascii=False))

