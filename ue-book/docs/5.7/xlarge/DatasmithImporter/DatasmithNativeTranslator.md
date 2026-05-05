# Datasmith Importer

> Importer for Datasmith files.（照抄，不翻译）

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

Datasmith 是 Unreal Engine 的企业级数据导入和工作流生态系统。`DatasmithImporter` 插件是该系统的核心，它不仅仅是一个简单的文件导入器，而是一个**转换和同步框架**。它解决了将复杂的 CAD、BIM（建筑信息模型）和 DCC（数字内容创建）软件资产（如来自 Revit, 3ds Max, SketchUp, CATIA 等）高效、高保真地导入到 Unreal Engine 中的难题。

其核心价值在于：
1.  **格式转换**：将各种工业设计格式转换为 UE 可用的资产（静态网格体、材质、灯光、层级等）。
2.  **实时同步**：通过 DirectLink 技术，支持源应用程序与 UE 之间的实时或增量更新，实现设计迭代的快速可视化。
3.  **数据优化**：在导入过程中进行网格体优化、材质转换和场景组织，以适应实时渲染的需求。

## 使用场景

-   **建筑可视化 (Arch Viz)**：建筑师使用 Revit 或 SketchUp 完成设计后，通过 Datasmith 将整个建筑模型（包括材质、灯光、家具）一键导入 UE，用于制作高质量的建筑漫游和营销视频。
-   **工业设计与制造**：汽车或产品设计师使用 CATIA, SolidWorks 等 CAD 软件创建精密模型，通过 Datasmith 导入 UE 进行虚拟评审、装配模拟或创建交互式产品配置器。
-   **大型场景构建**：需要从多个不同软件（如 3ds Max 的场景布局、Revit 的建筑结构、Rhino 的异形构件）导入资产并整合到一个 UE 项目中。
-   **设计迭代**：设计师在源软件中修改模型后，通过 Datasmith 的增量更新功能，仅将更改的部分同步到 UE 场景中，避免了重复导入整个大型场景。

## 蓝图用法

Datasmith 的核心功能主要通过 C++ API 和编辑器操作（如“Datasmith 场景导入”按钮）暴露。蓝图中直接操作底层翻译器（Translator）的节点较少，更多是通过编辑器工具或项目设置进行配置。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Import Datasmith Scene` | （编辑器操作）通过文件对话框选择并导入 `.udatasmith` 或其他支持格式的文件。 | `UDatasmithImportFactory` |
| `Reimport Datasmith Scene` | （编辑器操作）对已导入的 Datasmith 资产进行重新导入或更新。 | `UDatasmithImportFactory` |

### 使用示例（蓝图描述）

在蓝图中，通常不直接调用翻译器。最常见的用法是：
1.  在内容浏览器中右键，选择“导入到...”。
2.  在文件选择器中，选择一个 `.udatasmith` 文件。
3.  在弹出的 Datasmith 导入选项窗口中配置导入选项（如光照贴图分辨率、碰撞生成等）。
4.  点击“导入”，资产将被创建在指定路径下。

对于需要程序化控制导入的场景，可以使用 `UDatasmithImportFactory` 的 C++ 接口。

## C++ 用法

Datasmith 的 C++ API 主要面向需要深度集成或自定义导入流程的开发者。`DatasmithNativeTranslator` 模块提供了处理 `.udatasmith` 原生文件格式的翻译器实现。

### 头文件引入

```cpp
#include "DatasmithNativeTranslator.h"
#include "DatasmithTranslator.h"
```

### 基本用法

以下示例展示了如何通过 `FDatasmithNativeTranslator` 加载一个 `.udatasmith` 场景文件的基本流程。这通常在自定义的导入工具或自动化流程中使用。

```cpp
// 来源：基于 DatasmithNativeTranslator.h 接口推断的用法
#include "DatasmithNativeTranslator.h"
#include "DatasmithSceneFactory.h"
#include "IDatasmithSceneElements.h"

