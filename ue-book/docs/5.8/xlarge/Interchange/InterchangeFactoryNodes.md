# Interchange Framework

> The Interchange Framework plugin offers a customizable import and export system, with an extensible set of pipelines for handling common file types.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 通用资产交换框架 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `InterchangeAnalytics` (Runtime), `InterchangeCommon` (Runtime), `InterchangeDispatcher` (Runtime), `InterchangeExport` (Runtime), `InterchangeFactoryNodes` (Runtime), `InterchangeImport` (Runtime), `InterchangeMessages` (Runtime), `InterchangeNodes` (Runtime), `InterchangeCommonParser` (Runtime), `InterchangeFbxParser` (Runtime), `GLTFCore` (Runtime), `InterchangePipelines` (Runtime), `Draco` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-07-28 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Runtime) | |

---

**文档说明**：Interchange 框架是一个超大型插件（753 个源文件，13 个模块），本文档聚焦于 **InterchangeFactoryNodes** 模块，它是整个框架中负责定义"如何创建资产"的核心模块。其他模块（解析器、管线、节点等）的文档请参见后续专题。

---

## 用途

Interchange Framework 是 UE5 的新一代资产导入/导出框架，旨在取代 UnrealEd 中旧有的硬编码导入逻辑。它通过**节点图（Node Graph）**的方式描述资产数据，再由**工厂节点（Factory Nodes）**将这些数据转化为实际的 UE 资产。

**InterchangeFactoryNodes** 模块定义了所有工厂节点类——它们是整个导入流程中"最后一步"的关键角色。每种资产类型（静态网格、骨骼网格、材质、纹理、动画序列、相机、灯光等）都有对应的工厂节点类，携带该资产类型所需的全部自定义属性。

**核心设计思想**：
- **数据与创建分离**：翻译器（Translator）生成节点图，管线（Pipeline）修改节点图，工厂节点（Factory Node）负责创建最终资产
- **属性驱动**：每个工厂节点通过键值对（Attribute Key）存储属性，支持序列化、蓝图访问、编辑器 UI 展示
- **委托模式**：Set 函数支持 `bAddApplyDelegate` 参数，在工厂创建资产时自动将属性值写入对应 UObject 属性

## 使用场景

| 场景 | 说明 |
|---|---|
| 自定义导入管线 | 你需要在导入 FBX/glTF 时修改网格的特定属性 → 通过管线访问工厂节点的 `Get/Set` 方法 |
| 批量资产导入工具 | 你需要在蓝图中构建自定义导入流程 → 使用 `UInterchangeStaticMeshFactoryNode` 等蓝图类 |
| 导入设置编辑器 UI | 你需要在导入对话框中展示/修改资产设置 → 工厂节点的属性自动映射到编辑器 UI |
| 运行时资产加载 | 你需要在打包游戏中动态导入资产 → 使用 `IsRuntimeImportAllowed()` 为 true 的工厂节点 |
| 多格式支持 | 你需要统一处理 FBX、glTF、USD 等不同格式的相机/灯光导入 → 使用 `UInterchangeBaseCameraFactoryNode` 等基类 |

## 蓝图用法

所有工厂节点类均标记为 `BlueprintType`，可在蓝图中完全访问。

