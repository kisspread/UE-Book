# Interchange Framework

> The Interchange Framework plugin offers a customizable import and export system, with an extensible set of pipelines for handling common file types.

| 属性 | 值 |
|---|---|
| 中文名 | 交换框架 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、配置资产） |
| 模块 | `InterchangeAnalytics` (Runtime), `InterchangeCommon` (Runtime), `InterchangeDispatcher` (Runtime), `InterchangeExport` (Runtime), `InterchangeFactoryNodes` (Runtime), `InterchangeImport` (Runtime), `InterchangeMessages` (Runtime), `InterchangeNodes` (Runtime), `InterchangeCommonParser` (Runtime), `InterchangeFbxParser` (Runtime), `GLTFCore` (Runtime), `InterchangePipelines` (Runtime), `Draco` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-03-01 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Runtime) | |

---

## 用途

Interchange Framework 是 UE5 的**新一代资产导入导出框架**，旨在替代旧版的 UFactory 导入系统。它解决的核心问题是：

1. **导入流程标准化**：旧版导入系统将翻译（解析文件格式）、工厂（创建 UE 资产）、后处理混杂在一起，难以扩展和维护。Interchange 将导入流程拆分为三个清晰的阶段：**Translator**（翻译器，解析源文件为中间节点图）→ **Pipeline**（管线，操作中间节点图、创建工厂节点）→ **Factory**（工厂，根据工厂节点创建实际资产）。

2. **多格式统一处理**：支持 FBX、glTF、USD、MaterialX 等多种源格式，通过统一的中间节点表示（Interchange Nodes）实现格式无关的处理逻辑。

3. **可定制的导入管线**：用户可以组合、替换或创建自定义 Pipeline，控制导入行为的每个环节——从网格合并策略、材质搜索范围到动画采样率等。

4. **重新导入（Reimport）支持**：内置冲突检测（材质冲突、骨骼冲突）、差异比较、保留编辑器修改等重新导入策略。

简而言之，Interchange 是 Epic 为 UE5 规划的**长期资产 IO 基础设施**，取代 FBX Importer 等旧插件，提供更灵活、更可扩展的资产导入导出能力。

---

## 使用场景

- **你从 DCC 工具（Maya/Blender/3ds Max）导入 FBX 模型和动画** → Interchange 自动解析 FBX，通过管线决定创建 StaticMesh 还是 SkeletalMesh、如何处理材质和 LOD
- **你需要导入 glTF 2.0 格式的资产** → Interchange 内置 glTF 翻译器和管线，支持 glTF 的材质模型（MetalRough、SpecGloss 等）
- **你需要从 MaterialX 文件导入材质** → `UInterchangeMaterialXPipeline` 处理 MaterialX 着色器图，映射到 UE 材质表达式
- **你需要自定义导入行为**（例如强制所有网格为 SkeletalMesh、自定义 LOD 策略、控制材质实例化） → 组合不同的 Pipeline 子类，或创建自定义 Pipeline
- **你需要批量重新导入资产并处理冲突** → `UInterchangeGenericAssetsPipeline` 内置材质冲突和骨骼冲突检测对话框
- **你需要导入毛发（Groom）资产** → `UInterchangeGenericGroomPipeline` 处理 Groom、GroomBinding、GroomCache
- **你需要将场景层次结构导入为关卡 Actor** → `UInterchangeGenericLevelPipeline` 支持创建 Level Actor、Level Instance Actor 或 Packed Level Actor
- **你需要导入音频文件** → `UInterchangeGenericAudioPipeline` 处理 SoundWave 资产

