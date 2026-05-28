# Datasmith CAD Importer

> Collection of tools to work with CAD files.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | CAD 导入工具 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

DatasmithCADImporter 是一个企业级插件，专注于在 Unreal Engine 中导入和处理各种专业 CAD（计算机辅助设计）文件格式。它不仅仅是一个简单的文件导入器，而是一个包含多个子模块的综合工具集，能够解析复杂的 CAD 数据结构（如 B-Rep 模型、参数化曲面、装配体层级），并将其转换为 UE 可用的 Datasmith 场景元素（如 Static Mesh、PBR 材质、场景演员）。

该插件的核心价值在于解决工业设计、汽车、建筑等行业中，将 CAD 软件（如 Alias、CATIA、NX）产生的高精度、参数化模型无缝引入到 UE 游戏引擎或可视化项目中的难题。它处理了坐标系转换、几何体曲面细分（Tessellation）、材质映射和装配体结构保持等关键挑战。

## 使用场景

- 你在汽车行业做设计评审或虚拟展示 → 需要将 Alias 或 CATIA 模型导入 UE 并保持其材质和装配关系。
- 你在工业设备领域做数字孪生 → 需要将 NX 或 Creo 的复杂机械装配体导入 UE 进行交互式演示。
- 你在建筑行业做 BIM 可视化 → 需要处理包含复杂曲面（如幕墙）的 CAD 模型。
- 你需要将 PLMXML 格式的产品生命周期管理数据导入 UE。

## 蓝图用法

此插件主要为运行时翻译器，其蓝图接口主要集中在 `DatasmithCADTranslator` 模块提供的高层导入功能。核心节点通常封装在 `UDatasmithCADImportOptions` 等类中，用于配置导入选项。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ImportFile` | 触发 CAD 文件的导入流程。 | `UDatasmithCADTranslatorFactory` |
| `GetSupportedFileFormats` | 获取支持的 CAD 文件格式列表。 | `UDatasmithCADTranslator` |
| `设置细分选项` | 配置 CAD 模型导入时的曲面细分精度。 | `UDatasmithCADImportOptions` |

### 使用示例（蓝图描述）

在蓝图中，通常不会直接操作底层的 `WireInterface`。而是通过 Datasmith 的通用导入流程：
1. 创建一个 `UDatasmithCADImportOptions` 对象，设置所需的细分精度和材质处理规则。
2. 使用 `Datasmith Import Action` 节点，并将上述选项对象作为参数传入。
3. 指定要导入的 `.wire`、`.catpart` 等文件路径。
4. 执行导入，引擎会自动调用对应的内部翻译器（如 `WireInterface2023_0`）来处理文件。

## C++ 用法

此插件的 C++ 用法深度集成在 Datasmith 框架中，开发者通常通过继承或使用现有的翻译器接口来扩展或驱动导入过程。

### 头文件引入

```cpp
#include "DatasmithTranslator.h"
#include "WireInterfaceModule.h"
// 根据具体需要引入对应版本的 WireInterface 头文件，如 WireInterface2023_0 模块
```

### 基本用法

从 `WireInterfaceModule.h` 和 `WireInterfaceImpl.h` 推断，使用 WireInterface 翻译器需要遵循 Datasmith 的翻译器模式。以下是一个概念性的用法示例：

```cpp
// 来源： WireInterfaceModule.h, WireInterfaceImpl.h 推断
#include "IDatasmithSceneElements.h"
#include "WireInterfaceModule.h"

void ImportWireFile(const FString& WireFilePath)
{
    // 1. 确保 WireInterface 模块已加载
    if (!UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("WireInterface module not available."));
        return;
    }

    // 2. 创建一个 Datasmith 场景来接收数据
    TSharedPtr<IDatasmithScene> DatasmithScene = FDatasmithSceneFactory::CreateScene(*FPaths::GetBaseFilename(WireFilePath));

    // 3. 创建并初始化 Wire 翻译器实现 (通常由工厂类内部完成)
    // FWireTranslatorImpl Translator; // 这是内部类，实际不直接实例化
    // Translator.Initialize(*WireFilePath);
    // Translator.SetImportSettings(MyWireSettings); // 配置选项
    // Translator.Load(DatasmithScene);

    // 4. 在实际架构中，你会通过 Datasmith Translator 工厂获取对应的翻译器实例
    TSharedPtr<IDatasmithTranslator> Translator = FDatasmithTranslatorsFirstMatching::Get().CreateTranslator(WireFilePath);
    if (Translator)
    {
        FDatasmithTranslationOptions Options;
        // ... 设置选项
        Translator->Translate(DatasmithScene.ToSharedRef(), Options);
    }

    // 5. DatasmithScene 现在包含了从 .wire 文件解析出的场景元素（演员、网格、材质）
    // 接下来可以将其用于创建真实的 UE 资产或临时场景。
}
```

### 进阶用法

进阶用法涉及自定义转换器，例如将 Alias 模型同时转换为 CADKernel 和 TechSoft 格式以供内部处理。从 `AliasModelToCADKernelConverter.h` 和 `AliasModelToTechSoftConverter.h` 可以看出，插件提供了灵活的后端选择。

```cpp
// 来源： AliasModelToCADKernelConverter.h, AliasModelToTechSoftConverter.h
#include "AliasModelToCADKernelConverter.h"
#include "AliasModelToTechSoftConverter.h"
#include "CADLibrary.h"

