# MetaHuman Face Contour Tracker

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 面部轮廓追踪器 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（神经网络模型资产） |
| 模块 | `MetaHumanFaceContourTracker` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

`MetaHumanFaceContourTracker` 模块是 MetaHuman Animator 套件的核心组件之一，专门用于面部轮廓的检测与追踪。它管理着一系列预训练的神经网络模型，用于从视频或图像序列中检测人脸、追踪面部关键点（如眉毛、眼睛、鼻唇、嘴巴、下巴）以及估计牙齿置信度。这些追踪数据是生成和驱动 MetaHuman 数字人面部动画的基础，是连接原始视频素材与最终高保真数字人动画之间的关键桥梁。

## 使用场景

- 你正在使用 MetaHuman Animator 工具，将实拍视频转换为 MetaHuman 角色的面部动画。
- 你需要从视频中提取精确的面部表情和动作数据，以驱动数字人。
- 你在开发自定义的面部捕捉或口型同步流程，需要可靠的面部轮廓追踪能力。
- 你需要管理和加载用于面部特征提取的 AI 模型。

## 蓝图用法

该模块主要作为底层数据资产和运行时管理器，其公开的蓝图接口主要用于资产配置，而非直接在蓝图图表中调用追踪函数。

### 核心资产类

| 类 | 说明 |
|---|---|
| `UMetaHumanFaceContourTrackerAsset` | 核心资产类，管理用于面部各特征区域（人脸、眉毛、眼睛等）的神经网络模型数据。 |

### 蓝图可编辑属性（在资产编辑器中配置）

该资产中的 `TSoftObjectPtr<UNNEModelData>` 类型的属性（如 `FaceDetectorModelData`）可以在编辑器中指定或覆盖，以指向你自己的神经网络模型数据资产。运行时通过 `LoadTrackers` 系列函数加载这些模型。

## C++ 用法

核心交互是通过 `UMetaHumanFaceContourTrackerAsset` 类来完成模型的加载、配置和状态查询。

### 头文件引入

```cpp
#include "MetaHumanFaceContourTrackerAsset.h"
```

### 基本用法

加载并查询默认的追踪器资产。这通常在需要进行面部追踪处理的流程开始时进行。
```cpp
// 加载或获取默认的追踪器资产
TObjectPtr<UMetaHumanFaceContourTrackerAsset> TrackerAsset = UMetaHumanFaceContourTrackerAsset::LoadDefaultTracker();

if (TrackerAsset)
{
    // 检查资产是否已准备好（所有模型是否已加载且有效）
    if (TrackerAsset->CanProcess())
    {
        UE_LOG(LogTemp, Log, TEXT("追踪器资产已就绪，可以开始面部轮廓追踪。"));
        // ... 使用追踪器资产进行后续处理
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("追踪器资产未就绪，需要加载模型。"));
    }
}
```
*来源推断：基于 `MetaHumanFaceContourTrackerAsset.h` 中的 `LoadDefaultTracker()` 和 `CanProcess()` 函数。*

### 进阶用法

异步加载追踪器模型，并设置自定义的NNE推理后端。
```cpp
// 获取追踪器资产
TObjectPtr<UMetaHumanFaceContourTrackerAsset> TrackerAsset = UMetaHumanFaceContourTrackerAsset::LoadDefaultTracker();

if (TrackerAsset && !TrackerAsset->IsLoadingTrackers())
{
    // 可选：设置NNE后端（例如 “NNERuntimeORTDml”）
    TrackerAsset->SetNNEBackend(TEXT("NNERuntimeORTDml"));

    // 异步加载所有追踪器模型
    TrackerAsset->LoadTrackers(true /* bInShowProgressNotification */, [](bool bSuccess)
    {
        if (bSuccess)
        {
            UE_LOG(LogTemp, Log, TEXT("所有面部追踪模型异步加载完成。"));
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("面部追踪模型加载失败。"));
        }
    });
}

// 在需要时，可以取消正在进行的加载
if (TrackerAsset && TrackerAsset->IsLoadingTrackers())
{
    TrackerAsset->CancelLoadTrackers();
}
```
*来源推断：基于 `MetaHumanFaceContourTrackerAsset.h` 中的 `LoadTrackers`， `IsLoadingTrackers`， `SetNNEBackend` 和 `CancelLoadTrackers` 函数。*

## Demo 示例

以下是一个最小化的自定义追踪器资产类示例，演示如何在代码中创建和使用一个面部轮廓追踪器。

**MyCustomTracker.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MetaHumanFaceContourTrackerAsset.h"
#include "MyCustomTracker.generated.h"

UCLASS()
class UMyCustomTracker : public UObject
{
    GENERATED_BODY()

public:
    void Initialize();

    bool IsReady() const;

private:
    UPROPERTY()
    TObjectPtr<UMetaHumanFaceContourTrackerAsset> FaceTracker;
};
```

**MyCustomTracker.cpp**
```cpp
#include "MyCustomTracker.h"

void UMyCustomTracker::Initialize()
{
    // 加载默认的追踪器资产
    FaceTracker = UMetaHumanFaceContourTrackerAsset::LoadDefaultTracker();
    if (FaceTracker)
    {
        // 检查是否可以同步加载（不推荐在游戏线程中使用，但作为示例）
        if (!FaceTracker->IsLoadingTrackers())
        {
            bool bLoaded = FaceTracker->LoadTrackersSynchronous();
            if (bLoaded)
            {
                UE_LOG(LogTemp, Log, TEXT("追踪器同步加载成功。"));
            }
        }
    }
}

bool UMyCustomTracker::IsReady() const
{
    return FaceTracker && FaceTracker->CanProcess();
}
```

## 模块依赖

该模块的实现依赖于 Epic 的神经网络推理框架（NNE）。

| 模块 | 用途 |
|---|---|
| `NNE` | 提供统一的神经网络模型推理接口，用于加载和运行各种追踪器AI模型。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪时过滤可视化对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为已有的网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题。 |

### 维护评价

`MetaHumanAnimator` 插件（包含本模块）正处于**非常活跃的维护状态**。根据 Git 历史，在最近一周内（截至分析时间）有密集的更新提交，内容包括功能增强（支持身体追踪与序列导出的交互、为已有网格体导出动画）和重要的 bug 修复（渲染瑕疵、Sequencer 缓存问题）。这表明该插件是 Epic 当前重点投入开发的数字人创作工具链的核心部分。尽管 `MetaHumanFaceContourTracker` 模块本身作为底层资产管理模块，其独立更新可能不频繁，但作为整体 MetaHuman 工具套件的一部分，它得到了持续的、高质量的维护。

**推荐使用**，尤其对于需要在 UE5 中集成先进面部动画和口型同步功能的项目。

## 相关链接

- [源码 (MetaHumanAnimator 根目录)](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [源码 (MetaHumanFaceContourTracker 模块)](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceContourTracker)
- 官方文档链接未在 .uplugin 中提供。