---

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateInterchangePipelineMeshesUtilities` | 创建网格管线工具实例，用于查询和操作翻译后的网格数据 | `UInterchangePipelineMeshesUtilities` |
| `GetAllMeshInstanceUids` | 获取所有网格实例的唯一 ID 列表 | `UInterchangePipelineMeshesUtilities` |
| `GetAllSkinnedMeshInstance` | 获取所有蒙皮网格实例的唯一 ID 列表 | `UInterchangePipelineMeshesUtilities` |
| `GetAllStaticMeshInstance` | 获取所有静态网格实例的唯一 ID 列表 | `UInterchangePipelineMeshesUtilities` |
| `GetAllGeometryCacheInstance` | 获取所有几何缓存实例的唯一 ID 列表 | `UInterchangePipelineMeshesUtilities` |
| `GetAllMeshGeometry` | 获取所有网格几何体的唯一 ID 列表 | `UInterchangePipelineMeshesUtilities` |
| `CreateSoundWaveFactoryNode` | 为 SoundWave 节点创建工厂节点 | `UInterchangeGenericAudioPipeline` |

### 管线属性（在导入对话框中可编辑）

所有 Pipeline 类的 `UPROPERTY(EditAnywhere, BlueprintReadWrite)` 属性都会在导入对话框中显示为可编辑选项。主要分组如下：

**通用属性（UInterchangeGenericAssetsPipeline）**：
- `PipelineDisplayName` — 管线显示名称
- `ReimportStrategy` — 重新导入策略
- `bUseSourceNameForAsset` — 使用源文件名作为资产名
- `bSceneNameSubFolder` — 使用场景名创建子文件夹
- `bAssetTypeSubFolders` — 按资产类型分文件夹
- `AssetName` — 自定义资产名称
- `ImportOffsetTranslation/Rotation/UniformScale` — 导入偏移

**网格属性（UInterchangeGenericMeshPipeline）**：
- `bImportStaticMeshes` / `bImportSkeletalMeshes` — 是否导入静态/骨骼网格
- `CombineStaticMeshesBehavior` — 静态网格合并策略
- `CombineSkeletalMeshesBehavior` — 骨骼网格合并策略
- `bBuildNanite` / `NaniteTriangleThreshold` — Nanite 配置
- `bImportMorphTargets` — 是否导入变形目标
- `bCreatePhysicsAsset` — 是否创建物理资产

**材质属性（UInterchangeGenericMaterialPipeline）**：
- `bImportMaterials` — 是否导入材质
- `bReuseExistingMaterials` — 是否复用已有材质
- `SearchLocation` — 材质搜索位置
- `MaterialImport` — 导入为材质还是材质实例
- `bIdentifyDuplicateMaterials` — 检测重复材质

**动画属性（UInterchangeGenericAnimationPipeline）**：
- `bImportAnimations` — 是否导入动画
- `AnimationRange` — 动画范围类型
- `bUse30HzToBakeBoneAnimation` — 是否强制 30Hz 采样
- `bImportCustomAttribute` — 是否导入自定义属性

### 使用示例（蓝图描述）

在蓝图中，通常不需要直接操作 Pipeline 对象，因为导入流程由编辑器的导入对话框驱动。但如果你想在运行时或脚本化流程中使用：

1. 创建一个 `UInterchangePipelineMeshesUtilities` 实例，传入已有的 `UInterchangeBaseNodeContainer`
2. 调用 `GetAllMeshInstanceUids` 获取所有网格实例
3. 调用 `IterateAllStaticMeshInstance` 遍历所有静态网格实例，检查 `FInterchangeMeshInstance` 的属性（如 `bIsVisible`、`bHasMorphTargets`）

---

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeGenericAssetsPipeline.h"
#include "InterchangeGenericMeshPipeline.h"
#include "InterchangeGenericMaterialPipeline.h"
#include "InterchangeGenericAnimationPipeline.h"
#include "InterchangePipelineMeshesUtilities.h"
#include "InterchangeGenericTexturePipeline.h"
#include "InterchangeGenericAudioPipeline.h"
```

### 基本用法 — 查询网格管线数据

