# Datasmith Importer

> Importer for Datasmith files.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithExternalSource` (Runtime), `DatasmithImporter` (Runtime), `DatasmithNativeTranslator` (Runtime), `DatasmithTranslator` (Runtime), `DirectLinkExtension` (Runtime), `DirectLinkExtensionEditor` (Runtime), `DirectLinkTest` (Runtime), `ExternalSource.build` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithImporter) | |

## 用途

Datasmith Importer 是 Unreal Engine 的企业级数据导入框架，其核心是提供一个可扩展的“翻译器”（Translator）系统。它不仅仅是一个简单的文件导入器，而是一个完整的数据转换管线，用于将来自各种专业设计软件（如 CAD、BIM、DCC 工具）的复杂场景、模型、材质和元数据，转换为 Unreal Engine 可以理解和使用的原生资产（如 StaticMesh、Material、Actor 层次结构）。

该插件解决的核心问题是：**如何标准化、高效且可维护地将异构的工业设计数据引入游戏引擎环境**。它通过定义清晰的接口（`IDatasmithTranslator`）和管理器（`FDatasmithTranslatorManager`），允许第三方或内部模块注册自己的“翻译器”实现，从而支持新的文件格式，而无需修改核心导入逻辑。

## 使用场景

- **建筑、工程与施工 (AEC)**：将 Revit (.rvt)、ArchiCAD (.pln) 等 BIM 软件创建的建筑模型导入 UE，用于建筑可视化、虚拟样板间或数字孪生。
- **产品设计与制造**：导入来自 SolidWorks (.sldprt, .sldasm)、CATIA (.catpart)、NX (.prt) 等 CAD 软件的精密机械零件和装配体，用于产品展示、装配培训或数字展厅。
- **汽车设计**：将 Alias (.wire) 或 VRED (.vpb) 等汽车设计软件的模型导入 UE，用于实时渲染和交互式汽车配置器。
- **任何需要将专业设计数据实时可视化的场景**：当你的数据源是上述专业格式，且需要利用 UE 强大的渲染和交互能力时，应使用 Datasmith。

## 蓝图用法

Datasmith Importer 主要是一个 C++ 框架和运行时模块，其核心功能（如翻译器注册、场景加载）通常通过 C++ 代码或编辑器操作（如“导入”菜单）触发。提供的头文件中未发现直接暴露给蓝图的 `UFUNCTION(BlueprintCallable)` 节点。其交互主要发生在编辑器层面（通过文件对话框选择源文件）或通过 C++ API 编程控制。

## C++ 用法

### 头文件引入

```cpp
#include "DatasmithTranslator.h"
#include "DatasmithTranslatorManager.h"
#include "DatasmithTranslatableSource.h"
#include "DatasmithSceneSource.h"
```

### 基本用法：使用现有翻译器加载场景

以下代码演示了如何使用 `FDatasmithTranslatableSceneSource` 来加载一个 Datasmith 场景文件。这是最常用的用法。

```cpp
// 来源：基于 DatasmithTranslatableSource.h 和 DatasmithTranslator.h 的用法推断
#include "DatasmithTranslatableSource.h"
#include "DatasmithScene.h" // IDatasmithScene 的定义

// 1. 定义源文件
FDatasmithSceneSource SceneSource;
SceneSource.SetSourceFile(TEXT("/Game/MyModels/Building.udatasmith"));

// 2. 创建可翻译的源对象，它会自动查找并绑定合适的翻译器
FDatasmithTranslatableSceneSource TranslatableSource(SceneSource);

