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

Datasmith CAD Importer 是 Unreal Engine 中用于处理计算机辅助设计（CAD）文件的核心框架。它并非一个单一工具，而是一个完整的 CAD 数据导入和处理套件。其主要作用是将来自不同 CAD 软件（如 Alias、OpenNurbs、Parasolid 等）的工业级、高精度模型，转换为 Unreal Engine 可以理解和渲染的几何体（Mesh）和材质（Material）。该插件通过多个专用的翻译器模块（`DatasmithWireTranslator`, `DatasmithOpenNurbsTranslator` 等）和底层处理库（`CADLibrary`, `CADKernelSurface`），解决了从工程设计到实时渲染之间的数据鸿沟，使得汽车设计、建筑信息模型（BIM）、工业制造等领域的 CAD 模型能够被高效地用于可视化、仿真或产品展示。

## 使用场景

- 你正在为汽车行业创建一个车辆设计评审或配置器应用 → 使用此插件导入来自 Alias 等工业设计软件的 `.wire` 文件。
- 你需要将建筑或工程的 CAD/BIM 模型（如来自 Revit, CATIA）用于实时交互演示或 VR 体验 → 使用此插件集成 Datasmith 工作流。
- 你正在开发一个制造仿真或数字孪生项目，需要导入精确的机械零件 CAD 数据 → 使用此插件处理 Parasolid (`.x_t`)、STEP (`.stp`) 等格式。

## 蓝图用法

由于 Datasmith CAD Importer 的核心功能是通过 Datasmith 导入流程（通常在编辑器菜单中操作）或 C++ API 驱动，其直接的蓝图节点较少。主要的蓝图交互点通常是触发导入或配置导入参数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Datasmith Import Scene` | 通用的 Datasmith 场景导入节点，可处理 `.udatasmith` 和关联的 CAD 源文件。 | Datasmith 动态导入蓝图库 |
| `Set Datasmith Import Settings` | 配置导入选项，如细分精度、材质导出设置等。 | Datasmith 动态导入蓝图库 |

### 使用示例（蓝图描述）

在蓝图中，你通常不会直接调用 Wire Translator 模块。取而代之的是，你会使用 `Datasmith Import Scene` 节点，并指向一个 `.udatasmith` 源文件（该文件已通过 Datasmith 导出器从 CAD 源创建）。导入设置（如 `FDatasmithTessellationOptions`）可以在导入前通过相应节点进行配置。整个过程由插件内部的翻译器和调度器（`DatasmithDispatcher`）自动完成。

## C++ 用法

在 C++ 中，主要使用 `FDatasmithWireTranslatorModule` 来访问模块服务，或通过 Datasmith 的高级 API 来触发导入过程。对于深度集成，需要直接与特定翻译器交互。

### 头文件引入

```cpp
#include "WireInterfaceModule.h"
// 包含用于具体翻译器实现的头文件，例如：
// #include "WireInterfaceImpl.h" // 私有头，示例仅供理解结构
```

### 基本用法

（示例基于 `Public/WireInterfaceModule.h` 和通用 Datasmith API 用法）

```cpp
// 1. 检查模块是否可用
if (FDatasmithWireTranslatorModule::IsAvailable())
{
    // 2. 获取模块实例
    FDatasmithWireTranslatorModule& WireModule = FDatasmithWireTranslatorModule::Get();
    
    // 3. 通常，翻译器由 Datasmith 的导入流程（如 UDatasmithSceneImportFactory）内部管理。
    // 如果你需要单独使用某个翻译器（例如，自定义导入逻辑），你需要实例化其实现类。
    // 请注意，这通常是非标准用法，需要深入理解内部流程。
    UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FWireTranslatorImpl WireTranslator;
    
    // 4. 初始化翻译器
    if (WireTranslator.Initialize(TEXT("C:/Path/To/Your/Model.wire")))
    {
        // 5. 创建一个空的 Datasmith 场景用于存放导入结果
        TSharedPtr<IDatasmithScene> DatasmithScene = FDatasmithSceneFactory::CreateScene(TEXT("MyCADScene"));
        
        // 6. 加载模型到场景
        if (WireTranslator.Load(DatasmithScene))
        {
            // 成功，此时 `DatasmithScene` 中已包含转换后的 Actor 和 Mesh
            UE_LOG(LogTemp, Log, TEXT("CAD model loaded successfully into Datasmith scene."));
        }
    }
}
```

### 进阶用法

处理来自 `Alias` 软件的模型并配置转换选项。

```cpp
// 假设我们要处理一个 Alias (.wire) 文件并指定 CADKernel 作为转换后端
UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FWireTranslatorImpl Translator;
FString ModelPath = TEXT("C:/Design/CarBody.wire");

