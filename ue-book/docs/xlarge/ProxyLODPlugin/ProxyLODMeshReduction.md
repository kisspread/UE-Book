# Proxy LOD Plugin (Experimental)

> A plugin to generate Proxy LOD systems.

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ProxyLODMeshReduction` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2017-12-13 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/ProxyLODPlugin) | |

## 用途

ProxyLODPlugin 是一个用于生成代理LOD（Level of Detail）系统的编辑器插件。其核心功能是通过**体素化**和**CSG（构造实体几何）** 操作，将复杂的静态网格体简化为低面数的代理网格。这个代理网格保留了原始网格的大致形状和体积，但几何复杂度大大降低。

该插件主要解决**大型开放世界游戏**中，为大量静态网格体（如建筑、岩石、植被）生成**HLOD（Hierarchical Level of Detail）** 代理网格的问题。通过使用代理网格替代远处的高精度模型，可以显著减少渲染开销，提升游戏性能。它通常与引擎的 HLOD 系统集成使用。

## 使用场景

- 你在开发一个大型开放世界游戏，场景中有成千上万个静态网格体。
- 你需要为这些网格体生成简化的代理版本，用于远处的 HLOD 渲染，以优化性能。
- 你需要一个工具，能够自动处理多个网格体的合并、体素化和简化流程。

## 蓝图用法

该插件主要通过编辑器UI和C++接口使用，**没有直接暴露给蓝图的函数**。其核心功能（如 `IProxyLODVolume` 和 `IVoxelBasedCSG`）是C++接口，用于在编辑器工具或自定义构建流程中调用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateSDFVolumeFromMeshArray` | 从一组网格体数据创建SDF（有符号距离场）体积 | `IProxyLODVolume` |
| `CreateCSGTool` | 创建一个基于体素的CSG工具实例 | `IVoxelBasedCSG` |
| `ParameterizeMeshDescription` | 为网格体重新生成UV坐标 | `IProxyLODParameterization` |

### 使用示例（蓝图描述）

由于该插件主要面向C++和编辑器扩展，蓝图中的典型用法是通过**编辑器工具蓝图**或**编辑器Utility Widget**来调用底层的C++函数。例如，你可以创建一个编辑器工具，通过蓝图节点调用 `IProxyLODVolume::CreateSDFVolumeFromMeshArray` 来处理选中的Actor，然后使用 `ConvertToRawMesh` 获取简化后的网格数据。

## C++ 用法

### 头文件引入

```cpp
#include "IProxyLODPlugin.h"
#include "ProxyLODVolume.h"
#include "ProxyLODParameterization.h"
```

### 基本用法

以下示例展示了如何使用 `IProxyLODVolume` 接口从一组网格体创建SDF体积并提取简化网格。
（来源：基于 `IProxyLODVolume` 接口定义推断）

```cpp
#include "IProxyLODPlugin.h"
#include "ProxyLODVolume.h"
#include "MeshDescription.h"

void GenerateProxyLOD(const TArray<FMeshMergeData>& InputMeshes)
{
    // 1. 创建SDF体积
    float VoxelStep = 1.0f; // 体素大小，影响精度和性能
    TUniquePtr<IProxyLODVolume> SDFVolume = IProxyLODVolume::CreateSDFVolumeFromMeshArray(InputMeshes, VoxelStep);

    if (SDFVolume.IsValid())
    {
        // 2. 可选：闭合小间隙
        SDFVolume->CloseGaps(5.0f, 3); // 半径5单位，最多迭代3次

        // 3. 提取简化网格
        FMeshDescription ProxyMesh;
        SDFVolume->ConvertToRawMesh(ProxyMesh);

        // 现在 ProxyMesh 包含了简化的代理网格数据
        // 可以将其转换为 UStaticMesh 或用于其他用途
    }
}
```

### 进阶用法

结合 `IVoxelBasedCSG` 进行更复杂的网格操作，例如布尔运算。
（来源：基于 `IVoxelBasedCSG` 接口定义推断）

```cpp
#include "IProxyLODPlugin.h"
#include "ProxyLODVolume.h"
#include "MeshDescription.h"

void PerformCSGOperation(const FMeshDescription* MeshA, const FTransform& TransformA,
                         const FMeshDescription* MeshB, const FTransform& TransformB)
{
    // 1. 创建CSG工具
    float VoxelSize = 2.0f;
    TUniquePtr<IVoxelBasedCSG> CSGTool = IVoxelBasedCSG::CreateCSGTool(VoxelSize);

    if (CSGTool.IsValid())
    {
        // 2. 设置要操作的网格
        IVoxelBasedCSG::FPlacedMesh PlacedMeshA(MeshA, TransformA);
        IVoxelBasedCSG::FPlacedMesh PlacedMeshB(MeshB, TransformB);

        // 3. 执行CSG操作（例如：并集、交集、差集）
        // 具体操作函数需要查看完整接口，此处为示意
        // CSGTool->Union(PlacedMeshA, PlacedMeshB);
        // 或
        // CSGTool->Subtract(PlacedMeshA, PlacedMeshB);

        // 4. 获取结果网格
        // FMeshDescription ResultMesh = CSGTool->GetResultMesh();
    }
}
```

