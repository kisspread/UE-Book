# Reflex

> NVIDIA Reflex Latency Tracking and Tick Rate Handling

| 属性 | 值 |
|---|---|
| 分类 | Performance |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | Reflex (ClientOnly, Win64 only, 排除 arm64/arm64ec) |
| 创建时间 | 2021-01-21 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Nvidia/Reflex) | |

## 用途

Reflex plugin 是 Epic Games 与 NVIDIA 合作开发的低延迟技术集成，将 NVIDIA Reflex SDK 的两大核心能力引入 UE5：

1. **低延迟模式 (Low Latency Mode)**：通过控制 CPU 提交速率，使 CPU 不过度领先 GPU，从而减少从输入到画面显示的延迟。支持 `Enabled` 和 `Enabled + Boost` 两种模式，后者会在 GPU 空闲时维持高频以进一步降低延迟（代价是更高的功耗）。

2. **延迟标记 (Latency Markers)**：在游戏管线的关键阶段（输入采样、模拟开始/结束、渲染提交、呈现等）设置时间戳标记，用于精确测量从按下按键到画面显示的端到端延迟。NVIDIA 的 Reflex Stats 工具利用这些标记来计算各阶段耗时。

3. **Flash Indicator**：一种视觉指示器机制，配合外部工具使用，可在画面上标记特定帧以辅助延迟测量。

该 plugin 通过 UE 的 Modular Feature 系统注册，无需游戏代码直接引用 NVAPI，而是通过 `IMaxTickRateHandlerModule` 和 `ILatencyMarkerModule` 接口与引擎集成。

## 使用场景

- 你正在开发竞技类游戏（FPS、MOBA、格斗），需要尽可能降低输入延迟 → 启用 Reflex
- 你需要用 NVIDIA LDAT 或 PCAT 工具测量实际系统延迟 → 开启 Flash Indicator 并设置延迟标记
- 你希望在游戏设置菜单中提供 Reflex 开关，让玩家自行选择低延迟模式 → 蓝图调用 `SetReflexMode`
- 你想在开发过程中监控各渲染阶段的延迟分布 → 使用 `GetGameLatencyInMs` / `GetRenderLatencyInMs` 等函数

## 蓝图用法

所有蓝图节点来自 `UReflexBlueprintLibrary`，通过静态函数调用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Reflex Available` | 检查当前硬件是否支持 Reflex（需 NVIDIA GPU + 兼容驱动） | `UReflexBlueprintLibrary` |
| `Set Reflex Mode` | 设置 Reflex 模式：Disabled / Enabled / Enabled+Boost | `UReflexBlueprintLibrary` |
| `Get Reflex Mode` | 获取当前 Reflex 模式 | `UReflexBlueprintLibrary` |
| `Set Flash Indicator Enabled` | 启用/禁用 Flash 指示器 | `UReflexBlueprintLibrary` |
| `Get Flash Indicator Enabled` | 获取 Flash 指示器状态 | `UReflexBlueprintLibrary` |
| `Get Game to Render Latency in Ms` | 获取端到端总延迟（毫秒） | `UReflexBlueprintLibrary` |
| `Get Game Latency in Ms` | 获取游戏逻辑延迟（模拟开始 → 驱动提交结束） | `UReflexBlueprintLibrary` |
| `Get Render Latency in Ms` | 获取渲染延迟（OS 渲染队列 → GPU 渲染完成） | `UReflexBlueprintLibrary` |

### 使用示例（蓝图描述）

**游戏设置菜单中的 Reflex 开关：**

1. 创建一个 `Get Reflex Available` 节点，连接到 Branch
2. True 分支：显示 Reflex 设置 UI（下拉框或开关）
3. 用户选择模式后，调用 `Set Reflex Mode`，传入 `EReflexMode` 枚举值
4. False 分支：隐藏 Reflex 设置 UI

**HUD 延迟显示：**

1. 每帧调用 `Get Game to Render Latency in Ms`
2. 将返回值（float）格式化为文本，显示在 HUD 上
3. 同时可调用 `Get Game Latency` 和 `Get Render Latency` 分别显示

## C++ 用法

### 头文件引入

```cpp
#include "ReflexBlueprint.h"  // 蓝图库函数
```

### 基本用法

**检查 Reflex 可用性并设置模式**（来源：`ReflexBlueprint.cpp`）：

```cpp
#include "ReflexBlueprint.h"

// 检查硬件是否支持
if (UReflexBlueprintLibrary::GetReflexAvailable())
{
    // 启用 Reflex（Enabled 模式）
    UReflexBlueprintLibrary::SetReflexMode(EReflexMode::Enabled);
    
    // 或者启用 Boost 模式（更高功耗，更低延迟）
    // UReflexBlueprintLibrary::SetReflexMode(EReflexMode::EnabledPlusBoost);
}

