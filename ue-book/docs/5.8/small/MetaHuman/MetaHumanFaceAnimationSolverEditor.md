# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产定义、编辑器集成） |
| 模块 | `MetaHumanCore` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceContourTracker` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-07-16 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途
MetaHuman Animator 插件并非简单的运行时组件，而是一个**完整的、面向工作流的编辑器与运行时工具集**。它解决的核心问题是：**如何将原始的面部动作捕捉数据（如视频、深度数据）高效、精准地应用到MetaHuman数字人角色上，并生成可用于最终渲染的动画序列。**
该插件是Epic官方MetaHuman管线的核心实现，提供了从数据导入、人脸追踪、动画求解到最终动画输出的全链路工具。它内部包含了多个相互协作的子模块，分别处理面部轮廓追踪、深度生成、动画求解器、数据拟合等复杂任务，实现了专业级的面部动捕流水线。

## 使用场景
- 你需要将iPhone或其它设备录制的面部动作捕捉视频，直接应用到UE中的MetaHuman角色上，生成面部动画。
- 你是一名动画师，拥有专业的动作捕捉数据，希望快速驱动MetaHuman角色，并对其进行微调。
- 你需要在UE编辑器中，对一个已有的MetaHuman角色进行面部表情的批量处理或性能分析。
- 你需要开发一个自定义的、包含高级面部动画生成逻辑的MetaHuman处理管道。

## 蓝图用法
该插件的核心功能主要通过编辑器面板和资产系统集成，而非直接的蓝图节点。其大部分运行时功能被封装在管线（Pipeline）和求解器（Solver）模块中，更偏向于底层C++逻辑和编辑器扩展。通常，用户通过**MetaHuman面板**、**资产操作**或**自定义管线蓝图**来使用其功能，而非直接在蓝图图表中调用特定函数。

### 核心节点
| 节点 | 说明 | 所在类 |
|---|---|---|
| `创建/导入 MetaHuman 性能资产` | 在内容浏览器中通过右键菜单创建 `UMetaHumanPerformance` 资产，用于存储处理后的面部动画序列。 | `UMetaHumanPerformance` |
| `MetaHuman 面部动画求解器属性自定义` | 在“细节”面板中对 `UMetaHumanFaceAnimationSolver` 资产的属性进行自定义布局。 | `FMetaHumanFaceAnimationSolverCustomization` |

## C++ 用法
该插件的C++ API主要面向内部扩展和高级开发。常规使用通常通过编辑器交互完成，但开发者可以利用其底层类来集成或扩展面部动画流程。

### 头文件引入
```cpp
#include “MetaHumanPerformance/Classes/MetaHumanPerformance.h”
```

### 基本用法
从测试用例和工厂类推断，创建和管理 `MetaHumanPerformance` 资产是核心操作。
```cpp
// 模拟通过工厂创建一个新的 MetaHumanPerformance 资产（来源：推断自 UMetaHumanFaceAnimationSolverFactoryNew 逻辑）
UObject* NewAsset = UFactory::StaticCreateNewAsset(
    UMetaHumanPerformance::StaticClass(),
    InParent,
    InName,
    InFlags,
    Context,
    Warn
);
```

### 进阶用法
该插件的强大之处在于其模块化管线。开发者可以组合使用 `MetaHumanPipeline`、`MetaHumanFaceFittingSolver`、`MetaHumanFaceAnimationSolver` 等模块来构建自定义的动画生成流程。例如，一个典型的处理流程可能涉及：
1.  **数据摄入**: 通过 `MetaHumanFootageIngest` 或 `MetaHumanCaptureSource` 导入原始数据。
2.  **追踪与求解**: 使用 `MetaHumanFaceContourTracker` 追踪面部特征点，再由 `MetaHumanFaceFittingSolver` 和 `MetaHumanFaceAnimationSolver` 将数据拟合到MetaHuman骨骼。
3.  **输出与控制**: 通过 `MetaHumanPerformance` 生成动画资产，并利用 `MetaHumanSequencer` 将其集成到关卡序列中。

## Demo 示例
由于该插件工作流高度依赖编辑器交互和资产系统，一个最小的“代码化”示例通常是创建一个用于处理 `MetaHumanPerformance` 的异步任务。此示例展示了如何从C++启动一个面部动画处理任务，体现了其管线驱动的架构。
```cpp
// MetaHumanAnimationProcessor.h
#pragma once
#include “CoreMinimal.h”
#include “MetaHumanPerformance/Classes/MetaHumanPerformance.h”

class FMetaHumanAnimationProcessor
{
public:
    void ProcessPerformanceAsset(UMetaHumanPerformance* InPerformanceAsset);

private:
    // 内部处理函数，可能调用各个求解器模块
    void RunFaceAnimationPipeline(UMetaHumanPerformance* InAsset);
};
```
```cpp
// MetaHumanAnimationProcessor.cpp
#include “MetaHumanAnimationProcessor.h”

void FMetaHumanAnimationProcessor::ProcessPerformanceAsset(UMetaHumanPerformance* InPerformanceAsset)
{
    if (!InPerformanceAsset) return;

    // 异步启动复杂的面部动画求解管线
    AsyncTask(ENamedThreads::AnyBackgroundThreadNormalTask, [this, InPerformanceAsset]()
    {
        RunFaceAnimationPipeline(InPerformanceAsset);
        // 处理完成后，回到游戏线程更新资产状态
        AsyncTask(ENamedThreads::GameThread, [InPerformanceAsset]()
        {
            // 标记资产处理完成等操作
        });
    });
}

void FMetaHumanAnimationProcessor::RunFaceAnimationPipeline(UMetaHumanPerformance* InAsset)
{
    // 此处会集成 MetaHumanFaceAnimationSolver, MetaHumanFaceFittingSolver 等模块的逻辑
    // 将输入数据（如视频帧序列）转化为最终的面部动画曲线
}
```

## 模块依赖
要使用或扩展MetaHuman Animator插件的功能，你的模块可能需要依赖以下独特模块（取决于具体功能）：
| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | 核心基础功能和类型定义。 |
| `MetaHumanIdentity` | MetaHuman角色身份、骨骼和控制绑定。 |
| `MetaHumanPerformance` | 管理和存储面部动画性能数据（输出结果）。 |
| `MetaHumanPipeline` | 构建和执行模块化的动画处理管线。 |
| `MetaHumanFaceAnimationSolver` | 核心的面部动画求解算法。 |
| `MetaHumanFaceFittingSolver` | 将追踪数据拟合到MetaHuman模型的求解器。 |
| `MetaHumanCaptureProtocolStack` | 与各种动作捕捉设备和协议通信。 |

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出，避免冲突 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复MetaHuman角色上的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪模式下过滤可视化物体，提升性能/清晰度 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持将动画序列导出到已有的网格体上 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复与序列器相关的缓存问题 |

### 维护评价
**活跃维护**。MetaHuman Animator是Epic Games在MetaHuman技术栈中的核心产品级插件，从最近（2026年5月）密集的更新记录可以看出它正处于**非常活跃**的开发与维护中。更新内容涵盖了功能增强（如身体追踪集成）、渲染问题修复以及工作流优化（如动画导出），表明其仍在快速迭代。该插件是官方支持的、生产就绪的解决方案，推荐用于所有需要MetaHuman面部动画的项目。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档]() (注：.uplugin中未提供)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Tests)