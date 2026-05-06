# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图、材质模板、测试资源） |
| 模块 | `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageImporter` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDExporter` (Runtime), `USDClassesEditor` (Runtime), `GeometryCacheUSD` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-01 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDImporter) | |

---

## 用途

**USDSchemas 模块** 是 USD 导入器的核心转换层。它负责将 USD 场景描述（schema）中的各类基本图元（prim）转换为 Unreal Engine 对应的资源（Asset）和场景组件（SceneComponent）。该模块定义了一系列“翻译器”（Translator）类，每个翻译器对应一种 USD schema（如几何体、摄像机、灯光、骨骼等），实现将 USD 数据解析并生成 UE 可用的静态网格体、镜头、光源、骨骼网格体、毛发、Nanite 装配等。同时处理材质绑定、LOD、绘制模式（如卡片模式）等高级特性。

**为什么存在？**  
USD 文件包含丰富的场景结构，直接导入 UE 需要复杂的类型映射和资源创建逻辑。USDSchemas 将这一过程模块化为独立可扩展的翻译器，允许不同 schema 拥有独立的创建/更新逻辑，并支持自定义 schema 的注册。同时，它负责处理资产缓存、Prim 链接、LOD 切换等跨翻译器的共享逻辑。

---

## 使用场景

- 你正在开发一个需要从 USD 文件导入静态网格体、骨骼动画、毛发或材质的工具。
- 你需要自定义某个 USD 基元的导入行为（例如对特殊 schema 编写自定义翻译器）。
- 你希望从 USD 场景中提取摄像机、灯光信息以驱动 UE 场景。
- 你想要处理带有 LOD 或替代绘制模式（如卡片）的 USD 资产。
- 你需要在导入后进行材质分配和资源去重的优化。

---

## 蓝图用法

**本模块不公开任何直接可调的蓝图节点。** 所有翻译器（`FUsdGeomMeshTranslator`、`FUsdGeomCameraTranslator` 等）均为 C++ 内部类，通过 USD 导入流程（`USDStageImporter`）自动调用。  
蓝图中可通过以下间接方式使用：

- 使用 `USDStageImporter` 提供的蓝图节点（位于 `USDStageImporter` 模块）启动导入操作。
- 使用 `USDStageEditor` 的 UI 或 `UUsdStageImporterLibrary` 蓝图函数库。

---

## C++ 用法

### 头文件引入

```cpp
// 引入所需翻译器头文件
#include "USDGeomMeshTranslator.h"
#include "USDGeomCameraTranslator.h"
#include "USDSchemasModule.h"  // 模块注册接口
```

### 基本用法

翻译器通常不直接手动实例化，而是通过 `FUsdSchemaTranslatorRegistry`（已迁移至 `USDUtilities` 模块）注册并调度。以下示例展示如何注册一个自定义翻译器（以 `FUsdGeomMeshTranslator` 为例，注册过程在模块启动时自动完成）：

```cpp
// Source: USDSchemas/Private/USDSchemasModule.cpp (示意)
#include "Objects/USDSchemaTranslator.h"
#include "USDGeomMeshTranslator.h"

void FUsdSchemasModule::StartupModule()
{
    FUsdSchemaTranslatorRegistry& Registry = FUsdSchemaTranslatorRegistry::Get();
    // 注册 GeomMesh 翻译器
    Registry.Register<FUsdGeomMeshTranslator>(TEXT("GeomMesh"));
}
```

手工调用翻译器以创建资产和组件（通常由导入管道使用）：

```cpp
// 从 USD 场景中取得一个 GeomMesh Prim
UE::FUsdPrim MeshPrim = Stage.GetPrimAtPath(UE::FSdfPath(TEXT("/Root/MeshPrim")));

// 创建上下文
TSharedRef<FUsdSchemaTranslationContext> Context = MakeShared<FUsdSchemaTranslationContext>();
Context->Stage = Stage;
Context->AssetCache = NewObject<UUsdAssetCache3>();

