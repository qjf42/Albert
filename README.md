## 1. 介绍
简单的聊天机器人服务，目前只支持单轮，可通过配置简单模板增加自定义意图，也包含较完整的问答类服务（TODO），
模型部分见[Albert_model](https://github.com/qjf42/Albert_model)

## 2. 目录结构
```
- nlu           // 词法分析，意图识别，槽位解析
- rank          // 意图排序
- skills        // 技能
- qa            // QA类服务（独立服务，支持独立部署，详情见`qa/README.md`）
- conf          // 配置
- dict          // 词典
- enums         // 枚举类
- interfaces    // 接口类
- utils         // 工具类、函数
- dumb_bot.py   // 服务入口
```

## 3. 使用方式
### 3.1 启动
1. 将当前目录放在一个dev路径下，e.g
    ```
    mkdir dev && cd dev && git clone https://github.com/qjf42/Albert.git && cd Albert
    ```
2. 部署机器人服务到测试或线上环境
    ```
    # 会新建../test ../prod目录，将dev目录下的代码同步过去，并调整相关配置
    ./dist.sh test && cd ../../test/Albert
    # ./dist.sh prod && cd ../../prod/Albert
    ```
3. 启动服务
    ```
    ./start.sh
    ```
    端口：5510(test)/5500 (prod)

### 3.2 调用
具体调用的接口参考`dumb_bot.py`中的定义，根据不同的请求类型，可以有不同的参数配置

#### 3.2.1 GET/POST /chat_debug
- 请求

    | 字段 | 类型 | 说明 |
    |-|-|-|
    | query | str | |

- 返回

    | 字段 | 类型 | 说明 |
    |-|-|-|
    | success | bool | |
    | err_no | int | 参考`enums.EnumResponseError` |
    | err_msg | str | |
    | data.response.type | str | 机器人回复值类型，text/img |
    | data.response.value | str | 机器人回复话术 |
