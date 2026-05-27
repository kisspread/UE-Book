# Facial Animation Bulk Importer

> Bulk importer for facial animation curves and audio. Imports facial animation curve tables (from FBX) into sound waves.

| 属性 | 值 |
|---|---|
| 中文名 | 面部动画批量导入 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `FacialAnimation` (Runtime), `FacialAnimationEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2016-11-15 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/FacialAnimation) | |

## 用途

这个插件解决的是**音频与面部动画曲线的同步播放**问题。

在对话系统和过场动画中，角色的嘴型（口型）需要与音频精确同步。传统方式需要手动为每段音频制作独立的 Morph Target 动画，工作量巨大。FacialAnimation 插件提供了另一种方案：

1. **导入阶段**：将 FBX 文件中的面部动画曲线（BlendShape / Morph Target 权重曲线）批量导入，并将曲线数据嵌入到对应的 SoundWave 资产中
2. **播放阶段**：通过 `UAudioCurveSourceComponent` 播放音频时，自动根据音频播放进度提取对应的曲线值，驱动角色的面部动画

核心思路是将"面部曲线数据"与"音频"绑定为一个整体，运行时只需播放音频组件，曲线数据会自动同步输出，无需额外的时间轴管理。

## 使用场景

- 你在制作**对话系统**，需要大量角色的口型与语音同步 → 用 FacialAnimation 导入并播放
- 你有一批**从 Motion Builder / Maya 导出的 FBX 面部动画**，需要批量处理 → 用批量导入器
- 你需要**在 Persona 中预览音频对应的口型动画** → 该插件为 Persona 增加了音频预览功能
- 你使用**蓝图驱动口型同步**，需要一个能同时提供音频和曲线的组件 → 用 `UAudioCurveSourceComponent`

## 蓝图用法

`UAudioCurveSourceComponent` 标记为 `BlueprintSpawnableComponent`，可以在蓝图中作为组件添加到 Actor。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play` | 播放音频并开始输出曲线 | `UAudioCurveSourceComponent` |
| `Stop` | 停止播放 | `UAudioCurveSourceComponent` |
| `FadeIn` | 淡入播放，支持设置淡入时长和音量 | `UAudioCurveSourceComponent` |
| `FadeOut` | 淡出播放 | `UAudioCurveSourceComponent` |
| `IsPlaying` | 查询是否正在播放 | `UAudioCurveSourceComponent` |
| `GetCurves` | 获取当前所有活跃曲线的名称和值 | `UAudioCurveSourceComponent` |
| `GetCurveValue` | 获取指定曲线的当前值 | `UAudioCurveSourceComponent` |

### 核心属性

| 属性 | 类型 | 说明 |
|---|---|---|
| `CurveSourceBindingName` | `FName` | 曲线源绑定名称，AnimBP 通过此名称查找并绑定曲线源 |
| `CurveSyncOffset` | `float` | 曲线求值时的时间偏移量（秒），用于微调口型与音频的同步 |

### 使用示例（蓝图描述）

**步骤 1 — 添加组件**

在角色蓝图中添加 `UAudioCurveSourceComponent` 组件。设置 `CurveSourceBindingName` 为一个唯一名称（如 `"FacialCurves"`）。

**步骤 2 — 配置 AnimBP**

在动画蓝图中，使用曲线节点引用 `CurveSourceBindingName`。UE 的曲线求值系统会自动通过 `ICurveSourceInterface` 查找绑定了该名称的组件。

**步骤 3 — 播放与同步**

在蓝图中调用 `Play` 节点播放音频。组件内部会：
- 根据音频播放进度自动求值嵌入的曲线数据
- 通过 `ICurveSourceInterface` 向外部暴露曲线值
- AnimBP 中的 Morph Target 节点读取这些曲线值驱动口型

如果口型与音频有轻微偏移，可调整 `CurveSyncOffset` 属性进行微调。

## C++ 用法

### 头文件引入

```cpp
#include "AudioCurveSourceComponent.h"
```

### 基本用法

创建一个使用 `UAudioCurveSourceComponent` 的 Actor，代码来自 Public/AudioCurveSourceComponent.h 接口定义：

```cpp
// 在 Actor 中创建并使用 AudioCurveSourceComponent
UCLASS()
class AMyDialogueActor : public AActor
{
    GENERATED_BODY()

public:
    AMyDialogueActor()
    {
        // 创建音频曲线源组件
        AudioCurveSource = CreateDefaultSubobject<UAudioCurveSourceComponent>(TEXT("AudioCurveSource"));
        AudioCurveSource->CurveSourceBindingName = FName("FacialCurves");
        AudioCurveSource->CurveSyncOffset = 0.0f;  // 根据需要微调
    }

    UPROPERTY(VisibleAnywhere)
    UAudioCurveSourceComponent* AudioCurveSource;

    UFUNCTION(BlueprintCallable)
    void PlayDialogue(USoundWave* DialogueWave)
    {
        if (AudioCurveSource && DialogueWave)
        {
            AudioCurveSource->SetSound(DialogueWave);
            AudioCurveSource->Play();
        }
    }

    UFUNCTION(BlueprintCallable)
    void StopDialogue()
    {
        if (AudioCurveSource)
        {
            AudioCurveSource->FadeOut(0.3f, 0.0f);
        }
    }
};
```

### 进阶用法 — 查询曲线值

