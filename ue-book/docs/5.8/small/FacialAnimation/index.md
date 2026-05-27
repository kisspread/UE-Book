# Facial Animation Bulk Importer

> Bulk importer for facial animation curves and audio. Imports facial animation curve tables (from FBX) into sound waves.

| 属性 | 值 |
|---|---|
| 中文名 | 面部动画批量导入 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `FacialAnimation` (Runtime), `FacialAnimationEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2016-11-15 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/FacialAnimation) | |

## 用途

FacialAnimation 插件主要用于**批量导入和处理面部动画数据**。它解决了动画师需要从外部 DCC 工具（如 Maya）大量导入口型动画 FBX 文件，并将其与音频资源自动关联的需求。插件通过将导入的 FBX 面部动画曲线表（Curve Tables）转换并存储到引擎的 Sound Wave 资源中，为后续的基于音频驱动面部动画（Audio-Driven Facial Animation）工作流奠定了基础。它提供了关键的批量处理能力，避免了繁琐的手动导入和资产创建工作。

## 使用场景

- **动画团队需要为大量对话音频制作口型动画**：当你有成百上千条对话音频及其对应的 FBX 口型动画数据时，使用此插件可以一键批量导入并生成对应的带曲线数据的 Sound Wave 资产。
- **开发基于音频驱动的面部动画系统**：此插件是建立更复杂音画同步系统的数据准备工具，它生成的资产可被自定义的动画蓝图或组件用于实时驱动角色面部。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ImportAssets` | 异步执行批量导入任务，处理指定的 FBX 和音频文件对 | `UAsyncTaskImportFacialAnimation` |
| `OnProgressUpdated` | 导入进度更新的事件，可用于更新 UI 进度条 | `UAsyncTaskImportFacialAnimation` |
| `OnCompleted` | 所有文件导入完成的事件，返回处理后的资源列表 | `UAsyncTaskImportFacialAnimation` |
| `OnFailed` | 导入过程中发生错误时的事件 | `UAsyncTaskImportFacialAnimation` |

### 使用示例（蓝图描述）

1.  创建一个 `UAsyncTaskImportFacialAnimation` 类型的异步任务节点。
2.  将 FBX 文件路径数组和对应的音频文件路径数组分别连接到该节点的输入引脚。
3.  将该节点的 `OnProgressUpdated` 事件引脚连接到一个更新进度条的蓝图逻辑。
4.  将 `OnCompleted` 事件引脚连接到后续处理逻辑，例如将返回的资源数组保存或应用到角色上。
5.  将 `OnFailed` 事件引脚连接到一个显示错误信息的节点。

## C++ 用法

### 头文件引入

```cpp
#include “FacialAnimationImport.h”
```

### 基本用法

监听批量导入任务的完成和进度事件。

```cpp
// 创建异步导入任务
UAsyncTaskImportFacialAnimation* ImportTask = UAsyncTaskImportFacialAnimation::ImportFacialAnimation(
    FBXFilePaths, // TArray<FString>
    AudioFilePaths, // TArray<FString>
    OutputPath // FString, 输出路径
);

// 绑定完成事件
ImportTask->OnCompleted.AddDynamic(this, &UMyClass::HandleImportCompleted);

// 绑定进度事件
ImportTask->OnProgressUpdated.AddDynamic(this, &UMyClass::HandleImportProgress);

// 绑定失败事件
ImportTask->OnFailed.AddDynamic(this, &UMyClass::HandleImportFailed);

// 启动任务 (通常已自动启动，此处为示意)
// ImportTask->Activate();
```

### 进阶用法

在导入完成后，直接访问生成的资源并进行后续操作。

```cpp
void UMyClass::HandleImportCompleted(const TArray<UObject*>& ImportedAssets)
{
    for (UObject* Asset : ImportedAssets)
    {
        if (USoundWave* SoundWave = Cast<USoundWave>(Asset))
        {
            // SoundWave 现在包含了导入的面部动画曲线数据
            // 可以将其用于音频组件或直接应用到动画蓝图中
            // 例如：AudioComponent->SetSound(SoundWave);
            UE_LOG(LogTemp, Log, TEXT(“Successfully imported SoundWave with facial data: %s”), *SoundWave->GetName());
        }
    }
}
```

