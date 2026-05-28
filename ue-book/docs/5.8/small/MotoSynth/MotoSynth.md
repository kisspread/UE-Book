# MotoSynth

> An experimental granular vehicle engine. Intended to explore and demonstrate potential capabilities. Not supported.

| 属性 | 值 |
|---|---|
| 中文名 | 摩托音效合成器 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（合成器组件、预设资产） |
| 模块 | `MotoSynth` (Runtime), `MotoSynthEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-11-24 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MotoSynth) | |

## 用途

MotoSynth 是一个实验性的音频合成引擎，其核心功能是**实时生成逼真的摩托车/内燃机引擎声音**。它不依赖预先录制的循环音效，而是通过两种主要技术实现动态合成：
1.  **颗粒合成引擎**：将预先录制的引擎声音素材（加速声、减速声）分解成微小的“颗粒”，根据当前的转速（RPM）动态拼接、交叉淡化播放，从而生成连续、平滑且响应迅速的引擎声。
2.  **合成器音调与噪声**：可叠加基础的合成正弦波音调和噪声层，用于增强引擎的质感或模拟其他机械部件的声音。

这个插件解决了需要高度交互性、无限变化且节省内存的引擎音效需求，特别适用于赛车游戏或任何载具模拟。

## 使用场景

-   **赛车游戏**：需要根据油门、档位、负载实时变化引擎音效。
-   **载具模拟游戏**：如卡车、飞机、船只模拟，需要复杂且真实的引擎声音。
-   **VR 驾驶体验**：要求引擎声音与视觉和操控输入精确同步，以提供沉浸感。
-   **音效原型设计**：快速设计和迭代引擎声音效果，无需录制大量音频。

## 蓝图用法

核心功能通过 `USynthComponentMoto` 组件暴露给蓝图。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set RPM` | 设置当前引擎转速，可设置过渡时间实现平滑变化。 | `USynthComponentMoto` |
| `Get RPM Range` | 获取当前音源（加速/减速）所支持的有效转速范围。 | `USynthComponentMoto` |
| `Set Settings` | 运行时动态修改合成器预设参数（音量、滤波、颗粒设置等）。 | `USynthComponentMoto` |
| `Is Enabled` | 查询摩托合成器是否已启用（受全局 CVar 控制）。 | `USynthComponentMoto` |

### 使用示例（蓝图描述）

1.  在你的载具 Pawn 或 Actor 中添加一个 `SynthComponentMoto` 组件。
2.  在组件的细节面板中，指定一个 `MotoSynthPreset` 资产，该资产定义了引擎的声音特性。
3.  在蓝图中，根据游戏输入（如油门输入值）调用 `Set RPM` 节点。RPM 值需要映射到你的音源所支持的范围内（可通过 `Get RPM Range` 获取）。
4.  组件会自动根据设置的 RPM 实时合成播放引擎声音。

## C++ 用法

### 头文件引入

```cpp
#include "SynthComponents/SynthComponentMoto.h"
#include "MotoSynthPreset.h"
```

### 基本用法

创建并配置一个摩托合成器引擎实例。
```cpp
// 假设你有一个 USynthComponentMoto* MotoSynthComp

// 1. 设置一个预设
UMotoSynthPreset* MyPreset = LoadObject<UMotoSynthPreset>(nullptr, TEXT("/Game/Audio/MotoPreset.MyPreset"));
if (MyPreset)
{
    MotoSynthComp->MotoSynthPreset = MyPreset;
}

// 2. 启动合成器并设置初始 RPM
MotoSynthComp->Start();
MotoSynthComp->SetRPM(2000.0f, 0.1f); // 2000 RPM, 0.1秒内过渡

// 3. 在 Tick 或其他逻辑中更新 RPM
void AMyVehicle::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    // 根据油门输入计算目标 RPM
    float TargetRPM = FMath::Lerp(IdleRPM, MaxRPM, ThrottleInput);
    MotoSynthComp->SetRPM(TargetRPM, 0.05f); // 快速过渡
}
```

### 进阶用法

