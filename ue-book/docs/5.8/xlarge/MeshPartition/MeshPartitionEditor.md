# Mesh Partition

> Large-scale mesh authoring system through spatial partitioning, non-destructive modifier editing, and platform-adaptive runtime representations.

| 属性 | 值 |
|---|---|
| 分类 | Mesh Partition |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MeshPartition` (Runtime), `MeshPartitionCompute` (Runtime), `MeshPartitionEditor` (Runtime), `MeshPartitionEditorUI` (Runtime), `MeshPartitionModelingToolset` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshPartition) | |

## 用途

Mesh Partition 是一个面向大规模地形/环境网格的编辑与运行时系统。它解决的核心问题是：**如何在编辑器中以非破坏性方式对超大网格进行空间分区、修改器叠加编辑，并在运行时按平台自适应地表示这些网格**。

与传统的 StaticMesh 工作流不同，Mesh Partition 将网格拆分为多个空间分区（Section），每个分区可以独立构建、缓存和加载。修改器（Modifier）以组件形式挂载在 Actor 上，通过优先级排序和依赖图并行执行，最终合并为运行时网格。系统内置了 DDC（Derived Data Cache）支持，避免重复构建。

**为什么存在**：UE5 的 World Partition 系统需要一种方式来处理超大规模地形网格——传统单个 StaticMesh 无法高效处理数十平方公里的地形。Mesh Partition 提供了从编辑器创作到运行时渲染的完整管线，支持交互式预览、编译优化和平台自适应。

## 使用场景

- 你在制作开放世界游戏，需要对大面积地形进行非破坏性编辑（重网格化、细分、纹理贴图等）→ 用 Mesh Partition 的 Modifier 系统
- 你需要将超大网格按空间分区为多个 Section，配合 World Partition 按需加载 → 用 Mesh Partition 的空间分区和 Transformer 管线
- 你需要为不同平台（主机/PC/移动端）生成不同精度的碰撞和渲染网格 → 用 Mesh Partition 的平台自适应 Transformer
- 你需要从高度图文件快速生成分区地形 → 用 Mesh Partition 的 Heightmap Importer
- 你需要在编辑器中交互式地调整修改器参数并实时预览效果 → 用 Mesh Partition 的 Interactive Section 系统

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetInteractiveModifiers` | 设置交互式修改器列表及构建参数 | `AInteractiveSection` |
| `ClearInteractiveModifiers` | 重置交互式修改器，取消所有待处理任务 | `AInteractiveSection` |
| `AddModifier` | 向交互式 Section 添加修改器 | `AInteractiveSection` |
| `RemoveModifier` | 从交互式 Section 移除修改器 | `AInteractiveSection` |
| `OnModifierChanged` | 修改器参数变更后通知交互式 Section 更新 | `AInteractiveSection` |
| `Update` | 刷新编辑器组件，重建待处理的修改 | `UMeshPartitionEditorComponent` |
| `Import` | 执行高度图导入操作 | `FHeightmapImporter` (C++ only) |

### 修改器组件（UModifierComponent）

修改器以 `UModifierComponent` 形式存在，挂载在 `AModifierActor` 上。每个修改器需要实现：

- `InitializeModifier()` — 初始化修改器
- `UninitializeModifier()` — 清理修改器
- 创建对应的 `IModifierBackgroundOp` 来执行后台修改操作

### 材质表达式节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MeshPartitionResource` | 获取 MeshPartition 通道纹理资源（Texture2DArray） | `UMaterialExpressionMeshPartitionResource` |
| `MeshPartitionTexcoord` | 获取 MeshPartition 通道的纹理坐标 | `UMaterialExpressionMeshPartitionTexcoord` |
| `MeshPartitionChannelSample` | 在指定纹理坐标处采样某个通道 | `UMaterialExpressionMeshPartitionChannelSample` |

## C++ 用法

### 头文件引入

```cpp
#include "MeshPartitionEditorComponent.h"
#include "MeshPartitionModifierComponent.h"
#include "MeshPartitionMeshBuilder.h"
#include "MeshPartitionEditorSubsystem.h"
#include "MeshPartitionHeightmapImporter.h"
```

### 基本用法 — 启动网格构建

从 `MeshPartitionMeshBuilder.h` 提取的构建管线用法：

