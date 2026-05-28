# Pixel Streaming

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流送 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PixelStreaming` (Runtime), `PixelStreamingBlueprint` (Runtime), `PixelStreamingBlueprintEditor` (Runtime), `PixelStreamingEditor` (Runtime), `PixelStreamingHMD` (Runtime), `PixelStreamingInput` (Runtime), `PixelStreamingServers` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-31 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming) | |

## 用途

本插件的核心功能是实现 Unreal Engine 画面与音频的实时流式传输。它通过 WebRTC 协议将引擎的渲染输出和音频流推送到兼容的客户端，例如网页浏览器，使用户无需安装完整引擎或游戏客户端即可远程交互。`PixelStreamingHMD` 模块是此插件的关键组成部分，它提供了对虚拟现实（VR）头戴式显示器（HMD）的支持，允许用户在浏览器中以立体模式接收和交互 Pixel Streaming 内容，解决了在流媒体环境下支持沉浸式 VR 体验的问题。

## 使用场景

- **云游戏/云渲染服务**：玩家通过浏览器访问 3A 级游戏或复杂渲染应用，无需高性能本地硬件。
- **远程协作与评审**：团队成员通过浏览器查看和操作同一个 Unreal Engine 项目场景。
- **Web 端 VR 体验**：用户通过支持 WebXR 的浏览器，使用 VR 头显（如 HTC Vive， Quest）体验 Unreal Engine 生成的沉浸式内容，该模块 (`PixelStreamingHMD`) 为此提供了必要的 XR 系统和立体渲染支持。
- **轻量级客户端应用**：为移动设备、瘦客户端或特定工业终端提供高质量的 3D 可视化与交互。

## 蓝图用法

`PixelStreamingHMD` 模块主要作为引擎 HMD 子系统的运行时实现存在，其核心功能通过引擎内置的 HMD 管理接口进行访问，在蓝图中通常不直接暴露额外的节点。其蓝图可见性主要通过 `PixelStreamingBlueprint` 模块体现，但该模块的功能主要围绕核心 Pixel Streaming 的控制（如启停流、设置参数），而非直接操控 HMD 的立体渲染细节。因此，对于立体渲染的高级控制，通常在 C++ 层面进行。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetPixelStreamingHMD` | 获取当前 Pixel Streaming HMD 实例的指针（通过模块接口）。 | `IPixelStreamingHMDModule` |
| `GetActiveXRSystem` | 获取当前激活的 XR 系统类型。 | `IPixelStreamingHMDModule` |
| `SetActiveXRSystem` | 设置当前激活的 XR 系统类型（例如 HTC Vive, Quest）。 | `IPixelStreamingHMDModule` |

### 使用示例（蓝图描述）

由于 HMD 控制深度集成于引擎，更常见的是通过 C++ 或控制台变量（CVars）进行配置。在蓝图中，可通过 `Get Pixel Streaming HMD Module` 节点（如果可用）来访问模块接口，并调用上述函数。典型流程是：在应用启动时，通过 C++ 代码设置所需的 XR 系统类型，并确保 HMD 模块被正确加载，随后引擎的 VR 模式切换将自动利用该模块提供的追踪和渲染功能。

## C++ 用法

### 头文件引入

```cpp
// 引入模块接口和HMD类定义
#include "IPixelStreamingHMDModule.h"
#include "PixelStreamingHMD.h"
```

### 基本用法

从模块接口获取 HMD 实例并检查 XR 系统。

```cpp
// 检查模块是否可用
if (IPixelStreamingHMDModule::IsAvailable())
{
    // 获取模块接口
    IPixelStreamingHMDModule& HMDModule = IPixelStreamingHMDModule::Get();
    
    // 获取当前活动的XR系统 (例如：未知， HTC Vive， Quest)
    EPixelStreamingXRSystem CurrentXRSystem = HMDModule.GetActiveXRSystem();
    
    // 设置活动的XR系统，以启用特定设备的适配（如瞳距、控制器）
    HMDModule.SetActiveXRSystem(EPixelStreamingXRSystem::Quest);
    
    // 获取底层的HMD对象指针，可用于更精细的控制
    FPixelStreamingHMD* PixelStreamingHMD = HMDModule.GetPixelStreamingHMD();
    if (PixelStreamingHMD)
    {
        // 例如，检查是否启用了立体渲染
        bool bIsStereo = PixelStreamingHMD->IsStereoEnabled();
        
        // 手动设置HMD的变换（通常由流输入数据驱动）
        // PixelStreamingHMD->SetTransform(NewTransform);
    }
}
```

