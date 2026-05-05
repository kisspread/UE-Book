# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | 21 个 Runtime 模块 |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

DatasmithCADImporter 是 Datasmith 生态系统中的一个专用插件，其核心功能是将各种 CAD（计算机辅助设计）软件生成的文件（如 CATIA, NX, SolidWorks, STEP, IGES 等）导入到 Unreal Engine 中。它不仅仅是一个简单的格式转换器，更是一个处理复杂 CAD 数据的工具集。它解决了 CAD 模型中常见的参数化曲面、精确几何体、装配结构、元数据（如产品制造信息 PMI）在转换为游戏引擎可用的多边形网格和资产时所面临的精度、性能和工作流问题。

## 使用场景

- **建筑可视化 (AEC)**：导入 Revit, ArchiCAD 等 BIM 软件生成的复杂建筑模型，用于创建高质量的建筑漫游和可视化。
- **工业设计与制造**：将 SolidWorks, CATIA, NX 等机械 CAD 软件设计的精密零部件和装配体导入 UE，用于产品展示、虚拟装配、数字孪生或培训模拟。
- **汽车设计**：导入汽车行业的 CAD 数据（如 Alias, ICEM Surf），用于车辆设计评审、虚拟展厅和营销材料制作。
- **任何需要将工程级 CAD 数据用于实时 3D 应用的场景**：当源数据是参数化 CAD 模型而非多边形模型时，此插件是首选方案。

## 蓝图用法

此插件主要作为 Datasmith 导入管线的一部分运行，其核心功能通常不直接暴露为蓝图节点。用户主要通过以下方式使用：
1.  **Datasmith 导入器**：在编辑器中使用“Datasmith”导入功能，选择支持的 CAD 文件格式。插件会自动处理转换。
2.  **Datasmith 场景**：通过 `UDatasmithScene` 和相关的导入设置类（如 `UDatasmithCADImportOptions`）在 C++ 或蓝图中控制导入参数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ImportDatasmithScene` | 通过 Datasmith 框架导入场景文件（包括 CAD 文件） | `UDatasmithScene` |
| `SetCADOptions` | 设置 CAD 导入的特定选项（如曲面细分、单位转换） | `UDatasmithCADImportOptions` |

### 使用示例（蓝图描述）

在蓝图中，你通常不会直接调用此插件的函数。更常见的工作流是：
1.  在编辑器内容浏览器中右键，选择“导入到关卡/导入到项目”。
2.  在文件选择器中选择一个 CAD 文件（如 `.step`, `.catpart`）。
3.  在弹出的 Datasmith 导入选项窗口中，配置 CAD 相关的设置（如曲面公差、合并网格等）。
4.  点击导入，DatasmithCADImporter 插件将在后台处理转换。

## C++ 用法

对于高级用户或需要自动化导入流程的场景，可以通过 C++ 调用 Datasmith API 来使用此插件。

### 头文件引入

```cpp
#include "DatasmithSceneFactory.h"
#include "DatasmithImportOptions.h"
// 根据具体使用的模块，可能需要引入其他头文件，如 CADLibrary
```

### 基本用法

通过 Datasmith 工厂创建场景并设置导入选项。
```cpp
// 创建一个 Datasmith 场景对象
TSharedRef<IDatasmithScene> DatasmithScene = FDatasmithSceneFactory::CreateScene(TEXT("MyCADImport"));

// 获取或创建 CAD 导入选项
TSharedRef<IDatasmithImportOptions> ImportOptions = DatasmithScene->GetImportOptions();
// 这里可以向下转型为具体的 CAD 选项类并进行设置，例如调整曲面细分参数

