# PCG Geometry Script Interop

> Extra plugin for Procedural Content Generation Framework interacting with Geometry Scripts.

| 属性 | 值 |
|---|---|
| 中文名 | PCG 几何脚本互操作 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PCGGeometryScriptInterop` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-13 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCGInterops/PCGGeometryScriptInterop) | |

## 用途

PCGGeometryScriptInterop 是 PCG 框架与 Geometry Script 之间的桥梁插件。它解决的核心问题是：**在 PCG 程序化内容生成图中，如何对几何体（网格）进行程序化操作**。

没有这个插件，PCG 只能操作点云数据，无法直接处理网格几何体。有了它，你可以在 PCG 图中：
- 从静态网格/骨骼网格表面采样点（用于植被分布、装饰物撒点等）
- 对网格执行布尔运算（交集、并集、差集）
- 将样条线转换为网格（生成道路、墙体等线性几何体）
- 从 Actor 组件提取动态网格数据
- 在 PCG 图中合并、变换、保存动态网格

## 使用场景

- 你需要在复杂地形上基于网格表面分布植被或装饰物 → 用 Mesh Sampler 节点
- 你要在 PCG 流程中对网格做交集/差集切割 → 用 Boolean Operation 节点
- 你需要从样条线程序化生成墙体、栏杆等网格 → 用 Spline To Mesh 节点
- 你想从场景中已有的 Actor 提取网格数据进入 PCG 流程 → 用 Get Dynamic Mesh Data 节点
- 你要将 PCG 生成的动态网格保存为 Static Mesh 资产 → 用 Save Dynamic Mesh To Asset 节点
- 你需要从图元提取横截面样条线（如塔楼层级轮廓）→ 用 Primitive Cross-Section 节点
- 你想基于 PCG 点数据放置网格组合 → 用 Append Meshes From Points 节点

## 蓝图用法

本插件的蓝图接口主要通过 **PCG 节点** 在 PCG 图中使用，而非直接调用函数。以下为核心蓝图可用 API：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ProcessDynamicMesh` | 蓝图可实现事件，处理单个动态网格（输入→输出简化版） | `UPCGGeometryBlueprintElement` |
| `CopyOrStealInputData` | 高效获取输入动态网格数据（窃取或复制） | `UPCGGeometryBlueprintElement` |

### PCG 图中的节点（Settings 类）

| 节点名称 | 功能 | 类 |
|---|---|---|
| Mesh Sampler | 在网格表面采样点（支持三角形中心、顶点、泊松采样） | `UPCGMeshSamplerSettings` |
| Mesh To Dynamic Mesh | 将静态/骨骼网格转换为动态网格数据 | `UPCGMeshToDynamicMeshSettings` |
| Spline To Mesh | 将样条线转换为网格（支持挤压、偏移） | `UPCGSplineToMeshSettings` |
| Boolean Operation | 对两个动态网格执行布尔运算 | `UPCGBooleanOperationSettings` |
| Primitive Cross-Section | 从图元提取横截面样条线 | `UPCGPrimitiveCrossSectionSettings` |
| Append Meshes From Points | 在点位置附加网格（支持单网格、属性网格、动态网格） | `UPCGAppendMeshesFromPointsSettings` |
| Merge Dynamic Meshes | 合并所有输入动态网格 | `UPCGMergeDynamicMeshesSettings` |
| Create Empty Dynamic Mesh | 创建空动态网格 | `UPCGCreateEmptyDynamicMeshSettings` |
| Dynamic Mesh Transform | 对动态网格应用变换 | `UPCGDynamicMeshTransformSettings` |
| Get Materials Dynamic Mesh | 获取动态网格上的材质数组 | `UPCGGetMaterialsDynamicMeshSettings` |
| Set Materials Dynamic Mesh | 替换动态网格上的材质数组 | `UPCGSetMaterialsDynamicMeshSettings` |
| Get Dynamic Mesh Data | 从场景 Actor/组件提取动态网格数据 | `UPCGGetDynamicMeshDataSettings` |
| Save Dynamic Mesh To Asset | 将动态网格保存为静态网格资产 | `UPCGSaveDynamicMeshToAssetSettings` |
| Spawn Dynamic Mesh | 为每个输入动态网格生成组件 | `UPCGSpawnDynamicMeshSettings` |

