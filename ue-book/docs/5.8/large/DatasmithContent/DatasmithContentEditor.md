# Datasmith Content

> Content for Datasmith Importer.

| 属性 | 值 |
|---|---|
| 中文名 | 数据接驳内容 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（Datasmith场景资产、导入数据类） |
| 模块 | `DatasmithContent` (Runtime), `DatasmithContentEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2017-12-08 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithContent) | |

## 用途

DatasmithContent 插件为 Unreal Engine 的 **Datasmith 导入器**提供核心的运行时和编辑器基础内容。Datasmith 是一种企业级数据导入技术，专门用于将来自 CAD、BIM 以及其他专业设计软件（如 Revit, 3ds Max, SketchUp）的复杂场景、几何体、材质和元数据，高效、准确地转换并导入到 Unreal Engine 中。

这个插件自身不包含导入器的核心转换逻辑（该功能在 `DatasmithImporter` 插件中），而是定义了导入过程所需的关键数据类型（如 `UDatasmithScene`）、资产定义以及编辑器界面扩展。它解决的是“内容”的问题：Datasmith 导入器需要特定的资产类型和编辑器支持来存储、展示和操作导入的数据，本插件就提供了这些内容。

## 使用场景

- **建筑、工程与施工 (AEC)**：将 Revit 或 ArchiCAD 的 BIM 模型导入 UE，用于建筑可视化、VR 漫游和施工规划。
- **产品设计与制造**：将 SolidWorks, CATIA, NX 等 CAD 软件的机械零件和装配体导入 UE，用于设计评审、营销动画和交互式产品配置器。
- **数字孪生**：导入大型工厂或设施的布局数据，结合 IoT 数据在 UE 中创建实时的数字孪生体。
- **电影与虚拟制片**：将 VFX 流水线中的资产（如来自 3ds Max 的场景）通过 Datasmith 导入，保持材质和光照设置的高保真度。

## 蓝图用法

此插件主要提供编辑器扩展和数据类型，直接的运行时蓝图节点较少。其主要蓝图交互体现在对导入后的 `DatasmithScene` 资产的操作上。

### 核心资产操作

| 操作 | 说明 | 所在类 |
|---|---|---|
| **打开场景** | 在内容浏览器中双击 `.uasset` 资产，或右键选择“打开”。这会调用插件注册的 `UAssetDefinition_DatasmithScene::OpenAssets`。 | `UAssetDefinition_DatasmithScene` |
| **查看导入信息** | 在资产的“细节”面板中，可以查看和编辑其 `DatasmithImportInfo` 结构，这里包含了源文件路径等元数据，并由 `FDatasmithImportInfoCustomization` 提供自定义UI。 | `FDatasmithImportInfoCustomization` |
| **场景演员管理** | 选中场景中的 `ADatasmithSceneActor`，其“细节”面板由 `FDatasmithSceneActorDetailsPanel` 定制，提供重新导入或处理已删除演员的选项。 | `FDatasmithSceneActorDetailsPanel` |

### 使用示例（蓝图描述）

1.  **导入数据**：通过编辑器主菜单的 `Datasmith` 导入按钮，选择源文件进行导入。这将在内容浏览器中生成一个 `UDatasmithScene` 资产。
2.  **拖放到场景**：将导入的 `UDatasmithScene` 资产从内容浏览器拖放到场景中，这将自动生成一个 `ADatasmithSceneActor` 及其管理的子 Actor 树。
3.  **修改与重导入**：在源 CAD 软件中修改模型后，可以在 UE 中选中场景 Actor，在细节面板中通过插件提供的按钮触发重新导入，更新场景数据。

## C++ 用法

此插件的核心在于提供一个可扩展的编辑器模块接口 `IDatasmithContentEditorModule`，用于注册自定义的导入器和行为处理器。

### 头文件引入

```cpp
#include "DatasmithContentEditorModule.h"
```

### 基本用法

获取 `DatasmithContentEditor` 模块的单例接口，并检查其可用性。这是使用该模块任何功能的第一步。

```cpp
// 检查模块是否已加载
if (IDatasmithContentEditorModule::IsAvailable())
{
    // 获取模块实例
    IDatasmithContentEditorModule& DatasmithEditorModule = IDatasmithContentEditorModule::Get();

    // 接下来可以调用模块接口提供的各种方法...
}
```

### 进阶用法

注册一个自定义的 Datasmith 导入处理器。这允许其他插件向 Datasmith 导入对话框添加新的导入器类型。

```cpp
// 创建一个描述导入器的结构体
FImporterDescription MyImporterDesc;
MyImporterDesc.Label = NSLOCTEXT("MyPlugin", "ImporterLabel", "My Custom Importer");
MyImporterDesc.Description = NSLOCTEXT("MyPlugin", "ImporterDesc", "Imports data from my custom format.");
MyImporterDesc.StyleName = "ContentBrowser.AssetActions.Import"; // 使用标准导入按钮样式
MyImporterDesc.Formats.Add("myformat");
MyImporterDesc.FilterString = TEXT("My Custom Files (*.myformat)|*.myformat");

