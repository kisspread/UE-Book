# Tensorboard

> Optional tensorboard python package and dependencies

| 属性 | 值 |
|---|---|
| 中文名 | TensorBoard 依赖 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Python 依赖） |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-10-30 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Tensorboard) | |

## 用途
这是一个**依赖管理插件**。它本身不包含任何 C++ 代码或蓝图资产，其唯一作用是在启用时，通过 Unreal Engine 内置的 Python 包管理工具，自动安装 `tensorboard` 及其所有必需的 Python 依赖项。其核心目的是为 Unreal Engine 内基于 Python 的机器学习工作流（特别是与 `LearningAgents` 相关的强化学习训练）提供 TensorBoard 可视化支持，使开发者能够在训练过程中实时监控和记录标量、图像、图表等数据。

## 使用场景
- 你正在使用 Unreal Engine 的 Python 脚本或 `LearningAgents` 框架进行强化学习训练，并希望利用 TensorBoard 来可视化训练过程中的奖励、损失函数、学习率等关键指标。
- 你需要为 Unreal Engine 内嵌的 Python 环境快速、一键地安装完整的 TensorBoard 生态，而无需手动处理复杂的依赖关系。

## 蓝图用法
该插件不包含任何蓝图节点或资产。其作用完全在引擎的 Python 环境初始化阶段完成。启用此插件后，TensorBoard 包将被自动安装到引擎的 Python 环境中，供任何使用该环境的 Python 脚本或插件调用。

### 使用示例（Python 环境验证）
启用插件后，你可以通过 Unreal Engine 内置的 Python 控制台或通过脚本调用来验证 TensorBoard 是否已成功安装。

```python
# 在 Unreal Engine 的 Python 控制台中执行
import tensorboard
print(f"TensorBoard version: {tensorboard.__version__}")
```

## C++ 用法
不适用。该插件不提供任何 C++ API 或头文件。

### 头文件引入
不适用。

### 基本用法
不适用。

### 进阶用法
不适用。

## Demo 示例
该插件本身不提供可运行的 C++ 代码示例。要体验其功能，你需要：
1.  在插件管理器中启用 `Tensorboard` 插件（它会自动启用依赖的 `PythonMLPackages` 插件）。
2.  重启编辑器（首次安装时，引擎会在启动时安装依赖包）。
3.  通过上述“蓝图用法”章节中的 Python 代码验证安装。

## 模块依赖
该插件依赖于其他 Python 包管理插件来共同工作。

| 模块 | 用途 |
|---|---|
| `PythonMLPackages` | 提供基础的机器学习 Python 包支持框架，`Tensorboard` 插件在其基础上添加 TensorBoard 特定依赖。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-06-20 | `35f8ecb8` | PythonFoundationPackages: Move Torch python requirements to separate PythonMLPackages plugin | 将 PyTorch 的依赖定义从其他插件移至 `PythonMLPackages`，进行了依赖项的重构整理。 |
| 2024-10-30 | `213c8904` | LearningAgents: Add optional tensroboard plugin that can be enabled to install tensorboard and dependencies. | 首次创建该插件，为 `LearningAgents` 提供可选的 TensorBoard 安装功能。 |

### 维护评价
该插件创建于 2024 年 10 月底，非常新。最近的更新（2025-06-20）主要是对依赖项管理结构的重构，表明其底层的依赖管理框架仍在维护中。然而，`Tensorboard` 插件本身的功能自首次提交后未有实质变化，它是一个相对静态的依赖包定义。由于它作为 `LearningAgents` 机器学习工具链的一部分被引入，其长期维护与 `LearningAgents` 和 `PythonMLPackages` 插件的状态紧密相关。目前看来，它是一个功能明确且仍在维护的辅助插件。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Tensorboard)
- [官方文档]() （.uplugin 中未提供）
- [依赖插件: PythonMLPackages](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PythonMLPackages)