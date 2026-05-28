# MetaHuman Face Contour Tracker

> MetaHuman 面部轮廓追踪器资产，用于存储和加载各类面部特征（如面部、眉毛、眼睛、嘴部等）的追踪模型。

| 属性 | 值 |
|---|---|
| 中文名 | 面部轮廓追踪器 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（追踪器资产、模型数据） |
| 模块 | `MetaHumanFaceContourTracker` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-11-03 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceContourTracker) | |

## 用途

`MetaHumanFaceContourTracker` 模块的核心是提供 `UMetaHumanFaceContourTrackerAsset` 资产类型。此资产是一个容器，用于存储和管理一组预训练的神经网络（NNE）模型，这些模型专门用于从图像或视频中检测和追踪人脸的不同面部特征点（例如面部轮廓、眉毛、眼睛、鼻子、嘴唇、下巴和牙齿）。它是 MetaHuman 工具链中的关键组件，为后续的“身份（Identity）”创建和“表演（Performance）”捕捉处理提供基础的面部几何信息。该资产会动态加载指定的 NNE 模型，并在需要时在 GPU 上运行它们以进行高效的推理。

## 使用场景

- **创建 MetaHuman 身份资产**：当你从扫描数据或照片创建 MetaHuman 角色时，需要此追踪器资产来精确地定位面部关键点，以便后续进行面部拟合（Fitting）。
- **处理 MetaHuman 表演数据**：在将视频或深度摄像机数据转换为 MetaHuman 角色动画（Performance）时，追踪器用于从每一帧图像中提取面部特征运动轨迹。
- **自定义或扩展追踪流程**：开发者可以通过替换或修改追踪器资产中的 NNE 模型数据，来尝试使用自定义的、针对特定场景优化的面部追踪模型。

## 蓝图用法

该模块主要为底层运行时资产，其核心的 `UMetaHumanFaceContourTrackerAsset` 类提供的公开蓝图接口相对有限，更多功能通过编辑器或 C++ 驱动。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Load Default Tracker` | 加载默认的面部轮廓追踪器资产 | `UMetaHumanFaceContourTrackerAsset` |
| `Load Trackers` | 异步加载追踪器资产中指定的 NNE 模型 | `UMetaHumanFaceContourTrackerAsset` |
| `Can Process` | 检查追踪器是否已加载所有必需的模型并可以进行处理 | `UMetaHumanFaceContourTrackerAsset` |

### 使用示例（蓝图描述）

1.  **获取默认追踪器**：在蓝图中，调用 `Load Default Tracker` 静态函数，它会返回一个 `UMetaHumanFaceContourTrackerAsset` 对象，这是最常用的入口点。
2.  **检查并加载**：获取追踪器对象后，可以调用 `Can Process` 检查状态。如果未加载，可以调用 `Load Trackers` 来触发模型的异步加载，并传入一个回调函数在加载完成后执行后续逻辑（例如开始图像处理）。

## C++ 用法

主要涉及 `UMetaHumanFaceContourTrackerAsset` 的创建、加载和使用。

### 头文件引入

```cpp
#include "MetaHumanFaceContourTrackerAsset.h"
```

### 基本用法

加载默认追踪器资产并检查其状态。
（来源: 核心资产类用法）

```cpp
// 加载系统默认的面部轮廓追踪器
TObjectPtr<UMetaHumanFaceContourTrackerAsset> Tracker = UMetaHumanFaceContourTrackerAsset::LoadDefaultTracker();
if (Tracker && Tracker->CanProcess())
{
    // 追踪器已就绪，可以用于处理图像
    UE_LOG(LogTemp, Log, TEXT("Default face contour tracker is loaded and ready."));
}
else
{
    // 追踪器未加载或不可用
    UE_LOG(LogTemp, Warning, TEXT("Face contour tracker is not ready."));
}
```

### 进阶用法

异步加载追踪器模型，并在完成后执行操作。
（来源: 异步加载机制分析）

```cpp
UMetaHumanFaceContourTrackerAsset* MyTracker = /* 从某处获取或创建的追踪器资产 */;
if (MyTracker && !MyTracker->IsLoadingTrackers() && !MyTracker->CanProcess())
{
    MyTracker->LoadTrackers(true, [MyTracker](bool bSuccess)
    {
        if (bSuccess && MyTracker->CanProcess())
        {
            // 加载成功，可以开始使用 MyTracker 进行面部追踪
            UE_LOG(LogTemp, Log, TEXT("Tracker models loaded asynchronously."));
            // ... 执行实际的追踪逻辑
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("Failed to load tracker models."));
        }
    });
}

// 可以在需要时取消加载
if (MyTracker->IsLoadingTrackers())
{
    MyTracker->CancelLoadTrackers();
}
```

## Demo 示例

一个最小化的示例，展示如何创建和初始化一个 `MetaHumanFaceContourTracker` 资产。

```cpp
// MyTrackerComponent.h
#pragma once
#include "Components/ActorComponent.h"
#include "MetaHumanFaceContourTrackerAsset.h"
#include "MyTrackerComponent.generated.h"

UCLASS(ClassGroup=(MetaHuman), meta=(BlueprintSpawnableComponent))
class UMyTrackerComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyTrackerComponent();

    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = "Face Tracking")
    TObjectPtr<UMetaHumanFaceContourTrackerAsset> ContourTracker;

    UFUNCTION(BlueprintCallable, Category = "Face Tracking")
    void StartTrackerLoading();

    UFUNCTION(BlueprintCallable, Category = "Face Tracking")
    bool IsTrackerReady() const;
};
```

```cpp
// MyTrackerComponent.cpp
#include "MyTrackerComponent.h"

UMyTrackerComponent::UMyTrackerComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMyTrackerComponent::BeginPlay()
{
    Super::BeginPlay();

    // 如果没有指定追踪器资产，则使用默认的
    if (!ContourTracker)
    {
        ContourTracker = UMetaHumanFaceContourTrackerAsset::LoadDefaultTracker();
    }
}

void UMyTrackerComponent::StartTrackerLoading()
{
    if (ContourTracker && !ContourTracker->IsLoadingTrackers())
    {
        ContourTracker->LoadTrackers(false, [this](bool bSuccess)
        {
            if (bSuccess)
            {
                UE_LOG(LogTemp, Log, TEXT("Face Contour Tracker loaded for component."));
            }
        });
    }
}

bool UMyTrackerComponent::IsTrackerReady() const
{
    return ContourTracker && ContourTracker->CanProcess();
}
```

## 模块依赖

从 `MetaHumanFaceContourTracker.Build.cs` 分析，该模块依赖 MetaHuman 的核心技术库。

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | 提供 MetaHuman 底层核心算法和库支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 修复了启用身体追踪时关卡序列导出的错误 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复了 MetaHuman 上的渲染伪影问题 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 改进了身体追踪时的可视化对象过滤 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 新增为现有网格体导出动画序列的功能 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复了定序器的缓存问题 |

### 维护评价

该模块是 MetaHuman 工具链的核心运行时组件之一。从 git 记录看，它在近期（2026年5月）有非常密集的更新，主要集中在**修复渲染问题、改进功能（如动画序列导出）和优化身体追踪集成**。这表明它正处于**活跃维护**状态，并且随着 MetaHuman 工具的整体迭代而不断优化。由于其所属的 MetaHuman 插件是 Epic Games 的重点产品，预计将持续获得长期支持。推荐在涉及 MetaHuman 面部追踪或处理工作流的项目中使用此模块。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceContourTracker)
- [官方文档]() (无官方文档链接)
- [测试用例]() (未提供)