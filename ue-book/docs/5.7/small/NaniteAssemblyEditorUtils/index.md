# Nanite Assembly Editor Utilities

> Experimental support for Nanite Assembly creation in blueprint.

| 属性 | 值 |
|---|---|
| 中文名 | 纳米网格装配编辑器工具 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具） |
| 模块 | `NaniteAssemblyEditorUtils` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NaniteAssemblyEditorUtils) | |

## 用途

Nanite Assembl 是 UE5 中一种特殊类型的 Nanite 网格，它可以将多个静态网格或骨骼网格的实例合并为一个单一的 Nanite 兼容网格。该插件提供了蓝图可调用的 API，允许在编辑器中以编程方式创建和编辑 Nanite Assembly 资产，无需手动合并网格或编写 C++ 工具。

主要解决以下问题：
- 将多个分散的静态网格实例（如道具、建筑部件）合并为一个高效的 Nanite 网格，减少 Draw Call 并提升渲染性能。
- 支持骨骼网格的装配，使角色装备或车辆附属物可以合并为单一骨骼网格，同时保留各部分独立绑定的能力。
- 提供材质合并选项，自动处理不同部件之间的材质插槽冲突。

## 使用场景

- 你正在构建一个由大量重复或相似物体组成的场景（如城市、森林）→ 使用 Nanite Assembly 将同类物体合并，利用 Nanite 的虚拟几何体技术大幅节约性能。
- 你需要将多个静态网格组合成一个可复用的资产（如一辆由底盘、车轮、驾驶舱组成的车辆）→ 使用 `UNaniteAssemblyStaticMeshBuilder` 添加部件并最终生成一个完整的静态网格。
- 你正在开发角色换装系统，希望将多个骨骼网格部件（盔甲、武器）合并为一个骨骼网格，同时保留骨骼动画绑定 → 使用 `UNaniteAssemblySkeletalMeshBuilder` 并指定每个部件的骨骼绑定信息。
- 你在关卡中放置了大量组件实例，希望一键将其转换为 Nanite Assembly 资产 → 使用 `AddAssemblyPartsFromComponent` 函数直接从组件中提取数据。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BeginNewStaticMeshAssemblyBuild` | 创建一个新的静态网格 Nanite Assembly 构建器，指定目标目录和资产名称 | `UNaniteAssemblyStaticMeshBuilder` |
| `BeginEditStaticMeshAssemblyBuild` | 打开一个已有的静态网格进行编辑（如果它原本就是 Nanite Assembly 则覆盖部件） | `UNaniteAssemblyStaticMeshBuilder` |
| `AddAssemblyPart` | 向装配中添加一个静态网格部件，指定本地变换和材质合并选项 | `UNaniteAssemblyStaticMeshBuilder` |
| `AddAssemblyParts` | 批量添加多个静态网格部件（每个带独立变换） | `UNaniteAssemblyStaticMeshBuilder` |
| `AddAssemblyPartsFromComponent` | 从场景中的静态网格组件提取所有实例（包括子组件）并添加到装配中 | `UNaniteAssemblyStaticMeshBuilder` |
| `FinishAssemblyBuild` | 完成构建，输出最终生成的静态网格资产 | `UNaniteAssemblyStaticMeshBuilder` |
| `BeginNewSkeletalMeshAssemblyBuild` | 创建一个新的骨骼网格 Nanite Assembly 构建器，需要提供基础骨骼网格（用于骨架复制） | `UNaniteAssemblySkeletalMeshBuilder` |
| `BeginEditSkeletalMeshAssemblyBuild` | 打开一个已有的骨骼网格进行编辑（如果它原本就是 Nanite Assembly 则覆盖部件） | `UNaniteAssemblySkeletalMeshBuilder` |
| `AddAssemblyPart` | 向装配中添加一个骨骼网格部件，指定单个骨骼绑定和材质合并选项 | `UNaniteAssemblySkeletalMeshBuilder` |
| `AddAssemblyParts` | 批量添加多个骨骼网格部件，每个带独立绑定数组 | `UNaniteAssemblySkeletalMeshBuilder` |
| `CreateBindingByBoneName` | 通过骨骼名称创建部件绑定，并可选设置相对变换（适用于单骨骼根约束） | `UNaniteAssemblySkeletalMeshBuilder` |
| `FinishAssemblyBuild` | 完成构建，输出最终生成的骨骼网格资产 | `UNaniteAssemblySkeletalMeshBuilder` |

### 使用示例（蓝图描述）

**静态网格 Assembly 示例：**

1. 使用 `BeginNewStaticMeshAssemblyBuild`，填入目标目录（如 `/Game/MyAssemblies/`）和资产名称（如 `MyBuilding_Assembly`）。
2. 调用 `AddAssemblyPart`：输入要合并的静态网格（如 `SM_Wall`），设置为本地变换 `(X=0, Y=0, Z=0)`，材质合并选项保持默认。
3. 重复调用 `AddAssemblyPart` 添加其他部件（如 `SM_Door`，变换 `(X=200, Y=0, Z=0)`）。
4. 最后调用 `FinishAssemblyBuild`，输出新生成的静态网格。将其放置到关卡中即可作为一个 Nanite 网格使用。

**骨骼网格 Assembly 示例：**

1. 准备一个基础骨骼网格（如 `SK_Mannequin`）作为骨架模板。
2. 使用 `BeginNewSkeletalMeshAssemblyBuild`，传入参数（目标目录/名称）和基础网格。
3. 使用 `CreateBindingByBoneName` 为每个部件创建绑定。例如，为 `SK_Armor` 创建绑定，骨骼名称为 `Spine`，变换 `(X=0, Y=0, Z=10)`，输出绑定结构体。
4. 使用 `AddAssemblyPart` 将该部件和绑定添加到构建器。
5. 重复步骤 3-4 添加其他部件（如 `SK_Helmet` 绑定到 `Head` 骨骼）。
6. 调用 `FinishAssemblyBuild`，输出最终骨骼网格。该网格将包含所有合并的部件，且每个部件跟随其绑定的骨骼运动。

## C++ 用法

### 头文件引入

```cpp
#include "NaniteAssemblyStaticMeshBuilder.h"
#include "NaniteAssemblySkeletalMeshBuilder.h"
```

### 基本用法

以下示例演示如何在编辑器模块中通过 C++ 创建一个静态网格 Nanite Assembly：

```cpp
// 来源：Engine/Plugins/Experimental/NaniteAssemblyEditorUtils/Source/NaniteAssemblyEditorUtils/Private/NaniteAssemblyStaticMeshBuilder.cpp
// （非精确路径，仅示例）

