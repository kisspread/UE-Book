# Geometry

> Adds Geometry Collection Container.

| 属性 | 值 |
|---|---|
| 中文名 | 几何体集合编辑器 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GeometryCollectionDepNodes` (Runtime), `GeometryCollectionEditor` (Runtime), `GeometryCollectionNodes` (Runtime), `GeometryCollectionSequencer` (Runtime), `GeometryCollectionTracks` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-06 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryCollectionPlugin) | |

---

## 用途

该插件为 **Geometry Collection（几何体集合）** 资产提供完整的编辑器支持。几何体集合是 UE5 中用于**破坏模拟、程序化破碎**和**复杂物理对象组合**的核心容器，能够将多个静态网格体、骨骼网格体或子集合合并为一个单一的高效数据结构。此插件包含：

- 资产类型注册与工厂（创建、导入）
- 自定义细节面板（属性排序、缓存参数、警告信息）
- 缩略图渲染器
- 编辑器内转换工具（从选中的 Actor/Asset 生成几何体集合）
- 编辑器命令（统计、清理、设置属性等）
- 视口交互模式（点击选择刚体）
- 序列器轨道支持（动画化几何体集合变化）
- 数据流（Dataflow）节点集成

解决的核心问题：在编辑器中**高效创建、管理和编辑** Chaos 破碎系统所需的几何体集合资源，提供直观的 UI 和自动化工作流。

---

## 使用场景

- **制作可破坏环境**：将静态网格体（墙体、柱子）转换为几何体集合，在运行时用 Chaos 模拟破碎。
- **程序化生成**：利用 Dataflow 节点动态生成或编辑几何体集合结构。
- **游戏对象组合**：将多个零部件（如载具的轮胎、底盘）合并为一个物理体，减少碰撞开销。
- **影视/过场动画**：在 Sequencer 中为几何体集合添加关键帧，控制破碎动画。

---

## 蓝图用法

> 本模块主要提供编辑器 UI 和 C++ 工具，**极少暴露蓝图可调用函数**。几何体集合的运行时操作（如触发破碎、缓存回放）由 `GeometryCollectionComponent` 提供蓝图节点，属于 `GeometryCollectionEngine` 模块范畴，不在此文档。

本模块的蓝图相关内容仅涉及**资产创建辅助**（如 `UGeometryCollectionFactory` 可用 C++ 调用，蓝图无直接节点）。

---

## C++ 用法

### 头文件引入

```cpp
#include "GeometryCollection/GeometryCollectionEditorPlugin.h"
#include "GeometryCollection/GeometryCollectionCommands.h"
#include "GeometryCollection/GeometryCollectionConversion.h"
#include "GeometryCollection/GeometryCollectionFactory.h"
#include "GeometryCollection/GeometryCollectionCacheFactory.h"
#include "GeometryCollection/GeometryCollectionSelectRigidBodyEdMode.h"
```

### 基本用法

#### 1. 创建 Geometry Collection 资产

```cpp
// 使用工厂在内容目录创建新资产
UGeometryCollectionFactory* Factory = NewObject<UGeometryCollectionFactory>();
UPackage* Package = CreatePackage(TEXT("/Game/MyCollections"));
UGeometryCollection* NewCollection = Cast<UGeometryCollection>(
    Factory->FactoryCreateNew(
        UGeometryCollection::StaticClass(),
        Package,
        FName(TEXT("MyCollection")),
        RF_Public | RF_Standalone | RF_Transactional,
        nullptr,
        GWarn
    )
);
NewCollection->MarkPackageDirty();
```
*来源：`GeometryCollectionFactory.h`*

#### 2. 从静态网格体追加几何体

```cpp
// 将静态网格体数据加入已有集合
UStaticMesh* Mesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/MyMesh.MyMesh"));
UGeometryCollection* TargetCollection = ...;
FTransform Transform = FTransform::Identity;

// 从网格组件获取材质（若无组件则从静态网格本身获取）
TArray<UMaterialInterface*> Materials;
for (int32 i = 0; i < Mesh->GetStaticMaterials().Num(); ++i)
{
    Materials.Add(Mesh->GetStaticMaterials()[i].MaterialInterface);
}

