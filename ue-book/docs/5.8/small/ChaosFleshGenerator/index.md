# Chaos Flesh Generator

> Chaos Flesh Data Generator for ML Deformer

| 属性 | 值 |
|---|---|
| 中文名 | 混沌肌肉生成器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ChaosFleshGenerator` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-13 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/ChaosFleshGenerator) | |

## 用途

ChaosFleshGenerator 是一个**编辑器专用**工具插件，核心目的是为 Unreal Engine 的 **ML Deformer** 框架自动化生成训练数据。它解决了一个关键问题：ML Deformer 需要大量的、对应不同骨骼姿态的高精度变形网格作为训练数据，而手动运行 Chaos Flesh 物理模拟来生成这些数据既耗时又容易出错。此插件提供了一个集成在 ML Deformer 编辑器中的工作流，允许用户指定输入资产（骨架网格体、肌肉/软组织资产、动画序列）和模拟参数，然后**异步、批量地**运行物理模拟，自动收集并输出 Geometry Cache 作为训练结果。

## 使用场景

- **训练 ML Deformer 变形器**：当你使用 ML Deformer 框架来学习一个复杂的、基于物理的肌肉或软组织变形效果时，你需要为不同的角色姿态生成对应的模拟后的几何体。此插件自动化了这个数据生成过程。
- **自动化数据流水线**：在需要为多个角色或大量动画序列生成训练数据时，可以通过此工具批量处理，极大提升效率。

## 蓝图用法

此插件主要提供编辑器内的配置界面，其核心配置对象 `UFleshGeneratorProperties` 包含以下主要可配置属性（UPROPERTY）：

### 核心配置参数

| 属性 | 说明 | 所在类 |
|---|---|---|
| `SkeletalMeshAsset` | 用于 ML Deformer 的原始骨架网格体 | `UFleshGeneratorProperties` |
| `FleshAsset` | 用于模拟的 Chaos 肌肉资产 | `UFleshGeneratorProperties` |
| `AnimationSequence` | 作为训练输入的姿态动画序列 | `UFleshGeneratorProperties` |
| `SimulatedCache` | 输出的模拟结果（几何缓存资产） | `UFleshGeneratorProperties` |
| `FramesToSimulate` | 指定要模拟的帧范围（如 “0, 2, 5-10”），留空则使用全部帧 | `UFleshGeneratorProperties` |
| `SolverTiming` | 物理模拟的帧率、总帧数、子步长等时间设置组 | `UFleshGeneratorProperties` |
| `SolverEvolution`, `SolverCollisions` 等 | 物理求解器的其他详细设置（碰撞、约束、力） | `UFleshGeneratorProperties` |

### 使用示例（蓝图描述）

1.  在 **ML Deformer 编辑器** 中打开或创建一个 ML Deformer Asset。
2.  在工具栏或面板中找到并打开 **Chaos Flesh Generator** 面板（由 `FChaosFleshGeneratorToolsMenuExtender` 注册）。
3.  在生成器面板中，将 `SkeletalMeshAsset` 拖拽指向你的角色骨架网格体。
4.  将 `FleshAsset` 拖拽指向为该角色创建的 Chaos 肌肉资产。
5.  拖入一个包含多种变形姿态的 `AnimationSequence`。
6.  设置输出的 `SimulatedCache` 资产路径。
7.  根据需要调整 `SolverTiming` 中的 `FrameRate` 和 `NumFrames` 以匹配你的动画。
8.  点击生成按钮。插件将启动异步任务，在后台模拟，并在完成后将结果几何体保存到指定的 Geometry Cache 中。

## C++ 用法

此插件主要面向编辑器扩展开发者，其 API 不直接用于游戏运行时。核心逻辑封装在 `FChaosFleshGenerator` 编辑器可滴答对象和 `FLaunchSimsTask` 异步任务中。

### 头文件引入

对于编辑器扩展开发，若需要与生成器交互，可引入：
```cpp
#include "ChaosFleshGenerator.h" // 核心生成器逻辑
#include "ChaosFleshGeneratorThreading.h" // 任务资源
#include "FleshGeneratorProperties.h" // 属性配置类
```

### 基本用法（概念性）

插件内部通过 `FChaosFleshGenerator` 管理生成流程，并提交 `FLaunchSimsTask` 给线程池执行。以下是简化的任务启动流程概念：

```cpp
// 来自 Source/ChaosFleshGenerator/Private/ChaosFleshGenerator.cpp
// 1. 获取或创建生成器实例 (FChaosFleshGenerator 通常是一个单例)
FChaosFleshGenerator& Generator = /* ... */;

