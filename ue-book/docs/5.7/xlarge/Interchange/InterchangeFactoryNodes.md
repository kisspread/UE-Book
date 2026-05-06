# Interchange Factory Nodes

> The Interchange Framework plugin offers a customizable import and export system, with an extensible set of pipelines for handling common file types.

| 属性 | 值 |
|---|---|
| 中文名 | 导入工厂节点 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（工厂节点蓝图类） |
| 模块 | `InterchangeFactoryNodes` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-10-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Runtime/Source/FactoryNodes) | |

## 用途

Interchange Factory Nodes 是 Interchange 导入管线的关键组成部分。它们在导入流程中充当“配置项”的角色，定义了导入后每个资产（如静态网格体、骨骼网格体、材质、纹理、Actor等）应该具有的属性和行为。

每种工厂节点对应一种引擎资产类型，存储了从自定义管线或翻译器传来的全局/局部设置，例如：
- 是否启用 Nanite
- LOD 屏幕大小
- 材质颜色连接
- 全局偏移变换
- 碰撞体类型映射
- 纹理地址模式

最终由 Interchange 工厂系统根据这些节点数据创建或更新对应的 UObject。

## 使用场景

- 当你需要通过自定义 Pipeline（如修改 FBX 导入流程）来控制导入的参数时，可以创建并设置对应的工厂节点。
- 当你需要在蓝图或 C++ 中动态调整资产导入后属性（如光照贴图分辨率、骨骼网格体 UV 通道）时，可以直接操作工厂节点。
- 当你要实现自己的翻译器（Translator）时，需要生成这些工厂节点来告诉工厂系统如何生成资产。

## 蓝图用法

该类模块提供了大量 BlueprintCallable 函数，主要用于读取和设置工厂节点上的自定义属性。以下按资产类型分组列出常用节点类及核心操作。

### Actor 工厂节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetCustomGlobalTransform` / `SetCustomGlobalTransform` | 获取/设置全局变换 | `UInterchangeActorFactoryNode` |
| `GetCustomLocalTransform` / `SetCustomLocalTransform` | 获取/设置局部变换 | `UInterchangeActorFactoryNode` |
| `GetCustomComponentVisibility` / `SetCustomComponentVisibility` | 获取/设置组件可见性 | `UInterchangeActorFactoryNode` |
| `GetCustomActorVisibility` / `SetCustomActorVisibility` | 获取/设置 Actor 可见性 | `UInterchangeActorFactoryNode` |
| `GetCustomMobility` / `SetCustomMobility` | 获取/设置移动性（静态/可移动/固定） | `UInterchangeActorFactoryNode` |
| `AddComponentUid` / `GetComponentUids` | 添加/获取子组件 UID | `UInterchangeActorFactoryNode` |
| `AddLayerName` / `GetLayerNames` / `RemoveLayerName` | 管理 Actor 所属的层 | `UInterchangeActorFactoryNode` |

### 网格体工厂节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetCustomVertexColorReplace` / `SetCustomVertexColorReplace` | 控制是否替换顶点颜色 | `UInterchangeMeshFactoryNode` |
| `GetCustomVertexColorIgnore` / `SetCustomVertexColorIgnore` | 控制是否忽略顶点颜色 | `UInterchangeMeshFactoryNode` |
| `GetCustomVertexColorOverride` / `SetCustomVertexColorOverride` | 设置顶点颜色覆盖值 | `UInterchangeMeshFactoryNode` |
| `GetCustomKeepSectionsSeparate` / `SetCustomKeepSectionsSeparate` | 控制是否保持材质槽分离 | `UInterchangeMeshFactoryNode` |
| `GetLodDataCount` / `GetLodDataUniqueIds` | 获取 LOD 数据数量/唯一 ID | `UInterchangeMeshFactoryNode` |
| `AddLodDataUniqueId` / `RemoveLodDataUniqueId` | 管理 LOD 数据节点 UID | `UInterchangeMeshFactoryNode` |

