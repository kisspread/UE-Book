# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 集群同步渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SharedMemoryMediaEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 Unreal Engine 的核心集群渲染插件，用于将渲染负载分配到多个物理 PC（节点）上，实现同步的单眼或立体渲染。**SharedMemoryMediaEditor** 是该插件的编辑器扩展模块，专门负责处理 `SharedMemoryMediaSource` 这类资产。它的主要功能是在编辑器环境中为共享内存媒体源提供支持，例如将其正确注册到 nDisplay 的媒体配置系统中，并自动完成特定的初始化（如针对瓦片化渲染的初始化）。该模块是连接“共享内存媒体”底层技术与 nDisplay 复杂渲染拓扑配置之间的关键桥梁。

## 使用场景

- 你在使用 nDisplay 搭建一个由多台 PC 组成的 LED 墙虚拟制片环境，需要配置一个媒体源来将渲染内容输出到特定的显示节点。
- 你的 nDisplay 集群使用了瓦片化（Tiled）渲染模式，需要自动为每个瓦片（Tile）正确初始化共享内存媒体源的参数。
- 你需要一个在编辑器内可创建和配置的“共享内存媒体源”资产，用于在 nDisplay 的渲染通道间进行高速数据传输。

## 蓝图用法

`SharedMemoryMediaEditor` 模块主要提供底层的模块化特性和资产定义，不直接暴露高频使用的蓝图节点。其核心功能通过 `IDisplayClusterModularFeatureMediaInitializer` 接口被 nDisplay 的媒体子系统调用，以实现自动初始化。用户主要在编辑器内容浏览器中操作其提供的资产类型。

### 核心资产

| 资产类型 | 说明 |
|---|---|
| `Shared Memory Media Source` | 通过编辑器创建，用于配置基于共享内存的媒体源。在 nDisplay 的媒体配置中作为“源”使用。 |

### 使用示例（编辑器操作）

1.  在内容浏览器中右键，选择 **媒体 (Media) -> 媒体源 (Media Sources) -> Shared Memory Media Source** 来创建一个新的资产。
2.  双击打开资产进行配置。
3.  在 nDisplay 的配置资产（`.ndisplay` 文件）的媒体配置部分，将此资产设置为某个渲染通道的媒体源。

## C++ 用法

该模块通过注册模块化特性（Modular Feature）来扩展 nDisplay 的媒体初始化逻辑。开发者通常不需要直接调用其 API，而是通过实现自己的媒体初始化器来覆盖或扩展其行为。

### 头文件引入

```cpp
#include "SharedMemoryMediaEditorModule.h"
```

### 基本用法

该模块在启动时自动注册其核心的 `FSharedMemoryMediaInitializerFeature`。其生命周期由模块系统管理。

```cpp
// 文件: Private/SharedMemoryMediaEditorModule.cpp (推断)
void FSharedMemoryMediaEditorModule::StartupModule()
{
    // 创建并注册媒体初始化器的模块化特性
    MediaInitializer = MakeUnique<FSharedMemoryMediaInitializerFeature>();
    RegisterModularFeatures();
}

void FSharedMemoryMediaEditorModule::ShutdownModule()
{
    UnregisterModularFeatures();
    MediaInitializer.Reset();
}
```

### 进阶用法

理解 `FSharedMemoryMediaInitializerFeature` 的接口是理解其核心功能的关键。它决定了“共享内存媒体源”如何与 nDisplay 系统交互。

```cpp
// 文件: Private/ModularFeatures/SharedMemoryMediaInitializerFeature.h
// 这个类实现了 nDisplay 要求的媒体初始化器接口。
// 主要方法：
// - IsMediaObjectSupported: 检查给定的媒体对象（如媒体源、媒体输出）是否被此初始化器支持。
// - InitializeMediaObjectForTile: 为特定的显示瓦片（Tile）初始化媒体对象。
//   在瓦片化渲染配置中，nDisplay 会调用此方法为每个瓦片设置正确的媒体参数。
```

## Demo 示例

以下是一个极简的模块实现示例，演示了如何创建一个提供媒体初始化器的编辑器模块。此示例展示了模块的基本结构和对 `IDisplayClusterModularFeatureMediaInitializer` 的实现。

**SharedMemoryMediaEditorDemo.h**
```cpp
// 文件: SharedMemoryMediaEditorDemo.h
#pragma once

#include "Modules/ModuleManager.h"
#include "DisplayClusterMediaTypes.h" // 包含 EMediaStreamPropagationType 等类型

class IDisplayClusterModularFeatureMediaInitializer;

class FSharedMemoryMediaEditorDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    TUniquePtr<IDisplayClusterModularFeatureMediaInitializer> DemoMediaInitializer;
};

// 一个简单的初始化器实现示例
class FDemoMediaInitializer : public IDisplayClusterModularFeatureMediaInitializer
{
public:
    virtual bool IsMediaObjectSupported(const UObject* MediaObject) override;
    virtual bool AreMediaObjectsCompatible(const UObject* MediaSource, const UObject* MediaOutput) override;
    virtual bool GetSupportedMediaPropagationTypes(const UObject* MediaSource, const UObject* MediaOutput, EMediaStreamPropagationType& OutPropagationTypes) override;
    virtual void InitializeMediaObjectForTile(UObject* MediaObject, const FMediaObjectOwnerInfo& OwnerInfo, const FIntPoint& TilePos) override;
    virtual void InitializeMediaObjectForFullFrame(UObject* MediaObject, const FMediaObjectOwnerInfo& OwnerInfo) override;
};
```