void ConvertAliasGeometry(const FAlDagNodePtr& DagNode, CADLibrary::FImportParameters ImportParams)
{
    FDatasmithTessellationOptions TessOptions;
    // ... 配置细分选项

    // 方式一：使用 CADKernel 后端进行转换和细分
    UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FAliasModelToCADKernelConverter CADKernelConverter(TessOptions, ImportParams);
    CADKernelConverter.AddBRep(DagNode, FColor::White, EAliasObjectReference::LocalReference);
    // ... 执行 RepairTopology, Tessellate 等步骤获取 FMeshDescription

    // 方式二：使用 TechSoft (HOOPS) 后端进行转换
    UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FAliasModelToTechSoftConverter TechSoftConverter(ImportParams);
    TechSoftConverter.AddBRep(DagNode, 0 /* SlotID */, EAliasObjectReference::LocalReference);
    // ... 利用 TechSoft 内核进行后续操作
}
```

## Demo 示例

以下示例展示如何在 C++ 中，通过 Datasmith 框架的理念，模拟加载一个 Wire 文件并遍历其转换后的 Actor 结构。这是一个简化模型。

```cpp
// WireDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "WireDemo.generated.h"

class IDatasmithScene;
class IDatasmithActorElement;

UCLASS()
class AWireDemo : public AActor
{
    GENERATED_BODY()

public:
    AWireDemo();

    virtual void BeginPlay() override;

    // 模拟加载 Wire 文件并打印场景信息
    UFUNCTION(BlueprintCallable, Category = "Wire Demo")
    void LoadAndInspectWireScene(const FString& WireFilePath);

private:
    void TraverseDatasmithActor(const TSharedPtr<IDatasmithActorElement>& Actor, int32 Depth);
};
```

```cpp
// WireDemo.cpp
#include "WireDemo.h"
#include "IDatasmithSceneElements.h"
#include "DatasmithSceneFactory.h"
#include "WireInterfaceModule.h"

AWireDemo::AWireDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AWireDemo::BeginPlay()
{
    Super::BeginPlay();
}

void AWireDemo::LoadAndInspectWireScene(const FString& WireFilePath)
{
    if (!UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("Cannot load .wire file: WireInterface module is not loaded."));
        return;
    }

    // 注意：这是一个高度简化的示例。实际流程应通过 FDatasmithImporter 或编辑器操作触发。
    // 这里直接创建一个空的 Datasmith 场景对象来演示结构。
    TSharedPtr<IDatasmithScene> Scene = FDatasmithSceneFactory::CreateScene(TEXT("MyWireScene"));

    // 在真实场景中，Translator->Load() 会填充这个 Scene 对象。
    // 这里我们假设它已经被填充了。

    UE_LOG(LogTemp, Log, TEXT("Inspecting Datasmith scene..."));
    for (int32 i = 0; i < Scene->GetActorsCount(); ++i)
    {
        TSharedPtr<IDatasmithActorElement> Actor = Scene->GetActor(i);
        TraverseDatasmithActor(Actor, 0);
    }
}

void AWireDemo::TraverseDatasmithActor(const TSharedPtr<IDatasmithActorElement>& Actor, int32 Depth)
{
    if (!Actor.IsValid()) return;

    FString Indent = FString::ChrN(Depth * 2, ' ');
    UE_LOG(LogTemp, Log, TEXT("%sActor: %s (Type: %d)"), *Indent, *Actor->GetName(), (int32)Actor->GetType());

    // 递归遍历子级
    for (int32 i = 0; i < Actor->GetChildrenCount(); ++i)
    {
        TraverseDatasmithActor(Actor->GetChild(i), Depth + 1);
    }
}
```

## 模块依赖

要使用 DatasmithCADImporter 插件（特别是其 WireInterface 翻译功能），你的项目模块需要依赖以下独特的模块：

| 模块 | 用途 |
|---|---|
| `DatasmithCore` | Datasmith 核心框架，提供场景元素接口和基础翻译器功能。 |
| `CADLibrary` | 本插件的 CAD 处理库，定义通用的 CAD 几何、材质和转换器接口。 |
| `CADInterfaces` | 与第三方 CAD 内核（如 TechSoft HOOPS）交互的接口层。 |
| `WireInterface2023_0` | 针对特定年份/版本的 Alias Wire 文件格式的具体翻译器实现。 |
| `CADKernel` | (来自 Engine/Plugins/) UE 自有的 CAD 几何内核，用于高级几何处理。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量转换为浮点数时产生的编译警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 增加逻辑，使 Wire 翻译器在安装 Alias 2027 的环境下也能工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将 TechSoft (HOOPS) 库更新到 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 Datasmith CAD 缓存的版本。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器之间具有可移植性。 |

### 维护评价

**综合评价：活跃维护，推荐使用。**

1.  **创建时间**：创建于 2019 年，是一个相对成熟的插件。
2.  **近期更新**：最近一次提交在 2026 年 5 13 日，且近一周内有多次提交，内容涵盖兼容性更新（支持 Alias 2027）、第三方库升级（TechSoft）、编译警告修复和缓存版本更新。这表明插件处于**活跃维护**状态，并且 Epic 团队仍在持续改进其与最新 CAD 软件版本的兼容性。
3.  **维护状态**：作为 Epic Games 官方维护的企业级插件，其稳定性和支持有保障。更新专注于兼容性和稳定性，而非颠覆性重构。
4.  **已知限制**：该插件默认未启用 (`EnabledByDefault: false`)，需要用户在项目中手动启用。它依赖于特定的第三方库（TechSoft, OpenNurbs）和可能的 CAD 软件许可证（用于某些格式的读取）。
5.  **推荐使用**：如果你的项目涉及专业 CAD 文件（尤其是 Alias .wire 格式）的导入，并且需要高保真的几何和材质转换，那么这个插件是官方支持的首选方案。建议使用与其目标 CAD 软件版本匹配的 `WireInterfaceXXXX_X` 模块。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Datasmith) (插件没有独立的测试目录，相关测试可能位于 Engine/Tests/Datasmith)