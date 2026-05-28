# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | Datasmith CAD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

本插件是 Datasmith 导入流水线的 CAD 格式后端，专门处理各种工业 CAD 文件的导入。它解决的核心问题是：将 CAD 软件（CATIA、SolidWorks、NX、Rhino、Alias 等）产生的工程级三维数据，转换为 Unreal Engine 可以渲染的网格和场景层级结构。

插件通过以下机制实现 CAD 导入：
- **场景图构建**（Scene Graph Builder）：解析 CAD 装配体的层级结构（实例、引用、Body），映射为 Datasmith 的 Actor 层级
- **网格构建**（Mesh Builder）：将 CAD 的参数化曲面（NURBS、B-Rep 等）转换为三角化网格（MeshDescription）
- **材质映射**：保留 CAD 模型中的颜色和材质信息，转换为 UE 的 PBR 材质
- **多格式支持**：通过不同的 Translator 子模块支持不同 CAD 格式

**重要提示**：此插件默认未启用（`EnabledByDefault: false`），需要在项目的 Plugin 设置中手动启用。

## 使用场景

- 你正在为汽车、航空、建筑等行业制作可视化 → 需要导入 CATIA/NX/SolidWorks 的 CAD 模型
- 你有 Rhino (.3dm) 格式的工业设计模型 → 使用 OpenNurbs Translator 子模块
- 你有 Autodesk Alias (.wire) 的汽车 A 面数据 → 使用 Wire Translator 子模块
- 你有 Siemens PLM XML 格式的产品数据 → 使用 PLMXML Translator 子模块
- 你需要保持 CAD 装配体的层级结构和实例化关系 → 此插件会保留完整的场景图

## 蓝图用法

本插件主要作为 Datasmith 导入流水线的内部翻译器，没有暴露 BlueprintCallable 函数。使用方式是通过 Datasmith 的标准导入流程（Datasmith 导入面板或 `UDatasmithImportFactory`），插件会在后台自动处理 CAD 格式的转换。

### 使用方式

1. 在项目设置中启用 **Datasmith CAD Importer** 插件
2. 重启编辑器
3. 通过 **Datasmith 导入面板**（工具栏 → Datasmith → Import）导入 CAD 文件
4. 支持的格式会自动由对应的 Translator 处理

## C++ 用法

本插件主要供 Datasmith 内部调用，公共 API 较少。以下是关键的可编程接口。

### 头文件引入

```cpp
#include "DatasmithCADTranslatorModule.h"
#include "DatasmithSceneGraphBuilder.h"
#include "DatasmithMeshBuilder.h"
```

### 基本用法

获取模块实例和缓存目录：

```cpp
// 来源: Public/DatasmithCADTranslatorModule.h
if (FDatasmithCADTranslatorModule::IsAvailable())
{
    FDatasmithCADTranslatorModule& Module = FDatasmithCADTranslatorModule::Get();
    FString CacheDir = Module.GetCacheDir();
    UE_LOG(LogTemp, Log, TEXT("CAD cache directory: %s"), *CacheDir);
}
```

### 进阶用法

通过 Datasmith 翻译器接口加载 CAD 场景和网格（通常由 Datasmith 内部调用）：

```cpp
// 来源: Private/DatasmithCADTranslator.h
// 获取 CAD 翻译器（通过 Datasmith 的翻译器注册机制）
FDatasmithCADTranslator Translator;

// 配置翻译器能力
FDatasmithTranslatorCapabilities Capabilities;
Translator.Initialize(Capabilities);

// 检查源文件是否支持
FDatasmithSceneSource Source;
// ... 设置源文件路径 ...
if (Translator.IsSourceSupported(Source))
{
    // 加载整个 CAD 场景（包括层级结构、材质等）
    TSharedRef<IDatasmithScene> Scene = FDatasmithScene::Create();
    Translator.LoadScene(Scene);

    // 加载单个网格
    TSharedRef<IDatasmithMeshElement> MeshElement = /* ... */;
    FDatasmithMeshElementPayload Payload;
    Translator.LoadStaticMesh(MeshElement, Payload);

    // 用完后卸载
    Translator.UnloadScene();
}
```

使用场景图构建器从 CAD 存档数据构建 Datasmith 场景层级：

```cpp
// 来源: Public/DatasmithSceneGraphBuilder.h
// 创建场景图构建器
TMap<uint32, FString> CADFileToSceneGraphFile;
// ... 填充 CAD 文件到场景图描述文件的映射 ...

TSharedRef<IDatasmithScene> Scene = FDatasmithScene::Create();
FDatasmithSceneSource Source;
CADLibrary::FImportParameters ImportParams;

FDatasmithSceneGraphBuilder GraphBuilder(
    CADFileToSceneGraphFile,
    CachePath,
    Scene,
    Source,
    ImportParams
);

// 构建完整场景图
bool bSuccess = GraphBuilder.Build();
```

