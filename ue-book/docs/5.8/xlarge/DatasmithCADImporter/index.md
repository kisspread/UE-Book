# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | 数据智能CAD导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

这是一个强大的CAD数据导入与处理框架，远不止是简单的文件导入器。它核心目的是解决从专业工业设计/建筑信息模型(BIM)软件（如CATIA, NX, SolidWorks, Revit等）将复杂的CAD数据（包括精确的几何体、结构层次、材质信息）高质量转换到UE5中使用的问题。它提供了一个分层架构，通过**CADInterfaces**与外部CAD库（如TechSoft）通信，由**DatasmithCADTranslator**等模块协调翻译过程，最终利用**ParametricSurface**等模块将CAD中的参数化曲面（如BREP）转换为UE可用的网格。

## 使用场景

- **建筑可视化 (AEC)**：将Revit, ArchiCAD等BIM软件创建的建筑模型导入UE，保留墙体、门窗等构件信息。
- **汽车与制造业**：导入CATIA, NX, SolidWorks等软件生成的复杂机械零件和装配体，用于产品展示、虚拟验证或培训模拟。
- **工业设计评审**：设计师在UE中评审CAD模型的外观、结构和运动机构，无需依赖原生CAD软件。
- **PLM数据集成**：通过**DatasmithPLMXMLTranslator**导入产品生命周期管理(PLM)系统的结构数据。
- **历史数据兼容**：通过众多版本的**WireInterface**模块，支持与多年份发布的CAD软件版本进行通信和数据交换。

## 模块列表

本插件采用模块化设计，以适应复杂的CAD处理流程。

| 模块 | 类型 | 一句话说明 |
|---|---|---|
| `CADInterfaces` | Runtime | 核心接口层，负责与外部CAD库（如TechSoft）通信，定义通用数据接口。 |
| `CADLibrary` | Runtime | 提供CAD数据结构的基础库，如几何体、材质、层的通用表示。 |
| `CADTools` | Runtime | 提供处理CAD数据的工具集，如网格优化、曲面细分等。 |
| `CADKernelSurface` | Runtime | 使用CAD内核进行曲面处理和网格化的模块。 |
| `ParametricSurface` | Runtime | 将CAD参数化曲面（如B-Rep）转换为三角化网格的核心处理模块。 |
| `ParametricSurfaceExtension` | Runtime | 对`ParametricSurface`功能的扩展和补充。 |
| `DatasmithCADTranslator` | Runtime | 通用的CAD文件翻译器协调模块，负责驱动整个导入流程。 |
| `DatasmithDispatcher` | Runtime | 负责在多进程/多线程环境下分发CAD转换任务。 |
| `DatasmithOpenNurbsTranslator` | Runtime | 专门处理OpenNurbs（.3dm）格式文件的翻译器。 |
| `DatasmithPLMXMLTranslator` | Runtime | 专门处理PLMXML格式文件的翻译器，用于导入PLM系统结构。 |
| `DatasmithWireTranslator` | Runtime | 处理通过`WireInterface`通信的CAD数据的翻译器。 |
| `WireInterface20XX` | Runtime | 系列模块，提供与特定年份版本（2020-2026）CAD软件的通信接口适配层。 |

## 使用场景

- **蓝图用法**：主要通过`DatasmithCADTranslator`模块提供的蓝图节点（如文件导入、参数设置）进行操作。具体节点需查阅子模块文档。
- **C++用法**：涉及继承和扩展`CADInterfaces`以支持新的CAD格式，或使用`CADLibrary`中的类来处理转换后的几何数据。详细API请参考各子模块的独立文档。

## Demo 示例

作为大型数据处理框架，其使用通常通过Datasmith的整体导入流程触发。一个典型的C++集成示例是监听导入事件并处理转换后的资产：

```cpp
// 引入必要的头文件
#include "DatasmithCADTranslatorModule.h"
#include "CADLibrary/Public/ICADInterfaces.h"

// 假设在某个管理器类中
void FMyCADManager::OnDatasmithImportCompleted(const TArray<UObject*>& ImportedAssets)
{
    // 遍历所有导入的资产
    for (UObject* Asset : ImportedAssets)
    {
        // 检查是否为从CAD导入的StaticMesh
        if (UStaticMesh* Mesh = Cast<UStaticMesh>(Asset))
        {
            // 可以进一步访问与CAD相关的元数据或进行后续处理
            // 例如，检查原始CAD数据或应用特定后处理
        }
    }
}
```

## 模块依赖

本插件依赖多个外部库和引擎模块来支持各种CAD格式。

| 模块 | 用途 |
|---|---|
| `TechSoft` | 核心依赖，提供对主流CAD格式（如STEP, IGES, CATIA, NX等）的底层读写支持。 |
| `OpenNurbs6` | 为`DatasmithOpenNurbsTranslator`模块提供对OpenNurbs（.3dm）格式的支持。 |
| `DatasmithContent` | Datasmith的基础内容和核心功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量转单精度的警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 增加逻辑，使Wire翻译器在安装了Alias 2027时也能工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将TechSoft库更新到2026.3版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了DatasmithCAD缓存版本。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在MSVC和Clang编译器间可移植。 |

### 维护评价

该插件创建于2019年，是一个**成熟**的企业级工具。尽管`EnabledByDefault=false`表明它需要特定激活，但其核心模块仍在持续维护。从近期更新看，维护重点在于**兼容性更新**（如支持新CAD软件版本、更新第三方库）和**代码质量改善**（修复警告）。这表明它仍是官方支持的、用于CAD数据导入的重要管道，但功能相对稳定，新特性迭代较少。**推荐**在需要CAD导入的专业领域项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Enterprise/DatasmithCADImporter)