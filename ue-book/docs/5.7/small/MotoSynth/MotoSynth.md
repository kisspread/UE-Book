# MotoSynth

> An experimental granular vehicle engine. Intended to explore and demonstrate potential capabilities. Not supported.

| 属性 | 值 |
|---|---|
| 中文名 | 摩托车合成器 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频源资产、预设资产） |
| 模块 | `MotoSynth` (Runtime), `MotoSynthEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-07-29 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MotoSynth) | |

## 用途

MotoSynth 是一个实验性的颗粒合成引擎，专门用于程序化生成车辆发动机声音。它基于真实录制的发动机音频样本，通过颗粒合成（Granular Synthesis）技术，根据实时输入的 RPM（每分钟转速）值动态合成连续、逼真的发动机轰鸣声。该插件提供了一套完整的工具链：从导入音频源、分析 RPM 曲线、生成颗粒表，到在运行时通过组件控制音高、音量、滤波器等参数。

为什么存在？传统的车辆声音实现通常依赖交叉淡入淡出的多段循环音频，容易产生机械感，且难以精细匹配加速/减速过程。MotoSynth 的颗粒合成方案能更自然地模拟发动机从低转速到高转速的全过程，并能通过合成音与噪声层丰富声音细节。

## 使用场景

- **开发赛车、竞速或模拟驾驶类游戏**，需要动态、逼真的发动机声音，并能实时响应油门变化。
- **需要程序化声音合成工具**，允许音效设计师从真实录音创建可交互的发动机资产。
- **探索实验性音频功能**，该插件可作为学习颗粒合成在游戏音频中应用的范例。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetRPM` | 设置发动机的 RPM 值，可指定过渡时间（秒） | `USynthComponentMoto` |
| `SetSettings` | 动态覆盖当前运行时设置（如合成音、噪声参数） | `USynthComponentMoto` |
| `GetRPMRange` | 获取当前有效 RPM 范围（考虑加速/减速配置后的最小值和最大值） | `USynthComponentMoto` |
| `IsEnabled` | 返回 MotoSynth 是否已启用 | `USynthComponentMoto` |

### 使用示例（蓝图描述）

1. **基本发声**：
   - 在关卡中放置一个 `SynthComponentMoto` 组件（或动态添加）。
   - 在 Details 面板中为其 `MotoSynthPreset` 属性指定一个已创建的预设资产。
   - 设置 `RPM` 初始值（如 1000）。
   - 调用 `Play` 开始播放，组件将根据预设和 RPM 持续生成声音。

2. **动态控制 RPM**：
   - 每帧从游戏逻辑获取油门输入（如 0~1 的浮点数）。
   - 将油门值映射到 RPM 范围（例如 800~10000）。
   - 调用 `SetRPM` 节点，传入目标 RPM 和过渡时间（如 0.5 秒）。
   - 发动机声音会平滑变化至新 RPM。

3. **切换运行时设置**：
   - 创建一个 `MotoSynth Runtime Settings` 结构体变量（蓝图结构体 `FMotoSynthRuntimeSettings`）。
   - 调整其中的 `bSynthToneEnabled`、`bNoiseEnabled`、`bGranularEngineEnabled` 等字段。
   - 调用 `SetSettings` 节点传入该结构体，实时覆盖预设中的对应参数。

## C++ 用法

### 头文件引入

```cpp
#include "SynthComponentMoto.h"
#include "MotoSynthPreset.h"
```

### 基本用法

从测试用例和源码提炼的典型用法：

```cpp
// 假设已有 UMotoSynthPreset* MyPreset（已加载或从资产引用）

// 创建 MotoSynth 组件（可作为 Actor 的子组件自动创建）
USynthComponentMoto* MotoComponent = CreateDefaultSubobject<USynthComponentMoto>(TEXT("MotoSynth"));

// 赋值预设
MotoComponent->MotoSynthPreset = MyPreset;

// 设置初始 RPM
MotoComponent->RPM = 1500.0f;

// 激活并播放（通常由父 Actor 触发）
MotoComponent->Play();

// 在游戏过程中更新 RPM（例如受油门影响）
void AMyVehicle::UpdateEngineRPM(float TargetRPM, float TimeToReach)
{
    MotoComponent->SetRPM(TargetRPM, TimeToReach);
}

// 获取 RPM 范围
float MinRPM, MaxRPM;
MotoComponent->GetRPMRange(MinRPM, MaxRPM);

// 动态覆写运行时设置
FMotoSynthRuntimeSettings OverrideSettings;
OverrideSettings.bSynthToneEnabled = true;
OverrideSettings.SynthToneVolumeRange = FVector2D(0.2f, 0.8f);
MotoComponent->SetSettings(OverrideSettings);
```

