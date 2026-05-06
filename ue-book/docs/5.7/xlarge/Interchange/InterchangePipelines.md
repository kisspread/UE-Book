# Interchange Framework

The Interchange Framework plugin offers a customizable import and export system, with an extensible set of pipelines for handling common file types.

| 属性 | 值 |
|---|---|
| 中文名 | 交换框架 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeCommon` (Runtime), `InterchangeDispatcher` (Runtime), `InterchangeExport` (Runtime), `InterchangeFactoryNodes` (Runtime), `InterchangeImport` (Runtime), `InterchangeMessages` (Runtime), `InterchangeNodes` (Runtime), `InterchangeCommonParser` (Runtime), `InterchangeFbxParser` (Runtime), `GLTFCore` (Runtime), `InterchangePipelines` (Runtime), `Draco` (External) |
| 实验性 | 否 |
| 创建时间 | 2025-10-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Runtime) | |

> **注意**：本文档聚焦于 **InterchangePipelines** 模块。该模块提供了一系列预设的导入管线（Pipeline），用于控制从中间数据到最终资产的转换过程。完整插件还包含解析器、工厂节点等模块，本文不展开。

## 用途

InterchangePipelines 模块解决了导入流程中的 **资产转换与配置** 问题。当其他模块（如 FBX 解析器、glTF 解析器）将源文件翻译为统一的中间节点图后，Pipeline 负责：

- 根据用户配置决定是否创建特定类型的资产（静态网格体、骨骼网格体、动画、纹理、材质等）。
- 处理诸如“合并静态网格体”、“强制网格体类型”、“导入动画区间”、“材质实例化”、“碰撞生成”、“纹理压缩”等复杂逻辑。
- 提供可扩展的基类 `UInterchangePipelineBase`，允许开发者编写自定义管线。
- 集成第三方格式（glTF、MaterialX）的特殊处理。

该模块是 Interchange 框架中 **面向用户** 的部分，大多数导入选项都来源于此。

## 使用场景

- **导入 FBX 模型**：使用 `UInterchangeGenericAssetsPipeline` 设置网格体、动画、材质选项。
- **导入 glTF 资产**：使用 `UInterchangeGLTFPipeline` 处理 glTF 特有的材质映射。
- **导入 MaterialX 材质**：使用 `UInterchangeMaterialXPipeline` 将 MaterialX 着色器转换为虚幻材质。
- **导入 Groom 毛发**：使用 `UInterchangeGenericGroomPipeline` 控制毛发导入参数。
- **导入音效文件**：使用 `UInterchangeGenericAudioPipeline` 创建 Sound Wave 资产。
- **场景导入**：使用 `UInterchangeGenericLevelPipeline` 将场景层级导入为关卡 Actor 或关卡实例。

## 蓝图用法

大多数管线属性直接暴露为 `BlueprintReadWrite`，可在蓝图或细节面板中配置。以下是可调用的核心蓝图函数：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Sound Wave Factory Node` | 为给定的音频节点创建工厂节点，并初始化路径和目标节点 | `UInterchangeGenericAudioPipeline` |
| `Get Mesh Instances` (静态方法) | 从节点容器获取所有网格体实例（含 LOD 信息） | `UE::Interchange::PipelineMeshesUtilities` |
| `Get Mesh Geometries` (静态方法) | 从节点容器获取所有网格体几何数据 | `UE::Interchange::PipelineMeshesUtilities` |

> 注：`UInterchangePipelineMeshesUtilities` 提供的辅助函数（如 `GetAllMeshInstance`、`GetAllMeshGeometry`）通常在 C++ 中使用，但可通过蓝图节点调用（若标记为 `BlueprintCallable`）。实际实现需要查看完整头文件。此处仅列举文件中明确标记的节点。

### 使用示例（蓝图描述）

1. **导入动画**  
   - 在导入对话框中选择 `Interchange Generic Assets Pipeline`。  
   - 展开“Animations”类别，勾选 `Import Animations`。  
   - 设置 `Animation Length` 为“Animated Time”以仅导入有动画的帧。  
   - 若需要 bake 为 30 FPS，勾选 `Use 30Hz To Bake Bone Animation`。

2. **导入静态网格体时生成碰撞**  
   - 在 `UInterchangeGenericMeshPipeline` 的“Static Meshes”类别下，确保 `Collision` 为 true。  
   - 勾选 `Import Collisions According To Mesh Name`，并按规范命名碰撞体（如 `UBX_`、`UCX_`）。

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeGenericAssetsPipeline.h"
#include "InterchangeGenericMeshPipeline.h"
#include "InterchangePipelineMeshesUtilities.h"
```

### 基本用法

以下示例演示如何在 C++ 中获取网格体实例信息（来自测试代码片段）：

```cpp
// 假设已有 UInterchangeBaseNodeContainer* NodeContainer 和 UInterchangePipelineMeshesUtilities* Utilities
#include "InterchangePipelineMeshesUtilities.h"

// 获取所有网格体实例
TArray<FInterchangeMeshInstance> MeshInstances;
Utilities->GetMeshInstances(NodeContainer, MeshInstances);