#### 静态网格体特有

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetCustomBuildNanite` / `SetCustomBuildNanite` | 控制是否构建 Nanite | `UInterchangeStaticMeshFactoryNode` |
| `GetCustomAutoComputeLODScreenSizes` / `SetCustomAutoComputeLODScreenSizes` | 控制是否自动计算 LOD 屏幕大小 | `UInterchangeStaticMeshFactoryNode` |
| `GetLODScreenSizes` / `SetLODScreenSizes` | 获取/设置 LOD 屏幕大小数组 | `UInterchangeStaticMeshFactoryNode` |
| `GetSocketUidCount` / `GetSocketUids` | 管理 Socket UID | `UInterchangeStaticMeshFactoryNode` |

#### 骨骼网格体特有

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetCustomImportMorphTarget` / `SetCustomImportMorphTarget` | 控制是否导入变形目标 | `UInterchangeSkeletalMeshFactoryNode` |
| `GetCustomCreatePhysicsAsset` / `SetCustomCreatePhysicsAsset` | 控制是否创建物理资产 | `UInterchangeSkeletalMeshFactoryNode` |
| `GetCustomSkeletonSoftObjectPath` / `SetCustomSkeletonSoftObjectPath` | 获取/设置骨骼引用路径 | `UInterchangeSkeletalMeshFactoryNode` |

### 材质工厂节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetCustomIsMaterialImportEnabled` / `SetCustomIsMaterialImportEnabled` | 控制是否启用材料导入 | `UInterchangeBaseMaterialFactoryNode` |
| `ConnectToBaseColor` / `GetBaseColorConnection` | 连接/获取基础颜色输入 | `UInterchangeMaterialFactoryNode` |
| `ConnectToMetallic` / `GetMetallicConnection` | 连接/获取金属度输入 | `UInterchangeMaterialFactoryNode` |
| `ConnectToRoughness` / `GetRoughnessConnection` | 连接/获取粗糙度输入 | `UInterchangeMaterialFactoryNode` |
| `ConnectToNormal` / `GetNormalConnection` | 连接/获取法线输入 | `UInterchangeMaterialFactoryNode` |
| `ConnectToEmissiveColor` / `GetEmissiveColorConnection` | 连接/获取自发光颜色输入 | `UInterchangeMaterialFactoryNode` |

（所有材质输入均遵循类似的 `ConnectTo<Name>` / `Get<Name>Connection` 模式）

### 纹理工厂节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetCustomAdjustBrightness` / `SetCustomAdjustBrightness` | 调整亮度 | `UInterchangeTextureFactoryNode` |
| `GetCustomAdjustBrightnessCurve` / `SetCustomAdjustBrightnessCurve` | 调整亮度曲线 | `UInterchangeTextureFactoryNode` |
| `GetCustomAdjustVibrance` / `SetCustomAdjustVibrance` | 调整饱和度 | `UInterchangeTextureFactoryNode` |
| `GetCustomAdjustSaturation` / `SetCustomAdjustSaturation` | 调整色饱和度 | `UInterchangeTextureFactoryNode` |
| `GetCustomAdjustRGBCurve` / `SetCustomAdjustRGBCurve` | 调整 RGB 曲线 | `UInterchangeTextureFactoryNode` |
| `GetCustomAdjustHue` / `SetCustomAdjustHue` | 调整色相 | `UInterchangeTextureFactoryNode` |
| `GetCustomAdjustMinAlpha` / `SetCustomAdjustMinAlpha` | 调整最小 Alpha | `UInterchangeTextureFactoryNode` |
| `GetCustomAdjustMaxAlpha` / `SetCustomAdjustMaxAlpha` | 调整最大 Alpha | `UInterchangeTextureFactoryNode` |
| `GetCustomCompressionNoAlpha` / `SetCustomCompressionNoAlpha` | 控制是否压缩无 Alpha | `UInterchangeTextureFactoryNode` |
| `GetCustomCompressionQuality` / `SetCustomCompressionQuality` | 压缩质量 | `UInterchangeTextureFactoryNode` |
| `GetCustomTextureGroup` / `SetCustomTextureGroup` | 纹理组 | `UInterchangeTextureFactoryNode` |
| `GetCustomLODGroup` / `SetCustomLODGroup` | LOD 组 | `UInterchangeTextureFactoryNode` |
| `GetCustomPowerOfTwoMode` / `SetCustomPowerOfTwoMode` | 2 的幂模式 | `UInterchangeTextureFactoryNode` |
| `GetCustomPaddingColor` / `SetCustomPaddingColor` | 填充颜色 | `UInterchangeTextureFactoryNode` |
| `GetCustomMipGenSettings` / `SetCustomMipGenSettings` | Mip 生成设置 | `UInterchangeTextureFactoryNode` |

