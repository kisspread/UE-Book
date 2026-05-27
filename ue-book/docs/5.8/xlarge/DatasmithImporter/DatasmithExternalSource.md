# Datasmith Importer

> Importer for Datasmith files.

| 属性 | 值 |
|---|---|
| 中文名 | Datasmith导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（核心导入逻辑） |
| 模块 | `DatasmithExternalSource` (Runtime), `DatasmithImporter` (Runtime), `DatasmithNativeTranslator` (Runtime), `DatasmithTranslator` (Runtime), `DirectLinkExtension` (Runtime), `DirectLinkExtensionEditor` (Runtime), `DirectLinkTest` (Runtime), `ExternalSource` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter) | |

## 用途

DatasmithImporter 是 Unreal Engine Datasmith 生态系统中的核心导入插件。它的主要职责是处理 `.udatasmith` 文件以及通过 **DirectLink** 实时传入的数据流，将其转换为 UE 内部的资产和场景结构。该插件不仅是简单的文件导入器，更是一个数据转换桥梁，解决了从各种专业 CAD/BIM 软件（如 Revit, SketchUp, 3ds Max, CATIA 等）向 Unreal Engine 高效传递复杂模型、材质、灯光和元数据的问题。其存在是为了确保专业设计数据在游戏引擎中的高保真和可管理性。

## 使用场景

- 你是一名建筑师，使用 Revit 或 SketchUp 完成建筑模型设计，希望将其导入 Unreal Engine 制作交互式可视化、VR 漫游或影视级渲染。
- 你是一名汽车设计师，需要将 CATIA 或 SolidWorks 中的复杂曲面汽车模型导入 UE，进行实时渲染和虚拟评审。
- 你是一名机械工程师，希望在 Unreal Engine 中为数字化生产线创建一个装配线的数字孪生。
- 你需要将 3ds Max 或 Cinema 4D 制作的静态场景导入 UE，同时保留其材质、灯光和层级结构。
- 你需要与外部 CAD/BIM 软件进行**实时双向同步**，在 UE 中所做的修改能反馈到设计软件，或反之。

## 蓝图用法

该插件主要在 C++ 层面工作，提供的蓝图节点相对有限，主要用于触发导入流程和配置导入选项。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ImportDatasmithScene` | 从给定的场景资产和选项执行导入。 | `UDatasmithImportFactory` (静态) |
| `ImportFile` | 导入单个 Datasmith 文件。 | `UDatasmithImportFactory` (静态) |
| `GetImportOptions` | 获取当前可用的 Datasmith 导入选项对象。 | `UDatasmithImportFactory` (静态) |
| `资产/路径` (属性) | 配置 `UDatasmithSceneImportOptions` 对象，控制几何体、材质、灯光等的导入行为。 | `UDatasmithSceneImportOptions` |

### 使用示例（蓝图描述）

1.  **简单文件导入**：
    *   使用 `Construct Object from Class` 节点创建一个 `UDatasmithImportOptions` 对象。
    *   通过该对象的 `ImportOptions` 属性（类型为 `UDatasmithSceneImportOptions`）设置具体的导入选项。
    *   将 `.udatasmith` 文件的 `File Path` 和创建好的 `Import Options` 对象连接到 `UDatasmithImportFactory` 的 `Import File` 节点输入。
    *   执行节点即可触发导入。

2.  **使用预配置选项**：
    *   调用 `UDatasmithImportFactory` 的 `Get Import Options` 节点获取默认选项。
    *   将获取的选项对象连接到 `Import File` 或 `Import Datasmith Scene` 节点。

## C++ 用法

### 头文件引入

要使用 Datasmith 导入器的核心功能，你需要引入对应的模块头文件。根据你的需求，可能涉及以下模块：
```cpp
#include "DatasmithImporterModule.h" // 模块接口
#include "DatasmithImportFactory.h" // 工厂类
#include "DatasmithSceneImportContext.h" // 导入上下文
#include "DatasmithImportOptions.h" // 导入选项
#include "DatasmithTranslator.h" // 翻译器接口
```

### 基本用法

以下示例展示了如何在 C++ 中通过工厂类导入一个 Datasmith 文件。
*(来源: `Engine/Plugins/Enterprise/DatasmithImporter/Source/DatasmithImporter/Private/DatasmithImportFactory.cpp`)*

```cpp
// 假设我们已经有了文件路径和一组导入选项
FString DatasmithFilePath = TEXT("/Game/MyImportedScene.udatasmith");
UDatasmithImportOptions* ImportOptions = NewObject<UDatasmithImportOptions>();

