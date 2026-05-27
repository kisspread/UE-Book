# Fast Geo Streaming

> A system that extracts and converts a partitioned world's geometry to optimize world streaming performance.

| 属性 | 值 |
|---|---|
| 中文名 | 快速几何体流送 |
| 分类 | World Building |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产定义，工厂） |
| 模块 | `FastGeoStreaming` (Runtime), `FastGeoStreamingEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-20 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FastGeoStreaming) | |

## 用途

FastGeoStreaming 是一个用于优化大型开放世界（特别是采用 World Partition 管理的场景）中静态几何体流送性能的实验性系统。它解决了传统流送方式在处理海量静态网格体（Static Meshes）和实例化静态网格体（Instanced Static Meshes）时可能出现的性能瓶颈问题。

其核心机制是：在编辑器阶段，系统提取世界分区单元格中的不可变静态几何体，并将其转换为一种轻量级的非UObject数据结构。在运行时，这些数据被异步地流式加载和卸载，大部分处理过程不在游戏线程上进行，从而减轻主线程负担并提升流送效率。该系统与 World Partition 的数据层（Data Layers）和 HLOD 等功能兼容，是关卡流送流程的增强补充。

## 使用场景

- 你正在开发一个使用 **World Partition** 管理的大型开放世界游戏，场景中包含大量静态几何体。
- 你观察到关卡流送过程中，因加载/卸载静态网格体导致主线程卡顿或性能下降。
- 你需要一个能够利用多线程异步处理，且与 HLOD、数据层等高级功能兼容的几何体流送方案。
- 你希望探索 Epic 官方提供的、用于优化几何体流送的实验性底层解决方案。

## 蓝图用法

根据提供的代码片段，该插件的编辑器部分主要提供资产类型定义和自定义面板，未发现直接暴露给蓝图的 `BlueprintCallable` 函数。主要交互可能通过资产配置和编辑器工具完成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FastGeoTransformerSettings` 资产 | 配置几何体转换器的行为参数。 | `UFastGeoTransformerSettings` (UObject) |

### 使用示例（蓝图描述）

由于该插件主要处理底层数据转换与异步流送，通常不直接在游戏逻辑蓝图中使用。其工作流程主要通过编辑器内的资产和配置触发：
1.  **创建或编辑** `FastGeoTransformerSettings` 资产，以定义转换规则（例如，哪些几何体需要被提取和转换）。
2.  作为世界分区工作流的一部分，该插件会自动或由特定工具触发，**将匹配的几何体从世界中提取并转换**为优化格式。
3.  在游戏运行时，系统根据世界分区的流送策略，**异步加载/卸载**这些预转换的几何体数据。

## C++ 用法

**注意**：由于该插件为实验性且默认未启用，使用前需在项目设置中启用插件，并需满足前提条件（如启用 `p.Chaos.EnableAsyncInitBody`）。

### 头文件引入

```cpp
// 核心运行时模块
#include "FastGeoStreaming.h"

// 如果需要在编辑器扩展中使用（如自定义资产类型）
#include "FastGeoStreamingEditorModule.h"
```

### 基本用法

该插件的运行时核心（`FastGeoStreaming`模块）主要由内部系统驱动，对外部代码的直接API暴露可能有限。其主要工作是集成到引擎的关卡流送管线中。
根据创建描述，关键配置项是启用物理异步初始化的控制台变量。

```cpp
// 确保启用物理体的异步初始化，这是插件正常工作的前提条件之一
// 可以通过代码或配置文件设置
IConsoleVariable* CVar = IConsoleManager::Get().FindConsoleVariable(TEXT("p.Chaos.EnableAsyncInitBody"));
if (CVar)
{
    CVar->Set(1, EConsoleVariableFlags::ECVF_SetByCode);
}

// 注意：实际的几何体提取和转换逻辑由引擎内部的世界分区单元转换器（WorldPartitionCellTransformer）驱动，
// 开发者通常不直接调用底层API，而是通过配置和世界分区设置来影响其行为。
```
*来源参考：第一个提交信息中的前提条件说明。*

### 进阶用法

在编辑器工具或自定义管线中，你可能需要与 `FastGeoStreamingEditor` 模块提供的资产定义交互。

```cpp
// 在编辑器扩展中，查询 FastGeoTransformerSettings 资产类型
// 参考自: FastGeoAssetDefinitions.h
UClass* SettingsClass = UFastGeoTransformerSettings::StaticClass();
TArray<UObject*> FoundSettings;
EditorAssetLibrary::ListAssetsByClass(SettingsClass, FoundSettings);

// 可以通过工厂创建新的设置资产
// 参考自: FastGeoFactory.h
UFastGeoFactory* Factory = NewObject<UFastGeoFactory>();
Factory->InitialSettings = /* ... 配置一个已有的或默认的设置对象 */;
UObject* NewSettings = Factory->FactoryCreateNew(UFastGeoTransformerSettings::StaticClass(), GetTransientPackage(), TEXT("NewSettings"), RF_NoFlags, nullptr, GWarn);
```

