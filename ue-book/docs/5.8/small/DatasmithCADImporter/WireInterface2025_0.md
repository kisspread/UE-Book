# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | 数据化CAD导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

DatasmithCADImporter 是 UE5 Datasmith 导入管线中负责 **CAD 格式文件解析与转换** 的核心插件。它并非一个独立的"导入器"，而是 Datasmith 生态中专门处理工程/工业 CAD 数据的翻译层。

该插件解决的核心问题是：**将各种 CAD 格式（如 Autodesk Alias .wire、OpenNurbs .3dm、PLM XML 等）中的几何体、材质、层级结构转换为 UE 可消费的 Datasmith 场景元素（IDatasmithScene / IDatasmithMeshElement 等）**。

与普通的 FBX/OBJ 导入不同，CAD 文件通常包含：
- 参数化曲面（NURBS/贝塞尔），需要在导入时进行**曲面细分（Tessellation）**转化为多边形网格
- B-Rep（边界表示）拓扑结构，包含壳（Shell）、面（Face）、环（Loop）、边（Edge）等层级
- 复杂的材质系统（Blinn、Lambert、Phong 等着色模型）
- 层级结构（Layer/Group），需要映射为 UE 的 Actor 层级

### 模块架构

该插件包含 20 个模块，按功能可分为以下几层：

| 层级 | 模块 | 职责 |
|---|---|---|
| **SDK 接口层** | `WireInterface2020` ~ `WireInterface2026_0`（共 10 个） | 绑定不同版本的 Autodesk Alias/Wire SDK，提供版本无关的 `IWireInterface` |
| **翻译器层** | `DatasmithWireTranslator`, `DatasmithOpenNurbsTranslator`, `DatasmithPLMXMLTranslator` | 各格式的具体翻译实现 |
| **调度层** | `DatasmithDispatcher` | 多进程/多线程调度 CAD 转换任务 |
| **几何处理层** | `CADKernelSurface`, `ParametricSurface`, `ParametricSurfaceExtension` | 曲面细分、拓扑修复 |
| **公共库层** | `CADInterfaces`, `CADLibrary`, `CADTools` | 通用 CAD 数据结构和工具 |

**WireInterface 系列模块**（本文重点分析对象）是一组按年份版本化的 SDK 绑定。每个模块封装了对应年份的 Alias/Wire C API，通过实现 `IWireInterface` 接口提供统一的加载能力。这样做的原因是：Autodesk Alias 每年发布新版本，其 .wire 文件格式和 SDK API 会随之变化，需要对应的接口模块来保证兼容性。

## 使用场景

- 你在使用 **Autodesk Alias** 设计汽车/A 类曲面，需要将 .wire 文件导入 UE 进行实时可视化 → 启用此插件，通过 Datasmith Importer 导入
- 你需要导入 **Rhino 3DM**（OpenNurbs）文件 → 此插件包含 `DatasmithOpenNurbsTranslator`
- 你在使用 **PLM 系统**（如 Teamcenter、Windchill）导出 PLM XML → 此插件包含 `DatasmithPLMXMLTranslator`
- 你需要在导入 CAD 文件时精确控制曲面细分质量（Fast/Accurate 模式）→ 使用 `CADKernelSurface` 和相关参数
- 你的 CAD 文件使用了特定年份版本的 Alias 格式 → 自动选择对应的 WireInterface 模块

> **注意**：此插件默认未启用（`EnabledByDefault: false`）。需要在 **Edit → Plugins** 中手动启用，或在项目配置中设置。

## 蓝图用法

该插件主要作为 Datasmith 导入管线的底层翻译器运行，**不直接暴露蓝图节点**。所有代码中的类和方法均未标记 `UFUNCTION(BlueprintCallable)`。

实际使用方式是通过 **Datasmith Import** 流程间接调用：

### 核心节点

由于无蓝图 API，使用方式为：

1. 通过 **Datasmith Scene Import** 界面（Content Browser → Import）导入 .wire / .3dm / PLMXML 文件
2. 通过 **Datasmith Import Action** 蓝图节点触发运行时导入（需配合 DatasmithCADTranslator 模块）

### 使用示例（Datasmith 导入流程）

