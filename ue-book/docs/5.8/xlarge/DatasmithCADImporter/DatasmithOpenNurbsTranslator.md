# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | CAD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

DatasmithCADImporter 是 Datasmith 管线中负责处理 **CAD 工业格式**的扩展插件。它解决的核心问题是：将各种 CAD 软件（Rhino、Alias、STEP、IGES 等）生成的参数化曲面模型和 BRep（边界表示）几何体，转换为 Unreal Engine 可消费的网格数据。

该插件包含两条主要的转换管线：
1. **OpenNurbs 管线**（`DatasmithOpenNurbsTranslator`）：处理 Rhino 的 `.3dm` 文件，利用 OpenNurbs 库解析 NURBS 曲面和 BRep 几何，再通过 CADKernel 或 TechSoft 后端进行曲面细分（tessellation）
2. **Wire 管线**（`DatasmithWireTranslator` + 多版本 `WireInterface`）：处理 Autodesk Alias 的 `.wire` 文件，每个 WireInterface 模块对应一个 Alias 版本（2020–2026）
3. **PLMXML 管线**（`DatasmithPLMXMLTranslator`）：处理 Teamcenter 的 PLMXML 格式

插件默认不启用（`EnabledByDefault: false`），需要在项目设置中手动开启。部分功能依赖第三方商业库（TechSoft HOOPS、OpenNurbs6）。

## 使用场景

- 你在用 Rhino 建模并将 `.3dm` 文件导入 Unreal → 使用 Datasmith CAD Importer 的 OpenNurbs Translator
- 你在汽车/工业设计领域使用 Autodesk Alias 建模 → 使用 Datasmith CAD Importer 的 Wire Translator
- 你需要从 Teamcenter PLM 系统导入 CAD 数据 → 使用 PLMXML Translator
- 你需要在导入时选择"原始 NURBS 细分"还是"使用原始网格（保留 UV）"→ 使用 OpenNurbs 导入选项
- 你需要精确控制 CAD 模型的曲面细分质量和容差 → 使用插件提供的细分选项

## 蓝图用法

该插件主要为运行时（Runtime）翻译器，蓝图层面的直接交互较少，主要通过 Datasmith 导入选项对话框进行配置。

### 核心配置结构

| 结构体/枚举 | 说明 |
|---|---|
| `FDatasmithOpenNurbsOptions` | OpenNurbs 导入的几何与细分选项 |
| `EDatasmithOpenNurbsBrepTessellatedSource` | 几何体来源选择：Unreal NURBS 细分 或 原始渲染网格 |
| `UDatasmithOpenNurbsImportOptions` | OpenNurbs 导入选项的 UObject 包装，可在项目设置中持久化 |

### 导入模式说明

| 模式 | 行为 |
|---|---|
| `UseUnrealNurbsTessellation` | 将 BRep 数据在 Unreal 内部进行 NURBS 曲面细分，质量可控但导入较慢 |
| `UseRenderMeshes` | 直接使用文件中已有的渲染网格和 UV，导入速度快但不可编辑几何 |

## C++ 用法

### 头文件引入

```cpp
#include "DatasmithOpenNurbsTranslatorModule.h"
#include "DatasmithOpenNurbsImportOptions.h"
```

### 基本用法 — 获取模块引用

```cpp
// 来源: Public/DatasmithOpenNurbsTranslatorModule.h

// 检查模块是否已加载
if (FDatasmithOpenNurbsTranslatorModule::IsAvailable())
{
    // 获取临时目录（用于 CAD 缓存）
    FDatasmithOpenNurbsTranslatorModule& Module = FDatasmithOpenNurbsTranslatorModule::Get();
    FString TempDir = Module.GetTempDir();
}
```

### 基本用法 — 配置导入选项

```cpp
// 来源: Public/DatasmithOpenNurbsImportOptions.h

// 创建 OpenNurbs 导入选项
UDatasmithOpenNurbsImportOptions* Options = NewObject<UDatasmithOpenNurbsImportOptions>();

// 使用原始渲染网格（快速导入，保留原始 UV）
Options->Options.Geometry = EDatasmithOpenNurbsBrepTessellatedSource::UseRenderMeshes;

// 或使用 Unreal NURBS 细分（精确但慢）
Options->Options.Geometry = EDatasmithOpenNurbsBrepTessellatedSource::UseUnrealNurbsTessellation;

// 设置细分参数（继承自 FDatasmithTessellationOptions）
// Options->Options.ChordTolerance = 0.1f;
// Options->Options.MaxEdgeLength = 10.0f;
```

### 进阶用法 — BRep 转换（内部 API）

该模块的 BRep 转换器是内部类，用于将 OpenNurbs 的 BRep 几何转换为 CADKernel 或 TechSoft 的内部表示：

