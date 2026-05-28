# Interchange FBX Parser

> The Interchange Framework plugin offers a customizable import and export system, with an extensible set of pipelines for handling common file types.

| 属性 | 值 |
|---|---|
| 中文名 | FBX 解析器 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeFbxParser` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 未知 |
| 年龄标签 | 未知 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Runtime/Source/Parsers/Fbx) | |

## 用途

Interchange FBX Parser 是 Interchange 框架的核心解析器模块之一，专门负责解析 Autodesk FBX (.fbx) 格式的文件。它将 FBX SDK 的数据结构（如 `FbxScene`, `FbxMesh`）转换为 Interchange 框架通用的节点容器 (`UInterchangeBaseNodeContainer`) 格式，并将几何体、材质、动画等资产数据作为“负载” (Payload) 提取出来。该模块提供了两种实现：基于 Epic 自研 FBX SDK 封装的 `FFbxParser`，以及基于第三方开源库 uFBX 的实验性 `FUfbxParser`，旨在为 FBX 文件导入提供高性能和全面的格式支持。

## 使用场景

- 你的项目需要从 DCC 工具（如 Maya, 3ds Max, Blender）导入 FBX 格式的静态网格体、骨骼网格体或动画。
- 你需要解析 FBX 文件中的材质、纹理、相机和灯光属性。
- 你正在开发或扩展自定义的资产导入流程，并希望利用 Interchange 框架的模块化架构来处理 FBX 文件。

## 蓝图用法

此模块主要为运行时 C++ 代码设计，提供底层的解析能力。它不包含直接暴露给蓝图的函数节点。对 FBX 的导入操作通常由更高层级的 `InterchangeImport` 模块或编辑器的导入流程触发。

## C++ 用法

核心交互通过 `UE::Interchange::FInterchangeFbxParser` 类进行。该类封装了底层的 `IFbxParser` 实现，提供了文件加载、场景解析和负载获取的完整流程。

### 头文件引入

```cpp
#include "InterchangeFbxParser.h"
```

### 基本用法

1.  **创建解析器实例并加载 FBX 文件**
    ```cpp
    // 创建 FBX 解析器实例
    UE::Interchange::FInterchangeFbxParser FbxParser;

    // 加载 FBX 文件并填充节点容器
    const FString FBXFilePath = TEXT("C:/Models/MyModel.fbx");
    FbxParser.LoadFbxFile(FBXFilePath, BaseNodeContainer);
    ```

2.  **获取场景和网格体负载**
    ```cpp
    // 从加载的 FBX 中获取一个特定网格体的负载数据
    const FString MeshPayloadKey = TEXT("SomeMeshUniqueID");
    const FTransform MeshTransform = FTransform::Identity;

    // 方法一：将负载数据写入临时文件（用于非内存导入）
    FbxParser.FetchMeshPayload(MeshPayloadKey, MeshTransform, ResultFolder);

    // 方法二：将负载数据直接读入内存结构（需要 WITH_ENGINE）
    UE::Interchange::FMeshPayloadData MeshData;
    if (FbxParser.FetchMeshPayload(MeshPayloadKey, MeshTransform, MeshData))
    {
        // 使用 MeshData (包含 FMeshDescription)
    }
    ```

### 进阶用法

**切换解析器后端 (uFBX)**
默认使用 FBX SDK 解析器。可以通过 `Reset` 方法切换到实验性的 uFBX 解析器，后者在某些场景下可能更快且线程安全。
```cpp
FbxParser.Reset(true); // 参数 `bInUseUfbxParser` 设为 true 以启用 uFBX 解析器
FbxParser.LoadFbxFile(FBXFilePath, BaseNodeContainer);
// 后续操作（如 FetchPayload）将使用 uFBX 解析器执行
```

**获取动画负载**
动画数据以“烘焙变换”的形式获取，结果是一系列关键帧文件。
```cpp
TArray<UE::Interchange::FAnimationPayloadQuery> PayloadQueries;
// ... 填充 PayloadQueries，描述需要获取哪些节点的哪些动画数据 ...