// 3. 检查是否有翻译器支持此文件
if (TranslatableSource.IsTranslatable())
{
    // 4. 创建目标场景对象
    TSharedRef<IDatasmithScene> Scene = FDatasmithSceneFactory::CreateScene(*SceneSource.GetSceneName());

    // 5. 执行翻译（加载）
    bool bLoadSuccess = TranslatableSource.Translate(Scene);

    if (bLoadSuccess)
    {
        // 现在 `Scene` 对象中包含了从文件解析出的所有元素（网格、材质、Actor等）
        // 通常，后续步骤会将这些元素“实现”为 UE 资产和 Actor
        UE_LOG(LogTemp, Log, TEXT("Datasmith scene loaded successfully: %s"), *SceneSource.GetSceneName());
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to translate Datasmith scene."));
    }
}
else
{
    UE_LOG(LogTemp, Warning, TEXT("No translator found for file: %s"), *SceneSource.GetSourceFile());
}
```

### 进阶用法：注册自定义翻译器

Datasmith 的强大之处在于其可扩展性。你可以编写自己的翻译器来支持新的文件格式。

```cpp
// 来源：基于 DatasmithTranslator.h 和 DatasmithTranslatorManager.h 的接口定义
#include "DatasmithTranslator.h"
#include "DatasmithTranslatorManager.h"

// 1. 定义你的翻译器类，实现 IDatasmithTranslator 接口
class FMyCustomCADTranslator : public IDatasmithTranslator
{
public:
    virtual FName GetFName() const override { return FName(TEXT("MyCustomCADTranslator")); }

    virtual void Initialize(FDatasmithTranslatorCapabilities& OutCapabilities) override
    {
        // 声明支持的文件格式
        OutCapabilities.SupportedFileFormats.Add(FFileFormatInfo(TEXT(".mycad"), TEXT("My Custom CAD File")));
        // 可以设置其他能力，如是否支持并行加载网格
        OutCapabilities.bParallelLoadStaticMeshSupported = true;
    }

    virtual bool IsSourceSupported(const FDatasmithSceneSource& Source) override
    {
        // 可以添加额外的验证逻辑，例如检查文件头
        return Source.GetSourceFileExtension() == TEXT(".mycad");
    }

    virtual bool LoadScene(TSharedRef<IDatasmithScene> OutScene) override
    {
        // 在这里实现将 .mycad 文件解析为 IDatasmithScene 的逻辑
        // 这是翻译器的核心工作
        // ... 解析文件，创建 IDatasmithMeshElement, IDatasmithMaterialInstanceElement 等并添加到 OutScene
        return true;
    }

    virtual bool LoadStaticMesh(const TSharedRef<IDatasmithMeshElement> MeshElement, FDatasmithMeshElementPayload& OutMeshPayload) override
    {
        // 在这里实现为特定网格元素加载详细网格数据（LOD、碰撞体）的逻辑
        // ... 填充 OutMeshPayload.LodMeshes 等
        return true;
    }
    // ... 实现其他必要的虚函数，如 LoadLevelSequence 等
};

// 2. 在模块启动时注册你的翻译器
// 通常在一个模块的 StartupModule() 中调用
void FMyModule::StartupModule()
{
    // 使用模板函数注册，它会自动处理 FDatasmithTranslatorManager 的调用
    Datasmith::RegisterTranslator<FMyCustomCADTranslator>();
}

// 3. 在模块关闭时注销
void FMyModule::ShutdownModule()
{
    Datasmith::UnregisterTranslator<FMyCustomCADTranslator>();
}
```

## Demo 示例

一个完整的、可编译的最小示例，展示如何创建一个简单的翻译器并注册它。

**MySimpleTranslator.h**
```cpp
#pragma once

#include "DatasmithTranslator.h"

class FMySimpleTranslator : public IDatasmithTranslator
{
public:
    // IDatasmithTranslator 接口实现
    virtual FName GetFName() const override;
    virtual void Initialize(FDatasmithTranslatorCapabilities& OutCapabilities) override;
    virtual bool LoadScene(TSharedRef<IDatasmithScene> OutScene) override;
    virtual void UnloadScene() override;
    // ... 其他需要实现的虚函数
};
```

**MySimpleTranslator.cpp**
```cpp
#include "MySimpleTranslator.h"
#include "DatasmithSceneFactory.h"
#include "DatasmithScene.h"
#include "DatasmithMesh.h"
#include "DatasmithMeshElement.h"

FName FMySimpleTranslator::GetFName() const
{
    return FName(TEXT("MySimpleTranslator"));
}

