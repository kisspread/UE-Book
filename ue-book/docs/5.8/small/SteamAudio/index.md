# Steam Audio (Deprecated)

> This plugin is deprecated and will be removed in a future engine release. Please use the plugin from Valve's website.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 已弃用蒸汽音频 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `SteamAudio` (Runtime) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2017-05-02 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Steam/SteamAudio) | |

## 用途

此插件旨在将 Valve 的 Steam Audio 空间音频技术集成到 Unreal Engine 中，提供基于物理的声学模拟、HRTF（头相关传输函数）渲染和声学反射等功能。**然而，该插件已被官方弃用**，其核心功能应由 Valve 官方网站提供的更新版本插件替代。此插件的存在主要是为了向后兼容，不推荐用于新项目。

## 使用场景

**重要：此插件已被弃用，不应在新项目中使用。** 如果你需要集成 Steam Audio 的物理声学功能，请访问 [Valve 的官方网站](https://valvesoftware.github.io/steam-audio) 获取官方支持的插件版本。

## 蓝图用法

分析提供的源码文件，此插件未暴露任何 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。

### 核心节点

无公开的蓝图节点。

## C++ 用法

插件的功能高度封装，对外提供的 API 非常有限，主要用于模块管理。

### 头文件引入

```cpp
#include "ISteamAudioModule.h"
```

### 基本用法

该插件主要通过模块接口访问。
*来源: `Source/SteamAudio/Public/ISteamAudioModule.h`*

```cpp
// 检查模块是否加载并可用
if (ISteamAudioModule::IsAvailable())
{
    // 获取模块实例（单例模式）
    ISteamAudioModule& SteamAudioModule = ISteamAudioModule::Get();
    // 可以在此使用模块提供的功能（如有）
    // 注意：具体功能可能已被弃用或移除
}
else
{
    UE_LOG(LogTemp, Warning, TEXT("Steam Audio module is not available."));
}
```

### 进阶用法

由于插件已弃用且功能高度封装，源码中未提供进一步的 API 使用示例。更高级的集成应参考 Valve 官方插件的文档。

## Demo 示例

这是一个最小化的、仅检查模块状态的 C++ 示例。
*注意：此示例仅演示如何与弃用的模块接口交互，不包含任何音频功能。*

```cpp
// SteamAudioDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ISteamAudioModule.h"
#include "SteamAudioDemo.generated.h"

UCLASS()
class ASteamAudioDemo : public AActor
{
    GENERATED_BODY()

public:
    ASteamAudioDemo();

    virtual void BeginPlay() override;

    UPROPERTY(BlueprintReadOnly, Category = "SteamAudioDemo")
    bool bSteamAudioAvailable = false;
};
```

```cpp
// SteamAudioDemo.cpp
#include "SteamAudioDemo.h"

ASteamAudioDemo::ASteamAudioDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ASteamAudioDemo::BeginPlay()
{
    Super::BeginPlay();

    // 检查已弃用的 Steam Audio 模块是否可用
    bSteamAudioAvailable = ISteamAudioModule::IsAvailable();

    if (bSteamAudioAvailable)
    {
        UE_LOG(LogTemp, Log, TEXT("Deprecated Steam Audio module is loaded. Please migrate to the official Valve plugin."));
        // 获取模块实例，但通常无具体功能可调用
        ISteamAudioModule& Module = ISteamAudioModule::Get();
    }
    else
    {
        UE_LOG(LogTemp, Log, TEXT("Deprecated Steam Audio module is not loaded."));
    }
}
```

## 模块依赖

从 `SteamAudio.Build.cs` 分析，该插件依赖了一些非标准的模块。

| 模块 | 用途 |
|---|---|
| `EditorFramework` | 编辑器框架支持 |
| `UnrealEd` | 编辑器功能（一个运行时插件依赖编辑器模块，属异常配置） |
| `Landscape` | 地形系统支持（可能用于声学几何体生成） |

**注意**: 运行时模块 (`SteamAudio`) 依赖 `UnrealEd` 和 `EditorFramework` 是不寻常的，这可能是插件历史遗留或配置错误，也可能是其被弃用的原因之一。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移至新版 `UE_LOGF`。 |
| 2025-06-03 | `f4b398bd` | Disable deprecated Steam Audio plugin on Windows Arm64 | 在 Windows Arm64 平台上禁用此已弃用的插件。 |
| 2025-04-21 | `751c281d` | oneTBB, Embree, OpenVDB: activate new library versions | 更新第三方库（oneTBB, Embree, OpenVDB）版本。 |
| 2025-03-27 | `093ea461` | Embree: remove unused 2.7.0 version | 移除未使用的 Embree 2.7.0 版本库。 |
| 2023-05-11 | `2e909729` | Steam Audio Deprecation (resubmit) | 正式标记插件为弃用状态。 |

### 维护评价

**状态: 已弃用，维护不活跃。**

*   **年龄与状态**: 插件创建于约 8 年前，于 2023 年 5 月正式被标记为弃用。
*   **近期活动**: 最近的提交主要是针对引擎全局更新的适配（如日志宏迁移、平台禁用、第三方库版本同步），而非插件自身的功能修复或增强。2023 年的“弃用”提交是其最后一个实质性状态变更。
*   **结论**: 该插件已被官方弃用，并被 Valve 官方插件取代。**强烈不推荐在新项目或更新中使用**。它仅为了向后兼容而保留在引擎中，预计将在未来引擎版本中移除。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Steam/SteamAudio)
- [Valve 官方插件与文档](https://valvesoftware.github.io/steam-audio)