FGeometryCollectionConversion::AppendStaticMesh(
    Mesh,
    Materials,
    Transform,
    TargetCollection,
    true  // ReindexMaterials
);
```
*来源：`GeometryCollectionConversion.h`*

#### 3. 从骨骼网格体追加

```cpp
USkeletalMesh* SkeletalMesh = LoadObject<USkeletalMesh>(nullptr, TEXT("/Game/MySkeletalMesh.MySkeletalMesh"));
USkeletalMeshComponent* SkeletalComponent = ...; // 可选，提供材质和变换
FTransform Transform = FTransform::Identity;

FGeometryCollectionConversion::AppendSkeletalMesh(
    SkeletalMesh,
    SkeletalComponent,
    Transform,
    TargetCollection,
    true
);
```
*来源：同上*

#### 4. 执行编辑器命令

```cpp
// 输出统计信息到日志
FGeometryCollectionCommands::PrintStatistics(GWorld);
FGeometryCollectionCommands::PrintDetailedStatistics(GWorld);

// 删除重合顶点（影响性能）
FGeometryCollectionCommands::DeleteCoincidentVertices(TArray<FString>(), GWorld);

// 设置特定属性（示例：将 Transform 组中 BoneName 匹配 "Cube_1_1" 的 SimulatableParticlesAttribute 设为 false）
TArray<FString> Args;
Args.Add(TEXT("bool"));
Args.Add(TEXT("SimulatableParticlesAttribute"));
Args.Add(TEXT("Transform"));
Args.Add(TEXT("0"));  // Value 作为字符串
Args.Add(TEXT("BoneName"));
Args.Add(TEXT("Cube_1_1"));
FGeometryCollectionCommands::SetNamedAttributeValues(Args, GWorld);
```
*来源：`GeometryCollectionCommands.h`*

#### 5. 创建缓存（Cache）

```cpp
// 通过缓存工厂为几何体集合创建缓存
UGeometryCollection* Collection = ...; // 目标集合
UGeometryCollectionCacheFactory* CacheFactory = NewObject<UGeometryCollectionCacheFactory>();
CacheFactory->TargetCollection = Collection;
UGeometryCollectionCache* NewCache = Cast<UGeometryCollectionCache>(
    CacheFactory->FactoryCreateNew(
        UGeometryCollectionCache::StaticClass(),
        GetTransientPackage(),
        NAME_None,
        RF_Transactional,
        nullptr,
        GWarn
    )
);
```
*来源：`GeometryCollectionCacheFactory.h`*

### 进阶用法

#### 激活刚体选择编辑器模式

该模式允许用户在视口中点击几何体集合的刚体，并自动更新关联的属性（如刚性体 ID 和求解器 Actor）。

```cpp
// 准备好两个属性句柄（IPropertyHandle），并设置进入/退出回调
TSharedRef<IPropertyHandle> RigidBodyIdHandle = ...;
TSharedRef<IPropertyHandle> SolverActorHandle = ...;

if (FGeometryCollectionSelectRigidBodyEdMode::CanActivateMode())
{
    FGeometryCollectionSelectRigidBodyEdMode::ActivateMode(
        RigidBodyIdHandle,
        SolverActorHandle,
        []() { /* OnEnter - 例如禁用其他模式 */ },
        []() { /* OnExit - 恢复 */ }
    );
}
// 可通过静态方法 IsModeActive() 检查是否活跃
// 使用完毕后调用 DeactivateMode()
FGeometryCollectionSelectRigidBodyEdMode::DeactivateMode();
```
*来源：`GeometryCollectionSelectRigidBodyEdMode.h`*

#### 自定义缓存参数细节面板

在编辑器模块中注册自定义属性类型布局，以控制 `GeometryComponentCacheParameters` 的兼容性显示和过滤。

```cpp
// 在模块 StartupModule 中注册
FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
PropertyModule.RegisterCustomPropertyTypeLayout(
    "GeometryComponentCacheParameters",
    FOnGetPropertyTypeCustomizationInstance::CreateStatic(&FGeomComponentCacheParametersCustomization::MakeInstance)
);
```
*来源：`GeomComponentCacheCustomization.h`*

---

## Demo 示例

以下是一个最小 C++ 可编译示例：从选中的静态网格体创建几何体集合资产，并追加该网格体。

**MyGCExample.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyGCExample.generated.h"

UCLASS()
class UMyGCExample : public UObject
{
    GENERATED_BODY()

public:
    /** 从静态网格体创建几何体集合（编辑器工具） */
    UFUNCTION(BlueprintCallable, Category = "GeometryCollection|Example")
    static void CreateGCFromStaticMesh(UStaticMesh* SourceMesh, const FString& AssetName);
};
```

