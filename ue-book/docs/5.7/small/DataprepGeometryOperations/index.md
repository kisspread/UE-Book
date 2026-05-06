# Dataprep Geometry Operations

> Experimental geometry processing operations usable in the Dataprep Editor.

| 属性 | 值 |
|---|---|
| 中文名 | 数据准备几何操作 |
| 分类 | Dataprep |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DataprepGeometryOperations` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-04-24 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Enterprise/DataprepGeometryOperations) | |

## 用途

该插件为 Dataprep 编辑器添加了一组实验性的几何处理操作，包括重新网格化 (Remesh)、烘焙变换 (Bake Transform) 以及基于外包的过滤器/选择转换 (Jacketing Filter / Select in Volume)。它扩展了 Dataprep 在自动化预处理管线中的能力，允许用户在导入阶段直接对网格执行简化、变换修正和可见性剔除等操作，而无需切换到其他工具。

## 使用场景

- 你需要在 Dataprep 资产导入管线中对大量静态网格进行质量优化（如减少三角形数量） → 使用 Remesh 操作。
- 导入的模型坐标变换分散在各组件上，需要统一应用变换（烘焙变换） → 使用 Bake Transform 操作。
- 通过距离场快速判断哪些网格被其他网格遮挡，用于剔除或选择 → 使用 Jacketing 过滤或“Select In Volume”转换。
- 在场景级别对静态网格 Actor 进行遮挡剔除（隐藏/标记/删除） → 使用 Jacketing 过程（C++ 内调用 `FJacketingProcess::ApplyJacketingOnMeshActors`）。

## 蓝图用法

本插件所有类均用 `NotBlueprintable` 标记，且操作和过滤器没有暴露为蓝图可调用节点。所有功能仅在 Dataprep 资产管理器（Asset）的蓝图中通过“操作”和“过滤器”节点使用（它们是 C++ 类，但可在 Dataprep 蓝图资产中配置）。

### 核心节点

| 节点（显示名称） | 说明 | 对应 C++ 类 |
|---|---|---|
| `Remesh` | 对输入网格执行重新网格化，支持目标三角面数、平滑强度、属性丢弃等参数 | `UDataprepRemeshOperation` |
| `Bake Transform` | 烘焙所选对象的变换（应用于网格顶点并重置变换） | `UDataprepBakeTransformOperation` |
| `Jacketing` | 过滤器，基于距离场精度和合并距离，筛选被遮挡的对象 | `UDataprepJacketingFilter` |
| `Select In Volume` | 选择转换，根据重叠检测返回位于指定体积内的 Actor（可选仅完全包含或包含+重叠） | `UDataprepOverlappingActorsSelectionTransform` |

### 使用示例（蓝图描述）

在 Dataprep 资产编辑器中：
1. 添加一个 **Remesh** 操作，设置目标三角面数（如 1000）和光滑强度（0.25）。该操作会在用户定义的输入过滤器之后执行。
2. 如果需要烘焙变换，添加 **Bake Transform** 操作（无需额外参数）。
3. 若要过滤被遮挡的网格，添加 **Jacketing** 过滤器并调整 `VoxelPrecision`（体素精度）和 `GapMaxDiameter`（合并间隙）。该过滤器会返回未被遮挡的对象。
4. 使用 **Select In Volume** 转换从当前选择中提取与特定 Actor 集合重叠的 Actor。

所有参数均可通过 Dataprep 资产编辑器中的属性面板直接调节，无需 Blueprint 节点。

## C++ 用法

### 头文件引入

```cpp
#include "DataprepGeometryOperations.h"          // 包含所有操作类
#include "DataprepGeometryFilters.h"            // 包含 Jacketing 过滤器
#include "DataprepGeometrySelectionTransforms.h"// 包含 Select In Volume 转换
#include "JacketingProcess.h"                   // 直接调用 Jacketing 核心算法
```

### 基本用法

#### 1. Jacketing 过滤器

```cpp
// 创建一个 Jacketing 过滤器实例
UDataprepJacketingFilter* JacketingFilter = NewObject<UDataprepJacketingFilter>();
JacketingFilter->SetAccuracy(3.0f);       // 体素精度，单位 cm
JacketingFilter->SetMergeDistance(4.0f);  // 合并间隙，单位 cm

// 对一组对象进行过滤
TArray<UObject*> InputObjects = ...;
TArray<UObject*> FilteredObjects = JacketingFilter->FilterObjects(InputObjects);
```

#### 2. 在代码中直接使用 Jacketing 过程（不依赖 Dataprep 框架）

```cpp
#include "JacketingProcess.h"

