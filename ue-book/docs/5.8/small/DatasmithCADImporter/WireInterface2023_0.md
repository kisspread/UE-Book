# Datasmith CAD Importer

> Collection of tools to work with CAD files.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | CAD文件导入 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途
此插件并非一个简单的文件导入器，而是一个**针对专业CAD软件（如Autodesk Alias）的特定格式（.wire）的专用转换框架**。它解决的核心问题是将复杂的、包含精确NURBS曲面和拓扑结构的CAD模型数据，高效、准确地转换为UE可识别的Datasmith场景和静态网格（Static Mesh）。

该插件存在是为了满足工业设计（如汽车A级曲面）、产品设计和建筑可视化等领域对**高保真度CAD数据实时渲染**的需求。它通过一系列专门的转换器（Translator）和工具库，处理CAD模型中的层次结构、材质、几何体，并最终输出为适合UE渲染的网格体。由于其功能专业且涉及第三方库，**默认处于禁用状态**。

## 使用场景
- 你需要将 **Autodesk Alias** 的 `.wire` 格式模型导入UE进行可视化评审或实时渲染。
- 你在进行汽车或高端产品的A级曲面设计，需要将设计数据无损地导入UE制作VR体验或营销素材。
- 你的团队使用 **PLMXML**、**OpenNurbs (3dm)** 或其他CAD交换格式进行数据传递，并希望在UE中进行轻量化查看和交互。

## 蓝图用法
此插件的核心功能主要通过C++和Datasmith框架的导入流程集成，并不直接暴露大量简单的蓝图节点。其使用通常隐藏在标准的Datasmith文件导入操作（拖拽或通过内容浏览器导入）之后，由引擎内部调用。
因此，没有显著的、面向蓝图设计师的独立函数节点。

## C++ 用法
此插件作为Datasmith后端的扩展，其使用更多是框架性的，而非直接的应用程序接口调用。主要用法是**确保正确的模块依赖并启用插件**，然后通过Datasmith的通用导入流程触发。

### 头文件引入
根据你要使用的具体模块引入头文件，例如使用Wire接口时：
```cpp
#include "WireInterfaceModule.h"
```

### 基本用法
该插件的核心是提供 `IWireInterface` 这样的转换器接口。实际调用发生在Datasmith导入管线的内部。开发者通常不直接实例化这些转换器，而是确保它们所在的模块被正确加载和链接。

一个概念性的代码示例（展示内部流程）：
```cpp
// 假设在Datasmith导入管线的某个环节
// 获取 Wire Translator 模块（对应当前 UE 版本，如2023.0）
if (FDatasmithWireTranslatorModule::IsAvailable())
{
    // 该模块会注册对应的 Translator 工厂
    // 当处理 .wire 文件时，Datasmith 框架会创建对应的 IWireInterface 实现（如 FWireTranslatorImpl）并调用其 Load 方法
}
```

### 进阶用法
要为新的CAD格式编写支持，需要：
1.  实现一个继承自 `IWireInterface` 或相关基类（如 `FCADModelToCADKernelConverterBase`）的新转换器类。
2.  创建一个对应的Runtime模块（如 `WireInterfaceXXXX`），并在其 `Build.cs` 中声明对 `CADLibrary`, `DatasmithCore` 等模块的依赖。
3.  在模块的 `StartupModule` 中，向 `DatasmithCADTranslator` 模块注册你的新转换器工厂。

## Demo 示例
以下示例展示如何编写一个假想的新CAD格式转换器模块的骨架：
```cpp
// MyCADTranslatorModule.h
#pragma once

#include "Modules/ModuleManager.h"

class FMyCADTranslatorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```
```cpp
// MyCADTranslatorModule.cpp
#include "MyCADTranslatorModule.h"
#include "DatasmithTranslatorManager.h" // 假设用于注册

void FMyCADTranslatorModule::StartupModule()
{
    // 注册一个工厂，用于创建针对“.mycad”文件的翻译器
    // FDatasmithTranslatorManager::Get().RegisterTranslatorFactory(...);
}

void FMyCADTranslatorModule::ShutdownModule()
{
    // 注销工厂
}

IMPLEMENT_MODULE(FMyCADTranslatorModule, MyCADTranslator)
```

## 模块依赖
此插件的模块众多，依赖关系复杂。要成功使用此插件，你的模块（如果直接引用其功能）可能需要依赖以下**非标准**模块：

| 模块 | 用途 |
|---|---|
| `TechSoft` | 核心的CAD内核库，用于处理多种CAD格式（如STEP, IGES）的几何体。 |
| `OpenNurbs6` | 用于处理Rhino的 `.3dm` 格式的开源库。 |
| `CADLibrary` | 本插件提供的共享CAD工具库，包含通用数据结构（如 `FMeshParameters`）和接口（如 `ICADModelConverter`）。 |
| `CADKernel` | Epic自研的轻量化CAD内核，用于几何体处理和网格生成。 |
| `DatasmithCore` | Datasmith框架的核心库。 |

**注意**：由于此插件默认禁用，你需要在 `.uproject` 文件的 `Plugins` 数组中显式启用它，并可能需要在项目或模块的 `Build.cs` 中添加对上述特定模块的依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的编译警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 添加逻辑以支持在已安装Alias 2027的环境下工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 更新TechSoft库至2026.3版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了DatasmithCAD缓存的版本标识。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在MSVC和Clang编译器间可移植。 |

### 维护评价
此插件仍在**积极维护**中。从近期的提交记录看（2026年5月），维护重点包括：
1.  **兼容性更新**：确保插件能与最新版本的CAD软件（如Alias 2027）协同工作。
2.  **第三方库升级**：定期更新所依赖的核心库（如TechSoft）。
3.  **代码质量与可移植性**：修复编译警告，提升代码在不同编译器下的健壮性。

虽然插件本身有数年历史，但作为Enterprise/工业级功能，其维护是持续和有计划的。对于需要处理高精度CAD数据的用户，**推荐使用**，但需注意其默认禁用的状态和较复杂的模块依赖。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例] (未在提供的路径中发现，可能位于引擎测试目录或其他位置)