# MetaHuman Face Contour Tracker

> MetaHuman Animator 插件的面部轮廓追踪子模块，基于 NNE（Neural Network Engine）运行多个深度学习模型，对人脸图像进行关键点检测与稠密特征追踪。

| 属性 | 值 |
|---|---|
| 中文名 | 面部轮廓追踪器 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（NNE 模型数据） |
| 模块 | `MetaHumanFaceContourTracker` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-04-01 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceContourTracker) | |

## 用途

MetaHuman Face Contour Tracker 是 MetaHuman Animator 管线中的核心面部追踪模块。它封装了一组用于人脸关键点检测与稠密追踪的 NNE 模型，包括：

- **FaceDetector**：人脸检测器，在画面中定位面部区域
- **FullFaceTracker**：全脸追踪器，追踪完整面部轮廓
- **BrowsDenseTracker**：眉毛稠密追踪
- **EyesDenseTracker**：眼部稠密追踪
- **NasioLabialsDenseTracker**：鼻唇沟稠密追踪
- **MouthDenseTracker**：嘴部稠密追踪
- **LipzipDenseTracker**：嘴唇闭合稠密追踪
- **ChinDenseTracker**：下巴稠密追踪
- **TeethDenseTracker / TeethConfidenceTracker**：牙齿追踪与置信度

该模块解决了从视频/捕获画面中自动提取面部动画控制数据的问题。它是 MetaHuman Identity 创建和 Performance 捕获流程的底层依赖——后续的 `MetaHumanFaceFittingSolver` 和 `MetaHumanFaceAnimationSolver` 依赖本模块提供的追踪结果。

> **注意**：5.8 版本中 GPU 推理接口（`IModelInstanceGPU`）已全部标记为 `UE_DEPRECATED`，迁移到同步推理接口（`IModelInstanceRunSync`）。

## 使用场景

- 你在使用 MetaHuman Animator 从 iPhone 捕获的视频创建 MetaHuman Identity → 本模块负责检测面部关键点并追踪面部轮廓
- 你正在从视频素材驱动 MetaHuman 面部动画（Performance 工作流）→ 本模块提供逐帧的面部特征追踪数据
- 你需要配置或替换面部追踪使用的 NNE 模型后端（如切换 CPU/CUDA）→ 通过本模块的 `SetNNEBackend` API

## 蓝图用法

`UMetaHumanFaceContourTrackerAsset` 声明为 `BlueprintType`，可作为蓝图变量引用。但其公开函数均为 C++ `UE_API`，未标记 `BlueprintCallable`，因此主要通过 **资产属性面板** 在编辑器中配置，而非蓝图节点调用。

### 编辑器属性

| 属性 | 说明 | 类型 |
|---|---|---|
| `FaceDetectorModelData` | 人脸检测模型的 NNE 模型资产 | `TSoftObjectPtr<UNNEModelData>` |
| `FullFaceTrackerModelData` | 全脸追踪模型资产 | `TSoftObjectPtr<UNNEModelData>` |
| `BrowsDenseTrackerModelData` | 眉毛稠密追踪模型资产 | `TSoftObjectPtr<UNNEModelData>` |
| `EyesDenseTrackerModelData` | 眼部稠密追踪模型资产 | `TSoftObjectPtr<UNNEModelData>` |
| `NasioLabialsDenseTrackerModelData` | 鼻唇沟稠密追踪模型资产 | `TSoftObjectPtr<UNNEModelData>` |
| `MouthDenseTrackerModelData` | 嘴部稠密追踪模型资产 | `TSoftObjectPtr<UNNEModelData>` |
| `LipzipDenseTrackerModelData` | 嘴唇闭合追踪模型资产 | `TSoftObjectPtr<UNNEModelData>` |
| `ChinDenseTrackerModelData` | 下巴稠密追踪模型资产 | `TSoftObjectPtr<UNNEModelData>` |
| `TeethDenseTrackerModelData` | 牙齿稠密追踪模型资产 | `TSoftObjectPtr<UNNEModelData>` |
| `TeethConfidenceTrackerModelData` | 牙齿置信度追踪模型资产 | `TSoftObjectPtr<UNNEModelData>` |

所有模型数据属性均为 `EditAnywhere`，可在编辑器详情面板中直接指定 NNE 模型资产。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanFaceContourTrackerAsset.h"
```

### 基本用法

加载默认追踪器资产并异步加载模型：

```cpp
// 加载引擎内置的默认面部追踪器资产
TObjectPtr<UMetaHumanFaceContourTrackerAsset> Tracker = 
    UMetaHumanFaceContourTrackerAsset::LoadDefaultTracker();

