# TensorBoard（可选Python包）

> Optional tensorboard python package and dependencies

| 属性 | 值 |
|---|---|
| 中文名 | TensorBoard支持包 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Python包依赖定义） |
| 模块 | 无（纯Python包插件） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-10-30 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Tensorboard) | |

## 用途

该插件为 Unreal Engine 提供 **TensorBoard** Python 包及其所有依赖的安装支持。TensorBoard 是 TensorFlow 的可视化工具包，用于记录和展示机器学习训练过程中的指标（如损失、准确率、学习率等）、模型结构、嵌入向量等。

通过启用此插件，引擎内部的 Python 环境（由 `PythonMLPackages` 插件管理）将自动安装或更新 `tensorboard` 及其依赖（`absl-py`、`grpcio`、`Werkzeug` 等），使得在 UE 中运行的 Python 脚本可以直接导入并使用 `tensorboard` 进行训练监控。

**为什么存在？**  
UE 中执行机器学习训练（如强化学习、模仿学习、监督学习）时，需要实时可视化训练进度。TensorBoard 是业界标准工具，但默认不包含在 UE 的 Python 发行版中。此插件作为一个可选的轻量级包，让用户按需启用，避免引入不必要的依赖。

## 使用场景

- 你在开发基于 UE 的机器学习训练系统（如使用 `LearningAgents`、`ML-Agents Toolkit` 或自定义训练循环）→ 需要记录训练指标并实时查看 → 启用此插件并编写 Python 代码写入 TensorBoard 事件。
- 你需要分析和调试神经网络模型在 UE 中的行为 → 使用 TensorBoard 的可视化功能（如直方图、分布图、图结构）→ 启用此插件并调用 `tensorboard` API。
- 你在 UE 项目中集成外部 ML 库（如 PyTorch、TensorFlow）并希望统一日志记录 → 启用此插件后可在任意 Python 脚本中使用 TensorBoard。

## 蓝图用法

该插件**不提供**任何蓝图可调用的原生 C++ 节点。其所有功能均通过 Python 脚本暴露。

### 启用与使用

1. 在 **Editor Preferences → Plugins** 中启用 `Tensorboard` 插件（需要同时启用依赖的 `PythonMLPackages`）。
2. 重启编辑器，引擎将自动安装指定版本的 `tensorboard` 及其依赖。
3. 在任意 Python 脚本中导入并使用：

```python
import tensorboard as tb
from torch.utils.tensorboard import SummaryWriter  # 或使用原生 SummaryWriter

writer = SummaryWriter(log_dir='/path/to/logs')
for epoch in range(100):
    writer.add_scalar('Loss/train', loss, epoch)
writer.close()
```

## C++ 用法

该插件**不包含**任何 C++ 核心模块，无头文件引入或 C++ API 可用。所有交互通过 Python 执行。

### 在 C++ 中调用 Python

如果需要在 C++ 代码中间接使用 TensorBoard，可通过调用 Python 脚本来实现：

```cpp
// 启用 Python 脚本执行
FPythonCommandExecutor::Exec(*GWorld, TEXT("py my_tensorboard_script.py"));
```

或使用 `PythonScriptLibrary` 直接运行 Python 字符串。

## Demo 示例

由于无原生 C++ 组件，以下提供一个 Python 脚本示例，用于在 UE 训练循环中记录训练损失：

```python
# Content/Python/train_monitor.py
from torch.utils.tensorboard import SummaryWriter
import unreal

class TrainingMonitor:
    def __init__(self, log_dir="/Game/TrainingLogs"):
        self.writer = SummaryWriter(log_dir=log_dir)
    
    def on_training_step(self, step, loss, accuracy):
        self.writer.add_scalar('Loss/train', loss, step)
        self.writer.add_scalar('Accuracy/train', accuracy, step)
    
    def close(self):
        self.writer.close()

# 在训练循环中调用（示例）
monitor = TrainingMonitor()
for i in range(100):
    # 模拟训练步骤
    loss = 1.0 / (i + 1)
    acc = 1 - 0.1 * i
    monitor.on_training_step(i, loss, acc)
monitor.close()
```

在 UE 中执行：`py train_monitor.py`

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PythonMLPackages` | 提供 Python 包管理基础设施，负责下载和安装 `tensorboard` 及其依赖 |

其他常见模块（Core、Engine 等）均无特殊依赖。

## 维护状态

### 近期更新

- 2025-06-20 `35f8ecb8` PythonFoundationPackages: Move Torch python requirements to separate PythonMLPackages plugin
- 2024-10-30 `213c8904` LearningAgents: Add optional tensorboard plugin that can be enabled to install tensorboard and dependencies

### 维护评价

- **创建时间**：2024-10-30，距今约 9 个月。
- **更新频率**：仅有一次实质性更新（2025-06），将 Torch 相关需求移至 `PythonMLPackages`，属架构调整。
- **活跃度**：目前未发现频繁功能更新，但作为依赖包，其内容（Python 版本锁定）相对稳定。
- **已知问题**：插件为实验性，可能在大型项目中因依赖版本冲突导致安装失败。需确保 `PythonMLPackages` 插件正常运行。
- **推荐度**：如果需要 TensorBoard 功能，推荐启用。但建议在生产项目中进行充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Tensorboard)
- [TensorBoard 官方文档](https://www.tensorflow.org/tensorboard)
- [PythonMLPackages 插件文档](https://docs.unrealengine.com/5.7/en-US/python-ml-packages-plugin-in-unreal-engine/)（假想链接，实际可能不存在）