```cpp
#include "MeshPartitionMeshBuilder.h"

// 配置构建参数
UE::MeshPartition::FBuilderSettings Settings;
Settings.BuildType = UE::MeshPartition::EBuildType::Request;
Settings.Transform = FTransform::Identity;
Settings.ModifiersToProcess = ModifierComponents; // TArray<UModifierComponent*>
Settings.TypePriorities = { TEXT("Base"), TEXT("Remesh"), TEXT("Tessellate") };
Settings.bRecomputeNormals = true;
Settings.bRecomputeTangents = true;

// 启动异步构建
TArray<UE::MeshPartition::FBuildTaskHandle> Tasks = UE::MeshPartition::Build::LaunchBuilds(Settings);

// 等待完成
UE::MeshPartition::Build::Wait(Tasks);

// 检查是否全部完成
bool bDone = UE::MeshPartition::Build::AreAllTasksComplete(Tasks);
```

### 基本用法 — 网格空间分区

```cpp
#include "MeshPartitionMeshBuilder.h"

// 将网格按网格单元大小拆分
double CellSize = 10000.0; // 100m per cell
TMap<FIntVector, UE::MeshPartition::FMeshData> CellMeshes = 
    UE::MeshPartition::GridHelpers::BuildGridCellMeshes(MeshData, CellSize);

// 计算网格维度
UE::MeshPartition::GridHelpers::FGridDimensions Dims = 
    UE::MeshPartition::GridHelpers::ComputeGridDimensions(Bounds, CellSize);
```

### 进阶用法 — 自定义修改器后台操作

从 `MeshPartitionRemeshOp.h` 和 `MeshPartitionModifierComponent.h` 提取：

```cpp
#include "MeshPartitionModifierComponent.h"

// 自定义修改器后台操作
class FMyModifierBackgroundOp : public UE::MeshPartition::IModifierBackgroundOp
{
public:
    FMyModifierBackgroundOp(const FName& InOperationName) 
        : IModifierBackgroundOp(InOperationName) {}

    virtual void GetInstancesInBounds(const FBox& InBounds, 
        TArray<FInstanceInfo>& OutInstanceInfos) const override
    {
        // 返回在给定边界内的修改器实例
        FInstanceInfo Info;
        Info.Bounds = ModifierBounds;
        OutInstanceInfos.Add(Info);
    }

    virtual void ApplyModifications(UE::MeshPartition::FMeshView& InMeshView, 
        const FTransform3d& InTransform, const FInstanceInfo& InInstanceInfo) const override
    {
        // 获取子网格进行修改
        Geometry::FDynamicMesh3& SubMesh = InMeshView.GetSubmesh();
        // ... 对 SubMesh 进行几何操作 ...
    }

    virtual bool DisableDDCWrite() const override { return false; }
};
```

### 进阶用法 — 修改器任务图并行执行

从 `MeshPartitionModifierTaskGraph.h` 提取：

```cpp
#include "MeshPartitionModifierTaskGraph.h"

// 创建任务图并执行修改器
UE::MeshPartition::FModifierTaskGraph TaskGraph;

TArray<FName> TypePriorities = { TEXT("Base"), TEXT("Remesh"), TEXT("TexturePatch") };
FTransform WorldTransform = Actor->GetActorTransform();

// 执行：传入基础网格、修改器组、优先级
Tasks::FTask CompletionTask = TaskGraph.Execute(
    MoveTemp(BaseMesh),
    BaseGroupCacheKey,
    MoveTemp(ModifierGroup),
    WorldTransform,
    TypePriorities,
    true // bUseCache
);

// 等待完成并获取结果
TaskGraph.WaitForCompletion();
UE::MeshPartition::FMeshData& ResultMesh = TaskGraph.GetResultMesh();
UE::MeshPartition::FBuildPerfStats PerfStats = TaskGraph.GetBuildPerfStats();
```

### 进阶用法 — 碰撞生成

从 `MeshPartitionCollisionGeneration.h` 提取：

```cpp
#include "MeshPartitionCollisionGeneration.h"

// 配置碰撞简化参数
UE::MeshPartition::Collision::FCollisionSimplificationSettings SimplSettings;
SimplSettings.bSimplifyCollision = true;
SimplSettings.SimplifyMethod = UE::MeshPartition::Collision::ECollisionSimplificationMethod::QEM;
SimplSettings.ErrorTolerance = 10.f;
SimplSettings.bScaleAccuracyViaNormal = true;
SimplSettings.ScaleAccuracyNormalDirection = FVector(0, 0, 1); // 向上方向精度更高

// 配置网格到碰撞转换
UE::MeshPartition::Collision::FMeshToCollisionSettings Settings;
Settings.SimplificationSettings = SimplSettings;
Settings.DefaultPhysicalMaterial = DefaultPhysMat;
Settings.bFastCook = true;

// 执行转换
UE::MeshPartition::FMeshPartitionCollisionData CollisionData;
UE::MeshPartition::Collision::ConvertMeshToCollisionData(MeshData, CollisionData, Settings);
```