// 获取导入工厂
UDatasmithImportFactory* DatasmithFactory = GetMutableDefault<UDatasmithImportFactory>();
if (DatasmithFactory)
{
    // 创建一个临时的 UDatasmithSceneImportOptions 来填充具体设置
    UDatasmithSceneImportOptions* SceneImportOptions = NewObject<UDatasmithSceneImportOptions>();
    // 配置场景导入选项 (例如，启用几何体合并、设置材质策略等)
    SceneImportOptions->bMergeMeshes = true;
    SceneImportOptions->MaterialImport = EDatasmithImportMaterial::Import;

    // 将场景选项关联到导入选项
    ImportOptions->ImportOptions = SceneImportOptions;

    // 执行导入
    UObject* ImportedAsset = DatasmithFactory->ImportFile(DatasmithFilePath, ImportOptions);
    if (ImportedAsset)
    {
        UE_LOG(LogTemp, Log, TEXT("Datasmith scene imported successfully as: %s"), *ImportedAsset->GetName());
    }
}
```

### 进阶用法

更高级的用法包括直接操作导入上下文（`FDatasmithSceneImportContext`）和注册自定义的资产转换器（Translator）。这对于处理特定类型的资产或实现自定义导入逻辑至关重要。
*(来源: `Engine/Plugins/Enterprise/DatasmithImporter/Source/DatasmithImporter/Private/DatasmithSceneImportContext.cpp` 和 `Engine/Plugins/Enterprise/DatasmithImporter/Source/DatasmithTranslator/Private/DatasmithTranslatorModule.cpp`)*

```cpp
#include "DatasmithSceneImportContext.h"
#include "DatasmithSceneImporter.h"

// 创建一个导入上下文，它管理导入过程中的状态和资产映射
FDatasmithSceneImportContext ImportContext(DatasmithFilePath, ImportOptions);

// 注册一个自定义的资产转换器，用于处理特定类型的 Datasmith 资产
// 例如，为某种自定义几何体属性创建自定义 UStaticMesh
class FMyCustomMeshConverter : public IDatasmithMeshConverter
{
public:
    virtual bool ConvertMesh(const TSharedRef<IDatasmithMeshElement>& MeshElement, UObject& OutStaticMesh) override
    {
        // 自定义网格转换逻辑
        // ...
        return true;
    }
};

// 获取翻译器模块并注册
FDatasmithTranslatorModule& TranslatorModule = FModuleManager::LoadModuleChecked<FDatasmithTranslatorModule>(DATASMITHTRANSLATOR_MODULE_NAME);
TSharedRef<FMyCustomMeshConverter> MyConverter = MakeShared<FMyCustomMeshConverter>();
TranslatorModule.RegisterMeshConverter(MyConverter);

// 现在执行导入时，将使用我们的自定义转换器处理匹配的网格
FDatasmithSceneImporter SceneImporter(ImportContext);
SceneImporter.Import();

// 导入完成后清理
TranslatorModule.UnregisterMeshConverter(MyConverter);
```

## Demo 示例

一个完整的、可编译的最小示例，展示如何从给定的文件路径导入一个 Datasmith 场景。
**注意**: 请确保你的项目 `Build.cs` 文件中已正确添加了必要的模块依赖。

**MyDatasmithImporter.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class UDatasmithImportOptions;

class FMyDatasmithImporter
{
public:
    /** 从指定路径导入Datasmith文件 */
    static UObject* ImportDatasmithSceneFromFile(const FString& FilePath);
};
```

