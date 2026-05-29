# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | Alias Wire 翻译模块 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `WireInterface2020` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter/Source/WireInterface) | |

## 用途

`WireInterface2020` 是 Datasmith CAD Importer 插件中的一个**专用翻译模块**，用于读取和转换 Autodesk Alias（`.wire` 格式）文件。

该模块的核心功能是将 Alias 软件生成的 `.wire` 文件（一种行业标准的 A 级曲面设计格式）解析并转换为 Unreal Engine 的 Datasmith 场景。它解决了 Alias 设计师将精确的曲面模型数据直接导入到 Unreal 中进行实时可视化、评审和虚拟展示的需求。它并非通用的 CAD 导入器，而是专门处理 Alias 软件输出的数据结构。

## 使用场景

- **汽车设计可视化**：汽车设计师在 Alias 中完成 A 级曲面设计后，需要将 `.wire` 文件直接导入 Unreal，用于制作高质量的实时渲染演示或 VR 评审。
- **产品设计流程**：工业设计师使用 Alias 进行复杂曲面建模后，希望在 Unreal 中预览产品在真实光照下的效果，并进行设计验证。
- **跨部门协作**：设计部门提交 `.wire` 文件，下游的可视化或开发团队使用此模块将其无缝集成到 Unreal 项目中。

## 蓝图用法

该模块主要提供 C++ 层面的接口，蓝图直接操作有限。核心的蓝图相关功能体现在**模块状态检查**上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FDatasmithWireTranslatorModule::IsAvailable()` | 检查 `.wire` 翻译模块是否已加载并可用。 | `FDatasmithWireTranslatorModule` |
| `FDatasmithWireTranslatorModule::GetTempDir()` | 获取翻译器使用的临时目录路径（用于中间文件处理）。 | `FDatasmithWireTranslatorModule` |

### 使用示例（蓝图描述）

在蓝图中，你无法直接触发 `.wire` 文件的翻译过程，但可以通过“获取模块”节点检查 `DatasmithWireTranslator` 模块是否可用。例如，在导入工作流开始前，你可以执行一个检查：使用 `FModuleManager::Get().IsModuleLoaded(TEXT("DatasmithWireTranslator2020"))` 的蓝图等效节点（如“Is Module Loaded”），确保翻译器就绪。

## C++ 用法

### 头文件引入

```cpp
#include "WireInterfaceModule.h"
```

### 基本用法

检查 `.wire` 翻译模块是否可用，并获取其临时目录。
(来源: `Public/WireInterfaceModule.h`)

```cpp
// 在你的代码中，首先检查模块是否加载
if (UE::DatasmithWireTranslator::FDatasmithWireTranslatorModule::IsAvailable())
{
    // 获取翻译器模块实例
    UE::DatasmithWireTranslator::FDatasmithWireTranslatorModule& WireModule = UE::DatasmithWireTranslator::FDatasmithWireTranslatorModule::Get();
    
    // 获取用于中间文件处理的临时目录
    FString TempDirectory = WireModule.GetTempDir();
    UE_LOG(LogTemp, Log, TEXT("Wire Translator Temp Dir: %s"), *TempDirectory);
    
    // 模块已就绪，后续的 .wire 文件导入流程将由 Datasmith 管线自动调度此模块
}
else
{
    UE_LOG(LogTemp, Warning, TEXT("Datasmith Wire Translator module is not loaded."));
}
```

### 进阶用法

理解翻译器的核心实现类 `FWireTranslatorImpl` 的工作流程。它实现了 `IWireInterface` 接口，主要步骤是：
1.  **初始化** (`Initialize`)：接收 `.wire` 文件的完整路径。
2.  **加载** (`Load`)：将文件解析为 `IDatasmithScene`。这是核心过程，涉及遍历 Alias 的 DAG 节点、处理几何体（网格、壳体、曲面）、转换材质和变换。
3.  **获取网格** (`LoadStaticMesh`)：当需要具体网格数据时被调用。

在自定义导入工具或测试中，你可以模拟这个流程（尽管通常由 Datasmith 导入器自动完成）：
(来源: `Private/WireInterfaceImpl.h`)

```cpp
// 伪代码示例，展示翻译器内部逻辑
using namespace UE_DATASMITHWIRETRANSLATOR_NAMESPACE;