// 获取烘焙的动画变换负载，结果会存储到 ResultFolder 中，并更新映射表
FbxParser.FetchAnimationBakeTransformPayloads(PayloadQueries, ResultFolder);
// 可以通过 FbxParser.GetResultPayloadFilepath(PayloadKey) 查询某个负载对应的文件路径
```

## Demo 示例

以下是一个最小示例，演示如何使用 FBX 解析器加载一个 FBX 文件并遍历其生成的场景节点。

**FBXParserDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"

class UInterchangeBaseNodeContainer;

class FFBXParserDemo
{
public:
    static void RunDemo(const FString& FBXFilePath);
};
```

**FBXParserDemo.cpp**
```cpp
#include "FBXParserDemo.h"
#include "InterchangeFbxParser.h"
#include "InterchangeBaseNodeContainer.h"
#include "InterchangeSceneNode.h"

void FFBXParserDemo::RunDemo(const FString& FBXFilePath)
{
    // 1. 创建节点容器和解析器
    UInterchangeBaseNodeContainer* NodeContainer = NewObject<UInterchangeBaseNodeContainer>();
    UE::Interchange::FInterchangeFbxParser FbxParser;

    // 2. 加载 FBX 文件（场景图结构会被填充到 NodeContainer）
    FbxParser.LoadFbxFile(FBXFilePath, *NodeContainer);
    UE_LOG(LogTemp, Log, TEXT("FBX 文件已加载。"));

    // 3. 遍历所有生成的场景节点
    TArray<UInterchangeSceneNode*> SceneNodes;
    NodeContainer->GetNodes(UInterchangeSceneNode::StaticClass(), SceneNodes);

    for (UInterchangeSceneNode* Node : SceneNodes)
    {
        const FString NodeUid = Node->GetUniqueID();
        const FString DisplayLabel = Node->GetDisplayLabel();
        const FString ParentUid = Node->GetParentUid();
        UE_LOG(LogTemp, Log, TEXT("场景节点: UID=%s, Label=%s, ParentUID=%s"), *NodeUid, *DisplayLabel, *ParentUid);
    }

    // 4. (可选) 获取一个具体负载，例如纹理
    const FString SomeTexturePayloadKey = TEXT("MyTexturePayloadKey"); // 需要从实际生成的节点属性中获取
    TArray64<uint8> TextureData;
    if (FbxParser.FetchTexturePayload(SomeTexturePayloadKey, TextureData))
    {
        UE_LOG(LogTemp, Log, TEXT("成功获取纹理负载，大小: %d 字节"), TextureData.Num());
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `InterchangeCommon` | 提供 Interchange 框架的核心定义和基础节点类。 |
| `FBX SDK (第三方)` | 提供解析 Autodesk FBX 文件格式的核心库。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `3cfa4417` | Reinstated the uFBX parser as experimental | 重新将 uFBX 解析器作为实验性功能启用 |
| 2026-05-22 | `8fdd3a89` | [Interchange] Reset existing LODModels for reimport, so that Bone bindings and mappings are updated | 修复重新导入时 LOD 模型的骨骼绑定和映射未更新的问题 |
| 2026-05-19 | `755f95d4` | Interchange: Fix crash by protecting against nullptr objects in the list of imported objects. | 修复导入对象列表中存在空指针导致的崩溃问题 |

### 维护评价

该模块属于 Interchange 框架的核心组件，**处于活跃维护状态**。近期更新集中在 Bug 修复（如崩溃、重新导入问题）和实验性功能（uFBX 解析器）的推进上。虽然其作为底层解析器，功能相对稳定，但 Epic 仍在持续改进其兼容性和可靠性。对于需要导入 FBX 资产的项目，此模块是基础且必要的，可以放心使用。需要注意 uFBX 解析器目前仍标记为实验性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Runtime/Source/Parsers/Fbx)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Runtime/Tests) (Interchange 整体测试，包含 FBX 相关测试)