// 创建翻译器（自动根据 schema 类型匹配）
TSharedPtr<FUsdSchemaTranslator> Translator = FUsdSchemaTranslatorRegistry::Get().CreateTranslator(MeshPrim, Context);
if (Translator.IsValid())
{
    // 创建资产（例如 UStaticMesh）
    Translator->CreateAssets();
    
    // 创建组件并添加到场景
    USceneComponent* Component = Translator->CreateComponents();
    // 后续可将 Component 附加到根组件
}
```

### 进阶用法

#### 使用材质解析与覆盖

`MeshTranslationImpl::ResolveMaterialAssignmentInfo` 和 `SetMaterialOverrides` 可在导入网格体后手动处理材质：

```cpp
#include "MeshTranslationImpl.h"

// 获取材质分配信息
TArray<UsdUtils::FUsdPrimMaterialAssignmentInfo> AssignmentInfos = ...;
UUsdAssetCache3& AssetCache = *Context->AssetCache;
FUsdPrimLinkCache& PrimLinkCache = ...;

TMap<const UsdUtils::FUsdPrimMaterialSlot*, UMaterialInterface*> SlotMaterials =
    MeshTranslationImpl::ResolveMaterialAssignmentInfo(
        UsdPrim,
        AssignmentInfos,
        AssetCache,
        PrimLinkCache,
        Flags,
        bShareAssetsForIdenticalPrims
    );

// 设置材质覆盖到组件
UMeshComponent* MeshComp = Cast<UMeshComponent>(SomeComponent);
MeshTranslationImpl::SetMaterialOverrides(Prim, ExistingAssignments, *MeshComp, Context);
```

#### 处理 Nanite 装配导入

`FUsdNaniteAssemblyTranslator` 用于从 USD 导入 Nanite 装配资产。创建资产时自动处理网格聚类和替换：

```cpp
#include "USDNaniteAssemblyTranslator.h"

// 在数据库注册（通常自动）
// 创建翻译器
TSharedPtr<FUsdNaniteAssemblyTranslator> NaniteTranslator = MakeShared<FUsdNaniteAssemblyTranslator>(Context, Schema);
NaniteTranslator->CreateAssets();
```

#### 自定义翻译器扩展

继承 `FUsdGeomXformableTranslator` 或直接继承 `FUsdSchemaTranslator` 并覆盖虚方法：

```cpp
class FMyCustomPrimTranslator : public FUsdGeomXformableTranslator
{
public:
    using FUsdGeomXformableTranslator::FUsdGeomXformableTranslator;

    virtual void CreateAssets() override;
    virtual USceneComponent* CreateComponents() override;
    virtual void UpdateComponents(USceneComponent* SceneComponent) override;
};
// 然后注册到 FUsdSchemaTranslatorRegistry
```

---

## Demo 示例

以下是一个完整的最小示例，展示如何将 USD 几何体网格导入为一个 `UStaticMesh` 并作为组件放置在场景中。该示例假定您已在模块中使用 USDSchemas 和 USDStage。

**MyUSDImporter.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "UsdWrappers/UsdStage.h"
#include "Engine/StaticMesh.h"

class UUsdAssetCache3;
class USceneComponent;

class FMyUSDImporter
{
public:
    // 导入指定路径的 USD 文件，返回创建的组件
    USceneComponent* ImportUSD(const FString& FilePath);
private:
    TStrongObjectPtr<UUsdAssetCache3> AssetCache;
};
```

**MyUSDImporter.cpp**

