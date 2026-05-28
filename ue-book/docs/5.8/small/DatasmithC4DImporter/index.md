# Datasmith C4D Importer

> Adds support for importing content from Cinema4D applications into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | C4D导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithC4DTranslator` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithC4DImporter) | |

## 用途

DatasmithC4DImporter 是一个运行时翻译器模块，作为 Unreal Engine 的 Datasmith 管道的一部分。它主要解决的是将 Maxon Cinema 4D (`.c4d`) 应用程序创建的场景资产，包括几何体、材质、纹理、灯光、摄像机以及动画数据，无缝转换并导入到 Unreal Engine 中的问题。

该插件通过集成 Cineware SDK 来读取和解析 `.c4d` 文件的内部数据结构，然后将这些数据映射到 Datasmith 的标准化场景元素（如 `IDatasmithScene`、`IDatasmithActorElement` 等）。这使得建筑可视化、产品设计、工业设计等领域的艺术家和设计师，能够将在 Cinema 4D 中完成的复杂场景和动画资产高效地集成到 UE 项目中，用于实时渲染、虚拟现实或动态叙事等应用。

## 使用场景

-   **建筑与产品可视化**：你在 Cinema 4D 中创建了高质量的建筑模型或产品展示动画，需要将其导入 UE 中进行实时交互或制作高品质的离线渲染。
-   **跨软件协作**：团队使用 Cinema 4D 作为建模和动画工具，而其他成员使用 Unreal Engine 进行最终场景整合与发布。
-   **保留材质与动画**：你希望完整保留 Cinema 4D 材质通道、纹理映射以及关键帧动画、克隆器动画等，避免在 UE 中重新制作。
-   **批量资产迁移**：需要将一系列 `.c4d` 文件批量转换为 UE 可用的 Datasmith 资产格式。

## 蓝图用法

根据源码分析，该插件的模块 `DatasmithC4DTranslator` 主要是一个底层翻译器，实现了 `IDatasmithTranslator` 接口，其功能通常由 Datasmith 导入器（Importer）自动调用。没有发现直接暴露给蓝图（BlueprintCallable）的公共函数或节点。所有导入操作均通过 Datasmith 的标准导入流程触发。

## C++ 用法

该插件的核心是 `FDatasmithC4DImporter` 类，它负责实际的 Cineware 场景解析与 Datasmith 元素构建。使用者通常通过 Datasmith 的 `FDatasmithC4DTranslator` 与之交互。

### 头文件引入

```cpp
// 引入 Datasmith 翻译器接口
#include "DatasmithC4DTranslatorModule.h"
// 如果需要直接操作导入器，则引入其私有头文件（不推荐，应通过翻译器接口）
// #include "DatasmithC4DImporter.h"
```

### 基本用法

典型的使用模式是实例化翻译器并指示其加载场景。以下代码展示了通过 `FDatasmithC4DTranslator` 加载一个 `.c4d` 文件的基本流程（**注意：实际使用中通常由 Datasmith Importer 自动调度**）。

```cpp
// 来源于 DatasmithC4DTranslator.h 中的接口实现
TSharedRef<IDatasmithScene> DatasmithScene = MakeShared<FDatasmithScene>();
FDatasmithC4DTranslator Translator;

// 初始化翻译器能力
FDatasmithTranslatorCapabilities Capabilities;
Translator.Initialize(Capabilities);

// 检查翻译器是否支持该文件
if (Capabilities.bIsEnabled && Translator.CanImport(FilePath))
{
    // 加载场景，解析 .c4d 文件
    if (Translator.LoadScene(DatasmithScene))
    {
        // 此时 DatasmithScene 已经填充了从 C4D 导入的场景数据
        // 可以将此场景交给 DatasmithImporter 进行后续资产创建
    }
    // 使用完毕后卸载场景，释放 Cineware 资源
    Translator.UnloadScene();
}
```

### 进阶用法：自定义导入选项

可以通过设置 `UDatasmithC4DImportOptions` 来控制导入行为。以下示例展示了如何配置导入选项，例如强制生成法线并缩放整个场景。

```cpp
// 来源于 DatasmithC4DImportOptions.h
UDatasmithC4DImportOptions* ImportOptions = NewObject<UDatasmithC4DImportOptions>();
ImportOptions->bAlwaysGenerateNormals = true;
ImportOptions->ScaleVertices = 100.0f; // 例如，将 C4D 的厘米单位缩放为 UE 的米单位

TArray<TObjectPtr<UDatasmithOptionsBase>> OptionsArray;
OptionsArray.Add(ImportOptions);
Translator.SetSceneImportOptions(OptionsArray);

