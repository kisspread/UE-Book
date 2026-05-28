# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | CAD文件导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

该插件是 Epic Games 针对企业级应用提供的 CAD 数据导入解决方案。它并非一个单一的导入器，而是一个**框架和工具集**，旨在将来自多种专业 CAD 软件（如 CATIA, SolidWorks, NX, Alias 等）的复杂工程数据（包含精确几何体、参数化曲面、层级结构和元数据）高效、准确地转换并导入到 Unreal Engine 中。其核心价值在于保留 CAD 数据的原始设计意图和结构，同时进行必要的优化（如曲面细分）以适应实时渲染的需求。

“DatasmithWireTranslator” 子模块特指用于处理 **Autodesk Alias** 模型数据的翻译器。

## 使用场景

-   你是一名汽车或产品设计师，使用 Autodesk Alias 创建了复杂的 A 级曲面模型，需要将其导入 UE 进行实时可视化评审或虚拟原型展示。
-   你的团队使用 CATIA、SolidWorks、NX 等工业 CAD 软件进行机械设计，需要将装配体导入 UE 进行数字孪生、交互式技术文档或培训模拟。
-   你需要处理包含复杂曲面和精确尺寸的工程数据，并要求导入后的模型保持较高的几何精度和层级结构。

## 蓝图用法

该插件的核心功能主要通过 C++ 接口和编辑器导入流程提供，但部分配置选项暴露给蓝图。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Settings` (属性) | 配置 Wire (Alias) 文件的导入选项，如是否使用图层作为 Actor、按组合并几何体等。 | `UDatasmithWireOptions` |

### 使用示例（蓝图描述）

虽然核心翻译逻辑在 C++ 层，但可以在蓝图或编辑器中通过 “Datasmith 导入器” 对话框配置 `UDatasmithWireOptions` 中的属性。通常，用户在导入 .wire 文件时，会在弹出的导入选项面板中看到 “Wire Translation Options” 分类，可以勾选 `bUseLayerAsActor` 或 `bMergeGeometryByGroup` 等选项来控制最终生成的 Actor 结构和网格合并策略。

## C++ 用法

该插件的主要交互接口是 C++。以 `DatasmithWireTranslator` 模块为例。

### 头文件引入

```cpp
#include "IWireInterface.h"
#include "DatasmithWireTranslator.h"
```

### 基本用法

通过 `IWireInterface` 接口加载 Wire 文件并获取网格数据。
*(来源: Public/IWireInterface.h)*

```cpp
// 1. 创建或获取一个 WireInterface 实例（通常由翻译器内部管理）
TSharedPtr<IWireInterface> WireInterface = /* ... */;

// 2. 初始化接口并加载文件
if (WireInterface->Initialize(TEXT("path/to/model.wire")))
{
    // 创建一个用于存放场景的 Datasmith 场景对象
    TSharedPtr<IDatasmithScene> Scene = FDatasmithSceneFactory::CreateScene(TEXT("MyImportedScene"));

    // 设置导入参数
    FWireSettings Settings;
    Settings.bUseLayerAsActor = true;
    Settings.bMergeGeometryByGroup = false;
    WireInterface->SetImportSettings(Settings);

    // 加载场景，这会填充 Scene 对象中的各种元素（Actor, Mesh等）
    if (WireInterface->Load(Scene))
    {
        // 场景已成功加载，可以遍历 Scene 中的元素进行后续处理
        UE_LOG(LogTemp, Log, TEXT("Wire scene loaded successfully."));
    }
}

// 3. 对于场景中的每个网格元素，可以加载其实际的几何数据
TSharedPtr<IDatasmithMeshElement> MeshElement = /* 从Scene中获取 */;
FDatasmithMeshElementPayload MeshPayload;
FDatasmithTessellationOptions TessOptions; // 通常从选项获取

if (WireInterface->LoadStaticMesh(MeshElement, MeshPayload, TessOptions))
{
    // MeshPayload 现在包含了顶点、三角形等网格数据，可用于创建 UStaticMesh
}
```

### 进阶用法

`FDatasmithWireTranslator` 是集成到 Datasmith 管线中的完整翻译器，展示了更复杂的生命周期管理。
*(来源: Private/DatasmithWireTranslator.h)*

```cpp
// 假设已获得一个 FDatasmithWireTranslator 实例（通常在编辑器导入流程中由工厂创建）
FDatasmithWireTranslator Translator;

// 1. 初始化翻译器，声明其能力
FDatasmithTranslatorCapabilities Capabilities;
Translator.Initialize(Capabilities);