### 使用示例（蓝图描述）

**自定义几何体处理节点**：

1. 创建一个新蓝图类，父类选择 `PCGGeometryBlueprintElement`
2. 在蓝图中重写 `ProcessDynamicMesh` 事件
3. 该事件会自动对每个输入动态网格调用一次，你可以在此添加自定义 Geometry Script 操作
4. 输出结果自动收集，无需手动管理数据流

**高效数据处理模式**：

在 `ProcessDynamicMesh` 中，如果需要原地修改网格：
1. 调用 `CopyOrStealInputData` 获取网格数据（当数据未被其他节点使用时会窃取，避免复制）
2. 直接在返回的 `UDynamicMesh` 上执行 Geometry Script 操作
3. 修改后的网格自动输出

## C++ 用法

### 头文件引入

```cpp
#include "Elements/PCGGeometryBlueprintElement.h"
#include "Elements/PCGMeshSampler.h"
#include "Elements/PCGBooleanOperation.h"
```

### 基本用法

**创建自定义几何体处理节点**：

来自 `PCGGeometryBlueprintElement.h`，这是最常用的基类：

```cpp
// 自定义 PCG 蓝图元素，继承自 UPCGGeometryBlueprintElement
// 只需重写 ProcessDynamicMesh 即可处理每个输入的动态网格
UCLASS()
class UMyGeometryProcessor : public UPCGGeometryBlueprintElement
{
    GENERATED_BODY()

public:
    // 蓝图可实现事件：处理单个动态网格
    // InDynMesh - 输入的动态网格，可以直接原地修改
    // OutTags - 可选输出标签，默认继承输入标签
    UFUNCTION(BlueprintImplementableEvent)
    void ProcessDynamicMesh(UDynamicMesh* InDynMesh, TArray<FString>& OutTags);
    
    // 使用 CopyOrStealInputData 高效获取数据
    UFUNCTION(BlueprintCallable)
    UPCGDynamicMeshData* CopyOrStealInputData(const FPCGTaggedData& InTaggedData) const;
};
```

### 进阶用法

**布尔运算模式配置**（来自 `PCGBooleanOperation.h`）：

```cpp
// 三种布尔运算模式
// EachAWithEachB:     A1↔B1, A2↔B2, ...（一一对应，输出 N 个）
// EachAWithEachBSequentially: A1↔B1→B2, A2↔B1→B2, ...（顺序累积，输出 N 个）
// EachAWithEveryB:    A1↔B1, A1↔B2, A2↔B1, A2↔B2, ...（笛卡尔积，输出 N×M 个）

EPCGBooleanOperationMode Mode = EPCGBooleanOperationMode::EachAWithEachB;
EGeometryScriptBooleanOperation Operation = EGeometryScriptBooleanOperation::Intersection;
```

**网格采样方法**（来自 `PCGMeshSampler.h`）：

```cpp
// 三种采样方法
// OnePointPerTriangle: 每个三角形中心采一个点
// OnePointPerVertex:   每个顶点一个点
// PoissonSampling:     泊松采样（可配置密度，计算开销较大）

EPCGMeshSamplingMethod SamplingMethod = EPCGMeshSamplingMethod::OnePointPerTriangle;

// 可选功能：
// - 将顶点颜色通道映射到密度值
// - 提取 UV 坐标到属性
// - 输出三角形 ID 和材质信息
// - 体素化预处理
// - LOD 选择
```

**从 Actor 提取动态网格数据**（来自 `PCGGetDynamicMeshData.h`）：

```cpp
// 两个静态辅助函数用于从场景提取数据
namespace PCGGetDynamicMeshData
{
    bool GetDynamicMeshDataFromActor(FPCGContext*, const FPCGGetDataFunctionRegistryParams&, 
                                      AActor*, FPCGGetDataFunctionRegistryOutput&);
    bool GetDynamicMeshDataFromComponent(FPCGContext*, const FPCGGetDataFunctionRegistryParams&, 
                                          UActorComponent*, FPCGGetDataFunctionRegistryOutput&);
}
```

