# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 数字人动画师工具包 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质、配置数据、测试资源等） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 0-1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一个用于创建、编辑和驱动高质量数字人（MetaHuman）角色的综合性工具包。它解决的核心问题是**将现实世界中的表演捕捉数据，转化为可驱动虚幻引擎中高保真 MetaHuman 角色面部和身体动画的完整流程**。

该插件不仅仅是一个简单的模型导入器，而是一个完整的端到端解决方案，涵盖了从**视频素材摄入**、**面部特征点追踪**、**身份拟合（Fitting）**、**动画求解（Solving）**，到最终在引擎中实时驱动或导出动画序列的全过程。它使得艺术家和技术美术能够高效地制作电影级数字人表演。

## 使用场景

*   你有一段演员面部表演的视频素材，需要将其转换为可用于 MetaHuman 角色的动画数据 → 使用 `MetaHumanFaceContourTracker` 和 `MetaHumanFaceFittingSolver` 模块。
*   你希望根据一张或几张照片，为一个 MetaHuman 角色匹配最接近的面部模型，作为后续动画的基础 → 使用 `MetaHumanIdentity` 和 `MetaHumanFaceFittingSolver`。
*   你需要批量处理多个捕捉数据文件，生成动画资产 → 使用 `MetaHumanBatchProcessor` 和 `MetaHumanPipeline`。
*   你正在开发一个需要实时驱动数字人面部表情的应用程序（如虚拟客服）→ 使用 `MetaHumanFaceAnimationSolver` 配合实时输入（如音频）。
*   你需要将基于物理模拟或求解器生成的动画数据，在 Sequencer 中进行精细编辑和合成 → 使用 `MetaHumanSequencer`。

## 蓝图用法

由于该插件是一个复杂的管线工具，其大部分高级工作流程通过编辑器工具和资产数据驱动，直接暴露给蓝图的可调用节点相对有限，更多是用于状态查询和事件回调。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `LoadFaceFittingSolvers` | 加载面部拟合所需的求解器数据 | `UMetaHumanFaceFittingSolver` |
| `LoadPredictiveSolver` | 加载用于性能准备（Performance Preparation）的预测性求解器 | `UMetaHumanFaceFittingSolver` |
| `CanProcess` | 检查当前面部拟合求解器是否可以执行处理（例如，所有必要数据是否已加载） | `UMetaHumanFaceFittingSolver` |
| `OnInternalsChanged` | 一个委托（Delegate），当求解器内部状态（如配置更改）发生变化时广播 | `UMetaHumanFaceFittingSolver` |

### 使用示例（蓝图描述）

你无法直接在蓝图中“拖拽”出一个完整的面部追踪流程。这些节点主要用于**在插件内部或高级自定义工具中监控和控制求解器的状态**。

例如，你可以在一个自定义的编辑器工具蓝图中：
1.  持有一个 `UMetaHumanFaceFittingSolver` 对象的引用。
2.  调用 `LoadFaceFittingSolvers` 来确保求解器准备就绪。
3.  绑定到 `OnInternalsChanged` 代理，以便在求解器配置更改时更新你的UI。
4.  在执行处理前，调用 `CanProcess` 进行检查。

## C++ 用法

该插件的 C++ API 主要用于其内部模块间的交互，或用于构建扩展该插件功能的编辑器工具。对于最终用户，主要使用的是其通过编辑器资产（如 `MetaHumanIdentity`， `CaptureData`）暴露的工作流。

### 头文件引入

```cpp
#include "MetaHumanFaceFittingSolver.h"
```

### 基本用法

以下示例展示如何配置和使用 `UMetaHumanFaceFittingSolver` 来获取拟合数据。这通常发生在插件管线的内部逻辑中。
(来源: `Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceFittingSolver/Public/MetaHumanFaceFittingSolver.h`)

```cpp
// 假设已经存在一个 UCaptureData 对象，代表待处理的捕捉数据
UCaptureData* MyCaptureData = ...;

// 获取或创建一个面部拟合求解器实例
UMetaHumanFaceFittingSolver* FaceSolver = GetMutableDefault<UMetaHumanFaceFittingSolver>();

// （可选）配置求解器使用的设备配置
FaceSolver->bOverrideDeviceConfig = true;
FaceSolver->DeviceConfig = MyCustomMetaHumanConfig;

// 加载求解器所需的数据
FaceSolver->LoadFaceFittingSolvers();

if (FaceSolver->CanProcess())
{
    // 获取用于拟合的模板数据，可用于传递给底层的拟合算法
    FString TemplateData = FaceSolver->GetFittingTemplateData(MyCaptureData);
    
    // 获取拟合配置数据
    FString ConfigData = FaceSolver->GetFittingConfigData(MyCaptureData);
    
    // ... 将这些数据字符串传递给实际的拟合管线执行 ...
}
```

### 进阶用法

更复杂的用法涉及监听求解器状态变化，这在构建需要与求解器配置同步的UI时很有用。
(来源: `Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceFittingSolver/Public/MetaHumanFaceFittingSolver.h`)

