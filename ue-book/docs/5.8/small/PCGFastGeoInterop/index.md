# PCG FastGeo Interop

> Extra plugin for Procedural Content Generation Framework which enables runtime spawning of primitives using FastGeo components.

| 属性 | 值 |
|---|---|
| 中文名 | PCG快速几何体互操作 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PCGFastGeoInterop` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-29 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGInterops/PCGFastGeoInterop) | |

## 用途

这个插件是 PCG 框架的一个扩展插件，核心目的是**解决大型开放世界中程序化生成大量环境几何体时的性能和管理问题**。

PCG 框架本身可以在运行时生成 Actor 和组件，但在生成海量静态网格体（如草地、岩石、树木）时，每个生成物都对应一个 Actor 或组件会产生巨大的内存和性能开销。FastGeo（快速几何体）系统提供了一种“无组件”的散射机制，它将几何体实例数据打包到容器中，共享渲染状态，从而实现高效的 GPU 实例化渲染。

**PCGFastGeoInterop 插件**就是将这两者连接起来的桥梁。它允许 PCG 图表在运行时使用 FastGeo 组件来生成和渲染几何体，而不是创建传统的 Actor 或组件。这意味着开发者可以利用 PCG 强大的程序化生成逻辑，同时获得 FastGeo 系统带来的顶级渲染性能和内存效率，特别适用于需要生成百万级环境装饰物的场景。

## 使用场景

- 你正在制作一个大型开放世界游戏，需要程序化生成并高效渲染海量的草地、灌木、石头等环境装饰物。
- 你希望在运行时动态更新世界内容（例如随季节变化），但又不想因生成/销毁大量 Actor 而卡顿。
- 你的项目已经在使用 PCG 框架进行程序化布局，并希望无缝接入 FastGeo 的高性能渲染管线。

## 蓝图用法

根据源码分析，此插件主要提供底层 C++ 接口，未发现直接暴露的 `BlueprintCallable` 函数。其主要功能是通过为 PCG 的运行时图元生成系统注册一个自定义的工厂（`FPCGPrimitiveFactoryFastGeoPISMC`）来实现的。因此，使用者需要通过 C++ 代码与之交互，或依赖 PCG 框架内部根据配置自动调用。

## C++ 用法

### 头文件引入

```cpp
#include "PCGFastGeoInteropModule.h" // 模块
#include "PCGPrimitiveFactoryFastGeoPISMC.h" // 核心工厂类
```

### 基本用法

这个插件的核心是一个实现了 `IPCGPrimitiveFactoryISMBase` 接口的工厂类 `FPCGPrimitiveFactoryFastGeoPISMC`。PCG 系统在需要生成图元时会调用它。

1.  **创建工厂实例**：在 PCG 图元生成逻辑中，你需要创建此工厂的实例。

```cpp
// 位于 PCG 图元生成的计算流程中
TSharedPtr<FPCGPrimitiveFactoryFastGeoPISMC> FastGeoFactory = MakeShared<FPCGPrimitiveFactoryFastGeoPISMC>();
```

2.  **初始化与创建**：工厂需要被初始化并创建实际的几何体数据。

```cpp
// 准备工厂的初始化参数 (FParameters)
FPCGPrimitiveFactoryFastGeoPISMC::FParameters FactoryParams;
// ... 填充参数，如网格体、材质、变换等 ...

FastGeoFactory->Initialize(MoveTemp(FactoryParams));

// 在PCG上下文中执行创建操作
FPCGContext* Context = ...; // 获取当前的PCG上下文
if (FastGeoFactory->Create(Context))
{
    // 创建成功，工厂现在包含了FastGeo组件的引用和实例数据
}
```

3.  **与PCG系统集成**：创建的工厂实例需要被传递给 PCG 的图元管理系统，以便进行后续的渲染状态管理和生命周期管理。

### 进阶用法

工厂类 `FPCGPrimitiveFactoryFastGeoPISMC` 内部管理着与 FastGeo 系统的交互，特别是处理 FastGeo 组件的注册回调。一个关键机制是它使用一个共享的 `TSharedRef<bool> bFastGeoRegistered` 标志，确保即使在工厂对象销毁后，来自 FastGeo 容器的注册完成回调也能安全地执行。

插件还提供了 `UPCGManagedFastGeoContainer` 资源管理类，用于管理 FastGeo 容器及其引用的 UObject 生命周期，确保在 PCG 元素销毁时能正确释放相关资源。

## Demo 示例

以下是一个简化的 C++ 示例，展示如何在自定义的 PCG 节点或计算流程中使用 `FPCGPrimitiveFactoryFastGeoPISMC`。

```cpp
// MyCustomPCGNode.h
#pragma once

