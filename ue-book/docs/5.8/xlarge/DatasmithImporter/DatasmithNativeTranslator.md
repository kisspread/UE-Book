# Datasmith Importer

> Importer for Datasmith files.

| 属性 | 值 |
|---|---|
| 中文名 | 数据导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithExternalSource` (Runtime), `DatasmithImporter` (Runtime), `DatasmithNativeTranslator` (Runtime), `DatasmithTranslator` (Runtime), `DirectLinkExtension` (Runtime), `DirectLinkExtensionEditor` (Runtime), `DirectLinkTest` (Runtime), `ExternalSource` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter) | |

## 用途

DatasmithImporter 插件并非简单的文件导入器，而是 Unreal Engine 与众多专业设计和可视化软件（如 3ds Max, Revit, SketchUp, SolidWorks, Rhino 等）之间的**实时同步桥梁**。其核心是基于 Epic 的 **DirectLink** 实时通信协议，允许这些外部软件中的场景和资产变化能够近乎实时地同步到 Unreal Engine 中，无需手动反复导出和导入。这解决了在建筑设计、工业设计、制造等流程中，因设计软件与实时可视化引擎之间的数据孤岛而导致的迭代缓慢、信息滞后问题。它主要由多个模块组成，其中 `DatasmithNativeTranslator` 模块负责解析 `.udatasmith` 二进制格式文件。

## 使用场景

- **建筑可视化（Archviz）**：建筑师在 Revit 或 SketchUp 中进行设计，通过 DirectLink 实时将修改后的建筑模型、材质和灯光同步到 UE 中的实时渲染场景，用于客户演示或 VR 体验。
- **工业设计与制造**：工程师在 SolidWorks 或 CATIA 中调整机械部件设计后，可即时在 UE 中查看带有精确材质和光照的产品可视化效果，用于设计评审或市场营销材料制作。
- **游戏开发与虚拟制片**：使用 3ds Max 或 Maya 创建复杂的场景或道具，通过 Datasmith 管道高效导入 UE，并利用其实时同步能力快速迭代资产。
- **方案比选与设计评审**：设计师可以快速切换不同版本的设计方案，所有变更均能实时反映在沉浸式的 UE 环境中，便于团队进行对比和决策。

## 蓝图用法

Datasmith 主要通过 C++ API 或编辑器操作使用，但其 `DatasmithImporter` 模块也暴露了一些蓝图接口，用于程序化控制导入过程。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Initialize` | 初始化一个 Datasmith 场景翻译器，获取其能力描述。 | `FDatasmithNativeTranslator` (C++类) |
| `LoadScene` | 从已初始化的源文件加载场景数据到 `IDatasmithScene` 对象中。 | `FDatasmithNativeTranslator` |
| `LoadStaticMesh` | 根据网格元素描述，加载对应的网格几何数据（顶点、索引等）。 | `FDatasmithNativeTranslator` |

### 使用示例（蓝图描述）

1.  创建一个 `FDatasmithNativeTranslator` 实例。
2.  调用 `Initialize` 节点，并传入一个 `FDatasmithTranslatorCapabilities` 变量以接收该翻译器支持的资源类型信息。
3.  创建一个 `IDatasmithScene` 引用。
4.  调用 `LoadScene` 节点，将 `.udatasmith` 文件路径传入，并将加载的场景数据输出到上一步创建的 `IDatasmithScene` 对象。
5.  遍历加载场景中的网格元素 (`IDatasmithMeshElement`)，对每个元素调用 `LoadStaticMesh` 节点，获取其详细的 `FDatasmithMeshElementPayload`（包含顶点数据、材质槽等）。
6.  使用获取到的 Payload 数据，在 UE 中构建实际的 `UStaticMesh` 资产。

## C++ 用法

Datasmith 的强大功能主要通过 C++ API 来发挥。以下示例基于源码中的使用模式。

### 头文件引入

```cpp
#include "DatasmithNativeTranslator.h"
#include "DatasmithSceneFactory.h"
```

### 基本用法

以下代码展示了如何使用 `DatasmithNativeTranslator` 加载一个 Datasmith 文件并获取其场景数据。

