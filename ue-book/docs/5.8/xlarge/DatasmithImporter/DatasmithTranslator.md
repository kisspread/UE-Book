# Datasmith Translator

> Importer for Datasmith files.

| 属性 | 值 |
|---|---|
| 中文名 | Datasmith翻译器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithTranslator` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter) | |

## 用途

`DatasmithTranslator` 模块并非一个可直接用于资产导入的独立插件，而是构成整个 Datasmith 导入系统**核心架构层**的模块。它定义了一套标准化的接口（`IDatasmithTranslator`）和管理器（`FDatasmithTranslatorManager`），用于将各种第三方 CAD、BIM 和 DCC 软件（如 Revit、SketchUp、3ds Max、Cinema 4D 等）的专有文件格式“翻译”为 Unreal Engine 能够理解的通用 Datasmith 场景数据（`IDatasmithScene`）。

它的存在是为了实现**解耦**。不同的文件格式（如 `.udatasmith`, `.skp`, `.max`）由独立的、遵循此接口的“翻译器”（Translator）实现来处理。`DatasmithTranslator` 模块负责管理这些翻译器的注册、发现和生命周期，并为它们提供统一的辅助工具（如 `DatasmithMeshHelper` 用于处理网格数据），从而使得新增一种导入格式变得标准化和模块化。

## 使用场景

- 你是一个 BIM 软件（如 ArchiCAD、Bentley）的开发者或用户，希望将该软件的原生模型导入到 Unreal Engine 中 → 你需要为你的软件**实现一个 `IDatasmithTranslator` 接口**，并使用 `Datasmith::RegisterTranslator` 将其注册到此系统。
- 你正在开发一个 UE5 插件，需要支持导入某种自定义的 3D 数据格式 → 可以基于此模块提供的框架，快速构建一个翻译器，专注于解析格式和生成 `IDatasmithScene`，而无需关心 UE 资产创建的底层细节。
- 你在使用标准的 Datasmith 导入流程时，理解该模块有助于你调试特定格式的导入问题，因为问题可能出在对应的 Translator 实现中。

## 蓝图用法

`DatasmithTranslator` 模块的核心接口和类（如 `IDatasmithTranslator`, `FDatasmithTranslatorManager`）**没有暴露任何蓝图可调用的函数（BlueprintCallable）**。它是一个纯粹的 C++ 运行时模块，主要为其他模块（如 `DatasmithImporter`）和自定义的 Translator 实现提供底层支持。

在标准的 Datasmith 导入工作流中，用户通过“导入”对话框选择文件，系统在后台通过 `FDatasmithTranslatorManager::SelectFirstCompatible` 自动选择并使用合适的 Translator，这个过程对蓝图不可见。

## C++ 用法

### 头文件引入

```cpp
#include “DatasmithTranslator.h”
```

### 基本用法：实现并注册一个自定义翻译器

要支持一种新的文件格式，你需要从 `IDatasmithTranslator` 派生一个类，并实现其关键虚函数。下面的示例基于 `IDatasmithTranslator` 的接口定义。

**1. 定义翻译器类（Sprocket格式为例）**

```cpp
// SprocketTranslator.h
#pragma once

#include “DatasmithTranslator.h”

class FSprocketTranslator : public IDatasmithTranslator
{
public:
    // 获取翻译器唯一名称
    virtual FName GetFName() const override { return TEXT(“SprocketTranslator”); }

    // 声明支持的文件格式和能力
    virtual void Initialize(FDatasmithTranslatorCapabilities& OutCapabilities) override
    {
        OutCapabilities.SupportedFileFormats.Add(FFileFormatInfo(TEXT(“.sprocket”), TEXT(“Sprocket 3D File”)));
        OutCapabilities.bParallelLoadStaticMeshSupported = true; // 支持并行加载网格
    }

    // 可选：对源文件进行额外校验
    virtual bool IsSourceSupported(const FDatasmithSceneSource& Source) override
    {
        // 可以检查文件头等
        return true;
    }