## Demo 示例

一个最小的示例，展示如何在编辑器工具中调用 ProxyLOD 功能。

**MyProxyLODTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyProxyLODTool.generated.h"

class IProxyLODVolume;

UCLASS()
class UMyProxyLODTool : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "ProxyLOD")
    static bool GenerateProxyMeshFromActors(const TArray<AActor*>& Actors, UStaticMesh*& OutProxyMesh);
};
```

**MyProxyLODTool.cpp**
```cpp
#include "MyProxyLODTool.h"
#include "IProxyLODPlugin.h"
#include "ProxyLODVolume.h"
#include "Engine/StaticMesh.h"
#include "MeshDescription.h"
#include "StaticMeshAttributes.h"
#include "MeshMergeData.h"

bool UMyProxyLODTool::GenerateProxyMeshFromActors(const TArray<AActor*>& Actors, UStaticMesh*& OutProxyMesh)
{
    // 1. 收集网格体数据
    TArray<FMeshMergeData> MeshDataArray;
    for (AActor* Actor : Actors)
    {
        // ... 从Actor的StaticMeshComponent收集顶点、索引、变换等数据到FMeshMergeData ...
        // 此处省略具体收集逻辑
    }

    if (MeshDataArray.Num() == 0)
    {
        return false;
    }

    // 2. 生成SDF体积并提取代理网格
    TUniquePtr<IProxyLODVolume> Volume = IProxyLODVolume::CreateSDFVolumeFromMeshArray(MeshDataArray, 1.0f);
    if (!Volume.IsValid())
    {
        return false;
    }

    FMeshDescription ProxyMeshDesc;
    Volume->ConvertToRawMesh(ProxyMeshDesc);

    // 3. 将FMeshDescription转换为UStaticMesh
    // 此处需要创建新的UStaticMesh资产并填充数据
    // OutProxyMesh = ...;
    // ... 转换逻辑 ...

    return true;
}
```

**YourModule.Build.cs** (依赖配置)
```csharp
using UnrealBuildTool;

public class YourModule : ModuleRules
{
    public YourModule(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[] {
            "Core",
            "CoreUObject",
            "Engine",
            "ProxyLODMeshReduction" // 关键依赖
        });
    }
}
```

## 模块依赖

从 `ProxyLODMeshReduction.Build.cs` 分析，该插件依赖以下**独特**模块：

| 模块 | 用途 |
|---|---|
| `DirectXMesh` | 第三方库，用于网格处理（如计算邻接信息、法线等） |
| `UVAtlas` | 第三方库，用于UV图集生成和参数化 |
| `MeshUtilities` | 引擎模块，提供网格合并和简化相关的接口 |

## 维护状态

### 近期更新

```
22624953496b | 2024-08-21 | Workaround to prevent crash in UVAtlas
8396b185774c | 2024-08-20 | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 2/n
5754601389ed | 2024-08-19 | World Building - HLOD Generation: Changed some warnings to logs * List input components when no HLODs are generated #rb a.bialokozowicz
```

**解读**：
1.  `22624953496b`: 修复了UVAtlas库可能导致的崩溃问题，属于稳定性修复。
2.  `8396b185774c`: 代码维护，更新头文件以确保DLL导出符号正确，属于编译兼容性修复。
3.  `5754601389ed`: 与HLOD生成功能相关，将部分警告改为日志，并在没有生成HLOD时列出输入组件，属于调试和日志改进。

### 维护评价

- **创建时间**：2017年，是一个相对成熟的插件。
- **最近更新**：最近的提交（2024年8月）均为**维护性更新**（修复崩溃、编译问题、日志改进），没有新的功能特性添加。
- **活跃度**：维护不活跃，但仍有关键问题的修复。
- **状态**：插件标记为 **实验性 (IsBetaVersion=true)** 且 **默认未启用 (EnabledByDefault=false)**，表明它可能未达到生产就绪状态，或API可能发生变化。
- **推荐**：**谨慎使用**。适用于需要快速原型验证或对HLOD代理生成有特定需求的项目。不建议在追求稳定性的核心生产管线中依赖此插件。使用前应充分测试，并准备好应对潜在的API变更或限制。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/ProxyLODPlugin)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/ProxyLODPlugin/Tests) (如果存在)