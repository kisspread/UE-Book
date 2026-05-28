# Interchange Framework

> The Interchange Framework plugin offers a customizable import and export system, with an extensible set of pipelines for handling common file types.

| 属性 | 值 |
|---|---|
| 中文名 | 通用资产交换框架 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `InterchangeAnalytics` (Runtime), `InterchangeCommon` (Runtime), `InterchangeDispatcher` (Runtime), `InterchangeExport` (Runtime), `InterchangeFactoryNodes` (Runtime), `InterchangeImport` (Runtime), `InterchangeMessages` (Runtime), `InterchangeNodes` (Runtime), `InterchangeCommonParser` (Runtime), `InterchangeFbxParser` (Runtime), `GLTFCore` (Runtime), `InterchangePipelines` (Runtime), `Draco` (External) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange) | |

## 用途

Interchange Framework 是 UE5 引入的、旨在取代传统（FBX）导入管线的新一代资产导入/导出框架。其核心设计目标是**可扩展性和一致性**。它通过“解析器-节点-管道-工厂”的架构，将文件格式的解析、中间数据表示、处理规则和最终资产创建解耦。

`GLTFCore` 模块是该框架针对 **glTF 2.0** 格式的核心数据表示和解析层。它定义了 glTF 文件中所有概念（网格、材质、动画、场景节点等）的 C++ 数据结构（如 `FAsset`, `FMesh`, `FMaterial`），并提供了一个读取器（`FFileReader`）将 `.gltf` 或 `.glb` 文件解析到这些内存结构中。**这个模块本身不负责将 glTF 数据导入为 UE 资产**，那是上层 `InterchangeImport` 模块和相应管道的责任。它的存在是为了为整个 Interchange 框架提供一个标准化的、高效的 glTF 数据中间表示（Intermediate Representation）。

## 使用场景

- **你需要将 glTF 2.0 格式的 3D 资产导入 Unreal Engine** → Interchange 框架会自动调用 `GLTFCore` 来解析文件，并由后续管道创建静态网格、材质等资产。
- **你在开发自定义的资产处理管道或工具** → 你可以直接使用 `GLTFCore` 的 API 来读取和操作 glTF 文件的内部数据结构，而无需关心文件解析细节。
- **你需要一个轻量级的 glTF 文件查看器或数据提取器** → 可以利用 `GLTFCore` 将 glTF 文件加载到内存中，并遍历其场景图、网格数据等。

## 蓝图用法

`GLTFCore` 模块是一个纯 C++ 运行时模块，主要提供数据结构和文件读取功能，**不包含任何暴露给蓝图的 `UFUNCTION` 或 `UPROPERTY`**。与 glTF 文件的交互在蓝图层面通过 Interchange 框架提供的统一节点（如“Import Asset”）完成，用户通常无需直接操作 `GLTFCore` 的底层对象。

### 核心节点

无（本模块不提供蓝图节点）。

## C++ 用法

### 头文件引入

```cpp
#include "GLTFReader.h"
#include "GLTFAsset.h"
```

### 基本用法

从 `Public/GLTFReader.h` 中提取的典型用法：读取一个 glTF 文件并获取其资产数据。

```cpp
#include "GLTFReader.h"
#include "GLTFAsset.h"

// 假设你已经有了一个文件路径
FString GLTFFilePath = TEXT("/Game/Models/scene.gltf");

// 1. 创建资产结构和读取器
GLTF::FAsset AssetData;
GLTF::FFileReader FileReader;

// 2. 读取文件
// 参数：文件路径，是否加载图片二进制数据，是否加载元数据，输出资产对象
FileReader.ReadFile(GLTFFilePath, true, true, AssetData);

// 3. 检查读取是否成功（通过日志消息）
const TArray<GLTF::FLogMessage>& Messages = FileReader.GetLogMessages();
for (const auto& Msg : Messages)
{
    // 根据消息级别进行处理
    // EMessageSeverity::Display, Warning, Error
}

// 4. 使用资产数据
if (AssetData.Nodes.Num() > 0)
{
    const GLTF::FNode& RootNode = AssetData.Nodes[0];
    UE_LOG(LogTemp, Log, TEXT("第一个节点名称: %s"), *RootNode.Name);
}

if (AssetData.Meshes.Num() > 0)
{
    const GLTF::FMesh& FirstMesh = AssetData.Meshes[0];
    UE_LOG(LogTemp, Log, TEXT("第一个网格有 %d 个图元"), FirstMesh.Primitives.Num());
}
```
*来源: `Engine/Plugins/Interchange/Source/Parsers/GLTFCore/Public/GLTFReader.h`*

### 进阶用法

结合 `GLTFAccessor` 和 `GLTFMesh` 结构，深入访问网格的顶点数据。

