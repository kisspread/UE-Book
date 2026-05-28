# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、工具、配置） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 未知 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方推出的 MetaHuman 资产创建与动画工具包。它并非一个单一的功能模块，而是一个庞大的插件生态系统，旨在将高保真数字人（MetaHuman）的创建、面部动画捕捉、实时解算和编辑工作流集成到虚幻引擎编辑器中。

该插件解决的核心问题是：如何将复杂的 MetaHuman 数字人资产创建、面部动画数据采集与处理（例如从 iPhone 或其他设备捕捉的表演数据）无缝地转换为可在引擎中实时驱动的、高质量的面部动画。它提供了从原始视频素材导入、面部关键点追踪、动画解算、到在编辑器中进行精细化编辑和导出的完整流水线。

## 使用场景

- 你需要将 iPhone 或其他专业设备捕捉的面部表演视频，转换为驱动 MetaHuman 角色的高质量动画数据 → 使用 `MetaHumanFaceAnimationSolver` 和 `MetaHumanFaceContourTracker` 模块。
- 你正在开发一款需要大量逼真数字人对话的游戏或应用，并希望通过音频直接生成对应的面部动画 → 探索 `MetaHumanSpeech2Face` 模块。
- 你的项目需要批量处理大量 MetaHuman 角色的配置或资产 → 使用 `MetaHumanBatchProcessor`。
- 你需要为 MetaHuman 角色创建或修改基于控制绑定的动画蓝图 → 依赖 `MetaHumanIdentity` 模块（它集成了 ControlRig 开发工具）。
- 你需要在运行时检查玩家的硬件是否满足流畅运行 MetaHuman 角色的最低规格 → 使用 `MetaHumanPlatform` 模块提供的硬件查询功能。

## 蓝图用法

由于 `MetaHumanPlatform` 模块主要提供运行时系统规格检查功能，其公共接口均为 C++ 静态函数，没有标记为 `BlueprintCallable`。因此，此模块主要为 C++ 开发者提供底层支持，不直接暴露蓝图节点。

其他模块（如 `MetaHumanToolkit`、`MetaHumanIdentityEditor`）会提供丰富的蓝图和编辑器工具，但不在 `MetaHumanPlatform` 模块的范畴内。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 无 | 本模块无直接蓝图可调用节点 | - |

### 使用示例（蓝图描述）

本模块不提供蓝图节点。硬件检测功能通常在 C++ 代码中调用，用于决定是否启用高精度渲染或显示警告信息。

## C++ 用法

`MetaHumanPlatform` 模块提供静态工具类，用于查询运行系统的硬件信息，以判断是否满足 MetaHuman 角色渲染的最低要求。

### 头文件引入

```cpp
#include "MetaHumanMinSpec.h"
#include "MetaHumanPhysicalDeviceProvider.h"
```

### 基本用法

查询当前系统是否支持 MetaHuman 角色的最低规格渲染。

```cpp
// 来自 MetaHumanMinSpec.h
// 检查系统是否支持 MetaHuman 的最低规格
bool bIsSystemSupported = FMetaHumanMinSpec::IsSupported();

if (!bIsSystemSupported)
{
    FText MinSpecText = FMetaHumanMinSpec::GetMinSpec();
    UE_LOG(LogTemp, Warning, TEXT("当前系统不满足 MetaHuman 的最低规格要求: %s"), *MinSpecText.ToString());
    // 可以选择降级画质或提示用户
}
```

获取显卡的详细信息，例如用于特定优化或信息展示。

```cpp
// 来自 MetaHumanPhysicalDeviceProvider.h
FString EngineGpuLUID;
TArray<FString> AllGpuLUIDs;
if (FMetaHumanPhysicalDeviceProvider::GetLUIDs(EngineGpuLUID, AllGpuLUIDs))
{
    UE_LOG(LogTemp, Log, TEXT("引擎使用的物理设备 LUID: %s"), *EngineGpuLUID);
    for (const FString& Luid : AllGpuLUIDs)
    {
        UE_LOG(LogTemp, Log, TEXT("系统中发现物理设备 LUID: %s"), *Luid);
    }
}

int32 VRAMInMB = FMetaHumanPhysicalDeviceProvider::GetVRAMInMB();
UE_LOG(LogTemp, Log, TEXT("主显示适配器显存大小: %d MB"), VRAMInMB);
```

### 进阶用法

结合硬件信息，在项目启动或加载 MetaHuman 角色时动态调整渲染质量或功能开关。

