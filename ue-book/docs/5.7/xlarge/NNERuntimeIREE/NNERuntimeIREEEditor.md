# NNERuntimeIREE

> A runtime implementing the Neural Network Engine (NNE) API which is based on IREE, MLIR and LLVM and compiles neural networks directly to game code.

| 属性 | 值 |
|---|---|
| 中文名 | NNE IREE 运行时编辑器模块 |
| 分类 | ML |
| 默认启用 | ❌ 否（实验性插件） |
| 包含内容 | ❌ 无 |
| 模块 | `NNERuntimeIREEEditor` (Editor), `NNERuntimeIREE` (Runtime), `IREEDriverRDG` (Runtime), `IREEUtils` (Runtime), `NNERuntimeIREEShader` (Runtime), `IREE` (External), `NNEMlirTools` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-12 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeIREE) | |

## 用途

`NNERuntimeIREEEditor` 是 `NNERuntimeIREE` 插件的编辑器子模块，为 Unreal Editor 提供神经网络模型（如 ONNX）的导入支持。它通过注册一个 `UFactory`（`UNNERuntimeIREEModelDataFactory`），使得用户可以在内容浏览器中直接导入 `.onnx` 或其他支持的模型格式（取决于底层实现），将其转换为可在运行时使用的 UE 资源。

没有此模块，开发者需要手动处理模型文件或通过代码加载 IREE 编译产物，无法享受便捷的编辑器工作流。

## 使用场景

- 你正在使用 `NNERuntimeIREE` 在游戏中运行推理，需要在编辑器内将训练好的神经网络模型（如 ONNX 导出）导入项目。
- 你希望通过标准的“导入”操作（右键内容浏览器 → 导入资产）将模型文件纳入 UE 资产体系，并自动触发 IREE 的编译流水线（通过 `NNERuntimeIREE` 的其他模块完成）。
- 你需要在编辑器环境下对模型进行测试、预览或转储调试信息。

## 蓝图用法

该模块**没有**公开任何蓝图可调用函数或属性。所有功能均作为编辑器基础设施存在，因此以下表格为空。

| 节点 | 说明 | 所在类 |
|---|---|---|
| （无） | 该模块不提供蓝图 API | - |

### 使用示例（蓝图描述）

无。编辑器工厂的调用是隐式的：当用户执行“导入”操作并选择匹配的文件类型时，Unreal Editor 自动调用 `UNNERuntimeIREEModelDataFactory`。

## C++ 用法

如需在 C++ 中模拟导入过程（自动化脚本或批量处理），可以通过 `FReimportManager`、`UAssetTools` 或直接构造工厂实例来完成。

### 头文件引入

```cpp
#include "NNERuntimeIREEModelDataFactory.h"
```

### 基本用法

以下示例演示如何通过工厂直接创建一个模型资源，绕过编辑器 UI。此用法常见于自动构建工具或测试中。

```cpp
// 来源：Engine/Plugins/Experimental/NNERuntimeIREE/Source/NNERuntimeIREEEditor/Private/NNERuntimeIREEModelDataFactory.cpp
// （基于源码逻辑抽象）

bool ImportModel(const FString& InFilePath, const FString& InPackagePath)
{
    // 1. 创建工厂实例
    UNNERuntimeIREEModelDataFactory* Factory = NewObject<UNNERuntimeIREEModelDataFactory>();
    if (!Factory->FactoryCanImport(InFilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("File format not supported: %s"), *InFilePath);
        return false;
    }

    // 2. 准备导入参数
    TArray<uint8> FileData;
    if (!FFileHelper::LoadFileToArray(FileData, *InFilePath))
    {
        return false;
    }

    // 3. 调用 FactoryCreateBinary 创建资产
    UPackage* Package = CreatePackage(*(InPackagePath + TEXT("/ImportedModel")));
    UObject* NewAsset = Factory->FactoryCreateBinary(
        UNNEModelData::StaticClass(),
        Package,
        FName(TEXT("ImportedModel")),
        RF_Standalone | RF_Public,
        nullptr,                 // Context
        TEXT("onnx"),            // Type extension
        FileData.GetData(),
        FileData.GetData() + FileData.Num(),
        GWarn
    );

    if (NewAsset)
    {
        FAssetRegistryModule::AssetCreated(NewAsset);
        Package->MarkPackageDirty();
        return true;
    }
    return false;
}
```

### 进阶用法

如果需要更紧密地与 IREE 编译流程集成（例如在导入后自动触发编译），可以通过 `INNERuntimeIREE` 接口获取编译句柄，但该操作通常由 `NNERuntimeIREE` 运行时模块在资产加载时延迟完成。编辑器模块本身专注于资产创建。

## Demo 示例

以下是一个可编译的最小 C++ 示例，在编辑器模块启动时自动导入一个预置的 ONNX 模型（假设文件 `Model.onnx` 存放在 `Content/Models/` 下）。此代码应放在 `FNNERuntimeIREEEditorModule::StartupModule()` 中测试。

