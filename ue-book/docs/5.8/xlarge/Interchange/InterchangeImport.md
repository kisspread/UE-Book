# Interchange Framework

> The Interchange Framework plugin offers a customizable import and export system, with an extensible set of pipelines for handling common file types.

| 属性 | 值 |
|---|---|
| 中文名 | 数据交换框架 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（材质函数、材质模板） |
| 模块 | `InterchangeImport` (Runtime), `InterchangeExport` (Runtime), `InterchangeCommon` (Runtime), `InterchangeNodes` (Runtime), `InterchangeFactoryNodes` (Runtime), `InterchangePipelines` (Runtime), `InterchangeDispatcher` (Runtime), `InterchangeMessages` (Runtime), `InterchangeAnalytics` (Runtime), `InterchangeCommonParser` (Runtime), `InterchangeFbxParser` (Runtime), `GLTFCore` (Runtime), `Draco` (External) |
| 实验性 | 否 |
| 创建时间 | 2022-02-15 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Runtime) | |

## 用途

Interchange Framework 是 UE5 全新的资产导入/导出管道框架，旨在替代老旧的 `UFactory` 导入系统。它解决的核心问题是：**将"文件格式解析"与"资产创建"彻底解耦**。

传统导入流程中，每种文件格式的翻译逻辑和资产工厂逻辑耦合在同一个 UFactory 类中，导致扩展困难、无法异步化、难以复用。Interchange 将导入流程拆分为三层：

1. **Translator（翻译器）**：负责读取源文件（FBX、GLTF、OBJ 等），将其转换为通用的节点图（Node Container），同时提供 Payload 接口来按需返回重型数据（网格、纹理、动画）
2. **Pipeline（管线）**：负责对节点图进行过滤、修改和优化，决定最终导入哪些资产以及如何配置
3. **Factory（工厂）**：负责根据节点描述实际创建 UE 资产（StaticMesh、SkeletalMesh、Material、Texture 等）

这种分层设计支持：
- 多线程异步导入（Payload 数据可在后台线程加载）
- 格式解析器和资产工厂的独立扩展
- 统一的导入/重导入流程
- 内置 MaterialX 和 USD Pregen 支持

## 模块总览

| 模块 | 类型 | 职责 |
|---|---|---|
| `InterchangeImport` | Runtime | 导入系统核心：Translator、Factory、Payload 接口、MaterialX/GLTF/FBX 翻译器 |
| `InterchangeExport` | Runtime | 导出系统 |
| `InterchangeCommon` | Runtime | 公共类型和工具 |
| `InterchangeNodes` | Runtime | 通用节点定义（BaseNode、SceneNode、MeshNode 等） |
| `InterchangeFactoryNodes` | Runtime | 工厂节点定义（描述资产创建参数的节点类型） |
| `InterchangePipelines` | Runtime | 内置管线实现 |
| `InterchangeDispatcher` | Runtime | 跨进程调度器（用于 FBX Worker 导入） |
| `InterchangeMessages` | Runtime | 导入过程中的消息和日志 |
| `InterchangeAnalytics` | Runtime | 导入分析和遥测 |
| `InterchangeCommonParser` | Runtime | 通用解析器基础设施 |
| `InterchangeFbxParser` | Runtime | FBX SDK 封装解析器 |
| `GLTFCore` | Runtime | glTF 文件格式核心解析 |
| `Draco` | External | Draco 网格压缩第三方库 |

## 使用场景

- 你需要导入 FBX/glTF/OBJ 等 3D 模型文件 → Interchange 自动处理，通过 Pipeline 可自定义导入行为
- 你需要支持自定义文件格式（如专有资产格式）→ 实现自定义 Translator + Payload 接口
- 你需要批量导入大量资产并希望异步处理 → Interchange 原生支持异步 Payload 加载
- 你需要自定义材质导入逻辑（如 MaterialX 材质转 UE 材质）→ 使用 MaterialX 翻译器和材质工厂
- 你需要在导入时对资产图做复杂变换（如重命名、合并、过滤）→ 实现自定义 Pipeline

