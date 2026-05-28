# Geometry Collection Plugin

> Adds Geometry Collection Container.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 几何体集合容器 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `GeometryCollectionDepNodes` (Runtime), `GeometryCollectionEditor` (Runtime), `GeometryCollectionNodes` (Runtime), `GeometryCollectionSequencer` (Runtime), `GeometryCollectionTracks` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-07-31 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryCollectionPlugin) | |

## 用途

Geometry Collection Plugin 提供了一个用于管理 **几何体集合 (Geometry Collection)** 的核心框架。它解决的主要问题是将多个静态网格体 (Static Mesh)、骨骼网格体 (Skeletal Mesh) 甚至其他几何体集合组合成一个统一的、可管理的资产。这种集合资产是 UE5 中 Chaos 破碎系统 (Chaos Destruction) 的基石，允许复杂的物体（如墙壁、雕像）在物理交互下按照预定义的碎片层次结构进行破碎。

## 使用场景

- **室内破坏游戏**：制作一面墙壁，由数百块砖块组成，玩家射击或冲击时，墙壁能够根据砖块的连接关系和物理力进行真实的碎裂。
- **物体碎裂动画**：创建一个花瓶，预先定义其破碎的碎片和层级关系，在游戏中可以播放动画或受力时破碎。
- **建筑倒塌模拟**：构建一栋建筑，将其结构分解为梁、柱、外墙等几何体集合，实现可控的、符合物理规则的倒塌效果。
- **程序化生成破碎**：通过编辑器工具或代码，将场景中的多个静态网格体自动合并为一个几何体集合资产，为后续的破碎模拟做准备。

## 蓝图用法

本插件主要提供底层数据结构和编辑器工具，其蓝图接口相对有限，更侧重于 C++ 编程和编辑器工作流。大部分高级操作通过控制台命令或 C++ API 完成。

### 核心节点

该插件未暴露大量 `BlueprintCallable` 函数。其主要蓝图交互点是：

| 节点 | 说明 | 所在类 |
|---|---|---|
| 通过资产创建 | 在内容浏览器中右键 `Geometry Collection` 资产，创建 `GeometryCollectionActor` 并赋予其 `GeometryCollectionComponent`。 | `UActorFactoryGeometryCollection` |
| 属性编辑 | 在 `GeometryCollectionComponent` 的细节面板中，可以配置缓存、碰撞等参数。 | `UGeometryCollectionComponent` |

### 使用示例（蓝图描述）

1.  **创建资产**：在内容浏览器空白处右键 -> `几何体` -> `Geometry Collection`，创建一个新的几何体集合资产。
2.  **编辑资产**：双击打开该资产，进入专用编辑器。可以使用工具将场景中的静态网格体转换并添加到集合中，或者直接编辑其层次结构和属性。
3.  **放入场景**：将创建好的 `Geometry Collection` 资产从内容浏览器拖拽到场景中，引擎会自动生成一个带有 `GeometryCollectionComponent` 的 `GeometryCollectionActor`。
4.  **模拟破碎**：在关卡中对 `GeometryCollectionActor` 施加物理力（如爆炸、射线检测施加冲量），或使用 `GeometryCollectionComponent` 的缓存功能播放预先录制好的破碎动画。

## C++ 用法

该插件的核心价值在于其 C++ API，用于程序化地创建、操作和转换几何体集合。

### 头文件引入

```cpp
#include "GeometryCollection/GeometryCollectionConversion.h" // 用于网格体转换
#include "GeometryCollection/GeometryCollectionCommands.h"   // 用于编辑器命令
```

### 基本用法

以下是将一个静态网格体转换并追加到几何体集合的基本流程。

**来源**: `Engine/Plugins/Experimental/GeometryCollectionPlugin/Source/GeometryCollectionEditor/Public/GeometryCollection/GeometryCollectionConversion.h`

```cpp
// 假设你有一个 UStaticMesh* MyStaticMesh 和一个 UGeometryCollection* MyCollection
// 以及对应的组件和变换信息

// 方法一：提供网格体、材质数组和变换
TArray<UMaterialInterface*> Materials;
// ... 填充材质数组 ...
FTransform MeshTransform = FTransform::Identity;

FGeometryCollectionConversion::AppendStaticMesh(
    MyStaticMesh,
    Materials,
    MeshTransform,
    MyCollection,
    true // 是否重新索引材质
);

// 方法二：提供静态网格体组件（自动获取材质和变换）
// 假设 UStaticMeshComponent* MyComponent 存在于场景中
FGeometryCollectionConversion::AppendStaticMesh(
    MyStaticMesh,
    MyComponent,
    MyComponent->GetComponentTransform(),
    MyCollection,
    true
);
```

### 进阶用法

几何体集合支持嵌套和复杂操作。以下示例展示如何合并两个几何体集合并确保单一根节点。

**来源**: `Engine/Plugins/Experimental/GeometryCollectionPlugin/Source/GeometryCollectionEditor/Public/GeometryCollection/GeometryCollectionCommands.h`

