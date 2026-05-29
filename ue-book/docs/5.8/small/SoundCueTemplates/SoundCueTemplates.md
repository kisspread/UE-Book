# Sound Cue Templates

> Collection of SoundCue Templates, which provide rapid design of common audio design workflows.

| 属性 | 值 |
|---|---|
| 中文名 | 声音提示模板 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器自定义界面） |
| 模块 | `SoundCueTemplates` (Runtime), `SoundCueTemplatesEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-07-19 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SoundCueTemplates) | |

## 用途

该插件为音频设计师提供了一系列预设的 SoundCue 模板（如容器、距离渐变）。其核心目的是通过图形化的属性配置，自动生成复杂的 SoundCue 节点图，从而将常见的音频设计工作流程（如随机播放、拼接播放、基于距离的混音）从手动搭建节点中解放出来，实现“快速原型设计”。

## 使用场景

- 你需要为游戏中的脚步声、环境音效或武器音效快速创建一个带有随机变化（Randomize）或顺序播放（Concatenate）的 SoundCue。
- 你需要实现一个基于玩家距离远近，在不同音效之间自动渐变混音（Crossfade）的效果。
- 你希望统一团队中 SoundCue 的创建流程和质量等级（如低配、高配），以管理内存和性能开销。

## 蓝图用法

该插件的蓝图功能主要集中在编辑器工具和资产创建上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddSoundWavesToTemplate` | 将一组音频波形资源添加到模板中，用于初始化模板内容。 | `USoundCueTemplate` |

### 使用示例（蓝图描述）

1.  **创建模板资产**：在内容浏览器中右键，选择 `Audio` -> `Sound Cue Template` -> `Container` 或 `Distance Crossfade`。
2.  **配置模板属性**：在资产详情面板中，根据选择的模板类型设置参数。
    - 对于 `Container`，选择容器类型（Concatenate/Randomize/Mix）、循环、调制范围，并添加 `Variations`（音频波形）。
    - 对于 `Distance Crossfade`，设置循环，并为每个距离点配置一个 `Variation`，包含距离信息和对应的音效波形。
3.  **生成节点图**：当上述属性被修改时，插件会自动在后台为该 SoundCue 重建对应的节点图。你可以通过资产的 `“复制到声音提示”` 右键菜单，将生成的节点图复制到一个新的标准 SoundCue 中查看和编辑。

## C++ 用法

### 头文件引入

```cpp
#include "SoundCueTemplate.h"
#include "SoundCueContainer.h" // 如需使用容器模板
#include "SoundCueDistanceCrossfade.h" // 如需使用距离渐变模板
```

### 基本用法

通过继承 `USoundCueTemplate` 并重写 `OnRebuildGraph` 函数，可以创建自定义的 SoundCue 模板。以下是一个简化示例，创建一个简单的双音混合模板。

```cpp
// MySoundCueMixTemplate.h
#pragma once
#include "SoundCueTemplate.h"
#include "MySoundCueMixTemplate.generated.h"

UCLASS(MinimalAPI, BlueprintType)
class UMySoundCueMixTemplate : public USoundCueTemplate
{
    GENERATED_BODY()

#if WITH_EDITORONLY_DATA
public:
    UPROPERTY(EditAnywhere, Category = "Mix")
    TObjectPtr<USoundWave> WaveA;

    UPROPERTY(EditAnywhere, Category = "Mix")
    TObjectPtr<USoundWave> WaveB;

    UPROPERTY(EditAnywhere, Category = "Mix")
    float CrossfadeTime = 0.5f;
#endif

#if WITH_EDITOR
protected:
    virtual void OnRebuildGraph(USoundCue& SoundCue) const override;
#endif
};
```

```cpp
// MySoundCueMixTemplate.cpp
#include "MySoundCueMixTemplate.h"
#include "SoundCue.h"
#include "SoundNodeWavePlayer.h"
#include "SoundNodeMixer.h"

#if WITH_EDITOR
void UMySoundCueMixTemplate::OnRebuildGraph(USoundCue& SoundCue) const
{
    // 清除现有节点（如果有）
    SoundCue.ResetGraph();

    if (WaveA && WaveB)
    {
        // 创建根节点（Mixer）
        USoundNodeMixer& MixerNode = ConstructSoundNodeRoot<USoundNodeMixer>(SoundCue);
        MixerNode.InputVolume.Init(2); // 两个输入

        // 创建 WaveA 的播放器节点，并连接到 Mixer 的第 0 个输入
        USoundNodeWavePlayer& PlayerA = ConstructSoundNodeChild<USoundNodeWavePlayer>(SoundCue, &MixerNode, /*Column=*/1, /*Row=*/0, /*InputPinIndex=*/0);
        PlayerA.SetSoundWave(WaveA);

        // 创建 WaveB 的播放器节点，并连接到 Mixer 的第 1 个输入
        USoundNodeWavePlayer& PlayerB = ConstructSoundNodeChild<USoundNodeWavePlayer>(SoundCue, &MixerNode, /*Column=*/1, /*Row=*/1, /*InputPinIndex=*/1);
        PlayerB.SetSoundWave(WaveB);

        // 此处可添加更复杂的逻辑，例如基于 CrossfadeTime 连接 Crossfade 节点
    }
}
#endif
```