if (Translator.Initialize(*ModelPath))
{
    // 配置导入参数，例如选择使用 CADKernel 还是 TechSoft
    // 这通常通过 Translator 内部的 FImportParameters 或在初始化时设置
    Translator.SetImportSettings(FWireSettings::Default()); // 使用默认设置
    
    // 创建目标场景
    TSharedPtr<IDatasmithScene> Scene = FDatasmithSceneFactory::CreateScene(TEXT("AliasModel"));
    
    if (Translator.Load(Scene))
    {
        // 现在可以将场景中的内容应用到你的 UE 世界或资产中
        // 例如，将导入的 Actor 附加到当前关卡
        for (int32 i = 0; i < Scene->GetActorsCount(); ++i)
        {
            const TSharedPtr<IDatasmithActorElement>& ActorElement = Scene->GetActor(i);
            // ... 处理每个 Actor 元素
        }
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load Alias model: %s"), *ModelPath);
    }
}
```

## Demo 示例

一个可编译的最小示例，演示如何检查 Wire Translator 模块并获取其临时目录路径（一个典型的模块服务使用场景）。

**MyCADProcessor.h**
```cpp
#pragma once
#include "CoreMinimal.h"

class FMyCADProcessor
{
public:
    void ProcessCADFile();
};
```

**MyCADProcessor.cpp**
```cpp
#include "MyCADProcessor.h"
#include "WireInterfaceModule.h" // 引入 Wire Translator 模块头

void FMyCADProcessor::ProcessCADFile()
{
    // 步骤1：检查目标模块是否已加载
    if (!UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("Datasmith Wire Translator module is not available. Ensure the plugin is enabled."));
        return;
    }

    // 步骤2：获取模块实例（模块已加载，此处断言成功）
    auto& WireModule = UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::Get();
    UE_LOG(LogTemp, Log, TEXT("Wire Translator module loaded."));

    // 步骤3：使用模块提供的服务，例如获取其用于临时文件的目录
    FString TempDir = WireModule.GetTempDir();
    UE_LOG(LogTemp, Log, TEXT("Wire Translator temporary directory: %s"), *TempDir);

    // 后续可在此处初始化具体的翻译器并加载模型
    // ... （参见上文的 C++ 用法示例）
}
```

## 模块依赖

要使用此插件的功能，你的项目模块通常需要依赖 `DatasmithExporter` 和 `DatasmithContent` 等核心模块。由于该插件本身提供了多个运行时模块，其独特的外部依赖如下：

| 模块 | 用途 |
|---|---|
| `TechSoft` | 提供处理主流 CAD 格式（如 STEP, IGES, Parasolid）的底层引擎。`DatasmithCADTranslator` 和 `WireInterface` 模块依赖它。 |
| `OpenNurbs6` | 用于读取 Rhinoceros 3D (.3dm) 文件格式的库。`DatasmithOpenNurbsTranslator` 模块依赖它。 |
| `CADKernel` | Epic 开发的用于 CAD 几何体修复、细分和转换的核心库。`CADKernelSurface` 和相关的转换器模块依赖它。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量截断为浮点数产生警告的代码。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed. | 新增逻辑，使得即使安装了 Alias 2027，Wire 翻译器也能正常工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3. | 将 TechSoft 库更新至 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache. | 更新了 Datasmith CAD 缓存的版本。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器之间可移植。 |

### 维护评价

**活跃维护**。Datasmith CAD Importer 是 Unreal Engine 企业版的关键组件，持续获得更新。从最近的提交记录看，维护团队正在积极：
1.  **更新核心依赖**（如 TechSoft 库），以支持最新的 CAD 格式版本。
2.  **修复兼容性问题**，确保与新版本的 CAD 设计软件（如 Alias 2027）协同工作。
3.  **进行代码质量改进和编译器兼容性修复**。
该插件创建于 2019 年，是成熟的工业级解决方案，推荐在需要处理专业 CAD 数据的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Features/Datasmith/CAD) (路径待确认)