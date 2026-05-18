# Agent 项目面试复习手册（ROSA + ROS2）

## 1. 项目一句话介绍
我在 ROSA（Robot Operating System Agent）基础上，完成了一个面向 ROS2 导航场景的 Agent 工程化增强：
- 增加了基于 Callback 的 hook 机制
- 实现了 query/tool 两级结构化日志与工具调用可观测性
- 落地了最小可用长期记忆（检索注入 + 写回）

---

## 2. 你做了什么（面试重点）

### 2.1 Hook / 可观测性
- 在 Agent 执行链路接入 callback（tool start/end/error）
- 记录每次工具调用：工具名、输入摘要、耗时、状态
- 使用 `query_id` 串联 session 与 tools 日志，实现全链路追踪

可讲亮点：
- 不是只看最终回答，而是能追踪“模型为什么这么回答”
- 调试时能快速定位慢点和错误点

### 2.2 结构化日志
- 输出两类 JSONL：
  - `rosa_session.jsonl`：query_start/query_end/query_error
  - `rosa_tools.jsonl`：tool_start/tool_end/tool_error
- 日志带时间戳，支持滚动存储（RotatingFileHandler）

可讲亮点：
- 读写分层，避免日志混杂
- 机器可解析，方便做后续评估脚本

### 2.3 最小长期记忆（Phase 1）
- 新增 `memory_store.py`（JSONL 持久化）
- 每轮 `invoke()` 前：按 query 检索 top-k memory 注入上下文
- 每轮 `invoke()` 后：写入 summary/fact 记忆
- 去重：`type + content` hash 去重

可讲亮点：
- 从“纯短期对话”升级为“跨会话可复用知识”
- 先做轻量可运行版本，再逐步演进到向量检索

---

## 3. 当前技术架构（你可以画图）
用户输入
-> ROSA.invoke(query)
-> query_start 日志
-> memory 检索（top-k）并注入 prompt
-> LLM 决策工具调用
-> callback 捕获 tool_start/tool_end
-> query_end 日志
-> memory 写回（summary/fact）

核心文件：
- `src/rosa/rosa.py`（主调用链）
- `src/rosa/tool_trace_logger.py`（hook 与日志）
- `src/rosa/memory_store.py`（长期记忆）

---

## 4. 你要会解释的关键设计

### 4.1 为什么要 query_id
- 一个 query 可能调用多个工具
- `query_id` 把 session 和 tool 事件关联起来
- 实现“从用户问题追到每一步工具调用”

### 4.2 为什么日志拆成 session/tools 两份
- session 关注业务层（问了什么、答了什么）
- tools 关注执行层（调了什么工具、耗时多少）
- 便于调试和后续评估脚本

### 4.3 为什么长期记忆先用 JSONL
- 目标是先验证闭环，不引入重型依赖
- JSONL 可读、可 grep、可快速迭代
- 后续可替换成向量库（Chroma/FAISS/Milvus）

---

## 5. 面试高频问题与回答模板

### Q1：你怎么保证日志能定位到某次具体会话？
答：
- 每次 invoke 生成唯一 `query_id`
- session 和 tools 都写入这个 `query_id`
- 检索某次问题时按 `query_id` 过滤即可完整还原调用链

### Q2：你的 hook 是怎么工作的？
答：
- 使用 LangChain CallbackHandler
- 在 on_tool_start/on_tool_end/on_tool_error 中记录事件
- 通过 callbacks 注入到执行器和调用 config

### Q3：长期记忆是怎么检索的？
答：
- Phase 1 先做关键词重叠打分（轻量）
- 每轮召回 top-k 注入上下文
- 回答后写入 summary/fact，并做 hash 去重

### Q4：这套改造给你带来什么收益？
答：
- 调试效率提升：能看清 Agent 每步调用
- 可解释性提升：回答背后有工具轨迹
- 可扩展性提升：日志可直接用于评估与记忆沉淀

---

## 6. 可量化指标（建议你补真实数据）
- tool 调用平均时延：`xx ms`
- 单轮平均工具步数：`x.x`
- 故障定位时间缩短：`xx%`
- memory 命中率（召回非空比例）：`xx%`

---

## 7. 下一步路线（你可作为“未来工作”回答）
1. 记忆检索升级为向量检索（语义召回）
2. 从 tools 日志自动提炼 episodic memory
3. 加评估闭环：
   - memory_hit_rate
   - tool_step_reduction
   - task_success_rate
   - latency_delta

---

## 8. 一分钟自我讲述（可背）
我在 ROS2 Agent 项目里主要负责工程化增强。首先，我在执行链路上加了 callback hook，把工具调用过程做成可观测日志，能按 query_id 还原完整调用轨迹。其次，我把日志拆成 session 和 tools 两层，分别记录对话级和执行级信息，便于调试和评估。最后，我实现了一个最小长期记忆机制：每轮调用前检索历史记忆注入上下文，调用后把可复用信息写回，并做去重。这样系统从“只会当前对话”变成了“跨会话可复用经验”的 Agent。EOF