### 核心节点 — 网格工厂

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetCustomVertexColorReplace` / `Set` | 查询/设置是否替换顶点颜色 | `UInterchangeMeshFactoryNode` |
| `GetCustomVertexColorIgnore` / `Set` | 查询/设置是否忽略顶点颜色 | `UInterchangeMeshFactoryNode` |
| `GetCustomRecomputeNormals` / `Set` | 查询/设置是否重新计算法线 | `UInterchangeMeshFactoryNode` |
| `GetCustomRecomputeTangents` / `Set` | 查询/设置是否重新计算切线 | `UInterchangeMeshFactoryNode` |
| `GetCustomUseMikkTSpace` / `Set` | 查询/设置是否使用 MikkTSpace | `UInterchangeMeshFactoryNode` |
| `GetSlotMaterialDependencyUid` / `Set` | 获取/设置插槽材质依赖 | `UInterchangeMeshFactoryNode` |
| `GetLodDataCount` / `AddLodDataUniqueId` | 管理 LOD 数据 | `UInterchangeMeshFactoryNode` |
| `GetCustomBuildNanite` / `Set` | 查询/设置是否构建 Nanite | `UInterchangeStaticMeshFactoryNode` |
| `GetCustomAutoComputeLODScreenSizes` / `Set` | 自动计算 LOD 屏幕尺寸 | `UInterchangeStaticMeshFactoryNode` |
| `GetCustomGenerateLightmapUVs` / `Set` | 是否生成光照贴图 UV | `UInterchangeStaticMeshFactoryNode` |
| `InitializeSkeletalMeshNode` | 初始化骨骼网格节点 | `UInterchangeSkeletalMeshFactoryNode` |
| `GetCustomImportMorphTarget` / `Set` | 是否导入变形目标 | `UInterchangeSkeletalMeshFactoryNode` |
| `GetCustomImportContentType` / `Set` | 导入内容类型（几何体/蒙皮/全部） | `UInterchangeSkeletalMeshFactoryNode` |

### 核心节点 — 材质工厂

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ConnectToBaseColor` / `GetBaseColorConnection` | 连接基础颜色输入 | `UInterchangeMaterialFactoryNode` |
| `ConnectToNormal` / `GetNormalConnection` | 连接法线输入 | `UInterchangeMaterialFactoryNode` |
| `ConnectToRoughness` / `GetRoughnessConnection` | 连接粗糙度输入 | `UInterchangeMaterialFactoryNode` |
| `ConnectToMetallic` / `GetMetallicConnection` | 连接金属度输入 | `UInterchangeMaterialFactoryNode` |
| `ConnectToEmissiveColor` | 连接自发光颜色 | `UInterchangeMaterialFactoryNode` |
| `SetCustomShadingModel` | 设置着色模型 | `UInterchangeMaterialFactoryNode` |
| `SetCustomBlendMode` | 设置混合模式 | `UInterchangeMaterialFactoryNode` |

### 核心节点 — 动画工厂

| 节点 | 说明 | 所在类 |
|---|---|---|
| `InitializeAnimSequenceNode` | 初始化动画序列节点 | `UInterchangeAnimSequenceFactoryNode` |
| `GetCustomImportBoneTracks` / `Set` | 是否导入骨骼轨道 | `UInterchangeAnimSequenceFactoryNode` |
| `GetCustomImportBoneTracksSampleRate` / `Set` | 骨骼轨道采样率 | `UInterchangeAnimSequenceFactoryNode` |
| `GetCustomImportAttributeCurves` / `Set` | 是否导入属性曲线 | `UInterchangeAnimSequenceFactoryNode` |
| `GetCustomSkeletonSoftObjectPath` / `Set` | 指定现有骨架 | `UInterchangeAnimSequenceFactoryNode` |

### 核心节点 — 纹理工厂

| 节点 | 说明 | 所在类 |
|---|---|---|
| `InitializeTextureNode` | 初始化纹理节点 | `UInterchangeTextureFactoryNode` |
| `GetCustomCompressionSettings` / `Set` | 压缩设置 | `UInterchangeTextureFactoryNode` |
| `GetCustomAddressX` / `Set` | X 轴寻址模式 | `UInterchangeTexture2DFactoryNode` |
| `SetSourceBlocks` / `GetSourceBlock` | UDIM 纹理块管理 | `UInterchangeTexture2DFactoryNode` |

### 使用示例（蓝图描述）

**场景：在蓝图导入管线中设置静态网格的 Nanite 属性**

