# Tensorboard

> Optional tensorboard python package and dependencies

| 属性 | 值 |
|---|---|
| 中文名 | TensorBoard |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Python包依赖） |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-10-30 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Tensorboard) | |

## 用途

该插件本身不包含任何引擎模块或运行时代码。它的唯一作用是作为一个 **Python 包分发器**，通过其 `.uplugin` 文件中的 `PythonRequirements` 字段，在启用时为 Unreal Engine 的集成 Python 环境安装 `tensorboard` 及其所有必需依赖（如 `grpcio`, `Werkzeug` 等）。

其存在的意义是为 Unreal Engine 内使用 Python（特别是机器学习相关的 `LearningAgents` 插件）进行模型训练和监控的开发者，提供一个便捷的、可一键启用的 TensorBoard 可视化工具支持。

## 使用场景

- 你在使用 **LearningAgents** 插件训练智能体，并希望通过 TensorBoard 的 Web 界面实时监控训练损失、奖励曲线等关键指标。
- 你需要通过 Unreal Engine 的 Python 脚本将自定义的训练日志数据输出到 TensorBoard 格式。

## 蓝图用法

暂无。

### 核心节点

暂无。

### 使用示例（蓝图描述）

暂无。该插件不提供蓝图节点，其功能通过启用插件和 Python 环境来使用。

## C++ 用法

暂无。该插件不包含 C++ 模块。

### 头文件引入

暂无。

### 基本用法

暂无。

### 进阶用法

暂无。

## Demo 示例

暂无。这是一个纯内容（Python包）插件。

## 模块依赖

该插件本身无模块。但其 `.uplugin` 声明了对另一个插件的依赖。

| 插件 | 用途 |
|---|---|
| `PythonMLPackages` | 提供基础的 Python 机器学习环境。本插件的 TensorBoard 依赖在此基础上安装。 |

**使用前提**：要使用此插件，你需要在项目中启用 `Python` 和 `PythonEditorScripting` 插件，并确保项目的 Python 环境配置正确。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-06-20 | `35f8ecb8` | PythonFoundationPackages: Move Torch python requirements to separate PythonMLPackages plugin | 将Torch的Python依赖移至独立的`PythonMLPackages`插件，可能涉及插件依赖关系调整。 |
| 2024-10-30 | `213c8904` | LearningAgents: Add optional tensroboard plugin that can be enabled to install tensorboard and dependencies. | 插件初始创建，为LearningAgents提供可选的TensorBoard安装支持。 |

### 维护评价

- **创建时间**：非常新（约1年）。
- **最近更新**：最近一次更新（2025-06）涉及底层依赖包（`PythonMLPackages`）的重组，表明 Epic 在维护相关工具链。
- **活跃状态**：作为 `LearningAgents` 生态的一部分，属于活跃维护项目。
- **已知限制**：该插件是实验性的（`IsExperimentalVersion=true`）且默认不启用（`Installed=false`），需手动开启。其功能完全依赖外部 Python 包。
- **推荐使用**：**推荐**。如果你正在使用或计划使用 `LearningAgents` 进行机器学习实验，这是一个方便的依赖安装工具，省去了手动配置 TensorBoard Python 环境的麻烦。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Tensorboard)
- [官方文档]() （无）
- [测试用例]() （无）