# MetaHuman Face Contour Tracker

> MetaHuman Animator 的官方 Unreal Engine 工具包（MetaHuman 面部轮廓追踪器模块）

| 属性 | 值 |
|---|---|
| 中文名 | 面部轮廓追踪器 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MetaHumanFaceContourTracker` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026-05-20 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Face Contour Tracker 是 MetaHuman Animator 工具包中的一个核心运行时模块，专门负责面部关键特征点的实时检测与追踪。它通过加载并运行预训练的神经网络模型，从图像或视频序列中识别面部轮廓、眼睛、嘴巴、眉毛等区域的精细特征点，为后续的 MetaHuman 身份创建（MetaHuman Identity）和面部动画性能捕捉（MetaHuman Performance）提供关键的追踪数据。

**核心功能**：解决从原始视频或图像数据中稳定、精确地提取面部特征点的问题，这是实现从真实演员到数字 MetaHuman 角色表情迁移的基础环节。

## 使用场景

- 你需要创建 MetaHuman 数字人角色 → 用 MetaHuman Identity 工具时，需要先进行面部轮廓追踪。
- 你需要将真人演员的面部表演动画实时应用到 MetaHuman 身体上 → 用 MetaHuman Performance 工具时，依赖此模块进行实时特征点追踪。
- 你在开发一个需要从视频中分析面部表情的应用 → 可以直接使用此模块提供的面部特征点追踪功能。

## 蓝图用法

此模块主要面向 C++ 开发者和引擎内部使用，未提供公开的蓝图接口。其功能主要由 MetaHuman Identity 和 Performance 的编辑器工具在内部调用。

### 核心类

| 节点 | 说明 | 所在类 |
|---|---|---|
| `LoadDefaultTracker` | 加载默认的面部轮廓追踪器资产。 | `UMetaHumanFaceContourTrackerAsset` |
| `LoadTrackers` | 异步加载所有追踪器模型。 | `UMetaHumanFaceContourTrackerAsset` |
| `LoadTrackersSynchronous` | 同步加载所有追踪器模型（可能阻塞线程）。 | `UMetaHumanFaceContourTrackerAsset` |
| `CanProcess` | 检查追踪器模型是否已加载，可以开始处理。 | `UMetaHumanFaceContourTrackerAsset` |
| `SetNNEBackend` | 设置运行神经网络模型的后端（如 NNE 插件支持的不同后端）。 | `UMetaHumanFaceContourTrackerAsset` |

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanFaceContourTrackerAsset.h"
```

### 基本用法

获取并使用默认的面部轮廓追踪器资产来加载模型。

```cpp
// 来源：MetaHumanFaceContourTrackerAsset.h
// 获取默认的追踪器资产
UMetaHumanFaceContourTrackerAsset* TrackerAsset = UMetaHumanFaceContourTrackerAsset::LoadDefaultTracker();

if (TrackerAsset)
{
    // 设置 NNE 后端（可选）
    TrackerAsset->SetNNEBackend(TEXT("Default"));

    // 异步加载追踪器模型，并在加载完成后执行回调
    TrackerAsset->LoadTrackers(true, [TrackerAsset](bool bSuccess)
    {
        if (bSuccess && TrackerAsset->CanProcess())
        {
            UE_LOG(LogTemp, Log, TEXT("Face Contour Trackers loaded successfully."));
            // 现在可以开始使用 TrackerAsset 进行特征点追踪处理
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("Failed to load Face Contour Trackers."));
        }
    });
}
```

### 进阶用法

检查加载状态，并在需要时取消异步加载。

```cpp
// 来源：MetaHumanFaceContourTrackerAsset.h
UMetaHumanFaceContourTrackerAsset* TrackerAsset = UMetaHumanFaceContourTrackerAsset::LoadDefaultTracker();

// 开始加载
TrackerAsset->LoadTrackers(false, ...);

// 检查是否正在加载
if (TrackerAsset->IsLoadingTrackers())
{
    // 可以选择取消加载
    TrackerAsset->CancelLoadTrackers();
}
```

## Demo 示例

此模块为内部运行时模块，通常由 MetaHuman 工具链在后台使用。以下是一个简化的 C++ 示例，演示如何直接与 `UMetaHumanFaceContourTrackerAsset` 交互。

### MyFaceTrackerHelper.h
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MyFaceTrackerHelper.generated.h"

class UMetaHumanFaceContourTrackerAsset;

UCLASS()
class UMyFaceTrackerHelper : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    void InitializeFaceTracker();

    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    bool IsTrackerReady() const;

    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    void ShutdownTracker();

private:
    UPROPERTY()
    TObjectPtr<UMetaHumanFaceContourTrackerAsset> FaceTrackerAsset;

    void OnTrackersLoaded(bool bSuccess);
};
```

### MyFaceTrackerHelper.cpp
```cpp
#include "MyFaceTrackerHelper.h"
#include "MetaHumanFaceContourTrackerAsset.h"

void UMyFaceTrackerHelper::InitializeFaceTracker()
{
    // 加载默认资产
    FaceTrackerAsset = UMetaHumanFaceContourTrackerAsset::LoadDefaultTracker();
    if (FaceTrackerAsset)
    {
        // 异步加载模型
        FaceTrackerAsset->LoadTrackers(true, 
            [this](bool bSuccess) { OnTrackersLoaded(bSuccess); });
    }
}

bool UMyFaceTrackerHelper::IsTrackerReady() const
{
    return FaceTrackerAsset && FaceTrackerAsset->CanProcess();
}

void UMyFaceTrackerHelper::ShutdownTracker()
{
    if (FaceTrackerAsset && FaceTrackerAsset->IsLoadingTrackers())
    {
        FaceTrackerAsset->CancelLoadTrackers();
    }
    FaceTrackerAsset = nullptr;
}

void UMyFaceTrackerHelper::OnTrackersLoaded(bool bSuccess)
{
    if (bSuccess)
    {
        UE_LOG(LogTemp, Display, TEXT("MyFaceTrackerHelper: Face trackers loaded."));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("MyFaceTrackerHelper: Failed to load face trackers."));
    }
}
```

## 模块依赖

此模块的依赖主要由 MetaHuman 工具链内部使用，对于直接使用此模块的开发者，需注意以下依赖。

| 模块 | 用途 |
|---|---|
| `NNE` | 提供神经网络推理框架，用于运行面部追踪模型。 |
| `MetaHumanCaptureDataEditor` | 可能用于处理捕获数据。 |
| `MetaHumanSDKEditor` | MetaHuman SDK 编辑器相关功能。 |

**注意**：这是一个运行时（Runtime）模块，但主要被 MetaHuman 的编辑器工具调用，因此在编辑器环境中使用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MHA] 为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

基于最近的提交记录，该模块处于**活跃开发和维护**状态。最近一周内有多次提交，主要涉及功能优化（身体追踪集成）、问题修复（渲染瑕疵、缓存问题）以及动画导出功能的增强。作为 MetaHuman 工具链的关键组成部分，它得到了 Epic Games 的持续关注和更新。

**注意**：该模块在 5.8 版本中对一些旧的追踪器接口进行了 `UE_DEPRECATED` 标记（如 `FaceDetector`），并引入了新的基于 `IModelInstanceRunSync` 的接口（如 `FaceDetectorModel`）。使用时应参考新接口。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- 官方文档：暂无
- 测试用例：暂无公开测试用例路径（通常在插件内部或引擎测试中）