```cpp
// 来源：根据 DatasmithNativeTranslator.h 和典型使用模式编写
void LoadDatasmithScene()
{
    // 1. 创建并初始化翻译器
    TSharedRef<FDatasmithNativeTranslator> Translator = MakeShared<FDatasmithNativeTranslator>();
    FDatasmithTranslatorCapabilities Capabilities;
    Translator->Initialize(Capabilities);
    
    // 检查翻译器是否支持我们的源文件（例如 .udatasmith）
    if (!Capabilities.bIsSceneFileSupported)
    {
        UE_LOG(LogTemp, Error, TEXT("Translator does not support this file type."));
        return;
    }
    
    // 2. 创建空的 Datasmith 场景对象用于接收数据
    TSharedRef<IDatasmithScene> Scene = FDatasmithSceneFactory::CreateScene(TEXT("MyImportedScene"));
    
    // 3. 加载场景
    FString FilePath = TEXT("/Path/To/Your/Scene.udatasmith");
    if (Translator->LoadScene(Scene))
    {
        // 4. 场景加载成功，可以访问场景中的元素
        int32 MeshCount = Scene->GetMeshesCount();
        UE_LOG(LogTemp, Log, TEXT("Loaded scene with %d meshes."), MeshCount);
        
        // 5. 加载具体的网格资产
        for (int32 i = 0; i < MeshCount; ++i)
        {
            TSharedPtr<IDatasmithMeshElement> MeshElement = Scene->GetMesh(i);
            if (MeshElement.IsValid())
            {
                FDatasmithMeshElementPayload MeshPayload;
                if (Translator->LoadStaticMesh(MeshElement.ToSharedRef(), MeshPayload))
                {
                    // 使用 MeshPayload 中的数据（顶点、索引等）创建 UStaticMesh
                    // ... 具体的 UStaticMesh 创建逻辑 ...
                }
            }
        }
    }
}
```

### 进阶用法

处理文件路径解析和资源依赖。`DatasmithNativeTranslator` 提供了静态方法来处理资源路径，这在加载具有相对路径引用的场景时至关重要。

```cpp
// 来源：基于 DatasmithNativeTranslator.h 中的静态方法
void ResolveResourcePaths()
{
    // 假设主场景文件和资源（如 .udatamesh 文件）位于同一目录或特定子目录
    FString SceneFilePath = TEXT("C:/Projects/MyBuilding/Building.udatasmith");
    TArray<FString> SearchPaths;
    SearchPaths.Add(TEXT("C:/Projects/MyBuilding/Resources/"));
    SearchPaths.Add(TEXT("C:/Projects/MyBuilding/"));
    
    // 1. 解析单个文件路径
    FString RelativeMeshPath = TEXT("./Meshes/Wall.udatamesh");
    FString AbsoluteMeshPath = FDatasmithNativeTranslator::ResolveFilePath(RelativeMeshPath, SearchPaths);
    // AbsoluteMeshPath 可能解析为 "C:/Projects/MyBuilding/Resources/Meshes/Wall.udatamesh"
    
    // 2. 解析整个场景中所有文件的路径
    TSharedRef<IDatasmithScene> LoadedScene = FDatasmithSceneFactory::CreateScene(TEXT("Scene"));
    // ... 假设已经加载了场景 ...
    FDatasmithNativeTranslator::ResolveSceneFilePaths(LoadedScene, SearchPaths);
    // 此后，LoadedScene 内部所有元素的文件路径引用都已被修正为绝对路径
}
```

## Demo 示例

以下是一个完整的、自包含的 C++ 类，演示如何使用 `DatasmithNativeTranslator` 导入一个场景文件并输出基本信息。

### DatasmithDemo.h
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "DatasmithDemo.generated.h"

class IDatasmithScene;
class IDatasmithTranslator;

UCLASS()
class DATASMITHIMPORTER_API UDatasmithDemoSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    UFUNCTION(BlueprintCallable, Category = "Datasmith Demo")
    bool ImportDatasmithScene(const FString& FilePath);

