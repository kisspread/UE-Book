# Game Features Toolset

> Toolset for listing, inspecting, and creating Game Feature Plugins via the AI Toolset Registry.

| 属性 | 值 |
|---|---|
| 中文名 | 游戏功能工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameFeaturesToolset` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-31 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/GameFeaturesToolset) | |

## 用途

这是一个面向 **AI 助手** 的编辑器工具集插件，将 Game Feature Plugin（GFP）系统的操作暴露给 AI Toolset Registry。

核心解决的问题：AI 助手无法直接理解或操作 Game Feature Plugin 系统。GameFeatures 模块内部有约 34 种复杂状态，本插件将其简化为 6 种对 LLM 友好的状态（`Uninitialized`、`Installed`、`Registered`、`Loaded`、`Active`、`Unknown`），并提供一组静态函数供 AI 调用来列举、查询、激活和停用 GFP。

所有函数都标记了 `UFUNCTION(meta = (AICallable))`，这意味着它们通过 `UToolsetDefinition` 基类注册到 AI Toolset Registry，可被引擎内置的 AI 助手直接调用。

## 使用场景

- 你在编辑器中使用 AI 助手管理 Game Feature Plugin → 用本插件让 AI 能列举、激活/停用 GFP
- 你需要通过 AI 工作流创建新的 Game Feature Plugin → 本插件提供了创建功能
- 你想让 AI 助手能查询某个 GFP 的当前状态（是否已加载、是否已激活等）

## 蓝图用法

本插件所有函数均为 `static` 并标记 `AICallable`，主要面向 AI Toolset Registry 使用，但也可在蓝图中调用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ListEnabledGameFeaturePlugins` | 列出所有已启用的 GFP（排序） | `UGameFeaturesToolset` |
| `ListDiscoveredGameFeaturePlugins` | 列出所有已发现的 GFP（含已禁用） | `UGameFeaturesToolset` |
| `IsGameFeaturePlugin` | 检查指定插件是否为 GFP | `UGameFeaturesToolset` |
| `IsGameFeatureActive` | 检查指定 GFP 是否处于激活状态 | `UGameFeaturesToolset` |
| `GetGameFeatureState` | 获取 GFP 的简化状态枚举 | `UGameFeaturesToolset` |
| `RequestActivateGameFeature` | 异步请求激活 GFP | `UGameFeaturesToolset` |
| `RequestDeactivateGameFeature` | 异步请求停用 GFP | `UGameFeaturesToolset` |

### 状态枚举

`EPluginToolsetGFPState` 将引擎内部约 34 种 GFP 状态简化为：

| 值 | 含义 |
|---|---|
| `Uninitialized` | 未初始化 |
| `Installed` | 已安装 |
| `Registered` | 已注册 |
| `Loaded` | 已加载 |
| `Active` | 已激活 |
| `Unknown` | 未知状态 |

### 使用示例（蓝图描述）

1. **列出所有 GFP**：调用 `ListDiscoveredGameFeaturePlugins` 节点，输出为 `TArray<FString>`，包含所有已发现的 GFP 名称
2. **激活一个 GFP**：先调用 `IsGameFeaturePlugin` 确认是 GFP，再调用 `RequestActivateGameFeature` 提交激活请求，最后轮询 `GetGameFeatureState` 确认激活完成（激活是异步的）
3. **检查状态**：调用 `GetGameFeatureState` 获取 `EPluginToolsetGFPState` 枚举值，判断 GFP 处于哪个生命周期阶段

## C++ 用法

### 头文件引入

```cpp
#include "GameFeaturesToolset.h"
```

### 基本用法

```cpp
// 列出所有已发现的 Game Feature Plugins
TArray<FString> AllGFPs = UGameFeaturesToolset::ListDiscoveredGameFeaturePlugins();
for (const FString& GFPName : AllGFPs)
{
    UE_LOG(LogTemp, Log, TEXT("Found GFP: %s"), *GFPName);
}

// 检查某个 GFP 是否处于激活状态
FString PluginName = TEXT("MyGameFeature");
if (UGameFeaturesToolset::IsGameFeatureActive(PluginName))
{
    UE_LOG(LogTemp, Log, TEXT("%s is active"), *PluginName);
}
```

