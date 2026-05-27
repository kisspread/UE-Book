# Facial Animation Bulk Importer

> Bulk importer for facial animation curves and audio. Imports facial animation curve tables (from FBX) into sound waves.

| 属性 | 值 |
|---|---|
| 中文名 | 面部动画批量导入器 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `FacialAnimation` (Runtime), `FacialAnimationEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2016-11-15 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/FacialAnimation) | |

## 用途

这是一个面向动画师和编辑器工具的插件，旨在简化面部动画（尤其是口型同步）的工作流。其核心功能是**将音频文件（.wav）及其对应的面部动画曲线数据（通常从 FBX 文件中提取）批量导入并打包到 `USoundWave` 资产中**。

它解决的问题是：当需要为大量的对白或语音创建口型同步动画时，手动逐个创建动画序列或驱动数据非常繁琐。此插件通过批量处理，将曲线数据（如“jaw_open”、“mouth_wide”等）与音频绑定，使得动画师或技术美术能够快速生成一套可用于驱动骨骼网格体或 Morph Target 的动画数据。

此外，插件还提供了一个运行时组件 `UAudioCurveSourceComponent`，它继承自音频组件并实现了曲线源接口，能够根据播放的音频实时输出对应的动画曲线值，从而在游戏运行时驱动角色面部动画。

## 使用场景

- **为对话系统创建口型同步动画**：你的项目中有成百上千条对话语音，需要为每条语音生成对应的口型动画。使用此插件可以批量导入 FBX 中的曲线数据到对应的 SoundWave 中，节省大量手动设置时间。
- **需要基于音频实时驱动动画**：你希望角色的嘴部动作能够根据正在播放的语音实时变化，而不是预先烘焙好的动画序列。可以使用 `UAudioCurveSourceComponent` 来播放音频并获取同步的曲线数据。
- **技术美术构建自定义动画管线**：你需要将外部动画数据（如从 MotionBuilder 或专业口型同步软件导出）集成到 Unreal 的动画蓝图流程中。此插件提供了曲线源接口 (`ICurveSourceInterface`)，你可以基于它构建自己的数据驱动节点。

## 蓝图用法

该插件主要提供了一个可蓝图生成的运行时组件。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Curve Source Binding Name` | 设置此组件在动画蓝图中绑定时使用的名称。 | `UAudioCurveSourceComponent` |
| `Set Curve Sync Offset` | 设置在评估曲线时应用于音频播放位置的时间偏移量（秒）。 | `UAudioCurveSourceComponent` |
| `Get Curve Value` | 获取指定名称的动画曲线当前值。 | `UAudioCurveSourceComponent` (实现 ICurveSourceInterface) |
| `Get Curves` | 获取此组件当前提供的所有动画曲线值。 | `UAudioCurveSourceComponent` (实现 ICurveSourceInterface) |

### 使用示例（蓝图描述）

1.  **在角色蓝图中添加组件**：
    - 在你的角色蓝图中，添加一个 `UAudioCurveSourceComponent`。
    - 在该组件的细节面板中，设置 `Curve Source Binding Name` 为一个唯一的名称，例如 `“LipSyncSource”`。

2.  **在动画蓝图中绑定并使用曲线**：
    - 打开角色的动画蓝图。
    - 在动画图表中，添加一个 `Curve Source` 节点。
    - 将该节点的 `Source Name` 设置为与步骤 1 中相同的名称（`“LipSyncSource”`）。
    - 将 `Curve Source` 节点的输出引脚连接到后续的动画节点，例如 `Modify Curve` 节点或 `Morph Target` 节点，用于驱动面部骨骼或混合形状。

3.  **播放音频驱动动画**：
    - 在游戏逻辑（例如对话系统）中，调用 `AudioCurveSourceComponent` 的 `Play` 函数来播放绑定的 SoundWave。
    - 组件在播放音频的同时，会根据内置的曲线表数据，实时输出动画曲线值，从而驱动动画蓝图中的面部动画。

## C++ 用法

插件的核心运行时功能由 `UAudioCurveSourceComponent` 提供。它通常不需要直接实例化，而是作为其他系统的基础或通过编辑器工具链（批量导入器）生成的数据的运行时载体。

### 头文件引入

```cpp
// 使用 AudioCurveSourceComponent
#include "AudioCurveSourceComponent.h"

// 如果你需要实现自定义的曲线源接口
#include "Animation/CurveSourceInterface.h"
```

### 基本用法

你可以创建一个自定义组件来实现 `ICurveSourceInterface`，从而提供动画曲线。

```cpp
// MyCustomCurveSource.h
#pragma once
#include "Components/ActorComponent.h"
#include "Animation/CurveSourceInterface.h"
#include "MyCustomCurveSource.generated.h"

UCLASS(ClassGroup=(Animation), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyCustomCurveSource : public UActorComponent, public ICurveSourceInterface
{
    GENERATED_BODY()

public:
    // 通过 ICurveSourceInterface 提供绑定名称
    virtual FName GetBindingName_Implementation() const override
    {
        return TEXT("MyCustomSource");
    }

    // 返回指定曲线的当前值
    virtual float GetCurveValue_Implementation(FName CurveName) const override
    {
        // 此处应包含你的逻辑，例如从骨骼网格体、Morph Target 或外部数据获取曲线值
        if (CurveName == TEXT("jaw_open"))
        {
            return JawOpenValue; // 假设 JawOpenValue 是一个受控的成员变量
        }
        return 0.0f;
    }

    // 返回所有可用曲线的列表及其当前值
    virtual void GetCurves_Implementation(TArray<FNamedCurveValue>& OutCurve) const override
    {
        OutCurve.Add(FNamedCurveValue(TEXT("jaw_open"), GetCurveValue_Implementation(TEXT("jaw_open"))));
        // 添加其他曲线...
    }

    UPROPERTY(BlueprintReadWrite, Category="Curve")
    float JawOpenValue = 0.f;
};
```