### 光线工厂节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetCustomLightColor` / `SetCustomLightColor` | 灯光颜色 | `UInterchangeBaseLightFactoryNode` |
| `GetCustomIntensity` / `SetCustomIntensity` | 强度 | `UInterchangeBaseLightFactoryNode` |
| `GetCustomTemperature` / `SetCustomTemperature` | 色温 | `UInterchangeBaseLightFactoryNode` |
| `GetCustomUseTemperature` / `SetCustomUseTemperature` | 是否使用色温 | `UInterchangeBaseLightFactoryNode` |

### 通用管线数据节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetCustomGlobalOffsetTransform` / `SetCustomGlobalOffsetTransform` | 全局偏移变换（用于调整场景原点） | `UInterchangeCommonPipelineDataFactoryNode` |
| `GetBakeMeshes` / `SetBakeMeshes` | 是否烘焙网格体变换 | `UInterchangeCommonPipelineDataFactoryNode` |
| `GetBakePivotMeshes` / `SetBakePivotMeshes` | 是否烘焙轴心点变换 | `UInterchangeCommonPipelineDataFactoryNode` |

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeActorFactoryNode.h"
#include "InterchangeStaticMeshFactoryNode.h"
#include "InterchangeSkeletalMeshFactoryNode.h"
#include "InterchangeMaterialFactoryNode.h"
#include "InterchangeTextureFactoryNode.h"
```

### 基本用法

以下示例展示如何在自定义 Pipeline 中创建工厂节点并设置属性。源码参考：`Engine/Plugins/Interchange/Runtime/Source/FactoryNodes/Private/InterchangeActorFactoryNode.cpp` 等。

```cpp
// 创建 Actor 工厂节点
UInterchangeActorFactoryNode* ActorNode = NewObject<UInterchangeActorFactoryNode>(NodeContainer);
ActorNode->InitializeNode(NodeContainer, "ActorUniqueID", "MyActor", EInterchangeNodeContainerType::FactoryData);

// 设置全局变换
FTransform GlobalTransform(FRotator(0, 90, 0), FVector(100, 0, 0), FVector::OneVector);
ActorNode->SetCustomGlobalTransform(GlobalTransform);

// 设置可见性
ActorNode->SetCustomActorVisibility(false);

// 添加组件
ActorNode->AddComponentUid("ComponentUID_001");
```

```cpp
// 创建静态网格体工厂节点
UInterchangeStaticMeshFactoryNode* MeshNode = NewObject<UInterchangeStaticMeshFactoryNode>(NodeContainer);
MeshNode->InitializeStaticMeshNode("MeshUniqueID", "MyMesh", TEXT("/Script/Engine.StaticMesh"), NodeContainer);

// 启用 Nanite
MeshNode->SetCustomBuildNanite(true);

// 设置 LOD 屏幕大小
TArray<float> ScreenSizes = { 1.0f, 0.5f, 0.2f };
MeshNode->SetLODScreenSizes(ScreenSizes);
```

```cpp
// 创建材质工厂节点并连接颜色
UInterchangeMaterialFactoryNode* MatNode = NewObject<UInterchangeMaterialFactoryNode>(NodeContainer);
MatNode->InitializeNode(NodeContainer, "MatUID", "MyMaterial", EInterchangeNodeContainerType::FactoryData);
MatNode->ConnectToBaseColor("TextureNodeUID");
```

### 进阶用法

工厂节点通常与 `UInterchangeBaseNodeContainer` 结合使用，在 Pipeline 的 `ExecutePipeline` 或 `PostPipeline` 阶段构建节点图，最终由 Factory 系统消费。

```cpp
// 在 Pipeline 中创建 LOD 数据节点并关联到网格体
UInterchangeStaticMeshLodDataNode* LodDataNode = NewObject<UInterchangeStaticMeshLodDataNode>(NodeContainer);
LodDataNode->InitializeNode(NodeContainer, "Lod0UID", "LOD0", EInterchangeNodeContainerType::FactoryData);
LodDataNode->AddMeshUid("SceneNodeMeshUID");