## 蓝图用法

Interchange 主要通过编辑器 UI（导入对话框）使用，运行时蓝图暴露有限。以下是可用的蓝图可访问 API：

### 翻译器设置

| 属性 | 说明 | 所在类 |
|---|---|---|
| `CoordinateSystemPolicy` | FBX 坐标系映射策略（匹配上下/前轴、匹配上轴、保持 XYZ） | `UInterchangeFbxTranslatorSettings` |
| `bConvertScene` | 是否将 FBX 场景轴系统转换为 UE 轴系统 | `UInterchangeFbxTranslatorSettings` |
| `bConvertSceneUnit` | 是否将 FBX 单位转换为 UE 单位（厘米） | `UInterchangeFbxTranslatorSettings` |
| `bKeepFbxNamespace` | 是否保留 FBX 命名空间 | `UInterchangeFbxTranslatorSettings` |
| `bUseUfbxParser` | 是否使用实验性的 uFBX 解析器替代 FBX SDK | `UInterchangeFbxTranslatorSettings` |

### 支持的文件格式

| 格式 | 翻译器 | 支持的资产类型 |
|---|---|---|
| `.fbx` | `UInterchangeFbxTranslator` | 网格、纹理、动画、骨骼 |
| `.gltf` / `.glb` | `UInterchangeGLTFTranslator` | 网格、纹理、动画、变体集、灯光配置 |
| `.obj` | `UInterchangeOBJTranslator` | 网格、纹理 |
| `.dds` | `UInterchangeDDSTranslator` | 纹理（含切片/UDIM） |
| `.jpg` / `.jpeg` | `UInterchangeJPGTranslator` | 纹理 |
| `.ue.jpg` | `UInterchangeUEJPEGTranslator` | 纹理（UE 专用压缩格式） |
| MaterialX | 内置翻译器 | 材质 |

### Payload 接口（蓝图不可直接调用，供 C++ 扩展）

| 接口 | 用途 |
|---|---|
| `IInterchangeTexturePayloadInterface` | 提供纹理像素数据 |
| `IInterchangeMeshPayloadInterface` | 提供网格几何数据（FMeshDescription） |
| `IInterchangeAnimationPayloadInterface` | 提供动画曲线和变换数据 |
| `IInterchangeAudioPayloadInterface` | 提供音频波形数据 |
| `IInterchangeVolumePayloadInterface` | 提供体积数据（如 OpenVDB） |
| `IInterchangeGroomPayloadInterface` | 提供 Groom（毛发）数据 |
| `IInterchangeVariantSetPayloadInterface` | 提供变体集数据 |
| `IInterchangeTextureLightProfilePayloadInterface` | 提供 IES 灯光配置数据 |
| `IInterchangeSlicedTexturePayloadInterface` | 提供切片纹理数据 |
| `IInterchangeBlockedTexturePayloadInterface` | 提供 UDIM 阻塞纹理数据 |
| `IInterchangeGenericPayloadInterface` | 通用 Payload 扩展（USD 等使用） |

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeImportModule.h"
#include "InterchangeTexturePayloadInterface.h"
#include "InterchangeMeshPayloadInterface.h"
#include "InterchangeAnimationPayloadInterface.h"
```

### 基本用法：检查模块可用性

```cpp
// 来源: Public/InterchangeImportModule.h
#include "InterchangeImportModule.h"