```cpp
#include "MyUSDImporter.h"
#include "USDGeomMeshTranslator.h"
#include "Objects/USDSchemaTranslator.h"
#include "USDIncludesStart.h"
#include "USDIncludesEnd.h"
#include <pxr/usd/usd/stage.h>

USceneComponent* FMyUSDImporter::ImportUSD(const FString& FilePath)
{
    // 打开 USD 舞台
    UE::FUsdStage Stage = UE::FUsdStage::Open(*FilePath);
    if (!Stage)
    {
        return nullptr;
    }

    // 创建上下文
    TSharedRef<FUsdSchemaTranslationContext> Context = MakeShared<FUsdSchemaTranslationContext>();
    Context->Stage = Stage;
    AssetCache.Reset(NewObject<UUsdAssetCache3>());
    Context->AssetCache = AssetCache.Get();
    Context->bShareAssetsForIdenticalPrims = true;
    Context->Flags = RF_Transactional | RF_Public;

    // 获取根 Prim
    UE::FUsdPrim RootPrim = Stage.GetPrimAtPath(UE::FSdfPath(TEXT("/")));
    if (!RootPrim)
    {
        return nullptr;
    }

    // 遍历子 Prim（此处仅处理第一个 GeomMesh）
    TArray<UE::FUsdPrim> Children = RootPrim.GetChildren();
    for (const UE::FUsdPrim& Child : Children)
    {
        if (Child.GetTypeName() == TEXT("Xform")) // 可能有嵌套
        {
            // 递归查找 GeomMesh
            TArray<UE::FUsdPrim> GrandChildren = Child.GetChildren();
            for (const UE::FUsdPrim& GChild : GrandChildren)
            {
                if (GChild.GetTypeName() == TEXT("Mesh"))
                {
                    // 创建翻译器
                    TSharedPtr<FUsdSchemaTranslator> Translator =
                        FUsdSchemaTranslatorRegistry::Get().CreateTranslator(GChild, Context);
                    if (Translator.IsValid())
                    {
                        Translator->CreateAssets();
                        return Translator->CreateComponents();
                    }
                }
            }
        }
    }
    return nullptr;
}
```

---

## 模块依赖

该表列出了使用 USDSchemas 模块时需要依赖的**独有**模块（省略标准 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `USDStage` | 提供 `UE::FUsdStage`、`UE::FUsdPrim` 等 USD 场景对象包装 |
| `USDUtilities` | 提供 `FUsdSchemaTranslatorRegistry`、`FUsdInfoCache`、`FUsdPrimLinkCache` 等基础工具 |
| `USDClasses` | 提供编辑器环境下的资源创建和组件操作工具 |
| `USDCore` | 提供 USD SDK 集成（`USDIncludesStart.h`、`pxr/pxr.h` 等） |
| `GeometryCache` | 可选，用于 `FUsdGeometryCacheTranslator` |
| `AlembicLibrary` | 可选，用于几何缓存解码 |

---

## 维护状态

### 近期更新

- 2025-10-22 a1039b21 USD: Disabled UE allocator in USD for Windows.
- 2025-10-17 be609b71 [Backout] - CL47041219
- 2025-10-17 7ab79237 USD: Disabled UE allocator in USD for Windows.
- 2025-10-03 d887bd60 USD: Use the default collision profile for generated static meshes.
- 2025-10-01 b4449c58 Anim In Engine: Fix broken linked anim sequences.（不直接相关）

### 维护评价

- **创建时间**：2025-10-01，至今不足一个月，属于全新插件。
- **近期更新频率**：在 2025 年 10 月有多次提交，包括功能修复和配置调整，显示活跃开发。
- **实验性状态**：`.uplugin` 中标记为 `IsBetaVersion: true`，意味着 API 可能不稳定，适合尝试但不宜用于生产。
- **已知限制**：部分类已 deprecated（如 `FUsdSkelRootTranslator` 迁移至 `UsdSkelSkeletonTranslator`），`InfoCache` 和 `PrimLinkCache` 已移至 `USDUtilities` 模块，说明代码仍在重构中。
- **推荐使用**：如果项目需要 USD 导入能力且不介意实验性标签，该模块提供了完整且强大的转换框架。建议同时关注其上游依赖模块的稳定性。适合 UE5 开发早期评估和原型开发。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDImporter)
- [官方文档](https://docs.unrealengine.com/5.7/WorkingWithUSD/)（社区建议）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDImporter/Source/USDTests)