### 进阶用法

```cpp
// 完整的 GFP 激活流程
FString PluginName = TEXT("MyGameFeature");

// 第一步：确认是 GFP
if (!UGameFeaturesToolset::IsGameFeaturePlugin(PluginName))
{
    UE_LOG(LogTemp, Warning, TEXT("%s is not a Game Feature Plugin"), *PluginName);
    return;
}

// 第二步：检查当前状态
EPluginToolsetGFPState CurrentState = UGameFeaturesToolset::GetGameFeatureState(PluginName);
if (CurrentState == EPluginToolsetGFPState::Active)
{
    UE_LOG(LogTemp, Log, TEXT("%s is already active"), *PluginName);
    return;
}

// 第三步：提交激活请求（异步）
bool bRequestSubmitted = UGameFeaturesToolset::RequestActivateGameFeature(PluginName);
if (bRequestSubmitted)
{
    // 需要轮询确认激活完成
    // 在 Tick 或定时器中反复调用 GetGameFeatureState()
    // 直到状态变为 Active
}
```

## Demo 示例

本插件是纯编辑器工具集，无独立 Demo。所有函数均为静态方法，可直接在编辑器工具或蓝图中调用。

```cpp
// MyTool.h
#pragma once
#include "GameFeaturesToolset.h"

class FMyGFPSummary
{
public:
    static void PrintAllGFPStatus()
    {
        TArray<FString> GFPs = UGameFeaturesToolset::ListDiscoveredGameFeaturePlugins();
        for (const FString& Name : GFPs)
        {
            EPluginToolsetGFPState State = UGameFeaturesToolset::GetGameFeatureState(Name);
            bool bActive = UGameFeaturesToolset::IsGameFeatureActive(Name);
            UE_LOG(LogTemp, Display, TEXT("GFP: %s | State: %d | Active: %s"),
                *Name, (int32)State, bActive ? TEXT("Yes") : TEXT("No"));
        }
    }
};
```

## 模块依赖

从 `.uplugin` 的 Plugins 字段可知，本插件依赖以下插件：

| 模块 | 用途 |
|---|---|
| `ToolsetRegistry` | AI 工具集注册框架，提供 `UToolsetDefinition` 基类和 `AICallable` 元数据支持 |
| `GameFeatures` | Game Feature Plugin 系统，提供 GFP 发现、加载、激活/停用的核心子系统 |

无特殊模块依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `bbb96cf0` | Hack to hopefully silence spurious static analysis CI failure. | 修复静态分析 CI 误报的临时方案 |
| 2026-04-27 | `b4229de0` | Update GameFeaturesToolset to actually work with the GameFeaturesSubsystem and correctly identify ga | 修复与 GameFeaturesSubsystem 的集成，正确识别 GFP |
| 2026-04-18 | `6471b168` | [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools, | AI 助手框架调整工具发现机制 |
| 2026-04-17 | `8c911af5` | [Backout] - CL52878047 | 回退上一次提交 |
| 2026-04-17 | `9404cd3e` | [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools, | AI 助手框架调整工具发现机制 |

### 维护评价

- **状态**：🆕 新建插件，约 1 个月历史
- **活跃度**：过去一个月内有 5 次提交，开发非常活跃
- **稳定性**：仍在快速迭代中，最近一次提交（`b4229de0`）修复了与 GameFeaturesSubsystem 的集成问题，说明核心功能刚趋于可用；紧接着就有 CI 修复提交
- **风险提示**：标记为实验性（`IsExperimentalVersion=true`），默认未启用（`EnabledByDefault=false`），API 可能随时变化
- **建议**：适合在编辑器中集成 AI 助手功能时试用，不建议在生产环境中依赖此插件

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/GameFeaturesToolset)
- [ToolsetRegistry 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/ToolsetRegistry)（前置依赖）
- [GameFeatures 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/GameFeatures/GameFeatures)（前置依赖）