# Datasmith CAD Importer

> Collection of tools to work with CAD files.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

DatasmithCADImporter 是 Datasmith 导入管线的核心 CAD 文件处理插件，专门解决工业级 CAD 格式（如 Rhino .3dm、PLMXML、各种 Wire 格式）到 Unreal Engine 的转换问题。

该插件的存在意义在于：标准的 FBX/OBJ 等通用格式无法保留 CAD 文件中的精确几何信息（NURBS 曲面、参数化曲面、BRep 拓扑结构）。此插件通过集成 TechSoft（HOOPS）和 OpenNurbs 等专业 CAD 内核库，实现了对工业 CAD 格式的原生读取和高质量网格化（Tessellation），是建筑可视化、工业数字孪生、汽车设计等领域导入 CAD 数据的基础设施。

**注意**：此插件默认禁用（`EnabledByDefault: false`），需要在项目设置中手动启用。

## 模块架构

该插件包含 21 个 Runtime 模块，按功能可分为以下几层：

| 层级 | 模块 | 职责 |
|---|---|---|
| **CAD 内核层** | `CADInterfaces`, `CADLibrary`, `CADTools` | 封装底层 CAD 库接口（TechSoft/HOOPS） |
| **几何处理层** | `CADKernelSurface`, `ParametricSurface`, `ParametricSurfaceExtension` | NURBS/参数化曲面的网格化算法 |
| **格式翻译层** | `DatasmithCADTranslator`, `DatasmithOpenNurbsTranslator`, `DatasmithPLMXMLTranslator`, `DatasmithWireTranslator` | 各种 CAD 格式的 Datasmith 翻译器 |
| **版本适配层** | `WireInterface2020` ~ `WireInterface2026_0` | 不同版本 Wire 格式的适配器 |
| **调度层** | `DatasmithDispatcher` | 多进程/多线程导入调度 |

## 使用场景

- 你在做建筑可视化项目，需要导入 Rhino 的 .3dm 模型 → 用 DatasmithOpenNurbsTranslator
- 你在做汽车/工业数字孪生，需要导入 PLMXML 数据 → 用 DatasmithPLMXMLTranslator
- 你需要批量导入多种 CAD 格式并保持材质/层级关系 → 用 DatasmithCADTranslator 统一调度
- 你使用的是特定版本的 Wire 格式（如 NX、CATIA）→ 选择对应版本的 WireInterface 模块

## 蓝图用法

### 导入选项配置

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Options` (属性) | 配置 NURBS 导入的几何和网格化选项 | `UDatasmithOpenNurbsImportOptions` |
| `Geometry` (属性) | 选择 BRep 几何源：Unreal NURBS 网格化或 Rhino 原始网格 | `FDatasmithOpenNurbsOptions` |

### 使用示例（蓝图描述）

1. 在项目设置中启用 DatasmithCADImporter 插件
2. 通过 Datasmith 导入流程选择 .3dm 文件
3. 在导入选项面板中，配置 `Geometry` 属性：
   - 选择 **"Import as NURBS, Tessellate in Unreal"**：使用 Unreal 内置的 NURBS 网格化算法，精度更高但导入较慢
   - 选择 **"Import Rhino Meshes and UVs"**：直接使用 Rhino 文件中预存的渲染网格和 UV，导入更快
4. 配置继承自 `FDatasmithTessellationOptions` 的网格化参数（弦偏差、法线偏差等）

## C++ 用法

### 头文件引入

```cpp
#include "DatasmithOpenNurbsTranslatorModule.h"
#include "DatasmithOpenNurbsImportOptions.h"
```

### 基本用法

```cpp
// 检查模块是否可用
if (FDatasmithOpenNurbsTranslatorModule::IsAvailable())
{
    // 获取模块实例
    FDatasmithOpenNurbsTranslatorModule& Module = FDatasmithOpenNurbsTranslatorModule::Get();
    
    // 获取临时目录路径（用于中间文件处理）
    FString TempDir = Module.GetTempDir();
}
```

### 进阶用法

```cpp
// 配置 OpenNurbs 导入选项
UDatasmithOpenNurbsImportOptions* ImportOptions = NewObject<UDatasmithOpenNurbsImportOptions>();

// 使用 Unreal 内置 NURBS 网格化（更精确）
ImportOptions->Options.Geometry = EDatasmithOpenNurbsBrepTessellatedSource::UseUnrealNurbsTessellation;

// 或使用 Rhino 原始渲染网格（更快，保留原始 UV）
ImportOptions->Options.Geometry = EDatasmithOpenNurbsBrepTessellatedSource::UseRenderMeshes;

// 配置网格化精度参数（继承自 FDatasmithTessellationOptions）
// ImportOptions->Options 中包含弦偏差、法线偏差等参数
```

## Demo 示例

```cpp
// OpenNurbsImportHelper.h
#pragma once

#include "CoreMinimal.h"

class FOpenNurbsImportHelper
{
public:
    /** 检查 .3dm 文件导入支持 */
    static bool IsOpenNurbsImportAvailable();
    