if (IInterchangeImportModule::IsAvailable())
{
    IInterchangeImportModule& ImportModule = IInterchangeImportModule::Get();
    
    // 检查 Substrate 支持
    bool bSubstrateEnabled = ImportModule.IsSubstrateEnabled();
    bool bAdaptiveGBuffer = ImportModule.IsSubstrateAdaptiveGBufferEnabled();
}
```

### 基本用法：自定义 Translator 获取纹理 Payload

```cpp
// 来源: Public/Texture/InterchangeTexturePayloadInterface.h
class UMyTranslator : public UInterchangeTranslatorBase, public IInterchangeTexturePayloadInterface
{
    GENERATED_BODY()
public:
    virtual TOptional<UE::Interchange::FImportImage> GetTexturePayloadData(
        const FString& PayloadKey, 
        TOptional<FString>& AlternateTexturePath) const override
    {
        // 根据 PayloadKey 加载纹理数据
        // 返回 FImportImage 包含像素数据
        TOptional<UE::Interchange::FImportImage> Result;
        // ... 加载实现
        return Result;
    }
    
    virtual bool SupportCompressedTexturePayloadData() const override { return true; }
    
    virtual TOptional<UE::Interchange::FImportImage> GetCompressedTexturePayloadData(
        const FString& PayloadKey, 
        TOptional<FString>& AlternateTexturePath) const override
    {
        // 返回原始压缩格式的纹理数据
        return {};
    }
};
```

### 基本用法：自定义 Translator 获取网格 Payload

```cpp
// 来源: Public/Mesh/InterchangeMeshPayloadInterface.h
class UMyMeshTranslator : public UInterchangeTranslatorBase, public IInterchangeMeshPayloadInterface
{
    GENERATED_BODY()
public:
    virtual TOptional<UE::Interchange::FMeshPayloadData> GetMeshPayloadData(
        const FInterchangeMeshPayLoadKey& PayLoadKey,
        const UE::Interchange::FAttributeStorage& PayloadAttributes) const override
    {
        // PayloadAttributes 包含 Pipeline 传递的参数，如 MeshGlobalTransform
        const FTransform* MeshGlobalTransform = PayloadAttributes.GetAttributePtr<FTransform>(
            UE::Interchange::FAttributeKey{ UE::Interchange::MeshPayload::Attributes::MeshGlobalTransform });
        
        // 根据 PayLoadKey 构建 FMeshDescription
        TOptional<UE::Interchange::FMeshPayloadData> Result;
        // ... 网格数据加载
        return Result;
    }
};
```

### 进阶用法：MaterialX 材质翻译

```cpp
// 来源: Public/MaterialX/MaterialXUtils/MaterialXManager.h
#if WITH_EDITOR
#include "MaterialXManager.h"

// 在翻译器中使用 MaterialX Manager 将 .mtlx 文件转换为 Interchange 节点
bool TranslateMaterialXFile(const FString& Filename, UInterchangeBaseNodeContainer& BaseNodeContainer)
{
    // MaterialX Manager 是单例，管理 MaterialX 节点到 UE 材质表达式的映射
    UE::Interchange::MaterialX::FMaterialXManager& Manager = 
        UE::Interchange::MaterialX::FMaterialXManager::GetInstance();
    
    // 检查材质函数包是否已加载（必须在游戏线程调用）
    if (!UE::Interchange::MaterialX::AreMaterialFunctionPackagesLoaded())
    {
        return false;
    }
    
    // 翻译 MaterialX 文件到节点容器
    bool bSuccess = Manager.Translate(Filename, BaseNodeContainer, /*Translator=*/nullptr);
    
    // 查找 MaterialX 节点类别对应的 UE 材质表达式
    const FString* MaterialExpr = Manager.FindMatchingMaterialExpression(
        TEXT("standard_surface"), /*NodeGroup=*/{}, /*Type=*/{});
    
    return bSuccess;
}
#endif
```

### 进阶用法：GLTF 材质处理

```cpp
// 来源: Public/Gltf/InterchangeGLTFMaterial.h
#include "InterchangeGLTFMaterial.h"

// GLTF 材质支持的着色模型
// DEFAULT (MetalRoughness), UNLIT, CLEARCOAT, SHEEN, TRANSMISSION, SPECULARGLOSSINESS

