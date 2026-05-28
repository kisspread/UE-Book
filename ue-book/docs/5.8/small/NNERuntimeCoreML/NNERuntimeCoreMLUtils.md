# NNERuntimeCoreML

> CoreML backed runtime for the Neural Network Engine (NNE).

| 属性 | 值 |
|---|---|
| 中文名 | CoreML 运行时 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNERuntimeCoreMLEditor` (Editor), `NNERuntimeCoreML` (Runtime), `NNERuntimeCoreMLUtils` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-08 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeCoreML) | |

## 用途

本插件是 Unreal Engine 神经网络引擎 (NNE) 的一个运行时后端实现，它将 CoreML 作为推理引擎进行集成。其主要目的是让 NNE 训练或导入的模型能够在 Apple 平台（如 macOS）上运行，并能够充分利用 Apple 硬件（如 Neural Engine）的加速能力。该插件解决了在 UE 项目中高效部署和运行机器学习模型，尤其是在 Apple 设备上的需求。

## 使用场景

-   你在 macOS 上开发一个使用风格迁移（Style Transfer）功能的游戏或应用。
-   你需要在 macOS 或 iOS 平台上部署一个使用 CoreML 训练的图像识别模型。
-   你希望利用 Apple 芯片的 Neural Engine 来加速游戏内的 AI 推理，例如角色行为决策。

## 蓝图用法

当前模块 `NNERuntimeCoreMLUtils` 主要提供底层文件读写功能，未暴露蓝图可调用的函数（`UFUNCTION(BlueprintCallable)`）或属性（`UPROPERTY(BlueprintReadWrite)`）。更高级的模型加载、推理等蓝图接口由主模块 `NNERuntimeCoreML` 提供。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| *（当前模块无蓝图节点）* | | |

### 使用示例（蓝图描述）

本模块（`NNERuntimeCoreMLUtils`）主要供 C++ 代码内部调用，不直接用于蓝图图表。

## C++ 用法

本模块提供了用于将 CoreML 模型文件（如 `.mlmodel` 或 `.mlpackage`）加载到内存或从内存保存到磁盘的工具函数。

### 头文件引入

```cpp
#include "NNERuntimeCoreMLUtils/Internal/NNERuntimeCoreMLUtils.h"
```

### 基本用法

从 `Internal/NNERuntimeCoreMLUtils.h` 提取的实用函数。

```cpp
// 示例：将一个 CoreML 模型文件加载到内存字节数组中
TArray64<uint8> ModelData;
const FString ModelFilePath = FPaths::ProjectContentDir() / TEXT("ML/MyModel.mlpackage");

if (UE::NNERuntimeCoreML::LoadDirectoryToArray(ModelData, ModelFilePath))
{
    UE_LOG(LogTemp, Log, TEXT("成功加载模型，大小：%lld 字节"), ModelData.Num());
    // 接下来可以将 ModelData 传给 NNE 运行时进行编译或推理
}
else
{
    UE_LOG(LogTemp, Error, TEXT("加载模型失败：%s"), *ModelFilePath);
}

// 示例：将内存中的数据保存为 CoreML 模型文件
TArray64<uint8> SavedModelData = /* ... 从某处获取的数据 ... */;
const TCHAR* OutputPath = TEXT("/Users/username/ExportedModel.mlpackage");

if (UE::NNERuntimeCoreML::SaveArrayToDirectory(SavedModelData, OutputPath))
{
    UE_LOG(LogTemp, Log, TEXT("成功保存模型至：%s"), OutputPath);
}
else
{
    UE_LOG(LogTemp, Error, TEXT("保存模型失败"));
}
```

### 进阶用法

本函数通常与 NNE 的模型加载流程结合使用。以下是集成到模型加载管线的伪代码思路。

```cpp
#include "NNE.h"
#include "NNERuntimeCoreMLUtils/Internal/NNERuntimeCoreMLUtils.h"

// 1. 使用 CoreML 工具模块加载模型文件
TArray64<uint8> ModelFileData;
const FString Path = TEXT("Models/StyleTransfer.mlmodel");
if (!UE::NNERuntimeCoreML::LoadDirectoryToArray(ModelFileData, *Path))
{
    return false;
}

// 2. 通过 NNE 的全局实例创建模型资源
TObjectPtr<UNNEModelData> ModelData = NewObject<UNNEModelData>();
ModelData->SetModelData(MoveTemp(ModelFileData));

