好的，根据您提供的 UE5 插件模块 `InterchangeFbxParser` 的源码信息和规范，我为您生成了以下完整的中文使用文档。

---

# Interchange Fbx Parser（FBX 解析器）

> 此模块为 Interchange Framework 插件的一部分，提供 FBX 文件格式的底层解析功能。

| 属性 | 值 |
|---|---|
| 中文名 | FBX 解析器 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeFbxParser` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-10-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Runtime/Source/Parsers/Fbx) | |

## 用途

`InterchangeFbxParser` 模块是 Interchange Framework 管道中的底层数据解析层，专门负责处理 `.fbx`（及部分 `.obj`）文件的物理读取与 SDK 交互。

它封装了不同 FBX 解析库（原生 FBX SDK 和第三方 `ufbx` 解析器）的差异，对外提供一个统一的高层接口 `IFbxParser`。其核心职责包括：

1.  **文件加载与 SDK 管理**：管理 FBX SDK 或 `ufbx` 库的生命周期，加载 FBX 文件到内存中。
2.  **场景图构建**：将 FBX SDK 内部的场景层级结构（节点、网格、摄像机、灯光、材质等）转换为 Interchange 框架标准化的节点容器（`UInterchangeBaseNodeContainer`），以便后续管线处理。
3.  **Payload 数据提取**：按需提供网格顶点数据、材质纹理、动画曲线等复杂二进制数据的“负载”（Payload）。

**为什么存在？**
FBX 是一个复杂且庞大的格式，其官方 SDK 可能存在线程安全问题。此模块通过提供一个抽象的 `IFbxParser` 接口和两种实现（`FFbxParser` 和 `FUfbxParser`），将 UE 的 Interchange 导入框架与具体的 FBX 解析库解耦。这使得引擎可以：
- 灵活切换或并排使用两种解析库。
- 将 FBX Sdk 的调用与主游戏线程或 Interchange 工作线程分离，提升稳定性与性能。
- 方便未来支持更多的第三方解析库。

## 使用场景

- **3D 模型导入**：当你将任意包含网格、骨骼、蒙皮、变形目标的 `.fbx` 文件拖入 UE 编辑器时，此模块是读取原始数据的起点。
- **动画资源导入**：导入包含复杂骨骼动画、形态目标动画的自定义 FBX 文件。
- **关卡结构导入**：导入包含摄像机、灯光和空白节点的场景结构 FBX 文件。
- **多源数据格式支持**：Interchange 框架利用此模块与 `FbxSDK` 交互，处理 `.fbx` 和 `.obj` 文件。

## 蓝图用法

本模块`InterchangeFbxParser` 作为底层解析模块，不直接暴露蓝图可调用函数。其 API 主要通过 C++ 与 Interchange Framework 的编辑器功能交互。

Interchange 框架的整体 `UInterchangeFbxTranslator` 和 `UInterchangeFbxPipeline` 等高级节点提供了面向蓝图的配置入口，可以控制来自本模块解析到的数据如何被构建。

*需要注意的是：以下节点并非直接来自于 `InterchangeFbxParser` 模块，而是 Interchange Framework 提供的，用于配置由该模块解析的数据。*

- **`UInterchangeGenericAnimationPipeline`**：蓝图节点，配置动画导入选项（如是否导入动画、帧率重映射等）。
- **`UInterchangeGenericMeshPipeline`**：蓝图节点，配置网格导入选项（如是否合并网格、生成碰撞体、灯光图 UV 等）。
- **`UInterchangeGenericMaterialPipeline`**：蓝图节点，配置材质导入选项（如纹理分辨率、材质类型等）。

在使用时，你可以在自定义的 `UInterchangePipelineBase` 子类蓝图或预设中，引用这些管道来精细控制来自 `Import` 模块的数据处理方式，而 Import 模块则会调用 `InterchangeFbxParser` 来获取原始数据。

## C++ 用法

引入此模块的最常见方式是通过 `UInterchangeFbxTranslator`，该 Translator 内部持有 `FInterchangeFbxParser` 实例来完成具体工作。

### 头文件引入

```cpp
// 引入 FInterchangeFbxParser 类
#include "InterchangeFbxParser.h"
#include "FbxAPI.h"
```

### 基本用法：直接使用解析器加载并提取数据

以下示例展示了如何直接使用 `FInterchangeFbxParser` 来加载一个 FBX 文件并获取其场景结构。通常，这是在 `UInterchangeFbxTranslator` 内部发生的。

```cpp
// 来源: Engine/Plugins/Interchange/Runtime/Source/Parsers/Fbx/Private/InterchangeFbxParser.cpp

