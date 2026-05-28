# Geometry Collection Editor

> Adds Geometry Collection Container.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 几何体集合编辑器 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产工厂、细节自定义、编辑器命令、工具） |
| 模块 | `GeometryCollectionEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-07-31 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryCollectionPlugin/Source/GeometryCollectionEditor) | |

## 用途

GeometryCollectionPlugin 的核心是提供一个可破坏的几何体集合容器及其编辑工具。传统的破坏系统通常基于预分割的网格，而几何体集合（Geometry Collection）允许将多个静态网格、骨骼网格或其他几何体集合合并为一个单一的、结构化的资产。这个容器不仅存储几何数据，还定义了层次化的骨骼结构，使得集合中的每个“碎片”都可以被独立控制、动画和破坏。

该插件的编辑器模块（`GeometryCollectionEditor`）提供了在编辑器中创建、编辑和调试这些几何体集合的完整工具链。它解决了以下问题：
1.  **资产创建**：将场景中多个独立的网格体（如由多个Cube组成的墙壁）组合成一个统一的、可模拟的几何体集合资产。
2.  **编辑与调试**：提供命令行工具来检查集合状态（如打印统计信息）、修复几何问题（如删除重复顶点、修复孔洞）、以及设置属性（如模拟参数）。
3.  **工作流集成**：通过资产工厂、细节面板自定义和编辑器模式，无缝集成到标准的UE编辑器工作流中，使得艺术家和技术美术可以像处理普通资产一样处理几何体集合。

## 使用场景

-   **可破坏环境**：你在制作一个需要实时物理破坏的场景，例如一堵砖墙或一扇木门。你可以将组成墙体的所有砖块网格体转换成一个几何体集合，使其能够根据受力点进行真实的碎裂和模拟。
-   **车辆碰撞效果**：制作车辆变形或零件脱落效果时，将车辆的多个面板和零件组合成一个几何体集合，碰撞时可以精确控制哪些部分分离或变形。
-   **物理模拟调试**：在开发复杂的破坏逻辑时，使用插件提供的命令行工具（如 `GeometryCollection.PrintDetailedStatistics`）来分析集合的结构、骨骼层级和几何数据，快速定位问题。
-   **数据驱动工作流**：通过 `GeometryCollection.SetNamedAttributeValues` 等命令，可以根据命名规则（如骨骼名称）批量设置属性，实现自动化资产配置。

## 蓝图用法

该插件的核心功能主要通过 C++ 模块和编辑器命令提供，直接暴露给蓝图的节点较少。其编辑器功能主要通过控制台命令、编辑器模式和细节面板来使用。

### 核心节点 (蓝图可用)

插件本身没有提供大量 `BlueprintCallable` 节点。其命令行功能（如 `FGeometryCollectionCommands::ToString`）通常通过 `ExecuteConsoleCommand` 蓝图节点或编辑器控制台来调用。

一些关键的编辑器行为（如 `FGeometryCollectionConversion` 中的 `CreateGeometryCollectionCommand`）是通过编辑器模块命令注册的，主要在编辑器工具栏或菜单中使用。

### 使用示例（蓝图描述）

虽然直接蓝图节点不多，但你可以通过蓝图实现以下工作流：
1.  **在关卡蓝图中**：使用 `Execute Console Command` 节点，输入命令如 `GeometryCollection.PrintStatistics` 来输出当前选中几何体集合演员的统计信息到输出日志。
2.  **在编辑器工具蓝图中**：你无法直接调用 `FGeometryCollectionConversion` 的静态函数。这些函数是编辑器命令的一部分，通常由 UI 按钮触发。你需要通过扩展编辑器 UI（创建工具栏按钮）来调用这些命令。

## C++ 用法

### 头文件引入

使用编辑器转换和命令功能：
```cpp
#include "GeometryCollection/GeometryCollectionConversion.h"
#include "GeometryCollection/GeometryCollectionCommands.h"
```
使用资产工厂：
```cpp
#include "GeometryCollection/GeometryCollectionFactory.h"
```

### 基本用法

**创建几何体集合并追加网格（来源： `GeometryCollectionConversion.h` ）**

```cpp
// 假设你已经有了 UStaticMesh* 和对应的 UGeometryCollection* 资产
UStaticMesh* SourceMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Meshes/MyWallBrick"));
UGeometryCollection* GeometryCollection = NewObject<UGeometryCollection>();