// 之后调用 Translator.LoadScene(DatasmithScene) 将使用这些选项进行导入
```

### 进阶用法：处理网格体与序列

在 `FDatasmithC4DImporter` 内部，它提供了更细粒度的控制。例如，当需要单独获取某个网格体的数据时，可以使用 `GetGeometriesForMeshElementAndRelease` 函数（但这是翻译器内部流程的一部分）。

```cpp
// 概念性代码，来源于 DatasmithC4DImporter.h
TSharedRef<IDatasmithMeshElement> MeshElement = ...; // 已存在的网格体元素
TArray<FMeshDescription> MeshDescriptions;

// 从缓存中获取并释放为该网格体元素生成的 MeshDescription 数据
Importer->GetGeometriesForMeshElementAndRelease(MeshElement, MeshDescriptions);

// 现在可以使用 MeshDescriptions 来构建 UStaticMesh 等资产
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示了如何通过翻译器接口加载一个 Cinema 4D 文件。

```cpp
// MyC4DImporter.h
#pragma once

#include "CoreMinimal.h"

class IDatasmithScene;

class FMyC4DImporter
{
public:
    bool ImportC4DFile(const FString& C4DFilePath);
};
```

```cpp
// MyC4DImporter.cpp
#include "MyC4DImporter.h"
#include "DatasmithC4DTranslatorModule.h"
#include "DatasmithScene.h"

bool FMyC4DImporter::ImportC4DFile(const FString& C4DFilePath)
{
    // 检查翻译器模块是否可用
    if (!IDatasmithC4DTranslatorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("DatasmithC4DTranslator 模块未加载。请在插件设置中启用 DatasmithC4DImporter。"));
        return false;
    }

    IDatasmithC4DTranslatorModule& TranslatorModule = IDatasmithC4DTranslatorModule::Get();
    TSharedPtr<IDatasmithTranslator> Translator = TranslatorModule.GetFirstTranslator(C4DFilePath);
    if (!Translator.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("未找到支持文件 '%s' 的翻译器。"), *C4DFilePath);
        return false;
    }

    // 创建输出场景
    TSharedRef<IDatasmithScene> Scene = FDatasmithScene::Create();

    // 初始化并加载
    FDatasmithTranslatorCapabilities Capabilities;
    Translator->Initialize(Capabilities);
    if (Capabilities.bIsEnabled)
    {
        bool bSuccess = Translator->LoadScene(Scene);
        if (bSuccess)
        {
            UE_LOG(LogTemp, Log, TEXT("成功导入 C4D 场景。场景包含 %d 个顶层 Actor。"), Scene->GetActorsCount());
            // 此处可以将 `Scene` 传递给 Datasmith 的资产创建流水线
        }
        Translator->UnloadScene(); // 清理资源
        return bSuccess;
    }

    return false;
}
```

## 模块依赖

该插件依赖于 Datasmith 核心插件。要在你的模块中使用此翻译器，需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `DatasmithImporter` | Datasmith 核心导入器框架，提供 `IDatasmithTranslator` 等基础接口 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量截断为浮点数时产生的编译器警告。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了日志打印中格式化说明符与参数位数不匹配的问题（32位与64位）。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到 UE_LOGF（可能是新的日志宏或函数）。 |
| 2026-02-19 | `8db862b6` | Fixed crash of editor | 修复了编辑器崩溃的问题。 |
| 2026-02-10 | `901cd7d3` | Fixed crash of Automotive templates | 修复了汽车类项目模板的崩溃问题。 |

### 维护评价

DatasmithC4DImporter 插件自2019年创建，已有约7年历史。从近期（2026年2月至5月）的提交记录来看，该插件仍处于**活跃维护**状态。维护工作主要集中在：
1.  **编译器兼容性**：修复了在严格浮点模式和不同平台下产生的编译警告。
2.  **稳定性**：修复了编辑器和特定模板（汽车模板）相关的崩溃问题，提升了可靠性。
3.  **代码维护**：进行了代码迁移（如日志宏更新）。

插件虽然默认未启用（`EnabledByDefault: false`），但作为 Epic 官方维护的 Datasmith 生态核心组件之一，其稳定性和与新版 UE 的兼容性得到了持续保障。对于需要从 Cinema 4D 导入资产的用户，这是一个**推荐使用**的官方解决方案。需注意，该插件依赖于外部的 Cineware SDK，其授权和获取方式可能需要另行确认。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithC4DImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithC4DImporter/Tests)（如果存在，通常在插件目录或 Engine/Tests 下）