    // 核心：将源文件加载为 Datasmith 场景
    virtual bool LoadScene(TSharedRef<IDatasmithScene> OutScene) override
    {
        // 1. 使用 GetSource() 获取文件路径
        const FString& FilePath = GetSource().GetSourceFile();

        // 2. 解析 .sprocket 文件，填充 OutScene 中的网格、材质、变换等元素
        // ... 省略具体的解析逻辑 ...

        return true; // 解析成功
    }

    // 当需要网格的详细数据时被调用（延迟加载）
    virtual bool LoadStaticMesh(const TSharedRef<IDatasmithMeshElement> MeshElement, FDatasmithMeshElementPayload& OutMeshPayload) override
    {
        // 根据 MeshElement 中的信息（如原始文件中的ID），加载网格的 LOD、碰撞数据等
        // ... 省略 ...

        return true;
    }

    // 场景加载完成后的清理工作
    virtual void UnloadScene() override
    {
        // 释放解析过程中申请的资源
    }
};
```

**2. 注册翻译器**

在你的模块启动时，通常是在 `IModuleInterface::StartupModule` 中，调用注册函数。

```cpp
// SprocketTranslatorModule.cpp
#include “SprocketTranslator.h”
#include “DatasmithTranslator.h” // 包含注册函数所在的命名空间

void FSprocketTranslatorModule::StartupModule()
{
    // 使用模板函数进行类型安全的注册
    Datasmith::RegisterTranslator<FSprocketTranslator>();
}

void FSprocketTranslatorModule::ShutdownModule()
{
    // 在模块卸载时反注册
    Datasmith::UnregisterTranslator<FSprocketTranslator>();
}
```

### 进阶用法：使用网格辅助工具

`DatasmithMeshHelper` 命名空间提供了大量实用函数，用于在翻译器内部处理和验证网格数据。

```cpp
#include “Utility/DatasmithMeshHelper.h”

// 在 LoadScene 或 LoadStaticMesh 内部
virtual bool LoadStaticMesh(const TSharedRef<IDatasmithMeshElement> MeshElement, FDatasmithMeshElementPayload& OutMeshPayload) override
{
    // 假设我们已经从文件解析得到了一个 FMeshDescription MeshDesc

    // 1. 准备网格属性，使其兼容 StaticMesh
    DatasmithMeshHelper::PrepareAttributeForStaticMesh(MeshDesc);

    // 2. 检查网格是否有效（至少有一个非退化三角形）
    if (!DatasmithMeshHelper::IsMeshValid(MeshDesc))
    {
        UE_LOG(LogTemp, Warning, TEXT(“Loaded mesh for %s is degenerate.”), *MeshElement->GetName());
        return false;
    }

    // 3. 如果没有 UV，可以生成默认的
    if (!DatasmithMeshHelper::HasUVData(MeshDesc, 0))
    {
        DatasmithMeshHelper::CreateDefaultUVs(MeshDesc);
    }

    // 4. 将处理好的 MeshDescription 添加到 Payload 的 LOD 列表
    OutMeshPayload.LodMeshes.Add(MoveTemp(MeshDesc));

    return true;
}
```

## Demo 示例

一个最小化的、支持 `.sprocket` 纯文本格式（内容仅为顶点数）的翻译器实现。

**SprocketTranslator.h**
```cpp
#pragma once
#include “DatasmithTranslator.h”

class FSprocketTranslator : public IDatasmithTranslator
{
public:
    virtual FName GetFName() const override;
    virtual void Initialize(FDatasmithTranslatorCapabilities& OutCapabilities) override;
    virtual bool LoadScene(TSharedRef<IDatasmithScene> OutScene) override;
    virtual void UnloadScene() override;

private:
    // 存储解析的网格数据
    TSharedPtr<FMeshDescription> ParsedMesh;
};
```

**SprocketTranslator.cpp**
```cpp
#include “SprocketTranslator.h”
#include “Utility/DatasmithMeshHelper.h”
#include “Misc/FileHelper.h”
#include “DatasmithScene.h”

FName FSprocketTranslator::GetFName() const
{
    return TEXT(“SimpleSprocketTranslator”);
}

