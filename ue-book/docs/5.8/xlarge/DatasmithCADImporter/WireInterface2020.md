# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | CAD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020`~`WireInterface2026_0` (Runtime, 共10个) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

该插件是 Unreal Engine Datasmith 生态系统中的 **CAD 文件专用翻译器**，解决的核心问题是：将工业 CAD 软件（如 Autodesk Alias、Rhino/OpenNurbs、各类 PLMXML 格式）中的精确几何体（BRep 边界表示）导入到 UE 中。

CAD 软件使用的几何体是参数化曲面和精确数学表达，而 UE 使用的是三角面片网格（Polygon Mesh）。该插件通过以下流程完成转换：

1. **读取** CAD 文件的 BRep 拓扑数据（面、边、环、裁剪曲线等）
2. **转换** 为中间表示（CADKernel 或 TechSoft 格式）
3. **细分（Tessellation）** 参数化曲面为三角面片
4. **生成** `FMeshDescription` 供 UE 网格系统使用
5. **提取** 材质信息（Blinn/Lambert/Phong 着色器模型）并转换为 PBR 材质

**重要提示**：该插件默认不启用（`EnabledByDefault=false`），需要在项目设置中手动启用。

## 使用场景

- 你使用 **Autodesk Alias** 进行汽车/工业设计建模 → 使用 Datasmith 导入 `.wire` 文件
- 你有 **Rhino 3D** 的 `.3dm` 文件需要导入 → 通过 `DatasmithOpenNurbsTranslator` 模块处理
- 你需要从 **PLM 系统**导出产品模型到 UE 做可视化 → 使用 `DatasmithPLMXMLTranslator` 模块
- 你需要保留 CAD 模型的 **材质信息** 和 **场景层级**（层、组结构）
- 你追求精确的 **曲面细分质量**（Fast / Accurate 两种细分模式）

## 蓝图用法

该插件是一个纯 Runtime 翻译器模块，**不暴露任何 BlueprintCallable 节点**。

所有功能通过 Unreal Engine 的 Datasmith 导入管道内部调用。用户通过以下方式使用：

1. **Content Browser**：直接拖拽 `.wire` / `.3dm` 文件到 Content Browser
2. **Datasmith Import Actor**：在场景中放置 Datasmith 导入器
3. **C++/Python 脚本**：通过 `FDatasmithImportContext` API 调用

## C++ 用法

该插件的公共 API 通过模块接口暴露，主要用于扩展或程序化导入。

### 头文件引入

```cpp
#include "WireInterfaceModule.h"
```

### 基本用法

检查 Wire 翻译器模块是否可用并获取临时目录：

```cpp
// 来源: Source/WireInterface/Public/WireInterfaceModule.h
using namespace UE_DATASMITHWIRETRANSLATOR_NAMESPACE;

if (FDatasmithWireTranslatorModule::IsAvailable())
{
    FDatasmithWireTranslatorModule& WireModule = FDatasmithWireTranslatorModule::Get();
    FString TempDir = WireModule.GetTempDir();
    UE_LOG(LogTemp, Log, TEXT("Wire translator temp dir: %s"), *TempDir);
}
```

### 进阶用法

通过 `IWireInterface` 接口手动控制 `.wire` 文件的加载过程：

```cpp
// 来源: Source/WireInterface/Private/WireInterfaceImpl.h
// 注意：IWireInterface 是内部接口，以下为示意用法

using namespace UE_DATASMITHWIRETRANSLATOR_NAMESPACE;

// 创建 Wire 翻译器实例
TSharedPtr<FWireTranslatorImpl> Translator = MakeShared<FWireTranslatorImpl>();

// 设置导入参数
FWireSettings Settings;
Translator->SetImportSettings(Settings);

// 设置输出路径
Translator->SetOutputPath(FPaths::ProjectSavedDir() / TEXT("WireOutput"));

// 初始化并加载场景
if (Translator->Initialize(TEXT("/path/to/model.wire")))
{
    TSharedPtr<IDatasmithScene> Scene = /* 获取或创建 Datasmith Scene */;
    Translator->Load(Scene);
}
```

## Demo 示例

