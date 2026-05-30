# Online Subsystem Selector - GDK (Xbox PC)

> Automatically switches to OnlineSubsystemGDK when the game is installed via the Xbox PC App.

| 属性 | 值 |
|---|---|
| 中文名 | 在线子系统选择器（Xbox PC） |
| 分类 | Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MSGameOSSSelector` (RuntimeNoCommandlet) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-03 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Windows/MSGameOSSSelector) | |

## 用途

该插件的核心功能是解决 **Xbox PC App 平台的特殊分发需求**。当游戏通过 Xbox PC App 安装和运行时，插件会自动修改引擎的在线子系统（Online Subsystem）配置，将默认的 OSS 切换为针对 Xbox/GDK 优化的 `OnlineSubsystemGDK`。

它之所以存在，是因为 Xbox PC App 是一个特殊的分发平台，其运行时环境和权限与标准的 Steam 或直接发行版本不同。为了确保游戏的在线服务（如成就、排行榜、多人匹配等）能正确使用微软的 GDK 后端，需要在启动时动态注入配置。该插件通过检测运行环境（是否来自 MSGaming 插件/协议），实现了这一自动化切换，避免了为不同平台维护多份复杂配置或构建版本的麻烦。

## 使用场景

-   你正在开发一款需要同时支持 Steam 和 Xbox PC App 分发的跨平台游戏 → 用此插件在 Xbox PC 环境下自动启用 GDK 在线服务。
-   你的游戏需要集成 Xbox Game Pass 或依赖于 Xbox 网络的多人游戏功能 → 用此插件确保运行时配置正确。
-   你希望简化项目的配置管理，而不是为不同发行渠道创建多个 Engine.ini 配置文件 → 用此插件实现运行时的自动适配。

## 蓝图用法

该插件的功能主要在引擎启动早期（PostConfigInit阶段）自动执行，不提供直接操作的蓝图节点。它的输出状态可以通过模块接口查询。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Has Modified Configuration` | 查询配置是否被本插件修改过 | `IMSGameOSSSelectorModule` |

### 使用示例（蓝图描述）

1.  在蓝图中，使用“Get Module”节点获取 `MSGameOSSSelector` 模块接口。
2.  将返回的接口对象连接到 `Has Modified Configuration` 函数。
3.  该函数返回一个布尔值，可以用于条件判断，例如：`True` 表示当前运行在 Xbox PC App 环境且已应用 GDK 配置。

## C++ 用法

插件的 C++ 接口主要用于在运行时查询配置状态。

### 头文件引入

```cpp
#include "MSGameOSSSelectorModule.h"
```

### 基本用法

获取模块实例并检查配置状态。

```cpp
// 来自 MSGameOSSSelectorModule.h
if (IMSGameOSSSelectorModule::Get().HasModifiedConfiguration())
{
    // 当前运行在 Xbox PC App 环境下，GDK 在线配置已被自动应用
    UE_LOG(LogTemp, Log, TEXT("Running with Xbox PC App GDK Online Subsystem."));
}
else
{
    // 使用默认或项目配置的在线子系统
    UE_LOG(LogTemp, Log, TEXT("Using default Online Subsystem configuration."));
}
```

## Demo 示例

```cpp
// MyGameInstance.h
#pragma once
#include "CoreMinimal.h"
#include "Engine/GameInstance.h"
#include "MyGameInstance.generated.h"

UCLASS()
class UMyGameInstance : public UGameInstance
{
    GENERATED_BODY()

public:
    virtual void Init() override;

private:
    void LogOnlineSubsystemStatus();
};
```

```cpp
// MyGameInstance.cpp
#include "MyGameInstance.h"
#include "MSGameOSSSelectorModule.h"
#include "Modules/ModuleManager.h"

void UMyGameInstance::Init()
{
    Super::Init();
    LogOnlineSubsystemStatus();
}

void UMyGameInstance::LogOnlineSubsystemStatus()
{
    // 确保模块已加载
    if (FModuleManager::Get().IsModuleLoaded(TEXT("MSGameOSSSelector")))
    {
        const bool bIsGDKOSS = IMSGameOSSSelectorModule::Get().HasModifiedConfiguration();
        UE_LOG(LogTemp, Log, TEXT("Online Subsystem is GDK: %s"), bIsGDKOSS ? TEXT("True") : TEXT("False"));
    }
    else
    {
        UE_LOG(LogTemp, Log, TEXT("MSGameOSSSelector module is not loaded."));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OnlineSubsystemGDK` | 提供 Xbox/GDK 平台的在线服务实现，是本插件配置的目标 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复跨编译器（MSVC/Clang）的类型转换警告，提升代码可移植性。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG宏迁移到UE_LOGF，进行日志系统的现代化更新。 |
| 2026-03-03 | `551ea199` | New plugin that will automatically switch to OnlineSubsystemGDK when run from an MSGaming plugin | 插件初始创建，实现通过Xbox PC App启动时自动切换在线子系统的功能。 |

### 维护评价

该插件创建于2026年3月初，是一个非常新的插件。从提交记录看，它在创建后两个月内仍有维护性更新（修复警告、迁移API），表明它处于**早期积极维护阶段**。由于标记为实验性（`IsBetaVersion=true`）且默认禁用（`EnabledByDefault=false`），目前可能尚未完全稳定或功能未最终定型。它针对一个非常具体的平台（Xbox PC App）和功能（在线子系统切换），因此推荐在相关平台开发中使用，但需注意其“实验性”状态，建议在生产环境中谨慎使用并密切关注更新。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Windows/MSGameOSSSelector)
-   [官方文档]() (无)
-   [测试用例]() (源码中未发现测试文件)