// 创建一个新的 Assembly 构建器
FNaniteAssemblyCreateNewParameters Params;
Params.TargetDirectory.Path = TEXT("/Game/MyAssemblies");
Params.AssetName = TEXT("MyAssembly");
Params.bOverwriteExisting = false;

UNaniteAssemblyStaticMeshBuilder* Builder = UNaniteAssemblyStaticMeshBuilder::BeginNewStaticMeshAssemblyBuild(Params);
if (Builder)
{
    // 添加部件
    UStaticMesh* PartMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Props/SM_Brick.SM_Brick"));
    if (PartMesh)
    {
        FTransform PartTransform(FVector(100.0f, 0.0f, 0.0f));
        Builder->AddAssemblyPart(PartMesh, PartTransform);
    }

    // 最终完成构建
    UStaticMesh* ResultMesh = nullptr;
    if (Builder->FinishAssemblyBuild(ResultMesh))
    {
        // ResultMesh 即为生成的 Nanite Assembly 静态网格
    }
}
```

### 进阶用法

**从场景组件提取部件：**

```cpp
// 假设你在关卡编辑器中选中了一个包含多个子静态网格组件的 Actor
AActor* SelectedActor = ...; 
UStaticMeshComponent* MainComponent = SelectedActor->FindComponentByClass<UStaticMeshComponent>();

// 创建 Builder
UNaniteAssemblyStaticMeshBuilder* Builder = UNaniteAssemblyStaticMeshBuilder::BeginNewStaticMeshAssemblyBuild(Params);
if (Builder && MainComponent)
{
    // 将组件及其子组件中的所有网格实例添加到装配中
    FTransform OriginTransform = FTransform::Identity;
    Builder->AddAssemblyPartsFromComponent(MainComponent, OriginTransform, SelectedActor->GetRootComponent());
    
    UStaticMesh* ResultMesh = nullptr;
    Builder->FinishAssemblyBuild(ResultMesh);
}
```

**骨骼网格装配与多骨骼绑定：**

```cpp
// 创建骨骼网格 Builder
USkeletalMesh* BaseSkeleton = LoadObject<USkeletalMesh>(nullptr, TEXT("/Game/Characters/SK_BaseMannequin.SK_BaseMannequin"));
UNaniteAssemblySkeletalMeshBuilder* Builder = UNaniteAssemblySkeletalMeshBuilder::BeginNewSkeletalMeshAssemblyBuild(Params, BaseSkeleton);

// 创建部件绑定（例如绑定到 "Spine" 和 "Head" 骨骼）
FNaniteAssemblySkeletalMeshPartBinding Binding1, Binding2;
Builder->CreateBindingByBoneName(Binding1, TEXT("Spine"), FTransform(FVector(0.0f, 0.0f, 20.0f)));
Builder->CreateBindingByBoneName(Binding2, TEXT("Head"), FTransform(FVector(0.0f, 0.0f, 0.0f)));

// 添加部件
USkeletalMesh* ArmorMesh = LoadObject<USkeletalMesh>(nullptr, TEXT("/Game/Armor/SK_Armor.SK_Armor"));
USkeletalMesh* HelmetMesh = LoadObject<USkeletalMesh>(nullptr, TEXT("/Game/Armor/SK_Helmet.SK_Helmet"));
Builder->AddAssemblyPart(ArmorMesh, Binding1);
Builder->AddAssemblyPart(HelmetMesh, Binding2);

USkeletalMesh* Result = nullptr;
Builder->FinishAssemblyBuild(Result);
```

**材质合并选项：**

```cpp
FNaniteAssemblyMaterialMergeOptions MergeOptions;
MergeOptions.MaterialSlotGroup = 0;
MergeOptions.MergeBehavior = ENaniteAssemblyPartMaterialMerge::MergeIdenticalMaterials;
// 可选：提供材质覆盖
MergeOptions.MaterialOverrides.Add(OverrideMaterial);

Builder->AddAssemblyPart(PartMesh, Transform, MergeOptions);
```

## Demo 示例

以下是一个完整的、可编译的最小 C++ 示例，展示了在 Editor 模块中使用 `UNaniteAssemblyStaticMeshBuilder` 创建 Nanite Assembly 资产。假设你的模块已正确依赖该插件。

**MyAssemblyTool.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "MyAssemblyTool.generated.h"

UCLASS()
class UMyAssemblyTool : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "My Tools")
    static UStaticMesh* CreateSimpleAssembly(const FString& AssetPath, const FString& AssetName);
};
```

**MyAssemblyTool.cpp**

```cpp
#include "MyAssemblyTool.h"
#include "NaniteAssemblyStaticMeshBuilder.h"
#include "Engine/StaticMesh.h"
#include "UObject/SavePackage.h"

UStaticMesh* UMyAssemblyTool::CreateSimpleAssembly(const FString& AssetPath, const FString& AssetName)
{
    FNaniteAssemblyCreateNewParameters Params;
    Params.TargetDirectory.Path = AssetPath;
    Params.AssetName = AssetName;
    Params.bOverwriteExisting = false;

    UNaniteAssemblyStaticMeshBuilder* Builder = UNaniteAssemblyStaticMeshBuilder::BeginNewStaticMeshAssemblyBuild(Params);
    if (!Builder)
    {
        return nullptr;
    }

    // 加载两个示例网格（请确保资源存在）
    UStaticMesh* PartA = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/MyMeshes/SM_PartA.SM_PartA"));
    UStaticMesh* PartB = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/MyMeshes/SM_PartB.SM_PartB"));
    if (!PartA || !PartB)
    {
        return nullptr;
    }

    // 添加部件
    Builder->AddAssemblyPart(PartA, FTransform(FVector(0.0f, 0.0f, 0.0f)));
    Builder->AddAssemblyPart(PartB, FTransform(FVector(100.0f, 0.0f, 0.0f)));

    UStaticMesh* Result = nullptr;
    Builder->FinishAssemblyBuild(Result);
    return Result;
}
```

此示例函数接受路径和名称，创建一个包含两个部件的 Nanite Assembly 静态网格并返回。可在蓝图或其他 C++ 代码中调用。

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖 | 仅标准 Core/Engine/Slate 等 |

该插件自身为 Editor 模块，依赖隐式通过 `UStaticMesh`、`USkeletalMesh` 等引擎核心类型满足。实际运行时需要 Nanite 支持（项目设置中启用 Nanite），但不涉及其他第三方模块。

## 维护状态

### 近期更新

- 2025-09-23 `8d2e2d10` — [NaniteAssemblyBuilder] Move module header in public
- 2025-09-12 `f89d77ef` — Additional non-unity fixes from removing GCObject.h from StrongObjectPtr.h
- 2025-09-11 `87981cf5` — [NaniteAssemblies] Some final cleanup of NaniteAssemblyEditorUtils and the Blueprint interfaces it e
- 2025-09-08 `85cdc206` — [NaniteAssemblies] Adding a skeletal mesh Nanite Assembly builder to the NaniteAssemblyEditorUtils p
- 2025-09-02 `9a5141f3` — [NaniteAssemblies] Introducing NaniteAssemblyEditorUtils, a new experimental plugin to provide utili

### 维护评价

该插件于 2025 年 9 月创建，仍处于实验性阶段（`IsExperimentalVersion = true`）。从 git 历史看，它正在活跃开发中，短期内快速迭代，增加了骨骼网格支持并进行了清理。目前功能已基本完整，覆盖静态网格和骨骼网格的创建与编辑。插件设计为蓝图友好，API 文档较清晰。

**建议**：由于是实验性插件，API 可能在后续版本中发生变化，建议仅在测试项目中使用，避免直接依赖生产环境。如果在蓝图工作流中需要 Nanite Assembly，该插件是目前官方唯一的蓝图接口，值得尝试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NaniteAssemblyEditorUtils)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/nanite-virtualized-geometry/)（Nanite 通用文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NaniteAssemblyEditorUtils/Tests)（若存在）