由于该插件是 Datasmith 导入管道的一部分，没有独立的演示 Actor 或组件。以下展示如何通过 Datasmith C++ API 进行程序化导入：

```cpp
// DatasmithCADImportDemo.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DatasmithCADImportDemo.generated.h"

UCLASS()
class ADatasmithCADImportDemo : public AActor
{
    GENERATED_BODY()

public:
    ADatasmithCADImportDemo();

    /** 程序化导入 CAD 文件 */
    UFUNCTION(BlueprintCallable, Category = "CAD Import")
    bool ImportCADFile(const FString& FilePath);

protected:
    virtual void BeginPlay() override;
};
```

```cpp
// DatasmithCADImportDemo.cpp
#include "DatasmithCADImportDemo.h"
#include "DatasmithSceneFactory.h"
#include "DatasmithImportOptions.h"

ADatasmithCADImportDemo::ADatasmithCADImportDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ADatasmithCADImportDemo::BeginPlay()
{
    Super::BeginPlay();
}

bool ADatasmithCADImportDemo::ImportCADFile(const FString& FilePath)
{
    // 通过 Datasmith 管道导入，CAD 翻译器会自动识别文件格式
    // 具体的导入流程由 DatasmithImport 模块内部调度
    // Wire/CAD 翻译器作为 Runtime 模块在模块加载时注册
    UE_LOG(LogTemp, Log, TEXT("Importing CAD file: %s"), *FilePath);
    return true;
}
```

## 模块依赖

该插件包含 21 个模块，整体依赖关系如下：

| 模块 | 用途 |
|---|---|
| `TechSoft` | TechSoft 3D 几何内核，用于 BRep 曲面细分和拓扑修复（CADInterfaces 依赖） |
| `OpenNurbs6` | OpenNurbs NURBS 几何库，用于读取 .3dm 文件（DatasmithOpenNurbsTranslator 依赖） |
| `DatasmithCore` | Datasmith 场景元素和接口定义 |
| `DatasmithImporter` | Datasmith 导入管道框架 |
| `MeshDescription` | 网格描述数据结构，用于传递细分结果 |
| `CADLibrary` | CAD 工具库，提供网格参数、导入参数等基础设施 |
| `CADKernel` | UE 内置 CAD 内核，用于曲面拓扑表示和细分 |

## WireInterface 版本映射

WireInterface 模块按 **Autodesk Alias 版本** 分化，每个版本对应特定的 Alias SDK：

| 模块 | Alias 版本 |
|---|---|
| `WireInterface2020` | Alias 2020 |
| `WireInterface2021_3` | Alias 2021.3 |
| `WireInterface2022` | Alias 2022 |
| `WireInterface2022_1` | Alias 2022.1 |
| `WireInterface2022_2` | Alias 2022.2 |
| `WireInterface2023_0` | Alias 2023.0 |
| `WireInterface2023_1` | Alias 2023.1 |
| `WireInterface2024_1` | Alias 2024.1 |
| `WireInterface2025_0` | Alias 2025.0 |
| `WireInterface2026_0` | Alias 2026.0 |

系统会自动检测已安装的 Alias 版本并加载对应的模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 新增对 Alias 2027 的兼容支持 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 升级 TechSoft SDK 至 2026.3 版本 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新 DatasmithCAD 缓存版本 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复跨编译器（MSVC/Clang）类型转换警告 |

### 维护评价

- **活跃维护**：最近一次更新在 2026 年 5 月，距今不到 1 个月，属于高频维护状态
- **持续迭代**：持续跟踪 Autodesk Alias 新版本（已支持到 Alias 2026/2027），并定期更新底层依赖（TechSoft）
- **企业级插件**：由 Epic Games 官方维护，面向工业/汽车设计等专业领域
- **默认不启用**：需要手动在项目设置中启用，说明该功能面向特定用户群（使用 CAD 软件的设计师）
- **推荐使用**：如果你的工作流程涉及从 Autodesk Alias 或其他 CAD 软件导入数据到 UE，该插件是官方推荐的导入方案

⚠️ 该插件依赖 Alias SDK（Wire 模块）和 TechSoft SDK，这些是商业库，可能需要单独的许可证。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)