// 3. 使用特定的运行时（此处为 CoreML 运时）编译模型
const FString RuntimeName = TEXT("NNERuntimeCoreML"); // 需确保该运行时已加载
TWeakInterfacePtr<INNERuntime> Runtime = UE::NNE::GetRuntime(RuntimeName);
if (!Runtime.IsValid())
{
    UE_LOG(LogTemp, Error, TEXT("找不到运行时：%s"), *RuntimeName);
    return false;
}

TSharedPtr<UE::NNE::IModelInstanceGPU> ModelInstance = Runtime->CreateModelInstanceGPU(ModelData.Get());
if (!ModelInstance.IsValid())
{
    UE_LOG(LogTemp, Error, TEXT("模型实例创建失败"));
    return false;
}

// 4. 此时 ModelInstance 即可用于推理输入数据
```

## Demo 示例

一个最小化的控制台程序示例，演示如何使用该工具模块加载和保存文件。

```cpp
// NNERuntimeCoreMLDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FNNERuntimeCoreMLDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// NNERuntimeCoreMLDemo.cpp
#include "NNERuntimeCoreMLDemo.h"
#include "NNERuntimeCoreMLUtils/Internal/NNERuntimeCoreMLUtils.h"
#include "Misc/FileHelper.h"
#include "HAL/PlatformProcess.h"

void FNNERuntimeCoreMLDemoModule::StartupModule()
{
    // 示例用法
    TArray64<uint8> LoadedData;
    const FString SourcePath = FPaths::ProjectContentDir() / TEXT("TestModel.mlmodel");
    const FString DestPath = FPaths::ProjectSavedDir() / TEXT("CopiedModel.mlmodel");

    if (UE::NNERuntimeCoreML::LoadDirectoryToArray(LoadedData, SourcePath))
    {
        UE_LOG(LogTemp, Display, TEXT("已从 %s 加载 %lld 字节"), *SourcePath, LoadedData.Num());

        if (UE::NNERuntimeCoreML::SaveArrayToDirectory(LoadedData, *DestPath))
        {
            UE_LOG(LogTemp, Display, TEXT("已保存至 %s"), *DestPath);
        }
    }
}

void FNNERuntimeCoreMLDemoModule::ShutdownModule()
{
}

IMPLEMENT_PRIMARY_GAME_MODULE(FNNERuntimeCoreMLDemoModule, NNERuntimeCoreMLDemo, "NNERuntimeCoreMLDemo");
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移至 UE_LOGF，代码维护性更新。 |
| 2026-03-20 | `2724fcee` | [NNERuntimeCoreML] Fix output copy to use logical size from MLMultiArray shape | 修复输出数据拷贝错误，使用 CoreML 数组形状的逻辑尺寸。 |
| 2026-02-09 | `7c2ef798` | [NNE] NNERuntimeCoreML add .mlpackage format support. | 为 CoreML 运行时添加了对 .mlpackage 格式的支持。 |
| 2026-01-28 | `5f766aee` | Fixed modules that does not support portable toolchain | 修复了不支持便携工具链的模块编译问题。 |
| 2026-01-24 | `e793e61e` | Fixed more compile errors when using portable toolchain | 进一步修复便携工具链下的编译错误。 |

### 维护评价

-   **创建时间**: 2025-01-08。
-   **维护活跃度**: **活跃维护**。最近一次实质性功能更新（`.mlpackage` 格式支持）在 2026 年 2 月，且近期（2026 年 4 月）仍有维护性提交（日志宏迁移）。这表明该模块仍在持续开发和维护中。
-   **已知限制**：根据初始提交信息，目前主要支持 CPU 推理，且模型输入/输出仅支持 `float` 类型的 `MultiArray`，功能集将随后续提交扩展。
-   **推荐使用**：✅ **推荐在需要 Apple 平台硬件加速推理的项目中尝试使用**。该模块是 UE 机器学习生态在 Apple 硬件上的重要组成部分，维护活跃，但需注意其处于实验性阶段（`IsExperimentalVersion=true`）且默认未启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeCoreML/Source/NNERuntimeCoreMLUtils)
- [官方文档](https://dev.epicgames.com/community/learning/courses/e7w/unreal-engine-neural-network-engine-nne)（NNE 总体课程）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeCoreML/Tests)