# MLflow

> Optional mlflow python package and dependencies

| 属性 | 值 |
|---|---|
| 中文名 | MLflow 实验跟踪 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Python 包定义文件） |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-02-20 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MLflow) | |

## 用途

MLflow 插件为 Unreal Engine 提供了 **MLflow Python 包** 的安装和管理。MLflow 是一个开源的机器学习生命周期平台，用于跟踪实验、打包代码和部署模型。

该插件**本身不包含任何运行时代码**，它只是一个内容插件，其主要作用是：

1. **声明 Python 依赖**：定义了安装 MLflow 及其依赖项所需的 pip 包和版本约束。
2. **提供许可证文件**：包含 MLflow 的开源许可证信息。
3. **与 Unreal 的 Python 系统集成**：通过依赖 `PythonMLPackages` 插件，确保在 Unreal 的 Python 环境中可以正确安装 MLflow。

**核心价值**：让 Unreal 用户（尤其是使用 `Learning Agents` 插件进行机器学习相关的开发时）能够无缝地使用 MLflow 来记录、比较和管理机器学习实验的结果和参数，而无需手动配置复杂的 Python 环境。

## 使用场景

- 你正在使用 `Learning Agents` 插件进行强化学习或模仿学习实验，需要系统地记录每次训练的参数、指标和模型。
- 你需要在 Unreal 外部的 MLflow 服务器上可视化和比较不同实验版本的结果。
- 你的团队希望将 Unreal 的模拟数据和训练结果集成到已有的机器学习工作流中。

## 蓝图用法

该插件**不提供任何蓝图节点**。它的功能完全通过 Unreal 内置的 Python 环境实现。

使用流程如下：
1. 在项目设置中启用此插件及其依赖项 `PythonMLPackages`。
2. 重启编辑器，Unreal 会自动下载并安装 MLflow 包。
3. 在 Unreal 的 Python 控制台（`Output Log` 窗口输入 `py`）或通过 Python 脚本文件使用 MLflow。

## C++ 用法

该插件**不提供 C++ API**。其全部操作都在 Python 层面。

### 在 Python 中使用 MLflow

启用插件后，你可以直接在 Unreal 的 Python 环境中导入并使用 MLflow。

**头文件引入**

不需要 C++ 头文件。

**基本用法**

首先，在你的 Python 脚本中初始化 MLflow：

```python
import mlflow

# 设置跟踪服务器地址（可选，默认为本地文件目录）
# mlflow.set_tracking_uri("http://localhost:5000")

# 开始一个新的实验（run）
with mlflow.start_run(run_name="MyUnrealTrainingRun"):
    # 记录超参数
    mlflow.log_param("learning_rate", 0.001)
    mlflow.log_param("batch_size", 32)
    
    # 假设这是你的训练循环
    for epoch in range(10):
        # ... 训练代码 ...
        loss = ... # 计算的损失值
        accuracy = ... # 计算的准确率
        
        # 记录指标
        mlflow.log_metric("loss", loss, step=epoch)
        mlflow.log_metric("accuracy", accuracy, step=epoch)
    
    # 可以保存模型文件（例如，从 Unreal 导出的 PyTorch 模型）
    # mlflow.pytorch.log_model(my_model, "model")
    
    print("Experiment run logged to MLflow.")
```

**进阶用法**

结合 `Learning Agents` 插件，记录智能体（Agent）的学习过程：

```python
import mlflow
from unreal import LearningAgentsTrainer # 假设的导入路径

# 在你的训练脚本中
trainer = ... # 初始化你的 LearningAgentsTrainer

with mlflow.start_run(run_name="LearnerAgent"):
    # 记录训练器的配置
    mlflow.log_params(trainer.get_configuration())
    
    for i in range(trainer.num_training_episodes):
        trainer.run_episode()
        metrics = trainer.get_training_metrics()
        
        # 将训练器返回的指标字典记录到 MLflow
        mlflow.log_metrics(metrics, step=i)
        
        # 每 N 个 episode 可以保存一个快照
        if i % 100 == 0:
            trainer.save_checkpoint(f"checkpoint_{i}")
            mlflow.log_artifact(f"checkpoint_{i}.pkl") # 假设是 pkl 文件
```

## Demo 示例

由于这是一个纯内容插件，没有 C++ 或蓝图代码示例。以下是一个完整的、可在 Unreal Python 控制台中运行的最小 Python 示例，用于验证 MLflow 是否安装成功并基本可用：

```python
import mlflow
import os

# 1. 检查版本
print(f"MLflow version: {mlflow.__version__}")

# 2. 创建一个本地实验（默认保存在 ~/mlruns 目录）
experiment_name = "UE5_MLflow_Test"
mlflow.set_experiment(experiment_name)

# 3. 记录一些示例数据
with mlflow.start_run(run_name="HelloUE"):
    # 记录参数
    mlflow.log_param("unreal_engine_version", "5.8")
    mlflow.log_param("project", "TestProject")
    
    # 记录指标
    mlflow.log_metric("fps", 60.0)
    mlflow.log_metric("memory_usage_mb", 1024.5)
    
    # 创建一个临时文本文件作为产物（artifact）
    log_file = "ue5_log.txt"
    with open(log_file, "w") as f:
        f.write("This is a test artifact from Unreal Engine 5.")
    mlflow.log_artifact(log_file)
    os.remove(log_file) # 清理临时文件

    print(f"Run logged. Run ID: {mlflow.active_run().info.run_id}")

print(f"Experiment '{experiment_name}' created/updated.")
print("You can view the results by running 'mlflow ui' in the directory containing the 'mlruns' folder.")
```

## 模块依赖

该插件本身是纯内容插件，但它通过 `.uplugin` 声明了对另一个插件的硬依赖。

| 模块/插件 | 用途 |
|---|---|
| `PythonMLPackages` | **必需依赖**。提供 Unreal 的 Python 环境和包管理基础框架，是本插件能够安装 MLflow 的前提。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-06-20 | `35f8ecb8` | PythonFoundationPackages: Move Torch python requirements to separate PythonMLPackages plugin | 将 PyTorch 的 Python 依赖移动到单独的 PythonMLPackages 插件中。这表明插件依赖结构可能进行了重构。 |
| 2025-03-06 | `2b0a62bc` | Learning Agents: Simply MLflow pip dependencies and add license and proper TPS file | 简化了 MLflow 的 pip 依赖声明，并添加了许可证文件和正确的 TPS 文件。这是插件本身的完善工作。 |
| 2025-02-20 | `5ff67eb5` | Learning Agents: Add MLflow as an option for logging and tracking experiments | 首次提交，作为 Learning Agents 的可选实验记录工具添加了 MLflow。 |

### 维护评价

**维护评价：活跃维护（实验性）**

- **创建时间**：2025 年 2 月，插件非常年轻。
- **更新频率**：在创建后的 4 个月内有两次实质性更新，表明仍在积极开发和优化。
- **维护状态**：**活跃维护**。最新更新（2025年6月）是对依赖结构的重构，通常意味着开发者仍在关注其架构。
- **已知限制**：作为 `Experimental` 插件，其 API 和功能可能会在未来的版本中发生变化或移除。`Installed: false` 表明它默认不启用，用户需要手动打开。
- **推荐使用**：**推荐给正在使用或计划使用 `Learning Agents` 进行机器学习开发的用户**。它是 Epic 官方提供的、与 Unreal 工程深度集成的 MLflow 解决方案。对于非 ML 工作流，无需使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MLflow)
- [官方文档]( ) （暂无官方文档链接）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MLflow) （该插件没有独立的测试用例，其功能通过 Python 脚本集成测试）