for (const FInterchangeMeshInstance& Instance : MeshInstances)
{
    // 检查是否为骨骼网格体
    if (Instance.bReferenceSkinnedMesh)
    {
        // 处理骨骼网格体场景节点
        for (const auto& LODPair : Instance.SceneNodePerLodIndex)
        {
            int32 LODIndex = LODPair.Key;
            for (const UInterchangeBaseNode* SceneNode : LODPair.Value.BaseNodes)
            {
                // 执行自定义处理
            }
        }
    }
}
```

> 来源：`Engine/Plugins/Interchange/Runtime/Source/Pipelines/Private/InterchangePipelineMeshesUtilities.cpp`

### 高级用法：自定义管线

创建自定义管线继承 `UInterchangePipelineBase`，重写 `ExecutePipeline`：

```cpp
// MyCustomPipeline.h
#include "InterchangePipelineBase.h"
#include "InterchangeGenericAssetsPipelineSharedSettings.h"
#include "MyCustomPipeline.generated.h"

UCLASS()
class UMyCustomPipeline : public UInterchangePipelineBase
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MySettings")
    bool bEnableFeatureX = true;

protected:
    virtual void ExecutePipeline(UInterchangeBaseNodeContainer* NodeContainer,
                                 const TArray<UInterchangeSourceData*>& SourceDatas,
                                 const FString& ContentBasePath) override
    {
        // 在此处理节点图，创建工厂节点等
        if (bEnableFeatureX)
        {
            // ... 自定义逻辑
        }
    }
};
```

## Demo 示例

以下是一个最小示例，展示如何通过 C++ 代码手动配置并使用通用资产管线：

> 注意：实际使用中管线通常由导入对话框自动创建，此示例仅用于演示 API 调用。

```cpp
// MyInterchangeDemo.h
#pragma once
#include "Modules/ModuleManager.h"
#include "InterchangeGenericAssetsPipeline.h"
#include "InterchangeGenericAnimationPipeline.h"
#include "InterchangeGenericMeshPipeline.h"

class FMyInterchangeDemo
{
public:
    void RunImport();
};

// MyInterchangeDemo.cpp
#include "MyInterchangeDemo.h"
#include "InterchangeManager.h"
#include "InterchangeSourceData.h"
#include "Nodes/InterchangeBaseNodeContainer.h"

void FMyInterchangeDemo::RunImport()
{
    // 1. 创建源数据
    UInterchangeSourceData* SourceData = UInterchangeManager::GetInterchangeManager()->CreateSourceData(TEXT("C:/MyModel.fbx"));
    if (!SourceData) return;

    // 2. 创建资产管线
    UInterchangeGenericAssetsPipeline* AssetsPipeline = NewObject<UInterchangeGenericAssetsPipeline>();
    AssetsPipeline->bUseSourceNameForAsset = true;
    AssetsPipeline->bAssetTypeSubFolders = false;

    // 配置网格体子管线
    UInterchangeGenericMeshPipeline* MeshPipeline = AssetsPipeline->MeshPipeline;
    MeshPipeline->bImportStaticMeshes = true;
    MeshPipeline->bCombineStaticMeshes = false;
    MeshPipeline->bCollision = true;

    // 配置动画子管线
    UInterchangeGenericAnimationPipeline* AnimPipeline = AssetsPipeline->AnimationPipeline;
    AnimPipeline->bImportAnimations = true;
    AnimPipeline->bImportBoneTracks = true;
    AnimPipeline->AnimationRange = EInterchangeAnimationRange::Animated;

    // 3. 执行导入
    TArray<UInterchangePipelineBase*> Pipelines = { AssetsPipeline };
    FString ContentPath = TEXT("/Game/MyImportedAssets");
    UInterchangeManager::GetInterchangeManager()->ImportAsset(ContentPath, SourceData, Pipelines);
}
```

## 模块依赖

使用 `InterchangePipelines` 模块时，你的模块需要依赖以下模块（已省略标准 Core/Engine 等）：

| 模块 | 用途 |
|---|---|
| `InterchangeCore` | 提供基础节点容器和节点类型 |
| `InterchangeFactoryNodes` | 提供各类工厂节点（如静态网格体工厂节点） |
| `InterchangeNodes` | 提供中间节点类型（如 ShaderGraphNode） |
| `InterchangeCommon` | 提供通用数据类型和枚举 |
| `InterchangeImport` | 提供导入管理器和翻译器接口 |

> 注：实际依赖关系可能在 `InterchangePipelines.Build.cs` 中定义。上述为根据公开头文件推断的常见依赖。

## 维护状态

### 近期更新

- 2025-12-18 `93cfc06e` 修复了包含骨骼网格体的文件进行关卡重新导入时编辑器挂起的问题  
- 2025-10-23 `0158cf6a` 移除了命名 LOD 组中意外的 LOD 特化  
- 2025-10-21 `63c630c0` 修复了静态网格体导入时缺少关卡序列动画的问题  
- 2025-10-17 `765b3a10` 修复了非 Unity 编译环境下 InterchangeWorker 的编译错误  
- 2025-10-17 `2c91170f` 替换了对硬编码材质引用的使用，改为动态加载

### 维护评价

- **创建时间**：2025 年 10 月（全新插件）  
- **更新频率**：频繁，近三个月内有多项修复和功能更新  
- **活跃度**：高度活跃，官方仍持续投入维护  
- **稳定性**：虽为新插件，但已成为 UE5 默认导入框架，建议在项目中使用  
- **推荐度**：强烈推荐，Interchange 是下一代导入系统，未来将取代旧版 FBX 导入器。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Runtime)  
- [官方文档（暂无）]( )  
- [测试用例（本模块）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Runtime/Source/Pipelines/Private/Tests)（若存在）