// 执行导入（通常由编辑器模块或自定义导入器驱动）
// FDatasmithImporter::Get()->ImportScene(DatasmithScene, ImportOptions, ...);
```

### 进阶用法

直接使用 CAD 库模块处理几何数据，或为自定义 CAD 格式编写翻译器。
```cpp
#include "CADLibrary.h"
// 使用 CADLibrary 提供的接口来解析 CAD 文件中的几何和拓扑信息
// 这通常用于开发新的 CAD 格式支持或深度定制转换过程
```

## 模块列表

此插件由多个模块组成，各司其职，共同完成 CAD 数据的处理。

### 核心 CAD 处理与工具
- **[CADInterfaces](CADInterfaces.md)**: 定义与外部 CAD 库（如 TechSoft）交互的抽象接口。
- **[CADLibrary](CADLibrary.md)**: 提供核心的 CAD 数据处理、几何内核和工具函数库。
- **[CADTools](CADTools.md)**: 包含用于处理 CAD 数据的实用工具和辅助函数。
- **[CADKernelSurface](CADKernelSurface.md)**: 处理基于内核的参数化曲面（如 NURBS）的模块。

### Datasmith 翻译器
- **[DatasmithCADTranslator](DatasmithCADTranslator.md)**: 核心翻译器，将 CAD 数据转换为 Datasmith 可理解的中间表示。
- **[DatasmithDispatcher](DatasmithDispatcher.md)**: 负责分发和管理导入任务，可能用于多线程或批处理。
- **[DatasmithOpenNurbsTranslator](DatasmithOpenNurbsTranslator.md)**: 专门处理 OpenNurbs (.3dm) 文件格式的翻译器。
- **[DatasmithPLMXMLTranslator](DatasmithPLMXMLTranslator.md)**: 处理 PLMXML 文件格式的翻译器，常用于产品生命周期管理数据。
- **[DatasmithWireTranslator](DatasmithWireTranslator.md)**: 处理线框（Wire）数据的翻译器。

### 参数化曲面处理
- **[ParametricSurface](ParametricSurface.md)**: 处理参数化曲面的核心模块。
- **[ParametricSurfaceExtension](ParametricSurfaceExtension.md)**: 参数化曲面模块的扩展功能。

### Wire 接口版本模块
这些模块为不同版本的 CAD 软件 Wire 格式提供支持：
- **[WireInterface2020](WireInterface2020.md)**
- **[WireInterface2021_3](WireInterface2021_3.md)**
- **[WireInterface2022](WireInterface2022.md)**
- **[WireInterface2022_1](WireInterface2022_1.md)**
- **[WireInterface2022_2](WireInterface2022_2.md)**
- **[WireInterface2023_0](WireInterface2023_0.md)**
- **[WireInterface2023_1](WireInterface2023_1.md)**
- **[WireInterface2024_1](WireInterface2024_1.md)**
- **[WireInterface2025_0](WireInterface2025_0.md)**
- **[WireInterface2026_0](WireInterface2026_0.md)**

## 模块依赖

要使用或扩展此插件，你的模块可能需要依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `TechSoft` | 提供对 TechSoft 3D ACIS 内核的访问，用于处理高级 CAD 几何体。 |
| `OpenNurbs6` | 提供对 OpenNurbs 库的访问，用于解析 .3dm 等文件格式。 |
| `DatasmithCore` | Datasmith 的核心框架，是此插件的基础。 |

## 维护状态

### 近期更新
（基于提供的创建时间和企业级插件性质推断，具体 commit 信息需查询仓库）
- 作为 Epic Games 官方维护的企业级插件，通常会跟随引擎版本进行更新和兼容性修复。
- 主要更新可能集中在支持新版本的 CAD 软件 Wire 格式（如新增的 WireInterface 模块）以及性能优化和 Bug 修复。

### 维护评价
- **创建时间**：约 6 年前，是一个相对成熟的插件。
- **维护状态**：作为 Datasmith 商业套件的核心组件，预计处于**活跃维护**状态，以确保对最新 CAD 软件版本的支持和引擎兼容性。
- **推荐使用**：**强烈推荐**给所有需要将专业 CAD 数据导入 Unreal Engine 的用户。它是处理此类数据的官方和最可靠的解决方案。需要注意的是，它默认未启用，且依赖特定的第三方库（TechSoft, OpenNurbs），在打包或分发时需注意许可和部署问题。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests) (如果存在)