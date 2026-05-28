# ML Adapter

> A framework for training and utilizing machine learning agents in games. Creates an RPC interface through which an external process can query game state and control in-game actors. Once trained, agents can be run in-engine via neural networks loaded from ONNX models.

| 属性 | 值 |
|---|---|
| 中文名 | 机器学习适配器 |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MLAdapter` (Runtime), `MLAdapterTestSuite` (DeveloperTool) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-04-12 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MLAdapter) | |

## 用途

MLAdapter 为 UE5 游戏提供了一个完整的机器学习代理训练与运行框架。它解决了两个核心问题：

1. **外部进程通信**：通过 RPC（远程过程调用）接口，让外部 Python/ML 训练进程能够实时查询游戏状态、控制游戏内 Actor，实现强化学习的数据采集与动作执行。
2. **推理部署**：训练完成后，可通过加载 ONNX 格式的神经网络模型，直接在引擎内运行推理，无需依赖外部进程。

该插件本质上是连接 UE5 游戏世界与外部 ML 训练环境的桥梁，使得游戏 AI 可以通过机器学习方法进行训练和优化。

## 使用场景

- 你在做游戏 AI 的强化学习训练 → 用 MLAdapter 的 RPC 接口连接 Python 训练环境
- 你需要让外部训练好的神经网络直接控制游戏角色 → 用 ONNX 模型加载功能在引擎内运行推理
- 你需要批量收集游戏状态数据用于 ML 训练 → 用 MLAdapter 的状态查询接口
- 你在研究游戏 AI 的机器学习方法 → 用完整的端到端训练流程

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [MLAdapter](MLAdapter.md) | Runtime | 核心模块，提供 RPC 接口、游戏状态采集、Actor 控制和 ONNX 模型推理 |
| [MLAdapterTestSuite](MLAdapterTestSuite.md) | DeveloperTool | 测试套件，包含自动化测试用例验证 MLAdapter 功能 |

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RPCLib` | 提供远程过程调用底层通信能力 |
| `GameplayAbilities` | 插件级依赖，用于技能系统集成 |
| `EnhancedInput` | 插件级依赖，用于增强输入系统集成 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新版 UE_LOGF 接口 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复批量替换错误后的第二次尝试 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退之前的提交 CL51314860 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 迁移引擎初始化委托调用方式修复注册缺失 |
| 2026-02-04 | `80b637db` | Fixed printf format specifiers. | 修复 printf 格式化说明符问题 |

### 维护评价

MLAdapter 作为实验性插件，近期更新全部为引擎级维护性改动（日志宏迁移、委托 API 变更、格式修复），没有功能性更新。自 2021 年从 UE4ML 重命名以来，该插件一直处于实验性状态且默认未启用，说明 Epic 对其成熟度持保留态度。

该插件的架构设计完整（RPC 通信 + ONNX 推理），但考虑到：
- 长期标记为实验性且未正式发布
- 近期无功能性更新，仅跟随引擎全局 API 变更
- `Installed: false` 表明不会随引擎自动安装

**建议**：可用于 ML/AI 研究和原型开发，但不建议在生产环境中深度依赖。如需在正式项目中使用，需自行承担实验性 API 变更的风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MLAdapter)
- [MLAdapter 核心模块文档](MLAdapter.md)
- [测试套件模块文档](MLAdapterTestSuite.md)