if (Tracker)
{
    // 异步加载所有 NNE 模型，带进度通知
    Tracker->LoadTrackers(true /*bInShowProgressNotification*/, 
        [](bool bSuccess)
        {
            if (bSuccess)
            {
                UE_LOG(LogTemp, Log, TEXT("面部追踪模型加载完成"));
            }
        });
}
```

### 进阶用法

同步加载并配置 NNE 后端，检查处理就绪状态：

```cpp
// 设置 NNE 推理后端（例如 "CUDA"、"CPU" 等）
Tracker->SetNNEBackend(TEXT("CUDA"));
FString CurrentBackend = Tracker->GetNNEBackend();
UE_LOG(LogTemp, Log, TEXT("当前 NNE 后端: %s"), *CurrentBackend);

// 同步加载模型（会阻塞当前线程）
bool bLoaded = Tracker->LoadTrackersSynchronous();

if (bLoaded && Tracker->CanProcess())
{
    // 模型已就绪，可以进行面部追踪处理
    // 后续由 MetaHumanFaceFittingSolver / FaceAnimationSolver 调用
}

// 可在加载过程中取消
Tracker->CancelLoadTrackers();

// 检查是否正在加载中
if (Tracker->IsLoadingTrackers())
{
    // 等待加载完成
}
```

## Demo 示例

一个最小化的 C++ 使用示例，演示如何加载追踪器并检查就绪状态：

```cpp
// MetaHumanFaceTrackerExample.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MetaHumanFaceTrackerExample.generated.h"

class UMetaHumanFaceContourTrackerAsset;

UCLASS()
class UMetaHumanFaceTrackerExample : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    /** 加载默认面部追踪器并开始异步初始化 */
    void StartTrackerSetup();

    /** 检查追踪器是否就绪 */
    bool IsReady() const;

private:
    UPROPERTY()
    TObjectPtr<UMetaHumanFaceContourTrackerAsset> TrackerAsset;
};
```

```cpp
// MetaHumanFaceTrackerExample.cpp
#include "MetaHumanFaceTrackerExample.h"
#include "MetaHumanFaceContourTrackerAsset.h"

void UMetaHumanFaceTrackerExample::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    StartTrackerSetup();
}

void UMetaHumanFaceTrackerExample::Deinitialize()
{
    if (TrackerAsset)
    {
        TrackerAsset->CancelLoadTrackers();
    }
    Super::Deinitialize();
}

void UMetaHumanFaceTrackerExample::StartTrackerSetup()
{
    // 加载引擎内置的默认追踪器
    TrackerAsset = UMetaHumanFaceContourTrackerAsset::LoadDefaultTracker();

    if (!TrackerAsset)
    {
        UE_LOG(LogTemp, Error, TEXT("无法加载默认面部追踪器资产"));
        return;
    }

    // 设置推理后端
    TrackerAsset->SetNNEBackend(TEXT("CPU"));

    // 异步加载所有追踪模型，完成后回调
    TrackerAsset->LoadTrackers(true, [WeakTracker = MakeWeakObjectPtr(TrackerAsset)](bool bSuccess)
    {
        if (bSuccess)
        {
            UE_LOG(LogTemp, Log, TEXT("面部追踪模型全部加载完成，已就绪"));
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("部分或全部面部追踪模型加载失败"));
        }
    });
}

bool UMetaHumanFaceTrackerExample::IsReady() const
{
    return TrackerAsset && TrackerAsset->CanProcess();
}
```

## 模块依赖

本模块的 Build.cs 依赖中，除标准 Core/Engine/Slate 外，需要以下特殊模块：

| 模块 | 用途 |
|---|---|
| `NNE` | Neural Network Engine，用于加载和运行面部追踪深度学习模型 |
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库（推测，该插件多个模块均依赖此库） |

> 注：本模块实际 Build.cs 依赖未在输入中完整提供，上述基于头文件分析推断。如需精确依赖，请查看 `Source/MetaHumanFaceContourTracker/MetaHumanFaceContourTracker.Build.cs`。

## 维护状态

### 近期更新

以下为 MetaHuman Animator 插件整体的近期提交（本模块所在插件目录）：

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为已有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

- **活跃维护**：最近一次提交距今仅数天（2026-05-22），更新频率高
- **功能持续迭代**：近期提交包含新功能（动画序列导出）和 bug 修复（渲染瑕疵、缓存问题），表明插件处于活跃开发状态
- **API 迁移中**：5.8 版本将 GPU 推理接口迁移到同步推理接口（`IModelInstanceRunSync`），旧接口已标记 `UE_DEPRECATED`
- **推荐使用**：作为 MetaHuman 官方工具链的核心组件，由 Epic Games 直接维护，推荐在 MetaHuman 工作流中使用
- **注意**：本模块仅提供底层追踪能力，不建议绕过 MetaHuman Identity/Performance 工作流直接使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceContourTracker)
- [MetaHuman Animator 插件根目录](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/metahuman-animator-in-unreal-engine/)（MetaHuman Animator 概述）