# Datasmith CAD Importer

> Collection of tools to work with CAD files.

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

DatasmithCADImporter 是一个专门为工业级 CAD（计算机辅助设计）文件提供导入支持的插件集合。它并非一个独立的导入器，而是作为 Datasmith 导入流程的后端扩展，专门处理各种 CAD 格式（如 .wire, .plmxml, .3dm 等）的解析、几何转换和材质映射。其核心目标是将来自 Alias、CATIA、NX、SolidWorks 等专业 CAD 软件的高精度、参数化模型，无损或低损地转换为 UE 可用的静态网格体和材质资产，服务于汽车、航空、制造等行业的实时可视化、虚拟评审和数字孪生场景。

## 使用场景

- 你是一名汽车设计师，需要将 Alias 创建的复杂车身曲面模型（.wire 格式）导入 UE 进行实时渲染和评审。
- 你是一名工程师，需要将 CATIA 或 NX 生成的 PLMXML 格式的产品结构树和几何数据导入 UE，用于构建装配体的可视化。
- 你需要导入 Rhino 的 3DM 文件（基于 OpenNurbs），并希望保留其图层和材质信息。
- 你的工作流依赖于 Datasmith，但需要处理特定的 CAD 格式，此插件为 Datasmith 提供了必要的翻译器。

## 蓝图用法

该插件主要作为 Datasmith 导入管线的底层模块运行，其功能通常通过 Datasmith 的标准导入界面（如内容浏览器中的“导入”按钮或 Datasmith 场景导入）间接调用。插件本身不直接暴露大量面向设计师的蓝图节点，其核心价值在于为 Datasmith 的 `UDatasmithStaticMeshImporter` 等类提供 CAD 特定的处理逻辑。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （无直接蓝图节点） | 该插件的功能通过 Datasmith 导入流程集成，不提供独立的蓝图函数库。 | N/A |

### 使用示例（蓝图描述）

在蓝图中，你通常不会直接与此插件交互。正确的使用方式是：
1.  确保 `DatasmithCADImporter` 插件已在项目设置中启用。
2.  在内容浏览器中右键，选择“导入到...”。
3.  选择支持的 CAD 文件（如 .wire, .plmxml, .3dm）。
4.  在导入对话框中，Datasmith 会自动调用此插件中对应的翻译器模块来处理文件。
5.  导入完成后，你将获得转换后的静态网格体、材质和场景层级。

## C++ 用法

对于开发者，此插件提供了模块接口和底层处理类，可用于扩展或集成到自定义工具链中。

### 头文件引入

```cpp
#include "WireInterfaceModule.h" // 用于访问 Wire 文件翻译器模块
// 其他模块头文件根据具体功能引入，如 CADLibrary, ParametricSurface 等
```

### 基本用法

检查并加载 Wire 翻译器模块，获取临时目录路径。
（来源：`Engine/Plugins/Enterprise/DatasmithCADImporter/Source/WireInterface/Public/WireInterfaceModule.h`）

```cpp
// 检查 Datasmith Wire 翻译器模块是否可用
if (UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::IsAvailable())
{
    // 获取模块实例
    UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule& WireModule = 
        UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::Get();
    
    // 获取模块管理的临时目录，可能用于存储中间转换文件
    FString TempDirectory = WireModule.GetTempDir();
    UE_LOG(LogTemp, Log, TEXT("Wire Translator Temp Dir: %s"), *TempDirectory);
}
```

### 进阶用法

进阶用法涉及直接使用 `CADLibrary`、`ParametricSurface` 等模块中的类来处理 CAD 几何数据。这通常需要深入理解 CAD 内核（如 TechSoft, OpenNurbs）和 UE 的网格体描述（`FMeshDescription`）。由于源码复杂且高度专业化，建议参考插件内各翻译器模块（如 `DatasmithWireTranslator`）的实现作为示例。

## Demo 示例

一个最小化的 C++ 示例，展示如何初始化并检查 CAD 导入器插件的核心模块。

**MyCADTool.h**
```cpp
#pragma once
#include "CoreMinimal.h"

class FMyCADTool
{
public:
    static void InitializeCADImporterModules();
};
```

**MyCADTool.cpp**
```cpp
#include "MyCADTool.h"
#include "WireInterfaceModule.h" // 引入 Wire 翻译器模块头文件

void FMyCADTool::InitializeCADImporterModules()
{
    // 确保 Wire 翻译器模块已加载
    if (!UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("Datasmith Wire Translator module is not loaded. CAD .wire import may not be available."));
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("Datasmith CAD Importer modules are ready."));
    
    // 在这里可以进一步初始化其他 CAD 相关模块，如 CADLibrary
    // 例如：FCADLibraryModule::Get().Initialize();
}
```

## 模块依赖

该插件依赖多个外部 CAD 处理库和 UE 内部模块。以下是其**独特**的依赖项：

| 模块 | 用途 |
|---|---|
| `TechSoft` | 用于解析和转换多种主流 CAD 格式（如 CATIA, NX, SolidWorks, STEP, IGES）的核心商业库。 |
| `OpenNurbs6` | 用于解析 Rhino 的 .3dm 文件格式的开源库。 |
| `DatasmithCore` | Datasmith 的核心模块，提供场景、资产和导入器的基础框架。 |
| `MeshDescription` | UE 的网格体描述数据结构，用于构建和操作网格体几何数据。 |
| `StaticMeshDescription` | 用于从 `FMeshDescription` 构建 `UStaticMesh` 的工具模块。 |

## 维护状态

### 近期更新

```
- 90f00dd86ae6 Added support for Alias 2026.0
- 39994edb437c [Wire] Corrected missing incrementation The mesh was properly sectioned but the missing increment was assigning the same material to each section Somehow the increment step was deleted before submission :-(
- 61d36ec7677f [Wire] Fixed missing colors when using group option - Fixed coding error in FDatasmithStaticMeshImporter::SetupStaticMesh which was eliminating sections when some were sharing the same material - Simplified material assignment to MeshElement's slots. - removed redundant material assignment on MeshActor. - Fixed wrong material slot name used in FMeshDescription. It has to be an integer to work in Datasmith import.
```

- `90f00dd86ae6`: 新增了对 Alias 2026.0 版本的支持，表明插件在持续跟进上游 CAD 软件的更新。
- `39994edb437c` 和 `61d36ec7677f`: 修复了 Wire 文件导入过程中的材质分配和颜色显示错误，属于重要的稳定性修复。

### 维护评价

**综合评价：推荐使用，但需注意其企业级定位。**

- **活跃维护**：插件创建于 2019 年，但近期（2024-2025 年）仍有实质性更新，特别是添加对新版 CAD 软件的支持和关键 bug 修复，表明 Epic 仍在积极维护。
- **企业级功能**：作为 Enterprise 类别插件，其主要面向有专业 CAD 导入需求的行业用户，功能稳定但相对专精。
- **启用门槛**：默认未启用 (`EnabledByDefault=false`)，需要用户手动在插件管理器中开启。这可能是因为其依赖的第三方库（如 TechSoft）增加了包体积和复杂性。
- **依赖复杂**：依赖多个外部库，构建和部署环境需要配置这些库。
- **推荐**：如果你的工作流涉及从专业 CAD 软件导入模型到 UE，并且使用 Datasmith，那么此插件是必不可少的。对于游戏开发等通用场景，则无需启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests) (如果存在)