```cpp
// 来源: InterchangePipelineMeshesUtilities.h
// 创建网格管线工具实例，用于分析翻译后的节点图

UInterchangePipelineMeshesUtilities* MeshUtilities = 
    UInterchangePipelineMeshesUtilities::CreateInterchangePipelineMeshesUtilities(BaseNodeContainer);

// 获取所有静态网格实例
TArray<FString> StaticMeshInstanceUids;
MeshUtilities->GetAllStaticMeshInstance(StaticMeshInstanceUids);

// 获取所有骨骼网格实例
TArray<FString> SkinnedMeshInstanceUids;
MeshUtilities->GetAllSkinnedMeshInstance(SkinnedMeshInstanceUids);

// 获取所有网格几何体
TArray<FString> MeshGeometryUids;
MeshUtilities->GetAllMeshGeometry(MeshGeometryUids);

// 使用 lambda 遍历所有网格实例
MeshUtilities->IterateAllMeshInstance([](const FInterchangeMeshInstance& MeshInstance)
{
    if (MeshInstance.bIsVisible)
    {
        // 处理可见的网格实例
        const UInterchangeBaseNode* InstancingNode = MeshInstance.InstancingNode;
        for (const FString& MeshGeomUid : MeshInstance.ReferencingMeshGeometryUids)
        {
            // 处理引用的网格几何体
        }
    }
});
```

### 基本用法 — 创建音频工厂节点

```cpp
// 来源: InterchangeGenericAudioPipeline.h
// 为 SoundWave 翻译节点创建对应的工厂节点

UInterchangeGenericAudioPipeline* AudioPipeline = NewObject<UInterchangeGenericAudioPipeline>();
UInterchangeAudioSoundWaveNode* SoundWaveNode = /* 从 BaseNodeContainer 获取 */;
UInterchangeAudioSoundWaveFactoryNode* FactoryNode = 
    AudioPipeline->CreateSoundWaveFactoryNode(SoundWaveNode);
```

### 进阶用法 — 自定义管线子类

```cpp
// 创建自定义的动画管线，继承 UInterchangeGenericAnimationPipeline
UCLASS()
class UMyCustomAnimationPipeline : public UInterchangeGenericAnimationPipeline
{
    GENERATED_BODY()

protected:
    virtual void ExecutePipeline(
        UInterchangeBaseNodeContainer* InBaseNodeContainer,
        const TArray<UInterchangeSourceData*>& InSourceDatas,
        const FString& ContentBasePath) override
    {
        // 自定义动画导入逻辑前，先调用父类
        Super::ExecutePipeline(InBaseNodeContainer, InSourceDatas, ContentBasePath);
        
        // 在此添加自定义处理逻辑
        // 例如：遍历 BaseNodeContainer 中的动画节点进行后处理
    }

    virtual void AdjustSettingsForContext(
        const FInterchangePipelineContextParams& ContextParams) override
    {
        Super::AdjustSettingsForContext(ContextParams);
        // 根据上下文调整设置，例如禁用某些选项
    }
};
```

### 进阶用法 — 使用网格几何体信息判断网格类型

```cpp
// 来源: InterchangePipelineMeshesUtilities.h - FInterchangeMeshGeometry
// 使用 MeshGeometry 的辅助方法判断网格特性

UInterchangePipelineMeshesUtilities* MeshUtilities = 
    UInterchangePipelineMeshesUtilities::CreateInterchangePipelineMeshesUtilities(BaseNodeContainer);

TArray<FString> AllMeshGeometryUids;
MeshUtilities->GetAllMeshGeometry(AllMeshGeometryUids);

for (const FString& GeomUid : AllMeshGeometryUids)
{
    // 获取几何体信息
    const FInterchangeMeshGeometry* Geometry = MeshUtilities->GetMeshGeometry(GeomUid);
    if (!Geometry) continue;
    
    if (Geometry->IsSkinnedMesh())
    {
        // 这是一个蒙皮网格
    }
    
    if (Geometry->IsMorphTarget())
    {
        // 这是一个变形目标
    }
    
    if (Geometry->HasAssemblyPartDependencies())
    {
        // 有 Nanite 装配部件依赖
        TArray<FString> Dependencies;
        Geometry->GetAssemblyPartDependencies(Dependencies);
    }
    
    if (Geometry->bIsReferencedBySkeleton)
    {
        // 被骨骼引用
    }
}
```