### 进阶用法

模板可以集成质量等级系统，为不同硬件配置生成不同复杂度的节点图。

```cpp
// 在 OnRebuildGraph 中使用质量设置
#if WITH_EDITOR
void USoundCueContainer::OnRebuildGraph(USoundCue& SoundCue) const
{
    // ... 省略清理和基础设置 ...

    const USoundCueTemplateSettings* Settings = GetDefault<USoundCueTemplateSettings>();
    if (Settings)
    {
        // 假设我们使用第一个质量等级（如“低配”）
        const FSoundCueTemplateQualitySettings& QualitySettings = Settings->GetQualityLevelSettings(0);
        int32 MaxVariations = 0;

        switch (ContainerType)
        {
        case ESoundContainerType::Randomize:
            MaxVariations = QualitySettings.MaxRandomizedVariations;
            break;
        // ... 处理其他类型 ...
        }

        // 限制添加的变体数量
        TArray<TObjectPtr<USoundWave>> SelectedVariations;
        for (int32 i = 0; i < FMath::Min(Variations.Num(), MaxVariations); ++i)
        {
            SelectedVariations.Add(Variations[i]);
        }

        // 使用 SelectedVariations 而非完整的 Variations 来构建节点图
        // ... 构建随机、混合或拼接逻辑 ...
    }
}
#endif
```

## Demo 示例

以下是一个最小的、可编译的自定义 SoundCue 模板示例，它创建一个简单的循环播放器。

```cpp
// SimpleLoopTemplate.h
#pragma once
#include "SoundCueTemplate.h"
#include "SimpleLoopTemplate.generated.h"

UCLASS(MinimalAPI, BlueprintType)
class USimpleLoopTemplate : public USoundCueTemplate
{
    GENERATED_BODY()

#if WITH_EDITORONLY_DATA
public:
    UPROPERTY(EditAnywhere, Category = "Audio")
    TObjectPtr<USoundWave> WaveToLoop;
#endif

#if WITH_EDITOR
protected:
    virtual void OnRebuildGraph(USoundCue& SoundCue) const override;
#endif
};
```

```cpp
// SimpleLoopTemplate.cpp
#include "SimpleLoopTemplate.h"
#include "SoundCue.h"
#include "SoundNodeWavePlayer.h"

#if WITH_EDITOR
void USimpleLoopTemplate::OnRebuildGraph(USoundCue& SoundCue) const
{
    SoundCue.ResetGraph();

    if (WaveToLoop)
    {
        // 创建根节点并设置为循环播放
        USoundNodeWavePlayer& RootPlayer = ConstructSoundNodeRoot<USoundNodeWavePlayer>(SoundCue);
        RootPlayer.SetSoundWave(WaveToLoop);
        RootPlayer.bLooping = true;
    }
}
#endif
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AudioMixer` | 底层音频混合器接口 |
| `SoundUtilities` | 音频工具函数 |

*注意*：此插件主要与音频编辑器（如 `SoundCueGraph`）深度集成，因此可能依赖于多个编辑器模块。在你的 `Build.cs` 中，除了上述可能的运行时依赖，通常需要添加对 `SoundCueTemplates` 模块的 `PrivateDependencyModuleNames`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 更新了内容浏览器中音频相关的右键菜单。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF。 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied | 为生成头文件添加内联宏，优化编译。 |
| 2025-06-19 | `800d7a51` | Implement feedback & additional tidbits for right-click audio actions including | 改进了右键音频操作的反馈和细节。 |
| 2025-05-19 | `a60b2b5c` | Fixup API macros for merged modules, PURE_VIRTUAL does not need API export | 修复了合并模块的API宏导出问题。 |

### 维护评价

该插件创建于 2019 年，属于 **老古董** 级别资产。从 git 历史看，尽管更新频率不高，但**在最近一年内仍有维护性更新**（如 API 宏修复、菜单更新、代码优化）。然而，其 `.uplugin` 中明确标记为 `“IsBetaVersion”: true` 且 `“EnabledByDefault”: false`，表明它仍处于**实验阶段**。这意味着它可能未经过大规模生产环境验证，API 或功能未来可能发生变化。

**综合评价**：该插件仍处于活跃的维护和改进中，但其“实验性”状态是主要风险。适合在项目中用于**快速原型设计和内部工具开发**，若计划用于最终产品，需评估其稳定性并做好自行维护的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SoundCueTemplates)
- [官方文档]() (无)
- [测试用例]() (未在提供路径中发现标准测试文件)