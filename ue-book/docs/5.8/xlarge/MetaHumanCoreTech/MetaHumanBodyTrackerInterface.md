# MetaHuman Core Tech

> The core technology behind the MetaHuman Creator and MetaHuman Animator plugins.

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman核心科技 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（可能包含基础蓝图资产和配置） |
| 模块 | `MetaHumanBodyTrackerInterface` (Runtime), `MetaHumanCaptureData` (Runtime), `MetaHumanCoreTech` (Runtime), `MetaHumanCoreTechLib` (Runtime), `MetaHumanImageViewer` (Runtime), `MetaHumanPipelineCore` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（未知） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib) | |

## 用途

MetaHumanCoreTech 是 Epic Games MetaHuman 技术栈的核心基础库。它并非一个直接面向最终用户的功能性插件，而是一个为 `MetaHuman Creator` 和 `MetaHuman Animator` 提供底层能力的基础设施层。该插件主要解决了以下问题：

1.  **提供统一的身体追踪框架**：通过 `MetaHumanBodyTrackerInterface` 模块，定义了身体追踪器的标准接口（`IMetaHumanBodyTrackerInterface`），允许第三方或 Epic 内部实现不同的追踪算法（如从视频中提取身体动画数据）并集成到管线中。
2.  **构建数据处理管线**：`MetaHumanPipelineCore` 和 `MetaHumanCoreTechLib` 模块提供了核心的管线（Pipeline）架构，用于处理从原始数据（如视频、图像）到最终 MetaHuman 动画输出的整个数据流。这包括图像处理、面部动画、身体动画等多个阶段的协调。
3.  **封装底层核心算法**：`MetaHumanCoreTechLib` 很可能包含了用于人体形状建模（如 SMPL 模型）、动画重定向、骨骼绑定等核心计算逻辑。这些被封装成库，供上层插件调用。
4.  **管理采集数据**：`MetaHumanCaptureData` 和 `MetaHumanImageViewer` 模块负责处理和管理用于创建 MetaHuman 的原始数据（如多角度图像序列），为数据准备阶段提供支持。

简而言之，这个插件的存在是为了将 MetaHuman 技术中复杂、通用的计算和框架部分独立出来，形成一个稳定的基础，使得更上层的两个旗舰插件（Creator 和 Animator）可以专注于它们各自的用户体验和业务逻辑。

## 使用场景

你几乎不会直接使用这个插件，但当以下情况发生时，你正在间接依赖它：

*   **你在使用 MetaHuman Animator**：当你从视频中提取面部和身体动画并应用到 MetaHuman 角色时，其底层的身体追踪（可能通过 `MetaHumanBodyTrackerInterface`）、数据处理管线（`MetaHumanPipelineCore`）都在此插件的支持下运行。
*   **你在使用 MetaHuman Creator**：当你在云端或本地调整数字人的外貌、服装时，其形状生成、资产绑定等核心计算可能源自 `MetaHumanCoreTechLib`。
*   **你需要开发自定义的 MetaHuman 工作流工具**：如果你想要开发一个工具来批量处理数字人动画，或者集成一个不同的身体追踪算法，你就需要直接依赖和使用本插件提供的 `IMetaHumanBodyTrackerInterface` 接口和管线系统。

## 蓝图用法

本插件主要提供接口和底层库，公开给蓝图的直接节点较少。主要的蓝图交互可能通过继承和实现接口来完成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| (接口方法) `ExtendPipeline` | 身体追踪器扩展管线的核心方法，用于注入追踪逻辑。 | `IMetaHumanBodyTrackerInterface` |
| (接口方法) `GetBodyDriverActorClass` | 获取用于驱动身体动画的 Actor 类。 | `IMetaHumanBodyTrackerInterface` |
| `Initialize` / `Update` | 身体驱动器 Actor 的生命周期和动画更新方法。 | `AMetaHumanBodyDriverActorInterface` |

### 使用示例（蓝图描述）

由于这是一个底层接口插件，蓝图中的直接使用不常见。更典型的方式是在 C++ 中实现 `IMetaHumanBodyTrackerInterface`，然后将该实现作为“模块化特性”注册。上层的 MetaHuman 插件在运行时会查找并使用这些已注册的追踪器。

## C++ 用法

本插件的 C++ 用法核心在于实现其定义的接口，特别是 `IMetaHumanBodyTrackerInterface`，以扩展 MetaHuman 的数据处理管线。

### 头文件引入

```cpp
#include "IMetaHumanBodyTrackerInterface.h" // 来自 MetaHumanBodyTrackerInterface 模块
```

### 基本用法

1.  **实现身体追踪器接口**：
    你需要创建一个类来继承并实现 `IMetaHumanBodyTrackerInterface` 的所有纯虚函数。

    ```cpp
    // MyBodyTracker.h
    #pragma once
    #include "IMetaHumanBodyTrackerInterface.h"

    class FMyBodyTracker : public IMetaHumanBodyTrackerInterface
    {
    public:
        // IModularFeature 接口
        virtual bool ExtendPipeline(const FBodyTrackerInputParams& InBodyTrackerInputParams, UE::MetaHuman::Pipeline::FPipeline& InOutPipeline, FBodyTrackerOutputParams& OutBodyTrackerOutputParams) const override;
        virtual TSubclassOf<AMetaHumanBodyDriverActorInterface> GetBodyDriverActorClass() const override;
        // ... 实现其他纯虚函数 ...
    };
    ```

