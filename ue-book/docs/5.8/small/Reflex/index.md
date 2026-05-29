# Reflex

> NVIDIA Reflex Latency Tracking and Tick Rate Handling

| 属性 | 值 |
|---|---|
| 中文名 | 英伟达低延迟 |
| 分类 | Performance |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `Reflex` (ClientOnly) |
| 实验性 | 否 |
| 创建时间 | 2021-01-21 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Nvidia/Reflex) | |

## 用途

该插件为 NVIDIA Reflex 技术提供官方集成，其核心目的是**降低系统延迟**并提供**精确的帧时间统计**。Reflex 通过协调 CPU 与 GPU 的工作节奏，减少渲染队列的堆积，从而显著降低从用户输入到画面显示的整体延迟。对于竞技类游戏（如 FPS、MOBA）、VR 应用或任何对响应速度要求极高的场景，该技术能带来更跟手的操作体验。插件同时提供了详细的延迟统计指标，帮助开发者定位性能瓶颈。

## 使用场景

- 你正在开发一款第一人称射击（FPS）游戏，并希望为支持 Reflex 的 NVIDIA GPU 用户提供更低的输入延迟 → 启用 Reflex 插件并调用其 API。
- 你需要分析从游戏逻辑模拟到最终画面呈现在屏幕上的各阶段耗时（游戏延迟、渲染延迟、GPU 延迟等），以优化性能 → 使用 `ReflexLatencyMarkers` 或蓝图函数获取详细的延迟数据。
- 你希望在支持的系统上，根据 Reflex 技术动态调整游戏逻辑（Tick）的更新频率以进一步降低延迟 → 集成 `ReflexMaxTickRateHandler`。

## 蓝图用法

蓝图中主要通过 `UReflexBlueprintLibrary` 来控制 Reflex 模式和查询延迟数据。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Reflex Mode` | 设置 Reflex 的工作模式（禁用、启用、启用并增强） | `UReflexBlueprintLibrary` |
| `Get Reflex Mode` | 获取当前的 Reflex 模式 | `UReflexBlueprintLibrary` |
| `Get Reflex Available` | 检查当前系统/硬件是否支持 Reflex | `UReflexBlueprintLibrary` |
| `Set Flash Indicator Enabled` | 启用或禁用屏幕闪烁指示器（用于延迟测量） | `UReflexBlueprintLibrary` |
| `Get Flash Indicator Enabled` | 获取屏幕闪烁指示器的启用状态 | `UReflexBlueprintLibrary` |
| `Get Game To Render Latency In Ms` | 获取从游戏开始到渲染提交完成的总延迟（毫秒） | `UReflexBlueprintLibrary` |
| `Get Game Latency In Ms` | 获取游戏逻辑部分的延迟（毫秒） | `UReflexBlueprintLibrary` |
| `Get Render Latency In Ms` | 获取渲染部分的延迟（毫秒） | `UReflexBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **在游戏开始时启用 Reflex**：
    - 在合适的初始化事件（如 `BeginPlay`）中，调用 `Set Reflex Mode` 节点，并将 `Mode` 参数设为 `Enabled` 或 `Enabled + Boost`（如果需要更高帧率支持）。
2.  **显示当前延迟数据**：
    - 在 HUD 蓝图的 `Draw` 或 `Tick` 事件中，使用 `Get Game To Render Latency In Ms`、`Get Game Latency InMs` 和 `Get Render Latency InMs` 获取延迟值。
    - 将这些值格式化为字符串，并通过 `Draw Text` 节点显示在屏幕上。
3.  **检查功能可用性**：
    - 在尝试设置模式前，先使用 `Get Reflex Available` 节点进行判断，若返回 `false`，则无需调用后续设置，避免无效操作。

## C++ 用法

### 头文件引入

```cpp
#include "ReflexBlueprint.h" // 包含蓝图库的静态函数和枚举
// 如需直接操作底层标记器，可包含：
#include "ReflexLatencyMarkers.h"
#include "ReflexMaxTickRateHandler.h"
```

### 基本用法

以下代码展示了如何检查 Reflex 是否可用并设置其模式，以及如何查询延迟数据。

```cpp
// 示例：检查并启用Reflex，然后打印延迟信息
#include "ReflexBlueprint.h"

void AMyPlayerController::SetupReflex()
{
    // 检查Reflex是否被当前硬件/驱动支持
    if (UReflexBlueprintLibrary::GetReflexAvailable())
    {
        // 设置Reflex为启用+增强模式（低延迟+高帧率）
        UReflexBlueprintLibrary::SetReflexMode(EReflexMode::EnabledPlusBoost);
        
        // 在调试信息中打印当前模式
        EReflexMode CurrentMode = UReflexBlueprintLibrary::GetReflexMode();
        UE_LOG(LogTemp, Log, TEXT("Reflex模式已设置为: %d"), static_cast<int32>(CurrentMode));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("当前系统不支持NVIDIA Reflex技术。"));
    }
}

void AMyHUD::ShowLatencyStats()
{
    // 获取各项延迟指标（单位：毫秒）
    float TotalLatency = UReflexBlueprintLibrary::GetGameToRenderLatencyInMs();
    float GameLatency = UReflexBlueprintLibrary::GetGameLatencyInMs();
    float RenderLatency = UReflexBlueprintLibrary::GetRenderLatencyInMs();

    // 在屏幕特定位置绘制延迟信息（简化示例）
    GEngine->AddOnScreenDebugMessage(-1, 0.f, FColor::Yellow, 
        FString::Printf(TEXT("总延迟: %.2f ms | 游戏延迟: %.2f ms | 渲染延迟: %.2f ms"), 
                        TotalLatency, GameLatency, RenderLatency));
}
```