### 进阶用法

`UAudioCurveSourceComponent` 内部通过音频的 `OnPlaybackPercent` 事件来同步曲线评估。如果你需要深入理解或调试其同步机制，可以关注以下成员变量：

- `CachedCurveTable`：缓存的曲线表数据（来自 SoundWave）。
- `CachedCurveEvalTime`：根据音频播放进度计算出的曲线评估时间。
- `CurveSyncOffset`：用于补偿音频处理延迟的时间偏移。

在动画蓝图中，你可以使用 `Curve Source` 节点或通过 `Animation Node` 来查询任何实现了 `ICurveSourceInterface` 的对象。

## Demo 示例

以下是一个最小化的、实现自定义曲线源组件的示例，它不依赖于音频播放，而是基于一个外部输入的浮点数来驱动曲线。

### MySimpleCurveSource.h
```cpp
#pragma once
#include "Components/ActorComponent.h"
#include "Animation/CurveSourceInterface.h"
#include "MySimpleCurveSource.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class UMySimpleCurveSource : public UActorComponent, public ICurveSourceInterface
{
    GENERATED_BODY()

public:
    UMySimpleCurveSource();

    virtual FName GetBindingName_Implementation() const override;
    virtual float GetCurveValue_Implementation(FName CurveName) const override;
    virtual void GetCurves_Implementation(TArray<FNamedCurveValue>& OutCurve) const override;

    // 蓝图可设置的曲线输入值
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Curve Input")
    float SmileInputValue = 0.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Curve Input")
    float FrownInputValue = 0.f;

private:
    FName BindingName;
};
```

### MySimpleCurveSource.cpp
```cpp
#include "MySimpleCurveSource.h"

UMySimpleCurveSource::UMySimpleCurveSource()
{
    PrimaryComponentTick.bCanEverTick = false;
    BindingName = TEXT("SimpleCurveSource");
}

FName UMySimpleCurveSource::GetBindingName_Implementation() const
{
    return BindingName;
}

float UMySimpleCurveSource::GetCurveValue_Implementation(FName CurveName) const
{
    if (CurveName == TEXT("Smile"))
    {
        return SmileInputValue;
    }
    if (CurveName == TEXT("Frown"))
    {
        return FrownInputValue;
    }
    return 0.f;
}

void UMySimpleCurveSource::GetCurves_Implementation(TArray<FNamedCurveValue>& OutCurve) const
{
    OutCurve.Emplace(TEXT("Smile"), SmileInputValue);
    OutCurve.Emplace(TEXT("Frown"), FrownInputValue);
}
```

## 模块依赖

FacialAnimation 模块依赖以下模块：

| 模块 | 用途 |
|---|---|
| `AudioMixer` | 用于底层音频处理，特别是 `UAudioCurveSourceComponent` 中与播放百分比同步相关的功能。 |

*无特殊依赖（仅标准 Core/Engine/Slate 等）*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-07-10 | `abb369e2` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 为包含对应 `.gen.cpp` 文件的源文件添加内联生成宏。 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar | 使用 UnrealGame 构建目标查找并转换文件，为方法和静态变量添加 DLL 导出属性。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件目录的通用维护提交。 |
| 2022-11-03 | `fa90b399` | Added includes for future change. This changelist only contains added #include and a couple of empty | 为未来更改添加头文件包含。本次提交仅包含添加的 `#include` 和一些空行。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新内置插件的厂商链接，使用安全协议（HTTPS）。 |

### 维护评价

- **创建时间**：插件创建于 **2016年**，距今已约9年。
- **最近更新频率**：最近的提交记录均为**通用的引擎维护性更改**（如宏更新、编译属性调整、安全协议更新），并非针对 FacialAnimation 插件的功能更新或 Bug 修复。
- **活跃状态**：该插件自创建后，似乎**没有持续的活跃功能开发**。其“实验性/Beta”状态一直未改变，且最后一次涉及其核心功能的实质性提交（如 `610c4676` 之前）可追溯至数年前。
- **已知问题/限制**：插件标记为 `IsBetaVersion=true`，表明 Epic 官方认为其功能可能不完整或未经充分测试。`.uplugin` 中的 `Description` 也明确指出其用途，暗示这是一个特定工作流的工具。
- **推荐使用**：**谨慎使用**。该插件是为了解决一个非常具体的编辑器内批量导入工作流而创建的。对于新的项目，尤其是需要更通用或更强大口型同步解决方案的项目，建议评估现代方案（如 MetaHuman 的集成工具链或第三方插件）。如果项目历史资产依赖于此工作流，且其功能满足需求，则可以继续使用，但需自行承担其“实验性”状态带来的潜在风险，并可能无法获得官方的未来支持或更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/FacialAnimation)
- 官方文档：无
- 测试用例：未在插件目录中发现标准测试文件