# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 元人类动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、动画数据、配置） |
| 模块 | `MetaHumanCore` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanToolkit` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MeshTrackerInterface` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕 (约 N 年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一个大型工具包，其核心功能是利用深度学习技术，将视频或图片数据转换为高质量的 MetaHuman 角色面部动画。它不仅仅是一个简单的动画录制工具，而是提供了一套完整的工作流程：从捕获源（视频、摄像头流）导入数据，通过面部追踪、求解和拟合，最终驱动 MetaHuman 骨骼网格体生成动画序列。该插件旨在解决从传统动作捕捉或手工制作，转向自动化、高保真、大规模生产 MetaHuman 面部动画的难题。

## 使用场景

*   你使用 MetaHuman Creator 创建了逼真的数字人角色，并希望为其制作自然、细腻的面部动画 → 使用 **MetaHuman Animator** 的视频捕获和处理工作流。
*   你是一个独立开发者或小型团队，没有专业的动捕设备，但希望用手机或网络摄像头为角色录制动画 → 使用 **MetaHuman Animator** 配合 MetaHuman Live 应用。
*   你已经有现成的 MetaHuman 角色和一段包含表情的视频，希望快速生成对应的动画序列，用于游戏过场、虚拟人直播或影视制作 → 使用 **MetaHuman Animator** 的离线处理功能。
*   你需要批量处理大量视频素材，为多个 MetaHuman 角色生成动画 → 使用 **MetaHumanBatchProcessor** 模块。

## 蓝图用法

由于插件包含大量模块，功能分散，以下列出部分核心可调用的类和函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsSupported` | 静态函数，检查当前平台/设备是否满足运行 MetaHuman 处理流程的最低规格要求（通常需要支持特定计算的 GPU）。 | `FMetaHumanMinSpec` |
| `GetLUIDs` | 静态函数，获取当前 UE 使用的物理设备 LUID 以及所有可用物理设备的 LUID 列表，用于诊断或高级配置。 | `FMetaHumanPhysicalDeviceProvider` |
| `GetVRAMInMB` | 静态函数，获取当前 GPU 的显存大小（MB），是 `IsSupported` 检查的一部分。 | `FMetaHumanPhysicalDeviceProvider` |

### 使用示例（蓝图描述）

1.  **检查硬件支持**：在游戏开始或处理流程启动时，调用 `FMetaHumanMinSpec::IsSupported` 节点。根据返回的布尔值（True/False），决定是启动动画处理流程，还是向用户显示“硬件不支持”的提示。
2.  **获取设备信息用于调试**：在开发或测试阶段，可以调用 `FMetaHumanPhysicalDeviceProvider::GetLUIDs` 和 `GetVRAMInMB`，将获取到的信息（如 LUID 字符串、显存大小）打印到屏幕或日志中，用于排查性能或兼容性问题。

## C++ 用法

以下示例基于 `MetaHumanPlatform` 模块提供的 API。

### 头文件引入

```cpp
#include "MetaHumanMinSpec.h"
#include "MetaHumanPhysicalDeviceProvider.h"
```

### 基本用法

在尝试执行任何可能需要高性能 GPU 的 MetaHuman 处理任务前，进行检查。

```cpp
// 检查当前环境是否满足 MetaHuman 处理的最低要求
if (FMetaHumanMinSpec::IsSupported())
{
    // 平台支持，可以启动动画捕捉或处理流程
    UE_LOG(LogTemp, Log, TEXT("Platform supports MetaHuman processing."));
    // ... 启动相关任务
}
else
{
    // 平台不支持，给出提示
    FText MinSpecInfo = FMetaHumanMinSpec::GetMinSpec();
    UE_LOG(LogWarning, TEXT("Platform does not meet MetaHuman min spec. Details: %s"), *MinSpecInfo.ToString());
    // ... 显示警告给用户
}
```

### 进阶用法

结合设备信息查询，进行更详细的诊断。

```cpp
// 在用户报告问题时，收集详细的平台信息
FString UELUID;
TArray<FString> AllLUIDs;
bool bGotLUIDs = FMetaHumanPhysicalDeviceProvider::GetLUIDs(UELUID, AllLUIDs);

int32 VRAM = FMetaHumanPhysicalDeviceProvider::GetVRAMInMB();

if (bGotLUIDs)
{
    UE_LOG(LogTemp, Warning, TEXT("UE Physical Device LUID: %s, VRAM: %d MB"), *UELUID, VRAM);
    for (const FString& LUID : AllLUIDs)
    {
        UE_LOG(LogTemp, Warning, TEXT(" - Available Physical Device LUID: %s"), *LUID);
    }
}
else
{
    UE_LOG(LogTemp, Warning, TEXT("Failed to get physical device LUIDs."));
}
```

## Demo 示例

一个最小示例，展示如何在游戏逻辑中检查 MetaHuman Animator 的硬件要求。

### MetaHumanPlatformCheck.h
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MetaHumanPlatformCheck.generated.h"

UCLASS()
class UMetaHumanPlatformCheckSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()
public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual bool ShouldCreateSubsystem(UObject* Outer) const override;

    UFUNCTION(BlueprintCallable, Category = "MetaHuman|Platform")
    bool CheckPlatformSupport() const;

    UFUNCTION(BlueprintCallable, Category = "MetaHuman|Platform")
    FString GetPlatformDiagnostics() const;
};
```

### MetaHumanPlatformCheck.cpp
```cpp
#include "MetaHumanPlatformCheck.h"
#include "MetaHumanMinSpec.h"
#include "MetaHumanPhysicalDeviceProvider.h"

void UMetaHumanPlatformCheckSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    // 子系统初始化时检查一次，并记录到日志
    if (CheckPlatformSupport())
    {
        UE_LOG(LogTemp, Log, TEXT("MetaHuman Platform Check: PASSED"));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("MetaHuman Platform Check: FAILED - %s"), *FMetaHumanMinSpec::GetMinSpec().ToString());
    }
}

bool UMetaHumanPlatformCheckSubsystem::ShouldCreateSubsystem(UObject* Outer) const
{
    // 总是创建此子系统
    return true;
}

bool UMetaHumanPlatformCheckSubsystem::CheckPlatformSupport() const
{
    return FMetaHumanMinSpec::IsSupported();
}

FString UMetaHumanPlatformCheckSubsystem::GetPlatformDiagnostics() const
{
    FString Diagnostics;
    Diagnostics.Appendf(TEXT("Supports MetaHuman Processing: %s\n"), CheckPlatformSupport() ? TEXT("YES") : TEXT("NO"));

    FString LUID;
    TArray<FString> AllLUIDs;
    if (FMetaHumanPhysicalDeviceProvider::GetLUIDs(LUID, AllLUIDs))
    {
        Diagnostics.Appendf(TEXT("UE Primary Device LUID: %s\n"), *LUID);
        for (const auto& DeviceLUID : AllLUIDs)
        {
            Diagnostics.Appendf(TEXT(" - Available Device LUID: %s\n"), *DeviceLUID);
        }
    }
    Diagnostics.Appendf(TEXT("VRAM: %d MB\n"), FMetaHumanPhysicalDeviceProvider::GetVRAMInMB());

    return Diagnostics;
}
```

## 模块依赖

本插件模块众多，以下仅列出 `MetaHumanPlatform` 模块独特的依赖项。使用其他子模块（如 `MetaHumanPerformance`, `MetaHumanIdentity`）时，请查阅其各自 `Build.cs` 文件。

| 模块 | 用途 |
|---|---|
| `RHI` | 用于查询物理图形设备信息（如 LUID）。 |
| `RenderCore` | 渲染核心功能支持。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 修复在身体追踪模式下意外导出关卡序列的问题。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色身上的渲染瑕疵（伪影）。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪时过滤掉不必要的可视化对象，优化性能和显示。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 新功能：支持为已存在的网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复了 Sequencer 相关的缓存问题，提升稳定性。 |

### 维护评价

*   **创建时间**：未知，但从版本号和功能成熟度看，是 Epic 重点维护的项目。
*   **近期更新**：更新频率非常高（过去几天内连续多次提交），内容以**功能改进、错误修复和新特性**为主，属于**活跃维护**状态。
*   **已知问题/限制**：插件默认**未启用**，且对硬件（特别是 GPU 计算能力）有明确的最低要求。使用前必须通过 `FMetaHumanMinSpec::IsSupported()` 或官方文档确认设备兼容性。
*   **推荐使用**：**强烈推荐**给所有需要创建高质量 MetaHuman 面部动画的用户。这是 Epic 官方提供的最直接、高效的工具。请务必先确认硬件支持。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/metahuman-animator-in-unreal-engine/) (需确认URL准确性)
- [测试用例] (路径需在 UE 源码中具体查找，如 `Engine/Plugins/MetaHuman/MetaHumanAnimator/Tests/`)