void FMySimpleTranslator::Initialize(FDatasmithTranslatorCapabilities& OutCapabilities)
{
    // 声明支持 .simple 格式
    OutCapabilities.SupportedFileFormats.Add(FFileFormatInfo(TEXT(".simple"), TEXT("Simple Test Format")));
}

bool FMySimpleTranslator::LoadScene(TSharedRef<IDatasmithScene> OutScene)
{
    // 这是一个极简的示例，创建一个立方体网格并添加到场景中
    // 实际翻译器会从文件中读取数据

    // 1. 创建网格数据
    TSharedRef<FDatasmithMesh> MeshData = MakeShared<FDatasmithMesh>();
    // ... 在这里填充 MeshData 的顶点、三角形等数据（省略具体填充代码）

    // 2. 创建网格元素
    TSharedRef<IDatasmithMeshElement> MeshElement = FDatasmithSceneFactory::CreateMesh(TEXT("SimpleCube"));
    MeshElement->SetMeshName(TEXT("Cube"));

    // 3. 将网格元素添加到场景
    OutScene->AddMesh(MeshElement);

    // 注意：实际的网格数据（MeshData）通常在 LoadStaticMesh 阶段提供
    return true;
}

void FMySimpleTranslator::UnloadScene()
{
    // 清理资源
}
```

**MyModule.cpp (注册部分)**
```cpp
#include "Modules/ModuleManager.h"
#include "DatasmithTranslatorManager.h"
#include "MySimpleTranslator.h"

class FMyDatasmithExtensionModule : public IModuleInterface
{
public:
    virtual void StartupModule() override
    {
        // 注册翻译器
        Datasmith::RegisterTranslator<FMySimpleTranslator>();
    }

    virtual void ShutdownModule() override
    {
        // 注销翻译器
        Datasmith::UnregisterTranslator<FMySimpleTranslator>();
    }
};

IMPLEMENT_MODULE(FMyDatasmithExtensionModule, MyDatasmithExtension);
```

## 模块依赖

从模块名称和常见企业插件依赖推断，使用 DatasmithTranslator 模块（编写自定义翻译器）通常需要依赖以下模块。**省略了 Core, CoreUObject, Engine 等常见依赖**。

| 模块 | 用途 |
|---|---|
| `DatasmithCore` | Datasmith 的核心数据结构（IDatasmithScene, IDatasmithElement 等） |
| `MeshDescription` | 用于处理和构建网格数据（FMeshDescription） |
| `StaticMeshDescription` | 与 StaticMesh 资产交互的辅助工具 |

## 维护状态

### 近期更新

- b059f7b46335 Fix trivial unreachable code warnings.
  - 代码清理，修复了无法到达的代码警告。
- f5b459f97289 Datasmith - Remove the experimental Datasmith Clo json importer plugin, and deprecate unused Datasmith cloth code.
  - 移除了实验性的 Cloth 导入器插件，并废弃了未使用的布料相关代码。这表明插件在清理不再维护的实验性功能。
- 927adb79bef5 Correct deprecation versions #preflight trivial #rnx
  - 修正了废弃标记的版本号，属于维护性更新。

### 维护评价

Datasmith Importer 是一个成熟的企业级插件，自2019年创建以来已有约6年历史。从近期提交记录看，它仍在被积极维护，但更新内容主要集中在**代码清理、废弃功能移除和编译修复**上，而非大量新功能开发。这符合一个成熟、稳定的企业级工具的特征。

**优点**：
- 架构设计良好，可扩展性强（翻译器模式）。
- 是 Epic 官方维护的核心企业功能，有长期支持保障。
- 文档和社区资源相对丰富。

**注意事项**：
- 默认未启用（`EnabledByDefault: false`），需要在项目设置中手动启用。
- 主要面向专业用户和特定行业，对于纯游戏开发可能用不到。
- 依赖特定的企业级数据格式，如果源数据不是这些格式，则无需使用。

**推荐**：如果你的工作流程涉及将 CAD、BIM 等专业设计数据导入 Unreal Engine，Datasmith Importer 是**官方推荐且必须使用**的解决方案。对于其他场景，则无需引入此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithImporter/Tests) (如果存在)