    /** 获取导入临时目录 */
    static FString GetImportTempDirectory();
};
```

```cpp
// OpenNurbsImportHelper.cpp
#include "OpenNurbsImportHelper.h"
#include "DatasmithOpenNurbsTranslatorModule.h"

bool FOpenNurbsImportHelper::IsOpenNurbsImportAvailable()
{
    return FDatasmithOpenNurbsTranslatorModule::IsAvailable();
}

FString FOpenNurbsImportHelper::GetImportTempDirectory()
{
    if (FDatasmithOpenNurbsTranslatorModule::IsAvailable())
    {
        return FDatasmithOpenNurbsTranslatorModule::Get().GetTempDir();
    }
    return FString();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OpenNurbs6` | Rhino 的开源 NURBS 几何内核库，用于解析 .3dm 文件格式 |
| `DatasmithCore` | Datasmith 核心框架，提供翻译器注册和导入管线接口 |
| `CADInterfaces` | CAD 库抽象接口层，封装 TechSoft/HOOPS 访问 |
| `TechSoft` | HOOPS Exchange SDK，工业级 CAD 格式读取库 |

## 维护状态

### 近期更新

```
- c4c3894de032 Fix or silence false positive PVS warnings in 7.36
- c06ec68a8553 Fixed wrong initial value for GeometricTolerance
- c4e44debb7f7 Moved CADKernel library code from /Engine/Source/Runtime/Datasmith/CADKernel to /Engine/Source/Runtime/Datasmith/CADKernel/Base This is in preparation of the creation of a CADKernelEngine module
```

近期更新主要集中在代码质量改进（PVS 静态分析警告修复）和架构重构（CADKernel 模块拆分准备），表明该插件仍在积极维护中。

### 维护评价

- **创建时间**：2019 年，约 6 年历史
- **维护状态**：活跃维护中，近期有代码质量改进和架构优化
- **模块规模**：21 个模块，215 个源文件，属于大型企业级插件
- **版本适配**：WireInterface 模块覆盖 2020-2026 版本，持续跟进 CAD 格式更新
- **推荐程度**：✅ 推荐使用。作为 Epic 官方维护的企业级 CAD 导入方案，是 Unreal Engine 处理工业 CAD 数据的标准路径。适合建筑可视化、工业数字孪生等需要导入专业 CAD 格式的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests)

---

# Datasmith OpenNurbs Translator

> Datasmith Translator for .3dm files.

| 属性 | 值 |
|---|---|
| 分类 | Importers |
| 默认启用 | ❌ 否（父插件 DatasmithCADImporter 默认禁用） |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithOpenNurbsTranslator` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter/Source/DatasmithOpenNurbsTranslator) | |

## 用途

DatasmithOpenNurbsTranslator 是 DatasmithCADImporter 插件中专门处理 Rhino 3D 的 .3dm 文件格式的翻译器模块。

该模块通过集成 OpenNurbs 开源库（Rhino 官方提供的几何内核），实现了对 .3dm 文件的原生解析。它能够读取 Rhino 文件中的 NURBS 曲面（BRep）、网格、材质、图层等信息，并将其转换为 Datasmith 可识别的中间格式，最终导入到 Unreal Engine 中。

核心价值在于：.3dm 是建筑设计、工业设计领域广泛使用的格式，此模块让用户无需通过中间格式（如 FBX）即可直接导入 Rhino 模型，保留原始的几何精度和设计意图。

## 使用场景

- 你在做建筑可视化，设计师用 Rhino 建模 → 直接导入 .3dm 文件
- 你需要保留 Rhino 模型的原始网格和 UV 映射 → 选择 "Import Rhino Meshes and UVs" 模式
- 你需要更高的几何精度，愿意等待更长的导入时间 → 选择 "Import as NURBS, Tessellate in Unreal" 模式
- 你在开发自定义的 CAD 导入管线 → 通过 C++ API 访问模块功能

## 蓝图用法

### 导入选项枚举

| 枚举值 | 显示名称 | 说明 |
|---|---|---|
| `UseUnrealNurbsTessellation` | Import as NURBS, Tessellate in Unreal | 使用 Unreal 内置的 NURBS 网格化算法，精度更高 |
| `UseRenderMeshes` | Import Rhino Meshes and UVs | 直接使用 Rhino 文件中预存的渲染网格和 UV |

### 导入选项结构体

| 属性 | 类型 | 说明 | 所在类 |
|---|---|---|---|
| `Geometry` | `EDatasmithOpenNurbsBrepTessellatedSource` | BRep 几何源选择 | `FDatasmithOpenNurbsOptions` |
| `Options` | `FDatasmithOpenNurbsOptions` | 完整的导入选项配置 | `UDatasmithOpenNurbsImportOptions` |

### 使用示例（蓝图描述）

1. 在项目设置 → Plugins 中启用 DatasmithCADImporter
2. 通过 Content Browser → Import 或 Datasmith 工具栏导入 .3dm 文件
3. 在弹出的导入选项对话框中：
   - 展开 "Geometry & Tessellation Options" 分类
   - 设置 `Geometry` 下拉框：
     - **Import as NURBS, Tessellate in Unreal**：适合需要高精度几何的场景
     - **Import Rhino Meshes and UVs**：适合需要快速导入并保留原始 UV 的场景
   - 调整网格化参数（弦偏差、最大边长等）