1. 使用 `GetFactoryNode` 节点获取 `UInterchangeStaticMeshFactoryNode` 对象
2. 调用 `SetCustomBuildNanite(True)` 启用 Nanite
3. 调用 `SetCustomNanitePositionPrecision(8)` 设置位置精度
4. 调用 `SetCustomNaniteExplicitTangents(True)` 启用显式切线

**场景：在蓝图中连接材质输入**

1. 获取 `UInterchangeMaterialFactoryNode` 对象
2. 调用 `ConnectToBaseColor("TextureExpressionNodeUid")` 将纹理表达式连接到基础颜色
3. 调用 `ConnectToNormal("NormalMapExpressionNodeUid")` 连接法线贴图

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeFactoryNodesModule.h"
#include "InterchangeStaticMeshFactoryNode.h"
#include "InterchangeSkeletalMeshFactoryNode.h"
#include "InterchangeMaterialFactoryNode.h"
#include "InterchangeAnimSequenceFactoryNode.h"
#include "InterchangeTexture2DFactoryNode.h"
```

### 基本用法

**创建并配置一个静态网格工厂节点**（来源：`InterchangeStaticMeshFactoryNode.h`）

```cpp
// 创建静态网格工厂节点并添加到节点容器
UInterchangeStaticMeshFactoryNode* StaticMeshFactoryNode = NewObject<UInterchangeStaticMeshFactoryNode>(NodeContainer);
StaticMeshFactoryNode->InitializeStaticMeshNode(
    TEXT("UniqueMeshId"),
    TEXT("MyStaticMesh"),
    UStaticMesh::StaticClass()->GetPathName(),
    NodeContainer
);

// 配置导入选项
StaticMeshFactoryNode->SetCustomBuildNanite(true);
StaticMeshFactoryNode->SetCustomAutoComputeLODScreenSizes(true);
StaticMeshFactoryNode->SetCustomGenerateLightmapUVs(true);
StaticMeshFactoryNode->SetCustomRecomputeNormals(false, true); // false = 不重算, true = 添加委托

// 设置插槽材质依赖
StaticMeshFactoryNode->SetSlotMaterialDependencyUid(TEXT("slot_0"), TEXT("MaterialNodeUid_0"));
```

**创建骨骼网格工厂节点**（来源：`InterchangeSkeletalMeshFactoryNode.h`）

```cpp
UInterchangeSkeletalMeshFactoryNode* SkelMeshNode = NewObject<UInterchangeSkeletalMeshFactoryNode>(NodeContainer);
SkelMeshNode->InitializeSkeletalMeshNode(
    TEXT("UniqueSkelMeshId"),
    TEXT("MySkeletalMesh"),
    USkeletalMesh::StaticClass()->GetPathName(),
    NodeContainer
);

// 配置骨骼网格导入选项
SkelMeshNode->SetCustomImportMorphTarget(true);
SkelMeshNode->SetCustomImportContentType(EInterchangeSkeletalMeshContentType::All);
SkelMeshNode->SetCustomCreatePhysicsAsset(true);
SkelMeshNode->SetCustomUseHighPrecisionSkinWeights(true);
SkelMeshNode->SetCustomBoneInfluenceLimit(8);

// 指定现有骨架（而非导入新骨架）
FSoftObjectPath SkeletonPath(TEXT("/Game/Characters/Mannequin/UE5_Mannequin_Skeleton.UE5_Mannequin_Skeleton"));
SkelMeshNode->SetCustomSkeletonSoftObjectPath(SkeletonPath);
```

### 进阶用法

**创建材质工厂节点并连接节点图**（来源：`InterchangeMaterialFactoryNode.h`）

```cpp
// 创建材质工厂节点
UInterchangeMaterialFactoryNode* MaterialNode = NewObject<UInterchangeMaterialFactoryNode>(NodeContainer);
MaterialNode->InitializeMaterialNode(TEXT("MatNode_001"), TEXT("PBR_Material"), NodeContainer);

