# TensorBoard

> Optional tensorboard python package and dependencies

| 属性 | 值 |
|---|---|
| 中文名 | TensorBoard包安装器 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Python包依赖声明） |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-10-30 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Tensorboard) | |

## 用途

TensorBoard 插件本身不包含任何 C++ 代码或蓝图资产。它的核心功能是作为一个“依赖声明器”，为 Unreal Engine 内置的 Python 环境安装 `tensorboard` 及其全部必需的 Python 第三方库。该插件存在的目的是简化环境配置，使得依赖 Python 强化学习（特别是 `LearningAgents` 模块）的工作流能够无缝地使用 TensorBoard 进行训练监控和数据可视化，而无需用户手动使用 `pip` 安装复杂的依赖链。

## 使用场景

- 你正在使用 **LearningAgents** 模块进行强化学习训练，并希望实时查看训练指标（如损失、奖励）和性能图表。
- 你需要一个开箱即用的 TensorBoard 集成，不想处理 Python 虚拟环境和包版本冲突的问题。

## 蓝图用法

此插件**不提供**任何蓝图节点。它的作用是安装底层的 Python 包，用户通过启用此插件后，在 Python 脚本或 `LearningAgents` 相关的蓝图函数中间接使用 TensorBoard。

### 间接使用示例

1.  **启用插件**：在项目设置或 `.uproject` 文件中启用 `Tensorboard` 插件。
2.  **运行 TensorBoard**：在项目的 Python 环境中或通过命令行，使用 `tensorboard --logdir=<your_logs>` 命令启动 TensorBoard 服务器。由于插件已安装依赖，此命令应可直接执行。
3.  **记录数据**：在用于训练的 Python 脚本或通过 `ULearningAgentsTrainer` 等类配置日志路径，将训练数据输出到 TensorBoard 可读的格式。

## C++ 用法

此插件**不提供** C++ API。它是一个纯粹的“内容”插件，仅负责在引擎启动时通过插件依赖系统安装声明的 Python 包。

## Demo 示例

由于此插件无源码，以下是一个**使用步骤示例**，展示如何启用它并验证安装：

**步骤 1：在项目中启用插件**

在你的 `.uproject` 文件中，确保 `Plugins` 数组包含：
```json
"Plugins": [
    ...,
    {
        "Name": "Tensorboard",
        "Enabled": true
    },
    ...,
    {
        "Name": "PythonMLPackages",
        "Enabled": true
    }
]
```
**步骤 2：启动引擎并验证**

1.  启动 Unreal Editor 或你的项目。
2.  打开“输出日志”窗口。
3.  你应该能看到类似 `LogPython: Running pip install ...` 的输出，表明 `tensorboard` 及其依赖正在被安装。
4.  在项目的 Python 环境中，尝试运行 `import tensorboard; print(tensorboard.__version__)` 来验证安装。

## 模块依赖

此插件**依赖**于以下其他插件：

| 插件 | 用途 |
|---|---|
| `PythonMLPackages` | 提供基础的机器学习相关 Python 包（如 NumPy, SciPy），是 TensorBoard 依赖链的一部分。 |

你的模块或项目如果要使用此插件，需要在项目设置中同时启用 `Tensorboard` 和 `PythonMLPackages` 插件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-06-20 | `35f8ecb8` | PythonFoundationPackages: Move Torch python requirements to separate PythonMLPackages plugin | 重构了 Python 包的组织结构，将 PyTorch 依赖移出，明确了本插件专注于 TensorBoard 链。 |
| 2024-10-30 | `213c8904` | LearningAgents: Add optional tensroboard plugin that can be enabled to install tensorboard and dependencies. | 初始创建，为 LearningAgents 工作流添加 TensorBoard 支持。 |

### 维护评价

- **创建时间**：较新，不足一年。
- **最近更新**：最近一次更新在 2025 年 6 月，是一次依赖结构的重构，表明该插件作为 `LearningAgents` 生态的一部分仍在**活跃维护**中。
- **当前状态**：功能稳定，但标记为**实验性**（`IsExperimentalVersion: true`）。这意味着其 API 或行为在未来版本中可能发生不兼容的变化。
- **推荐使用**：**推荐**用于开发和研究阶段。如果你正在使用 `LearningAgents` 并需要 TensorBoard 可视化，启用此插件是最简便的方式。对于生产环境，需关注其“实验性”标签。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Tensorboard)
- [官方文档]() (无)
- [测试用例]() (无，此插件为纯依赖声明，无独立测试)