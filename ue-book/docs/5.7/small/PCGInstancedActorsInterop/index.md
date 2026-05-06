# Procedural Content Generation Framework (PCG) Instanced Actors Interop

> Extra plugin for Procedural Content Generation Framework interacting with Instanced Actors plugin.

| 属性 | 值 |
|---|---|
| 中文名 | PCG实例Actor互操作 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PCGInstancedActorsInterop` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-23 |
| 年龄标签 | 🆕（约0年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PCGInterops/PCGInstancedActorsInterop) | |

## 用途

该插件是 PCG（程序化内容生成框架）与 Instanced Actors 插件之间的桥梁。它提供了一个新的 PCG 节点 **Spawn Instanced Actors**，允许开发者利用 Instanced Actors 插件的高效实例化系统来生成大量重复的 Actor 实例，而无需为每个实例创建独立的动态网格体（ISM/HISM）。这可以显著降低运行时开销，并简化场景中大量静态物体的管理（如树木、石块、道具等）。

Instanced Actors 插件本身需要 Actor 类在项目设置中正确注册，且目前**不支持运行时创建/删除实例**，也不支持预览/加载为预览工作流。该插件封装了这些限制，并提供统一的 PCG 管道集成。

## 使用场景

- 在开放世界中程序化生成大量植被、岩石、装饰物，并希望使用 Instanced Actors 模块来优化渲染和碰撞性能。
- 需要将 PCG 生成结果与 Instanced Actors 的数据驱动系统结合，利用属性选择器动态指定 Actor 类。
- 在关卡设计和编辑器工作流中，通过 PCG 图快速填充场景，并一键切换为 Instanced Actors 管理模式。

## 蓝图用法

该插件暴露一个 PCG 节点 `Spawn Instanced Actors`，可在 PCG 蓝图图中通过“Spawner”类别找到。其核心设置通过 `UPCGSpawnInstancedActorsSettings` 类的公开属性控制。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Spawn Instanced Actors` | 根据输入的 PCG 点数据生成 Instanced Actors 实例。支持通过属性选择器动态指定 Actor 类。 | `UPCGSpawnInstancedActorsSettings`（设置） + `FPCGSpawnInstancedActorsElement`（执行） |

### 节点属性（蓝图可读写）

| 属性 | 类型 | 说明 |
|---|---|---|
| `bSpawnByAttribute` | bool | 是否通过输入点上的属性来选择 Actor 类（代替固定 Actor 类） |
| `SpawnAttributeSelector` | FPCGAttributePropertyInputSelector | 指定用于决定 Actor 类的属性路径（仅在 `bSpawnByAttribute = true` 时生效） |
| `ActorClass` | TSubclassOf<AActor> | 固定 Actor 类（仅在 `bSpawnByAttribute = false` 时生效），须为已注册的 InstancedActor |
| `bMuteOnEmptyClass` | bool | 当 Actor 类为空时静默警告（用于部分点可能无合法类的情况） |

### 使用示例（蓝图描述）

1. **使用固定 Actor 类**：在 PCG 图中连接任意输出点数据（如“Surface Sampler”）到 `Spawn Instanced Actors` 节点。在节点详情面板中，设置 `ActorClass` 为已注册的 Instanced Actor（如 `BP_Tree_Instanced`），保持 `bSpawnByAttribute = false`。运行生成，每个点将创建一个该类的实例。

2. **根据属性动态选择类**：在输入点数据上预先准备一个字符串属性（如 `TreeType`），将 `bSpawnByAttribute` 设为 true，并在 `SpawnAttributeSelector` 中选择该属性。节点将根据每个点的 `TreeType` 值查找对应的 Actor 类（需确保属性值匹配项目设置中注册的 Instanced Actor 类名或路径）。若部分点没有合法类，可开启 `bMuteOnEmptyClass` 避免报错。

## C++ 用法

### 头文件引入

```cpp
#include "Elements/PCGSpawnInstancedActors.h"
#include "PCGInstancedActorsResource.h"
```

### 基本用法

以下示例演示如何通过 C++ 创建并配置 `UPCGSpawnInstancedActorsSettings`，然后通过 PCG 上下文执行。

```cpp
// 来源：Engine/Plugins/Experimental/PCGInterops/PCGInstancedActorsInterop/Source/PCGInstancedActorsInterop/Public/Elements/PCGSpawnInstancedActors.h

void SpawnInstancedActorsFromPoints(AActor* TargetActor, const TArray<FPCGPoint>& Points, TSubclassOf<AActor> ActorClass)
{
    // 1. 创建设置对象
    UPCGSpawnInstancedActorsSettings* Settings = NewObject<UPCGSpawnInstancedActorsSettings>();
    Settings->bSpawnByAttribute = false;
    Settings->ActorClass = ActorClass;

    // 2. 构造 PCG 执行上下文（简化示意）
    FPCGContext Context;
    Context.InputData.InitializeFromPoints(Points);
    Context.Settings = Settings;

    // 3. 执行节点
    FPCGSpawnInstancedActorsElement Element;
    Element.Execute(Context);

    // 4. 资源管理：生成的实例句柄存放在 UPCGInstancedActorsManagedResource::Handles 中
    // 可使用 Context.OutputData.GetResources<UPCGInstancedActorsManagedResource>() 获取并管理
}
```

### 进阶用法

当需要动态选择 Actor 类时，可以先在点数据上设置属性，再创建设置：