void MyCustomWireImport(const TCHAR* WireFilePath)
{
    // 创建翻译器实例（在实际 Datasmith 流程中由工厂创建）
    TSharedPtr<FWireTranslatorImpl> Translator = MakeShared<FWireTranslatorImpl>();
    
    // 配置导入选项
    FWireSettings ImportSettings;
    // ... 设置导入选项 ...
    Translator->SetImportSettings(ImportSettings);
    
    // 初始化翻译器，关联到具体的 .wire 文件
    if (Translator->Initialize(WireFilePath))
    {
        // 创建目标 Datasmith 场景容器
        TSharedPtr<IDatasmithScene> TargetScene = FDatasmithSceneFactory::CreateScene(TEXT("MyWireImport"));
        
        // 执行加载，将 .wire 文件内容解析到 TargetScene 中
        if (Translator->Load(TargetScene))
        {
            UE_LOG(LogTemp, Log, TEXT("Successfully loaded Wire scene into Datasmith scene."));
            // 此时，TargetScene 已经包含了从 .wire 文件解析出的层次结构、网格、材质等信息
            // 你可以进一步处理这个场景，例如将其添加到 Datasmith 导入器的处理队列中
        }
    }
}
```

## Demo 示例

以下是一个最小的 C++ 示例，演示如何使用 `WireInterfaceModule` 来检查并获取模块。
（注：实际的文件导入由 Datasmith 导入系统触发，此示例仅为演示模块交互）

**MyWireChecker.h**
```cpp
#pragma once
#include "CoreMinimal.h"

class FMyWireChecker
{
public:
    static bool IsWireTranslatorReady();
    static FString GetTranslatorTempPath();
};
```

**MyWireChecker.cpp**
```cpp
#include "MyWireChecker.h"
#include "WireInterfaceModule.h"

bool FMyWireChecker::IsWireTranslatorReady()
{
    // 检查名为 DatasmithWireTranslator2020 的模块是否已加载
    // 模块名通常由 UE_STRINGIZE(UE_DATASMITHWIRETRANSLATOR_MODULE_NAME) 定义
    return FModuleManager::Get().IsModuleLoaded(TEXT("DatasmithWireTranslator2020"));
}

FString FMyWireChecker::GetTranslatorTempPath()
{
    if (IsWireTranslatorReady())
    {
        // 使用静态 Get 方法获取已加载的模块实例
        return UE::DatasmithWireTranslator::FDatasmithWireTranslatorModule::Get().GetTempDir();
    }
    return FString();
}
```

## 模块依赖

要使用 `WireInterface2020` 模块，你的项目需要链接以下依赖（从 `WireInterface2020.Build.cs` 提取）。**注意：** 这些是该模块的独特依赖，核心的 `Core`, `Engine` 等常见模块已省略。

| 模块 | 用途 |
|---|---|
| `TechSoft` | 提供用于 CAD 内核转换的 TechSoft (HOOPS) 工具库，是处理复杂 B-Rep 几何的关键依赖。 |
| `CADKernelSurface` | 用于参数化曲面（如 Alias 曲面）的几何处理和细分。 |
| `ParametricSurface` | 处理参数化曲面定义。 |
| `CADLibrary` | Datasmith CAD 导入的核心库，提供通用的 CAD 模型转换接口和工具。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数产生的编译警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 增加逻辑以支持在安装了 Alias 2027 版本后，翻译器仍能正常工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将底层依赖 TechSoft 库升级到 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 Datasmith CAD 缓存的版本标识。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器之间可移植。 |

### 维护评价

- **活跃维护**：近期（2026年5月）仍有实质性更新，主要集中在**依赖库升级**（TechSoft）和**兼容性修复**（支持新版 Alias 2027、编译器警告修复）。这表明该模块仍处于活跃维护状态，以跟进其核心依赖 Alias 和 TechSoft 的更新。
- **创建较久**：该模块（作为更大插件的一部分）创建于2019年，已有7年历史，属于成熟模块。
- **专业性强**：作为 Alias 专用翻译器，其维护与 Alias 软件版本发布节奏密切相关。
- **推荐使用**：对于需要将 Autodesk Alias (`.wire`) 文件集成到 Unreal Engine 5 的专业工作流（如汽车设计可视化），这是官方支持的推荐方式。使用前需确保正确安装并启用了 `DatasmithCADImporter` 插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter/Source/WireInterface)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Enterprise/DatasmithTests) (通用 Datasmith 测试)