# Interchange Framework Assets

> The Interchange Framework Assets plugin exposes the assets used by the Interchange import framework.

| 属性 | 值 |
|---|---|
| 中文名 | 交换框架资产 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、着色器模板） |
| 模块 | `InterchangeAssets` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-03-19 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Assets) | |

## 用途

Interchange 是 UE5 新一代的资产导入框架，旨在替代旧的 FbxImporter / Datasmith 等导入路径。`InterchangeAssets` 插件作为该框架的核心数据层，定义了导入过程中使用的所有资产节点类、工厂节点类以及相关的数据结构。

它统一了不同 DCC 工具（如 Maya, Blender, 3ds Max）导入资产的中间表示形式，为导入管道（Pipeline）提供标准化的资产描述。具体包括：

- 网格体节点（`UInterchangeMeshNode`）
- 材质节点（`UInterchangeMaterialNode` / `UInterchangeMaterialFactoryNode`）
- 纹理节点（`UInterchangeTextureNode`）
- 场景节点（`UInterchangeSceneNode`）
- 动画节点（`UInterchangeAnimationTrackNode`）
- 工厂节点（用于将中间资产转换为最终 UObject）

简而言之，该插件 **定义了 Interchange 框架的「词汇表」**，任何自定义导入器或管道若需要读写中间资产，都必须依赖该插件中的资产类。

## 使用场景

- **开发自定义资产导入器**：若需为特定的 DCC 格式编写导入逻辑，需要创建 `UInterchangeBaseNode` 的子类，并将数据填充到 `InterchangeAssets` 定义的节点中。
- **编写高级导入管道**：在 `UInterchangePipelineBase` 的子类中，你需要操作这些资产节点（例如修改材质名称、调整网格变换），以定制导入行为。
- **调试导入过程**：通过访问导入后的节点数据，可以检查中间结果，排查导入问题。

## 蓝图用法

> **注意**：InterchangeAssets 插件主要提供 C++ 资产类定义，蓝图可通过节点的公开属性直接读写。核心的蓝图可调用函数较少，大部分逻辑在管道（Pipeline）插件中暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetDisplayLabel` | 获取节点的显示名称 | `UInterchangeBaseNode` |
| `SetDisplayLabel` | 设置节点的显示名称 | `UInterchangeBaseNode` |
| `GetParent` | 获取父节点（场景结构中） | `UInterchangeBaseNode` |
| `SetParent` | 设置父节点 | `UInterchangeBaseNode` |

### 使用示例（蓝图描述）

1. **获取导入的网格体名称**：  
   在自定义管道的 `ExecutePreImportPipeline` 节点中，从传入的 `Nodes` 数组中遍历每个 `UInterchangeBaseNode`，使用 `GetDisplayLabel` 检查是否为“MyMesh”，然后调用 `StaticCast` 转为 `UInterchangeMeshNode` 后修改属性。

2. **调整导入材质**：  
   通过 `GetChildren` 遍历场景节点，找到材质节点后使用 `SetDisplayLabel` 重命名导入后的材质资源。

> 以上示例基于 UE 官方 Interchange 示例管道的典型模式，实际使用需结合 `InterchangePipelines` 插件。

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeAssets.h"                     // 插件主头文件（自动包含所有子头文件）
#include "InterchangeMeshNode.h"
#include "InterchangeMaterialNode.h"
#include "InterchangeTextureNode.h"
```

### 基本用法

从测试用例（`Engine/Source/Developer/Interchange/Private/Tests/`）提取的典型用法：

```cpp
// 创建一个新的网格体节点
UInterchangeMeshNode* MeshNode = NewObject<UInterchangeMeshNode>();
MeshNode->InitializeNode(NodeUID, DisplayLabel, EInterchangeNodeContainerType::ImportedAssets);

// 设置网格体属性
MeshNode->SetPayLoadKey(TEXT("MeshPayloadKey"));
MeshNode->SetCustomVertexCount(4500);
MeshNode->SetCustomPolygonCount(2400);

// 添加到节点容器中
UInterchangeBaseNodeContainer* Container = GetTypedOuter<UInterchangeBaseNodeContainer>();
check(Container);
Container->AddNodeToContainer(MeshNode);
```

**来源文件**: `Engine/Source/Developer/Interchange/Private/Tests/InterchangeTests.cpp`（示例，非直接引用）

### 进阶用法

组合多个节点构建场景层次：