void ApplyJacketing(AActor* TargetActor, TArray<AActor*>& OutOccludedActors)
{
    TArray<AActor*> Actors = { TargetActor };
    FJacketingOptions Options(/*Accuracy*/ 1.0f, /*MergeDistance*/ 0.0f, EJacketingTarget::Level);
    FJacketingProcess::ApplyJacketingOnMeshActors(Actors, &Options, OutOccludedActors, /*bSilent*/ false);
}
```

#### 3. 查找重叠 Actor

```cpp
TArray<AActor*> ActorsToTest;
TArray<AActor*> ActorsToTestAgainst;
TArray<AActor*> OverlappingActors;

FJacketingOptions Options(3.0f, 0.0f, EJacketingTarget::Level);
FJacketingProcess::FindOverlappingActors(ActorsToTest, ActorsToTestAgainst, &Options, OverlappingActors, false);
```

### 进阶用法

通过 Dataprep 底层 API 组合多个操作：

```cpp
// 创建 Dataprep 资产并添加操作
UDataprepAssetProducers* Producers = ...;
UDataprepOperation* RemeshOp = NewObject<UDataprepRemeshOperation>();
RemeshOp->TargetTriangleCount = 500;
RemeshOp->RemeshType = ERemeshType::Standard;
Producers->AddOperation(RemeshOp);

UDataprepOperation* BakeTransformOp = NewObject<UDataprepBakeTransformOperation>();
Producers->AddOperation(BakeTransformOp);
```

## Demo 示例

以下是一个完整的最小 C++ 示例，展示如何在插件启动时对场景中的静态网格 Actor 执行 Jacketing（遮挡剔除）。该示例假设您在一个编辑器模块中（例如自定义的 Dataprep 操作或蓝图函数库）。

### JacketingDemo.h

```cpp
#pragma once
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "JacketingDemo.generated.h"

UCLASS()
class UJacketingDemo : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category = "DataprepDemo")
    static void ApplyJacketingToSelectedActors(float Accuracy, float MergeDistance);
};
```

### JacketingDemo.cpp

```cpp
#include "JacketingDemo.h"
#include "JacketingProcess.h"
#include "EngineUtils.h"
#include "Engine/World.h"
#include "Engine/StaticMeshActor.h"

void UJacketingDemo::ApplyJacketingToSelectedActors(float Accuracy, float MergeDistance)
{
    UWorld* World = ...; // 获取当前世界（可通过 GEditor->GetEditorWorldContext().World()）
    if (!World) return;

    TArray<AActor*> AllMeshActors;
    for (TActorIterator<AStaticMeshActor> It(World); It; ++It)
    {
        AllMeshActors.Add(*It);
    }

    FJacketingOptions Options(Accuracy, MergeDistance, EJacketingTarget::Level);
    TArray<AActor*> OccludedActors;
    FJacketingProcess::ApplyJacketingOnMeshActors(AllMeshActors, &Options, OccludedActors, /*bSilent*/ false);

    // 对遮挡的 Actor 执行操作（例如隐藏）
    for (AActor* Actor : OccludedActors)
    {
        Actor->SetActorHiddenInGame(true);
    }
}
```

**注意**：实际使用时需处理模块依赖、头文件包含和世界指针获取方式。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DataprepCore` | Dataprep 框架核心（操作、过滤器基础类） |
| `GeometryProcessingInterfaces` | 几何处理接口（Jacketing 算法依赖） |
| `DynamicMesh` | 动态网格数据结构（Remesh 操作依赖） |
| `ModelingOperators` | 建模操作符（Remesh、Simplify 等） |
| `MeshConversion` | 网格格式转换（用于烘焙变换时的网格更新） |

**无特殊依赖（仅标准 Core/Engine/Slate 等）**中不属于上述列表的均为常见基础模块。

## 维护状态

### 近期更新

```
- 2024-12-20 d0cf4301 ModelingTools: Promote experimental modeling tools to beta.
- 2024-12-19 0b7db795 [Backout] - CL38936187
- 2024-12-19 4581f566 ModelingTools: Promote experimental modeling tools to beta.
- 2024-04-24 6139b100 Build fix
- 2024-04-24 02a0620a MergeActor - 1st pass cleaning up include files in order to avoid rebuilding the whole engine when e
```

### 维护评价

该插件创建于 2024 年 4 月，目前仍标记为实验性 (`IsBetaVersion=true`)。最近更新（2024 年 12 月）与 ModelingTools 提升到 Beta 相关，说明该插件在这些改动中保持了同步，但自身功能并未有实质性更新。截至 2025 年 10 月，已有近 10 个月无专属功能提交，建议使用前评估其稳定性和未来支持力度。对于新项目，推荐仅作尝试性使用，避免依赖尚未稳定的 API。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Enterprise/DataprepGeometryOperations)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/dataprep-editor/) (Dataprep 通用文档)
- 测试用例（无专用测试目录）