// 设置材质属性
MaterialNode->SetCustomShadingModel(MSM_DefaultLit);
MaterialNode->SetCustomBlendMode(BLEND_Opaque);
MaterialNode->SetCustomTwoSided(false);

// 连接材质输入（连接到翻译器生成的表达式节点）
MaterialNode->ConnectToBaseColor(TEXT("TextureExpr_Albedo"));
MaterialNode->ConnectToNormal(TEXT("TextureExpr_Normal"));
MaterialNode->ConnectToRoughness(TEXT("ScalarExpr_Roughness"));
MaterialNode->ConnectToMetallic(TEXT("ScalarExpr_Metallic"));
MaterialNode->ConnectToEmissiveColor(TEXT("TextureExpr_Emissive"));

// 使用带输出名的连接（当表达式有多个输出时）
MaterialNode->ConnectOutputToBaseColor(TEXT("TextureExpr_ChannelPack"), TEXT("R"));  // 使用 R 通道
```

**创建动画序列工厂节点并配置曲线导入**（来源：`InterchangeAnimSequenceFactoryNode.h`）

```cpp
UInterchangeAnimSequenceFactoryNode* AnimNode = NewObject<UInterchangeAnimSequenceFactoryNode>(NodeContainer);
AnimNode->InitializeAnimSequenceNode(TEXT("AnimNode_001"), TEXT("Walk_Cycle"), NodeContainer);

// 关联骨架
AnimNode->SetCustomSkeletonFactoryNodeUid(TEXT("SkeletonNode_001"));

// 配置骨骼轨道导入
AnimNode->SetCustomImportBoneTracks(true);
AnimNode->SetCustomImportBoneTracksSampleRate(30.0);
AnimNode->SetCustomImportBoneTracksRangeStart(0.0);
AnimNode->SetCustomImportBoneTracksRangeStop(2.0);  // 只导入前 2 秒

// 配置曲线导入
AnimNode->SetCustomImportAttributeCurves(true);
AnimNode->SetCustomDoNotImportCurveWithZero(true);    // 跳过全零曲线
AnimNode->SetCustomRemoveCurveRedundantKeys(true);    // 移除冗余关键帧

// 添加动画属性曲线
AnimNode->SetAnimatedAttributeCurveName(TEXT("CustomProp_Float"));

// 设置场景节点动画载荷键
TMap<FString, FString> PayloadKeyUids;
TMap<FString, uint8> PayloadKeyTypes;
PayloadKeyUids.Add(TEXT("BoneNode_Root"), TEXT("AnimPayload_Root"));
PayloadKeyTypes.Add(TEXT("BoneNode_Root"), 0);
AnimNode->SetAnimationPayloadKeysForSceneNodeUids(PayloadKeyUids, PayloadKeyTypes);
```

## Demo 示例

以下是一个完整的工厂节点使用示例，展示如何在自定义管线中创建并配置一个静态网格工厂节点。

### MyInterchangePipeline.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "InterchangePipelineBase.h"
#include "InterchangeStaticMeshFactoryNode.h"
#include "InterchangeBaseNodeContainer.h"
#include "MyInterchangePipeline.generated.h"

UCLASS(EditInlineNew, Category = "Interchange | Pipeline", meta = (DisplayName = "My Custom Pipeline"))
class MYGAME_API UMyInterchangePipeline : public UInterchangePipelineBase
{
    GENERATED_BODY()

public:
    /** 覆写管线执行函数 */
    virtual void ExecutePipeline(UInterchangeBaseNodeContainer* BaseNodeContainer,
                                  const TArray<UInterchangeSourceData*>& SourceDatas) override;

    virtual UClass* GetPipelineClass() const override;

    /** 启用 Nanite 的配置属性 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Import Settings")
    bool bEnableNanite = true;

    /** 是否重新计算法线 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Import Settings")
    bool bRecomputeNormals = false;
};
```

### MyInterchangePipeline.cpp

