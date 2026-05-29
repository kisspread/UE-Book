# Sound Cue Templates

> Collection of SoundCue Templates, which provide rapid design of common audio design workflows.

| 属性 | 值 |
|---|---|
| 中文名 | 声音提示模板 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产类型模板，蓝图类模板） |
| 模块 | `SoundCueTemplates` (Runtime), `SoundCueTemplatesEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-07-19 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SoundCueTemplates) | |

## 用途

该插件提供了一系列预制的 SoundCue 蓝图类模板，旨在加速常见音频设计工作流的创建。它解决了音频设计师在创建重复性声音效果（如随机播放、循环、淡入淡出、衰减混合等）时，需要从零开始手动搭建复杂节点网络的问题。通过预置模板，设计师可以快速生成基础 SoundCue 结构，然后进行微调，从而大幅提高工作效率。

## 使用场景

- 你需要为游戏中的环境音（如风声、雨声、人群嘈杂声）快速创建一个具有随机音调和音量变化的 SoundCue。
- 你需要为 UI 按钮点击、菜单切换等反馈音创建一个包含随机选择、淡入淡出和音量标准化的 SoundCue。
- 你的音频设计团队希望在项目中标准化某些常用声音效果（如爆炸、枪声）的创建流程，确保一致性。
- 你希望为新加入项目的音频设计师提供一个易于上手的起点，减少学习复杂 SoundCue 节点的时间。

## 蓝图用法

此插件主要通过编辑器扩展提供模板资产创建功能，其蓝图节点主要在创建资产时的配置对话框中使用，而非在运行时蓝图图表中直接调用。

### 核心资产创建

在编辑器的内容浏览器中，右键点击，选择“创建基本资产” -> “声音” -> “Sound Cue 模板”或“声音提示模板”。这将打开一个工厂配置窗口，允许你：
1.  **选择模板类**：从预定义的 `USoundCueTemplate` 子类中选择（如随机、循环等）。
2.  **添加音波资产**：将需要作为输入的 `USoundWave` 资产拖拽到配置窗口中。
3.  **生成资产**：确认后，插件将基于所选模板和输入音频资产，自动生成一个新的 `USoundCue` 资产。

## C++ 用法

该插件主要作为编辑器工具链的一部分，其核心 C++ 接口用于扩展编辑器行为（如资产工厂、资产定义）。以下为相关的类和用法示例。

### 头文件引入

```cpp
#include “SoundCueTemplateFactory.h”
```

### 基本用法：复制一个 SoundCueTemplate

`USoundCueTemplateCopyFactory` 类用于从一个已有的 `USoundCueTemplate` 对象复制并创建新的 SoundCue 资产。

```cpp
// 假设你有一个有效的 USoundCueTemplate 指针
USoundCueTemplate* SourceTemplate = ...;

// 获取工厂实例
USoundCueTemplateCopyFactory* CopyFactory = NewObject<USoundCueTemplateCopyFactory>();
CopyFactory->SoundCueTemplate = SourceTemplate;

// 定义新资产的基本信息
UObject* Parent = GetTransientPackage(); // 或者内容浏览器的目标路径
FName Name(“NewSoundCue_Copy”);
EObjectFlags Flags = RF_Public | RF_Standalone;

// 使用工厂创建新资产
UObject* NewAsset = CopyFactory->FactoryCreateNew(
    USoundCue::StaticClass(), Parent, Name, Flags, nullptr, GWarn);

if (USoundCue* NewCue = Cast<USoundCue>(NewAsset))
{
    // 新的声音提示已创建，可以进行后续编辑或保存
}
```

### 进阶用法：通过编程方式创建模板实例

虽然通常通过编辑器 UI 使用，但你也可以在 C++ 中调用 `USoundCueTemplateFactory` 来创建基于特定模板类的新资产。

```cpp
// 获取工厂
USoundCueTemplateFactory* TemplateFactory = NewObject<USoundCueTemplateFactory>();

// 设置要使用的模板类（必须是 USoundCueTemplate 的子类）
TemplateFactory->SoundCueTemplateClass = UMyCustomRandomSoundCueTemplate::StaticClass();

// 提供输入的音频资产
TArray<TWeakObjectPtr<USoundWave>> Waves;
Waves.Add(MySoundWave1);
Waves.Add(MySoundWave2);
TemplateFactory->SoundWaves = Waves;

// 设置创建参数
UObject* Parent = ...; // 目标包
FName Name(“ProcedurallyCreatedCue”);
EObjectFlags Flags = ...;

// 创建资产
UObject* NewAsset = TemplateFactory->FactoryCreateNew(
    UMyCustomRandomSoundCueTemplate::StaticClass(), Parent, Name, Flags, nullptr, GWarn);
```

## Demo 示例

以下示例展示了如何创建一个自定义的 `USoundCueTemplate` 子类，该模板定义了一种简单的音量随机化行为。

```cpp
// MyRandomVolumeSoundCueTemplate.h
#pragma once

#include "SoundCueTemplate.h"
#include "MyRandomVolumeSoundCueTemplate.generated.h"

/**
 * 一个简单的声音提示模板，生成的 SoundCue 会将输入音波的音量随机化。
 */
