# Camera Calibration Machine Learning

> Reference implementation of a machine learning approach to distortion calibration.

| 属性 | 值 |
|---|---|
| 中文名 | 机器学习镜头校准 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有 (Python 脚本) |
| 模块 | `CameraCalibrationML` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2024-09-11 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CameraCalibrationML) | |

## 用途

本插件提供了一个使用机器学习（PyTorch）来校准相机镜头畸变的参考实现。它通过分析捕获的棋盘格图案图像，训练一个神经网络来学习镜头固有的畸变参数，而非依赖传统的物理模型。其主要目的是为虚拟制作（Virtual Production）工作流提供一种更精确、数据驱动的镜头校准方法，以确保在 LED 墙或摄像机内视觉效果 (ICVFX) 中合成的图像与物理镜头完美匹配。

## 使用场景

- 你是虚拟制作团队中的技术美术或工具程序员，需要为特定镜头（尤其是畸变复杂或非标准的镜头）创建高精度的畸变校准数据，以用于实时合成或后期制作。
- 你希望探索并评估基于机器学习的镜头校准方法，以替代或补充 `CameraCalibration` 插件中提供的传统物理模型。
- 你在开发自定义的校准流程，并需要一个利用 PyTorch 进行模型训练和推理的基础框架。

## 蓝图用法

此插件为 **编辑器模块**，主要提供底层的 Python 脚本执行环境和参考代码，**不包含可直接在运行时蓝图中调用的公开蓝图函数**。其核心功能是通过 Python 脚本在编辑器内或外部环境中运行机器学习训练和推理流程。

### 核心节点

无（此插件不提供蓝图节点）

## C++ 用法

此插件主要以 Python 脚本形式提供核心逻辑，不包含可供其他 C++ 模块直接链接和调用的公开 C++ API。其作用是将机器学习相关的依赖（PyTorch）隔离在一个独立的插件中，供 `CameraCalibration` 插件或其他需要调用这些脚本的功能使用。

### 头文件引入

无直接 C++ API 可供引入。

### 基本用法

无。

### 进阶用法

无。

## Demo 示例

不适用。

## 模块依赖

要使用此插件，你的项目或插件需要依赖以下特殊模块：

| 模块 | 用途 |
|---|---|
| `CameraCalibration` | 核心镜头校准框架，提供基础的数据结构和校准流程 |
| `PythonMLPackages` | 提供运行机器学习 Python 脚本所需的环境和包（如 PyTorch） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-06-20 | `35f8ecb8` | PythonFoundationPackages: Move Torch python requirements to separate PythonMLPackages plugin | 将 PyTorch 的 Python 依赖项迁移至独立的 PythonMLPackages 插件，进一步隔离依赖。 |
| 2024-09-11 | `08a49766` | CameraCalibration: Move ML python scripts into dedicated plugin to isolate pytorch dependency | 初始提交。将机器学习 Python 脚本从 CameraCalibration 插件移入此专用插件，以隔离 PyTorch 依赖。 |

### 维护评价

- **年龄**：创建于 2024 年 9 月，非常年轻的插件（约 1 年）。
- **近期更新**：最近一次更新（2025-06）是依赖管理的调整，而非功能增强。创建以来仅有两次提交，更新频率极低。
- **维护状态**：**实验性且维护不活跃**。该插件被标记为 `IsExperimentalVersion` 且默认不启用。从提交历史看，它更像是一个为隔离依赖而拆分出的“容器”插件，而非一个处于积极功能开发中的成熟产品。
- **已知限制**：作为参考实现，其功能可能局限于特定场景。实验性状态意味着其API、结构和依赖项在未来的引擎版本中可能发生重大变更。
- **使用建议**：**仅推荐用于学习和研究**。不建议将其作为生产环境中的核心依赖。如果你需要成熟的机器学习镜头校准方案，应考虑基于此参考实现进行深度二次开发，并自行承担实验性功能带来的维护风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CameraCalibrationML)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CameraCalibrationML/Tests)