```cpp
#include "MyInterchangePipeline.h"
#include "InterchangeStaticMeshFactoryNode.h"
#include "InterchangeBaseNodeContainer.h"

void UMyInterchangePipeline::ExecutePipeline(UInterchangeBaseNodeContainer* BaseNodeContainer,
                                              const TArray<UInterchangeSourceData*>& SourceDatas)
{
    // 遍历所有工厂数据节点
    TArray<FString> FactoryNodeUids;
    BaseNodeContainer->GetFactoryNodeUids(FactoryNodeUids);

    for (const FString& NodeUid : FactoryNodeUids)
    {
        UInterchangeFactoryBaseNode* FactoryNode = BaseNodeContainer->GetFactoryNode(NodeUid);
        if (!FactoryNode)
        {
            continue;
        }

        // 只处理静态网格工厂节点
        if (UInterchangeStaticMeshFactoryNode* StaticMeshNode =
                Cast<UInterchangeStaticMeshFactoryNode>(FactoryNode))
        {
            // 设置 Nanite
            StaticMeshNode->SetCustomBuildNanite(bEnableNanite, true);

            // 设置法线重算
            StaticMeshNode->SetCustomRecomputeNormals(bRecomputeNormals, true);

            // 设置顶点颜色处理
            StaticMeshNode->SetCustomVertexColorReplace(false);
            StaticMeshNode->SetCustomVertexColorIgnore(false);

            // 启用 MikkTSpace 切线计算
            StaticMeshNode->SetCustomUseMikkTSpace(true, true);
            StaticMeshNode->SetCustomRecomputeTangents(true, true);

            // 生成光照贴图 UV
            StaticMeshNode->SetCustomGenerateLightmapUVs(true, true);

            // 移除退化三角形
            StaticMeshNode->SetCustomRemoveDegenerates(true, true);

            UE_LOG(LogTemp, Log, TEXT("Configured static mesh factory node: %s"),
                   *StaticMeshNode->GetDisplayLabel());
        }
    }
}

UClass* UMyInterchangePipeline::GetPipelineClass() const
{
    return UMyInterchangePipeline::StaticClass();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `InterchangeNodes` | 基础节点类（`UInterchangeBaseNode`、`UInterchangeFactoryBaseNode` 等） |
| `InterchangeCommon` | 公共类型定义（属性键、载荷类型等） |
| `InterchangeMessages` | 依赖 Engine 模块的消息系统 |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

**Build.cs 模块依赖**（InterchangeFactoryNodes）：
- `PublicDependencyModuleNames`: InterchangeNodes, InterchangeCommon
- `PrivateDependencyModuleNames`: Core, CoreUObject, Engine

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-25 | `61d0e791` | USD Pregen: Implement tracking of Skeleton and PhysicsAssets | USD 预生成模块新增骨架和物理资产追踪功能 |
| 2026-05-23 | `176334d2` | Fix localization warnings for UE 5.8 | 修复 UE 5.8 版本的本地化警告 |
| 2026-05-22 | `8fdd3a89` | [Interchange] Reset existing LODModels for reimport, so that Bone bindings and mappings are updated | 重导入时重置现有 LOD 模型以更新骨骼绑定 |
| 2026-05-22 | `3cfa4417` | Reinstated the uFBX parser as experimental | 恢复 uFBX 解析器为实验性功能 |
| 2026-05-19 | `755f95d4` | Interchange: Fix crash by protecting against nullptr objects in the list of imported objects. | 修复导入对象列表中空指针导致的崩溃 |

### 维护评价

- **活跃程度**：活跃维护中。最近更新集中在 2026 年 5 月，距今不到 1 个月，包含功能增强和 Bug 修复
- **迭代速度**：高频更新，近期涉及 USD 集成、FBX 解析器、LOD 重导入等核心功能
- **成熟度**：该框架仍在快速演进中，标记为实验性（IsBetaVersion），API 可能在未来版本有变化
- **已知限制**：
  - `.uplugin` 中标记为实验性版本
  - 部分工厂节点（如 `UInterchangeSkeletalMeshFactoryNode`）不支持运行时导入
  - 存在大量 `UE_DEPRECATED(5.8, ...)` 标记的旧 API，建议使用新版本
- **推荐使用**：✅ 推荐。这是 Epic 官方主推的新一代导入框架，替代旧的 UFactory 系统。虽然仍在实验阶段，但已是默认启用的核心插件，建议新项目优先采用

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Runtime)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/interchange-framework-in-unreal-engine/)（UE 官方文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Tests)（自动化测试）

---

## 附录：FactoryNodes 类层次结构

```
UInterchangeFactoryBaseNode
├── UInterchangeMeshFactoryNode (Abstract)
│   ├── UInterchangeStaticMeshFactoryNode
│   ├── UInterchangeSkeletalMeshFactoryNode
│   └── UInterchangeGeometryCacheFactoryNode
├── UInterchangeBaseMaterialFactoryNode (Abstract)
│   ├── UInterchangeMaterialFactoryNode
│   ├── UInterchangeMaterialInstanceFactoryNode
│   ├── UInterchangeMaterialFunctionFactoryNode
│   ├── UInterchangeMaterialReferenceFactoryNode
│   └── UInterchangeDecalMaterialFactoryNode
├── UInterchangeMaterialExpressionFactoryNode
│   └── UInterchangeMaterialFunctionCallExpressionFactoryNode
├── UInterchangeActorFactoryNode
│   ├── UInterchangeBaseCameraFactoryNode
│   │   ├── UInterchangePhysicalCameraFactoryNode
│   │   └── UInterchangeStandardCameraFactoryNode
│   ├── UInterchangeBaseLightFactoryNode
│   │   ├── UInterchangeDirectionalLightFactoryNode
│   │   ├── UInterchangeLightFactoryNode
│   │   │   ├── UInterchangeRectLightFactoryNode
│   │   │   └── UInterchangePointLightFactoryNode
│   │   │       └── UInterchangeSpotLightFactoryNode
│   │   └── UInterchangeSkyLightFactoryNode
│   ├── UInterchangeMeshActorFactoryNode
│   ├── UInterchangeDecalActorFactoryNode
│   ├── UInterchangeHeterogeneousVolumeActorFactoryNode
│   └── UInterchangeLevelInstanceActorFactoryNode
├── UInterchangeTextureFactoryNode (Abstract)
│   ├── UInterchangeTexture2DFactoryNode
│   │   └── UInterchangeTextureLightProfileFactoryNode
│   ├── UInterchangeTexture2DArrayFactoryNode
│   ├── UInterchangeTextureCubeFactoryNode
│   ├── UInterchangeTextureCubeArrayFactoryNode
│   └── UInterchangeVolumeTextureFactoryNode
├── UInterchangeAnimSequenceFactoryNode
├── UInterchangeSkeletonFactoryNode
├── UInterchangePhysicsAssetFactoryNode
├── UInterchangeGroomFactoryNode
├── UInterchangeGroomCacheFactoryNode
├── UInterchangeGroomBindingFactoryNode
├── UInterchangeLevelFactoryNode
├── UInterchangeLevelSequenceFactoryNode
├── UInterchangeSceneVariantSetsFactoryNode
├── UInterchangeCommonPipelineDataFactoryNode
├── UInterchangeSpecularProfileFactoryNode
├── UInterchangeSparseVolumeTextureFactoryNode
├── UInterchangeSceneImportAssetFactoryNode
├── UInterchangeAudioSoundWaveFactoryNode
├── UInterchangeStaticMeshLodDataNode
├── UInterchangeSkeletalMeshLodDataNode
└── UInterchangeSceneComponentFactoryNode
    ├── UInterchangeInstancedStaticMeshComponentFactoryNode
    └── UInterchangeGroomComponentFactoryNode
```