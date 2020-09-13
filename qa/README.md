## 1. 介绍
问答类服务

## 2. 目录结构
```
- analysis          // 问题分析
- retrieval         // 召回
  - term            // 词匹配召回
  - semantic        // 语义召回
  - knowledge_base  // 知识库召回
  - search_engine   // 搜索引擎召回
- processing        // 对召回做进一步处理
  - matching        // 语义匹配
  - knowledge_base  // KBQA
  - summarization   // 文档摘要
  - reading_comprehension   //阅读理解
  - generative      // 生成式
- scripts           // 工具脚本
- conf              // 配置
- enums             // 枚举类
- interfaces        // 接口类
- utils             // 工具类、函数
```

## 3. 使用方式
### 3.1 启动
1. 先根据`Albert/README.md`部署好机器人服务
2. 部署QA服务到测试或线上环境
    ```
    cd dev/Albert/qa
    # 将dev目录下的代码同步过去，并调整相关配置
    ./dist.sh test && cd ../../test/Albert/qa
    # ./dist.sh prod && cd ../../prod/Albert/qa
    ```
3. 启动服务
    ```
    ./start.sh
    ```
    端口：5511(test)/5501 (prod)

### 3.2 调用
具体调用的接口参考`qa_service.py`中的定义，根据不同的请求类型，可以有不同的参数配置

#### 3.2.1 GET/POST /ask
- 请求

    | 字段 | 类型 | 说明 |
    |-|-|-|
    | query | str | |
    | lexical_res | dict | 参考`Albert.interfaces.nlu.LexicalResult` |
    | debug | bool | |

- 返回

    | 字段 | 类型 | 说明 |
    |-|-|-|
    | success | bool | |
    | err_no | int | 参考`Albert.enums.EnumResponseError` |
    | err_msg | str | |
    | data.response.type | str | 机器人回复值类型，text/img |
    | data.response.value | str | 机器人回复话术 |