---

## Demo 示例

以下展示如何创建一个自定义管线，在导入时强制所有网格为静态网格：

```cpp
// MyCustomForceStaticMeshPipeline.h
#pragma once

#include "CoreMinimal.h"
#include "InterchangeGenericMeshPipeline.h"
#include "MyCustomForceStaticMeshPipeline.generated.h"

UCLASS(BlueprintType)
class MYPROJECT_API UMyCustomForceStaticMeshPipeline : public UInterchangeGenericMeshPipeline
{
    GENERATED_BODY()

public:
    UMyCustomForceStaticMeshPipeline()
    {
        // 默认配置：只导入静态网格
        bImportStaticMeshes = true;
        bImportSkeletalMeshes = false;
        CombineStaticMeshesBehavior = EInterchangeCombineStaticMeshesBehavior::All;
    }

protected:
    virtual void ExecutePipeline(
        UInterchangeBaseNodeContainer* InBaseNodeContainer,
        const TArray<UInterchangeSourceData*>& InSourceDatas,
        const FString& ContentBasePath) override
    {
        // 在父类处理之前，强制所有网格为静态网格类型
        // CommonMeshesProperties->ForceAllMeshAsType = EInterchangeForceMeshType::IFMT_StaticMesh;
        
        Super::ExecutePipeline(InBaseNodeContainer, InSourceDatas, ContentBasePath);
    }
};
```

```cpp
// MyCustomForceStaticMeshPipeline.cpp
#include "MyCustomForceStaticMeshPipeline.h"
```

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `HairStrandsCore` | Groom（毛发）资产导入支持 |
| `InterchangeCore` | Interchange 基础框架（节点、翻译器接口） |
| `InterchangeNodes` | 中间节点类型定义（SceneNode、MeshNode 等） |
| `InterchangeFactoryNodes` | 工厂节点类型定义（StaticMeshFactoryNode 等） |
| `InterchangeImport` | 导入核心逻辑（Translator、Factory） |

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-25 | `61d0e791` | USD Pregen: Implement tracking of Skeleton and PhysicsAssets | USD 预生成中实现骨骼和物理资产的跟踪功能 |
| 2026-05-23 | `176334d2` | Fix localization warnings for UE 5.8 | 修复 UE 5.8 中的本地化警告 |
| 2026-05-22 | `8fdd3a89` | [Interchange] Reset existing LODModels for reimport, so that Bone bindings and mappings are updated | 重新导入时重置 LOD 模型，确保骨骼绑定和映射正确更新 |
| 2026-05-22 | `3cfa4417` | Reinstated the uFBX parser as experimental | 恢复 uFBX 解析器为实验性功能 |
| 2026-05-19 | `755f95d4` | Interchange: Fix crash by protecting against nullptr objects in the list of imported objects. | 修复导入对象列表中空指针导致的崩溃 |

### 维护评价

- **活跃维护中**：最近一周内有多次提交，涵盖功能新增、Bug 修复和兼容性维护
- **持续进化**：正在进行 USD 支持扩展（Pregen）、FBX 解析器替换（uFBX parser 实验性恢复）
- **API 快速迭代**：源码中大量 5.8 版本的废弃标记（`UE_DEPRECATED(5.8, ...)`），说明 API 仍在频繁重构
- **模块化程度高**：13 个子模块分离关注点，便于独立扩展
- **⚠️ 注意**：`.uplugin` 中 `IsBetaVersion=true`，该插件仍处于 Beta 状态，API 可能在未来版本继续变动
- **推荐使用**：作为 Epic 官方力推的新一代导入系统，Interchange 已在 UE5 中默认启用。如果你正在开发新的导入相关功能，应优先基于 Interchange Pipeline 体系扩展，而非旧的 UFactory 体系。但需要注意其 API 稳定性仍在演进中。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Runtime)
- 官方文档：无（.uplugin 中 DocsURL 为空）