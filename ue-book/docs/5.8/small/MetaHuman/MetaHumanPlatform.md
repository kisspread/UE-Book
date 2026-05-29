# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、蓝图资产） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023（估计） |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

> ⚠️ 本插件默认未启用（`Installed: false`），需在插件管理器中手动启用。

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 面部动画工具套件。它并非简单的"MetaHuman 资产管理器"，而是一个**完整的面部表演捕获与动画生成管线**。

该插件解决的核心问题是：**如何将真实演员的面部表演（视频/音频）转化为高保真的 MetaHuman 角色动画**。它覆盖了从数据捕获到最终动画输出的完整工作流：

- **捕获层**（Capture）：从 iPhone TrueDepth 摄像头或专业面部捕获设备获取原始表演数据
- **追踪层**（Tracking）：面部轮廓追踪、深度图生成、面部拟合求解
- **动画层**（Animation）：面部动画求解器、语音驱动面部动画（Speech2Face）、身体追踪集成
- **管线层**（Pipeline）：批量处理、序列器集成、动画序列导出
- **平台层**（Platform）：系统最低配置检测、GPU 能力验证

插件需要**手动启用**（`EnabledByDefault: false`），因为它依赖特定的硬件能力（支持 GPU 推理的显卡）和额外的 MetaHuman 服务配置。

## 使用场景

- 你使用 iPhone（LiDAR 或 TrueDepth）捕获了演员的面部表演 → 通过 **MetaHumanCaptureSource** 导入并生成面部动画
- 你有一个视频文件需要转换为 MetaHuman 面部动画 → 使用 **MetaHumanFaceContourTracker** + **MetaHumanFaceFittingSolver** 管线处理
- 你只有音频文件，想生成对口型的面部动画 → 使用 **MetaHumanSpeech2Face** 模块
- 你需要批量处理大量表演数据 → 使用 **MetaHumanBatchProcessor** 自动化处理
- 你想确认用户的 GPU 是否能运行 MetaHuman 动画生成 → 使用 **MetaHumanPlatform** 模块检测最低配置
- 你需要将动画结果与 Sequencer 集成进行后期编辑 → 使用 **MetaHumanSequencer** 模块

## 模块架构概览

本插件共包含 28 个模块，按功能可分为以下几组：

| 功能组 | 模块 | 说明 |
|---|---|---|
| **核心** | `MetaHumanCore`, `MetaHumanCoreEditor` | 基础设施和编辑器扩展 |
| **捕获** | `MetaHumanCaptureSource`, `MetaHumanCaptureProtocolStack`, `MetaHumanCaptureUtils`, `MetaHumanCaptureDataEditor` | 从设备/文件捕获表演数据 |
| **追踪与拟合** | `MetaHumanFaceContourTracker`, `MetaHumanFaceFittingSolver`, `MetaHumanDepthGenerator` | 面部轮廓追踪、拟合、深度图生成 |
| **动画** | `MetaHumanFaceAnimationSolver`, `MetaHumanSpeech2Face`, `MetaHumanPerformance` | 动画求解器、语音驱动动画 |
| **身份** | `MetaHumanIdentity`, `MetaHumanIdentityEditor` | MetaHuman 身份管理与编辑 |
| **管线** | `MetaHumanPipeline`, `MetaHumanBatchProcessor` | 数据处理管线与批量处理 |
| **平台** | `MetaHumanPlatform` | GPU/系统能力检测 |
| **集成** | `MetaHumanSequencer`, `MetaHumanToolkit`, `MetaHumanFootageIngest`, `MetaHumanImageViewerEditor` | Sequencer 集成、工具集、素材导入 |
| **其他** | `MeshTrackerInterface`, `MetaHumanConfig`, `MetaHumanConfigEditor`, `MetaHumanControlsConversionTest` | 网格追踪接口、配置管理 |

## MetaHumanPlatform 模块详解

`MetaHumanPlatform` 是一个轻量级运行时模块，负责**系统能力检测**——判断当前硬件是否满足运行 MetaHuman 动画管线的最低要求。

### 核心类

#### FMetaHumanMinSpec

最低配置检测类，用于判断当前系统是否支持 MetaHuman 动画处理。

| 方法 | 说明 |
|---|---|
| `IsSupported()` | 返回当前系统是否满足 MetaHuman 最低硬件要求 |
| `GetMinSpec()` | 返回最低配置要求的文本描述 |
| `Reset()` | 重置检测缓存状态，下次调用 `IsSupported()` 时重新检测 |

#### FMetaHumanPhysicalDeviceProvider

GPU 物理设备信息查询类，用于获取显卡标识和显存信息。

| 方法 | 说明 |
|---|---|
| `GetLUIDs(OutUEPhysicalDeviceLUID, OutAllPhysicalDeviceLUIDs)` | 获取当前 UE 使用的 GPU LUID 和系统中所有 GPU 的 LUID 列表 |
| `GetVRAMInMB()` | 获取当前 GPU 的显存大小（MB） |

### 蓝图用法

本模块的所有 API 均为 C++ 静态函数（非 UObject 方法），不直接暴露到蓝图。如需在蓝图中检查平台支持，需要通过自定义蓝图函数库包装调用。

### C++ 用法

#### 头文件引入

```cpp
#include "MetaHumanMinSpec.h"
#include "MetaHumanPhysicalDeviceProvider.h"
```

#### 基本用法：检查系统是否支持 MetaHuman