UCLASS(Blueprintable)
class MYGAME_API UMyRandomVolumeSoundCueTemplate : public USoundCueTemplate
{
    GENERATED_BODY()

public:
    UMyRandomVolumeSoundCueTemplate();

    /** 音量随机化的最小值 (0.0 - 1.0) */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Randomization", meta=(ClampMin="0.0", ClampMax="1.0"))
    float MinVolumeMultiplier;

    /** 音量随机化的最大值 (0.0 - 1.0) */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Randomization", meta=(ClampMin="0.0", ClampMax="1.0"))
    float MaxVolumeMultiplier;

    // UFactory 接口的实现，用于构建 SoundCue 的节点网络
    virtual UObject* FactoryCreateNew(UClass* InClass, UObject* InParent, FName InName, EObjectFlags Flags, UObject* Context, FFeedbackContext* Warn, FName CallingContext) override;

private:
    // 辅助函数，用于向 SoundCue 添加节点
    void AddRandomVolumeNode(USoundCue* InCue, USoundWave* InWave);
};
```

```cpp
// MyRandomVolumeSoundCueTemplate.cpp
#include "MyRandomVolumeSoundCueTemplate.h"
#include "SoundCue.h"
#include "Sound/SoundNodeRandom.h"

UMyRandomVolumeSoundCueTemplate::UMyRandomVolumeSoundCueTemplate()
    : MinVolumeMultiplier(0.8f)
    , MaxVolumeMultiplier(1.2f)
{
    // 设置该模板的默认名称和描述
    TemplateName = NSLOCTEXT("SoundCueTemplates", "MyRandomVolumeTemplate", "随机音量模板");
    TemplateDescription = NSLOCTEXT("SoundCueTemplates", "MyRandomVolumeTemplateDesc", "为输入音频应用随机音量变化。");
}

UObject* UMyRandomVolumeSoundCueTemplate::FactoryCreateNew(UClass* InClass, UObject* InParent, FName InName, EObjectFlags Flags, UObject* Context, FFeedbackContext* Warn, FName CallingContext)
{
    // 确保创建的是 USoundCue 类型
    USoundCue* NewCue = NewObject<USoundCue>(InParent, InClass, InName, Flags);
    if (NewCue)
    {
        // 假设我们已经通过某种方式（如编辑器选择）获得了输入的音波
        // 这里我们仅演示如何为单个音波添加节点，实际模板可能需要处理 SoundWaves 数组
        // for (USoundWave* Wave : CachedInputWaves)
        // {
        //     AddRandomVolumeNode(NewCue, Wave);
        // }
        // 为了演示，这里添加一个默认节点作为根节点
        USoundNodeRandom* RandomNode = NewObject<USoundNodeRandom>(NewCue);
        RandomNode->RandomWeights.Add(1.0f); // 单个输入的权重
        NewCue->FirstNode = RandomNode;
        NewCue->PostEditChange();
    }
    return NewCue;
}

void UMyRandomVolumeSoundCueTemplate::AddRandomVolumeNode(USoundCue* InCue, USoundWave* InWave)
{
    // 此函数的实现将创建一个 SoundNodeRandom，并连接到输入的 Wave 节点，
    // 然后设置随机的音量倍增属性。
    // 完整实现涉及更多节点操作，此处为简化演示。
}
```

## 模块依赖

该插件本身依赖于引擎的音频和蓝图系统，使用者需要在自己的 `Build.cs` 中添加以下模块依赖以使用其提供的模板类和工厂功能。

| 模块 | 用途 |
|---|---|
| `SoundCueTemplates` | 提供 `USoundCueTemplate` 基类，定义了模板的基本结构和接口。 |

*注意：编辑器模块 `SoundCueTemplatesEditor` 为插件内部使用，用于提供编辑器工厂和资产定义，一般不需要被外部项目直接依赖。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 更新了内容浏览器的“添加”菜单中音频相关的菜单结构。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将代码中的日志宏从 UE_LOG 迁移到 UE_LOGF。 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie | 为包含对应 .gen.cpp 文件的源文件添加了 UE_INLINE_GENERATED_CPP_BY_NAME 宏以优化编译。 |
| 2025-06-19 | `800d7a51` | Implement feedback & additional tidbits for right-click audio actions including | 改进了右键音频操作菜单的反馈和细节。 |
| 2025-05-19 | `a60b2b5c` | Fixup API macros for merged modules, PURE_VIRTUAL does not need API export | 修复了合并模块的 API 宏问题，PURE_VIRTUAL 不再需要 API 导出。 |

### 维护评价

- **创建时间**：该插件于2019年创建，已有7年历史。
- **更新频率**：最近一次更新在2026年4月，表明它仍在积极维护，主要是一些编译优化和编辑器集成方面的改进。
- **Beta状态**：插件自创建起就标记为 `IsBetaVersion = true`，且 `EnabledByDefault = false`。这是一个显著的警告信号，意味着它可能功能不完整、存在bug，或者API可能不稳定，不建议在生产环境中关键依赖。
- **综合评价**：虽然插件仍在维护，但其长期的Beta状态是主要风险点。它对于提高音频原型设计和工作流效率很有价值，但使用者需要接受其“实验性”的本质，并准备好自行修复或绕过潜在问题。**谨慎推荐使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SoundCueTemplates)
- [官方文档]()（.uplugin 中 DocsURL 为空）