使用网格构建器从 CAD 体数据生成网格描述：

```cpp
// 来源: Public/DatasmithMeshBuilder.h
// 从缓存文件构建
TMap<uint32, FString> CADFileToMeshFile;
FDatasmithMeshBuilder MeshBuilder(CADFileToMeshFile, CachePath, ImportParams);

// 或从内存中的体网格数据构建
TArray<CADLibrary::FBodyMesh> BodyMeshSet;
// ... 填充体网格数据 ...
FDatasmithMeshBuilder MeshBuilder2(BodyMeshSet, ImportParams);

// 获取网格描述
TSharedRef<IDatasmithMeshElement> MeshElement = /* ... */;
CADLibrary::FMeshParameters MeshParams;
TOptional<FMeshDescription> MeshDesc = MeshBuilder.GetMeshDescription(MeshElement, MeshParams);

if (MeshDesc.IsSet())
{
    // 使用网格描述数据
    FMeshDescription& Mesh = MeshDesc.GetValue();
}
```

## Demo 示例

以下是一个通过 Datasmith 公共 API 导入 CAD 文件的最小示例：

```cpp
// DatasmithCADImportExample.h
#pragma once

#include "CoreMinimal.h"

class FDatasmithCADImportExample
{
public:
    /** 导入指定路径的 CAD 文件到当前关卡 */
    static bool ImportCADFile(const FString& FilePath);
};
```

```cpp
// DatasmithCADImportExample.cpp
#include "DatasmithCADImportExample.h"
#include "DatasmithCADTranslatorModule.h"
#include "DatasmithSceneFactory.h"
#include "DatasmithSceneGraphBuilder.h"
#include "DatasmithMeshBuilder.h"
#include "DatasmithImportOptions.h"

bool FDatasmithCADImportExample::ImportCADFile(const FString& FilePath)
{
    // 确保 CAD 翻译器模块已加载
    if (!FDatasmithCADTranslatorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("DatasmithCADTranslator module is not available. "
            "Please enable the DatasmithCADImporter plugin."));
        return false;
    }

    FDatasmithCADTranslatorModule& CADModule = FDatasmithCADTranslatorModule::Get();
    FString CacheDir = CADModule.GetCacheDir();

    // 创建 Datasmith 场景
    TSharedRef<IDatasmithScene> Scene = FDatasmithScene::Create(TEXT("CADImportScene"));

    // 配置导入参数
    CADLibrary::FImportParameters ImportParams;
    // ImportParams 可配置公差、缝合精度等

    // 通过 Datasmith 翻译器系统加载（实际使用中由 Datasmith 框架调度）
    // 此处演示直接使用构建器的流程
    TMap<uint32, FString> FileMap;
    FDatasmithSceneSource Source;

    FDatasmithSceneGraphBuilder GraphBuilder(
        FileMap,
        CacheDir,
        Scene,
        Source,
        ImportParams
    );

    // 加载场景图描述并构建层级
    GraphBuilder.LoadSceneGraphDescriptionFiles();
    bool bBuilt = GraphBuilder.Build();

    if (bBuilt)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully built scene graph with %d actors"),
            Scene->GetActorsCount());
    }

    return bBuilt;
}
```

## 模块依赖

本插件包含多个模块，以下是关键的外部依赖：

| 模块 | 用途 |
|---|---|
| `TechSoft` | TechSoft CAD 内核库，用于解析多种工业 CAD 格式（STEP、IGES、CATIA、NX 等） |
| `OpenNurbs6` | OpenNURBS 库，用于解析 Rhino (.3dm) 文件 |
| `DatasmithContent` | Datasmith 内容模块，提供 Datasmith 资产类型定义 |
| `DatasmithCore` | Datasmith 核心模块，提供场景、Actor、Mesh 等接口定义 |
| `MeshDescription` | 网格描述数据结构，用于存储转换后的三角化网格 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | Wire 翻译器新增对 Alias 2027 的兼容支持 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 升级 TechSoft CAD 内核到 2026.3 版本 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新 Datasmith CAD 缓存版本格式 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复跨编译器（MSVC/Clang）的类型转换警告 |

### 维护评价

**✅ 活跃维护**

本插件维护状态良好：
- **持续更新**：最近 5 次提交集中在 2026 年 5 月，涵盖第三方库升级（TechSoft 2026.3）、新版本 CAD 软件支持（Alias 2027）、编译兼容性修复等实质性改动
- **WireInterface 模块持续扩展**：从 2020 版到 2026_0 版本的 WireInterface 模块表明对 Autodesk Alias 每个新版本都在跟进支持
- **企业级插件**：由 Epic Games 官方维护，作为 Datasmith 企业导入管线的核心组件
- **注意**：此插件默认未启用，需要手动在项目设置中开启
- **注意**：依赖第三方闭源库 TechSoft，该库需要单独获取许可

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/ImportExportTests)