```cpp
#include "MetaHumanMinSpec.h"

void CheckMetaHumanSupport()
{
    if (FMetaHumanMinSpec::IsSupported())
    {
        UE_LOG(LogTemp, Log, TEXT("系统满足 MetaHuman 最低要求"));
    }
    else
    {
        FText MinSpecText = FMetaHumanMinSpec::GetMinSpec();
        UE_LOG(LogTemp, Warning, TEXT("系统不满足要求: %s"), *MinSpecText.ToString());
    }
}
```

#### 进阶用法：查询 GPU 信息并判断显存

```cpp
#include "MetaHumanMinSpec.h"
#include "MetaHumanPhysicalDeviceProvider.h"

void DiagnoseMetaHumanPlatform()
{
    // 1. 检查最低配置
    if (!FMetaHumanMinSpec::IsSupported())
    {
        UE_LOG(LogMetaHumanPlatform, Warning, TEXT("系统不满足 MetaHuman 最低要求"));
        FText Spec = FMetaHumanMinSpec::GetMinSpec();
        UE_LOG(LogMetaHumanPlatform, Warning, TEXT("最低要求: %s"), *Spec.ToString());
        return;
    }

    // 2. 获取 GPU 详细信息
    FString UELUID;
    TArray<FString> AllLUIDs;
    if (FMetaHumanPhysicalDeviceProvider::GetLUIDs(UELUID, AllLUIDs))
    {
        UE_LOG(LogMetaHumanPlatform, Log, TEXT("UE 使用的 GPU LUID: %s"), *UELUID);
        for (const FString& LUID : AllLUIDs)
        {
            UE_LOG(LogMetaHumanPlatform, Log, TEXT("可用 GPU: %s"), *LUID);
        }
    }

    // 3. 检查显存
    int32 VRAMInMB = FMetaHumanPhysicalDeviceProvider::GetVRAMInMB();
    UE_LOG(LogMetaHumanPlatform, Log, TEXT("GPU 显存: %d MB"), VRAMInMB);

    // 4. 如需重新检测（例如切换了 GPU），可重置缓存
    FMetaHumanMinSpec::Reset();
}
```

### Demo 示例

以下示例展示如何在编辑器工具中集成 MetaHuman 平台检测：

```cpp
// MetaHumanPlatformCheck.h
#pragma once

#include "CoreMinimal.h"

class FMetaHumanPlatformCheck
{
public:
    /** 返回平台检测结果的摘要字符串 */
    static FString GetPlatformSummary();

    /** 尝试重置并重新检测平台能力 */
    static bool RefreshAndCheck();
};
```

```cpp
// MetaHumanPlatformCheck.cpp
#include "MetaHumanPlatformCheck.h"
#include "MetaHumanMinSpec.h"
#include "MetaHumanPhysicalDeviceProvider.h"

FString FMetaHumanPlatformCheck::GetPlatformSummary()
{
    FString Result;

    if (FMetaHumanMinSpec::IsSupported())
    {
        Result += TEXT("✅ 系统满足 MetaHuman 要求\n");
    }
    else
    {
        Result += TEXT("❌ 系统不满足要求\n");
        Result += FString::Printf(TEXT("  最低要求: %s\n"), *FMetaHumanMinSpec::GetMinSpec().ToString());
    }

    int32 VRAM = FMetaHumanPhysicalDeviceProvider::GetVRAMInMB();
    Result += FString::Printf(TEXT("  GPU 显存: %d MB\n"), VRAM);

    FString UELUID;
    TArray<FString> AllLUIDs;
    if (FMetaHumanPhysicalDeviceProvider::GetLUIDs(UELUID, AllLUIDs))
    {
        Result += FString::Printf(TEXT("  活动 GPU LUID: %s\n"), *UELUID);
        Result += FString::Printf(TEXT("  可用 GPU 数量: %d\n"), AllLUIDs.Num());
    }

    return Result;
}

bool FMetaHumanPlatformCheck::RefreshAndCheck()
{
    FMetaHumanMinSpec::Reset();
    return FMetaHumanMinSpec::IsSupported();
}
```

## 模块依赖

以下是 `MetaHumanPlatform` 模块的依赖（基于同类平台检测模块推断）：

| 模块 | 用途 |
|---|---|
| `RHI` | 访问 GPU 设备信息、LUID、显存等渲染硬件接口 |

其余模块的依赖参见各自 Build.cs，主要涉及：

| 依赖模块 | 被依赖的模块 |
|---|---|
| `MetaHumanCoreTechLib` | `MetaHumanConfig` |
| `ControlRigDeveloper` | `MetaHumanIdentity` |
| `MetaHumanSDKEditor` | `MetaHumanIdentity` |
| `SkeletalMeshUtilitiesCommon` | `MetaHumanIdentity` |
| `MetaHumanImageViewerEditor` | `MetaHumanCaptureDataEditor` |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 身体追踪启用时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 渲染伪影 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复序列器缓存问题 |

### 维护评价

**活跃维护** — 最近更新集中于 2026 年 5 月 20-22 日，一周内有 5 次提交，覆盖功能增强（动画序列导出、身体追踪集成）和 bug 修复（渲染伪影、序列器缓存）。

- ✅ 最近更新非常频繁，开发处于活跃期
- ✅ 功能持续迭代，身体追踪和序列器集成是近期重点
- ⚠️ 插件规模庞大（28 个模块、544 个源文件），复杂度较高
- ⚠️ 默认未启用（`Installed: false`），需要用户主动开启
- ✅ 推荐使用：这是 Epic 官方维护的 MetaHuman 动画核心工具，功能完整且持续更新

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- 官方文档（.uplugin 中未提供 DocsURL）
- MetaHuman 官网：https://www.unrealengine.com/en-US/metahuman