**动态网格数据可视化辅助**（来自 `PCGGeometryHelpers.h`）：

```cpp
// 几何脚本调试信息转 PCG 日志
PCGGeometryHelpers::GeometryScriptDebugToPCGLog(Context, DebugObject);

// 材质重映射（用于合并网格时保持材质正确性）
PCGGeometryHelpers::RemapMaterials(DynamicMesh, FromMaterials, ToMaterials, OptionalMappings);

// 通用数据转动态网格
PCGGeometryHelpers::ConvertDataToDynMeshes(InData, Context, OutMeshes, bMergeMeshes);
```

## Demo 示例

### 自定义几何体处理节点

```cpp
// MyGeometryProcessor.h
#pragma once

#include "Elements/PCGGeometryBlueprintElement.h"
#include "MyGeometryProcessor.generated.h"

UCLASS(BlueprintType, Blueprintable)
class UMyGeometryProcessor : public UPCGGeometryBlueprintElement
{
    GENERATED_BODY()

public:
    UMyGeometryProcessor();
    
    // 处理每个输入的动态网格 - 应用简单变换
    UFUNCTION(BlueprintCallable, Category = "PCG|Execution")
    void ProcessDynamicMesh(UDynamicMesh* InDynMesh, TArray<FString>& OutTags);
};
```

```cpp
// MyGeometryProcessor.cpp
#include "MyGeometryProcessor.h"
#include "UDynamicMesh.h"
#include "Operations/MeshBooleanOp.h"

UMyGeometryProcessor::UMyGeometryProcessor()
{
    // 节点会在构造时自动配置输入/输出引脚为 DynamicMesh 类型
}

void UMyGeometryProcessor::ProcessDynamicMesh(UDynamicMesh* InDynMesh, TArray<FString>& OutTags)
{
    if (!InDynMesh || !InDynMesh->GetMesh())
    {
        return;
    }

    // 获取可编辑的 FDynamicMesh3 引用
    UE::Geometry::FDynamicMesh3& Mesh = *InDynMesh->GetMesh();
    
    // 在这里添加你的几何体处理逻辑
    // 例如：翻转法线、缩放、UV 操作等
    
    // 添加自定义标签
    OutTags.Add(TEXT("ProcessedByCustomNode"));
}
```

## 模块依赖

从插件元数据中的 `Plugins` 字段和源码依赖关系提取：

| 模块 | 用途 |
|---|---|
| `PCG` | PCG 程序化内容生成框架核心 |
| `GeometryScripting` | Geometry Script 几何脚本库，提供网格操作 API |
| `GeometryScriptingCore` | Geometry Script 核心类型（UDynamicMesh、FGeometryScriptMeshBooleanOptions 等） |
| `DynamicMesh` | 动态网格底层数据结构（FDynamicMesh3） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `11b0f25a` | [PCG] Better categorization for spline to mesh node | 优化 Spline To Mesh 节点的分类归属 |
| 2026-05-12 | `8ec40885` | [PCG] Fixed various typos in tooltips | 修复多个节点工具提示中的拼写错误 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新版 UE_LOGF 格式 |
| 2026-03-19 | `bea3db0c` | [PCG] Add default color override for Mesh Sampler + fix bounds in SubdivideSpline | Mesh Sampler 新增默认颜色覆盖选项，修复 SubdivideSpline 边界计算 |
| 2026-02-26 | `7e8d8259` | [PCG] Made spline to mesh polygon aware | 增强 Spline To Mesh 对多边形的感知能力 |

### 维护评价

- **活跃维护**：近 3 个月内有多次功能性更新（颜色覆盖、多边形感知、节点分类优化）
- **版本 0.2 + Beta 标记**：仍在积极开发中，API 可能有变动
- **EnabledByDefault=false**：需手动启用，属于实验性功能
- **创建时间**：2024-08-13，约 2 年前，属于较新的插件
- **更新频率**：稳定，每月 1-2 次提交
- **推荐使用**：可以使用，但需注意 API 可能在后续版本中变化。适合需要在 PCG 流程中处理几何体的工作流。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCGInterops/PCGGeometryScriptInterop)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)