通过 `ICurveSourceInterface` 查询当前播放时刻的曲线值：

```cpp
#include "AudioCurveSourceComponent.h"
#include "Curves/CurveSourceInterface.h"

// 获取当前所有曲线值
void QueryCurrentCurves(UAudioCurveSourceComponent* Component)
{
    if (!Component) return;

    TArray<FNamedCurveValue> Curves;
    Component->GetCurves_Implementation(Curves);

    for (const FNamedCurveValue& Curve : Curves)
    {
        UE_LOG(LogTemp, Log, TEXT("Curve: %s = %f"), *Curve.Name.ToString(), Curve.Value);
    }
}

// 获取单条曲线值（可用于 Morph Target 驱动）
float GetMouthOpenValue(UAudioCurveSourceComponent* Component, FName CurveName)
{
    if (!Component) return 0.0f;
    return Component->GetCurveValue_Implementation(CurveName);
}
```

**来源**：Public/AudioCurveSourceComponent.h 中 `ICurveSourceInterface` 接口实现的函数签名。

## Demo 示例

一个完整的最小 Actor 示例，可编译使用：

**MyDialogueActor.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyDialogueActor.generated.h"

class UAudioCurveSourceComponent;
class USoundWave;

UCLASS()
class MYPROJECT_API AMyDialogueActor : public AActor
{
    GENERATED_BODY()

public:
    AMyDialogueActor();

    /** 播放对话音频，同时自动输出面部动画曲线 */
    UFUNCTION(BlueprintCallable, Category = "Dialogue")
    void PlayDialogue(USoundWave* DialogueWave);

    /** 停止对话（淡出） */
    UFUNCTION(BlueprintCallable, Category = "Dialogue")
    void StopDialogue(float FadeOutDuration = 0.3f);

protected:
    /** 音频曲线源组件：同时提供音频播放和曲线输出 */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Dialogue")
    UAudioCurveSourceComponent* AudioCurveSource;

    /** 曲线绑定名称，AnimBP 通过此名称查找曲线源 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dialogue")
    FName CurveBindingName;

    /** 时间偏移，用于微调口型与音频的同步 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dialogue", meta = (ClampMin = "-1.0", ClampMax = "1.0"))
    float SyncOffset;
};
```

**MyDialogueActor.cpp**

```cpp
#include "MyDialogueActor.h"
#include "AudioCurveSourceComponent.h"
#include "Sound/SoundWave.h"

AMyDialogueActor::AMyDialogueActor()
{
    AudioCurveSource = CreateDefaultSubobject<UAudioCurveSourceComponent>(TEXT("AudioCurveSource"));
    RootComponent = AudioCurveSource;

    CurveBindingName = FName("FacialCurves");
    SyncOffset = 0.0f;
}

void AMyDialogueActor::PlayDialogue(USoundWave* DialogueWave)
{
    if (!AudioCurveSource || !DialogueWave)
    {
        return;
    }

    // 设置绑定名称和同步偏移
    AudioCurveSource->CurveSourceBindingName = CurveBindingName;
    AudioCurveSource->CurveSyncOffset = SyncOffset;

    // 设置音频并播放
    AudioCurveSource->SetSound(DialogueWave);
    AudioCurveSource->Play();
}

void AMyDialogueActor::StopDialogue(float FadeOutDuration)
{
    if (AudioCurveSource && AudioCurveSource->IsPlaying())
    {
        AudioCurveSource->FadeOut(FadeOutDuration, 0.0f);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Engine/Editor 等） | — |

`FacialAnimation` 运行时模块依赖标准的 Engine 模块（UAudioComponent 继承自 Engine）。`FacialAnimationEditor` 编辑器模块提供 FBX 批量导入功能，依赖 UnrealEd 等编辑器基础设施。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-07-10 | `abb369e2` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 添加 UE_INLINE_GENERATED_CPP_BY_NAME 宏优化编译 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar | 添加 DLL 导出标记以支持模块化构建 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件目录结构调整 |
| 2022-11-03 | `fa90b399` | Added includes for future change. This changelist only contains added #include and a couple of empty | 添加头文件引入为后续改动做准备 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新内置插件的供应商链接为 HTTPS |

### 维护评价

- **年龄**：创建于 2016 年 11 月，至今约 9 年
- **实验性状态**：`.uplugin` 标记为 `IsBetaVersion: true`，该插件自 2016 年创建以来一直处于 Beta 状态，从未正式毕业
- **更新频率**：近 3 年的更新均为全引擎范围的维护性改动（编译标记、链接修复、协议更新），没有针对该插件的功能性更新
- **活跃度**：**维护不活跃**。最后一次实质性功能更新可追溯到 2016 年创建时的初始提交
- **已知限制**：Beta 标签意味着 API 可能在未来版本中变更或移除；源码中 `Experimental` 标记（UCLASS 宏中）进一步确认其不稳定性

**结论**：该插件功能完整可用，但已长期处于"实验性维护"状态，没有积极开发。如果你的需求匹配其功能（音频驱动口型曲线），可以放心使用，但需要注意它可能在 UE 未来版本中被重构或废弃。如果你的项目对稳定性有较高要求，考虑自行实现基于 `ICurveSourceInterface` 的解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/FacialAnimation)
- 官方文档：无（`.uplugin` 中 DocsURL 为空）