**SharedMemoryMediaEditorDemo.cpp**
```cpp
// 文件: SharedMemoryMediaEditorDemo.cpp
#include "SharedMemoryMediaEditorDemo.h"
#include "DisplayClusterModularFeatureMediaInitializer.h" // 包含注册宏

// 实现 FSharedMemoryMediaEditorDemoModule
void FSharedMemoryMediaEditorDemoModule::StartupModule()
{
    DemoMediaInitializer = MakeUnique<FDemoMediaInitializer>();
    // 注册模块化特性，关键宏。名称需要与特性ID一致。
    REGISTER_DISPLAY_CLUSTER_MODULAR_FEATURE(IDisplayClusterModularFeatureMediaInitializer, FDemoMediaInitializer);
}

void FSharedMemoryMediaEditorDemoModule::ShutdownModule()
{
    UNREGISTER_DISPLAY_CLUSTER_MODULAR_FEATURE(IDisplayClusterModularFeatureMediaInitializer, FDemoMediaInitializer);
    DemoMediaInitializer.Reset();
}

// 实现 FDemoMediaInitializer 的空方法体（实际应用中需根据需求填写）
bool FDemoMediaInitializer::IsMediaObjectSupported(const UObject* MediaObject) { return false; }
bool FDemoMediaInitializer::AreMediaObjectsCompatible(const UObject* MediaSource, const UObject* MediaOutput) { return false; }
bool FDemoMediaInitializer::GetSupportedMediaPropagationTypes(const UObject* MediaSource, const UObject* MediaOutput, EMediaStreamPropagationType& OutPropagationTypes) { return false; }
void FDemoMediaInitializer::InitializeMediaObjectForTile(UObject* MediaObject, const FMediaObjectOwnerInfo& OwnerInfo, const FIntPoint& TilePos) {}
void FDemoMediaInitializer::InitializeMediaObjectForFullFrame(UObject* MediaObject, const FMediaObjectOwnerInfo& OwnerInfo) {}

// 注册模块
IMPLEMENT_MODULE(FSharedMemoryMediaEditorDemoModule, SharedMemoryMediaEditorDemo)
```

## 模块依赖

`SharedMemoryMediaEditor` 模块本身依赖关系简单，主要是 UE 核心模块。它的功能强依赖于运行时模块 `SharedMemoryMedia` 和 nDisplay 的媒体核心 `DisplayClusterMedia`。从其他模块的依赖列表可见，`DisplayClusterMedia` 依赖 `D3D12RHI`，说明其底层使用了 DirectX 12 进行 GPU 内存操作。

无特殊依赖（仅标准 Core/Engine/Slate 等）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 nDisplay 的电影管线添加了 EXR 多层输出支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 优化了电影管线中的扭曲混合模式，合并了 Alpha 通道处理。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了媒体关系图中的拓扑感知相机命名和 MPCDI/ICVFX 着色器中的不透明 Alpha 问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复了输出帧编码回退时未正确使用非默认显示伽马值的问题。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当 GUI 纹理尺寸小于视口尺寸时出现的闪烁问题。 |

### 维护评价

nDisplay 是 Epic Games 用于虚拟制片、CAVE 系统和大型沉浸式体验的核心技术之一，属于活跃维护的核心企业功能。
- **创建时间**：约 8 年前（2018年），属于老古董插件，但技术复杂度高，仍在持续迭代。
- **近期更新**：更新非常频繁（最近提交集中在2026年5月），且都是实质性的功能添加（如多层EXR支持）和重要 bug 修复（如着色器、闪烁问题）。
- **维护状态**：**活跃维护中**。尽管 `SharedMemoryMediaEditor` 模块本身的提交可能被包含在更大的 nDisplay 提交中，但其所属的 nDisplay 生态系统正在被积极开发和改进。
- **已知限制**：默认未启用（`EnabledByDefault: false`），需要用户手动在项目设置中启用。这表明它面向专业用户和特定硬件/软件环境。
- **推荐使用**：**推荐**。对于需要进行多机同步渲染、虚拟制片或构建复杂显示墙的用户，这是官方唯一且持续维护的解决方案。开发者应确保目标平台（Win64/Linux）受支持，并准备好应对其复杂的配置。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/n-display-in-unreal-engine/)（nDisplay 总体文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)（nDisplay 核心测试）