private:
    TSharedPtr<IDatasmithTranslator> Translator;
    TSharedPtr<IDatasmithScene> CurrentScene;
};
```

### DatasmithDemo.cpp
```cpp
#include "DatasmithDemo.h"
#include "DatasmithNativeTranslator.h"
#include "DatasmithSceneFactory.h"
#include "IDatasmithSceneElements.h"
#include "Misc/FileHelper.h"
#include "HAL/PlatformFileManager.h"

void UDatasmithDemoSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    Translator = MakeShared<FDatasmithNativeTranslator>();
}

void UDatasmithDemoSubsystem::Deinitialize()
{
    Translator.Reset();
    CurrentScene.Reset();
    Super::Deinitialize();
}

bool UDatasmithDemoSubsystem::ImportDatasmithScene(const FString& FilePath)
{
    if (!Translator.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Datasmith translator not initialized."));
        return false;
    }

    // 检查文件是否存在
    if (!FPlatformFileManager::Get().GetPlatformFile().FileExists(*FilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("File not found: %s"), *FilePath);
        return false;
    }

    // 初始化翻译器
    FDatasmithTranslatorCapabilities Capabilities;
    Translator->Initialize(Capabilities);

    // 创建新场景
    CurrentScene = FDatasmithSceneFactory::CreateScene(FPaths::GetBaseFilename(FilePath));

    // 执行加载
    if (!Translator->LoadScene(CurrentScene.ToSharedRef()))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load Datasmith scene from: %s"), *FilePath);
        CurrentScene.Reset();
        return false;
    }

    // 成功，输出场景信息
    UE_LOG(LogTemp, Log, TEXT("Successfully imported Datasmith scene '%s'."), *CurrentScene->GetName());
    UE_LOG(LogTemp, Log, TEXT("  Meshes: %d"), CurrentScene->GetMeshesCount());
    UE_LOG(LogTemp, Log, TEXT("  Materials: %d"), CurrentScene->GetMaterialsCount());

    return true;
}
```

## 模块依赖

要使用 `DatasmithNativeTranslator` 模块，你的模块需要依赖以下核心模块：

| 模块 | 用途 |
|---|---|
| `DatasmithTranslator` | 提供 `IDatasmithTranslator` 接口，是所有翻译器（包括原生翻译器）的基础。 |
| `DirectLink` | 提供 DirectLink 实时通信的底层支持，是 Datasmith 实时同步功能的基石。 |
| `ExternalSource` | 提供 `IExternalSource` 接口，用于管理外部数据源，Datasmith 作为一种外部源类型实现。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的编译警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将过时的 UE_LOG 宏迁移到新的 UE_LOGF 宏。 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introd... | 废弃了带 `bIncludeNestedObjects` 参数的 `GetObjects`/`ForEachObjectWithOuter` 函数，并引入了新接口。 |
| 2026-03-06 | `7b69892a` | clean up code changing texture properties with wrapping in PreEditChange/PostEditChange as required. | 清理纹理属性修改代码，确保在 `PreEditChange`/`PostEditChange` 中正确包裹修改操作。 |
| 2026-03-05 | `1adb9f68` | New material translator work: | 新的材质翻译器相关工作（具体功能未在消息中完全说明）。 |

### 维护评价

DatasmithImporter 是一个**活跃维护**的核心企业级插件。
- **创建时间**：2019年，随着 Unreal Engine 对设计和工程可视化领域的支持而生，已超过5年，属于**老古董**级别的插件。
- **近期活动**：从 git 历史看，在2026年仍有持续的更新，主要集中在**代码现代化**（如宏迁移）、**API 废弃与替换**、以及**编译警告修复**。这表明 Epic 团队仍在积极维护其代码质量和兼容性，以适应 UE 新版本的演进。
- **状态评估**：作为连接专业设计软件与 UE 的官方桥梁，它是 Epic 战略的一部分，因此不太可能被废弃。它支持最新的 UE 5.x 版本。
- **使用推荐**：**强烈推荐**有专业软件数据导入需求（特别是需要实时同步）的用户使用。需要注意的是，它**默认未启用**，且主要通过 C++ API 操作，对使用者的技术要求较高。建议参考 Epic 官方文档和示例项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter/Source/DirectLinkTest)