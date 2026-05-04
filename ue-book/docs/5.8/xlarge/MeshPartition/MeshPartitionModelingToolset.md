# Mesh Partition

> Large-scale mesh authoring system through spatial partitioning, non-destructive modifier editing, and platform-adaptive runtime representations.

| 属性 | 值 |
|---|---|
| 分类 | Mesh Partition |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（建模工具、编辑器扩展、材质模板） |
| 模块 | `MeshPartition` (Runtime), `MeshPartitionCompute` (Runtime), `MeshPartitionEditor` (Runtime), `MeshPartitionEditorUI` (Runtime), `MeshPartitionModelingToolset` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshPartition) | |

## 用途

Mesh Partition 是一个大规模网格空间分区与建模系统，解决的核心问题是：**如何在 UE5 中高效地创建、编辑和管理超大规模的网格资产（MegaMesh）**。

传统网格工作流在处理大型地形或建筑群时面临内存瓶颈和编辑困难。Mesh Partition 通过以下方式解决这些问题：

1. **空间分区（Spatial Partitioning）**：将大型网格自动或手动分割为多个 Section，每个 Section 独立存储和加载，支持 World Partition 按需加载
2. **非破坏性修改器编辑（Non-destructive Modifier Editing）**：通过 Modifier 组件栈对网格进行层叠式编辑，支持布尔、噪声、样条、重网格化等多种修改器，可随时调整或移除
3. **平台自适应运行时表示（Platform-adaptive Runtime Representations）**：针对不同平台（移动端/PC/主机）自动优化网格的运行时表现
4. **完整的建模工具集**：提供转换、分割、合并、缝合、扩展、高度雕刻、高度图导入等一整套建模工具，集成到 UE5 的 Modeling Mode 中

本质上，这是一个面向开放世界和大型场景的 **程序化网格资产管线**。

## 使用场景

- 你在制作开放世界游戏，需要管理超大地形网格 → 用 Mesh Partition 的空间分区和高度图导入
- 你需要对大型网格进行非破坏性编辑（布尔运算、噪声变形等） → 用 Modifier 系统
- 你需要将一个大网格拆分为多个可独立加载的 Section → 用 Split/Resection 工具
- 你需要将多个小网格合并为一个整体 → 用 Merge/Stitch 工具
- 你需要在网格边界上挤出或镜像新几何体 → 用 Expand 工具
- 你需要对网格顶点进行高度雕刻（类似地形编辑） → 用 Height Sculpt 工具
- 你需要从高度图文件批量生成网格 → 用 Heightmap Import 工具
- 你需要在网格上绘制权重通道（用于修改器混合） → 用 Attribute Paint 工具

## 蓝图用法

本模块（MeshPartitionModelingToolset）主要提供编辑器建模工具，蓝图 API 有限。核心交互通过 Modeling Mode 工具面板完成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddChannel` | 添加新的权重通道用于属性绘制 | `UAttributePaintToolAddChannelProperties` |
| `Weld` | 缝合工具：焊接选中边 | `UStitchToolActions` |
| `FillHole` | 缝合工具：填充孔洞 | `UStitchToolActions` |
| `PostAction` | 触发缝合工具动作 | `UStitchToolActions` |

### 使用示例（蓝图描述）

本插件的工具主要通过编辑器 UI 操作，而非蓝图节点调用。典型工作流：

1. 在 Modeling Mode 工具栏中找到 "Mega Mesh Tools" 选项卡
2. 选择目标网格后，点击对应工具按钮（Convert / Split / Merge 等）
3. 在工具属性面板中调整参数
4. 点击 Accept 应用修改

## C++ 用法

### 头文件引入

```cpp
#include "MeshPartitionConvertTool.h"
#include "MeshPartitionSplitTool.h"
#include "MeshPartitionMergeTool.h"
#include "MeshPartitionExpandTool.h"
#include "MeshPartitionHeightSculptTool.h"
#include "MeshPartitionHeightmapImportTool.h"
#include "MeshPartitionStitchTool.h"
#include "MeshPartitionResectionTool.h"
#include "MeshPartitionPlaceModifierTool.h"
#include "MeshPartitionAttributePaintTool.h"
#include "MeshPartitionCreateMeshTool.h"
```

### 基本用法 - 工具注册

本模块通过 `IModelingModeToolExtension` 接口将工具注册到 UE5 的 Modeling Mode 中。

```cpp
// 来源: Public/MeshPartitionModelingToolsetModule.h
namespace UE::MeshPartition
{
class FMegaMeshModelingToolsetModule : public IModuleInterface, public IModelingModeToolExtension
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    // IModelingModeToolExtension - 向 Modeling Mode 注册工具
    virtual FText GetExtensionName() override;
    virtual FText GetToolSectionName() override;
    virtual void GetExtensionTools(
        const FExtensionToolQueryInfo& QueryInfo,
        TArray<FExtensionToolDescription>& ToolsOut) override;
};
}
```

### 基本用法 - 命令注册

```cpp
// 来源: Private/MeshPartitionModelingToolCommands.h
class FMegaMeshModelingToolCommands : public TCommands<FMegaMeshModelingToolCommands>
{
public:
    FMegaMeshModelingToolCommands();

