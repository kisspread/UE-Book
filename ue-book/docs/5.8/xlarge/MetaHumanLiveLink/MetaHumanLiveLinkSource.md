# MetaHuman Live Link

> Live Link sources and associated utilities for streaming real time MetaHuman animation data.

| 属性 | 值 |
|---|---|
| 中文名 | 元人类实时链接 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产，材质模板） |
| 模块 | `LiveLinkFaceDiscovery` (Runtime), `LiveLinkFaceSource` (Runtime), `LiveLinkFaceSourceEditor` (Runtime), `MetaHumanLiveLinkSource` (Runtime), `MetaHumanLiveLinkSourceEditor` (Runtime), `MetaHumanLocalLiveLinkSource` (Runtime), `MetaHumanLocalLiveLinkSourceEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-05 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanLiveLink) | |

## 用途

此插件为 Unreal Engine 5 的 Live Link 框架提供了针对 MetaHuman 的专用数据源和处理工具。它的核心作用是将来自外部设备（如 iPhone 的 ARKit）或应用程序（如 Epic 的 Live Link Face 应用）的实时面部动画捕捉数据，通过 Live Link 协议流式传输到引擎中，用于驱动 MetaHuman 角色。它不仅支持实时表演捕捉，还内置了校准、平滑、头部姿态控制等关键的动画优化功能，并能处理预录制数据的回放，是实时 MetaHuman 动画工作流的核心桥梁。

## 使用场景

- **实时虚拟表演**：你正在使用 iPhone 或专业面部捕捉设备进行实时表演，需要将你的面部表情和动作实时映射到游戏或虚拟制片场景中的 MetaHuman 角色上。
- **MetaHuman 直播**：你在进行虚拟主播直播，需要极低延迟的面部动画来驱动你的 MetaHuman 虚拟形象。
- **动画预览与调试**：在动画制作阶段，你需要快速查看 MetaHuman 在不同表情下的表现，通过 Live Link 实时输入数据进行预览。
- **使用 Take Recorder 录制动画**：你正在使用 Take Recorder 录制来自 Live Link 源的 MetaHuman 动画数据，用于后期编辑。

## 蓝图用法

此插件的大部分功能通过 `Live Link Subject Settings` 暴露给蓝图，允许你在运行时动态控制动画流。

### 核心节点

**校准 (Calibration)**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetCalibrationProperties` | 设置需要校准的属性名称列表 | `UMetaHumanLiveLinkSubjectSettings` |
| `GetCalibrationProperties` | 获取当前设置的校准属性列表 | `UMetaHumanLiveLinkSubjectSettings` |
| `SetCalibrationAlpha` | 设置校准权重 (Alpha)，范围 0-1 | `UMetaHumanLiveLinkSubjectSettings` |
| `GetCalibrationAlpha` | 获取当前校准权重 | `UMetaHumanLiveLinkSubjectSettings` |
| `SetCalibrationNeutralFrame` | 设置用于校准的中性表情帧数据 | `UMetaHumanLiveLinkSubjectSettings` |
| `GetCalibrationNeutralFrame` | 获取当前设置的中性帧数据 | `UMetaHumanLiveLinkSubjectSettings` |
| `CaptureNeutrals` | 开始捕获一组中性表情（面部、身体等）用于校准 | `UMetaHumanLiveLinkSubjectSettings` |
| `CaptureNeutralFrame` | 捕获单帧中性表情数据 | `UMetaHumanLiveLinkSubjectSettings` |

**平滑 (Smoothing)**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSmoothing` | 设置实时平滑参数对象 | `UMetaHumanLiveLinkSubjectSettings` |
| `GetSmoothing` | 获取当前平滑参数对象 | `UMetaHumanLiveLinkSubjectSettings` |

**头部姿态 (Head Pose)**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetNeutralHeadTranslation` | 设置中性头部平移偏移 | `UMetaHumanLiveLinkSubjectSettings` |
| `GetNeutralHeadTranslation` | 获取中性头部平移偏移 | `UMetaHumanLiveLinkSubjectSettings` |
| `SetNeutralHeadOrientation` | 设置中性头部旋转偏移 | `UMetaHumanLiveLinkSubjectSettings` |
| `GetNeutralHeadOrientation` | 获取中性头部旋转偏移 | `UMetaHumanLiveLinkSubjectSettings` |
| `CaptureNeutralHeadPose` | 捕获当前头部位置作为中性姿态 | `UMetaHumanLiveLinkSubjectSettings` |

**主题检测 (Subject Detection)**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SubjectAdded` (委托) | 当一个新的 Live Link 主题被发现时广播 | `UMetaHumanLiveLinkSourceBlueprint` |

### 使用示例（蓝图描述）

1.  **添加 Live Link 源**：在 Live Link 面板中，添加 “MetaHuman Live Link” 或 “Live Link Face” 源。连接成功后，会自动出现一个或多个主题（Subject）。
2.  **获取设置对象**：在你的角色蓝图或动画蓝图中，通过 `Get Live Link Subject Settings` 节点获取对应主题的 `UMetaHumanLiveLinkSubjectSettings` 对象。
3.  **运行时控制校准**：使用 `SetCalibrationProperties` 和 `SetCalibrationAlpha` 节点，在游戏运行时调整校准效果。你可以绑定到 UI 滑块上。
4.  **应用平滑**：创建一个 `MetaHuman Realtime Smoothing Params` 资产，配置平滑参数，然后通过 `SetSmoothing` 节点应用到设置对象上。
5.  **监听新主题**：创建一个 `UMetaHumanLiveLinkSourceBlueprint` 实例（例如在 GameMode 中），将其 `SubjectAdded` 委托绑定到你的自定义函数，当有新的 Live Link 设备连接时做出响应。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanLiveLinkSubjectSettings.h"
#include "MetaHumanSmoothingPreProcessor.h"
```