直接使用底层的 `FMotoSynthEngine` 进行更精细的控制（通常通过预设和组件间接使用）。
```cpp
// 注意：直接操作 FMotoSynthEngine 需要深入理解音频线程回调
#include "MotoSynthEngine.h"

// 创建引擎实例
FMotoSynthEngine MotoEngine;
MotoEngine.Init(GetAudioDeviceSampleRate());

// 配置预设（需要创建 FMotoSynthRuntimeSettings）
FMotoSynthRuntimeSettings Settings;
Settings.bGranularEngineEnabled = true;
Settings.GranularEngineVolume = 1.0f;
// ... 设置其他参数
MotoEngine.SetSettings(Settings);

// 设置音源（需要从 UMotoSynthSource 获取数据ID）
MotoEngine.SetSourceData(AccelerationDataID, DecelerationDataID);

// 在音频线程中生成音频（通常由 USynthComponentMoto 自动处理）
// void* AudioBuffer = ...;
// int32 NumSamples = 256;
// MotoEngine.OnGenerateAudio((float*)AudioBuffer, NumSamples);
```

## Demo 示例

最小的可编译示例：一个会根据输入改变引擎声的 Actor。
```cpp
// MyEngineSoundActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyEngineSoundActor.generated.h"

class USynthComponentMoto;

UCLASS()
class AMyEngineSoundActor : public AActor
{
    GENERATED_BODY()

public:
    AMyEngineSoundActor();

    UPROPERTY(VisibleAnywhere)
    USynthComponentMoto* MotoSynthComponent;

    UPROPERTY(EditAnywhere)
    float CurrentThrottle = 0.0f;

    UPROPERTY(EditAnywhere)
    float MinRPM = 1000.0f;

    UPROPERTY(EditAnywhere)
    float MaxRPM = 8000.0f;

    virtual void Tick(float DeltaTime) override;
};

// MyEngineSoundActor.cpp
#include "MyEngineSoundActor.h"
#include "SynthComponents/SynthComponentMoto.h"

AMyEngineSoundActor::AMyEngineSoundActor()
{
    PrimaryActorTick.bCanEverTick = true;

    MotoSynthComponent = CreateDefaultSubobject<USynthComponentMoto>(TEXT("MotoSynth"));
    RootComponent = MotoSynthComponent;
    MotoSynthComponent->bAutoActivate = true;
}

void AMyEngineSoundActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 假设 CurrentThrottle 从 0.0 (怠速) 到 1.0 (全油门) 变化
    // 你需要根据 MotoSynthPreset 中配置的实际 RPM 范围来映射
    float TargetRPM = FMath::Lerp(MinRPM, MaxRPM, CurrentThrottle);
    if (MotoSynthComponent)
    {
        MotoSynthComponent->SetRPM(TargetRPM, 0.1f); // 0.1秒内平滑过渡
    }
}
```

## 模块依赖

从源码头文件包含和类继承关系推断，此插件没有特殊的外部模块依赖。使用该插件本身无需额外依赖其他不常见的模块。

**要在此插件基础上开发，你的模块需要依赖：**
| 模块 | 用途 |
|---|---|
| `Synthesis` | 底层音频合成器框架（FOsc, FBiquadFilter等） |
| `Engine` | 核心引擎模块，提供声波、组件等基础类 |
| `AudioMixer` | 音频混音器，用于音频流处理和播放 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，代码将 double 常量截断为 float 时产生的警告。 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 内容浏览器“添加”菜单中新增“音频”子菜单。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移到新的 UE_LOGF 宏。 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将插件配置文件从 `Base*.ini` 重命名为 `Default*.ini`。 |
| 2025-08-28 | `08e89bc9` | fixup ISoundGenerator::GetNextBuffer() implementers (don't assume zero'd buffer) | 修复 ISoundGenerator::GetNextBuffer() 的实现，不再假设传入的缓冲区已清零。 |

### 维护评价

MotoSynth 自 2020 年创建以来已约有 5 年历史。从 git 日志看，它长期处于**实验性**且**维护不活跃**的状态。
-   **近期更新**：最近一次实质性更新（针对双精度警告）是约 3 年前。其他更新主要是引擎范围的代码迁移（日志宏、配置文件重命名）或编辑器 UI 调整，与插件核心音频合成功能无关。
-   **状态**：`.uplugin` 中明确标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`。官方描述中也注明“Not supported”（不支持）。
-   **功能**：核心的颗粒合成算法在 2020 年左右已基本完成，后续没有显著的功能增强或优化记录。
-   **建议**：可以用于学习和原型设计，了解颗粒合成在游戏中的应用。**不推荐用于生产环境项目**，因为它缺少官方支持、测试和持续维护。如果需要稳定的引擎声音解决方案，应考虑商业中间件或更成熟的开源方案。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MotoSynth)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MotoSynth/Tests) (如果存在)
-   [Synthesis 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Synthesis) (MotoSynth 所依赖的底层音频合成框架)