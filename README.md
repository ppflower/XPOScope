# XPOScope

## 项目结构说明

```cmd
├─dynamicExerciser  	  # 小程序自动化点击测试模块
│  ├─checkpoints		  # 与训练集合
│  ├─data				  # 运行数据存放位置
│  │ ├─evaluate_classifer
│  │ ├─page_text
│  │ ├─picCache
│  │ └─screenshots
│  │ │  ├─alipay
│  │ │  ├─baidu
│  │ │  └─wechat
│  ├─page_utils
│  └─picLabel
├─HookAliPayTrafficXposed # 支付宝流量抓取Xposed模块
├─MiniAppLog              # 小程序流量和页面文本Log
├─LogAnalysis			  # XPO分析模块（分析MiniAppLog中的文件）
├─OcrDump				  # 图片文本识别模块
├─trafficMonitor		  # 流量监听模块
├─config.py				  # 全局配置文件
├─xpochecker.py			  # 单个小程序测试启动器
├─xpocheckerList.py		  # 数据集小程序批量测试启动器
├─AlipayTrafficHook.apk	  # 支付宝流量Hook Xposed模块
├─AliPay_XPOCheckerMini_TestCases.xls # 支付宝平台数据集
├─Baidu_XPOCheckerMini_TestCases.xls  # 百度平台数据集
└─Wechat_XPOCheckerMini_TestCases.xls # 微信平台数据集
```



## 项目构建说明

如需要XPOScope工具，使用者可以从https://github.com/ppflower/XPOScope.git上将代码拉取下来，由于文件过大或者空文件等原因，用户将代码拉取下来，需要将项目进行一些补充：

1. ./dynamicExerciser/checkpoints 预处理文件由于体积过大，无法上传至github，使用者可以从该链接（链接：https://pan.baidu.com/s/1gXsLrqnFZT1jeAN9eOyKMA  提取码：7mha）中进行提取
2. ./dynamicExerciser/data 运行时图片文本存放位置属于临时文件，使用者按照项目结构进行创建即可
3. ./MiniAppLog 小程序流量和页面文本Log属于临时文件，使用者进行创建即可
4. 项目中的数据集（AliPay_XPOCheckerMini_TestCases.xls，Baidu_XPOCheckerMini_TestCases.xls，Wechat_XPOCheckerMini_TestCases.xls）如需要修改或者替换，记得变更。




## 代码定制化说明

该项目所有小程序启动运行都是根据Oneplus 9手机进行设置，此外不同版本的微信、百度、支付宝应用布局也会存在差异，请使用者根据下述提示进行代码修改和配置：

1. 定制化小程序启动和运行

   - dynamicExerciser/mini_app_auto.py 中start_mini_app(self)，根据不同应用版本进行修改

   - dynamicExerciser/mini_app_auto.py 中clear_background_apps()用于关闭当前小程序，不同机型可能存在区别，需要进行定制化

   - 尽管代码中开发者已经利用uiautomator2来确定机型的长和宽，但是如果遇到点击错位的问题，可以确认./config.py中DEVICE_WIDTH和DEVICE_HEIGHT是否正确。

     

2. 定制化小程序批量测试和运行

   进行小程序批量测试和运行，主要关注config.py文件中的以下参数：

   - MINI_APP_TEST_TIME : 单个小程序运行时间
   - Mini_App_Type : 针对数据集中30个类别小程序进行选择，可以选择单个类别进行测试
   - WORK_BOOK : 测试数据集的路径
   - TCP_PORT : 本地TCP数据传输会使用的端口，如果存在冲突进行修改（默认 12345）

   

2. 定制化支付宝小程序流量监听

   支付宝小程序相较于微信和百度对小程序流量保护起来，无法直接通过流量抓取工具mitmproxy获取，该工具利用Xposed框架Hook支付宝相关接口的方式来读取支付宝小程序的流量。

   - 如需使用XPOScope来测试支付宝，请安装目录中的AlipayTrafficHook.apk
   - 如需对支付宝流量Hook进行定制化操作，可以参考并修改./HookAliPayTrafficXposed中代码
   
   
   
   

## XPOScope使用说明

1. 设备准备操作

   - 准备一台root安卓手机并配置手动代理 127.0.0.1:9999（端口号需要修改可以参考xpocheckerList.py文件），如需要测试支付宝小程序，需安装EdXposed环境（用于安装AlipayTrafficHook.apk）
   - 在安卓手机中创建 /sdcard/screenshots和/sdcard/picCache两个文件夹，用于存放临时文件
   - 一台PC设备，该设备存放针对上述安卓手机定制完成的XPOScope代码，并在链接（链接：https://pan.baidu.com/s/1gXsLrqnFZT1jeAN9eOyKMA  提取码：7mha）中下载stanford-corenlp-4.1.2工具包
   - 将安卓手机使用数据线连接至PC设备，并允许文件传输

   

2. 启动文本处理模块

   - 将stanford-corenlp-4.1.2工具包解压在PC设备上，并运行下述命令行

     ```
     java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -preload tokenize,ssplit,pos,lemma,ner,parse,depparse -status_port 9000 -port 9000 -timeout 15000
     ```

     

3. 启动XPOScope工具

   - xpochecker.py:  仅运行单个小程序，修改main函数中的mini_app_platform（0：支付宝，1：微信，2：百度）、mini_app_name参数
   - xpocheckerList.py：运行数据集中的小程序，参考代码定制化中的说明修改WORK_BOOK等参数。

   