**MyGCExample.cpp**
```cpp
#include "MyGCExample.h"
#include "GeometryCollection/GeometryCollectionFactory.h"
#include "GeometryCollection/GeometryCollectionConversion.h"
#include "GeometryCollection/GeometryCollectionObject.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInterface.h"
#include "UObject/Package.h"
#include "FileHelpers.h"

void UMyGCExample::CreateGCFromStaticMesh(UStaticMesh* SourceMesh, const FString& AssetName)
{
    if (!SourceMesh) return;

    // 1. 创建包和资产
    FString PackagePath = FString::Printf(TEXT("/Game/GeometryCollections/%s"), *AssetName);
    UPackage* Package = CreatePackage(*PackagePath);
    UObject* Outer = Package;
    FName Name = FName(*AssetName);

    UGeometryCollectionFactory* Factory = NewObject<UGeometryCollectionFactory>();
    UGeometryCollection* GC = Cast<UGeometryCollection>(Factory->FactoryCreateNew(
        UGeometryCollection::StaticClass(),
        Outer,
        Name,
        RF_Public | RF_Standalone | RF_Transactional,
        nullptr,
        GWarn
    ));
    if (!GC) return;

    // 2. 从静态网格体收集材质
    TArray<UMaterialInterface*> Materials;
    for (const FStaticMaterial& Mat : SourceMesh->GetStaticMaterials())
    {
        Materials.Add(Mat.MaterialInterface);
    }

    // 3. 追加网格体数据
    FTransform Transform = FTransform::Identity;
    FGeometryCollectionConversion::AppendStaticMesh(SourceMesh, Materials, Transform, GC, true);

    // 4. 标记脏并保存
    GC->MarkPackageDirty();
    UEditorLoadingAndSavingUtils::SaveDirtyPackages(false, true);
}
```

> 注意：此示例需要在编辑器模式下运行，因为它使用了 `UEditorLoadingAndSavingUtils`。生产中建议迁移到 `UPackage::Save` 异步接口。

---

## 模块依赖

> 以下列出本插件独特的依赖项（省略核心引擎标准依赖）。

| 模块 | 用途 |
|---|---|
| `GeometryCollectionEngine` | 运行时核心（`UGeometryCollection`, `UGeometryCollectionComponent`） |
| `ChaosSolverEngine` | 混沌求解器，用于物理模拟 |
| `DataflowCore` / `DataflowEngine` | 数据流系统基础，用于程序化编辑 |
| `GeometryCollectionNodes` | 数据流节点，实现几何体集合的操作 |
| `Sequencer` / `MovieScene` | 序列器轨道支持（`GeometryCollectionSequencer`, `GeometryCollectionTracks`） |
| `UnrealEd` | 编辑器基础设施（常见，但此处用于工厂、细节面板等） |

若想在自己的模块中使用 `GeometryCollectionEditor`，需在 `Build.cs` 中添加：  
`PublicDependencyModuleNames.AddRange(new string[] { "GeometryCollectionEditor", "GeometryCollectionEngine", ... });`

---

## 维护状态

### 近期更新

- 2025-09-25 `745ebb56` — Add support for override materials for geometry collection root proxies
- 2025-09-24 `787ab8b2` — Geometry collection : add cvar to disable the dialog that ask to create a Dataflow graph when opening
- 2025-09-23 `29aa54b8` — Dataflow : add settings for Dataflow editor
- 2025-09-16 `9a2a2477` — Dataflow : fix Tetrahedron rendering crashing when the source collection was split in multiple geometries
- 2025-09-06 `38d85df2` — dataflow : expose all properties of TransformCollection node as inputs

### 维护评价

该插件创建于 2025 年 9 月，**非常新**（不足一个月），但更新频率极高（几乎每天都有提交）。当前版本标记为 0.1 Beta，Epic 正在积极开发，主要围绕 **Dataflow 集成** 和 **编辑器体验改进**。

- ✅ **活跃维护**：近期 commit 包含功能增加、Bug 修复和配置优化。
- ⚠️ **实验性**：`IsBetaVersion = true`，API 可能随时变更。
- 💡 推荐用于**需要最新破碎特性**的项目，但需注意潜在不稳定性和未来升级成本。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryCollectionPlugin)
- [官方文档]（暂无独立文档页）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryCollectionPlugin/Tests)（部分测试位于插件目录内）