2.  **注册为模块化特性**：
    在你的模块启动函数中，将你的追踪器注册到模块化特性系统。

    ```cpp
    // MyBodyTrackerModule.cpp
    #include "IModularFeatures.h"

    void FMyBodyTrackerModule::StartupModule()
    {
        // 创建追踪器实例
        TSharedPtr<FMyBodyTracker> MyTracker = MakeShared<FMyBodyTracker>();
        // 注册为模块化特性
        IModularFeatures::Get().RegisterModularFeature(IMetaHumanBodyTrackerInterface::GetModularFeatureName(), MyTracker.Get());
    }

    void FMyBodyTrackerModule::ShutdownModule()
    {
        IModularFeatures::Get().UnregisterModularFeature(IMetaHumanBodyTrackerInterface::GetModularFeatureName(), MyTracker.Get());
    }
    ```

### 进阶用法

在 `ExtendPipeline` 实现中，你需要构建你的自定义管线节点，并将其连接到输入参数提供的源节点（`ImageSrcNode`, `FaceAnimSrcNode`）上。你需要处理 `FBodyTrackerInputParams` 中的配置，如追踪模式、帧范围等，并将结果通过 `FBodyTrackerOutputParams` 输出。

## Demo 示例

以下是一个最小化的身体追踪器接口实现示例，展示了基本的框架和注册过程。

**MyBodyTracker.h**
```cpp
#pragma once
#include "IMetaHumanBodyTrackerInterface.h"

// 一个最小化的身体追踪器实现
class FMinimalBodyTracker : public IMetaHumanBodyTrackerInterface
{
public:
    // 扩展管线，在这里添加你的自定义处理节点
    virtual bool ExtendPipeline(const FBodyTrackerInputParams& InInput, UE::MetaHuman::Pipeline::FPipeline& InPipeline, FBodyTrackerOutputParams& OutOutput) const override;
    // 返回一个默认的驱动器 Actor 类（可以返回 AActor 的子类）
    virtual TSubclassOf<AMetaHumanBodyDriverActorInterface> GetBodyDriverActorClass() const override;
    // 返回 ControlRig 资产的路径
    virtual FString GetBodyControlRigAssetPath() const override;
    // ... 其他必要的虚函数实现 ...
};
```

**MyBodyTracker.cpp**
```cpp
#include "MyBodyTracker.h"

bool FMinimalBodyTracker::ExtendPipeline(const FBodyTrackerInputParams& InInput, UE::MetaHuman::Pipeline::FPipeline& InPipeline, FBodyTrackerOutputParams& OutOutput) const
{
    // 在这里添加你的处理逻辑。
    // 例如，你可以创建一个新的节点连接到 InInput.ImageSrcNode
    // 并设置 OutOutput.AnimationPinName 为新节点输出动画数据的引脚名称。
    // 这是一个简化的示例，实际实现会复杂得多。
    return true;
}

TSubclassOf<AMetaHumanBodyDriverActorInterface> FMinimalBodyTracker::GetBodyDriverActorClass() const
{
    // 返回一个默认的 AActor 子类，实际项目中应返回你自己的驱动器类
    return AActor::StaticClass();
}

FString FMinimalBodyTracker::GetBodyControlRigAssetPath() const
{
    // 返回一个有效的 ControlRig 资产路径，例如：
    return TEXT("/Game/MetaHuman/Common/ControlRig/Body_CR.Body_CR");
}

// ... 其他函数的简单实现 ...
```

## 模块依赖

本插件的各个模块相互依赖，并且依赖一些非标准模块。

| 模块 | 用途 |
|---|---|
| `MetaHumanImageViewer` | 用于查看和处理 MetaHuman 采集数据的图像序列。 |
| `OpenCV` / `OpenCVHelper` | 提供计算机视觉功能，用于图像处理和可能的身体特征点检测。 |
| `DirectoryWatcher` | 监视文件目录变化，可能用于自动发现和处理新的采集数据。 |
| `UnrealEd` | 编辑器模块依赖，用于在编辑器中扩展细节面板（如 `CustomizePerformanceDetails`）和处理资产。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `7f10fbf1` | [MetaHuman] Titan v9.0.8 | MetaHuman Titan 工具链更新至 v9.0.8 版本。 |
| 2026-05-26 | `cfa3dac6` | [MetaHuman] Titan v9.0.7 | MetaHuman Titan 工具链更新至 v9.0.7 版本。 |
| 2026-05-21 | `e936df4b` | [MetaHuman] Titan v9.0.6 | MetaHuman Titan 工具链更新至 v9.0.6 版本。 |
| 2026-05-20 | `c5214fb2` | [MetaHumanBodyTracker] allow foot-locking to be toggled on or off | 为身体追踪器添加了脚部锁定（Foot-locking）的开关控制功能。 |
| 2026-05-19 | `a29cddd9` | [MHA] Crash during MHC assembly with body performance | 修复了在 MetaHuman Creator 中组装带有身体动画的数字人时发生的崩溃问题。 |

### 维护评价

*   **维护状态**：**活跃维护中**。从 git 历史看，最近一周内有连续多次提交，表明此插件正在被积极开发和更新。
*   **内容**：更新内容集中在 Titan 工具链版本迭代、功能增强（如脚部锁定开关）和关键 Bug 修复（如组装崩溃）。
*   **推荐使用**：作为 Epic 官方 MetaHuman 技术栈的**基础组件**，它是稳定且必要的。如果你在使用 MetaHuman Creator 或 Animator，你必然依赖它。如果你计划进行深度自定义开发，则需要理解和遵循它的接口设计。虽然它是底层库，但由于其官方和基础地位，推荐在相关开发中使用。

## 相关链接

*   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib)
*   官方文档：该插件作为内部基础库，通常不提供独立文档。相关功能文档可在 MetaHuman Creator 和 MetaHuman Animator 的官方文档中找到。