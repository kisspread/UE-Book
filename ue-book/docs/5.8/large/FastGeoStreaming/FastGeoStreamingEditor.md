# Fast Geo Streaming

> A system that extracts and converts a partitioned world's geometry to optimize world streaming performance.

| 属性 | 值 |
|---|---|
| 中文名 | 快速几何流式加载 |
| 分类 | World Building |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产定义） |
| 模块 | `FastGeoStreaming` (Runtime), `FastGeoStreamingEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-20 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FastGeoStreaming) | |

## 用途

FastGeoStreaming 是一个实验性插件，旨在解决超大规模世界（如开放世界）中，基于世界分区（World Partition）的几何体流式加载性能瓶颈问题。

传统方式下，每个静态网格体（StaticMesh）组件都是独立的 UObject，在流式加载时涉及大量的对象序列化、反序列化和内存分配操作，当场景中存在海量静态网格体时，会造成显著的性能开销和卡顿。

本插件通过一个“世界分区单元转换器”（WorldPartitionCellTransformer），将世界中**不可变**的静态几何体（包括 StaticMesh 和 InstanceStaticMesh，支持或不支持碰撞）提取出来，转换并存储为一种轻量级的**非 UObject 数据结构**。在运行时，系统能够在此数据结构的基础上，高效地进行异步的流式加载和卸载（大部分逻辑不在游戏线程执行），从而极大提升世界分区的流式加载性能，并与数据层（Data Layers）、HLOD 等功能兼容。

**核心价值**：将海量静态网格体组件的流式加载从“对象级”优化为“数据级”，是面向开放世界性能的关键优化技术。

## 使用场景

- 你正在使用世界分区（World Partition）构建超大开放世界地图，需要极致的流式加载性能。
- 你的场景包含大量重复的静态几何体（如地形、建筑、岩石、树木等），希望进行性能优化。
- 你需要一种与数据层（Data Layers）和 HLOD 兼容的高级几何体流式解决方案。

## 蓝图用法

本插件主要提供运行时优化，其核心逻辑（如单元转换器、数据结构）并未直接暴露为公共蓝图 API。插件的主要交互发生在编辑器和运行时引擎内部。

然而，`FastGeoStreamingEditor` 模块提供了一些编辑器扩展功能，用于创建和管理优化所需的资产：

### 编辑器资产与操作

| 节点/资产 | 说明 | 所在类/系统 |
|---|---|---|
| `FastGeoTransformerSettings` 资产 | 用于配置几何体提取和转换规则的资产。你可以在内容浏览器中创建并编辑此资产。 | `UFastGeoTransformerSettings` (通过 `UAssetDefinition_FastGeoTransformerSettings` 定义资产类型) |
| `ConvertFastGeoSettingsAssetButton` | 一个属性自定义按钮，可能用于触发转换操作。 | `FConvertFastGeoSettingsAssetButtonCustomization` |

### 使用示例（蓝图描述）

1.  **创建设置资产**：在内容浏览器中右键，选择“杂项”（Miscellaneous）或特定分类下的“FastGeo Transformer Settings”来创建一个新的设置资产。
2.  **配置规则**：双击打开该资产，配置需要提取的网格体类型、碰撞处理、LOD 策略等规则。
3.  **应用到世界分区**：配置完成后，需要通过编辑器工具或自动化流程，将该设置应用到目标世界分区的单元上，触发几何体提取和转换过程。具体操作通常由引擎内部的“世界分区单元转换器”驱动，用户可能通过蓝图或控制台命令触发。

## C++ 用法

### 头文件引入

```cpp
#include "FastGeoStreaming/FastGeoStreaming.h"
```

### 基本用法

本插件的核心类并未设计为由用户代码直接实例化和调用。其运行时工作流由引擎内部的世界分区流式加载系统驱动。开发者的主要交互点在于**创建和配置转换规则资产**。

以下是如何以编程方式创建和使用 `UFastGeoTransformerSettings` 的示例（假设在编辑器工具或自动化脚本中）：

```cpp
// 示例来源：推断自 FastGeoFactory.h 和资产定义
#include "FastGeoStreaming/UFastGeoTransformerSettings.h"
#include "Engine/World.h"