```
Content Browser → 右键 → Import → 选择 .wire 文件 → Datasmith 导入对话框
    → 设置细分选项（Tessellation Options）
    → 确认导入 → 自动生成 StaticMesh + Material + Actor 层级
```

## C++ 用法

该插件的核心 C++ 接口是 `IWireInterface`，由 `FWireTranslatorImpl` 实现。

### 头文件引入

```cpp
#include "WireInterfaceModule.h"
```

### 基本用法

以下示例展示如何使用 WireInterface 加载 .wire 文件并获取 Datasmith 场景：

```cpp
// 来源: Private/WireInterfaceImpl.h
// 通过模块获取 WireInterface 实例
if (FDatasmithWireTranslatorModule::IsAvailable())
{
    // 创建翻译器实例
    FWireTranslatorImpl Translator;

    // 1. 初始化：指定 .wire 文件路径
    if (Translator.Initialize(TEXT("C:/Models/CarBody.wire")))
    {
        // 2. 配置导入设置
        FWireSettings Settings;
        Translator.SetImportSettings(Settings);

        // 3. 设置输出路径
        Translator.SetOutputPath(TEXT("C:/UE_Project/Content/Imported"));

        // 4. 加载场景（创建 Datasmith 场景元素）
        TSharedPtr<IDatasmithScene> Scene = MakeShared<IDatasmithScene>();
        if (Translator.Load(Scene))
        {
            // 场景加载成功，Scene 中包含：
            // - Actor 层级（对应 CAD 的 Layer/Group）
            // - Mesh 元素（细分后的多边形网格）
            // - 材质元素（Blinn/Lambert/Phong → PBR 材质）
        }
    }
}
```

### 进阶用法：加载单个网格元素

```cpp
// 来源: Private/WireInterfaceImpl.h
// 加载特定的 Mesh 元素并获取细分后的 MeshDescription
FWireTranslatorImpl Translator;
Translator.Initialize(TEXT("C:/Models/CarBody.wire"));

TSharedPtr<IDatasmithMeshElement> MeshElement = MakeShared<IDatasmithMeshElement>();
FDatasmithMeshElementPayload MeshPayload;

// 配置细分选项
FDatasmithTessellationOptions TessellationOptions;
// TessellationOptions 控制细分精度（Fast vs Accurate）

if (Translator.LoadStaticMesh(MeshElement, MeshPayload, TessellationOptions))
{
    // MeshPayload 包含细分后的几何数据
    // 可用于创建 UStaticMesh 等资产
}
```

### 进阶用法：使用 CADKernel 进行 B-Rep 曲面细分

```cpp
// 来源: Private/AliasModelToCADKernelConverter.h
// 使用 CADKernel 后端将 Alias B-Rep 几何转换为多边形网格
FAliasModelToCADKernelConverter Converter(TessellationOptions, ImportParameters);

// 添加 BRep 几何体（支持颜色和材质槽两种方式）
Converter.AddBRep(DagNode, Color, EAliasObjectReference::LocalReference);
// 或按材质槽索引
Converter.AddBRep(DagNode, SlotID, EAliasObjectReference::LocalReference);

// 修复拓扑（处理间隙、重叠等）
Converter.RepairTopology();

// 执行细分，输出 MeshDescription
FMeshDescription MeshDescription;
CADLibrary::FMeshParameters MeshParameters;
Converter.Tessellate(MeshParameters, MeshDescription);
```

### 进阶用法：使用 TechSoft 后端进行曲面细分

```cpp
// 来源: Private/AliasModelToTechSoftConverter.h
// TechSoft 是另一个曲面细分后端（商业库）
FAliasModelToTechSoftConverter Converter(ImportParameters);

Converter.AddBRep(DagNode, Color, EAliasObjectReference::LocalReference);
// TechSoft 会将 Alias 曲面转换为 A3D 拓扑结构后再细分
```

## Demo 示例

以下展示一个最小的 WireInterface 初始化和场景加载示例：

```cpp
// WireLoader.h
#pragma once

#include "CoreMinimal.h"
#include "WireInterfaceModule.h"
#include "IDatasmithScene.h"

class FWireLoader
{
public:
    /** 加载 .wire 文件并返回 Datasmith 场景 */
    TSharedPtr<IDatasmithScene> LoadWireFile(const FString& WireFilePath);

    /** 加载单个网格并获取 MeshDescription */
    bool LoadMesh(const FString& WireFilePath,
                  const TSharedPtr<IDatasmithMeshElement>& MeshElement,
                  FDatasmithMeshElementPayload& OutPayload);
};
```

