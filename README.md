# XPOScope

## 项目构建说明
1 将checkpoint预处理文件放置dynamicExerciser目录下

2 在dynamicExerciser/data目录下创建 evaluate_classifier文件夹，page_text文件夹，picCache文件夹，screenshots文件夹（screenshots下需要有alipay,baidu,wechat三个子文件夹）

3 在XPOScope根目录下创建MiniAppLog文件夹



## 运行注意事项

根据不同手机需要进行一定的定制化

1. 小程序的启动操作

   dynamicExerciser/mini_app_auto.py 中start_wx_mini_app(self)函数需要进行定制化（其他平台先不管）

   clear_background_apps()需要根据不同机型定制，主要就是平常的请后台操作

2. 配置文件的设置

   主要关注config.py文件中MINI_APP_TEST_TIME以及MINI_APP_TYPE以及mini_app_start_num()函数

   MINI_APP_TEST_TIME:每个应用运行的时间

   MINI_APP_TYPE:30个google类别中的任意一个，你要跑那个类别，就进行设置即可

   mini_app_start_num():主要是防止没跑完停下来，下次知道从哪儿开始继续跑，一般不需要动（会根据已经生成的报告书自动调节）

2. 支付宝流量监听

   需要将项目HookAliPayTrafficXposed进行apk打包安装至测试机上，并在测试机上进行本地端口8080配置，才可以进行支付宝流量监听功能。

   

   

## 运行顺序

1. 先启动stanford_nlp数据处理模块

   ```
   java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -preload tokenize,ssplit,pos,lemma,ner,parse,depparse -status_port 9000 -port 9000 -timeout 15000
   
   ```

   

2. 直接pycharm内运行xpochecker.py文件即可