## Demo 示例

以下为一个最小示例，展示如何在C++中检查插件状态和基础配置。由于插件核心逻辑深度集成，完整演示需要完整的World Partition环境。

```cpp
// MyGameFastGeoExample.h
#pragma once
#include "CoreMinimal.h"

class FMyGameFastGeoExample
{
public:
    /** 检查FastGeoStreaming插件是否已加载并配置就绪 */
    static bool IsPluginReady();

    /** 获取插件描述信息（用于调试） */
    static FString GetPluginInfo();
};
```

```cpp
// MyGameFastGeoExample.cpp
#include "MyGameFastGeoExample.h"
#include "Modules/ModuleManager.h"
#include "Engine/Engine.h"

bool FMyGameFastGeoExample::IsPluginReady()
{
    // 检查核心运行时模块是否加载
    bool bRuntimeModuleLoaded = FModuleManager::Get().IsModuleLoaded(TEXT("FastGeoStreaming"));
    // 检查必要的CVar（实际环境中应通过CVarManager获取）
    const IConsoleVariable* CVar = IConsoleManager::Get().FindConsoleVariable(TEXT("p.Chaos.EnableAsyncInitBody"));
    bool bCVarEnabled = CVar && CVar->GetInt() == 1;
    
    UE_LOG(LogTemp, Log, TEXT("FastGeoStreaming Runtime Module Loaded: %s"), bRuntimeModuleLoaded ? TEXT("Yes") : TEXT("No"));
    UE_LOG(LogTemp, Log, TEXT("Async Physics Init Enabled: %s"), bCVarEnabled ? TEXT("Yes") : TEXT("No"));

    return bRuntimeModuleLoaded && bCVarEnabled;
}

FString FMyGameFastGeoExample::GetPluginInfo()
{
    FModuleManager& ModuleManager = FModuleManager::Get();
    bool bEditorModuleLoaded = ModuleManager.IsModuleLoaded(TEXT("FastGeoStreamingEditor"));
    
    return FString::Printf(
        TEXT("FastGeoStreaming Plugin Status:\n")
        TEXT("  Runtime Module: %s\n")
        TEXT("  Editor Module: %s\n")
        TEXT("  Purpose: Experimental world geometry streaming optimization."),
        ModuleManager.IsModuleLoaded(TEXT("FastGeoStreaming")) ? TEXT("Loaded") : TEXT("Not Loaded"),
        bEditorModuleLoaded ? TEXT("Loaded") : TEXT("Not Loaded")
    );
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UnrealEd` | `FastGeoStreaming`模块的依赖项，可能用于访问编辑器特定的世界操作或资产系统接口。 |

**说明**：`FastGeoStreamingEditor`模块的依赖未在提供的信息中明确列出，通常作为Editor模块，它会依赖 `UnrealEd`, `Slate`, `SlateCore`, `PropertyEditor` 等标准编辑器模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `d478e533` | [CodeClarity] CVar description and naming cleanup for FastGeo / SSAM / Async Physics | 清理FastGeo相关控制台变量的描述和命名规范。 |
| 2026-05-12 | `8b5eabf3` | FastGeo: Support GPU animated instanced skinned meshes. | 新增对GPU驱动的动画实例化蒙皮网格体的支持。 |
| 2026-05-12 | `10c54c93` | [FastGeo] Harden surrogate component physics queries | 加强了替代组件（surrogate component）物理查询的健壮性。 |
| 2026-05-12 | `6fa3ba35` | [FastGeo] Fix world transform for unregistered components in runtime cell transformer | 修复了运行时单元转换器中未注册组件的的世界变换问题。 |
| 2026-05-12 | `8ce6709d` | [FastGeo] Resolve WalkableSlopeOverride from BodySetup when building surrogate descriptor | 在构建替代描述符时，从BodySetup中解析WalkableSlopeOverride。 |

### 维护评价

- **活跃维护**：插件创建于2025年3月，属于实验性阶段。从Git历史看，在**2026年5月仍有非常密集的更新**，包括新功能支持（GPU动画实例）、Bug修复、代码清理和健壮性增强。这表明该插件正处在**积极的开发和优化阶段**。
- **状态**：**实验性（Experimental）且默认禁用**。这意味着API和功能可能不稳定，生产环境使用需谨慎。
- **推荐度**：适用于项目前期技术调研、性能优化实验或作为未来大型项目储备技术。**不推荐在需要稳定性的正式项目当前版本中直接依赖**。建议持续关注其向稳定版本演进的情况。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FastGeoStreaming)
- 官方文档（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FastGeoStreaming/Tests)