## Demo 示例

### 自定义修改器组件

```cpp
// MyCustomModifier.h
#pragma once

#include "MeshPartitionModifierComponent.h"
#include "MyCustomModifier.generated.h"

UCLASS()
class UMyCustomModifier : public UE::MeshPartition::UModifierComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "My Modifier")
    float Strength = 1.0f;

    virtual void InitializeModifier() override
    {
        Super::InitializeModifier();
        // 初始化资源
    }

    virtual void UninitializeModifier() override
    {
        Super::UninitializeModifier();
        // 清理资源
    }

    virtual TSharedPtr<UE::MeshPartition::IModifierBackgroundOp> CreateBackgroundOp() const override;
};
```

```cpp
// MyCustomModifier.cpp
#include "MyCustomModifier.h"

class FMyCustomBackgroundOp : public UE::MeshPartition::IModifierBackgroundOp
{
public:
    float OpStrength;

    FMyCustomBackgroundOp(const FName& InName, float InStrength)
        : IModifierBackgroundOp(InName)
        , OpStrength(InStrength)
    {}

    virtual void GetInstancesInBounds(const FBox& InBounds,
        TArray<FInstanceInfo>& OutInstanceInfos) const override
    {
        FInstanceInfo Info;
        Info.Bounds = ModifierBounds;
        OutInstanceInfos.Add(Info);
    }

    virtual void ApplyModifications(UE::MeshPartition::FMeshView& InMeshView,
        const FTransform3d& InTransform, const FInstanceInfo& InInstanceInfo) const override
    {
        Geometry::FDynamicMesh3& Mesh = InMeshView.GetSubmesh();
        for (int VID : Mesh.VertexIndicesItr())
        {
            FVector3d Pos = Mesh.GetVertex(VID);
            // 应用自定义修改
            Pos.Z += OpStrength * FMath::Sin(Pos.X * 0.01);
            Mesh.SetVertex(VID, Pos);
        }
    }

    virtual bool DisableDDCWrite() const override { return false; }
};

TSharedPtr<UE::MeshPartition::IModifierBackgroundOp> UMyCustomModifier::CreateBackgroundOp() const
{
    return MakeShared<FMyCustomBackgroundOp>(GetFName(), Strength);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GeometryFramework` | 动态网格（FDynamicMesh3）基础框架 |
| `MeshConversion` | 网格数据格式转换 |
| `ModelingComponents` | 建模操作组件（Remesh、Tessellate 等） |
| `ModelingOperators` | 建模算子（RemeshMeshOp 等） |
| `MeshModelingToolset` | 网格建模工具集 |
| `DynamicMesh` | 动态网格数据结构 |
| `GeometryCore` | 几何核心算法（AABB 树、空间查询） |
| `WorldPartition` | World Partition 集成（ActorDesc、RuntimeCell） |
| `Foliage` | 植被系统集成（BaseID 过滤） |
| `RenderCore` | 渲染核心（场景代理、纹理） |
| `MaterialShaderQualitySettings` | 材质着色器质量设置 |

## 维护状态

### 近期更新

- 2026-04-24 `44085aba` Mesh Partition: avoid passing hard-coded SM6 argument to GenerateMips. Fixes a crash on projects wit
- 2026-04-24 `473e05b1` Mesh Terrain sculpt layer tools:
- 2026-04-24 `bb6e1b38` Guard against empty UV-Layers and unset element triangles
- 2026-04-23 `2a27739c` Add a path where the for-all-modifiers iteration allows null modifiers to be silently skipped, to av
- 2026-04-23 `dbed6742` Fix broken handling of UV seams at mesh skirt vertices -- take care to copy the UVs from the vertice

### 维护评价

- **状态**：实验性插件（Experimental），默认未启用
- **代码成熟度**：高——包含完整的编辑器管线、异步任务图、DDC 缓存、碰撞生成、材质表达式、World Partition 集成
- **模块化程度**：高——5 个独立模块（Runtime 核心、Compute、Editor、EditorUI、ModelingToolset）
- **推荐使用**：适合需要大规模地形网格编辑的项目，但作为实验性功能，API 可能在未来版本中发生变化。建议在生产环境中谨慎使用，关注后续版本的稳定性更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshPartition)
- [官方文档](https://dev.epicgames.com/community/learning/knowledge-base/nK7J/unreal-engine-introduction-to-mesh-terrain)