// 绑定一个处理器委托，该委托将在用户选择此导入器时被调用
MyImporterDesc.Handler = FOnCreateDatasmithImportHandler::CreateLambda([]() -> TSharedPtr<IDataprepImporterInterface>
{
    // 返回你自定义的导入处理器实例
    return MakeShared<FMyCustomDatasmithImporter>();
});

// 注册导入器
IDatasmithContentEditorModule& EditorModule = IDatasmithContentEditorModule::Get();
EditorModule.RegisterDatasmithImporter(MyPluginInstance, MyImporterDesc);

// 在插件关闭时，记得取消注册
EditorModule.UnregisterDatasmithImporter(MyPluginInstance);
```

## Demo 示例

以下是一个最小的 C++ 模块示例，展示如何获取 `DatasmithContentEditor` 模块接口并验证其可用性。

**MyModule.h**
```cpp
#pragma once

#include "Modules/ModuleManager.h"

class FMyModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**MyModule.cpp**
```cpp
#include "MyModule.h"
#include "DatasmithContentEditorModule.h" // 包含DatasmithContentEditor模块头文件

void FMyModule::StartupModule()
{
    // 在启动时检查DatasmithContentEditor模块是否可用
    if (IDatasmithContentEditorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Log, TEXT("DatasmithContentEditor module is available."));
    }
}

void FMyModule::ShutdownModule()
{
    // 清理代码...
}

IMPLEMENT_MODULE(FMyModule, MyModule)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `VariantManagerContent` | 提供变体管理器（Variant Manager）所需的内容资产。Datasmith导入的场景可能包含变体数据，因此依赖此模块。 |
| `DatasmithContent` | (运行时模块) 提供核心的 Datasmith 场景资产定义（如 `UDatasmithScene`），被 `DatasmithContentEditor` 模块依赖。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF，可能是为了日志功能增强。 |
| 2026-03-24 | `69a7403a` | Fixed cooking failure duue to ensure | 修复了因一个 `ensure` 断言导致的打包失败问题。 |
| 2026-03-24 | `76f61985` | Deprecated UDatasmithStaticMeshCADImportData class as it is not used anymore and introduces a securi | 废弃了未使用且存在安全风险的 `UDatasmithStaticMeshCADImportData` 类。 |
| 2026-03-23 | `06410f9f` | [Backout] - CL52072615 | 回滚了一个之前的变更 (CL52072615)。 |
| 2026-03-23 | `c14d73ba` | Deprecated UDatasmithStaticMeshCADImportData class as it is not used anymore and introduces a securi | （同上，为同一变更的首次尝试） |

### 维护评价

DatasmithContent 是 Unreal Engine 企业版（Enterprise）功能的重要组成部分，自 2017 年创建以来一直处于**活跃维护**状态。从近期的 git 提交可以看出，维护团队仍在持续工作：
1.  **进行重构**：迁移到更现代的日志宏 (`UE_LOGF`)。
2.  **修复关键问题**：及时修复了影响打包流程的 `ensure` 断言错误。
3.  **清理代码**：主动废弃未使用的、存在安全隐患的类，表明对代码质量和安全性的关注。
4.  **尽管有回滚操作**，但表明变更被谨慎评估。

该插件与 UE 版本同步更新，与核心的 Datasmith 导入器紧密关联，是完成专业数据导入工作流的必备插件。对于需要导入 CAD/BIM 数据的项目，**强烈推荐使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithContent)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)