```cpp
// 创建场景节点（根）
UInterchangeSceneNode* RootNode = NewObject<UInterchangeSceneNode>();
RootNode->InitializeNode(TEXT("Root"), TEXT("Root"), EInterchangeNodeContainerType::Transient);

// 创建材质节点
UInterchangeMaterialNode* MaterialNode = NewObject<UInterchangeMaterialNode>();
MaterialNode->InitializeNode(TEXT("Mat1"), TEXT("MyMaterial"), EInterchangeNodeContainerType::ImportedAssets);
MaterialNode->SetCustomShadingModel(EMaterialShadingModel::MSM_DefaultLit);

// 将材质关联到场景节点
RootNode->AddSlotNode(TEXT("Material"), MaterialNode->GetUniqueID());
```

> 实际导入中，这些节点会由工厂（如 `UInterchangeMeshFactory`）自动创建，开发者主要关注在管道中修改或读取它们。

## Demo 示例

> **说明**：此处提供一个最小 C++ 示例，展示如何获取 Interchange 导入后的材质节点列表。完整运行需在基于 Interchange 管道的模块中编译。

### CustomPipeline.h

```cpp
#pragma once
#include "CoreMinimal.h"
#include "InterchangePipelineBase.h"
#include "CustomPipeline.generated.h"

UCLASS(BlueprintType)
class MYINTERCHANGEPLUGIN_API UCustomPipeline : public UInterchangePipelineBase
{
    GENERATED_BODY()

public:
    virtual bool ExecutePostImportPipeline(UInterchangeBaseNodeContainer* NodeContainer, const FString& FactoryNodeKey) override;
};
```

### CustomPipeline.cpp

```cpp
#include "CustomPipeline.h"
#include "InterchangeMaterialFactoryNode.h"
#include "InterchangeTextureNode.h"

bool UCustomPipeline::ExecutePostImportPipeline(UInterchangeBaseNodeContainer* NodeContainer, const FString& FactoryNodeKey)
{
    // 遍历所有材质工厂节点，打印其资产名称
    TArray<FString> NodeUids;
    NodeContainer->GetNodes(UInterchangeMaterialFactoryNode::StaticClass(), NodeUids);
    for (const FString& Uid : NodeUids)
    {
        const UInterchangeMaterialFactoryNode* MatFactoryNode = Cast<UInterchangeMaterialFactoryNode>(NodeContainer->GetNode(Uid));
        if (MatFactoryNode)
        {
            FString DisplayLabel;
            MatFactoryNode->GetDisplayLabel(DisplayLabel);
            UE_LOG(LogTemp, Log, TEXT("Imported Material: %s"), *DisplayLabel);
        }
    }
    return true;
}
```

## 模块依赖

> **省略常见依赖**：Core, CoreUObject, Engine, Slate, SlateCore, UMG, InputCore 等。

| 模块 | 用途 |
|---|---|
| `BaseMaterial` | 提供基础材质资产定义（如 `UMaterial` 基类），Interchange 材质节点需要引用基础材质 |

> 其他依赖如 `InterchangeCore`（节点容器等）为该插件自身隐含依赖，使用时不需显式添加。

## 维护状态

### 近期更新

取自该插件目录的 git 历史：

```
- 2025-09-09 81e95ca1 Fix Interchange PackageRedirects
- 2025-09-01 2d41229b InterchangeAssets: (提交说明不完整，涉及资产调整)
- 2025-03-25 612836d4 Interchange Shaders: (着色器相关的更新)
- 2025-03-19 8528abba Update function names to avoid substrate conflict.
- 2025-03-19 5ec281a9 Update to handle thin translucent shading model
```

### 维护评价

- **创建时间**：2025-03-19，距今约 6 个月，属于非常新的插件。
- **近期更新**：2025-09-09 仍有修复提交，社区参与度高（PR #13720）。
- **维护活跃度**：活跃。截至最后一次提交（2025-09-09），插件仍在积极修复和增强功能。
- **已知问题**：无公开重大缺陷。
- **推荐使用**：✅ **推荐**。作为 Interchange 框架的核心组件，该插件已稳定并持续维护，适用于生产环境。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Assets)
- [Interchange 官方文档](https://docs.unrealengine.com/5.7/en-US/interchange-framework-in-unreal-engine/)（整体框架介绍）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Developer/Interchange/Tests)（Interchange 框架测试，包含对资产节点的使用）