来源文件：`Engine/Plugins/Experimental/MotoSynth/Source/MotoSynth/Classes/SynthComponents/SynthComponentMoto.h`

### 进阶用法

结合预设和数据管理器，手动加载源数据：

```cpp
#include "MotoSynthSourceAsset.h"
#include "MotoSynthDataManager.h"

// 加载一个 MotoSynthSource 资源
UMotoSynthSource* MySource = LoadObject<UMotoSynthSource>(nullptr, TEXT("/Game/MyVehicleEngineSource"));

// 源资源会在 PostLoad 时自动向 FMotoSynthSourceDataManager 注册数据，
// 之后颗粒引擎可以直接使用。无需额外操作。

// 若要手动管理数据（例如在编辑器工具中），可使用 FMotoSynthSourceDataManager::RegisterData
// 但通常通过资源资产加载即可。
```

通过 `FMotoSynthAssetManager` 全局单例管理资产池（实际由引擎内部处理，用户一般不直接调用）。

## Demo 示例

以下是一个最小化的 C++ Actor 类，演示如何创建并控制 MotoSynth 组件。

**MyVehicle.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyVehicle.generated.h"

class USynthComponentMoto;

UCLASS()
class AMyVehicle : public AActor
{
    GENERATED_BODY()

public:
    AMyVehicle();

    virtual void Tick(float DeltaTime) override;

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Audio")
    USynthComponentMoto* MotoSynthComponent;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Audio")
    class UMotoSynthPreset* MotoPreset;

    float CurrentRPM;
    float TargetRPM;
};
```

**MyVehicle.cpp**
```cpp
#include "MyVehicle.h"
#include "SynthComponentMoto.h"
#include "MotoSynthPreset.h"

AMyVehicle::AMyVehicle()
{
    PrimaryActorTick.bCanEverTick = true;

    MotoSynthComponent = CreateDefaultSubobject<USynthComponentMoto>(TEXT("MotoSynth"));
    MotoSynthComponent->bAutoActivate = false; // 手动激活
    RootComponent = MotoSynthComponent; // 作为根组件（仅演示）
}

void AMyVehicle::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 模拟油门控制（假设按空格加速）
    if (GetWorld()->GetFirstPlayerController() &&
        GetWorld()->GetFirstPlayerController()->WasInputKeyJustPressed(EKeys::SpaceBar))
    {
        TargetRPM = FMath::FRandRange(2000.0f, 8000.0f);
        // 平滑过渡到目标 RPM，耗时 0.3 秒
        MotoSynthComponent->SetRPM(TargetRPM, 0.3f);
    }
}

void AMyVehicle::BeginPlay()
{
    Super::BeginPlay();
    if (MotoPreset)
    {
        MotoSynthComponent->MotoSynthPreset = MotoPreset;
        MotoSynthComponent->RPM = 1000.0f;
        MotoSynthComponent->Play();
    }
}
```

注意：需要在 Build.cs 中添加对 `MotoSynth` 模块的依赖。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AudioMixer` | 底层音频混合与渲染 |
| `SignalProcessing` | 颗粒合成、滤波器、振荡器 DSP 库 |
| `Engine` | 声音生成器、音频组件基类 |

（`Core`, `CoreUObject`, `Engine` 等标准依赖省略。）

## 维护状态

### 近期更新

- 2025-08-28 `08e89bc9` fixup ISoundGenerator::GetNextBuffer() implementers (don't assume zero'd buffer)
- 2025-06-19 `800d7a51` Implement feedback & additional tidbits for right-click audio actions including
- 2025-04-23 `939cc6e5` Used FortniteClient build target to find and convert all files to have dllstorage on methods/staticv
- 2024-11-10 `66e9bb39` Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base
- 2024-07-29 `0084b0f6` CIS Followup - deleting pointer to incomplete type.

### 维护评价

- **年龄**：创建于 2024 年 7 月，至今约 1 年。
- **更新频率**：2024 年有几次提交，2025 年有三次功能性/修复性更新，表明仍在维护中。
- **活跃度**：较活跃，最近一次更新在 2025 年 8 月。
- **已知问题**：标为实验性（IsExperimentalVersion=true），官方注"Not supported"。可能存在性能或稳定性限制，不建议直接用于生产项目。
- **推荐度**：适合学习和实验，或作为临时解决方案。对于正式项目，建议评估后使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MotoSynth)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/MotoSynth/Source/MotoSynth/Private/MotoSynthEngine.cpp)（引擎主要实现在该文件中）
- 官方文档：无（实验性插件，无独立文档）