```cpp
// WireLoader.cpp
#include "WireLoader.h"
#include "WireInterfaceImpl.h"

TSharedPtr<IDatasmithScene> FWireLoader::LoadWireFile(const FString& WireFilePath)
{
    using namespace UE_DATASMITHWIRETRANSLATOR_NAMESPACE;

    if (!FDatasmithWireTranslatorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("WireInterface 模块未加载"));
        return nullptr;
    }

    FWireTranslatorImpl Translator;

    // 初始化翻译器，指定 .wire 文件路径
    if (!Translator.Initialize(*WireFilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("无法初始化 Wire 翻译器: %s"), *WireFilePath);
        return nullptr;
    }

    // 配置导入设置
    FWireSettings Settings;
    Translator.SetImportSettings(Settings);
    Translator.SetOutputPath(FPaths::ProjectContentDir() / TEXT("Imported"));

    // 创建并加载 Datasmith 场景
    TSharedPtr<IDatasmithScene> Scene = MakeShared<IDatasmithScene>();
    if (!Translator.Load(Scene))
    {
        UE_LOG(LogTemp, Error, TEXT("Wire 场景加载失败: %s"), *WireFilePath);
        return nullptr;
    }

    UE_LOG(LogTemp, Log, TEXT("Wire 场景加载成功: %s"), *WireFilePath);
    return Scene;
}

bool FWireLoader::LoadMesh(const FString& WireFilePath,
                           const TSharedPtr<IDatasmithMeshElement>& MeshElement,
                           FDatasmithMeshElementPayload& OutPayload)
{
    using namespace UE_DATASMITHWIRETRANSLATOR_NAMESPACE;

    FWireTranslatorImpl Translator;
    if (!Translator.Initialize(*WireFilePath))
    {
        return false;
    }

    FDatasmithTessellationOptions TessOptions;
    return Translator.LoadStaticMesh(MeshElement, OutPayload, TessOptions);
}
```

## 模块依赖

该插件的核心依赖是 **第三方 CAD SDK**，而非标准 UE 模块：

| 模块 | 用途 |
|---|---|
| `TechSoft` | TechSoft 3D ACIS 内核，用于 B-Rep 曲面细分（CADInterfaces、TechSoft Converter 依赖） |
| `OpenNurbs6` | OpenNurbs 库，用于解析 Rhino .3dm 文件（DatasmithOpenNurbsTranslator 依赖） |
| `DatasmithCore` | Datasmith 核心框架（IDatasmithScene、IDatasmithMeshElement 等接口） |
| `CADKernel` | UE 内置 CAD 内核，用于曲面细分和拓扑修复（CADKernelSurface 模块依赖） |

> WireInterface 系列模块还依赖 **Autodesk Alias/Wire SDK**（通过预编译库链接），这是商业 SDK，不在 UE 源码中分发。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 新增逻辑支持 Alias 2027 版本已安装时 Wire 翻译器仍能正常工作 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将 TechSoft SDK 升级到 2026.3 版本 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新 DatasmithCAD 缓存版本号 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复函数类型转换警告在 MSVC 和 Clang 间的可移植性 |

### 维护评价

**活跃维护**。该插件近一周内（2026-05-12 ~ 2026-05-13）有 5 次提交，内容涵盖：

- **SDK 版本更新**：持续跟进 TechSoft（2026.3）和 Alias（2027）的最新版本
- **编译兼容性修复**：解决跨编译器（MSVC/Clang）的浮点精度警告
- **缓存版本管理**：定期更新 DatasmithCAD 缓存格式

该插件自 2019 年创建以来持续维护，WireInterface 系列模块从 2020 版到 2026 版逐年更新，说明 Autodesk Alias 用户群体是 Epic 重点支持的企业客户。**推荐在需要导入 Alias .wire 文件的项目中使用**。

注意事项：
- 需要手动启用（`EnabledByDefault: false`）
- WireInterface 模块依赖商业 Alias/Wire SDK，需要单独安装对应版本的 Autodesk Alias
- OpenNurbs 和 TechSoft 为第三方库，可能存在额外许可要求

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)