// 获取所需的材质函数路径
TArray<FString> RequiredPaths = UE::Interchange::GLTFMaterials::GetRequiredMaterialFunctionPaths();

// 检查材质函数包是否已加载
bool bLoaded = UE::Interchange::GLTFMaterials::AreRequiredPackagesLoaded();
```

### 进阶用法：网格碰撞导入辅助

```cpp
// 来源: Public/Mesh/InterchangeMeshHelper.h
#include "InterchangeMeshHelper.h"

// 使用 MeshHelper 进行网格碰撞导入
using namespace UE::Interchange::Private::MeshHelper;

// 从网格顶点生成凸包碰撞体
bool bSuccess = AddConvexGeomFromVertices(ImportArguments, MeshDescription, AggGeom);

// 从网格三角形生成盒体碰撞
bSuccess = AddBoxGeomFromTris(MeshDescription, AggGeom);

// 从网格顶点生成胶囊碰撞体
bSuccess = AddCapsuleGeomFromVertices(ImportArguments, MeshDescription, AggGeom);

// 根据名称前缀判断碰撞类型（UBX_, UCX_, USP_, UCP_ 等）
EInterchangeMeshCollision CollisionType = GetMeshCollisionFromName(MeshName);

// 计算场景节点的完整变换
FTransform CompleteTransform = CalculateCompleteSceneNodeTransform(
    BaseNodeContainer, SceneNode, bBakeMeshes, bBakePivots, GlobalOffsetTransform);
```

## Demo 示例

### 自定义纹理 Translator

```cpp
// MyTextureTranslator.h
#pragma once

#include "CoreMinimal.h"
#include "InterchangeTranslatorBase.h"
#include "InterchangeTexturePayloadInterface.h"
#include "MyTextureTranslator.generated.h"

UCLASS(MinimalAPI, BlueprintType)
class UMyTextureTranslator : public UInterchangeTranslatorBase,
                              public IInterchangeTexturePayloadInterface
{
    GENERATED_BODY()

public:
    // 声明支持的文件格式
    virtual TArray<FString> GetSupportedFormats() const override
    {
        return { TEXT(".mytex") };
    }

    virtual EInterchangeTranslatorAssetType GetSupportedAssetTypes() const override
    {
        return EInterchangeTranslatorAssetType::Textures;
    }

    virtual EInterchangeTranslatorType GetTranslatorType() const override
    {
        return EInterchangeTranslatorType::Textures;
    }

    // 将源文件翻译为节点图
    virtual bool Translate(UInterchangeBaseNodeContainer& BaseNodeContainer) const override;

    // 提供纹理像素数据给工厂使用
    virtual TOptional<UE::Interchange::FImportImage> GetTexturePayloadData(
        const FString& PayloadKey,
        TOptional<FString>& AlternateTexturePath) const override;
};
```

```cpp
// MyTextureTranslator.cpp
#include "MyTextureTranslator.h"
#include "InterchangeTextureNode.h"
#include "Nodes/InterchangeBaseNodeContainer.h"

bool UMyTextureTranslator::Translate(UInterchangeBaseNodeContainer& BaseNodeContainer) const
{
    // 获取源文件路径
    const UInterchangeSourceData* SourceData = GetSourceData();
    FString Filename = SourceData->GetFilename();

    // 创建纹理节点
    UInterchangeTexture2DNode* TextureNode = NewObject<UInterchangeTexture2DNode>(&BaseNodeContainer);
    
    FString NodeUID = TEXT("MyTexture_") + FPaths::GetBaseFilename(Filename);
    BaseNodeContainer.SetupNode(TextureNode, NodeUID, 
        FPaths::GetCleanFilename(Filename), EInterchangeNodeContainerType::TranslatedAsset);

    // 设置纹理属性
    TextureNode->SetPayLoadKey(Filename);
    TextureNode->SetCustomSRGB(true);
    TextureNode->SetCustomWrapU(EInterchangeTextureWrapMode::Wrap);
    TextureNode->SetCustomWrapV(EInterchangeTextureWrapMode::Wrap);

    return true;
}

