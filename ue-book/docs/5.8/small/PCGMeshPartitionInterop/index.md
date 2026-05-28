# PCG Mesh Partition Interop

> Interoperability of Mesh Partition with PCG.

| 属性 | 值 |
|---|---|
| 中文名 | PCG网格分区互操作 |
| 分类 | Mesh Partition |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `PCGMeshPartitionInterop` (Runtime), `PCGMeshPartitionInteropEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-05 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGMeshPartitionInterop) | |

## 用途

本插件作为 PCG（程序化内容生成）框架与 Mesh Partition（网格分区）系统之间的桥梁。其主要目的是让 PCG 图能够利用 Mesh Partition 的功能，对程序化生成的网格进行分区处理，从而优化大规模程序化内容的渲染性能、内存管理和 LOD 处理。它解决了在 PCG 工作流中集成网格分区这一高级优化技术的问题。

## 使用场景

- 你在使用 PCG 框架生成广阔的世界地形，并需要将其自动分区为可管理的网格块以进行流式加载和 LOD 切换。
- 你需要程序化生成大规模城市或地牢，并希望自动将最终生成的复杂网格进行分区，以提升渲染效率。
- 你希望在 PCG 生成的内容上应用基于网格分区的优化策略，以管理内存和性能。

## 蓝图用法

本插件主要提供 PCG 数据交互节点和编辑器集成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BakeMeshAttr` | 将网格属性烘焙到网格分区中。 | `UPCGMeshPartitionSettings` |
| `BakeMeshTerrainSection` | 将网格烘焙为地形分区块。 | `UPCGMeshPartitionSettings` |
| `Get Mesh Terrain Section` | 获取网格地形分区块数据。 | `UPCGMeshPartitionSettings` |

### 使用示例（蓝图描述）

在 PCG 图中，你可以使用 `BakeMeshTerrainSection` 节点将程序化生成的网格体烘焙成地形分区块。该节点通常连接在生成最终网格的 PCG 节点之后。烘焙操作会在引擎中创建对应的网格分区资源，可用于后续的地形 LOD 和流式处理。

## C++ 用法

### 头文件引入

```cpp
// 引入核心模块
#include "PCGMeshPartitionInterop/PCGMeshPartitionInteropModule.h"
// 引入编辑器模块（仅在编辑器环境中）
#include "PCGMeshPartitionInteropEditor/PCGMeshPartitionInteropEditorModule.h"
```

### 基本用法

本插件的核心是通过 `PCGMeshPartitionSettings` 类来配置和执行网格分区与 PCG 的互操作。以下代码展示了如何在 C++ 中访问和配置相关设置（假设已有一个 `UPCGComponent`）：

```cpp
// 假设 `PCGComponent` 是一个有效的 UP指向 PCG 组件的指针
UPCGComponent* PCGComp = ...;

// 获取或创建与 PCG 组件关联的网格分区设置对象
UPCGMeshPartitionSettings* Settings = PCGComp->GetOrCreateSettings<UPCGMeshPartitionSettings>();

// 配置烘焙参数
Settings->bBakeMeshTerrain = true;
Settings->TerrainGridSize = FVector2D(1024.0f, 1024.0f);

// 触发一次烘焙操作（通常由 PCG 框架的执行流程自动调用）
if (Settings->CanExecute(PCGComp))
{
    Settings->Execute(PCGComp);
}
```
*（注：以上为基于模块接口推断的示例结构，具体 API 需参考实际头文件。）*

## Demo 示例

由于本插件主要提供 PCG 框架内的节点和编辑器工具，一个典型的“最小”示例是在 PCG 资产中正确连接相关节点。此处提供一个概念性的 C++ 结构，展示如何与插件提供的核心设置类交互。

```cpp
// MyPCGGraphManager.h
#pragma once
#include "CoreMinimal.h"
#include "PCGComponent.h"

class UMyPCGGraphManager
{
public:
    void InitializeAndBakeMeshPartition(UPCGComponent* InPCGComponent);
};

// MyPCGGraphManager.cpp
#include "MyPCGGraphManager.h"
#include "PCGMeshPartitionSettings.h" // 假设的设置头文件

void UMyPCGGraphManager::InitializeAndBakeMeshPartition(UPCGComponent* InPCGComponent)
{
    if (!InPCGComponent)
    {
        return;
    }

    // 获取插件提供的设置类
    UPROPERTY(Transient)
    UPCGMeshPartitionSettings* PartitionSettings = InPCGComponent->GetOrCreateSettings<UPCGMeshPartitionSettings>();

    if (PartitionSettings)
    {
        // 根据项目需求配置设置
        PartitionSettings->bEnabled = true;
        PartitionSettings->SomeRelevantParameter = ...;

        // 执行烘焙（实际调用点取决于你的 PCG 工作流）
        PartitionSettings->Execute(InPCGComponent);
    }
}
```

## 模块依赖

从插件的依赖关系（.uplugin 文件中的 `Plugins` 和模块 Build.cs 推断）来看，要使用此插件，你的项目或模块应依赖以下特有模块：

| 模块 | 用途 |
|---|---|
| `PCG` | 程序化内容生成框架核心 |
| `MeshPartition` | 网格分区系统 |
| `PCGGeometryScriptInterop` | PCG 与几何脚本的互操作层（本插件可能基于此构建） |

*（注：你的模块在 `Build.cs` 中应包含对上述模块的依赖。）*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `99ccb29e` | [PCG] Fix crash in BakeMeshAttr/BakeMeshTerrainSection reading RHI resources that either aren't resi... | 修复了`BakeMeshAttr`和`BakeMeshTerrainSection`节点在读取不合规RHI资源时导致的崩溃。 |
| 2026-05-14 | `82d81c0e` | [PCG] Add Bake Mesh Terrain Section Mesh node | 新增了“烘焙网格地形分区块网格”节点。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数产生的警告。 |
| 2026-05-13 | `0fc2fa0f` | [PCG] Track Final layer key for refresh on modifier changes in Get Mesh Terrain Section node | 在“获取网格地形分区块”节点中，追踪最终图层键以便在修改器更改时刷新。 |
| 2026-05-13 | `6cf8f045` | [PCG] Fix GPU crash arising from binding a compressed texture as a UAV which is not supported. | 修复了因将压缩纹理作为不支持的UAV绑定而导致的GPU崩溃。 |

### 维护评价

- **活跃度**：该插件近期（2026年5月）有频繁的提交，主要集中在功能新增（`BakeMeshTerrainSection` 节点）和稳定性修复（崩溃修复、GPU兼容性）上，表明其正处于活跃开发和修复阶段。
- **状态**：插件标记为**实验性**且**默认禁用**，说明它尚不稳定，API 可能发生变化，不建议在正式生产项目中直接使用。
- **推荐度**：适合在原型开发或技术预研中，用于探索 PCG 与网格分区的高级集成。由于其依赖 PCG、MeshPartition 等同样可能处于演进中的系统，使用时需注意版本兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGMeshPartitionInterop)
- [官方文档（PCG框架）](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGMeshPartitionInterop/Tests)