**MyDatasmithImporter.cpp**
```cpp
#include "MyDatasmithImporter.h"
#include "DatasmithImportFactory.h"
#include "DatasmithImportOptions.h"
#include "DatasmithSceneImportOptions.h"

UObject* FMyDatasmithImporter::ImportDatasmithSceneFromFile(const FString& FilePath)
{
    // 1. 获取或创建导入选项
    UDatasmithImportOptions* ImportOptions = NewObject<UDatasmithImportOptions>();
    UDatasmithSceneImportOptions* SceneOptions = NewObject<UDatasmithSceneImportOptions>();
    
    // 2. 配置导入行为（可根据需要调整）
    SceneOptions->bMergeMeshes = false; // 示例：不合并网格体
    SceneOptions->MaterialImport = EDatasmithImportMaterial::Import; // 导入材质
    ImportOptions->ImportOptions = SceneOptions;

    // 3. 获取导入工厂并执行导入
    UDatasmithImportFactory* Factory = GetMutableDefault<UDatasmithImportFactory>();
    if (Factory)
    {
        return Factory->ImportFile(FilePath, ImportOptions);
    }
    return nullptr;
}
```

## 模块依赖

要使用 `DatasmithImporter` 插件的功能，你的模块需要在 `.Build.cs` 文件中添加以下依赖。这是一些非标准、具有 Datasmith 特色的模块依赖。

| 模块 | 用途 |
|---|---|
| `DatasmithCore` | Datasmith 数据格式和核心接口定义。 |
| `DatasmithContent` | Datasmith 资产的运行时内容，如 `UDatasmithScene`。 |
| `DatasmithTranslator` | 翻译器接口，用于实现自定义的资产转换逻辑。 |
| `ExternalSource` | 外部数据源抽象，支持文件和DirectLink等。 |

**注意**: `DirectLinkExtension` 和 `DirectLinkExtensionEditor` 是支持 DirectLink 实时连接的模块，仅在你需要实现或使用 DirectLink 功能时才需要依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量被截断为浮点数的警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将过时的 UE_LOG 日志宏迁移到新的 UE_LOGF 宏。 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introd | 废弃了旧版对象查询函数，引入了新的API。 |
| 2026-03-06 | `7b69892a` | clean up code changing texture properties with wrapping in PreEditChange/PostEditChange as required. | 清理修改纹理属性的代码，确保符合编辑器修改事务规范。 |
| 2026-03-05 | `1adb9f68` | New material translator work: | 新材料翻译器的工作： (提交信息不完整) |

### 维护评价

**综合评价：维护中但不活跃。**

- **创建与年龄**：插件创建于2019年，已有约7年历史，属于成熟的企业级工具。
- **更新频率与内容**：从提交历史看，近期（2026年）仍有更新，但主要集中在**编译警告修复**、**API迁移**（如日志宏）、**代码清理**和**小范围重构**。最后一条功能性更新信息（`1adb9f68`）在2026年3月，且提交信息不完整。
- **活跃度**：Epic Games 仍在维护此插件以保证其与最新引擎版本的兼容性，但**核心功能和架构已非常稳定**，近年来没有引入重大新特性。
- **已知限制**：作为 `EnabledByDefault=false` 的插件，它需要用户显式启用。其功能高度依赖 Datasmith SDK 和与其他 Enterprise 插件（如 `DatasmithContent`）的协同。
- **推荐**：**推荐使用**。这是 Unreal Engine 官方推荐的用于专业设计数据导入的解决方案，稳定可靠。尽管近期没有激动人心的新功能，但它持续得到维护，确保了兼容性。

**警告**：尽管近期有编译层面的更新，但超过1年没有观察到实质性的**功能增强或架构改进**。它是一个功能完备但处于稳定维护期的工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter/Source/DirectLinkTest) (DirectLinkTest模块包含相关测试)