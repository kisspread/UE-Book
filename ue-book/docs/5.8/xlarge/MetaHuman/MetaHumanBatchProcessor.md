# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源、预设配置） |
| 模块 | `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanPipeline` (Runtime) 等 |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

**MetaHuman Animator** 是 Epic Games 官方提供的 MetaHuman 工具包，其核心功能是将音频（语音）驱动转换为高保真的面部动画，从而为 MetaHuman 角色赋予逼真的口型同步和面部表情。它解决了从音频源到最终可用动画资产（如动画序列或关卡序列）的自动化、批量化处理流程，极大地提升了动画制作效率。

## 使用场景

- **影视与动画制作**：配音演员录制了大量对话音频，需要快速生成对应的面部动画。
- **游戏开发**：游戏项目中存在成百上千条角色对话音频，需要批量转换为驱动 MetaHuman 面部动画的数据。
- **实时虚拟人**：在直播或会议场景中，需要将麦克风实时输入的音频转换为虚拟人的面部动画。

## 蓝图用法

该插件通过一系列蓝图类型和结构体暴露核心功能，便于在编辑器中或通过蓝图脚本进行配置和调用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FMetaHumanSpeechProcessingSettings` | 语音处理配置，包含眨眼生成、音频混合、输出部位等选项。 | `USTRUCT` |
| `FExportAnimSequenceSettings` | 导出动画序列的配置，包含目标骨架、插值方式等。 | `USTRUCT` |
| `FExportLevelSequenceSettings` | 导出关卡序列的配置，包含目标MetaHuman类、是否导出音频/相机等。 | `USTRUCT` |
| `UMetaHumanSpeechToPerformance` | 将语音转换为 MetaHuman Performance 的完整配置对象。 | `UObject` |
| `UMetaHumanExportAnimSequenceSettings` | 导出动画序列的配置对象。 | `UObject` |
| `UMetaHumanExportLevelSequenceSettings` | 导出关卡序列的配置对象。 | `UObject` |

### 使用示例（蓝图描述）

在编辑器内容浏览器中，可以右键创建 `MetaHumanSpeechToPerformance` 类型的资产。打开该资产后，在细节面板中可详细配置“处理设置”（如是否生成眨眼、处理哪些面部部位）和“导出设置”（如目标骨架、是否覆盖现有资产）。配置完成后，通常结合编辑器工具或批处理工具来执行实际的语音到动画的转换流程。

## C++ 用法

在 C++ 层面，主要通过 `UMetaHumanBatchOperation` 类来驱动批量处理流程。

### 头文件引入

```cpp
#include "MetaHumanBatchOperation.h"
```

### 基本用法

创建一个批处理操作，并基于音频资产数组运行。

```cpp
// 来源：MetaHumanBatchOperation.h 的使用推断
#include "MetaHumanBatchOperation.h"
#include "Sound/SoundWave.h"

void RunBatchSpeechToAnimation()
{
    // 1. 准备输入音频资产
    TArray<TWeakObjectPtr<UObject>> AudioAssets;
    // ... 从资产注册表或数组填充 AudioAssets，例如加载一批 USoundWave

    // 2. 创建并配置批处理上下文
    FMetaHumanBatchOperationContext Context;
    Context.AssetsToProcess = AudioAssets;
    Context.BatchStepsFlags = EBatchOperationStepsFlags::SoundWaveToPerformance
                            | EBatchOperationStepsFlags::ProcessPerformance
                            | EBatchOperationStepsFlags::ExportAnimSequence;
    Context.bGenerateBlinks = true;
    Context.bMixAudioChannels = true;
    // ... 配置其他导出选项，如 TargetSkeletonOrSkeletalMesh

    // 3. 创建批处理操作对象并执行
    UMetaHumanBatchOperation* BatchOp = NewObject<UMetaHumanBatchOperation>();
    BatchOp->RunProcess(Context);
}
```

### 进阶用法

结合编辑器UI和自定义处理步骤进行更精细的控制。例如，在编辑器工具中先弹出配置对话框，再执行批处理。

```cpp
// 来源：对 MetaHumanBatchProcessor 模块结构的分析
#include "MetaHumanBatchOperation.h"
#include "SMetaHumanSpeechProcessingSettings.h" // 用于显示设置UI
#include "EditorAnimUtils.h"

