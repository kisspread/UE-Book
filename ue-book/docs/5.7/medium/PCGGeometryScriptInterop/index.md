# PCG Geometry Script Interop

> Extra plugin for Procedural Content Generation Framework interacting with Geometry Scripts.

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（INI 配置重定向） |
| 模块 | `PCGGeometryScriptInterop` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-03-14 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/PCGInterops/PCGGeometryScriptInterop) | |

## 用途

PCG Geometry Script Interop 是 PCG（Procedural Content Generation）框架与 Geometry Script 之间的桥梁插件。它提供了一组 PCG 节点，让开发者可以在 PCG 图中直接操作 **Dynamic Mesh**（动态网格）数据——这是 UE5 Geometry Script 的核心数据类型。

这个插件解决的核心问题是：PCG 原生只支持处理 Points、Spline、Volume 等空间数据类型，而 Geometry Script 工作在 Dynamic Mesh 上。没有这个插件，你无法在 PCG 流程中执行网格布尔运算、网格采样、样条转网格等几何操作。有了它，你可以在 PCG 图中完成从 Static Mesh 导入、几何变换、布尔运算、合并、采样到最终导出为 Static Mesh 资产的完整流程。

**关键设计理念：**

- **Data Steal 优化**：所有 Dynamic Mesh 节点默认不可缓存（`IsCacheable = false`），以启用"数据窃取"机制——当输入数据未被多个下游节点使用时，直接转移所有权而非复制，大幅提升性能
- **通过 CVar `pcg.DynamamicMesh.AllowDataSteal` 可控制此行为**，`pcg.DynamamicMesh.DataStealVerbose` 可追踪窃取事件

## 使用场景

