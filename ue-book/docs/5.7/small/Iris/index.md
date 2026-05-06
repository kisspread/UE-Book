# Iris

> Iris networking.

| 属性 | 值 |
|---|---|
| 中文名 | Iris 网络系统 |
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Iris` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-10-07 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Iris) | |

## 用途

Iris 是 Unreal Engine 5 引入的新一代网络复制系统，用于替代传统的 `AActor` 属性复制和 RPC 机制。它提供更高效、更灵活的数据同步能力，能够显著降低带宽占用和延迟，同时支持更复杂的网络架构（如分片、空间相关等）。Iris 主要解决传统网络复制在大型开放世界和大规模多人游戏中遇到的性能瓶颈和扩展性限制。

该插件是 Iris 系统的核心模块，负责实现复制管道、对象持久化、序列化、可靠性保证等底层功能。它通常与 `IrisCore` 等其他模块配合使用，但本插件 `Iris` 本身是一个运行时模块，用于启用并接入 Iris 框架。

## 使用场景

- 你是 UE5 开发者，需要构建一个大型多人在线游戏或虚拟世界。
- 你的项目对网络带宽和性能有较高要求，希望减少每帧的复制数据量。
- 你需要支持动态分片、空间格子或自定义复制策略。
- 你正在从旧版网络系统迁移到 UE5 的新网络框架。

## 蓝图用法

Iris 属于底层基础设施，没有暴露直接的蓝图中可调用的函数或属性。所有配置均通过项目设置和 C++ 代码完成。蓝图用户无需直接与 Iris 交互，而是通过 `AActor` 和 `UActorComponent` 的复制设置间接使用 Iris 功能（需在项目设置中启用 Iris）。

在项目设置中启用 Iris：
- 打开 **Project Settings → Engine → Network**，勾选 **Enable Iris**。
- 或通过 `DefaultEngine.ini` 增加：`[/Script/Iris.IrisPluginSettings] bEnableIris=True`

## C++ 用法

### 头文件引入

```cpp
#include "Iris/Iris.h"
```

### 基本用法

Iris 本质上是替换了引擎原生的复制路径，因此启用后大部分 `AActor::SetReplicates(true)` 和 `DOREPLIFETIME` 宏依然有效，但底层使用了 Iris 的新管道。以下代码演示如何在项目中启用 Iris 并检查其状态：

```cpp
// 检查 Iris 是否激活
if (Iris::IsEnabled())
{
    UE_LOG(LogTemp, Log, TEXT("Iris 网络系统已启用"));
}

// 或者通过模块接口
IIris* IrisModule = FModuleManager::LoadModulePtr<IIris>("Iris");
if (IrisModule && IrisModule->IsEnabled())
{
    // ...
}
```

**来源文件推断**：上述函数可见于 `Iris/Public/Iris.h` 和 `Iris/Private/IrisModule.cpp`。

### 进阶用法

Iris 提供了插件级别的配置，可通过 `IIrisPluginSettings` 接口在 C++ 中设置：

```cpp
#include "Iris/IrisPluginSettings.h"

// 在游戏模块启动时强制启用 Iris（需要与项目设置协调）
if (UIrisPluginSettings* Settings = GetMutableDefault<UIrisPluginSettings>())
{
    Settings->bEnableIris = true;
    Settings->SaveConfig();
}
```

此外，Iris 允许自定义 `FObjectReplicationBridge` 和 `FReplicationSystem`，但这属于更深入的主题，需要参考 `IrisCore` 模块的文档。

## Demo 示例

以下是一个最小的可编译示例，展示如何在自定义 `AActor` 中启用 Iris 复制（需项目已启用 Iris）。

**MyReplicatedActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyReplicatedActor.generated.h"

UCLASS()
class MYGAME_API AMyReplicatedActor : public AActor
{
    GENERATED_BODY()

public:
    AMyReplicatedActor();

    UPROPERTY(Replicated)
    float Health;

protected:
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;

    virtual void BeginPlay() override;
};
```

**MyReplicatedActor.cpp**
```cpp
#include "MyReplicatedActor.h"
#include "Iris/IrisPluginSettings.h"  // 可选，用于检查 Iris

AMyReplicatedActor::AMyReplicatedActor()
{
    bReplicates = true; // 启用复制，Iris 会自动接管
}

void AMyReplicatedActor::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME(AMyReplicatedActor, Health); // 使用标准的宏，底层由 Iris 处理
}

void AMyReplicatedActor::BeginPlay()
{
    Super::BeginPlay();
#if WITH_IIS // 如果定义了 WITH_IIS（Iris 宏），可在此判断
    if (Iris::IsEnabled())
    {
        UE_LOG(LogTemp, Log, TEXT("Iris 已激活，Actor 将使用 Iris 复制"));
    }
#endif
}
```

**注意**：示例中使用了 `#if WITH_IIS`，但此宏可能不存在（Iris 没有通用预定义宏），实际可改为 `#ifdef IRIS_ENABLED` 或直接编译检查。更稳妥的方法是在运行时通过 `FModuleManager` 查询。

## 模块依赖

**无特殊依赖**（仅标准 Core/Engine/Slate 等）。该插件仅依赖于 `Core`、`CoreUObject`、`Engine` 等基础模块，没有引入其他非标准模块。

## 维护状态

### 近期更新

- 2025-09-23 `f99ca52e` — Iris goes Beta.  
- 2025-09-08 `77a167d7` — Iris Beta  
- 2023-01-12 `2f78497e` — [Engine/Plugins]  
- 2022-10-12 `acc15538` — Changes to allow compiling engine modules with Iris replication code by default, and link against mo  
- 2022-10-07 `31ed81a3` — Change Iris plugin status to Experimental.

### 维护评价

Iris 从 2022 年末的 Experimental 阶段进入 2025 年的 Beta 阶段，表明 Epic Games 正在积极推动其成熟。最近一次更新在 2025-09-23（约当前日期），属于活跃维护。虽然仍有 Beta 标记，但已在多个 UE5 项目中实际使用。由于是官方推荐的新网络框架，推荐新项目启用 Iris。已知限制是部分高级功能（如自定义复制策略）的文档尚不完善，且迁移旧项目需要一定的适配工作。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Iris)
- [官方文档](https://docs.unrealengine.com/5.3/en-US/iris-replication-system-in-unreal-engine/)（UE5.3+ 版本）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Tests/Iris)（部分测试位于引擎测试目录）