# Tensorboard

> Optional tensorboard python package and dependencies

| 属性 | 值 |
|---|---|
| 中文名 | Tensorboard 安装器 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Python 包定义） |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-10-30 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Tensorboard) | |

## 用途

该插件并非传统的、包含 C++ 或蓝图逻辑的运行时插件。它的核心功能是**定义并安装 Tensorboard Python 包及其所有必要的依赖项**。它解决的是在 Unreal Engine 5 环境中，快速、一致地部署用于机器学习模型训练过程可视化的 Tensorboard 工具链的问题。通过启用此插件，引擎的 Python 环境（由 `PythonScriptPlugin` 提供）将自动安装 `.uplugin` 文件中 `PythonRequirements` 字段列出的所有 Python 包，无需用户手动操作。

其存在的意义是为 UE5 中与机器学习相关的功能（例如 `LearningAgents`）提供数据可视化支持，使开发者能够在 Tensorboard 的 Web 界面中监控训练过程中的损失、奖励等指标。

## 使用场景

- 你正在使用 `LearningAgents` 插件进行智能体训练，并希望实时监控和可视化训练过程中的各项指标（如奖励、损失函数）。
- 你需要在 Unreal Editor 中快速启动一个 Tensorboard 服务来查看已有的 `.tfevents` 日志文件。
- 你希望避免手动管理复杂的 Python 依赖关系，而希望由引擎插件系统来保证环境的一致性。

## 蓝图用法

此插件不包含任何蓝图可调用的函数或节点。它的作用体现在环境配置层面。启用插件后，你可以在 Python 脚本或命令行中直接使用 `tensorboard` 命令。

### 使用示例（Python 脚本）

在启用此插件的 UE5 编辑器中，打开 Output Log，切换到 Python 模式，执行以下命令即可启动 Tensorboard 服务器：
```python
import subprocess
# 假设你的训练日志目录是 `/Game/MyTrainingLogs`
log_dir = "/Game/MyTrainingLogs"
# 启动 tensorboard 服务， --bind_all 使其在局域网可访问
process = subprocess.Popen(['tensorboard', '--logdir', log_dir, '--bind_all'])
print(f"Tensorboard started. Access at http://localhost:6006")
```

## C++ 用法

此插件没有 C++ 模块，因此没有头文件需要引入，也没有 C++ 层面的直接使用方法。其影响完全作用于引擎的 Python 环境。

## Demo 示例

此插件本身不提供可编译的示例。以下是一个使用 Tensorboard 的标准 Python 训练记录示例，说明了为什么需要安装这个包：

```python
# 假设在 UE5 的 Python 环境中执行（插件已启用）
import torch
from torch.utils.tensorboard import SummaryWriter
import numpy as np

# 创建一个 SummaryWriter 实例，指定日志目录
writer = SummaryWriter('runs/experiment_1')

# 模拟训练循环
for i in range(100):
    loss = 1.0 / (i + 1) + np.random.randn() * 0.1
    reward = 10.0 - loss * 5 + np.random.randn()
    # 记录标量数据
    writer.add_scalar('Loss/train', loss, i)
    writer.add_scalar('Reward/train', reward, i)

writer.close()
print("Training data logged. Now enable Tensorboard plugin and start server to view.")
```

## 模块依赖

此插件自身没有 C++ 模块依赖，但它依赖以下插件来提供 Python 环境和基础包：

| 插件 | 用途 |
|---|---|
| `PythonMLPackages` | 提供核心的 Python 机器学习基础包（如 NumPy, SciPy, Matplotlib）。Tensorboard 插件在此基础上进行扩展。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-06-20 | `35f8ecb8` | PythonFoundationPackages: Move Torch python requirements to separate PythonMLPackages plugin | 将 Torch 的 Python 依赖从基础包插件移至新的 `PythonMLPackages` 插件，Tensorboard 插件随之调整依赖关系。 |
| 2024-10-30 | `213c8904` | LearningAgents: Add optional tensorboard plugin that can be enabled to install tensorboard and dependencies. | 作为 LearningAgents 的可选伴侣插件被首次创建，定义了 Tensorboard 及其依赖。 |

### 维护评价

- **创建时间**：约 1 年前（2024年10月），是一个非常新的插件。
- **更新频率**：更新频率较低，仅 2 次提交，但最近一次更新（2025年6月）是一次结构性调整，表明插件仍在维护中，并与 `PythonMLPackages` 协同演进。
- **维护状态**：**维护中**。虽然代码量极小（本质是配置文件），但作为基础设施的一部分，它随上层插件（如 `LearningAgents`、`PythonMLPackages`）的更新而被关注。
- **已知限制**：
    1.  **实验性**：标记为 `IsExperimentalVersion: true`，接口和行为可能发生变化。
    2.  **依赖管理**：所有包都指定了精确的版本和哈希值，这保证了环境的可重复性，但用户无法轻松升级到 Tensorboard 的新版本，除非等待插件更新。
    3.  **功能单一**：仅负责安装，不提供将 UE5 数据（如图像、自定义指标）写入 Tensorboard 格式的原生集成。
- **推荐使用**：如果你正在使用 `LearningAgents` 或需要在 UE5 Python 环境中快速使用 Tensorboard，**推荐启用**。它能省去复杂的依赖安装步骤。对于追求最新 Tensorboard 版本或有深度定制需求的用户，可能需要手动管理 Python 环境。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Tensorboard)
- [官方文档](https://www.tensorflow.org/tensorboard)（Tensorboard 官方网站）
- [相关插件：LearningAgents](https://docs.unrealengine.com/5.0/en-US/scripted-automation-and-machine-learning-in-unreal-engine/)
- [相关插件：PythonMLPackages](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PythonMLPackages)