```cpp
#include "MetaHumanMinSpec.h"
#include "MetaHumanPhysicalDeviceProvider.h"

void AMyGameMode::CheckMetaHumanSupport()
{
    // 第一步：进行最低规格检查
    if (!FMetaHumanMinSpec::IsSupported())
    {
        // 系统不支持，禁用高质量 MetaHuman 渲染或采取降级方案
        bEnableHighQualityMetaHuman = false;
        UE_LOG(LogTemp, Warning, TEXT("已禁用高质量 MetaHuman 渲染。"));
        return;
    }

    // 第二步：进行更精细的显存检查
    const int32 MinimumRequiredVRAM_MB = 4000; // 假设需要 4GB 显存
    int32 AvailableVRAM = FMetaHumanPhysicalDeviceProvider::GetVRAMInMB();

    if (AvailableVRAM < MinimumRequiredVRAM_MB)
    {
        bEnableHighQualityMetaHuman = false;
        UE_LOG(LogTemp, Warning, TEXT("显存不足 (%d MB < %d MB)，已降低 MetaHuman 渲染质量。"), AvailableVRAM, MinimumRequiredVRAM_MB);
    }
    else
    {
        bEnableHighQualityMetaHuman = true;
        UE_LOG(LogTemp, Log, TEXT("系统满足 MetaHuman 渲染要求。"));
    }

    // 根据结果应用配置
    ApplyMetaHumanQualitySettings();
}
```

## Demo 示例

一个最小化的示例，展示如何在项目中集成 `MetaHumanPlatform` 模块进行硬件检测。

```cpp
// MyGameModule.h
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyGameModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    /** 检查并应用 MetaHuman 硬件配置 */
    void CheckAndApplyMetaHumanHardwareConfig();

private:
    bool bMetaHumanHardwareSupported;
};
```

```cpp
// MyGameModule.cpp
#include "MyGameModule.h"
#include "MetaHumanMinSpec.h"
#include "MetaHumanPhysicalDeviceProvider.h"

#define LOCTEXT_NAMESPACE "FMyGameModule"

void FMyGameModule::StartupModule()
{
    CheckAndApplyMetaHumanHardwareConfig();
}

void FMyGameModule::ShutdownModule()
{
    // 清理
}

void FMyGameModule::CheckAndApplyMetaHumanHardwareConfig()
{
    // 1. 检查最低规格
    bMetaHumanHardwareSupported = FMetaHumanMinSpec::IsSupported();

    if (!bMetaHumanHardwareSupported)
    {
        FText MinSpecInfo = FMetaHumanMinSpec::GetMinSpec();
        UE_LOG(LogTemp, Error, TEXT("系统未达到运行 MetaHuman 的最低硬件要求: %s"), *MinSpecInfo.ToString());
        // 在此处可以设置全局标志，禁用游戏中的 MetaHuman 生成或触发警告 UI
        return;
    }

    // 2. 获取硬件详情以备后用
    int32 VRAM = FMetaHumanPhysicalDeviceProvider::GetVRAMInMB();
    UE_LOG(LogTemp, Log, TEXT("MetaHuman 硬件支持已启用。检测到显存: %d MB"), VRAM);

    // 3. 根据更详细的硬件信息调整资源加载策略（示例）
    // 例如，VRAM > 6GB 时加载 4K 材质，否则加载 2K 材质
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyGameModule, MyGame)
```

## 模块依赖

根据 `MetaHumanPlatform` 模块自身的构建文件，它没有列出对外部插件模块的独特依赖。其功能是基础的系统查询。

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine 等） | 该模块仅封装了基础的平台硬件查询功能 |

## 维护状态

`MetaHumanPlatform` 是 MetaHuman Animator 巨型插件的一部分。根据提供的最近 git 提交记录，插件整体仍处于**活跃开发**中。提交主要集中在动画导出、渲染瑕疵修复和身体追踪支持方面。

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出，避免功能冲突。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色上的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 进行身体追踪时过滤掉某些可视化对象，优化视图。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MetaHuman Animator] 支持为已有的网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复了 Sequencer（序列器）相关的缓存问题。 |

### 维护评价

- **活跃度**：插件整体处于**积极维护**状态，近期有多次针对功能改进和问题修复的提交。
- **模块性质**：`MetaHumanPlatform` 作为基础支撑模块，代码稳定，不常需要频繁修改。其更新频率不直接反映其健康状况。
- **推荐使用**：作为 Epic 官方提供的核心 MetaHuman 工具链的一部分，**强烈推荐**使用。它代表了数字人技术的最佳实践和官方支持路径。对于任何需要高保真数字人或面部动画的项目，都应将其视为首选工具。
- **注意事项**：这是一个功能庞杂的大型插件，需要较陡峭的学习曲线和一定的硬件资源（特别是用于面部捕捉数据解算时）。建议仔细阅读官方文档并从示例项目开始。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档]() （.uplugin 中 DocsURL 为空，请访问 Unreal Engine 官方文档站搜索 “MetaHuman”）
- [测试用例]() （测试用例通常位于插件内部或引擎的 `Tests` 目录下，此处未直接提供路径）