```cpp
// 创建两个几何体集合
UGeometryCollection* CollectionA = ...; // 通过 FObjectFinder 或 NewObject 创建
UGeometryCollection* CollectionB = ...;

// 将集合B追加到集合A
FGeometryCollectionConversion::AppendGeometryCollection(
    CollectionB,
    TArray<UMaterialInterface*>(), // 材质数组，可留空
    FTransform(FVector(100, 0, 0)), // 变换：将集合B偏移100个单位
    CollectionA,
    true
);

// 确保整个组合后的集合有一个单一的根节点（对于层级结构和破碎很重要）
int32 RootIndex = FGeometryCollectionCommands::EnsureSingleRoot(CollectionA);
UE_LOG(LogTemp, Log, TEXT("新根节点索引: %d"), RootIndex);

// 使用控制台命令调试输出集合信息
FGeometryCollectionCommands::ToString(GWorld);
```

## Demo 示例

一个最小化的 C++ 示例，演示如何创建并填充一个 `UGeometryCollection` 对象。

**MyGeometryCollectionDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyGeometryCollectionDemo.generated.h"

class UGeometryCollection;
class UStaticMesh;

UCLASS(BlueprintType)
class UMyGeometryCollectionDemo : public UObject
{
    GENERATED_BODY()

public:
    // 从指定的静态网格体创建并填充一个几何体集合
    UFUNCTION(BlueprintCallable, Category = "GeometryCollectionDemo")
    UGeometryCollection* CreateCollectionFromMesh(UStaticMesh* SourceMesh, const FTransform& MeshTransform);

private:
    // 用于存储创建的集合资产，避免被GC回收
    UPROPERTY()
    TObjectPtr<UGeometryCollection> CachedCollection;
};
```

**MyGeometryCollectionDemo.cpp**
```cpp
#include "MyGeometryCollectionDemo.h"
#include "GeometryCollection/GeometryCollectionConversion.h"
#include "GeometryCollection/GeometryCollection.h"

UGeometryCollection* UMyGeometryCollectionDemo::CreateCollectionFromMesh(UStaticMesh* SourceMesh, const FTransform& MeshTransform)
{
    if (!SourceMesh)
    {
        return nullptr;
    }

    // 1. 创建一个新的几何体集合对象
    // 在实际使用中，这通常会通过UFactory创建持久化资产
    UGeometryCollection* NewCollection = NewObject<UGeometryCollection>(GetTransientPackage(), NAME_None, RF_Transient);
    if (!NewCollection)
    {
        return nullptr;
    }

    // 2. 准备材质数组（这里使用网格体自带的材质）
    TArray<UMaterialInterface*> Materials;
    for (int32 MaterialIndex = 0; MaterialIndex < SourceMesh->GetNumSections(0); ++MaterialIndex) // 假设LOD0
    {
        Materials.Add(SourceMesh->GetMaterial(MaterialIndex));
    }

    // 3. 将静态网格体追加到几何体集合中
    FGeometryCollectionConversion::AppendStaticMesh(
        SourceMesh,
        Materials,
        MeshTransform,
        NewCollection,
        true // 自动重新索引材质
    );

    // 4. 确保有单一的根节点
    FGeometryCollectionCommands::EnsureSingleRoot(NewCollection);

    CachedCollection = NewCollection;

    UE_LOG(LogTemp, Log, TEXT("成功从网格体 '%s' 创建了几何体集合"), *SourceMesh->GetName());
    return NewCollection;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Chaos` | Chaos 物理求解器核心，几何体集合的物理模拟依赖于此。 |
| `ChaosSolverEngine` | Chaos 求解器引擎，提供物理场景和模拟接口。 |
| `GeometryCollectionEngine` | 几何体集合运行时引擎，处理组件的逻辑和渲染。 |
| `SkeletalMeshDescription` | 用于处理骨骼网格体数据转换的中间描述结构。 |
| `EditorSubsystem` | 编辑器子系统框架，用于注册编辑器模式和菜单。 |
| `PropertyEditor` | 属性编辑器框架，用于自定义几何体集合资产的细节面板。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-23 | `176334d2` | Fix localization warnings for UE 5.8 | 修复本地化警告以兼容UE 5.8 |
| 2026-05-14 | `ae91b9c4` | Dataflow: | 数据流功能更新（具体改动未显示） |
| 2026-05-14 | `28e138a1` | [Backout] - CL53945814 | 回退了某个提交 (CL53945814) |
| 2026-05-14 | `88fb5004` | Dataflow: | 数据流功能更新（具体改动未显示） |
| 2026-05-14 | `d2897727` | Dataflow : add a node to create external collision on a geometry collection | 新增一个数据流节点，用于在几何体集合上创建外部碰撞 |

### 维护评价

该插件创建于 **2018年**，历史悠久。尽管如此，从最近的 Git 记录看，它**仍在活跃维护中**，特别是围绕 **Dataflow** 工具集的功能正在持续开发和集成。

**优点**：
- 作为 Chaos Destruction 的基础，核心功能稳定。
- 代码库持续更新，适应新版 UE（如 5.8）。
- 提供了丰富的编辑器工具和调试命令。

**缺点与注意事项**：
- 标记为 **实验性** (`IsBetaVersion=true`) 且 **默认禁用**，意味着 Epic 官方认为其 API 和功能在未来版本中可能发生变化。
- 是一个大型、复杂的插件，学习曲线较陡峭。
- 文档主要依赖源码注释和示例，官方文档较少。

**推荐**：如果你正在开发需要高级物理破碎效果的游戏，特别是需要精细控制破碎模式和性能，**推荐使用**此插件。但请做好应对 API 变更的心理准备，并将其视为一个需要深入研究和定制的**高级框架**，而非开箱即用的简单功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryCollectionPlugin)
- 官方文档：无
- 测试用例：插件源码内未发现独立的自动化测试文件。