void UInterchangeFbxTranslator::SourceNodeTranslate(
    UInterchangeBaseNodeContainer& BaseNodeContainer,
    const FString& SourceFilename,
    const FString& DestinationFilename,
    const FInterchangeTranslateArguments& Arguments,
    UInterchangeResultsContainer* ResultsContainer)
{
    // 1. 创建解析器实例
    TUniquePtr<UE::Interchange::FInterchangeFbxParser> FbxParser = 
        MakeUnique<UE::Interchange::FInterchangeFbxParser>();

    // 2. 设置转换配置（非常关键）
    // bConvertScene 决定是否将 FBX 坐标系转换为 UE 坐标系
    // bForceFrontXAxis 决定是否强制 X 轴为前方
    // bConvertSceneUnit 决定是否将单位转换为厘米
    // bKeepFbxNamespace 决定是否保留 FBX 的命名空间前缀
    const bool bConvertScene = true;
    const bool bForceFrontXAxis = false;
    const bool bConvertSceneUnit = true;
    const bool bKeepFbxNamespace = false;
    FbxParser->SetConvertSettings(bConvertScene, bForceFrontXAxis, bConvertSceneUnit, bKeepFbxNamespace);

    // 3. 加载 FBX 文件并填充节点容器
    // 这是最核心的操作，它会将 FBX 的层级结构转换为 BaseNodeContainer
    FbxParser->LoadFbxFile(SourceFilename, BaseNodeContainer);
    
    // 此时，BaseNodeContainer 中已经包含了所有 FBX 解析出的标准节点
    // 例如: UInterchangeMeshNode, UInterchangeSceneNode, UInterchangeAnimationTrackNode 等
}
```

### 进阶用法：获取特定类型的 Payload 数据

除了场景结构，网格顶点数据和动画曲线需要按需提取。

```cpp
// 来源: Engine/Plugins/Interchange/Runtime/Source/Parsers/Fbx/Private/InterchangeFbxParser.cpp

// ... 假设已经有了 BaseNodeContainer，并且你已经找到了一个 UInterchangeMeshNode
// ...

// 4. 获取网格的 Payload 数据
const FString MeshPayloadKey = InterchangeMeshNode->GetUniqueID();
const FTransform MeshGlobalTransform = FTransform::Identity; // 或任何需要应用的变换

FMeshPayloadData MeshPayloadData; // 包含了 FTransform, FMeshDescriptionBuilder 等
bool bSuccess = FbxParser->FetchMeshPayload(MeshPayloadKey, MeshGlobalTransform, MeshPayloadData);
if (bSuccess)
{
    // 现在可以访问网格描述并构建几何体
    // MeshPayloadData.MeshDescription
}

// 5. 获取动画 Payload 数据（批量烘焙）
TArray<UE::Interchange::FAnimationPayloadQuery> AnimationPayloadQueries;
// ... 填充查询列表，指定骨骼节点、时间范围等

const FString ResultFolder = DestinationFilePaths; // 输出目录
FbxParser->FetchAnimationBakeTransformPayloads(AnimationPayloadQueries, ResultFolder);

// 获取结果文件路径
TMap<FString, FString> ResultPayloads = FbxParser->FetchAnimationBakeTransformPayloads(AnimationPayloadQueriesJson, ResultFolder);
```

## Demo 示例

以下是一个最小化但完整的 C++ 示例，它假设你在一个 `UBlueprintFunctionLibrary` 或 `AActor` 的子类中使用，并展示如何集成 `FInterchangeFbxParser`。

**注意**: 此示例为示意性代码，用于展示模块核心 API 的调用流程。在实际插件中，`UInterchangeBaseNodeContainer` 和 Payload 结果会传递给后续的 Pipeline。

```cpp
// DemoInterchangeFbxParser.h
#pragma once

#include "CoreMinimal.h"
#include "InterchangeFbxParser.h"
#include "Nodes/InterchangeBaseNodeContainer.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "DemoInterchangeFbxParser.generated.h"

