# World Conditions

> General purpose cached conditions

| 属性 | 值 |
|---|---|
| 中文名 | 世界条件 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `WorldConditions` (Runtime), `WorldConditionsEditor` (Editor), `WorldConditionsTestSuite` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-11-16 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WorldConditions) | |

## 用途

World Conditions 提供了一套**通用的缓存式条件求值系统**，用于游戏逻辑中的条件判断。其核心设计目标是：

- **条件组合**：支持从多个基础条件构建复杂表达式（And/Or/Not 等逻辑组合）
- **缓存优化**：条件结果会被缓存，只在相关状态变化时重新求值，避免每帧重复计算
- **解耦设计**：将条件定义与求值逻辑分离，条件可以在不同系统间复用

该插件面向需要频繁进行条件判断的游戏系统（如任务系统、状态门控、AI 决策等），通过缓存机制显著减少不必要的条件重算开销。

## 使用场景

- 你需要一个任务系统，多个任务有不同的前置/完成条件 → 用 World Conditions 定义条件表达式
- 你需要在 AI 或游戏逻辑中做大量状态判断，但不想每帧全部重新计算 → 用缓存式条件求值
- 你需要蓝图可视化编辑复杂的条件组合（And/Or/Not）→ 用 WorldConditionsEditor 提供的自定义编辑器
- 你需要条件在多个系统间复用（如 UI 显示、Gameplay 门控共用同一条件）→ 定义一次，多处引用

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `WorldConditions` | Runtime | 核心条件求值框架，包含条件定义、表达式构建、缓存求值逻辑 |
| `WorldConditionsEditor` | Editor | 编辑器扩展，提供条件表达式的可视化编辑 UI |
| `WorldConditionsTestSuite` | UncookedOnly | 自动化测试套件，验证条件求值正确性 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WorldConditions)
- [WorldConditions 模块文档](WorldConditions.md)
- [WorldConditionsEditor 模块文档](WorldConditionsEditor.md)
- [WorldConditionsTestSuite 模块文档](WorldConditionsTestSuite.md)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `cfaec1a0` | [WorldConditions] Build SharedDefinition before serialize so name harvest matches write | 修复序列化时 SharedDefinition 构建顺序，确保名称收集与写入一致 |
| 2026-04-23 | `f49c6ff0` | [WorldConditions][Stability] Do not dereference Owner during GC in FWorldConditionQueryState destruc | 修复 GC 期间 FWorldConditionQueryState 析构时解引用 Owner 的崩溃问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF | 日志宏迁移至 UE_LOGF 格式 |
| 2026-03-24 | `2da4cdac` | [AI][WorldConditions] Add WorldConditionsToolset plugin for MCP inspection | 新增 MCP 检查工具插件，支持运行时条件状态调试 |
| 2026-03-10 | `ba65d06d` | [WorldCondition] fixed case where world condition queries would not be properly linked when embedded | 修复嵌入式条件查询链接不正确的问题 |

### 维护评价

**活跃维护** 🟢

- 创建于 2022 年，至今约 4 年
- 近期更新非常频繁：2026 年 3-4 月有多次实质性提交，涵盖 bug 修复、稳定性改进、新工具集成
- 标记为实验性（`IsExperimentalVersion=true`）且默认未启用（`EnabledByDefault=false`），说明 Epic 内部在积极使用但尚未正式发布为稳定 API
- 有配套的 MCP 调试工具（WorldConditionsToolset），说明该系统在 AI 和游戏逻辑中有较深的实际应用
- **推荐用于实验性项目或内部系统**，但生产环境需注意 API 可能变动