- 你需要在 PCG 流程中对网格进行布尔运算（交集/并集/差集）→ 用 **Boolean Operation** 节点
- 你想把 Static Mesh 转为 Dynamic Mesh 在 PCG 图中处理 → 用 **Static Mesh To Dynamic Mesh** 节点
- 你想从网格表面采样点用于散布 → 用 **Mesh Sampler** 节点
- 你想把 PCG 生成的样条线转换为网格 → 用 **Spline To Mesh** 节点
- 你想在多个点位置上复制网格并合并 → 用 **Append Meshes From Points** 节点
- 你想把处理完的 Dynamic Mesh 保存为 Static Mesh 资产 → 用 **Save Dynamic Mesh To Asset** 节点
- 你想用蓝图自定义 Dynamic Mesh 处理逻辑 → 继承 **Geometry Blueprint Element**
- 你想从 Primitive/Volume 提取截面轮廓 → 用 **Primitive Cross-Section** 节点

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Static Mesh To Dynamic Mesh` | 将 Static Mesh 转换为 Dynamic Mesh Data，支持 LOD 和材质提取 | `UPCGStaticMeshToDynamicMeshSettings` |
| `Create Empty Dynamic Mesh` | 创建空的 Dynamic Mesh Data，作为构建流程的起点 | `UPCGCreateEmptyDynamicMeshSettings` |
| `Boolean Operation` | 对两个 Dynamic Mesh 执行布尔运算（交/并/差），支持多种配对模式 | `UPCGBooleanOperationSettings` |
| `Merge Dynamic Meshes` | 将多个 Dynamic Mesh 按顺序追加合并为一个 | `UPCGMergeDynamicMeshesSettings` |
| `Dynamic Mesh Transform` | 对 Dynamic Mesh 应用 Transform（位移/旋转/缩放） | `UPCGDynamicMeshTransformSettings` |
| `Spline To Mesh` | 将闭合样条线三角化为网格，支持挤出和偏移 | `UPCGSplineToMeshSettings` |
| `Append Meshes From Points` | 在每个点的 Transform 位置追加网格副本，支持从 Static Mesh 属性读取不同网格 | `UPCGAppendMeshesFromPointsSettings` |
| `Mesh Sampler` | 从网格表面采样 PCG 点，支持每三角形/每顶点/Poisson 采样 | `UPCGMeshSamplerSettings` |
| `Get Dynamic Mesh Data` | 从场景中的 Actor/Component 提取 Dynamic Mesh Data | `UPCGGetDynamicMeshDataSettings` |
| `Spawn Dynamic Mesh` | 为每个 Dynamic Mesh Data 生成 Dynamic Mesh Component | `UPCGSpawnDynamicMeshSettings` |
| `Save Dynamic Mesh To Asset` | 将 Dynamic Mesh Data 保存为 Static Mesh 资产（仅编辑器） | `UPCGSaveDynamicMeshToAssetSettings` |
| `Primitive Cross-Section` | 从 Primitive/Volume/Dynamic Mesh 提取样条截面 | `UPCGPrimitiveCrossSectionSettings` |
| `Geometry Blueprint Element` | 蓝图可继承基类，用 `ProcessDynamicMesh` 事件自定义网格处理 | `UPCGGeometryBlueprintElement` |

### 使用示例（蓝图描述）

**示例 1：网格布尔运算**

1. 创建 **Static Mesh To Dynamic Mesh** 节点 A，指向一个立方体 Static Mesh
2. 创建 **Static Mesh To Dynamic Mesh** 节点 B，指向一个球体 Static Mesh
3. 创建 **Boolean Operation** 节点，设置 `BooleanOperation = Difference`
4. 将 A 连接到 `InA` 引脚，B 连接到 `InB` 引脚
5. 将输出连接到 **Spawn Dynamic Mesh** 节点查看结果

**示例 2：从网格采样点**

1. 创建 **Mesh Sampler** 节点
2. 设置 `StaticMesh` 为你要采样的网格
3. 选择 `SamplingMethod`（如 `PoissonSampling`）
4. 可选：启用 `bUseColorChannelAsDensity` 将顶点色映射到密度
5. 输出引脚连接到下游的散布节点

**示例 3：蓝图自定义网格处理**

1. 创建蓝图类，父类选择 `PCGGeometryBlueprintElement`
2. 在蓝图中 override `ProcessDynamicMesh` 事件
3. 事件提供 `InDynMesh`（`UDynamicMesh*`）可直接用 Geometry Script 蓝图节点操作
4. 通过 `OutTags` 输出自定义标签
5. 在 PCG 图中使用此蓝图节点

## C++ 用法

### 头文件引入

```cpp
#include "Elements/PCGDynamicMeshBaseElement.h"
#include "Data/PCGDynamicMeshData.h"
#include "Helpers/PCGGeometryHelpers.h"
```

### 基本用法

从源码中提取的典型用法——创建 Dynamic Mesh Data 并执行布尔运算：

```cpp
// 来源: Elements/PCGBooleanOperation.cpp
// 获取输入的 Dynamic Mesh Data
const UPCGDynamicMeshData* InputMeshA = Cast<const UPCGDynamicMeshData>(InputA.Data);
const UPCGDynamicMeshData* InputMeshB = Cast<const UPCGDynamicMeshData>(InputB.Data);

// 使用 CopyOrSteal 优化：如果数据未被多处引用则直接转移所有权，否则复制
UPCGDynamicMeshData* OutputMeshData = IPCGDynamicMeshBaseElement::CopyOrSteal(InputA, Context);

// 执行布尔运算（使用 Geometry Script API）
UGeometryScriptLibrary_MeshBooleanFunctions::ApplyMeshBoolean(
    OutputMeshData->GetMutableDynamicMesh(),
    FTransform::Identity,
    const_cast<UDynamicMesh*>(InputMeshB->GetDynamicMesh()),
    FTransform::Identity,
    EGeometryScriptBooleanOperation::Intersection,
    FGeometryScriptMeshBooleanOptions());
```

### 进阶用法

**从多种 PCG 数据类型转换为 Dynamic Mesh**：

```cpp
// 来源: Helpers/PCGGeometryHelpers.cpp
// ConvertDataToDynMeshes 支持多种输入类型:
// - UPCGPrimitiveData: 通过 CopyMeshFromComponent 提取
// - UPCGVolumeData: 从 Brush 或 Box bounds 生成
// - UPCGCollisionShapeData: 从 Box/Sphere/Capsule 碰撞体生成
// - UPCGCollisionWrapperData: 从碰撞包装数据生成
// - UPCGDynamicMeshData: 直接使用

