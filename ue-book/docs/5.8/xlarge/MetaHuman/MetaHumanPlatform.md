# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 元人类动画师 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、处理管线） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-04-15 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 为 MetaHuman 角色在虚幻引擎中驱动面部动画提供的官方核心工具集。它不仅仅是一个简单的动画控制器，而是一个完整的、模块化的生态系统，用于从各种源头（如 iPhone 深度摄像头视频、专业摄像机画面、音频文件）**采集、处理、解算和应用**高保真的面部动画数据。其核心目标是解决将真实世界表演转化为逼真数字角色动画的复杂流程问题，使开发者能够在引擎内完成从面部追踪到最终动画输出的全流程。

## 使用场景

- 你使用 **iPhone Pro** 或其他深度摄像头拍摄了演员的面部表演视频，需要将其转化为 MetaHuman 角色的动画。
- 你拥有来自 **专业动作捕捉** 会话的数据，需要将其匹配并应用到你的 MetaHuman 角色上。
- 你希望通过一段 **音频文件** 驱动 MetaHuman 角色进行口型同步和表情动画。
- 你需要批量处理大量面部动画素材，或对现有 MetaHuman 角色动画进行二次编辑和优化。
- 你需要检查运行 MetaHuman 面部动画所需的 **最低硬件规格**。

## 蓝图用法

本插件功能主要由复杂的 C++ 后端管线构成，蓝图公开接口相对集中，主要用于状态查询和流程触发。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Is Supported` | 检查当前系统是否满足运行 MetaHuman 面部动画的最低硬件要求。 | `FMetaHumanMinSpec` |
| `Get Min Spec` | 获取描述最低硬件要求的文本信息。 | `FMetaHumanMinSpec` |
| `Reset` | 重置最低规格检查状态，强制下次检查时重新检测硬件。 | `FMetaHumanMinSpec` |
| `Get LUIDs` | 获取当前 UE 使用的物理设备 LUID 以及所有可用物理设备的 LUID 列表。 | `FMetaHumanPhysicalDeviceProvider` |
| `Get VRAMInMB` | 获取当前系统中所有物理设备的总显存大小（MB）。 | `FMetaHumanPhysicalDeviceProvider` |

### 使用示例（蓝图描述）

在游戏开始时，使用 `Is Supported` 节点检查硬件。如果不支持，则显示一个警告界面。若支持，则可以继续加载 MetaHuman 角色并触发动画处理管线（例如 `MetaHumanPipeline` 中的其他节点）。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanMinSpec.h"
#include "MetaHumanPhysicalDeviceProvider.h"
```

### 基本用法

检查系统是否满足 MetaHuman 动画的运行要求，并获取相关硬件信息。
（来源：基于 `Public/MetaHumanMinSpec.h` 和 `Public/MetaHumanPhysicalDeviceProvider.h` 头文件分析）

```cpp
// 检查系统兼容性
if (FMetaHumanMinSpec::IsSupported())
{
    UE_LOG(LogTemp, Log, TEXT("系统满足 MetaHuman 动画运行要求。"));
    
    // 获取当前物理设备的 LUID
    FString UELUID;
    TArray<FString> AllLUIDs;
    if (FMetaHumanPhysicalDeviceProvider::GetLUIDs(UELUID, AllLUIDs))
    {
        UE_LOG(LogTemp, Log, TEXT("UE 使用的物理设备 LUID: %s"), *UELUID);
    }
    
    // 获取总显存
    int32 TotalVRAMMB = FMetaHumanPhysicalDeviceProvider::GetVRAMInMB();
    UE_LOG(LogTemp, Log, TEXT("系统总显存: %d MB"), TotalVRAMMB);
}
else
{
    // 系统不满足要求，获取具体描述
    FText MinSpecText = FMetaHumanMinSpec::GetMinSpec();
    UE_LOG(LogTemp, Warning, TEXT("系统不支持。要求: %s"), *MinSpecText.ToString());
}
```

### 进阶用法

在应用程序设置界面中，提供一个按钮用于重新检测硬件（例如用户可能刚升级了显卡驱动）。