```cpp
#include "GLTFAccessor.h"
#include "GLTFMesh.h"

// ... 假设 AssetData 已通过 FileReader 加载 ...

const GLTF::FMesh& Mesh = AssetData.Meshes[0];
const GLTF::FPrimitive& Prim = Mesh.Primitives[0];

// 检查图元是否有位置数据
if (Prim.HasPositions())
{
    TArray<FVector3f> Positions;
    // 获取顶点位置数据（自动处理 glTF 到 UE 的坐标系转换）
    Prim.GetPositions(Positions);
    UE_LOG(LogTemp, Log, TEXT("图元有 %d 个顶点"), Positions.Num());
}

// 访问具体的 Accessor 获取原始数据
// 例如，获取第一个图元的索引 Accessor
if (Prim.GetIndicesAccessorIndex() != INDEX_NONE)
{
    const GLTF::FAccessor& IndicesAccessor = AssetData.Accessors[Prim.GetIndicesAccessorIndex()];
    TArray<uint32> TriangleIndices;
    IndicesAccessor.GetUnsignedIntArray(TriangleIndices);
    // 处理三角形索引...
}
```
*来源: `Engine/Plugins/Interchange/Source/Parsers/GLTFCore/Public/GLTFMesh.h`, `Engine/Plugins/Interchange/Source/Parsers/GLTFCore/Public/GLTFAccessor.h`*

## Demo 示例

一个最小化的、可编译的 C++ 示例，展示如何在模块中加载并简单查询 glTF 文件。

**MyGLTFLoader.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"

class FMyGLTFLoaderModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    void LoadAndLogGLTFFile(const FString& FilePath);
};
```

**MyGLTFLoader.cpp**
```cpp
#include "MyGLTFLoader.h"
#include "GLTFReader.h"
#include "GLTFAsset.h"

#define LOCTEXT_NAMESPACE "FMyGLTFLoaderModule"

void FMyGLTFLoaderModule::StartupModule()
{
    // 模块启动逻辑
}

void FMyGLTFLoaderModule::ShutdownModule()
{
    // 模块清理逻辑
}

void FMyGLTFLoaderModule::LoadAndLogGLTFFile(const FString& FilePath)
{
    GLTF::FAsset LoadedAsset;
    GLTF::FFileReader Reader;

    Reader.ReadFile(FilePath, false, true, LoadedAsset);

    // 记录基本资产信息
    UE_LOG(LogTemp, Log, TEXT("glTF 资产 '%s' 加载完成。"), *LoadedAsset.Name);
    UE_LOG(LogTemp, Log, TEXT(" - 节点数: %d"), LoadedAsset.Nodes.Num());
    UE_LOG(LogTemp, Log, TEXT(" - 网格数: %d"), LoadedAsset.Meshes.Num());
    UE_LOG(LogTemp, Log, TEXT(" - 材质数: %d"), LoadedAsset.Materials.Num());

    // 打印第一个节点信息
    if (LoadedAsset.Nodes.Num() > 0)
    {
        const GLTF::FNode& FirstNode = LoadedAsset.Nodes[0];
        UE_LOG(LogTemp, Log, TEXT(" - 首个节点名称: %s, 类型: %d"), *FirstNode.Name, static_cast<int32>(FirstNode.Type));
    }

    // 输出读取过程中的警告或错误
    for (const auto& LogMsg : Reader.GetLogMessages())
    {
        switch (LogMsg.Get<0>())
        {
        case GLTF::EMessageSeverity::Warning:
            UE_LOG(LogTemp, Warning, TEXT("[glTF Warning] %s"), *LogMsg.Get<1>().ToString());
            break;
        case GLTF::EMessageSeverity::Error:
            UE_LOG(LogTemp, Error, TEXT("[glTF Error] %s"), *LogMsg.Get<1>().ToString());
            break;
        default:
            UE_LOG(LogTemp, Log, TEXT("[glTF Info] %s"), *LogMsg.Get<1>().ToString());
        }
    }
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyGLTFLoaderModule, MyGLTFLoader)
```

## 模块依赖

从 `GLTFCore.Build.cs` 的依赖项推断。要使用 `GLTFCore` 模块，你的模块需要在 `Build.cs` 文件中添加以下依赖。

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心功能 |
| `Json` | 用于解析 glTF JSON 数据 |
| `MeshDescription` | 用于从 glTF 数据构建网格描述 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-25 | `61d0e791` | USD Pregen: Implement tracking of Skeleton and PhysicsAssets | 为 USD 预生成添加骨骼和物理资产跟踪 |
| 2026-05-23 | `176334d2` | Fix localization warnings for UE 5.8 | 修复 UE 5.8 的本地化警告 |
| 2026-05-22 | `8fdd3a89` | [Interchange] Reset existing LODModels for reimport, so that Bone bindings and mappings are updated | 重导入时重置现有 LOD 模型，以更新骨骼绑定和映射 |
| 2026-05-22 | `3cfa4417` | Reinstated the uFBX parser as experimental | 恢复 uFBX 解析器为实验性功能 |
| 2026-05-19 | `755f95d4` | Interchange: Fix crash by protecting against nullptr objects in the list of imported objects. | 修复导入对象列表中空指针导致的崩溃 |

### 维护评价

`GLTFCore` 作为 Interchange 框架的核心解析模块，**维护非常活跃**。从最近的提交记录可以看到，Epic 持续在修复 bug、兼容新引擎版本（如 UE 5.8）并与其他资产格式（USD, FBX）的解析器进行协同更新。该模块是官方支持 glTF 导入的基石，稳定性和可靠性有保障。**强烈推荐使用**，尤其是在需要高质量、标准化 glTF 导入的项目中。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Source/Parsers/GLTFCore)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/interchange-framework-in-unreal-engine/) (Interchange 框架整体文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Tests) (Interchange 测试，可能包含 glTF 相关测试)