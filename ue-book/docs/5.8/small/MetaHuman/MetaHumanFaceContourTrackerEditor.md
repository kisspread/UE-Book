# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman动画器 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产、材质、脚本等） |
| 模块 | `MetaHumanCore` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanSpeech2Face` (Runtime), ...等 28 个模块 |
| 实验性 | 否 |
| 创建时间 | 2022-05-04 (推断) |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 工具包，用于从视频源（如 iPhone 深度摄像头或普通视频）创建高保真、可驱动的 MetaHuman 数字人。它不仅仅是一个简单的资产导入工具，而是一个完整的端到端工作流解决方案。其核心功能是：通过追踪视频中的人脸和身体，生成精确的面部动画、身体动画，并将其应用于 MetaHuman 角色模型，最终可以在 Sequencer 中导出为动画序列。它解决了从真实世界表演到虚拟角色动画的高保真、自动化转换问题。

## 使用场景

- 你是一名独立开发者，希望为游戏快速创建一个以真人演员为原型的数字人角色。
- 你正在开发一个虚拟制片项目，需要将演员在绿幕前的表演实时或离线地驱动到虚拟 MetaHuman 角色上。
- 你需要将预先录制好的面部表演视频，批量转换为可复用的动画资产，用于过场动画或对话系统。
- 你希望使用 iPhone 的深度摄像头数据来创建更精准的面部动画，比纯视频追踪更真实。

## 蓝图用法

MetaHuman Animator 的蓝图功能高度模块化，核心节点围绕 `MetaHumanIdentity`、`MetaHumanPerformance` 和 `MetaHumanPipeline` 展开。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create MetaHuman Identity` | 从一个或多个视频片段创建或更新一个 MetaHuman Identity 资产。 | `UMetaHumanIdentity` |
| `Run Face Tracker` | 对指定的视频媒体源运行面部轮廓追踪，生成追踪数据。 | `UMetaHumanFaceContourTracker` |
| `Run Face Animation Solver` | 使用追踪数据和配置来解算面部动画。 | `UMetaHumanFaceAnimationSolver` |
| `Run Body Tracker` | 对视频运行身体姿态追踪。 | `UMetaHumanBodyTracker` |
| `Export Animation Sequence` | 将解算完成的动画数据导出为 UAnimSequence 资产。 | `UMetaHumanPerformance` |
| `Execute Pipeline` | 执行一个预定义的处理流水线，自动化从追踪到导出的全过程。 | `UMetaHumanPipeline` |

### 使用示例（蓝图描述）

1.  **创建 Identity**：拖入一个 `Create MetaHuman Identity` 节点。连接一个包含演员正面和侧面视频的媒体源资产。这会生成一个 `MetaHumanIdentity` 资产，它是所有后续操作的“身份证”。
2.  **运行追踪与解算**：使用 `Run Face Tracker` 节点，输入刚刚创建的 Identity 和一段表演视频。追踪完成后，将结果输入给 `Run Face Animation Solver` 节点进行解算。
3.  **应用与导出**：将解算得到的动画数据通过 `Apply to Control Rig` 节点应用到一个 MetaHuman 角色的 Control Rig 上进行预览。满意后，使用 `Export Animation Sequence` 节点将动画烘焙到一个 `UAnimSequence` 资产中，供游戏或 Sequencer 使用。

## C++ 用法

MetaHuman Animator 的 C++ API 主要面向希望深度集成或扩展工作流的开发者。当前模块 `MetaHumanFaceContourTrackerEditor` 展示了编辑器扩展点。

### 头文件引入

```cpp
// 用于创建面部轮廓追踪器资产的工厂
#include "MetaHumanFaceContourTrackerAssetFactoryNew.h"
// 用于定义资产在编辑器中的行为（如显示颜色、打开方式）
#include "AssetDefinitions/AssetDefinition_MetaHumanFaceContourTracker.h"
```

### 基本用法

以下示例展示了如何在 C++ 中以编程方式创建一个面部轮廓追踪器资产，这在自动化工具链或单元测试中很有用。代码灵感来源于 `UMetaHumanFaceContourTrackerAssetFactoryNew` 的实现。

```cpp
// 基于 MetaHumanFaceContourTrackerAssetFactoryNew.cpp
UObject* CreateFaceContourTrackerAsset(UObject* InParent, const FName& InName)
{
    // 获取要创建的资产类
    UClass* AssetClass = UMetaHumanFaceContourTrackerAsset::StaticClass();

    // 使用对象工厂创建新资产，与编辑器中“右键->新建”行为一致
    UMetaHumanFaceContourTrackerAsset* NewAsset = NewObject<UMetaHumanFaceContourTrackerAsset>(
        InParent, // 外部对象（如文件夹）
        AssetClass,
        InName, // 资产名称
        RF_Public | RF_Standalone | RF_Transactional
    );

    return NewAsset;
}
```