### 基本用法

设置一个 MetaHuman Live Link 主题的校准属性。
*(概念示例，基于 `UMetaHumanLiveLinkSubjectSettings` API)*

```cpp
// 假设你已经获取到有效的 UMetaHumanLiveLinkSubjectSettings* LiveLinkSettings
if (LiveLinkSettings)
{
    // 定义要校准的属性（通常是面部控制器名称）
    TArray<FName> PropertiesToCalibrate;
    PropertiesToCalibrate.Add(“CTRL_expressions_browDownLeft”);
    PropertiesToCalibrate.Add(“CTRL_expressions_eyeSquintRight”);

    // 应用校准设置
    LiveLinkSettings->SetCalibrationProperties(PropertiesToCalibrate);
    LiveLinkSettings->SetCalibrationAlpha(0.8f); // 设置80%的校准权重
}
```

### 进阶用法

创建一个自定义的 Live Link 帧预处理器，在帧数据到达动画蓝图前进行自定义平滑处理。
*(概念示例，基于 `UMetaHumanSmoothingPreProcessor` 架构)*

```cpp
// 1. 创建并配置平滑参数对象
UMetaHumanRealtimeSmoothingParams* SmoothingParams = NewObject<UMetaHumanRealtimeSmoothingParams>();
SmoothingParams->SetFaceSmoothingAmount(0.5f);
SmoothingParams->SetBodySmoothingAmount(0.3f);

// 2. 创建预处理器实例
UMetaHumanSmoothingPreProcessor* SmoothingPreProcessor = NewObject<UMetaHumanSmoothingPreProcessor>();
SmoothingPreProcessor->Parameters = SmoothingParams;

// 3. 将其应用到特定的 Live Link 主题设置中
// (通常通过 Live Link 面板或代码配置 Subject Pipeline)
```

## Demo 示例

一个最小的 C++ 示例，展示如何初始化并控制 MetaHuman Live Link 设置。
```cpp
// MyCharacter.h
#pragma once
#include "GameFramework/Character.h"
#include "MetaHumanLiveLinkSubjectSettings.h"
#include "MyCharacter.generated.h"

UCLASS()
class AMyCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyCharacter();

    // 用于存储运行时获取的 Live Link 设置指针
    UPROPERTY(Transient)
    TObjectPtr<UMetaHumanLiveLinkSubjectSettings> LiveLinkSettings;

    // 蓝图可调用的函数，用于开始校准
    UFUNCTION(BlueprintCallable, Category = “MetaHuman”)
    void StartFaceCalibration();
};

// MyCharacter.cpp
#include “MyCharacter.h”
#include “LiveLinkBlueprintLibrary.h”

AMyCharacter::AMyCharacter()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyCharacter::StartFaceCalibration()
{
    // 此函数通常在运行时，确认已连接到 MetaHuman Live Link 源后调用
    // 假设已知主题键 (Subject Key)
    FLiveLinkSubjectKey SubjectKey;
    // ... 获取正确的 SubjectKey ...

    // 通过蓝图库函数获取设置对象
    UObject* SettingsObject = ULiveLinkBlueprintLibrary::GetLiveLinkSubjectSettings(SubjectKey);
    LiveLinkSettings = Cast<UMetaHumanLiveLinkSubjectSettings>(SettingsObject);

    if (LiveLinkSettings)
    {
        // 开始捕获中性表情帧，用于后续校准
        LiveLinkSettings->CaptureNeutralFrame();
        UE_LOG(LogTemp, Log, TEXT(“Starting MetaHuman Face Calibration…”));
    }
}
```

## 模块依赖

要使用此插件的核心功能，你的项目模块通常需要依赖以下插件模块（在你的 `.Build.cs` 文件中添加）：

| 模块 | 用途 |
|---|---|
| `MetaHumanLiveLinkSource` | 提供核心的 Live Link 数据源、主题设置和处理逻辑 |
| `LiveLink` | Unreal Engine 的 Live Link 框架基础模块 |
| `MetaHumanCreator` (如适用) | 与 MetaHuman Creator 工具链集成 |
| `MetaHumanRealtimeSmoothing` | 提供实时动画数据平滑算法和参数对象 |

**注意**：`MetaHumanLocalLiveLinkSource` 模块依赖 `UnrealEd`、`PropertyEditor` 等编辑器模块，如果你的功能仅在运行时使用，应避免依赖此类模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `9bee2cb0` | [MHA] Expose detection thresholds for body | 暴露身体动作检测的阈值参数 |
| 2026-05-14 | `988b3911` | [MHA] Face animation sequence export changes for combined solve | 为组合解算修改面部动画序列导出逻辑 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点的警告代码 |
| 2026-05-12 | `8bf9ba92` | [MetaHumanLiveLink] Use AvfMedia for FileMediaSource bundles on Apple platforms | 在苹果平台上为文件媒体源包使用AvfMedia后端 |
| 2026-05-12 | `fa06fada` | New ADA model | 引入新的ADA（可能是自适应或高级）模型 |

### 维护评价

**积极维护中**。该插件作为 Epic MetaHuman 生态的关键组成部分，自2025年2月创建以来，一直保持**非常活跃**的更新。近期的提交（截至2026年5月）显示其功能仍在快速迭代，包括扩展身体动画能力、优化导出流程、修复平台兼容性问题以及引入新的算法模型。所有更新均围绕功能增强和性能优化，没有出现废弃标记。

**结论**：强烈推荐使用。这是驱动 MetaHuman 实时动画的官方且正在被积极开发的解决方案。请确保使用与你的引擎版本匹配的插件版本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanLiveLink)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanLiveLink/Tests) (如果存在)