```cpp
// 来源：根据源码逻辑推导

// 设置每个点的属性值（例如类名）
TArray<FPCGPoint> Points;
FPCGAttributeAccessorKeysPoints PointKeys(Points);
for (int32 i = 0; i < Points.Num(); ++i)
{
    FString ClassName = (i % 2 == 0) ? TEXT("Tree_Oak") : TEXT("Tree_Pine");
    // 使用 FPCGMetadataAttribute 写入属性
    // ...
}

UPCGSpawnInstancedActorsSettings* Settings = NewObject<UPCGSpawnInstancedActorsSettings>();
Settings->bSpawnByAttribute = true;
Settings->SpawnAttributeSelector.SetAttributeName(TEXT("ActorClass"));

// 执行后将根据每个点的 "ActorClass" 属性值查找注册的 Instanced Actor 类
```

**资源管理**：`UPCGInstancedActorsManagedResource` 负责跟踪生成的实例句柄，支持清理、释放、移动到新 Actor 等操作。

## Demo 示例

以下是一个最小 C++ 示例，展示如何在编辑器上下文中使用该节点生成实例。

### MyPCGGenerator.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyPCGGenerator.generated.h"

UCLASS()
class AMyPCGGenerator : public AActor
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "PCG")
    void GenerateInstancedActors();

protected:
    UPROPERTY(EditAnywhere, Category = "PCG")
    TSubclassOf<AActor> TreeClass;

    UPROPERTY(EditAnywhere, Category = "PCG")
    int32 NumPoints = 100;
};
```

### MyPCGGenerator.cpp

```cpp
#include "MyPCGGenerator.h"
#include "Elements/PCGSpawnInstancedActors.h"
#include "PCGComponent.h"
#include "PCGContext.h"
#include "Data/PCGPointData.h"

void AMyPCGGenerator::GenerateInstancedActors()
{
    // 1. 创建简单的点数据
    UPCGPointData* PointData = NewObject<UPCGPointData>();
    TArray<FPCGPoint>& Points = PointData->GetMutablePoints();
    Points.Reserve(NumPoints);

    for (int32 i = 0; i < NumPoints; ++i)
    {
        FPCGPoint Point;
        Point.Transform.SetLocation(FVector(FMath::FRandRange(-500, 500), FMath::FRandRange(-500, 500), 0));
        Points.Add(Point);
    }

    // 2. 配置 Spawn Instanced Actors 设置
    UPCGSpawnInstancedActorsSettings* Settings = NewObject<UPCGSpawnInstancedActorsSettings>();
    Settings->bSpawnByAttribute = false;
    Settings->ActorClass = TreeClass;

    // 3. 构造输入数据
    FPCGDataCollection InputData;
    InputData.TaggedData.Emplace(PointData, FName(TEXT("Points")));

    // 4. 创建上下文并执行
    FPCGContext Context;
    Context.InputData = InputData;
    Context.Settings = Settings;
    Context.SourceComponent = nullptr; // 根据需要绑定 PCG 组件

    FPCGSpawnInstancedActorsElement Element;
    Element.Execute(Context);

    // 5. 输出结果（生成的 Actor 会自动添加到世界中，并可通过资源句柄查询）
    UE_LOG(LogTemp, Log, TEXT("SpawnInstancedActors executed successfully."));
}
```

**注意**：实际使用时需确保 `TreeClass` 已在项目设置中注册为 Instanced Actor，且插件 `InstancedActors` 和 `PCG` 已启用。

## 模块依赖

在模块的 `Build.cs` 中，依赖主要来自 `.uplugin` 的 `Plugins` 字段。以下为使用该插件时需引用的独特依赖：

| 模块 | 用途 |
|---|---|
| `PCG` | 核心程序化内容生成框架，提供基础数据类型、节点和管道 |
| `InstancedActors` | Instanced Actors 系统，负责 Actor 实例的管理和渲染 |

**无其他特殊依赖（标准 Core/Engine/Slate 等已省略）。**

## 维护状态

### 近期更新

- 2025-08-27 `74386d31` Fixup API macro usage（修正 API 宏使用）
- 2025-06-13 `d35afb72` [PCG] Adjusted the instanced actor resources so that they can't be released at runtime, which prevents...（调整实例化 Actor 资源，防止运行时释放）
- 2025-04-23 `7986632f` [PCG] Added missing undef LOCTEXT_NAMESPACE（添加缺失的 LOCTEXT_NAMESPACE 未定义）
- 2025-04-23 `0788fa69` [PCG] Added a PCG interop plugin for Instanced Actors. Has some limitations stemming from the Instan...（初始版本：添加 PCG 与 Instanced Actors 互操作插件，附带已知限制）

### 维护评价

- **创建时间**：2025-04-23，距今约 5 个月，属于**非常新的插件**。
- **近期更新**：最近一次为 2025-08-27 的修复，更新频率尚可（约每 2 个月一次），但主要是编译修复和资源管理调整，无新增功能。
- **状态**：该插件仍标记为**实验性（IsExperimentalVersion=true）**，且默认不启用，表明其 API 和功能可能不稳定，可能在未来版本中变更或移除。
- **已知限制**：通过 header 注释可知：Actor 类需提前注册，不支持运行时创建/移除实例，不支持预览/加载为预览工作流。
- **推荐度**：如果项目需要将 PCG 与 Instanced Actors 结合，且能接受实验性插件的风险，可以尝试使用。但建议仅在编辑器/设计阶段使用，运行时需谨慎测试。对于生产项目，等待其转为正式版可能更为稳妥。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PCGInterops/PCGInstancedActorsInterop)
- [官方文档（PCG 框架）](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PCGInterops/PCGInstancedActorsInterop/Tests)（可能有，但当前目录未包含测试文件）