### 进阶用法

MetaHuman Animator 的强大之处在于 `MetaHumanPipeline` 模块。你可以组合多个步骤定义一个完整的自动化流程。

```cpp
// 伪代码，展示Pipeline概念
// 1. 加载或定义Pipeline资产（包含步骤列表）
// 2. 为Pipeline准备输入（媒体源、Identity资产等）
// 3. 异步执行Pipeline，并绑定进度和完成回调
// 4. 在完成回调中获取输出的动画序列资产
```

## Demo 示例

以下是一个最小化示例，演示如何初始化 MetaHuman 工作流的核心组件。

```cpp
// MetaHumanMinimalDemo.h
#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MetaHumanMinimalDemo.generated.h"

class UMetaHumanIdentity;
class UMediaSource;

UCLASS()
class UMetaHumanMinimalDemoSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category = "MetaHumanDemo")
    void CreateIdentityFromMedia(UMediaSource* MediaSource);

private:
    UPROPERTY()
    TWeakObjectPtr<UMetaHumanIdentity> CurrentIdentity;
};
```

```cpp
// MetaHumanMinimalDemo.cpp
#include "MetaHumanMinimalDemo.h"
#include "MetaHumanIdentity.h" // 核心Identity资产类
// 包含其他需要的MetaHuman头文件...

void UMetaHumanMinimalDemoSubsystem::CreateIdentityFromMedia(UMediaSource* MediaSource)
{
    if (!MediaSource) return;

    // 创建一个临时的包来存储资产
    UPackage* TempPackage = CreatePackage(nullptr, TEXT("/Temp/MetaHumanDemoIdentity"));

    // 创建MetaHuman Identity资产
    CurrentIdentity = NewObject<UMetaHumanIdentity>(TempPackage, UMetaHumanIdentity::StaticClass(), TEXT("DemoIdentity"), RF_Public | RF_Standalone);

    if (CurrentIdentity.IsValid())
    {
        // 初始化Identity（这会触发内部模块的设置）
        CurrentIdentity->Initialize();

        // 通常下一步会调用类似 SetMediaSource(MediaSource) 的函数来绑定视频源
        // 然后可以启动追踪流程，但此简化示例仅展示对象创建
        UE_LOG(LogTemp, Log, TEXT("MetaHuman Identity created successfully for demo."));
    }
}
```

## 模块依赖

要使用 MetaHuman Animator 的核心功能，你的模块通常需要依赖以下关键模块。这取决于你具体要使用哪个功能。

| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | 提供核心基础类、工具和配置管理 |
| `MetaHumanIdentity` | 处理“数字人身份”的创建、管理与资产化 |
| `MetaHumanPerformance` | 处理表演数据（追踪结果）的管理与动画导出 |
| `MetaHumanPipeline` | 提供可配置的处理流水线框架，用于自动化工作流 |
| `MetaHumanFaceAnimationSolver` | 负责从追踪数据解算出面部动画 |
| `MetaHumanFaceContourTracker` | 负责视频中面部关键点的追踪 |
| `MetaHumanCaptureSource` | 提供不同视频源（如iPhone, Webcam）的抽象接口 |
| `MetaHumanSDKEditor` | 提供编辑器集成、资产自定义等（仅编辑器模块） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出，修复了同时使用两种功能时的冲突 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复了 MetaHuman 模型上的渲染瑕疵问题 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 进行身体追踪时，过滤掉不必要的可视化对象，优化编辑器显示 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 新增功能：可以为已存在的网格体（而非仅MetaHuman）导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复了与 Sequencer 缓存相关的问题，提升了稳定性 |

### 维护评价

**活跃维护**。MetaHuman Animator 是 Epic Games 战略级产品 MetaHuman 的核心工具链，一直处于密集的开发和维护中。从近期的提交记录看，团队不仅在修复 bug（如渲染瑕疵、缓存问题），还在持续添加新功能（如支持为现有网格体导出动画、优化身体追踪与序列导出的协同）。插件创建时间不长，且更新频率很高，表明它是一个仍在快速演进的核心产品。**强烈推荐**需要创建高保真人形数字人动画的项目使用，但需注意其版本迭代可能带来 API 变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/metahuman-animator-in-unreal-engine/) (MetaHuman 官方文档页)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest) (Controls转换测试示例)