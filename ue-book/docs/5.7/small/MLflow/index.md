# MLflow

> Optional mlflow python package and dependencies

| 属性 | 值 |
|---|---|
| 中文名 | MLflow 实验跟踪 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Python 依赖包及配置文件） |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-02-20 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MLflow) | |

## 用途

该插件为 UE 提供 **MLflow** 所需的 Python 包及其依赖（如 `mlflow`、`boto3` 等），作为 [Learning Agents](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LearningAgents) 插件的可选依赖项。MLflow 是一个开源平台，用于管理机器学习实验的生命周期（记录参数、指标、模型等）。通过此插件，开发者可以在 UE 的训练流程中启用 MLflow 日志记录功能，从而追踪超参数、训练曲线和模型版本。

**为什么存在？**  
Learning Agents 插件需要一种标准化方式记录和比较训练实验。MLflow 提供了轻量级的 REST API 和本地存储方案，适合在 UE 训练环境（如 Python 脚本）中使用。该插件将 MLflow 所需的 Python 环境整合到 UE 的 Python 包管理体系中，无需用户手动安装。

## 使用场景

- 你使用 Learning Agents 插件训练智能体（如强化学习），希望记录每个 epoch 的奖励、损失等指标。
- 你需要将训练参数（学习率、网络结构）自动保存到 MLflow 实验，以便后续对比分析。
- 你希望将训练后的模型注册到 MLflow Model Registry，方便版本管理和部署。

## 蓝图用法

本插件仅提供 Python 依赖，**不包含任何可供蓝图调用的 C++ 函数或组件**。MLflow 的调用必须通过 **Python 脚本**（由 UE Python 插件或 External Script 执行）完成。

若需在蓝图中间接使用，可通过 `Execute Python Script` 节点调用 Python 代码，示例：

```
import mlflow
mlflow.set_experiment("MyUEExperiment")
mlflow.log_param("learning_rate", 0.001)
```

## C++ 用法

无 C++ API。该插件未导出任何 C++ 类或函数。

## Demo 示例

无独立示例。可参考 Learning Agents 插件的测试用例，其中通过 Python 调用 MLflow 进行日志记录。

## 模块依赖

| 模块 | 用途 |
|------|------|
| `PythonMLPackages` | 提供基础 Python 依赖管理，MLflow 插件在此基础上添加专属包 |

**注意**：使用本插件必须同时启用 `PythonMLPackages` 插件。

## 维护状态

### 近期更新

- 2025-06-20 `35f8ecb8` — PythonFoundationPackages: Move Torch python requirements to separate PythonMLPackages plugin  
  （将 Torch 依赖移出到独立插件，MLflow 插件保持独立）
- 2025-03-06 `2b0a62bc` — Learning Agents: Simply MLflow pip dependencies and add license and proper TPS file  
  （简化 MLflow pip 依赖，添加许可证和 TPS 文件）
- 2025-02-20 `5ff67eb5` — Learning Agents: Add MLflow as an option for logging and tracking experiments  
  （为 Learning Agents 添加 MLflow 作为实验日志记录选项）

### 维护评价

- **创建时间**：2025-02-20，距今约 1 年。
- **近期更新频率**：最后一次实质性更新为 2025-06-20（约 4 个月前），后续无变更。
- **活跃度**：目前处于实验阶段，功能随 Learning Agents 插件同步更新，独立维护较少。
- **已知问题**：该插件仅提供 Python 包依赖，不包含版本锁定或冲突检测，需注意 Python 环境兼容性。
- **推荐使用**：仅在需要 Learning Agents 实验日志记录功能时启用。对于普通项目，无其他用途。

## 相关链接

- [源码目录（5.7 分支）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MLflow)