    TSharedPtr<FUICommandInfo> MegaMeshToolsTabButton;
    TSharedPtr<FUICommandInfo> BeginConvertMeshTool;
    TSharedPtr<FUICommandInfo> BeginSplitMeshTool;
    TSharedPtr<FUICommandInfo> BeginMergeMeshTool;
    TSharedPtr<FUICommandInfo> BeginResectionMeshTool;
    TSharedPtr<FUICommandInfo> BeginStitchMeshTool;
    TSharedPtr<FUICommandInfo> BeginHeightmapImport;
    TSharedPtr<FUICommandInfo> BeginHeightSculptTool;
    TSharedPtr<FUICommandInfo> BeginExpandMeshTool;
    TSharedPtr<FUICommandInfo> BeginCreateMegaMeshRectangleTool;
    TSharedPtr<FUICommandInfo> BeginAddModifierTool;

    virtual void RegisterCommands() override;
};
```

### 进阶用法 - 自定义 Tool Target

Tool Target 是连接建模工具与实际网格数据的桥梁。Mesh Partition 提供了多种 Tool Target 实现：

```cpp
// 来源: Public/MeshPartitionToolTarget.h
// 整个 AMeshPartition Actor 的 Tool Target
UCLASS(Transient, MinimalAPI)
class UMeshPartitionToolTarget :
    public UPrimitiveComponentToolTarget,
    public IDynamicMeshProvider,
    public IDynamicMeshCommitter,
    public IMaterialProvider,
    public IPhysicsDataSource
{
    // 获取合并后的动态网格
    virtual Geometry::FDynamicMesh3 GetDynamicMesh() override;
    
    // 提交修改后的网格（自动拆分回各 Section）
    virtual void CommitDynamicMesh(
        const Geometry::FDynamicMesh3& InMesh,
        const FDynamicMeshCommitInfo& InCommitInfo) override;
};
```

```cpp
// 来源: Public/MeshPartitionMultiSectionToolTarget.h
// 多 Section 合并编辑的 Tool Target
UCLASS(Transient, MinimalAPI)
class UMultiSectionToolTarget : public UToolTarget,
    public IDynamicMeshProvider,
    public IDynamicMeshCommitter,
    public IPrimitiveComponentBackedTarget,
    public IMaterialProvider
{
    // 初始化：传入多个基础 Section
    void Initialize(const TArray<TObjectPtr<UMeshProviderModifier>> BaseSections);
    
    // 获取合并后的网格用于编辑
    virtual Geometry::FDynamicMesh3 GetDynamicMesh() override;
    
    // 提交时自动拆分回各 Section
    virtual void CommitDynamicMesh(
        const Geometry::FDynamicMesh3& InMesh,
        const FDynamicMeshCommitInfo& InCommitInfo) override;
};
```

```cpp
// 来源: Public/MeshPartitionModifierToolTarget.h
// Modifier 组件的 Tool Target - 支持查看修改器应用后的网格
UCLASS(Transient, MinimalAPI)
class UModifierToolTarget :
    public USceneComponentToolTarget,
    public IDynamicMeshProvider,
    public IMaterialProvider,
    public IPhysicsDataSource
{
    void Initialize(UModifierComponent* ModifierComponent);
    
    // 获取修改器应用后的网格
    virtual Geometry::FDynamicMesh3 GetDynamicMesh() override;
    
    // 配置预览渲染
    void ConfigurePreviewForRendering(UPrimitiveComponent* PrimitiveComponent) const;
    void UpdateRenderTextureForPreview(const Geometry::FDynamicMesh3& PreviewMesh);
};
```

### 进阶用法 - 网格三角形分配到边界

```cpp
// 来源: Private/MeshPartitionToolTargetUtils.h
namespace UE::MeshPartition
{
    // 将网格三角形分配到最近的包围盒
    // 返回数组：索引为三角形 ID，值为最近包围盒的索引
    TArray<int32> AssignMeshTrisToClosestBounds(
        const UE::Geometry::FDynamicMesh3& Mesh,
        const TArray<UE::Geometry::FAxisAlignedBox3d>& Bounds,
        int32 DefaultAssignment = 0);
}
```

## Demo 示例

### 创建自定义建模工具扩展

```cpp
// MyMeshPartitionToolExtension.h
#pragma once

#include "CoreMinimal.h"
#include "ModelingModeToolExtensions.h"

class FMyMeshPartitionToolExtension : public IModelingModeToolExtension
{
public:
    virtual FText GetExtensionName() override
    {
        return NSLOCTEXT("MyExtension", "Name", "My Mesh Partition Tools");
    }