// 2. 检查源文件是否受支持
FDatasmithSceneSource Source;
Source.SetSourceFile(TEXT("model.wire"));
if (Translator.IsSourceSupported(Source))
{
    // 3. 设置导入选项（如前所述的 WireSettings）
    TArray<TObjectPtr<UDatasmithOptionsBase>> Options;
    Translator.GetSceneImportOptions(Options); // 获取默认选项
    // ... 配置 Options 中的 UDatasmithWireOptions ...
    Translator.SetSceneImportOptions(Options);

    // 4. 加载整个场景
    TSharedRef<IDatasmithScene> OutScene = FDatasmithSceneFactory::CreateScene(TEXT("ImportedWireScene"));
    if (Translator.LoadScene(OutScene))
    {
        // 5. 按需加载各个网格的负载
        for (int32 i = 0; i < OutScene->GetMeshesCount(); ++i)
        {
            TSharedRef<IDatasmithMeshElement> Mesh = OutScene->GetMesh(i);
            FDatasmithMeshElementPayload Payload;
            if (Translator.LoadStaticMesh(Mesh, Payload))
            {
                // 使用 Payload 创建引擎内的 UStaticMesh 资产
            }
        }
    }

    // 6. 使用完毕后卸载场景以释放资源
    Translator.UnloadScene();
}
```

## Demo 示例

一个最小的、通过 `IWireInterface` 加载 Wire 文件并打印网格信息的示例。
```cpp
// MyWireLoader.h
#pragma once
#include "CoreMinimal.h"
#include "IWireInterface.h"

class FMyWireLoader
{
public:
    void LoadAndPrintInfo(const FString& WireFilePath);
};
```

```cpp
// MyWireLoader.cpp
#include "MyWireLoader.h"
#include "DatasmithSceneFactory.h"

void FMyWireLoader::LoadAndPrintInfo(const FString& WireFilePath)
{
    // 获取接口实现 (实际注册由模块启动时完成)
    TSharedPtr<IWireInterface> WireInterface = IWireInterface::GetInterface(/* 可能需要版本号 */);
    if (!WireInterface)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to get Wire Interface."));
        return;
    }

    if (!WireInterface->Initialize(*WireFilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to initialize Wire Interface for: %s"), *WireFilePath);
        return;
    }

    TSharedPtr<IDatasmithScene> Scene = FDatasmithSceneFactory::CreateScene(TEXT("TempScene"));
    FWireSettings Settings;
    Settings.bUseLayerAsActor = false; // 按需求设置
    WireInterface->SetImportSettings(Settings);

    if (WireInterface->Load(Scene))
    {
        UE_LOG(LogTemp, Log, TEXT("Scene loaded. Meshes found: %d"), Scene->GetMeshesCount());
        for (int32 i = 0; i < Scene->GetMeshesCount(); ++i)
        {
            TSharedPtr<IDatasmithMeshElement> Mesh = Scene->GetMesh(i);
            if (Mesh.IsValid())
            {
                UE_LOG(LogTemp, Log, TEXT("  Mesh %d: %s"), i, *Mesh->GetName());
            }
        }
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load scene from Wire file."));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TechSoft` | 提供底层的 CAD 文件格式读取和几何处理核心库（如 HOOPS Exchange）。 |
| `OpenNurbs6` | 用于读取和解析 Rhino 3DM 文件格式（由 DatasmithOpenNurbsTranslator 使用）。 |
| `DatasmithCore` | 提供 Datasmith 的核心接口、数据结构（IDatasmithScene等）和工厂。 |
| `ParametricSurface` | 提供参数化曲面（如来自 CATIA、NX 的精确曲面）到细分曲面的转换支持。 |
| `CADLibrary` | 提供 CAD 处理的通用工具、数据类型和跨格式支持库。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数的编译警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed. | 增加逻辑，使 Wire 翻译器在安装 Alias 2027 时也能工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将 TechSoft 依赖库更新至 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 DatasmithCAD 缓存的版本号。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器之间可移植。 |

### 维护评价

**综合评价：活跃维护中的企业级工具。**

该插件创建于 2019 年，作为 Epic Games 企业解决方案的一部分，具有较长的历史。从最近的提交记录（2026年5月）来看，插件仍在进行**非常积极的维护**，更新内容包括：修复编译警告（提升代码健壮性）、支持最新版本的 CAD 软件（Alias 2027）、更新核心依赖库（TechSoft 2026.3），以及改进跨平台兼容性。

-   **优势**：是 UE 中处理专业 CAD 数据的事实标准方案，功能强大，格式支持广泛，且有 Epic 的官方维护。
-   **注意事项**：该插件 **默认未启用** (`EnabledByDefault: false`)，需要在项目设置中手动启用。它依赖于第三方商业库（TechSoft），完整功能可能需要相应的许可证。
-   **推荐**：对于任何需要从专业 CAD 软件导入高精度模型的企业级项目或高端可视化应用，强烈推荐使用。对于独立开发者或小型项目，如果不需要导入复杂的工程 CAD 格式，则无需启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests) (可能存在)