## C++ 用法

### 头文件引入

```cpp
#include "DatasmithOpenNurbsTranslatorModule.h"
#include "DatasmithOpenNurbsImportOptions.h"
```

### 基本用法

```cpp
// 检查 OpenNurbs 翻译器模块是否已加载
if (FDatasmithOpenNurbsTranslatorModule::IsAvailable())
{
    FDatasmithOpenNurbsTranslatorModule& TranslatorModule = FDatasmithOpenNurbsTranslatorModule::Get();
    
    // 获取导入过程使用的临时目录
    FString TempDirectory = TranslatorModule.GetTempDir();
    UE_LOG(LogTemp, Log, TEXT("OpenNurbs temp dir: %s"), *TempDirectory);
}
```

### 进阶用法

```cpp
#include "DatasmithOpenNurbsImportOptions.h"

// 创建并配置 OpenNurbs 导入选项
UDatasmithOpenNurbsImportOptions* Options = NewObject<UDatasmithOpenNurbsImportOptions>();

// 方案 A：使用 Unreal 内置 NURBS 网格化（高精度，较慢）
Options->Options.Geometry = EDatasmithOpenNurbsBrepTessellatedSource::UseUnrealNurbsTessellation;

// 方案 B：使用 Rhino 原始渲染网格（快速，保留 UV）
Options->Options.Geometry = EDatasmithOpenNurbsBrepTessellatedSource::UseRenderMeshes;

// 获取选项的哈希值（用于缓存判断）
uint32 OptionsHash = Options->Options.GetHash();
```

## Demo 示例

```cpp
// RhinoImportManager.h
#pragma once

#include "CoreMinimal.h"
#include "DatasmithOpenNurbsImportOptions.h"

/**
 * Rhino .3dm 文件导入管理器示例
 */
class FRhinoImportManager
{
public:
    /** 检查是否支持 .3dm 导入 */
    static bool CanImportRhinoFile()
    {
        return FDatasmithOpenNurbsTranslatorModule::IsAvailable();
    }
    
    /** 创建高精度导入选项 */
    static UDatasmithOpenNurbsImportOptions* CreateHighPrecisionOptions()
    {
        UDatasmithOpenNurbsImportOptions* Options = NewObject<UDatasmithOpenNurbsImportOptions>();
        Options->Options.Geometry = EDatasmithOpenNurbsBrepTessellatedSource::UseUnrealNurbsTessellation;
        return Options;
    }
    
    /** 创建快速导入选项（保留原始网格） */
    static UDatasmithOpenNurbsImportOptions* CreateFastImportOptions()
    {
        UDatasmithOpenNurbsImportOptions* Options = NewObject<UDatasmithOpenNurbsImportOptions>();
        Options->Options.Geometry = EDatasmithOpenNurbsBrepTessellatedSource::UseRenderMeshes;
        return Options;
    }
    
    /** 获取临时工作目录 */
    static FString GetWorkingDirectory()
    {
        if (FDatasmithOpenNurbsTranslatorModule::IsAvailable())
        {
            return FDatasmithOpenNurbsTranslatorModule::Get().GetTempDir();
        }
        return FPaths::ProjectSavedDir() / TEXT("RhinoImport");
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OpenNurbs6` | Rhino 官方开源 NURBS 几何内核，用于解析 .3dm 文件格式中的 NURBS 曲面、曲线、网格等几何数据 |
| `DatasmithCore` | Datasmith 核心框架，提供 `IDatasmithTranslator` 接口和导入管线 |
| `CADInterfaces` | CAD 库抽象层，提供通用的 CAD 数据结构和接口 |

## 维护状态

### 近期更新

```
- c4c3894de032 Fix or silence false positive PVS warnings in 7.36
- c06ec68a8553 Fixed wrong initial value for GeometricTolerance
- c4e44debb7f7 Moved CADKernel library code from /Engine/Source/Runtime/Datasmith/CADKernel to /Engine/Source/Runtime/Datasmith/CADKernel/Base This is in preparation of the creation of a CADKernelEngine module
```

- `c4c3894`：修复 PVS-Studio 静态分析的误报警告，代码质量维护
- `c06ec68`：修复 GeometricTolerance 的初始值错误，属于 bug 修复
- `c4e44de`：CADKernel 库代码重构，为新模块拆分做准备

### 维护评价

- **维护状态**：✅ 活跃维护中
- **近期活动**：有 bug 修复和架构优化，表明仍在积极开发
- **稳定性**：作为企业级功能，经过多个 UE 版本验证
- **推荐程度**：✅ 推荐。如果你的项目需要导入 Rhino .3dm 文件，这是官方推荐的标准方案。注意需要手动启用插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter/Source/DatasmithOpenNurbsTranslator)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [DatasmithCADImporter 插件根目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter)