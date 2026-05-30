# Groom

> Rendering and simulation of grooms

| 属性 | 值 |
|---|---|
| 中文名 | 毛发系统 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Groom 资产模板） |
| 模块 | `HairCardGeneratorFramework` (Runtime), `HairStrandsCore` (Runtime), `HairStrandsDataflow` (Runtime), `HairStrandsDeformer` (Runtime), `HairStrandsEditor` (Runtime), `HairStrandsRuntime` (Runtime), `HairStrandsSolver` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-11-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/HairStrands) | |

## 用途

HairStrands（Groom）是 Unreal Engine 5 的**毛发渲染与模拟**插件，提供从资产导入到实时渲染和物理模拟的完整毛发管线。它解决了以下核心问题：

- **Groom 资产管理**：支持从 DCC 工具（如 Maya/Houdini）导入 Alembic 格式的毛发数据，将其转换为引擎内部的 Groom 资产格式
- **Strand-based 渲染**：基于每根发丝的逐点渲染，支持 LOD、绑定（Binding）和发片卡片（Hair Cards）等多种渲染策略
- **物理模拟**：通过 GroomSolver 组件实现毛发的物理驱动模拟，包括重力、碰撞、约束等
- **GPU 变形器集成**：通过 Optimus Deformer Graph 系统，允许用户在 GPU 上以节点图方式自定义毛发变形逻辑
- **数据流编辑**：通过 Dataflow 节点系统提供可视化的毛发数据处理能力

插件默认不启用（`EnabledByDefault=false`），需要在项目设置中手动开启。

## 模块架构

| 模块 | 职责 |
|---|---|
| **HairStrandsCore** | 核心数据结构：GroomAsset、FHairGroupInstance、渲染资源等基础类型定义 |
| **HairStrandsRuntime** | 运行时渲染管线：LOD 选择、绑定计算、GPU 资源管理 |
| **HairStrandsDeformer** | Optimus Deformer 集成：提供毛发相关的 Compute Data Interface 和 Data Provider |
| **HairStrandsSolver** | 物理求解器：GroomSolver 组件、碰撞检测、约束求解 |
| **HairStrandsDataflow** | Dataflow 节点系统：可视化的毛发数据处理节点 |
| **HairStrandsEditor** | 编辑器工具：Groom 资产编辑器、预览、属性面板 |
| **HairCardGeneratorFramework** | 发片卡片生成：将 Strand 数据转换为 Hair Cards 用于低 LOD 渲染 |

## 使用场景

- 你正在制作一个需要逼真头发的角色 → 使用 Groom 资产导入毛发并配置 GroomComponent
- 你需要头发随骨骼动画产生物理摆动 → 启用 GroomSolver 组件进行模拟
- 你需要自定义毛发变形逻辑（如风力扭曲、程序化造型） → 通过 Optimus Deformer Graph 使用 HairStrandsDeformer 模块
- 你的项目需要跨平台支持，在低端设备上用卡片替代发丝 → 使用 HairCardGeneratorFramework
- 你需要在数据流中处理毛发拓扑数据（如重采样、合并） → 使用 HairStrandsDataflow 节点

---

> 以下为 **HairStrandsDeformer** 子模块的详细文档。

# HairStrandsDeformer

## 子模块信息

| 属性 | 值 |
|---|---|
| 模块类型 | Runtime |
| 文件数 | ~30+（Private 头文件 + .cpp） |
| 核心功能 | Optimus Compute Framework 毛发数据接口 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/HairStrands/Source/HairStrandsDeformer) | |

## 用途

HairStrandsDeformer 是 Groom 插件与 **Optimus Deformer Graph**（基于 Compute Framework 的节点图变形系统）之间的桥梁模块。它实现了一系列 **Compute Data Interface** 和对应的 **Data Provider**，让用户能够在 Deformer Graph 中以 GPU 计算着色器的方式读取和写入毛发数据。

**核心价值**：没有此模块，Optimus 无法感知毛发数据（发丝点位、引导线、骨骼绑定等），用户也就无法通过可视化节点图创建自定义毛发变形效果。

## 架构概述

每个 Data Interface 遵循 Unreal Compute Framework 的标准三件套模式：

```
DataInterface (资源描述 + HLSL 生成)
    └── DataProvider (CPU 端数据收集)
        └── ProviderProxy (渲染线程 RDG 资源绑定)
```

### Data Interface 一览

| Data Interface | 类名 | 功能 |
|---|---|---|
| GroomStrandsRead | `UOptimusGroomStrandsReadDataInterface` | 读取毛发发丝（Strands）的位置、属性 |
| GroomStrandsWrite | `UOptimusGroomStrandsWriteDataInterface` | 写入变形后的发丝位置和属性 |
| GroomGuidesRead | `UOptimusGroomGuidesReadDataInterface` | 读取引导线（Guides）数据 |
| GroomGuidesWrite | `UOptimusGroomGuidesWriteDataInterface` | 写入变形后的引导线数据 |
| GroomAttributeRead | `UOptimusGroomAttributeReadDataInterface` | 读取自定义 Groom 属性（支持多种数据类型） |
| GroomCollisionRead | `UOptimusGroomCollisionReadDataInterface` | 读取碰撞网格数据（静态/骨骼网格体） |
| GroomMeshesRead | `UOptimusGroomMeshesReadDataInterface` | 读取绑定的骨骼网格体骨骼矩阵 |
| GroomSolverRead | `UOptimusGroomSolverReadDataInterface` | 读取求解器状态和模拟配置 |
| GroomExec | `UOptimusGroomExecDataInterface` | 定义执行域（每线程对应哪种元素） |

### 执行域（Execution Domains）

`EOptimusGroomExecDomain` 枚举定义了 GPU 计算内核可以操作的最小粒度：

| 枚举值 | 说明 | 所属类别 |
|---|---|---|
| `ControlPoint` (StrandsPoints) | 每个线程处理一个发丝控制点 | Strands |
| `Curve` (StrandsCurves) | 每个线程处理一根发丝曲线 | Strands |
| `StrandsEdges` | 每个线程处理一条发丝边 | Strands |
| `StrandsObjects` | 每个线程处理一个发丝对象 | Strands |
| `GuidesPoints` | 每个线程处理一个引导线控制点 | Guides |
| `GuidesCurves` | 每个线程处理一根引导线曲线 | Guides |
| `GuidesEdges` | 每个线程处理一条引导线边 | Guides |
| `GuidesObjects` | 每个线程处理一个引导线对象 | Guides |

### 组件源（Component Sources）

用于告诉 Optimus 系统哪些 Actor 组件可以作为数据源：

| 组件源类 | 绑定名称 | 绑定组件 |
|---|---|---|
| `UOptimusGroomAssetComponentSource` | Groom Asset | `UGroomComponent` |
| `UOptimusGroomSolverComponentSource` | Groom Solver | `UGroomSolverComponent` |
| `UOptimusGroomCollisionComponentSource` | Groom Collision | `UGroomSolverComponent` |

## 蓝图用法

本模块主要通过 **Optimus Deformer Graph 编辑器**使用，不直接暴露典型的 `BlueprintCallable` 节点。以下是蓝图中可访问的 Data Provider 属性：

### 数据绑定属性

| 属性 | 类型 | 说明 | 所在类 |
|---|---|---|---|
| `MeshComponent` | `TObjectPtr<UMeshComponent>` | 要绑定的 Groom 组件 | 各 `UOptimusGroom*DataProvider` |
| `SolverComponent` | `TObjectPtr<UGroomSolverComponent>` | 要绑定的求解器组件 | `UOptimusGroomSolverReadDataProvider`、`UOptimusGroomCollisionReadDataProvider` |
| `GroomAttributeName` | `FName` | 要读取的自定义属性名 | `UOptimusGroomAttributeReadDataProvider` |
| `GroomAttributeGroup` | `EOptimusGroomExecDomain` | 属性所属的执行域 | `UOptimusGroomAttributeReadDataProvider` |
| `GroomAttributeType` | `EOptimusGroomAttributeTypes` | 属性数据类型 | `UOptimusGroomAttributeReadDataProvider` |

### 自定义属性类型

`EOptimusGroomAttributeTypes` 支持的属性数据类型：

`Bool`、`Int`、`IntVector2`、`IntVector3`、`IntVector4`、`Uint`、`Float`、`Vector2`、`Vector3`、`Vector4`、`LinearColor`、`Quat`、`Rotator`、`Transform`、`Matrix3x4`

### 使用示例（Optimus Deformer Graph）

1. **在角色蓝图上**添加 `GroomComponent`，加载 Groom 资产
2. **创建 Deformer Graph**：在内容浏览器中右键 → Animation → Deformer Graph
3. **配置组件源**：在 Deformer Graph 编辑器中，选择 "Groom Asset" 作为绑定源
4. **添加执行域**：拖入 `GroomExec` 节点，选择如 `GuidesPoints` 域
5. **添加数据读取**：连接 `GroomGuidesRead` 节点获取引导线数据
6. **编写自定义内核**：添加 Custom Compute Kernel 节点，处理读入的位置数据
7. **添加数据写入**：连接 `GroomGuidesWrite` 节点输出变形结果
8. **绑定到组件**：在 GroomComponent 的 Details 面板中指定 Deformer Graph

## C++ 用法

### 头文件引入

```cpp
// 引入工具函数（私有头文件，仅模块内部使用）
#include "DeformerGroomInterfaceUtils.h"
#include "DeformerGroomDomainsExec.h"
#include "DeformerGroomDomainsSource.h"
```

### 基本用法：收集 Groom 组件的 GroupInstance

从 `DeformerGroomInterfaceUtils.h` 提取的核心工作流：

```cpp
#include "DeformerGroomInterfaceUtils.h"
#include "GroomComponent.h"

// 收集 Actor 上的所有 Groom 组件
void GatherGroomData(UActorComponent* InComponent)
{
    using namespace UE::Groom::Private;
    
    TArray<const UGroomComponent*> GroomComponents;
    GatherGroomComponents(InComponent, GroomComponents);
    
    // 将 GroomComponent 转换为 GroupInstance（用于 GPU 数据绑定）
    TArray<TRefCountPtr<const FHairGroupInstance>> GroupInstances;
    GroomComponentsToInstances(GroomComponents, GroupInstances);
    
    // 检查实例资源是否就绪
    if (HaveStrandsInstanceResources(GroupInstances) && 
        HaveGuidesInstanceResources(GroupInstances))
    {
        // 资源已初始化，可以安全地构建 GPU Dispatch
    }
}
```