// 2. 配置属性 (UFleshGeneratorProperties 可从编辑器 UI 获取)
UFleshGeneratorProperties* Properties = Generator.GetProperties();

// 3. 请求开始生成动作
Generator.RequestAction(EFleshGeneratorActions::StartGenerate);

// 4. 在 Tick 中，生成器会初始化 FTaskResource 并启动 FLaunchSimsTask
//    FLaunchSimsTask::DoWork() 会在后台线程运行物理模拟
```

### 进阶用法（任务资源管理）

生成过程使用 `FTaskResource` 来管理模拟资源和状态：
```cpp
// 来自 Source/ChaosFleshGenerator/Private/ChaosFleshGeneratorThreading.h
struct FTaskResource
{
    // 模拟资源数组，每帧或每个子任务可能有独立的模拟状态
    TArray<TSharedPtr<FSimResource>> SimResources;
    // 异步任务执行体
    TUniquePtr<FExecuterType> Executer;
    // 用于显示进度通知
    TUniquePtr<FAsyncTaskNotification> Notification;
    // 存储模拟结果
    TArray<TArray<FVector3f>> SimulatedPositions;
    // ... 其他状态管理
};
```

## Demo 示例

由于此插件是纯编辑器工具，没有游戏运行时 API。一个最小的使用流程如下：

1.  **资产准备**：
    - 一个 `USkeletalMesh` (角色骨架)
    - 一个 `UFleshAsset` (该角色的肌肉/软组织物理资产)
    - 一个 `UAnimSequence` (包含待模拟的姿态序列)
    - 一个空的 `UGeometryCache` (用于接收输出)

2.  **在 ML Deformer 编辑器中操作**：
    - 打开 ML Deformer Asset。
    - 使用 Chaos Flesh Generator 面板。
    - 填入上述四个资产。
    - 设置模拟参数（如帧率24，总帧数150）。
    - 点击生成。

生成器将创建临时的模拟 Actor 和组件，运行异步任务，完成后 Geometry Cache 将包含模拟出的顶点位置序列。

## 模块依赖

从 `.uplugin` 的 `Plugins` 部分及代码逻辑推断，使用或二次开发此插件需要以下独特依赖：

| 模块 | 用途 |
|---|---|
| `ChaosFlesh` | 提供核心的 Chaos Flesh 物理模拟框架和资产类型 |
| `GeometryCache` | 用于存储和播放生成的顶点动画序列（输出格式） |
| `MLDeformerFramework` | ML Deformer 的基础框架，提供编辑器扩展点和数据类型 |
| `ChaosVDRuntime` | (潜在) 用于 Chaos 物理模拟的可视化调试 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从UE_LOG迁移到UE_LOGF，适配引擎日志系统更新。 |
| 2025-10-08 | `d09a94c5` | Fix for non-unity build errors | 修复非Unity构建模式下的编译错误。 |
| 2025-09-23 | `244d1dae` | ChaosFlesh: (commit message truncated) | 与 ChaosFlesh 框架相关的更新。 |
| 2025-04-11 | `43d8b160` | Fix include for module manager | 修复头文件包含，解决模块管理器相关问题。 |
| 2025-02-27 | `1eb5b0f5` | Chaosflesh: fixed geometry cache frame rate (defaulted 24, now set to simulation fps) | 修复几何缓存的帧率问题，使其正确使用模拟帧率而非默认的24。 |

### 维护评价

该插件**创建时间较新（约2年）**，但**实验性状态明确**。从 Git 历史看，**更新频率较低，且多为兼容性修复或小 bug 修复**，未见重大功能迭代。最近一次更新（2026年）是日志宏迁移，属于引擎底层适配。插件代码规模较小（16个文件），功能聚焦。由于其**实验性标记**和**依赖于 ChaosFlesh 等同样可能处于实验阶段的模块**，建议仅用于**研究或原型开发**。在生产环境中使用需谨慎，并做好它可能随引擎版本更新而变化或被弃用的心理准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/ChaosFleshGenerator)
- [官方文档]() (无)
- [测试用例]() (插件目录下未发现公开测试用例)