### 进阶用法

直接操作延迟标记器和最大帧率处理器。这通常用于深度自定义或需要更精细控制的场景。

```cpp
// 示例：直接访问Reflex模块的底层功能
#include "Interfaces/IPluginManager.h"
#include "ReflexModule.h" // 私有头文件，谨慎使用

void InitializeReflexDirectly()
{
    // 获取Reflex模块实例（通常在Module的StartupModule中完成初始化）
    IModuleInterface* ReflexModule = FModuleManager::Get().LoadModule(TEXT("Reflex"));
    if (ReflexModule)
    {
        // 注意：FReflexModule的公共接口有限，大多数操作通过全局句柄或静态类完成。
        // 延迟标记器和TickRate处理器在模块启动时就已自动创建和初始化。
        
        // 通常，使用 UReflexBlueprintLibrary 的静态方法是最简单安全的方式。
        // 直接操作 IMaxTickRateHandlerModule 或 ILatencyMarkerModule 需要更底层的引擎知识。
        
        // 获取延迟标记模块（通过ILatencyMarkerModule接口）
        ILatencyMarkerModule* LatencyMarker = FModuleManager::Get().GetModule<ILatencyMarkerModule>(TEXT("Reflex"));
        if (LatencyMarker)
        {
            // 手动触发一个自定义的延迟标记点（例如，在特定游戏事件时）
            LatencyMarker->SetCustomLatencyMarker(100, GFrameCounter); // MarkerId=100
        }
    }
}
```

## Demo 示例

一个最小化的 C++ 示例，展示如何在 `GameInstance` 中初始化 Reflex 并在每帧输出延迟统计。

```cpp
// MyGameInstance.h
#pragma once
#include "Engine/GameInstance.h"
#include "MyGameInstance.generated.h"

UCLASS()
class UMyGameInstance : public UGameInstance
{
    GENERATED_BODY()
public:
    virtual void Init() override;
    virtual void Shutdown() override;
    
    // 用于绘制调试信息的函数
    UFUNCTION(BlueprintCallable, Category="Debug")
    void DrawReflexDebugInfo();
};

// MyGameInstance.cpp
#include "MyGameInstance.h"
#include "ReflexBlueprint.h"

void UMyGameInstance::Init()
{
    Super::Init();
    
    // 检查并尝试启用Reflex
    if (UReflexBlueprintLibrary::GetReflexAvailable())
    {
        UReflexBlueprintLibrary::SetReflexMode(EReflexMode::Enabled);
        UE_LOG(LogTemp, Log, TEXT("NVIDIA Reflex 已启用。"));
    }
}

void UMyGameInstance::Shutdown()
{
    // 在游戏关闭时，可以选择重置模式
    if (UReflexBlueprintLibrary::GetReflexAvailable())
    {
        UReflexBlueprintLibrary::SetReflexMode(EReflexMode::Disabled);
    }
    Super::Shutdown();
}

void UMyGameInstance::DrawReflexDebugInfo()
{
    if (!UReflexBlueprintLibrary::GetReflexAvailable())
        return;
        
    float Total = UReflexBlueprintLibrary::GetGameToRenderLatencyInMs();
    float Game = UReflexBlueprintLibrary::GetGameLatencyInMs();
    float Render = UReflexBlueprintLibrary::GetRenderLatencyInMs();
    
    // 输出到日志
    UE_LOG(LogTemp, Verbose, TEXT("[Reflex] Total: %.1f ms, Game: %.1f ms, Render: %.1f ms"), Total, Game, Render);
    
    // 或者绘制到屏幕（需要调用场景或HUD）
    // GEngine->AddOnScreenDebugMessage(1, 0.f, FColor::Green, ...);
}
```

## 模块依赖

从 `Build.cs` 分析，使用此插件需要以下非标准依赖：

| 模块 | 用途 |
|---|---|
| `NvReflex` | NVIDIA Reflex SDK 的底层封装，提供核心延迟降低和标记功能。 |
| `NvApi` | NVIDIA 专用 API 库，用于检测硬件信息、驱动版本和设置特定参数。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复编译警告，提升跨平台编译兼容性。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移至新的 `UE_LOGF` 宏，属于引擎日志系统重构。 |
| 2026-02-19 | `3e97632c` | Refactored FSceneViewport / FViewport to remove the ViewportRHI field | 引擎视口系统重构，移除了过时的 `ViewportRHI` 字段，插件需适配。 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复了“不可达代码”的编译错误，可能是条件逻辑优化所致。 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 引擎级代码格式化，将析构函数体改为 `= default`，提升编译器优化空间。 |

### 维护评价

该插件处于**活跃维护**状态。虽然创建于约5年前，但作为 NVIDIA 关键技术的重要集成，近期（2025-2026年）有持续的代码更新和维护。这些更新主要包括编译器兼容性修复、引擎代码迁移和重构适配，表明 Epic 与 NVIDIA 仍在协同维护此组件以确保其在新版引擎中稳定运行。插件仅支持 Windows 64位（非ARM）平台，这是由底层 SDK 决定的。对于目标平台包含 NVIDIA GPU 的 Windows 项目，这是一个稳定且推荐的性能优化方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Nvidia/Reflex)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/reflex-in-unreal-engine/)