```cpp
// 在一个管理器类中
void UMyFittingManager::BindToSolver()
{
    UMetaHumanFaceFittingSolver* FaceSolver = GetMutableDefault<UMetaHumanFaceFittingSolver>();
    
    // 绑定到内部状态变更代理
    FaceSolver->OnInternalsChanged().AddUObject(this, &UMyFittingManager::OnSolverStateChanged);
}

void UMyFittingManager::OnSolverStateChanged()
{
    UE_LOG(LogTemp, Log, TEXT("Face Fitting Solver configuration has changed."));
    // 在此处更新你的UI或重新验证拟合状态
    RefreshUI();
}
```

## Demo 示例

由于 `MetaHumanFaceFittingSolver` 主要是一个配置和数据管理类，其“最小示例”即为上述 C++ 用法中的基本配置和查询。一个完整的演示需要结合 `UCaptureData` 资产和整个 `MetaHumanAnimator` 编辑器工具。

下面是一个非常简化的、概念性的头文件，展示如何在一个自定义类中集成求解器管理逻辑。

```cpp
// MyFittingProcessor.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MetaHumanFaceFittingSolver.h"
#include "MyFittingProcessor.generated.h"

UCLASS()
class UMyFittingProcessor : public UObject
{
    GENERATED_BODY()

public:
    UMyFittingProcessor();

    /** 初始化求解器并准备处理 */
    void Initialize();

    /** 尝试处理给定的捕捉数据 */
    bool ProcessCaptureData(UCaptureData* InCaptureData);

private:
    UPROPERTY()
    TObjectPtr<UMetaHumanFaceFittingSolver> FaceSolver;

    void HandleSolverChanged();
};
```

```cpp
// MyFittingProcessor.cpp
#include "MyFittingProcessor.h"
#include "CaptureData.h" // 假设的捕捉数据类

UMyFittingProcessor::UMyFittingProcessor()
{
    FaceSolver = GetMutableDefault<UMetaHumanFaceFittingSolver>();
}

void UMyFittingProcessor::Initialize()
{
    if (FaceSolver)
    {
        FaceSolver->LoadFaceFittingSolvers();
        FaceSolver->OnInternalsChanged().AddUObject(this, &UMyFittingProcessor::HandleSolverChanged);
    }
}

bool UMyFittingProcessor::ProcessCaptureData(UCaptureData* InCaptureData)
{
    if (!FaceSolver || !InCaptureData || !FaceSolver->CanProcess())
    {
        return false;
    }

    // 获取配置字符串并传递给实际的处理逻辑（此处为示意）
    FString Config = FaceSolver->GetFittingConfigData(InCaptureData);
    FString Template = FaceSolver->GetFittingTemplateData(InCaptureData);
    
    // ... 调用实际的拟合算法 ...
    
    return true;
}

void UMyFittingProcessor::HandleSolverChanged()
{
    UE_LOG(LogTemp, Warning, TEXT("Solver configuration changed in MyFittingProcessor."));
}
```

## 模块依赖

该插件包含众多子模块，以下是针对当前模块 `MetaHumanFaceFittingSolver` 的独特依赖。使用该插件的其他功能可能需要不同的依赖。

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心算法库，提供底层的数据格式和处理工具。 |
| `MetaHumanConfig` | 提供 `UMetaHumanConfig` 配置资产类，用于管理设备参数和求解器设置。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时，禁用关卡序列导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 模型上的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤掉可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

**评价：活跃维护，推荐使用。**

*   **活跃度**：从近期 git 历史看，该插件正在被**积极开发和维护**。最近的提交集中在 2026 年 5 月，内容涵盖新功能（为现有网格导出动画）、Bug 修复（渲染瑕疵、缓存问题）以及功能优化（身体追踪时的行为调整）。
*   **成熟度**：插件 `.uplugin` 明确标记为 `IsBetaVersion: false`, `IsExperimentalVersion: false`，表明它已达到正式发布状态，可作为生产工具使用。
*   **来源与支持**：由 Epic Games 官方开发和维护，是 MetaHuman 技术栈的核心组成部分，拥有可靠的技术支持和持续更新保障。
*   **注意事项**：该插件非常庞大（544个源文件），模块众多，学习曲线较陡。它主要面向技术美术、角色动画师和开发者，而非完全不懂技术的美术人员。其功能实现依赖于特定的外部算法库（MetaHumanCoreTechLib）。
*   **建议**：对于需要高质量、程序化生成或驱动 MetaHuman 动画的项目，**强烈推荐使用**。对于仅需要静态 MetaHuman 角色的简单项目，可能无需引入如此复杂的工具链。

## 相关链接

*   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
*   [官方文档](https://docs.unrealengine.com/en-US/Plugins/MetaHuman/) （假设的官方文档链接，请根据实际情况调整）
*   测试用例路径：`Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/` 下的 `*Test` 模块（如 `MetaHumanControlsConversionTest`）。