TOptional<UE::Interchange::FImportImage> UMyTextureTranslator::GetTexturePayloadData(
    const FString& PayloadKey,
    TOptional<FString>& AlternateTexturePath) const
{
    // 根据 PayloadKey（即文件路径）加载自定义格式的纹理数据
    TArray64<uint8> RawData;
    if (!FFileHelper::LoadFileToArray(RawData, *PayloadKey))
    {
        return {};
    }

    // 解析自定义格式并转换为 FImportImage
    UE::Interchange::FImportImage ImportImage;
    // ... 解析逻辑
    // ImportImage.RawData = 解码后的像素数据;
    // ImportImage.SizeX = 宽度;
    // ImportImage.SizeY = 高度;
    // ImportImage.Format = ERGBFormat::BGRA8;

    return ImportImage;
}
```

## 模块依赖

`InterchangeImport` 模块的核心依赖（Build.cs 中提取）：

| 模块 | 用途 |
|---|---|
| `InterchangeNodes` | 通用 Interchange 节点类型定义 |
| `InterchangeFactoryNodes` | 工厂节点类型定义 |
| `InterchangeCommon` | 公共工具和类型 |
| `InterchangeMessages` | 导入消息和日志系统 |
| `InterchangePipelines` | 管线实现 |
| `InterchangeCommonParser` | 通用解析器基础 |
| `MeshDescription` | 网格描述数据结构 |
| `MaterialXCore` / `MaterialXFormat` | MaterialX 库封装 |
| `StaticMeshDescription` | 静态网格描述扩展 |
| `SkeletalMeshDescription` | 骨骼网格描述扩展 |
| `MeshUtilitiesCommon` | 网格工具 |
| `DatasmithContent` | Datasmith 内容支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-25 | `61d0e791` | USD Pregen: Implement tracking of Skeleton and PhysicsAssets | USD Pregen 实现骨骼和物理资产的追踪 |
| 2026-05-23 | `176334d2` | Fix localization warnings for UE 5.8 | 修复 UE 5.8 本地化警告 |
| 2026-05-22 | `8fdd3a89` | [Interchange] Reset existing LODModels for reimport, so that Bone bindings and mappings are updated | 重导入时重置 LODModels 以更新骨骼绑定和映射 |
| 2026-05-22 | `3cfa4417` | Reinstated the uFBX parser as experimental | 恢复 uFBX 解析器为实验性功能 |
| 2026-05-19 | `755f95d4` | Interchange: Fix crash by protecting against nullptr objects in the list of imported objects. | 修复导入对象列表中的空指针崩溃 |

### 维护评价

**活跃维护** — Interchange Framework 是 UE5 资产导入系统的核心替代方案，由 Epic 团队持续积极开发。

- **创建时间**：约 2022 年初，作为 UE5 全新导入管线引入
- **更新频率**：近期（2026 年 5 月）仍有密集的功能更新和 bug 修复，包括 USD Pregen 骨骼追踪、uFBX 解析器恢复、重导入逻辑改进等
- **模块规模**：753 个源文件，13 个子模块，属于超大型 plugin
- **实验性特性**：uFBX 解析器标记为实验性（`bUseUfbxParser`），MaterialX 和 MaterialX Fractal 节点仍标记为 Private
- **已知限制**：部分 MaterialX 表达式已废弃（如 `UMaterialExpressionMaterialXPlace2D` 在 5.5 废弃，建议使用材质函数 `MX_Place2D`）
- **推荐程度**：强烈推荐使用。Interchange 是 Epic 官方力推的下一代导入框架，已在 UE5 中默认启用，长期来看将逐步替代传统 `UFactory` 系统。对于自定义格式支持需求，Interchange 的 Translator + Pipeline + Factory 三层架构比传统方案更灵活、更易扩展。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Runtime)
- 官方文档（暂无链接）