### 进阶用法

通过控制台变量（CVars）动态配置 HMD 行为。这些变量在 `Settings.h` 中定义，可在运行时通过控制台命令或配置文件调整。

```cpp
// 直接通过控制台变量修改参数
IConsoleVariable* CVarEnableHMD = IConsoleManager::Get().FindConsoleVariable(TEXT("PixelStreaming.HMD.Enable"));
if (CVarEnableHMD)
{
    CVarEnableHMD->Set(true);
}

// 调整视场角
IConsoleVariable* CVarHFOV = IConsoleManager::Get().FindConsoleVariable(TEXT("PixelStreaming.HMD.HFOV"));
if (CVarHFOV)
{
    CVarHFOV->Set(110.0f); // 设置水平视场角为110度
}

// 调整瞳距 (IPD)
IConsoleVariable* CVarIPD = IConsoleManager::Get().FindConsoleVariable(TEXT("PixelStreaming.HMD.IPD"));
if (CVarIPD)
{
    CVarIPD->Set(0.064f); // 设置IPD为64mm（单位通常是米）
}

// 控制是否应用从流中接收的眼部位置和旋转
IConsoleVariable* CVarApplyEyePos = IConsoleManager::Get().FindConsoleVariable(TEXT("PixelStreaming.HMD.ApplyEyePosition"));
if (CVarApplyEyePos)
{
    CVarApplyEyePos->Set(true);
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何在项目启动时初始化并配置 Pixel Streaming HMD 模块。

**MyGameHMDSetup.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MyGameHMDSetup.generated.h"

UCLASS()
class UMyGameHMDSetup : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
};
```

**MyGameHMDSetup.cpp**
```cpp
#include "MyGameHMDSetup.h"
#include "IPixelStreamingHMDModule.h"

void UMyGameHMDSetup::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    // 确保在游戏实例初始化时配置HMD模块
    if (IPixelStreamingHMDModule::IsAvailable())
    {
        IPixelStreamingHMDModule& HMDModule = IPixelStreamingHMDModule::Get();
        
        // 根据项目目标或设备检测，设置合适的XR系统
        HMDModule.SetActiveXRSystem(EPixelStreamingXRSystem::Quest);
        
        UE_LOG(LogTemp, Log, TEXT("Pixel Streaming HMD module configured for Quest."));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Pixel Streaming HMD module is not available."));
    }
}
```

## 模块依赖

从 `PixelStreamingHMD` 模块的 `Build.cs` 文件分析，其核心依赖包括引擎的 HMD 和 XR 基础框架。

| 模块 | 用途 |
|---|---|
| `HeadMountedDisplay` | Unreal Engine 核心 HMD 框架，提供 `FHeadMountedDisplayBase` 等基类。 |
| `XRBase` | 提供 `EXRTrackedDeviceType`、`FSceneViewExtension` 等 XR 系统基础定义。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `c1dab3e1` | [PixelStreaming2] Fix: Input handler obtaining default target window from wrong method | 修复 PixelStreaming2 输入处理器获取默认目标窗口的方法错误 |
| 2026-05-14 | `876d5541` | Fix the crash with PIE/Simulate | 修复编辑器中 PIE（运行）和模拟模式下的崩溃问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下将双精度常量截断为浮点数产生的警告 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the ... | 虚拟制片：将多种虚拟制片资产移至不同的资产分类并进行迁移 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以同时支持 FString 和 UE::FSharedString |

### 维护评价

**活跃维护**。尽管 Pixel Streaming 插件本身已有数年历史，但根据近期的 Git 提交记录（截至2026年5月），其相关模块仍在频繁接受更新，内容涉及功能修复（如PIE崩溃、输入处理）、代码质量改进（浮点警告修复）以及架构优化（虚拟制片资产重构、字符串支持）。这表明 Epic Games 团队仍在积极维护此功能，特别是与虚拟制片和下一代 `PixelStreaming2` 相关的部分。

**重要提示**：从提交记录中频繁出现的 `[PixelStreaming2]` 标记来看，Epic 可能正在开发一个重大重构或替代版本。当前的 `PixelStreaming` 插件虽在维护，但未来可能会被 `PixelStreaming2` 取代。对于新项目，建议关注 `PixelStreaming2` 的发展状态。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming/Tests)