void FSprocketTranslator::Initialize(FDatasmithTranslatorCapabilities& OutCapabilities)
{
    OutCapabilities.SupportedFileFormats.Add(FFileFormatInfo(TEXT(“.sprocket”), TEXT(“Simple Sprocket File”)));
    OutCapabilities.bParallelLoadStaticMeshSupported = false;
}

bool FSprocketTranslator::LoadScene(TSharedRef<IDatasmithScene> OutScene)
{
    const FString FilePath = GetSource().GetSourceFile();
    FString FileContent;
    if (!FFileHelper::LoadFileToString(FileContent, *FilePath))
    {
        return false;
    }

    // 简单解析：文件第一行是顶点数
    int32 VertexCount = FCString::Atoi(*FileContent.TrimEnd());
    if (VertexCount <= 0)
    {
        return false;
    }

    // 创建一个包含 VertexCount 个点的简单网格（实际应用会解析顶点数据）
    ParsedMesh = MakeShared<FMeshDescription>();
    DatasmithMeshHelper::PrepareAttributeForStaticMesh(*ParsedMesh);

    // 添加顶点（示例：创建一条线段）
    for (int32 i = 0; i < VertexCount; ++i)
    {
        ParsedMesh->CreateVertex(FVector3f(i * 100.f, 0, 0));
    }

    // 创建一个三角形（如果有足够顶点）
    if (VertexCount >= 3)
    {
        FPolygonGroupID PolygonGroupID = ParsedMesh->CreatePolygonGroup();
        FVertexInstanceID Inst0 = ParsedMesh->CreateVertexInstance(FVertexID(0));
        FVertexInstanceID Inst1 = ParsedMesh->CreateVertexInstance(FVertexID(1));
        FVertexInstanceID Inst2 = ParsedMesh->CreateVertexInstance(FVertexID(2));
        ParsedMesh->CreateTriangle(PolygonGroupID, {Inst0, Inst1, Inst2});
    }

    // 创建一个网格元素并添加到场景
    TSharedPtr<IDatasmithMeshElement> MeshElement = FDatasmithSceneFactory::CreateMesh(TEXT(“SprocketMesh”));
    OutScene->AddMesh(MeshElement);

    // 需要立即加载网格数据（因为我们的 Translator 不支持延迟加载）
    // 这部分通常由 DatasmithImporter 模块调用 Translator->LoadStaticMesh，这里简化处理
    return true;
}

void FSprocketTranslator::UnloadScene()
{
    ParsedMesh.Reset();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RenderCore` | 提供 `FMeshDescription` 等核心渲染数据结构 |
| `MeshDescription` | 提供 `FMeshDescription` 的具体操作和编辑功能 |
| `DatasmithContent` | 提供 `IDatasmithScene`, `IDatasmithMeshElement` 等核心数据接口定义 |
| `MeshConversion` | 可能在 `DatasmithMeshHelper` 内部用于网格格式转换 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下双精度常量截断为浮点数产生的警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 `UE_LOG` 宏迁移至新的 `UE_LOGF` 宏。 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introduced new overloads. | 废弃了接受 `bIncludeNestedObjects` 布尔参数的 `GetObjects*` 和 `ForEachObjectWithOuter` 函数，引入了新的重载版本。 |
| 2026-03-06 | `7b69892a` | clean up code changing texture properties with wrapping in PreEditChange/PostEditChange as required. | 清理了修改纹理属性的代码，按要求用 `PreEditChange/PostEditChange` 进行包装。 |
| 2026-03-05 | `1adb9f68` | New material translator work: | 新材质翻译器工作： |

### 维护评价

- **活跃维护**：近期（2026年）有多次提交，内容涉及代码质量改进（修复警告、迁移新宏）、API 废弃与更新，以及功能开发（新材质翻译器）。这表明 Epic Games 仍在持续维护和演进此核心企业级功能模块。
- **长期存在**：该模块自 2019 年创建，已稳定运行约 6 年，是 Unreal Engine 企业版（现集成在标准版中）的核心组件，不太可能被废弃。
- **推荐使用**：如果你需要为新的 CAD 格式开发导入器，使用 `DatasmithTranslator` 模块提供的框架是**官方推荐且最标准**的方式，它能确保你的实现与引擎的其他部分（如资产管线、编辑器UI）无缝集成。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)