#include "CoreMinimal.h"
#include "PCGSettings.h"
#include "MyCustomPCGNode.generated.h"

UCLASS(BlueprintType)
class UMyCustomPCGSettings : public UPCGSettings
{
    GENERATED_BODY()
    // ... 定义PCG节点的属性 ...
};

// MyCustomPCGNode.cpp
#include "MyCustomPCGNode.h"
#include "PCGPrimitiveFactoryFastGeoPISMC.h"
#include "PCGContext.h"
#include "PCGComponent.h"

FPCGContext* UMyCustomPCGSettings::CreateContext()
{
    return new FPCGContext();
}

bool UMyCustomPCGSettings::ExecuteInternal(FPCGContext* InContext) const
{
    // 1. 创建FastGeo工厂
    auto FastGeoFactory = MakeShared<FPCGPrimitiveFactoryFastGeoPISMC>();

    // 2. 准备参数 (示例参数，实际需根据网格体资产等构建)
    FPCGPrimitiveFactoryFastGeoPISMC::FParameters Params;
    // Params.Mesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Meshes/SM_Rock"));
    // Params.Material = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Materials/M_Rock"));
    // Params.InstanceTransforms = ... // 从PCG点集获取变换数据

    // 3. 初始化并创建
    FastGeoFactory->Initialize(MoveTemp(Params));
    if (FastGeoFactory->Create(InContext))
    {
        // 4. (关键) 将创建的工厂注册到PCG组件的资源管理器中
        //    这通常由PCG图元生成框架的内部流程完成，此处仅为示意。
        if (UPCGComponent* PCGComp = InContext->SourceComponent.Get())
        {
            // PCGComp->GetResourceManager()->RegisterPrimitiveFactory(FastGeoFactory);
        }

        return true; // 执行成功
    }

    return false; // 执行失败
}
```

## 模块依赖

根据插件名称和 .uplugin 中的 `Plugins` 依赖项，使用此插件时，你的模块需要依赖以下特定模块。

| 模块 | 用途 |
|---|---|
| `PCG` | Procedural Content Generation 核心框架 |
| `FastGeoStreaming` | 提供 FastGeo 组件和流式加载基础功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `f98f08ff` | [PCG] Fix missing GPU-instanced primitive instances in some high load scenarios like startup. | 修复了在高负载（如启动时）场景下GPU实例化图元实例丢失的问题。 |
| 2026-05-20 | `de6f7bc8` | [PCG] Fixed refresh paths being too wide for non-GPU runtime generation scenarios. | 修复了非GPU运行时生成场景下刷新路径过宽的问题。 |
| 2026-05-14 | `4c78079c` | [PCG] Optimizations and fixes for primitive spawning. | 对图元生成进行了优化和缺陷修复。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG宏迁移到新的UE_LOGF宏。 |
| 2026-03-31 | `db46fcdc` | [FastGeo] Add runtime API for PCG componentless scattering. | 为PCG无组件散射添加了运行时API。 |

### 维护评价

- **状态**：**活跃维护中**。该插件创建于2025年8月，距今不到1年。从Git历史看，在2026年3月至5月期间有密集的更新，包括功能添加、优化和关键缺陷修复，表明开发团队正在积极开发和完善它。
- **特点**：作为一个**实验性插件**（`IsExperimentalVersion: true`），并且**默认未启用**（`EnabledByDefault: false`），意味着它的API和功能可能会发生变化，主要面向开发者进行测试和集成。
- **推荐**：对于追求极致运行时生成性能，并且愿意跟进实验性API的项目，特别是大型开放世界游戏，这是一个非常值得关注和尝试的插件。建议在项目早期进行技术验证。由于其活跃的维护状态，遇到问题时获得修复支持的预期较高。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGInterops/PCGFastGeoInterop)
- [官方文档 (PCG框架)](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)