// 在某个编辑器工具函数中
void CreateAndConfigureFastGeoSettings()
{
    // 1. 创建一个新的设置资产（通常通过 UFactory 或在内容浏览器中创建）
    UFastGeoTransformerSettings* Settings = NewObject<UFastGeoTransformerSettings>();
    
    // 2. 配置设置（根据 .uplugin 描述和类名推断）
    // 例如：设置要处理的 Actor 类型、网格体过滤规则、碰撞处理等
    // Settings->SetActorFilter(...);
    // Settings->SetCollisionHandling(...);
    
    // 3. 将资产保存到磁盘（通常在编辑器上下文中完成）
    // FAssetEditorManager::Get().OpenEditorForAsset(Settings);
    
    // 4. 最终，这些设置将被用于初始化和驱动 WorldPartitionCellTransformer
    // 具体集成由引擎内部模块完成，开发者通常不直接调用转换逻辑。
}
```

### 进阶用法

从提供的 `FastGeoStreaming` 运行时模块的 `Build.cs` 文件中可以看到它依赖 `UnrealEd`，这表明其运行时组件与编辑器工具链紧密相关。真正的“提取和转换”流程很可能在编辑器中预处理阶段完成，生成优化的数据资产，运行时则负责这些资产的异步加载。

因此，更高级的用法涉及理解其数据流：
1.  **编辑时处理**：使用配置好的 `UFastGeoTransformerSettings`，通过插件提供的 `FastGeoStreamingEditor` 工具，对关卡中的几何体进行分析、提取，并生成优化后的流式加载数据块。
2.  **运行时加载**：当世界分区单元被请求加载时，运行时模块接管，异步加载对应的优化数据块，并在游戏线程外（或同步点）将其转换为可渲染、可碰撞的运行时表示（如代理组件），整个过程避免了创建海量 UObject。

## Demo 示例

一个展示如何在编辑器工具中初始化并准备应用 FastGeoStreaming 设置的最小示例：

**FastGeoDemoTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class UFastGeoTransformerSettings;

class FFastGeoDemoTool
{
public:
    FFastGeoDemoTool();
    ~FFastGeoDemoTool();

    void DemonstrateSettingsCreation();

private:
    UPROPERTY()
    TObjectPtr<UFastGeoTransformerSettings> CachedSettings;
};
```

**FastGeoDemoTool.cpp**
```cpp
#include "FastGeoDemoTool.h"
#include "FastGeoStreaming/UFastGeoTransformerSettings.h"
#include "UObject/Package.h"

FFastGeoDemoTool::FFastGeoDemoTool()
{
}

FFastGeoDemoTool::~FFastGeoDemoTool()
{
}

void FFastGeoDemoTool::DemonstrateSettingsCreation()
{
    // 创建一个临时设置对象用于演示
    CachedSettings = NewObject<UFastGeoTransformerSettings>(GetTransientPackage(), NAME_None, RF_Transient);
    
    if (CachedSettings)
    {
        UE_LOG(LogTemp, Display, TEXT("Created FastGeo Transformer Settings object."));
        
        // 在实际使用中，这里会配置 CachedSettings 的各个属性
        // CachedSettings->SomeProperty = ...;
        
        // 通常，该设置对象会被传递给世界分区流式加载子系统或特定的转换命令
        // 例如：IWorldPartitionStreamingSubsystem::Get()->ApplyTransformerSettings(CachedSettings);
        
        UE_LOG(LogTemp, Display, TEXT("Settings configured (demo). This object would be used to drive geometry extraction."));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create FastGeo Transformer Settings object."));
    }
}
```

**注意**：这是一个高度简化的示例，主要说明 `UFastGeoTransformerSettings` 的创建。实际的应用需要与编辑器模块（如 `FastGeoStreamingEditor`）和世界分区系统集成。

## 模块依赖

从提供的 `Build.cs` 文件依赖分析：

| 模块 | 用途 |
|---|---|
| `UnrealEd` | `FastGeoStreaming` 运行时模块依赖 `UnrealEd`，表明其转换和数据处理逻辑与编辑器工具链深度耦合，可能用于访问编辑器专用的数据处理接口或资产管道。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `d478e533` | [CodeClarity] CVar description and naming cleanup for FastGeo / SSAM / Async Physics | 代码清理：优化了 FastGeo 相关控制台变量的描述和命名。 |
| 2026-05-12 | `8b5eabf3` | FastGeo: Support GPU animated instanced skinned meshes. | 新增功能：支持对 GPU 动画的实例化蒙皮网格体进行优化处理。 |
| 2026-05-12 | `10c54c93` | [FastGeo] Harden surrogate component physics queries | 修复/增强：加固了代理组件（surrogate component）的物理查询逻辑，提高稳定性。 |
| 2026-05-12 | `6fa3ba35` | [FastGeo] Fix world transform for unregistered components in runtime cell transformer | 修复了运行时单元转换器中未注册组件的变换矩阵计算问题。 |
| 2026-05-12 | `8ce6709d` | [FastGeo] Resolve WalkableSlopeOverride from BodySetup when building surrogate descriptor | 修复：在构建代理描述符时，现在能正确从 BodySetup 解析 WalkableSlopeOverride 设置。 |

### 维护评价

FastGeoStreaming 是一个创建于 2025 年 3 月的**实验性**插件，版本号为 0.1。尽管如此，从最近的提交记录（2026年5月）可以看出，它正处于**非常活跃的开发和维护**阶段。

- **近期更新频率**：非常高，仅在 2026 年 5 月 12-14 日就有 5 次提交，包含新功能支持、问题修复和代码优化。
- **更新内容**：涵盖了功能增强（支持更多网格体类型）、稳定性修复和代码质量提升。
- **维护状态**：**活跃开发中**。作为实验性功能，其 API 和实现可能随着开发而变化。
- **推荐度**：对于追求极致世界分区流式加载性能的项目，尤其是使用超大规模静态场景的开放世界游戏，**推荐关注和进行技术预研**。但由于其`EnabledByDefault=false`且标记为实验性，在生产环境中使用需要自行评估稳定性风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FastGeoStreaming)
- 测试用例路径未在提供信息中明确，通常可能位于 `Engine/Tests/FastGeoStreaming/` 或插件内部的 `Tests/` 目录。