    virtual FText GetToolSectionName() override
    {
        return NSLOCTEXT("MyExtension", "Section", "Custom Tools");
    }

    virtual void GetExtensionTools(
        const FExtensionToolQueryInfo& QueryInfo,
        TArray<FExtensionToolDescription>& ToolsOut) override
    {
        // 注册自定义工具到 Modeling Mode
        FExtensionToolDescription Desc;
        Desc.ToolName = NSLOCTEXT("MyExtension", "MyTool", "My Custom Tool");
        Desc.ToolBuilder = NewObject<UMyCustomToolBuilder>();
        ToolsOut.Add(Desc);
    }
};
```

### 使用预览网格工具

```cpp
// MyPreviewExample.h
#pragma once

#include "CoreMinimal.h"
#include "MeshPartitionToolPreviewActor.h"

class FMyPreviewExample
{
    void CreatePreview(const MeshPartition::FMeshData& MeshData,
                       const MeshPartition::FSectionChannels& ChannelData,
                       UMaterialInterface* Material)
    {
        // 创建预览 Actor
        AToolPreviewMesh* PreviewActor = GetWorld()->SpawnActor<AToolPreviewMesh>();
        
        // 设置网格数据
        PreviewActor->SetMesh(MakeSharedRef<const MeshPartition::FMeshData>(MeshData));
        
        // 设置通道数据（用于权重可视化）
        PreviewActor->SetChannelData(ChannelData);
        
        // 设置材质
        PreviewActor->SetMaterial(Material);
    }
};
```

### 创建预览网格线

```cpp
// MyGridPreview.h
#pragma once

#include "CoreMinimal.h"
#include "MeshPartitionPreviewUtils.h"
#include "Drawing/PreviewGeometry.h"

class FMyGridPreview
{
    void CreateGridPreview(UPreviewGeometry* PreviewGeo)
    {
        FBox Bounds(FVector(-500, -500, 0), FVector(500, 500, 100));
        FIntVector Dims(4, 4, 1); // 4x4 网格
        
        UE::MeshPartition::CreatePreviewGridLines(
            Bounds,
            Dims,
            TEXT("SectionGrid"),
            PreviewGeo
        );
    }
};
```

## 模块依赖

从 Build.cs 分析，本插件依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `ModelingToolsEditorMode` | Modeling Mode 集成，工具注册和扩展接口 |
| `ModelingTools` | 基础建模工具框架（BrushOp、SelectionTool 等） |
| `ModelingComponents` | 建模组件（PreviewMesh、ToolTarget 等） |
| `InteractiveToolsFramework` | 交互式工具框架 |
| `DynamicMesh` | 动态网格数据结构（FDynamicMesh3） |
| `GeometryFramework` | 几何框架（PreviewGeometry、DynamicMeshComponent） |
| `MeshModelingTools` | 网格建模工具基类（MeshAttributePaintTool、MeshVertexSculptTool） |
| `MeshPartition` | 核心分区模块（FMeshData、FSectionChannels 等数据结构） |
| `MeshPartitionCompute` | 计算模块（分区算法、网格处理） |
| `MeshPartitionEditor` | 编辑器模块（编辑器组件、资产类型） |

## 维护状态

### 近期更新

- 2026-04-24 `44085aba` Mesh Partition: avoid passing hard-coded SM6 argument to GenerateMips. Fixes a crash on projects wit
- 2026-04-24 `473e05b1` Mesh Terrain sculpt layer tools:
- 2026-04-24 `bb6e1b38` Guard against empty UV-Layers and unset element triangles
- 2026-04-23 `2a27739c` Add a path where the for-all-modifiers iteration allows null modifiers to be silently skipped, to av
- 2026-04-23 `dbed6742` Fix broken handling of UV seams at mesh skirt vertices -- take care to copy the UVs from the vertice

### 维护评价

- **创建时间**：2026-04-23，非常新的实验性插件
- **维护状态**：🆕 新创建的实验性插件，由 Epic Games 开发
- **实验性标记**：⚠️ 位于 `Experimental` 目录，`EnabledByDefault=false`，需要手动启用
- **API 稳定性**：⚠️ 实验性插件的 API 可能在版本间发生破坏性变更
- **模块类型异常**：所有 5 个模块均标记为 `Runtime`，但 `MeshPartitionEditor` 和 `MeshPartitionEditorUI` 从名称看应为 Editor 类型，这可能是实验阶段的临时配置
- **推荐使用**：适合早期采用者和实验性项目。生产环境建议等待正式发布或密切关注 API 变更

**⚠️ 警告**：此插件为实验性功能，API 和功能可能在后续版本中发生重大变更。在生产项目中使用前请充分评估风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshPartition)
- [官方文档](https://dev.epicgames.com/community/learning/knowledge-base/nK7J/unreal-engine-introduction-to-mesh-terrain)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshPartition/Tests)（如果存在）