void AdvancedBatchProcessWithUI()
{
    // 1. 显示设置对话框（编辑器环境下）
    TSharedRef<SMetaHumanSpeechToAnimProcessingSettings> SettingsDialog =
        SNew(SMetaHumanSpeechToAnimProcessingSettings);
    if (SettingsDialog->ShowModal() == EAppReturnType::Cancel)
        return;

    // 2. 从设置对象中获取配置并构建上下文
    UObject* SettingsObject = SettingsDialog->SettingsObject; // 假设为 UMetaHumanSpeechToAnimSequenceProcessingSettings
    FMetaHumanBatchOperationContext Context;
    // ... 从 SettingsObject 中读取 ProcessingSettings 和 ExportSettings 填充 Context

    // 3. 可能还需要处理文件命名规则（由 SMetaHumanBatchExportPathDialog 配置）
    EditorAnimUtils::FNameDuplicationRule NameRule;
    // ... 配置 NameRule

    Context.PerformanceNameRule = NameRule;
    Context.bOverrideAssets = false;

    // 4. 执行批处理
    UMetaHumanBatchOperation* BatchOp = NewObject<UMetaHumanBatchOperation>();
    BatchOp->RunProcess(Context);
}
```

## Demo 示例

以下是一个最小化的示例，演示如何在C++中配置并触发一次基于指定音频资产的批处理操作。

**SpeechBatchProcessor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MetaHumanBatchOperation.h"
#include "SpeechBatchProcessor.generated.h"

class USoundWave;

UCLASS(Blueprintable)
class USpeechBatchProcessor : public UObject
{
    GENERATED_BODY()

public:
    // 蓝图可调用的函数，输入一个音频数组进行批处理
    UFUNCTION(BlueprintCallable, Category = "MetaHuman Batch")
    void ProcessAudioArray(const TArray<USoundWave*>& InSoundWaves);
};
```

**SpeechBatchProcessor.cpp**
```cpp
#include "SpeechBatchProcessor.h"
#include "MetaHumanBatchOperation.h"

void USpeechBatchProcessor::ProcessAudioArray(const TArray<USoundWave*>& InSoundWaves)
{
    if (InSoundWaves.Num() == 0)
    {
        UE_LOG(LogTemp, Warning, TEXT("No sound waves provided for batch processing."));
        return;
    }

    // 构造弱指针数组
    TArray<TWeakObjectPtr<UObject>> Assets;
    for (USoundWave* Wave : InSoundWaves)
    {
        Assets.Add(Wave);
    }

    // 配置批处理上下文
    FMetaHumanBatchOperationContext Context;
    Context.AssetsToProcess = Assets;
    Context.BatchStepsFlags = EBatchOperationStepsFlags::SoundWaveToPerformance | EBatchOperationStepsFlags::ProcessPerformance;
    Context.bGenerateBlinks = true;
    Context.bEnableHeadMovement = true;

    // 创建并运行批处理操作
    UMetaHumanBatchOperation* BatchOp = NewObject<UMetaHumanBatchOperation>();
    BatchOp->RunProcess(Context);
}
```

## 模块依赖

要使用 `MetaHumanBatchProcessor` 模块，你的项目需要添加对以下独特模块的依赖（在 `Build.cs` 中）：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | 提供 MetaHuman 核心技术库的功能支持。 |

*注：依赖列表基于 `MetaHumanBatchProcessor.build.cs` 的直接依赖。在实际项目中，可能还需要间接依赖其他 MetaHuman 模块。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时，禁用关卡序列导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MHA] 支持为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

**活跃维护**。该模块最近（2026年5月）有多次提交，内容涵盖新功能（如为现有网格导出动画）、Bug修复（渲染瑕疵、Sequencer缓存）和功能调整（身体追踪与关卡序列的兼容性）。这表明该模块正在积极开发和维护中，与 Epic 主推的 MetaHuman 技术栈保持同步。推荐在需要批处理音频到动画流程的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档]() （暂无）
- [测试用例]() （暂未提供）