### 进阶用法：获取骨骼绑定数据

从 `GroomComponentsToSkelmeshes` 函数提取的骨骼网格绑定流程：

```cpp
void GetSkinBindingData(const UGroomComponent* GroomComponent)
{
    using namespace UE::Groom::Private;
    
    TArray<const UGroomComponent*> GroomComponents = {GroomComponent};
    
    TArray<const FSkeletalMeshObject*> SkeletalMeshes;
    TArray<FMatrix44f> SkeletalTransforms;
    TArray<TArray<FMatrix44f>> BonesRefToLocals;
    TArray<TArray<FMatrix44f>> BindTransforms;
    TArray<TRefCountPtr<const FHairGroupInstance>> GroupInstances;
    
    // 一次性收集所有绑定所需的骨骼数据
    GroomComponentsToSkelmeshes(
        GroomComponents,
        SkeletalMeshes,       // 每个 Group 对应的骨骼网格体
        SkeletalTransforms,   // 骨骼空间到 Groom 空间的变换矩阵
        BonesRefToLocals,     // 每根骨骼的 Ref->Local 矩阵
        BindTransforms,       // 绑定变换矩阵（逆参考姿态）
        GroupInstances        // 对应的毛发实例
    );
    
    // 现在可以将这些数据上传到 GPU 用于计算着色器
}
```

### 进阶用法：计算执行域的元素数量

```cpp
void CalculateDispatchCounts(const UGroomComponent* GroomComponent)
{
    using namespace UE::Groom::Private;
    
    TArray<const UGroomComponent*> GroomComponents = {GroomComponent};
    TArray<int32> InvocationCounts;
    
    // 计算 Strands Points 域的总元素数
    int32 TotalPoints = GetGroomInvocationElementCounts(
        GroomComponents,
        UOptimusGroomAssetComponentSource::FStrandsExecutionDomains::Points,
        InvocationCounts
    );
    
    // 计算 Guides Curves 域的总元素数
    TArray<int32> GuideCounts;
    int32 TotalGuides = GetGroomInvocationElementCounts(
        GroomComponents,
        UOptimusGroomAssetComponentSource::FGuidesExecutionDomains::Curves,
        GuideCounts
    );
}
```

## 模块依赖

从源码分析推断的依赖关系：

| 模块 | 用途 |
|---|---|
| `HairStrandsCore` | 毛发核心数据结构（FHairGroupInstance、UGroomAsset 等） |
| `ComputeFramework` | Optimus/Compute Framework 基础设施（UComputeDataInterface、UComputeDataProvider） |
| `HairStrandsSolver` | 求解器组件和设置（UGroomSolverComponent、FGroomSolverSettings） |
| `OptimusCore` | Optimus 节点系统（UOptimusNode、UOptimusComponentSource） |
| `RenderCore` | RDG 构建器和渲染资源（FRDGBuilder、FRDGBufferSRVRef） |
| `RHI` | 底层图形接口（FRHIShaderResourceView） |

> 无特殊依赖（仅标准 Core/Engine/Slate 等 + 上述模块特有依赖）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `aa770ac7` | Remove crash in mobile renderer when using groom binding. | 修复移动端渲染器使用毛发绑定时的崩溃 |
| 2026-05-26 | `3da4e98e` | Fix crash when selecting the addSolverDeformer dataflow node | 修复选择 addSolverDeformer 数据流节点时的崩溃 |
| 2026-05-26 | `d2f5bcd4` | Fix crash when recompiling BP while playing groom in dataflow editor + fix bad number of vertices ca | 修复数据流编辑器中重编译蓝图时的崩溃及顶点数计算错误 |
| 2026-05-22 | `9ce84766` | Remove the CreateGroomDataflowAsset from the context menu | 从右键菜单中移除创建 Groom Dataflow 资产的选项 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口通知逻辑，减少重复代码 |

### 维护评价

**活跃维护**。最近的提交集中在 2026 年 5 月，距离本文档时间仅数天，显示插件仍在积极维护中。

- **创建时间**：2020-11-24，随 UE5 早期开发引入
- **更新频率**：近期一周内有多次提交，以稳定性修复为主（修复崩溃、修复计算错误）
- **维护状态**：活跃维护中，Epic 持续投入
- **已知限制**：`EnabledByDefault=false`，需手动启用；部分功能仍标记为实验性
- **推荐度**：✅ 推荐使用。这是 UE5 官方毛发系统的唯一实现，对于需要高质量毛发渲染的项目是必选插件。GPU 变形器集成使得高级用户可以扩展毛发行为。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/HairStrands)
- [Deformer 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/HairStrands/Source/HairStrandsDeformer)
- 官方文档：无（`.uplugin` 中 DocsURL 为空）