```cpp
// 来源: Private/OpenNurbsBRepToCADKernelConverter.h
// 仅供插件内部使用，以下为概念示例

CADLibrary::FImportParameters ImportParams;
FDatasmithTessellationOptions TessOptions;

// CADKernel 后端转换器
FOpenNurbsBRepToCADKernelConverter Converter(ImportParams, TessOptions);

// 将 ON_Brep 添加到转换器，带偏移量（用于将网格枢轴点放在表面边界框中心）
ON_Brep Brep;
ON_3dVector Offset(0, 0, 0);
Converter.AddBRep(Brep, Offset);
```

```cpp
// 来源: Private/OpenNurbsBRepToTechSoftConverter.h

// TechSoft 后端转换器（需要 USE_TECHSOFT_SDK 宏）
FOpenNurbsBRepToTechSoftConverter TechSoftConverter(ImportParams);
TechSoftConverter.AddBRep(Brep, Offset);
```

## Demo 示例

以下演示如何在代码中程序化配置并触发 OpenNurbs 文件导入：

```cpp
// MyOpenNurbsImporter.h
#pragma once

#include "CoreMinimal.h"

class FMyOpenNurbsImporter
{
public:
    /** 导入一个 .3dm 文件并配置细分选项 */
    static bool ImportRhinoFile(const FString& FilePath, bool bUseTessellation);
};
```

```cpp
// MyOpenNurbsImporter.cpp
#include "MyOpenNurbsImporter.h"
#include "DatasmithOpenNurbsTranslatorModule.h"
#include "DatasmithOpenNurbsImportOptions.h"

bool FMyOpenNurbsImporter::ImportRhinoFile(const FString& FilePath, bool bUseTessellation)
{
    // 1. 确认模块可用
    if (!FDatasmithOpenNurbsTranslatorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("DatasmithOpenNurbsTranslator 模块未加载"));
        return false;
    }

    // 2. 配置导入选项
    UDatasmithOpenNurbsImportOptions* ImportOptions = NewObject<UDatasmithOpenNurbsImportOptions>();
    
    if (bUseTessellation)
    {
        // 使用 Unreal 内置 NURBS 细分 — 可控精度
        ImportOptions->Options.Geometry = EDatasmithOpenNurbsBrepTessellatedSource::UseUnrealNurbsTessellation;
    }
    else
    {
        // 使用文件中的原始渲染网格 — 更快，保留原始 UV
        ImportOptions->Options.Geometry = EDatasmithOpenNurbsBrepTessellatedSource::UseRenderMeshes;
    }

    // 3. 获取临时目录（用于缓存中间数据）
    FString TempDir = FDatasmithOpenNurbsTranslatorModule::Get().GetTempDir();
    UE_LOG(LogTemp, Log, TEXT("OpenNurbs 临时目录: %s"), *TempDir);

    // 4. 此处实际导入应通过 Datasmith 导入框架完成
    // 在编辑器中通常通过 FDatasmithImportFactory 或 UI 操作触发
    
    return true;
}
```

## 模块依赖

### DatasmithOpenNurbsTranslator 模块

| 模块 | 用途 |
|---|---|
| `OpenNurbs6` | McNeel 的 OpenNurbs 库，用于解析 Rhino `.3dm` 文件中的 NURBS 几何数据 |
| `CADLibrary` | 提供通用 CAD 导入参数、曲面细分选项等基础设施 |
| `ParametricSurface` | 参数化曲面的 Unreal 内置 NURBS 细分引擎 |
| `CADKernelSurface` | CADKernel 后端，用于高质量 BRep 曲面细分 |

### 整个插件的特殊依赖

| 模块 | 用途 |
|---|---|
| `TechSoft` | TechSoft HOOPS 工具包（商业库），用于 BRep 到网格的转换后端 |
| `OpenNurbs6` | McNeel OpenNurbs 库，用于 Rhino 文件解析 |
| `DatasmithContent` | Datasmith 的核心资产类型和场景元素定义 |
| `DatasmithCore` | Datasmith 翻译器框架、IDatasmithScene 等核心接口 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 添加逻辑使 Wire 翻译器兼容已安装 Alias 2027 的环境 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 更新 TechSoft 依赖至 2026.3 版本 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新 DatasmithCAD 缓存版本号 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 之间保持可移植性 |

### 维护评价

该插件**仍在活跃维护中**。从近期提交记录来看，Epic Games 持续进行：
- **第三方库升级**（TechSoft 2026.3）
- **编译器兼容性修复**（跨平台警告修复）
- **新版本软件支持**（Alias 2027 兼容）
- **缓存机制更新**

插件拥有 21 个模块、114 个源文件，属于**大型企业级插件**，结构复杂但维护节奏稳定。由于依赖商业库（TechSoft HOOPS），实际可用功能取决于许可证。作为 Datasmith 管线的重要组成部分，建议在企业级 CAD 导入工作流中使用。

⚠️ **注意**：该插件默认未启用（`EnabledByDefault: false`），需要在项目的插件设置中手动启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [DatasmithOpenNurbsTranslator 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter/Source/DatasmithOpenNurbsTranslator)