TArray<UDynamicMesh*> DynamicMeshes;
UGeometryScriptDebug* Debug = FPCGContext::NewObject_AnyThread<UGeometryScriptDebug>(Context);
PCGGeometryHelpers::ConvertDataToDynMeshes(TaggedData.Data, Context, DynamicMeshes, 
    /*bMergeMeshes=*/false, Debug);
```

**材质重映射**：

```cpp
// 来源: Helpers/PCGGeometryHelpers.cpp
// 合并网格时自动处理材质 ID 重映射
PCGGeometryHelpers::RemapMaterials(
    OutputMesh->GetMutableDynamicMesh()->GetMeshRef(),
    InputMaterials,    // 源材质数组
    OutputMaterials,   // 目标材质数组（可变，新材质会被追加）
    &MeshIndexMappings // 可选：只对部分三角形重映射
);
```

## Demo 示例

### 最小 Dynamic Mesh 处理蓝图元素

**MyGeometryProcessor.h**
```cpp
#pragma once
#include "Elements/PCGGeometryBlueprintElement.h"
#include "MyGeometryProcessor.generated.h"

// 直接使用 UPCGGeometryBlueprintElement 的蓝图子类即可
// C++ 中如果需要自定义，可 override Execute_Implementation
UCLASS()
class UMyGeometryProcessor : public UPCGGeometryBlueprintElement
{
    GENERATED_BODY()
public:
    // ProcessDynamicMesh 在蓝图中 override 即可
    // C++ 中可直接 override Execute_Implementation 做更复杂的操作
};
```

**Build.cs 依赖**
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "PCG",
    "GeometryScriptingCore",
    "PCGGeometryScriptInterop"
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心功能 |
| `GeometryScriptingCore` | Geometry Script 核心 API（Dynamic Mesh、布尔运算、采样等） |
| `Projects` | 插件/模块管理 |
| `RenderCore` | 渲染核心（材质相关） |
| `RHI` | 渲染硬件接口 |
| `PCG` | PCG 框架核心 |
| `ModelingOperators` | 建模操作符（样条三角化等） |
| `GeometryCore` | 几何核心（私有依赖） |
| `GeometryFramework` | 几何框架（DynamicMeshComponent） |
| `ModelingComponents` | 建模组件（私有依赖） |

编辑器额外依赖：
| 模块 | 用途 |
|---|---|
| `AdvancedPreviewScene` | 高级预览场景（编辑器） |
| `UnrealEd` | 编辑器工具 |
| `PCGEditor` | PCG 编辑器集成 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-09-29 | `0ea53ac` | **[PCG] Fix Cross Section issue**: 修复截面高度比较逻辑反转的问题 |
| 2025-09-23 | `f9639c2` | **[PCG] Fix RemapMaterial**: 修复目标网格没有材质时材质重映射失败的问题 |
| 2025-09-23 | `531814b` | **[PCG] Fix Grammar nodes**: 修复 Grammar 节点在数据域下不工作的问题（涉及此插件的基础设施） |

### 维护评价

- **创建时间**：2023-03-14（最初在 Experimental 目录下）
- **最近更新**：2025-09-29，最近 6 个月内有实质性 bug 修复
- **维护状态**：✅ 活跃维护 — 持续有 bug 修复和功能改进
- **实验性警告**：`.uplugin` 中 `IsBetaVersion=true`，`EnabledByDefault=false`，需要手动启用
- **推荐程度**：如果你需要在 PCG 流程中处理几何网格，这是**必装插件**。虽然标记为 Beta，但代码质量高，由 Epic 官方维护，功能完整且稳定
- **注意**：`Save Dynamic Mesh To Asset` 仅在编辑器构建中可用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/PCGInterops/PCGGeometryScriptInterop)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)
- [PCG 插件源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/PCG)
- [Geometry Scripting 源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/GeometryScripting)