// 查询当前模式
EReflexMode CurrentMode = UReflexBlueprintLibrary::GetReflexMode();
```

### 进阶用法

**读取延迟数据**（来源：`ReflexBlueprint.cpp` 中的延迟查询函数）：

```cpp
// 获取各阶段延迟
float TotalLatency = UReflexBlueprintLibrary::GetGameToRenderLatencyInMs();
float GameLatency = UReflexBlueprintLibrary::GetGameLatencyInMs();
float RenderLatency = UReflexBlueprintLibrary::GetRenderLatencyInMs();

// GameLatency 定义：游戏模拟开始 → 驱动提交结束
// RenderLatency 定义：OS 渲染队列开始 → GPU 渲染完成
// TotalLatency = GameLatency + RenderLatency（近似）

// 启用 Flash 指示器（配合 LDAT 硬件工具使用）
UReflexBlueprintLibrary::SetFlashIndicatorEnabled(true);
```

**通过 Modular Feature 直接访问底层接口**（来源：`ReflexModule.cpp`）：

```cpp
#include "Performance/MaxTickRateHandlerModule.h"
#include "Performance/LatencyMarkerModule.h"

// 获取 MaxTickRateHandler 实现
TArray<IMaxTickRateHandlerModule*> Handlers = 
    IModularFeatures::Get().GetModularFeatureImplementations<IMaxTickRateHandlerModule>(
        IMaxTickRateHandlerModule::GetModularFeatureName());

for (IMaxTickRateHandlerModule* Handler : Handlers)
{
    if (Handler->GetAvailable())
    {
        Handler->SetEnabled(true);
    }
}
```

## Demo 示例

**最小 Reflex 启用示例**（GameMode 或 GameInstance 中）：

```cpp
// MyGameInstance.h
#pragma once
#include "Engine/GameInstance.h"
#include "MyGameInstance.generated.h"

UCLASS()
class UMyGameInstance : public UGameInstance
{
    GENERATED_BODY()
    
    virtual void Init() override;
};

// MyGameInstance.cpp
#include "MyGameInstance.h"
#include "ReflexBlueprint.h"

void UMyGameInstance::Init()
{
    Super::Init();
    
    // 启动时启用 Reflex
    if (UReflexBlueprintLibrary::GetReflexAvailable())
    {
        UReflexBlueprintLibrary::SetReflexMode(EReflexMode::Enabled);
        UE_LOG(LogTemp, Log, TEXT("NVIDIA Reflex enabled"));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("NVIDIA Reflex not available on this hardware"));
    }
}
```

**Build.cs 依赖**：

```csharp
// 不需要额外依赖。Reflex 通过 Modular Feature 注册，
// 蓝图函数通过 ReflexBlueprint.h 调用，无需在你的 Build.cs 中添加模块依赖。
// 只需确保 Plugin 已启用。
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础引擎功能 |
| `Engine` | 引擎核心（Modular Features 系统） |
| `RHI` | 渲染硬件接口 |
| `CoreUObject` | UObject 系统 |
| `SlateCore` | UI 框架基础 |
| `Slate` | UI 框架 |

外部依赖：**NVAPI**（NVIDIA 提供的 GPU 控制接口，通过 `Engine/Source/ThirdParty/NVAPI` 引入）

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-06-03 | `0a44e4b` | Plugin modules can be included & excluded on a per-architecture basis | 新增 `PlatformArchitectureDenyList`，排除 ARM64 架构（Reflex 仅支持 x86_64） |
| 2025-04-23 | `93a1308` | Used LyraGame build target to find and convert all files to have dllstorage | 代码维护：统一 DLL 导出标记风格，无功能变化 |
| 2025-04-21 | `fd72441` | Use FScopeIdle with NvAPI_D3D_Sleep for NVIDIA Reflex to remove time pollution | 重要改进：使用 NvAPI 的 Sleep 函数替代系统 sleep，避免 Reflex 启用时污染游戏线程帧时间统计 |

### 维护评价

- **创建时间**：2021 年 1 月，已超过 5 年
- **最近更新**：2025 年 6 月有架构级别的配置更新，2025 年 4 月有实质性性能改进
- **维护状态**：**维护中** — 虽然更新不频繁，但仍在持续改进，且是 NVIDIA 与 Epic 合作的官方集成
- **限制**：
  - 仅支持 Win64 x86_64 平台（不支持 ARM64）
  - 需要 NVIDIA GPU + 支持 Reflex 的驱动版本
  - `EnabledByDefault = false`，需手动启用
  - 模块类型为 `ClientOnly`，仅客户端可用
- **推荐使用**：如果你的游戏面向竞技玩家或对延迟敏感的场景，强烈推荐启用。这是 NVIDIA Reflex 在 UE5 中的官方集成方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Nvidia/Reflex)
- [NVIDIA Reflex 官方文档](https://developer.nvidia.com/reflex)