void LoadDatasmithScene(const FString& UDatasmithFilePath)
{
    // 1. 创建原生翻译器实例
    TSharedRef<FDatasmithNativeTranslator> Translator = MakeShared<FDatasmithNativeTranslator>();

    // 2. 初始化翻译器并获取其能力描述
    FDatasmithTranslatorCapabilities Capabilities;
    Translator->Initialize(Capabilities);

    // 3. 创建一个空的 Datasmith 场景对象用于接收数据
    TSharedRef<IDatasmithScene> DatasmithScene = FDatasmithSceneFactory::CreateScene(TEXT("MyImportedScene"));

    // 4. 加载场景数据（解析 .udatasmith 文件）
    if (Translator->LoadScene(DatasmithScene))
    {
        UE_LOG(LogTemp, Log, TEXT("Datasmith scene loaded successfully. Actor count: %d"), DatasmithScene->GetActorsCount());
        // 此时 DatasmithScene 包含了从文件解析出的所有元素（Actor, Mesh, Material 等）。
        // 下一步通常是使用 FDatasmithImporter 将这些元素转换为 UE 资产。
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load Datasmith scene from: %s"), *UDatasmithFilePath);
    }
}
```

### 进阶用法

更复杂的用法涉及加载场景中的特定资产，例如单独加载一个静态网格体。这需要先加载场景以获取元素引用，再使用翻译器加载其详细数据。

```cpp
// 来源：基于 FDatasmithNativeTranslator::LoadStaticMesh 接口推断
void LoadSpecificMesh(TSharedRef<IDatasmithScene> LoadedScene, const FString& MeshElementName)
{
    // 假设已通过 LoadScene 加载了场景
    TSharedRef<FDatasmithNativeTranslator> Translator = MakeShared<FDatasmithNativeTranslator>();
    FDatasmithTranslatorCapabilities Caps;
    Translator->Initialize(Caps);

    // 在场景中查找名为 MeshElementName 的网格体元素
    TSharedPtr<IDatasmithMeshElement> MeshElement;
    for (int32 i = 0; i < LoadedScene->GetMeshesCount(); ++i)
    {
        TSharedRef<IDatasmithMeshElement> CurrentMesh = LoadedScene->GetMesh(i);
        if (CurrentMesh->GetName() == MeshElementName)
        {
            MeshElement = CurrentMesh;
            break;
        }
    }

    if (MeshElement.IsValid())
    {
        // 准备用于接收网格体数据的 Payload
        FDatasmithMeshElementPayload MeshPayload;

        // 使用翻译器加载该网格体的几何数据
        if (Translator->LoadStaticMesh(MeshElement.ToSharedRef(), MeshPayload))
        {
            UE_LOG(LogTemp, Log, TEXT("Mesh '%s' loaded. Vertex count: %d"), *MeshElementName, MeshPayload.GetMesh().GetVertexCount());
            // MeshPayload 现在包含了网格体的顶点、索引、UV 等数据。
        }
    }
}
```

## Demo 示例

一个最小化的 C++ 示例，展示如何集成 DatasmithNativeTranslator 来加载场景。

**MyDatasmithLoader.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "DatasmithNativeTranslator.h"
#include "IDatasmithSceneElements.h"

class FMyDatasmithLoader
{
public:
    /** 加载指定的 .udatasmith 文件并返回解析后的场景对象。返回 nullptr 表示失败。 */
    static TSharedPtr<IDatasmithScene> LoadUDatasmithFile(const FString& FilePath);
};
```

**MyDatasmithLoader.cpp**
```cpp
#include "MyDatasmithLoader.h"
#include "DatasmithSceneFactory.h"

TSharedPtr<IDatasmithScene> FMyDatasmithLoader::LoadUDatasmithFile(const FString& FilePath)
{
    // 检查文件是否存在
    if (!FPaths::FileExists(FilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("File not found: %s"), *FilePath);
        return nullptr;
    }

    // 创建翻译器
    TSharedRef<FDatasmithNativeTranslator> Translator = MakeShared<FDatasmithNativeTranslator>();
    FDatasmithTranslatorCapabilities Capabilities;
    Translator->Initialize(Capabilities);

    // 创建场景容器
    TSharedRef<IDatasmithScene> Scene = FDatasmithSceneFactory::CreateScene(FPaths::GetBaseFilename(FilePath));

    // 执行加载
    if (Translator->LoadScene(Scene))
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully loaded Datasmith scene: %s"), *FilePath);
        return Scene;
    }

    UE_LOG(LogTemp, Error, TEXT("Failed to load Datasmith scene: %s"), *FilePath);
    return nullptr;
}
```

## 模块依赖

`DatasmithNativeTranslator` 模块依赖于 Datasmith 的核心框架。要在你的模块中使用它，需要在 `Build.cs` 中添加以下依赖。

| 模块 | 用途 |
|---|---|
| `DatasmithCore` | Datasmith 的核心数据结构和接口定义（如 `IDatasmithScene`, `IDatasmithMeshElement`）。 |
| `DatasmithTranslator` | 翻译器基类和接口（`IDatasmithTranslator`）。 |

## 维护状态

### 近期更新

```
- 2024-10-18 7ce30a026d64 Fix simple cases of unreachable code for loops that terminate after one iteration
- 2024-10-18 f5b459f97289 Datasmith - Remove the experimental Datasmith Clo json importer plugin, and deprecate unused Datasmith cloth code.
- 2024-10-18 7549a32b4159 Datasmith: Cloth Serialization support - native translator can load expoorted cloths #rb JeanLuc.Corenthin #preflight 6308f5363405456ee56fd221
```

**解读**：
-   最近的提交（2024-10-18）主要是代码清理和功能废弃。移除了实验性的布料导入器插件，并废弃了相关的布料代码。同时修复了一些代码质量问题。这表明该模块处于**维护状态**，主要进行稳定性和代码健康度的改进，而非新功能开发。

### 维护评价

-   **创建时间**：约 6 年前（2019年），是一个成熟的系统。
-   **更新频率**：近期更新集中在代码清理和废弃功能，没有重大新功能。更新频率较低。
-   **活跃度**：属于**维护中**。作为 Unreal Engine 企业版的核心组件，它会持续得到支持以确保与引擎版本的兼容性和稳定性，但不会有频繁的功能迭代。
-   **已知限制**：依赖于 Epic 的 Datasmith 运行时库。对源软件版本和特定功能的支持需要参考官方兼容性列表。
-   **推荐使用**：**强烈推荐**用于任何需要将工业 CAD/BIM 数据导入 UE 的项目。它是官方支持的、最成熟和高效的解决方案。尽管更新不频繁，但其核心功能稳定可靠。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithImporter)
-   [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithImporter/Tests) (路径推断)