*（代码示例基于对插件功能及 UAsyncTaskImportFacialAnimation 类的通用设计推断）*

## Demo 示例

一个最小的监听导入进度的 Actor 示例。

```cpp
// MyImporterActor.h
#pragma once
#include “CoreMinimal.h”
#include “GameFramework/Actor.h”
#include “FacialAnimationImport.h”
#include “MyImporterActor.generated.h”

UCLASS()
class AMyImporterActor : public AActor
{
    GENERATED_BODY()
public:
    AMyImporterActor();

    UFUNCTION(BlueprintCallable, Category = “Facial Animation”)
    void StartBatchImport(const TArray<FString>& FBXFiles, const TArray<FString>& AudioFiles, const FString& OutputDir);

protected:
    UFUNCTION()
    void OnImportCompleted(const TArray<UObject*>& ImportedAssets);

    UFUNCTION()
    void OnImportFailed(const FString& ErrorMessage);

private:
    UPROPERTY()
    UAsyncTaskImportFacialAnimation* CurrentTask = nullptr;
};
```

```cpp
// MyImporterActor.cpp
#include “MyImporterActor.h”

AMyImporterActor::AMyImporterActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyImporterActor::StartBatchImport(const TArray<FString>& FBXFiles, const TArray<FString>& AudioFiles, const FString& OutputDir)
{
    if (CurrentTask)
    {
        CurrentTask->OnCompleted.RemoveDynamic(this, &AMyImporterActor::OnImportCompleted);
        CurrentTask->OnFailed.RemoveDynamic(this, &AMyImporterActor::OnImportFailed);
        // Cancel previous task if possible
    }

    CurrentTask = UAsyncTaskImportFacialAnimation::ImportFacialAnimation(FBXFiles, AudioFiles, OutputDir);
    if (CurrentTask)
    {
        CurrentTask->OnCompleted.AddDynamic(this, &AMyImporterActor::OnImportCompleted);
        CurrentTask->OnFailed.AddDynamic(this, &AMyImporterActor::OnImportFailed);
    }
}

void AMyImporterActor::OnImportCompleted(const TArray<UObject*>& ImportedAssets)
{
    UE_LOG(LogTemp, Warning, TEXT(“Batch import finished! Imported %d assets.”), ImportedAssets.Num());
    CurrentTask = nullptr;
}

void AMyImporterActor::OnImportFailed(const FString& ErrorMessage)
{
    UE_LOG(LogTemp, Error, TEXT(“Batch import failed: %s”), *ErrorMessage);
    CurrentTask = nullptr;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `FacialAnimation` | 提供核心运行时功能和异步导入任务 (`UAsyncTaskImportFacialAnimation`) |
| `FacialAnimationEditor` | 提供编辑器集成和 UI 操作支持 |

*注：该插件的两个模块均依赖于标准的 Core, CoreUObject, Engine 等模块，未列出特殊依赖。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-07-10 | `abb369e2` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 为源码文件添加宏以改善编译性能。 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i | 修改构建配置以确保符号正确导出。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件目录的一次批量更新。 |
| 2022-11-03 | `fa90b399` | Added includes for future change. This changelist only contains added #include and a couple of empty | 为未来改动预先添加头文件包含。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新插件内置链接使用 HTTPS 安全协议。 |

### 维护评价

- **年龄**: 创建于 2016 年，是一个拥有 8 年历史的插件。
- **更新频率**: 近 3 年内有提交，但主要是**编译修复、代码规范化（添加宏、include 整理）和构建系统调整**，没有任何面向用户的功能更新或 Bug 修复。
- **活跃度**: **维护不活跃**。核心功能代码自 2016 年创建后似乎未再修改。
- **状态**: .uplugin 中标记为 `IsBetaVersion: true`，表明它从未正式脱离“实验性”状态。
- **推荐**: **谨慎使用**。虽然插件默认启用，但作为长期未更新且仍为“实验性”的工具，其稳定性和对未来引擎版本的兼容性存在风险。仅建议在需要批量处理旧版面部动画数据时作为一次性工具使用，不推荐将其深度集成到新的核心工作流中。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/FacialAnimation)
- 官方文档：无
- 测试用例：无