```cpp
// 在用户点击“重新检测硬件”按钮时调用
void UMySettingsWidget::OnRecheckHardwareClicked()
{
    FMetaHumanMinSpec::Reset();
    
    // 重新执行检查逻辑
    if (FMetaHumanMinSpec::IsSupported())
    {
        // 更新 UI 为“通过”
    }
    else
    {
        // 更新 UI 显示失败原因
        FText FailureReason = FMetaHumanMinSpec::GetMinSpec();
        // ... 显示 FailureReason
    }
}
```

## Demo 示例

一个完整的、可编译的最小示例，用于在运行时检测 MetaHuman 兼容性并输出结果。

```cpp
// MetaHumanPlatformTest.h
#pragma once

#include "CoreMinimal.h"

class FMetaHumanPlatformTest
{
public:
    static void RunCompatibilityCheck();
};
```

```cpp
// MetaHumanPlatformTest.cpp
#include "MetaHumanPlatformTest.h"
#include "MetaHumanMinSpec.h"
#include "MetaHumanPhysicalDeviceProvider.h"

void FMetaHumanPlatformTest::RunCompatibilityCheck()
{
    UE_LOG(LogTemp, Log, TEXT("开始 MetaHuman 系统兼容性检查..."));

    // 步骤1: 检查是否支持
    bool bIsSupported = FMetaHumanMinSpec::IsSupported();
    UE_LOG(LogTemp, Log, TEXT("系统支持状态: %s"), bIsSupported ? TEXT("支持") : TEXT("不支持"));

    if (bIsSupported)
    {
        // 步骤2: 获取硬件详情
        int32 TotalVRAM = FMetaHumanPhysicalDeviceProvider::GetVRAMInMB();
        UE_LOG(LogTemp, Log, TEXT("检测到总显存: %d MB"), TotalVRAM);

        FString UsedLUID;
        TArray<FString> AllLUIDs;
        if (FMetaHumanPhysicalDeviceProvider::GetLUIDs(UsedLUID, AllLUIDs))
        {
            UE_LOG(LogTemp, Log, TEXT("UE 当前使用的物理设备: %s"), *UsedLUID);
            UE_LOG(LogTemp, Log, TEXT("共发现 %d 个物理设备。"), AllLUIDs.Num());
        }
    }
    else
    {
        // 步骤3: 获取失败原因
        FText MinSpec = FMetaHumanMinSpec::GetMinSpec();
        UE_LOG(LogTemp, Warning, TEXT("不满足最低要求。详情: %s"), *MinSpec.ToString());
    }

    // (可选) 步骤4: 重置并重新检查
    FMetaHumanMinSpec::Reset();
    bool bRecheckSupported = FMetaHumanMinSpec::IsSupported();
    UE_LOG(LogTemp, Log, TEXT("重置后再次检查，支持状态: %s"), bRecheckSupported ? TEXT("支持") : TEXT("不支持"));
}
```

## 模块依赖

`MetaHumanPlatform` 模块本身的依赖非常基础。

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础功能 |
| `CoreUObject` | UObject 系统基础 |

*无特殊依赖（仅标准 Core/CoreUObject）。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 修复在启用身体追踪时级别序列导出的兼容性问题 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色上的渲染瑕疵/伪影 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪时过滤掉不必要的可视化对象，优化性能或显示 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 为现有网格体导出动画序列功能，增强工具集实用性 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 中的缓存问题，提升稳定性和性能 |

### 维护评价

**积极维护中**。MetaHuman Animator 是 Epic Games 的重点产品之一，从近 5 年前创建至今，最近更新（2026年5月）非常密集且全是功能性改进和 Bug 修复，表明插件处于**非常活跃的维护状态**。它是 MetaHuman 工作流的核心组件，官方支持力度大，推荐在需要 MetaHuman 面部动画的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/metahuman-animator-in-unreal-engine/) (未在 .uplugin 中提供，此处为推测的官方文档链接格式)
- [测试用例] (测试用例可能分布于各个子模块中，例如 `MetaHumanCore` 或 `MetaHumanPipeline` 模块内)