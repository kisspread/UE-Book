# Datasmith CAD Importer

> Collection of tools to work with CAD files.（照抄，不翻译）

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

DatasmithCADImporter 是一个专门用于导入和转换工业级 CAD（计算机辅助设计）文件的插件工具集。其核心目标是将来自专业 CAD 软件（如 Autodesk Alias）的复杂、高精度几何体（特别是 `.wire` 格式）无缝导入 Unreal Engine 中，用于可视化、实时渲染、虚拟审查或产品配置。

它通过庞大的模块系统（如 `WireInterface` 系列）支持不同版本的 CAD 软件，并使用 `CADKernel` 或 `TechSoft` 等几何内核进行严格的曲面细分和拓扑修复，确保导入的网格既忠实于原始 CAD 设计，又能满足游戏引擎实时渲染的性能要求。该插件是 Unreal Engine 在工业设计、汽车设计、产品原型设计等领域应用的关键桥梁。

## 使用场景

- 你正在为汽车制造商开发一个基于 UE 的实时数字孪生或 VR 展厅 → 使用此插件导入车辆 CAD 模型。
- 你是一名产品设计师，需要将 Alias 创建的复杂概念模型导入 UE 进行实时交互式渲染 → 使用此插件。
- 你需要在 UE 中对导入的 CAD 模型进行材质分配、碰撞体生成和 LOD 创建 → 该插件支持完整的材质和几何体处理管线。
- 你需要批量或自动化导入大量 CAD 文件 → 该插件的 `DatasmithDispatcher` 模块提供了进程外处理能力。

## 蓝图用法

由于本插件主要为运行时导入提供底层支持，其核心功能通常通过 Datasmith 导入器框架调用，直接暴露的蓝图 API 相对有限。以下是关键的可调用接口：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetTempDir` | 获取插件使用的临时目录路径 | `FDatasmithWireTranslatorModule` |

### 使用示例（蓝图描述）

1.  **初始化**：该插件通常作为 Datasmith 导入流程的一部分被自动调用。用户可以通过 Datasmith 导入面板选择支持的 CAD 格式（如 `.wire`）进行导入。
2.  **参数设置**：导入时，可以在导入对话框中设置细分（Tessellation）选项，这些选项会传递给插件的内部处理流程。
3.  **结果**：导入完成后，原始的 CAD 数据结构会被转换为 UE 的 `StaticMesh` 和 `Material` 资产，并在内容浏览器中生成。

## C++ 用法

### 头文件引入

要使用 `WireInterface` 模块的核心功能，主要包含其模块头文件。

```cpp
#include "WireInterfaceModule.h"
```

### 基本用法

以下示例展示如何获取模块实例并检查其可用性。

```cpp
// 检查 WireInterface 模块是否加载
if (UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::IsAvailable())
{
    // 获取模块实例
    auto& WireModule = UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::Get();
    UE_LOG(LogTemp, Log, TEXT("Wire Translator Module Temp Dir: %s"), *WireModule.GetTempDir());
}
```
*来源: `Public/WireInterfaceModule.h`*

### 进阶用法

更高级的用法涉及使用 `IWireInterface` 接口来控制导入过程。这通常发生在自定义的 Datasmith 转换器内部。

```cpp
// 创建一个 Wire Translator 实例（假设在自定义转换器中）
TUniquePtr<IWireInterface> WireTranslator = IWireInterface::Create();

// 1. 初始化，传入 CAD 文件路径
if (WireTranslator->Initialize(TEXT("C:/Models/CarBody.wire")))
{
    // 2. 配置导入设置
    FWireSettings Settings;
    // ... 配置 Settings ...
    WireTranslator->SetImportSettings(Settings);
    WireTranslator->SetOutputPath(FPaths::ProjectSavedDir());

    // 3. 创建一个 Datasmith 场景来接收数据
    TSharedPtr<IDatasmithScene> DatasmithScene = FDatasmithSceneFactory::CreateScene(TEXT("ImportedCar"));

    // 4. 执行加载，将 CAD 数据转换为 Datasmith 元素
    if (WireTranslator->Load(DatasmithScene))
    {
        // 5. 此后，DatasmithScene 包含了从 CAD 文件解析出的 Actor、Mesh、Material 元素
        //    可以继续使用 Datasmith 导入器的标准流程将其转换为 UE 资产
    }
}
```
*来源: `Private/WireInterfaceImpl.h` 接口定义*

## Demo 示例

一个展示如何通过模块接口查询信息的最小 C++ 示例。

**MyCADTools.h**
```cpp
#pragma once
#include "CoreMinimal.h"

class FMyCADHelper
{
public:
    static void LogWireModuleInfo();
};
```

**MyCADTools.cpp**
```cpp
#include "MyCADTools.h"
#include "WireInterfaceModule.h"

void FMyCADHelper::LogWireModuleInfo()
{
    // 确保模块可用
    if (UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::IsAvailable())
    {
        auto& Module = UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::Get();
        FString TempDir = Module.GetTempDir();
        UE_LOG(LogTemp, Display, TEXT("Datasmith CAD Importer (Wire Interface) module is active."));
        UE_LOG(LogTemp, Display, TEXT("Temp directory: %s"), *TempDir);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Datasmith CAD Importer (Wire Interface) module is not loaded."));
    }
}
```

## 模块依赖

要使用本插件的某个模块（例如 `WireInterface2020`），你的模块需要在 `.Build.cs` 文件中添加以下**非标准**依赖。通常你需要依赖整个插件或 `DatasmithCADImporter` 模块。

| 模块 | 用途 |
|---|---|
| `TechSoft` | 使用 TechSoft 几何内核进行 CAD 文件解析和曲面细分（特定 WireInterface 模块依赖） |
| `CADLibrary` | 提供通用的 CAD 模型处理、几何内核抽象层和导入参数定义 |
| `CADKernelSurface` | 提供基于 Epic CADKernel 的曲面细分和处理能力 |
| `DatasmithRuntime` | 提供核心的 Datasmith 运行时场景、元素和资产工厂 |
| `OpenNurbs6` | 使用 OpenNurbs 库解析 .3dm 等格式（特定翻译器依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，代码将 double 常量截断为 float 时产生的警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 添加了逻辑，使 Wire 翻译器在安装了 Alias 2027 时也能工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将 TechSoft 库更新至 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 DatasmithCAD 缓存的版本。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器之间兼容。 |

### 维护评价

- **创建时间**：2019 年 10 月，属于较早的 Enterprise 插件。
- **近期活跃度**：**高度活跃**。在最近一周内（2026-05-12 至 2026-05-13）有多次提交，内容包括：
    1.  **功能兼容性更新**：为即将到来的 Alias 2027 提供支持。
    2.  **依赖库升级**：更新了核心依赖 TechSoft 的版本。
    3.  **代码质量与可移植性**：修复编译警告，提高跨编译器兼容性。
- **维护状态**：该插件由 Epic Games 作为企业级功能进行积极维护，持续适配最新的 CAD 软件版本并修复问题。尽管其 `EnabledByDefault` 为 false，但它仍然是 Epic 支持的核心企业功能之一。
- **推荐使用**：✅ **推荐使用**。对于需要处理高端 CAD 数据（特别是 Alias .wire 文件）的 UE 企业用户或大型项目，这是官方支持且维护良好的解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)