// 创建材质数组（示例为单个材质）
TArray<UMaterialInterface*> Materials;
if (SourceMesh->GetStaticMaterials().Num() > 0)
{
    Materials.Add(SourceMesh->GetStaticMaterials()[0].MaterialInterface);
}

// 获取网格在世界中的变换
FTransform MeshTransform = FTransform::Identity;

// 调用静态方法将静态网格追加到几何体集合中
FGeometryCollectionConversion::AppendStaticMesh(
    SourceMesh,
    Materials,
    MeshTransform,
    GeometryCollection
    /*, bReindexMaterials = true */
);

// 此时 GeometryCollection 对象已包含该网格的几何和变换数据
```

**执行几何体集合操作命令（来源： `GeometryCollectionCommands.h` ）**

```cpp
// 需要在编辑器环境中执行（例如在自定义编辑器模块或控制台命令处理中）
UWorld* World = GEditor->GetEditorWorldContext().World();

// 打印选中几何体集合演员的统计信息
FGeometryCollectionCommands::PrintStatistics(World);

// 确保集合只有一个根节点，返回根节点索引
int32 RootIndex = FGeometryCollectionCommands::EnsureSingleRoot(MyGeometryCollection);
UE_LOG(LogTemp, Log, TEXT("Root index after ensure: %d"), RootIndex);

// 删除零面积的面
TArray<FString> Args;
FGeometryCollectionCommands::DeleteZeroAreaFaces(Args, World);
```

### 进阶用法

**通过工厂创建几何体集合资产（来源： `GeometryCollectionFactory.h` ）**

```cpp
// 在编辑器代码中（如资产创建逻辑）
UGeometryCollectionFactory* Factory = NewObject<UGeometryCollectionFactory>();
UPackage* Package = CreatePackage(*FString::Printf(TEXT("/Game/Collections/%s"), *AssetName));
UObject* NewObject = Factory->FactoryCreateNew(
    UGeometryCollection::StaticClass(),
    Package,
    FName(*AssetName),
    RF_Public | RF_Standalone,
    nullptr,
    GWarn
);

if (UGeometryCollection* NewCollection = Cast<UGeometryCollection>(NewObject))
{
    // 新资产已创建，可以继续向其追加几何数据
    FGeometryCollectionConversion::AppendStaticMesh(/*...*/);
    NewCollection->MarkPackageDirty();
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何在编辑器插件中创建一个几何体集合并保存它。

**GeometryCollectionEditorDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "GeometryCollectionEditorDemo.generated.h"

class UGeometryCollection;
class UStaticMesh;

UCLASS(BlueprintType)
class UGeometryCollectionDemoHelper : public UObject
{
    GENERATED_BODY()

public:
    // 创建一个包含指定静态网格的几何体集合资产
    UFUNCTION(BlueprintCallable, Category = "GeometryCollectionDemo", meta=(CallInEditor="true"))
    static UGeometryCollection* CreateDemoCollectionFromMesh(UStaticMesh* InMesh, const FString& AssetPath);
};
```

**GeometryCollectionEditorDemo.cpp**
```cpp
#include "GeometryCollectionEditorDemo.h"
#include "GeometryCollection/GeometryCollectionConversion.h"
#include "GeometryCollection/GeometryCollection.h"
#include "Engine/StaticMesh.h"
#include "AssetToolsModule.h"
#include "IAssetTools.h"

UGeometryCollection* UGeometryCollectionDemoHelper::CreateDemoCollectionFromMesh(UStaticMesh* InMesh, const FString& AssetPath)
{
    if (!InMesh)
    {
        UE_LOG(LogTemp, Error, TEXT("Input mesh is null."));
        return nullptr;
    }

    // 创建包和资产
    IAssetTools& AssetTools = FModuleManager::LoadModuleChecked<FAssetToolsModule>("AssetTools").Get();
    UObject* NewAsset = AssetTools.CreateAsset(
        FPaths::GetBaseFilename(AssetPath),
        FPaths::GetPath(AssetPath),
        UGeometryCollection::StaticClass(),
        nullptr
    );

    UGeometryCollection* NewCollection = Cast<UGeometryCollection>(NewAsset);
    if (!NewCollection)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create GeometryCollection asset."));
        return nullptr;
    }

    // 准备追加所需数据
    TArray<UMaterialInterface*> Materials;
    const FStaticMeshSourceModel& SourceModel = InMesh->GetSourceModel(0);
    for (const FStaticMaterial& MatSlot : InMesh->GetStaticMaterials())
    {
        if (MatSlot.MaterialInterface)
        {
            Materials.Add(MatSlot.MaterialInterface);
        }
    }

    // 使用默认变换将网格追加到集合
    FGeometryCollectionConversion::AppendStaticMesh(
        InMesh,
        Materials,
        FTransform::Identity,
        NewCollection
    );

    // 标记资产已修改
    NewCollection->MarkPackageDirty();
    UE_LOG(LogTemp, Log, TEXT("Successfully created GeometryCollection at: %s"), *AssetPath);

    return NewCollection;
}
```

## 模块依赖

要使用 `GeometryCollectionEditor` 模块的功能（如 `FGeometryCollectionConversion` 和 `FGeometryCollectionCommands`），你的项目或插件模块需要在 `.Build.cs` 文件中添加以下依赖。

| 模块 | 用途 |
|---|---|
| `Engine` | 核心引擎模块，包含 `UObject`、`UFactory` 等基础类。 |
| `GeometryCollection` | 提供 `UGeometryCollection` 核心数据资产类型。 |
| `PhysicsCore` | 提供物理相关的核心接口，几何体集合与物理破坏紧密相关。 |
| `Slate`, `SlateCore` | 用于编辑器UI扩展，如细节面板自定义和编辑器模式。 |
| `EditorStyle`, `PropertyEditor` | 用于编辑器样式和属性面板自定义。 |
| `UnrealEd` | 提供 `FEdMode`、`UFactory` 等编辑器框架。 |
| `AssetTools` | 用于创建和操作资产。 |

**注意**：`Core`, `CoreUObject`, `Engine`, `Slate`, `SlateCore`, `UMG`, `InputCore`, `UnrealEd`, `EditorStyle`, `PropertyEditor`, `Projects`, `DeveloperSettings` 等模块属于常见依赖，上表中已包含在 `Engine`, `UnrealEd` 等条目下，但为清晰起见仍列出。请根据你的具体需求调整。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-23 | `176334d2` | Fix localization warnings for UE 5.8 | 修复 UE 5.8 中的本地化警告。 |
| 2026-05-14 | `ae91b9c4` | Dataflow: | Dataflow 相关更新。 |
| 2026-05-14 | `28e138a1` | [Backout] - CL53945814 | 回退了某个更改（CL53945814）。 |
| 2026-05-14 | `88fb5004` | Dataflow: | Dataflow 相关更新。 |
| 2026-05-14 | `d2897727` | Dataflow : add a node to create external collision on a geometry collection | 为几何体集合添加了一个创建外部碰撞的 Dataflow 节点。 |

### 维护评价

该插件创建于 **2018年**，历史较长。从近期的提交记录（2026年5月）来看，它仍在**活跃维护**中，特别是围绕 **Dataflow** 节点集进行功能扩展和修复。
- **活跃度**：近期更新频率较高，且集中在功能增强（添加新Dataflow节点）和版本兼容性修复（UE 5.8本地化警告）上，表明它仍在跟随引擎主线发展。
- **实验性状态**：插件在 `.uplugin` 中明确标记为 `IsBetaVersion: true`，且默认不启用。这意味着它功能可能尚不完全稳定，API 随时可能发生变化。
- **已知限制**：作为实验性插件，其文档和测试用例可能不完整，直接在生产环境中使用需要谨慎。
- **推荐**：对于需要**高级破坏模拟和几何体管理**的项目，这是一个强大的工具。建议在**项目原型阶段或技术验证阶段**采用，并密切关注引擎版本更新可能带来的变更。由于其活跃的维护状态和底层的重要性（是Chaos破坏系统的一部分），值得投入学习，但不宜在缺乏深入理解的情况下直接用于核心生产系统。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryCollectionPlugin/Source/GeometryCollectionEditor)
- 官方文档（暂无公开链接，可参考引擎内置的 `GeometryCollection` 相关文档和示例项目）