UCLASS()
class UDemoInterchangeFbxParser : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "Demo | Interchange")
    static bool ParseFBXFile(const FString& InFBXFilePath, const FString& InResultFolderPath)
    {
        // 1. 创建结果容器
        UInterchangeResultsContainer* ResultsContainer = NewObject<UInterchangeResultsContainer>();

        // 2. 创建解析器
        UE::Interchange::FInterchangeFbxParser FbxParser;
        FbxParser.SetResultContainer(ResultsContainer);

        // 3. 设置转换设置
        FbxParser.SetConvertSettings(true, false, true, false);

        // 4. 创建节点容器
        UInterchangeBaseNodeContainer* NodeContainer = NewObject<UInterchangeBaseNodeContainer>();
        NodeContainer->InitializeContainer();

        // 5. 加载并解析 FBX 文件
        UE_LOG(LogTemp, Log, TEXT("[Demo] Loading FBX file: %s"), *InFBXFilePath);
        FbxParser.LoadFbxFile(InFBXFilePath, *NodeContainer);

        // 检查结果
        if (ResultsContainer->GetResults().Num() > 0)
        {
            // 处理错误/警告
            for (const UInterchangeResult* Result : ResultsContainer->GetResults())
            {
                UE_LOG(LogTemp, Error, TEXT("[Interchange] %s"), *Result->GetText().ToString());
            }
            return false;
        }

        // 6. 遍历节点容器
        TArray<FString> NodeUids;
        NodeContainer->GetNodes(NodeUids);
        UE_LOG(LogTemp, Log, TEXT("[Demo] Parsed %d nodes from the FBX file."), NodeUids.Num());

        // 7. 尝试获取一个网格的 Payload (假设你知道了 PayloadKey)
        // 这里仅作演示，实际需要从 NodeContainer 中找到 UInterchangeMeshNode
        const FString ExampleMeshPayloadKey = TEXT("SomeMeshUniqueID"); 
        const FTransform ExampleTransform = FTransform::Identity;
        FMeshPayloadData OutMeshData;
        if (FbxParser.FetchMeshPayload(ExampleMeshPayloadKey, ExampleTransform, OutMeshData))
        {
            UE_LOG(LogTemp, Log, TEXT("[Demo] Successfully fetched mesh payload for key: %s"), *ExampleMeshPayloadKey);
            // OutMeshData.MeshDescription 现在包含了网格的几何数据
        }

        // 8. 返回成功
        return true;
    }
};
```

## 模块依赖

要使用此模块，你的 `Build.cs` 需要增加 `InterchangeFbxParser` 依赖。

| 模块 | 用途 |
|---|---|
| **无特殊依赖** | 仅依赖标准 Core/Engine/Slate 等模块。`UBT` 会自动处理其内部依赖的 `FbxSdk`、`ufbx`、`json` 以及 `InterchangeMessages`、`InterchangeNodes` 等模块。 |

## 维护状态

### 近期更新

- 2025-12-18 `93cfc06e` Fixed editor hanging when level reimporting a file containing skeletal meshes (修复了包含骨骼网格的关卡重新导入时编辑器挂起的问题)
- 2025-10-23 `0158cf6a` Removed unintended LOD specialization from named LOD Groups. (移除了命名 LOD 组中意外的 LOD 特化)
- 2025-10-21 `63c630c0` Fixing missing animation sequence import for LevelSequence on StaticMesh imported with... (修复了导入静态网格时关卡序列动画丢失的问题)

### 维护评价

该模块作为 `Interchange Framework` 的一部分，是 Epic 当前和未来的导入系统核心，虽然它被标记为较新的（约1年），但其在引擎架构中处于基础和活跃的开发阶段。从 git 历史看，团队仍在持续进行功能修复和迭代。

- **更新频率**：活跃。与整个 Interchange 框架一起频繁更新。
- **质量**：良好。设计上考虑了线程安全和模块化，提供了两种解析器（FBXSDK 和 ufbx）。
- **限制**：目前仍处于积极开发中，API 可能在未来版本中发生变化。`ufbx` 解析器相关的一些设置（如 `SetConvertSettings`）尚未完全实现。
- **推荐**: **强烈推荐使用**。它是导入新版 UE 项目 3D 资源的标准方式，是 `Datasmith` 和 `FBX Importer` 的现代替代方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Runtime/Source/Parsers/Fbx)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Tests) (Interchange 框架的测试目录)