# Microsoft GDK Runtime Plug-in for Unreal Engine

> Provides GDK Runtime capabilities for Windows games

| 属性 | 值 |
|---|---|
| 中文名 | 微软 GDK 运行时 |
| 分类 | Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MSGamingRuntime` (RuntimeNoCommandlet) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2026-02-16 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Windows/MSGamingRuntime) | |

## 用途

此插件是微软 GDK (Gaming Development Kit) 在 Unreal Engine 5 中的运行时集成层。它为在 Windows 平台上使用 GDK 工具链开发和运行游戏（特别是面向 Xbox 生态系统的游戏）提供了基础支持。插件本身不包含具体的游戏逻辑或资产，而是作为一个接口和平台适配层，确保 UE5 项目能与 GDK 运行时环境正确交互和初始化。

## 使用场景

- 你正在使用微软 GDK 开发一个面向 Xbox 平台的 UE5 项目，需要在 Windows 上进行开发和调试。
- 你的游戏需要调用 GDK 提供的特定运行时功能或服务，例如成就、存档、社交功能等，这些功能需要 GDK 运行时环境支持。

## 蓝图用法

该插件主要提供 C++ 模块接口，没有直接暴露 `BlueprintCallable` 函数。因此，蓝图中没有特定的节点可用。所有交互都应通过 C++ 代码进行。

## C++ 用法

该插件提供了一个单例模块接口，用于检查 GDK 运行时的可用性。

### 头文件引入

```cpp
#include "MSGamingRuntimeModule.h"
```

### 基本用法

在你的 C++ 代码中，你可以检查 GDK 运行时是否可用。这通常用于在尝试调用 GDK 特定功能前进行安全检查。

```cpp
// 来源: Source/MSGamingRuntime/Public/MSGamingRuntimeModule.h

// 获取模块单例并检查 GDK 是否可用
if (IMSGamingRuntimeModule::Get().IsAvailable())
{
    // GDK 运行时已初始化，可以安全地调用 GDK 相关功能
    // 例如，访问 IGDKRuntimeModule (来自 MSGamingSupport 插件)
}
else
{
    // GDK 运行时不可用，执行备用逻辑或跳过 GDK 功能
}
```

### 进阶用法

由于该插件被设计为其他 GDK 相关插件（如 `MSGamingSupport`）的依赖项，更复杂的用法通常涉及与其他模块的交互。你可以通过此接口确保 GDK 基础环境就绪，然后再加载和使用更高级的 GDK 功能模块。

## Demo 示例

由于插件非常基础，且依赖于特定的 GDK 运行时环境，这里提供一个最小化的可用性检查示例。

**MSGamingRuntimeTest.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MSGamingRuntimeTest.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API UMSGamingRuntimeTest : public UActorComponent
{
	GENERATED_BODY()

public:
	virtual void BeginPlay() override;

protected:
	void CheckGDKAvailability();
};
```

**MSGamingRuntimeTest.cpp**
```cpp
#include "MSGamingRuntimeTest.h"
#include "MSGamingRuntimeModule.h"

void UMSGamingRuntimeTest::BeginPlay()
{
	Super::BeginPlay();
	CheckGDKAvailability();
}

void UMSGamingRuntimeTest::CheckGDKAvailability()
{
	if (IMSGamingRuntimeModule::IsAvailable())
	{
		UE_LOG(LogTemp, Log, TEXT("GDK Runtime is available."));
		// 在此添加你的 GDK 相关初始化代码
	}
	else
	{
		UE_LOG(LogTemp, Warning, TEXT("GDK Runtime is not available."));
	}
}
```

## 模块依赖

该插件的 `.Build.cs` 文件表明其依赖了 `UnrealEd` 模块，这对于一个 `RuntimeNoCommandlet` 类型的模块来说是不寻常的。这可能意味着该模块包含了一些仅在编辑器中需要的功能或钩子。

| 模块 | 用途 |
|---|---|
| `MSGamingSupport` | 提供基础 GDK 支持模块 |
| `UnrealEd` | （推测）可能用于编辑器特定的 GDK 集成或工具 |

**注意**：依赖 `UnrealEd` 使得该模块在打包游戏时可能不会被包含，或者需要条件编译。具体行为取决于其 `LoadingPhase` 和 `PlatformAllowList` 设置。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-24 | `101f2bf3` | Enable GDK ARM64 support in plugins (requires April 2026 GDK & modern folder layout) | 为插件添加 GDK ARM64 架构支持 |
| 2026-04-17 | `5f051051` | fixes for MSGamingRuntime's bLazyInitialize: | 修复 MSGamingRuntime 的延迟初始化问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF |
| 2026-03-09 | `5eb8fada` | [Backout] - CL51493025 | 回退了一个之前的变更 |
| 2026-03-06 | `21bccda6` | Enable arm64 support in plugins | 为插件启用 arm64 架构支持 |

### 维护评价

这是一个非常新的插件（创建于 2026 年 2 月），并且在最近几个月内持续有功能更新和修复。更新内容主要集中在**平台支持扩展（ARM64）** 和 **核心初始化流程的优化**上。鉴于其标记为实验性 (`IsBetaVersion: true`) 且默认未启用，它目前处于积极开发和内部测试阶段。虽然其本身功能简单，但作为 GDK 集成链路中的关键一环，推荐需要 GDK 支持的项目关注并测试此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Windows/MSGamingRuntime)
- [官方文档](https://learn.microsoft.com/en-us/gaming/gdk/)（微软 GDK 官方文档）