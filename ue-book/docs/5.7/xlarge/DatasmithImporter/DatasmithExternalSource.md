# Datasmith Importer

> Importer for Datasmith files.

| 属性 | 值 |
|---|---|
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithExternalSource` (Runtime), `DatasmithImporter` (Runtime), `DatasmithNativeTranslator` (Runtime), `DatasmithTranslator` (Runtime), `DirectLinkExtension` (Runtime), `DirectLinkExtensionEditor` (Runtime), `DirectLinkTest` (Runtime), `ExternalSource.build` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithImporter) | |

## 用途

Datasmith Importer 是 Unreal Engine 企业级数据交换解决方案 Datasmith 的核心导入插件。它不仅仅是一个简单的文件导入器，而是一个完整的数据转换和同步框架。其主要功能是将来自专业设计软件（如 CAD、BIM、DCC 工具）的复杂场景、模型和元数据，通过 Datasmith 格式（`.udatasmith`）或 DirectLink 实时连接，高效、准确地转换为 Unreal Engine 的资产（如 Static Mesh、Material、Actor 等）。

该插件解决了专业设计领域与实时 3D 引擎之间的数据鸿沟问题，确保了设计意图、层级结构、材质属性和元数据在转换过程中的保真度，是建筑、工程、施工（AEC）和制造行业工作流的关键组件。

## 使用场景

- **建筑可视化**：将 Revit、ArchiCAD 或 SketchUp 的 BIM 模型导入 UE，用于创建高质量的建筑漫游和营销材料。
- **产品设计与制造**：导入 SolidWorks、CATIA 或 NX 的 CAD 模型，用于创建交互式产品配置器、装配说明或虚拟展厅。
- **工厂规划与仿真**：将大型工厂布局（来自 AutoCAD、Navisworks）导入 UE，进行物流仿真、安全培训和运营规划。
- **实时设计评审**：通过 DirectLink 功能，在设计软件中修改模型后，UE 中的场景能近乎实时地同步更新，用于跨团队协作和即时反馈。

## 蓝图用法

由于 Datasmith 的核心导入逻辑主要在 C++ 层实现，并通过编辑器菜单和资产导入流程触发，其直接的蓝图 API 相对有限。主要的交互点在于模块管理和状态查询。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsAvailable` | 检查 DatasmithExternalSource 模块是否已加载并可用。 | `FDatasmithExternalSourceModule` |

### 使用示例（蓝图描述）

在蓝图中，你通常不会直接调用 Datasmith 的导入函数。更常见的用法是检查模块状态，以确保相关的导入功能可用。
1.  使用 `FDatasmithExternalSourceModule::IsAvailable` 节点（或通过 C++ 暴露的等效蓝图函数）来判断 Datasmith 外部源功能是否就绪。
2.  根据返回的布尔值，决定是否启用依赖 Datasmith 的 UI 元素或功能逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "DatasmithExternalSourceModule.h"
```

### 基本用法

检查 Datasmith 外部源模块的可用性，这是在使用任何依赖该模块的功能前的安全检查。

```cpp
// 来源: Engine/Plugins/Enterprise/DatasmithImporter/Source/DatasmithExternalSource/Public/DatasmithExternalSourceModule.h
if (FDatasmithExternalSourceModule::IsAvailable())
{
    // Datasmith 外部源（如 DirectLink）功能可用
    // 可以安全地初始化相关功能或显示相关UI
    UE_LOG(LogTemp, Log, TEXT("Datasmith External Source module is loaded and ready."));
}
else
{
    UE_LOG(LogTemp, Warning, TEXT("Datasmith External Source module is not available."));
}
```

### 进阶用法

获取模块单例的引用，以便调用更具体的模块方法（如果存在）。这通常用于需要与模块生命周期深度集成的场景。

```cpp
// 来源: Engine/Plugins/Enterprise/DatasmithImporter/Source/DatasmithExternalSource/Public/DatasmithExternalSourceModule.h
// 确保模块已加载
if (FDatasmithExternalSourceModule::IsAvailable())
{
    FDatasmithExternalSourceModule& ExternalSourceModule = FDatasmithExternalSourceModule::Get();
    // 调用模块提供的其他方法...
    // ExternalSourceModule.SomeSpecificFunction();
}
```

## Demo 示例

一个最小化的 C++ 示例，展示如何安全地检查并使用 Datasmith 外部源模块。

```cpp
// MyDatasmithUser.h
#pragma once

#include "CoreMinimal.h"

class FMyDatasmithUser
{
public:
    void Initialize();
    bool IsDatasmithReady() const;
};
```

```cpp
// MyDatasmithUser.cpp
#include "MyDatasmithUser.h"
#include "DatasmithExternalSourceModule.h"

void FMyDatasmithUser::Initialize()
{
    if (IsDatasmithReady())
    {
        // 执行依赖 Datasmith 外部源的初始化逻辑
        UE_LOG(LogTemp, Log, TEXT("Initializing with Datasmith External Source support."));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Proceeding without Datasmith External Source support."));
    }
}

bool FMyDatasmithUser::IsDatasmithReady() const
{
    return FDatasmithExternalSourceModule::IsAvailable();
}
```

## 模块依赖

从模块名称和典型 Datasmith 架构推断，使用者可能需要依赖以下模块。具体依赖需查阅各模块的 `Build.cs` 文件。

| 模块 | 用途 |
|---|---|
| `DatasmithCore` | Datasmith 的核心数据结构和接口定义。 |
| `DirectLink` | 实现 DirectLink 实时同步协议的底层通信库。 |
| `DatasmithContent` | 包含 Datasmith 导入后生成的特定资产类型（如 DatasmithScene）。 |

## 维护状态

### 近期更新

```
- c11db69b54bd [Datasmith] Modified DirectLinkExtension and ExternalSource modules to be runtime
- 32047af14586 Datasmith: Moved path resolution logic out of the xml reader in order to share that logic with scenes received from DirectLink
- 0ed0c3ab8a71 Exposing FSceneGuard and using it to manage the loaded state of FExternalSource's translator
```

- `c11db69b54bd`: 将 DirectLinkExtension 和 ExternalSource 模块的类型修改为 Runtime，这可能意味着它们现在可以在打包后的游戏中使用，而不仅仅是在编辑器中。
- `32047af14586`: 重构了路径解析逻辑，使其能够被 XML 读取器和 DirectLink 场景共享，提高了代码复用性和一致性。
- `0ed0c3ab8a71`: 暴露了 `FSceneGuard` 并用它来管理外部源转换器的加载状态，增强了状态管理的健壮性。

### 维护评价

**活跃维护**。Datasmith 作为 Epic 的重点企业产品，其导入器插件持续得到更新和优化。从最近的提交记录看，开发团队正在进行架构优化（模块类型调整、逻辑解耦）和功能增强（改进状态管理），以提升性能和可扩展性。该插件是成熟且关键的基础设施，推荐在相关行业工作流中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithImporter/Source/DirectLinkTest) (DirectLinkTest 模块可能包含相关测试)