// 将 LOD 数据节点添加到网格体工厂节点
MeshNode->AddLodDataUniqueId("Lod0UID");
```

```cpp
// 使用通用管线数据节点设置全局偏移
UInterchangeCommonPipelineDataFactoryNode* CommonNode = UInterchangeCommonPipelineDataFactoryNode::FindOrCreateUniqueInstance(NodeContainer);
CommonNode->SetCustomGlobalOffsetTransform(NodeContainer, FTransform(FVector(0, 0, -100)));
CommonNode->SetBakeMeshes(true);
```

## Demo 示例

以下是一个完整的 C++ Pipeline 示例，演示如何创建工厂节点并设置属性。假设你的模块已经依赖了 `InterchangeFactoryNodes`。

**MyCustomPipeline.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "InterchangePipelineBase.h"
#include "InterchangeActorFactoryNode.h"
#include "InterchangeMeshFactoryNode.h"
#include "InterchangeStaticMeshFactoryNode.h"
#include "InterchangeCommonPipelineDataFactoryNode.h"
#include "MyCustomPipeline.generated.h"

UCLASS(BlueprintType)
class UMyCustomPipeline : public UInterchangePipelineBase
{
    GENERATED_BODY()

public:
    virtual void ExecutePipeline(UInterchangeBaseNodeContainer* NodeContainer, const TArray<UInterchangeSourceData*>& InSourceDatas) override
    {
        // 1. 设置全局偏移
        UInterchangeCommonPipelineDataFactoryNode* CommonNode = UInterchangeCommonPipelineDataFactoryNode::FindOrCreateUniqueInstance(NodeContainer);
        CommonNode->SetCustomGlobalOffsetTransform(NodeContainer, FTransform(FRotator(0, 90, 0), FVector::ZeroVector));
        CommonNode->SetBakeMeshes(true);

        // 2. 遍历容器中的网格体工厂节点
        TArray<UInterchangeStaticMeshFactoryNode*> MeshNodes;
        NodeContainer->GetNodes(UInterchangeStaticMeshFactoryNode::StaticClass(), MeshNodes);
        for (UInterchangeStaticMeshFactoryNode* MeshNode : MeshNodes)
        {
            // 启用 Nanite
            MeshNode->SetCustomBuildNanite(true);
            // 设置顶点颜色忽略
            MeshNode->SetCustomVertexColorIgnore(true);

            // 创建 LOD 数据节点并关联
            FString LodUid = MeshNode->GetUniqueID() + TEXT("_LOD0");
            UInterchangeStaticMeshLodDataNode* LodData = NewObject<UInterchangeStaticMeshLodDataNode>(NodeContainer);
            LodData->InitializeNode(NodeContainer, LodUid, TEXT("LOD0"), EInterchangeNodeContainerType::FactoryData);
            LodData->AddMeshUid(MeshNode->GetUniqueID()); // 将网格自身作为 LOD 源
            MeshNode->AddLodDataUniqueId(LodUid);
        }

        // 3. 遍历 Actor 工厂节点，设置所有 Actor 可见性为 true
        TArray<UInterchangeActorFactoryNode*> ActorNodes;
        NodeContainer->GetNodes(UInterchangeActorFactoryNode::StaticClass(), ActorNodes);
        for (UInterchangeActorFactoryNode* ActorNode : ActorNodes)
        {
            ActorNode->SetCustomActorVisibility(true);
        }
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `InterchangeCore` | 提供 Interchange 框架的基础设施（节点容器、属性系统） |
| `InterchangeNodes` | 提供基础节点类（如 `UInterchangeFactoryBaseNode`） |
| `Engine` | 需要引用引擎资产类（`UStaticMesh`, `USkeletalMesh` 等） |

无其他特殊依赖（标准 Core/CoreUObject 已省略）。

## 维护状态

### 近期更新

- 2025-12-18 `93cfc06e` 修复了包含骨骼网格体的关卡重新导入时编辑器挂起的问题
- 2025-10-23 `0158cf6a` [Interchange] 从命名 LOD 组中移除意外的 LOD 专业化
- 2025-10-21 `63c630c0` [Interchange] 修复了通过静态网格体导入 LevelSequence 时缺少动画序列的问题
- 2025-10-17 `765b3a10` 修复了非 Unity InterchangeWorker 的编译错误
- 2025-10-17 `2c91170f` 替换 PhongSurfaceMaterial 引用为 Interchange 内部材质

### 维护评价

- **创建时间**：2025-10-17（距今约 0.2 年）
- **最近更新频率**：2025 年 12 月仍有修复提交，更新活跃
- **活跃程度**：积极维护中，修复了实际使用中的崩溃和功能缺失
- **已知问题**：从 commit 看出存在 Lua 导入失败、着色器编译等历史问题，但已在不断修复
- **推荐使用**：✅ 推荐。作为 UE5 官方导入框架的核心模块，功能稳定且持续更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Runtime/Source/FactoryNodes)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/interchange-framework-in-unreal-engine/)（UE5.7 版本）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Tests)