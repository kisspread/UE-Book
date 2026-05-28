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
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

本插件是 Datasmith 框架的扩展，专注于将**工业级 CAD 文件**（如 CATIA, NX, SolidWorks, STEP, IGES 等）和**特定工程软件格式**（如 PLMXML， Alias/Wire 文件）导入到虚幻引擎中。它并非一个简单的文件格式转换器，而是一个包含**解析、曲面重建、网格生成、场景组织**的完整处理流水线。

其核心价值在于将复杂的参数化 CAD 模型（包含精确的几何体和装配体信息）高效地转换为适合实时渲染的三角化网格，并保留完整的元数据和结构信息，支持汽车、航空航天、工业制造等领域的数字孪生和可视化应用。

## 使用场景

- **汽车设计可视化**：设计师在 Alias 中完成的汽车A面模型，可以直接导入虚幻引擎进行实时渲染、评审和虚拟展示。
- **工业设备数字孪生**：使用 CATIA 或 NX 设计的复杂装配体，导入引擎后用于创建交互式维护手册或虚拟培训系统。
- **PLM 系统集成**：从 Teamcenter 等 PLM 系统中导出的 PLMXML 数据包，可以批量、自动化地导入引擎，构建产品目录或数字孪生库。

## 蓝图用法

此插件主要提供底层的 C++ 翻译器（Translator）接口，通常**不直接提供蓝图节点**。其功能通过 `Datasmith` 导入流程间接使用。

用户在编辑器中通过“Datasmith 导入”选择 CAD 文件时，此插件中的翻译器会被自动调用。高级用户可以通过 C++ 编程方式直接调用其接口。

## C++ 用法

本插件的核心是实现了 `IDatasmithTranslator` 接口的一系列翻译器。

### 头文件引入

```cpp
// 要使用特定的翻译器，例如 PLMXML 翻译器
#include "DatasmithPlmXmlTranslatorModule.h"
```

### 基本用法（调用翻译器）

翻译器通常由 Datasmith 导入管理器自动实例化和调用。但如果你需要编程控制导入过程，可以按照以下模式操作。以下代码基于 `FDatasmithPlmXmlTranslator` 接口。

**来源：** `Source/DatasmithPLMXMLTranslator/Private/DatasmithPlmXmlTranslator.h`

```cpp
// 1. 检查翻译器模块是否可用
if (IDatasmithPlmXmlTranslatorModule::IsAvailable())
{
    // 2. 通过工厂创建翻译器实例 (通常由 Datasmith 框架完成)
    // TSharedPtr<IDatasmithTranslator> Translator = ...;
    // 3. 初始化并设置能力
    // FDatasmithTranslatorCapabilities Capabilities;
    // Translator->Initialize(Capabilities);
    
    // 4. 加载场景 (解析文件)
    TSharedRef<IDatasmithScene> Scene = FDatasmithSceneFactory::CreateScene(TEXT("MyScene"));
    if (Translator->LoadScene(Scene))
    {
        // 5. 场景加载成功，`Scene` 中包含了从 CAD 文件解析出的所有元素
        // 可以遍历 Scene->GetMeshes(), Scene->GetActors() 等获取数据
        
        // 6. 对于网格元素，可以按需加载其网格数据
        // for (const TSharedPtr<IDatasmithMeshElement>& MeshElement : Scene->GetMeshes())
        // {
        //     FDatasmithMeshElementPayload MeshPayload;
        //     if (Translator->LoadStaticMesh(MeshElement.ToSharedRef(), MeshPayload))
        //     {
        //         // 使用 MeshPayload 中的顶点、索引等数据构建 UStaticMesh
        //     }
        // }
        
        // 7. 完成后卸载场景
        Translator->UnloadScene();
    }
}
```

### 进阶用法（架构理解）

整个插件由多个协作模块组成：
1.  **翻译器 (`DatasmithCADTranslator`, `DatasmithWireTranslator` 等)**: 负责识别特定文件格式并驱动整个导入流程。
2.  **核心库 (`CADLibrary`, `CADTools`)**: 提供通用的几何处理、网格操作工具。
3.  **接口库 (`CADInterfaces`)**: 封装对第三方几何内核（如 TechSoft）的访问。
4.  **曲面重建 (`ParametricSurface`, `CADKernelSurface`)**: 将 CAD 参数化曲面转换为三角化网格。
5.  **进程调度 (`DatasmithDispatcher`)**: 通过启动子进程来处理大型 CAD 文件的几何计算，避免阻塞编辑器主线程。

## Demo 示例

本插件的集成示例主要体现在对 `IDatasmithTranslator` 接口的实现上。一个简化的翻译器头文件示例如下：

```cpp
// MyCustomCadTranslator.h
#pragma once
#include "IDatasmithTranslator.h"

class FMyCustomCadTranslator : public IDatasmithTranslator
{
public:
    virtual FName GetFName() const override { return TEXT("MyCustomCadTranslator"); }
    virtual void Initialize(FDatasmithTranslatorCapabilities& OutCapabilities) override;
    virtual bool LoadScene(TSharedRef<IDatasmithScene> OutScene) override;
    virtual void UnloadScene() override;
    virtual bool LoadStaticMesh(const TSharedRef<IDatasmithMeshElement> MeshElement, FDatasmithMeshElementPayload& OutMeshPayload) override;
    virtual bool IsSourceSupported(const FDatasmithSceneSource& Source) override;
    // ... 其他接口实现
};
```

对应的实现文件（.cpp）将包含具体的文件解析逻辑，这正是本插件中各个 Translator 模块所做的工作。

## 模块依赖

从各模块的 `Build.cs` 分析，本插件依赖于多个第三方库和引擎模块。

| 模块 | 用途 |
|---|---|
| `TechSoft` | 访问 TechSoft 3D SDK，用于解析 CATIA, NX, JT, STEP, IGES 等多种 CAD 格式的核心引擎。 |
| `OpenNurbs6` | 用于解析 Rhino (3DM) 文件格式的开放源码库。 |
| `Datasmith` | 核心 Datasmith 框架模块，提供场景元素接口和导入基础设施。 |
| `MeshConversion` | 用于在不同网格数据格式之间进行转换。 |
| `MeshDescription` | 提供描述三角网格的抽象数据结构，用于构建 `UStaticMesh`。 |

**注意**：实际编译时，你的 Build.cs 需要确保链接到 `TechSoft` 和 `OpenNurbs6` 等第三方库，并设置正确的包含路径。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量被截断为单精度时产生的编译警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 增加逻辑，确保即使安装了 Alias 2027，Wire 翻译器仍能正常工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将 TechSoft 3D SDK 更新到 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 Datasmith CAD 缓存的版本标识。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器之间保持可移植性。 |

### 维护评价

**维护状态：活跃维护**
- **创建时间**：插件于 2019 年随“Dev-Enterprise”分支合并引入，已有约 6 年历史，属于成熟的工业级功能模块。
- **近期活动**：在最近几天内有多个提交，涉及**第三方库升级**（TechSoft）、**兼容性修复**（针对 Alias 2027）和**代码质量改进**，表明该插件仍在积极迭代和维护中。
- **稳定性与推荐**：作为 Epic Games 官方企业版功能的一部分，用于支持高端可视化客户，其稳定性和功能性有保障。**推荐**给有明确 CAD 数据导入需求的企业用户或大型项目使用。由于默认未启用（`EnabledByDefault: false`），用户需手动在插件列表中开启。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)