**MyModelImporter.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyModelImporterModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
};
```

**MyModelImporter.cpp**
```cpp
#include "MyModelImporter.h"
#include "NNERuntimeIREEModelDataFactory.h"
#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "AssetRegistry/AssetRegistryModule.h"

IMPLEMENT_MODULE(FMyModelImporterModule, MyModelImporter);

void FMyModelImporterModule::StartupModule()
{
    // 注意：此示例仅在编辑器下有效，且需要先启用 NNERuntimeIREE 插件
    if (!GIsEditor) return;

    FString ModelPath = FPaths::ProjectContentDir() / TEXT("Models/Model.onnx");
    if (!IFileManager::Get().FileExists(*ModelPath))
    {
        UE_LOG(LogTemp, Warning, TEXT("Model file not found: %s"), *ModelPath);
        return;
    }

    UNNERuntimeIREEModelDataFactory* Factory = NewObject<UNNERuntimeIREEModelDataFactory>();
    if (!Factory->FactoryCanImport(ModelPath))
    {
        UE_LOG(LogTemp, Error, TEXT("Cannot import file type."));
        return;
    }

    TArray<uint8> FileData;
    if (!FFileHelper::LoadFileToArray(FileData, *ModelPath))
    {
        return;
    }

    UPackage* Package = CreatePackage(*(FPaths::ProjectContentDir() + TEXT("/Models/ImportedModel")));
    UObject* NewAsset = Factory->FactoryCreateBinary(
        UNNEModelData::StaticClass(),
        Package,
        FName(TEXT("ImportedModel")),
        RF_Public | RF_Standalone,
        nullptr,
        TEXT("onnx"),
        FileData.GetData(),
        FileData.GetData() + FileData.Num(),
        GWarn
    );

    if (NewAsset)
    {
        FAssetRegistryModule::AssetCreated(NewAsset);
        Package->MarkPackageDirty();
        UE_LOG(LogTemp, Log, TEXT("Model imported successfully: %s"), *NewAsset->GetName());
    }
}
```

**注意**：此示例依赖 `UNNEModelData` 类，它属于 `NNERuntimeIREE` 运行时模块。请确保该模块已在项目插件中启用。

## 模块依赖

引用 `NNERuntimeIREEEditor` 模块时，你的模块需要链接以下依赖（常见编辑器模块 `UnrealEd` 等未列出）：

| 模块 | 用途 |
|---|---|
| `NNERuntimeIREE` | 核心运行时模块，提供 `UNNEModelData` 等模型资产定义 |
| `IREEUtils` | IREE 工具函数及句柄管理 |
| `IREEDriverRDG` | RDG 驱动的 IREE 编译器（用于编译模型） |
| `IREE`（第三方） | 底层 IREE 库（C API 封装） |

**注意**：如果你仅使用编辑器工厂功能，可能只需运行时模块的资产定义头文件。但建议直接依赖 `NNERuntimeIREE` 以保证兼容。

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 编辑器核心（工厂基类、资产工具） |
| `AssetRegistry` | 资产注册表通知 |
| `CoreUObject` | UObject 系统 |

（标准依赖已省略）

## 维护状态

### 近期更新

- 2025-09-26 — 修复 Mac 上路径包含空格时 RelTest 构建的 RDG 支持问题
- 2025-09-24 — [NNE] NNERuntimeIREERdg 始终优先使用 wave32 以与 IREE GPU profile 一致
- 2025-09-24 — [NNE] NNERuntimeIREE 修复 Linux 构建脚本中的拼写错误
- 2025-09-24 — [NNE] NNERuntime IREE 支持 Mac 上路径包含空格的 RelTest 构建
- 2025-09-12 — [NNE] NNERuntimeIREE 修复 onnx importer 依赖在 Engine 安装构建中未 staged 的问题

### 维护评价

该插件创建于 2025 年 9 月，至今约 7 个月，属于全新实验性插件。开发团队（Epic Games）在创建后的几周内持续进行修复和优化，更新频繁，涉及多个平台（Mac, Linux, Win64）和构建配置（RelTest, Engine 安装构建）。但近期（自 9 月下旬起）缺乏新功能提交，可能处于稳定期或优先级调整。整体上，插件 `NNERuntimeIREE` 及其编辑器模块 `NNERuntimeIREEEditor` 目前是**活跃维护**状态，但因为是实验特性，API 和功能可能在未来版本中发生较大变化。推荐在非生产项目中使用，并密切关注后续更新。

## 相关链接

- [源码（NNERuntimeIREE 根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeIREE)
- [编辑器模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeIREE/Source/NNERuntimeIREEEditor)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/neural-network-engine-in-unreal-engine)（NNE 官方文档，包含 IREE 后端概览）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeIREE/Source/NNERuntimeIREEEditor/Tests)（如有）