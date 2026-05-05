# Soundscape Plugin

> A Dynamic Ambient Sound System

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（自定义资产类型：Soundscape Color、Soundscape Palette） |
| 模块 | `Soundscape` (Runtime), `SoundscapeEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-05-27 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Soundscape) | |

## 用途

Soundscape 是一个**程序化环境声生成系统**。它解决的核心问题是：在开放世界游戏中，设计师需要根据玩家位置、区域特征和游戏状态，动态地播放数百个环境音效（鸟叫、虫鸣、风声、水声等），而不需要手动在场景中放置数百个 Audio Component。

Soundscape 的设计采用了"画家"隐喻：

- **Color**（颜色）：一种声音的定义，包含音频资产、音量/音调、生成行为（距离、角度、数量、重试频率）和调制行为（随机化音量/音调、淡入淡出）
- **Palette**（调色板）：多个 Color 的集合，附带播放条件（基于 GameplayTag Query），用于描述一个"声景"，例如"森林白天"、"森林夜晚"、"城市雨天"
- **Palette Collection**（调色板集合）：多个 Palette 的软引用集合，可以在 Project Settings 中全局配置，也可以运行时通过代码动态添加

系统通过 **GameplayTag 状态机** 控制当前激活哪些 Palette。当调用 `SetState` 设置一个标签时，Subsystem 会评估所有已加载 Palette 的条件（`SoundscapePalettePlaybackConditions`），自动开始/停止对应的环境声。

此外，Soundscape 还提供了一个 **Color Point 系统**：通过在场景中放置带 `SoundscapeColorPointComponent` 的 Actor，可以标记"声音区域点"（如鸟的位置），系统用 3 级 LOD 的空间哈希表计算密度，Color 可以根据密度阈值决定是否生成声音。

## 使用场景

- 你在做一个开放世界游戏，需要根据生物群落和时间自动切换环境声 → 用 Soundscape Palette + State 系统
- 你需要让鸟叫声只在有鸟巢的区域播放 → 用 Color Point + `bFilterByColorPointDensity`
- 你需要程序化地在玩家周围随机生成环境声，距离、角度都可以配置 → 用 Soundscape Color 的 Spawn Behavior
- 你需要在运行时动态切换声景（如进入室内、天气变化）→ 用 `SetState` / `ClearState`

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetState` | 设置 Soundscape 状态标签，触发匹配的 Palette 播放 | `USoundscapeSubsystem` |
| `ClearState` | 清除状态标签，停止不再匹配的 Palette | `USoundscapeSubsystem` |
| `RestartSoundscape` | 重启所有活跃的 Palette | `USoundscapeSubsystem` |
| `AddPaletteCollection` | 动态添加一个 Palette 集合（运行时加载） | `USoundscapeSubsystem` |
| `RemovePaletteCollection` | 移除一个 Palette 集合 | `USoundscapeSubsystem` |
| `AddColorPointCollection` | 添加一组 Color Point 位置数据 | `USoundscapeSubsystem` |
| `RemoveColorPointCollection` | 移除 Color Point 集合 | `USoundscapeSubsystem` |
| `CheckColorPointDensity` | 查询指定位置的 Color Point 密度 | `USoundscapeSubsystem` |
| `SpawnSoundscapeColor` | 手动生成一个 Color 实例（不自动播放） | `USoundscapeBPFunctionLibrary` |
| `SpawnSoundscapePalette` | 手动生成一个 Palette 实例 | `USoundscapeBPFunctionLibrary` |
| `Play` | 开始播放 Active Soundscape Color | `UActiveSoundscapeColor` |
| `Stop` | 停止播放 Active Soundscape Color | `UActiveSoundscapeColor` |
| `IsPlaying` | 查询是否正在播放 | `UActiveSoundscapeColor` |

### 使用示例（蓝图描述）

**基本声景切换（推荐方式）**：

1. 在 Project Settings → Soundscape 中，配置 `SoundscapePaletteCollection`，添加所有 Palette 资产
2. 在 Level Blueprint 或 GameMode 的 BeginPlay 中：
   - Get Game Instance → Get Subsystem `USoundscapeSubsystem` → 调用 `SetState`，传入 `GameplayTag`（如 `Soundscape.Biome.Forest`）
3. 当玩家切换区域时，调用 `ClearState` 清除旧标签，`SetState` 设置新标签

**手动控制单个 Color**：

1. Get Game Instance → Get Subsystem → 调用 `SpawnSoundscapeColor`，传入一个 `SoundscapeColor` 资产
2. 从返回的 `UActiveSoundscapeColor` 引用调用 `Play(1.0, 1.0, 2.0)`（音量、音调、淡入时间）
3. 需要停止时调用 `Stop(2.0)`（淡出时间）

**使用 Color Point 控制声音区域**：

1. 在场景中放置 Actor，添加 `SoundscapeColorPointComponent`，设置 `ColorPoint` 标签（如 `Soundscape.ColorPoint.Bird`）
2. 在 `SoundscapeColor` 的 Spawn Behavior 中启用 `bFilterByColorPointDensity`，设置 `ColorPoint` 标签和 `MinColorPointNumber`
3. Color 只会在 Color Point 密度达到阈值的区域生成声音

## C++ 用法

### 头文件引入

```cpp
#include "SoundscapeSubsystem.h"
#include "SoundscapeColor.h"
#include "SoundScapePalette.h"
#include "SoundScape.h"
```

### 基本用法

从 Subsystem 的运行时行为提取：

```cpp
// 获取 Soundscape Subsystem
UGameInstance* GameInstance = World->GetGameInstance();
USoundscapeSubsystem* SoundscapeSubsystem = GameInstance->GetSubsystem<USoundscapeSubsystem>();

// 设置状态（触发匹配的 Palette 播放）
SoundscapeSubsystem->SetState(FGameplayTag::RequestGameplayTag(TEXT("Soundscape.Biome.Forest")));

// 清除状态（停止不再匹配的 Palette）
SoundscapeSubsystem->ClearState(FGameplayTag::RequestGameplayTag(TEXT("Soundscape.Biome.Forest")));

// 重启所有 Palette
SoundscapeSubsystem->RestartSoundscape();
```

### 进阶用法

动态添加 Palette Collection 和 Color Point Collection：

```cpp
// 动态添加一个 Palette Collection
FSoundscapePaletteCollection NewCollection;
NewCollection.SoundscapePaletteCollection.Add(FSoftObjectPath("/Game/Audio/Palettes/ForestDay"));
NewCollection.SoundscapePaletteCollection.Add(FSoftObjectPath("/Game/Audio/Palettes/ForestNight"));
SoundscapeSubsystem->AddPaletteCollection(FName("ForestCollection"), NewCollection);

// 添加 Color Point Collection（静态位置数据）
FSoundscapeColorPointCollection ColorPointCollection;
FSoundscapeColorPointVectorArray BirdPoints;
BirdPoints.ColorPoint = FGameplayTag::RequestGameplayTag(TEXT("Soundscape.ColorPoint.Bird"));
BirdPoints.Locations.Add(FVector(1000.0f, 500.0f, 0.0f));
BirdPoints.Locations.Add(FVector(-200.0f, 800.0f, 0.0f));
ColorPointCollection.ColorPointCollection.Add(BirdPoints);
SoundscapeSubsystem->AddColorPointCollection(FName("BirdNests"), ColorPointCollection);

// 查询某位置的 Color Point 密度
int32 Density = SoundscapeSubsystem->CheckColorPointDensity(
    FVector(500.0f, 600.0f, 0.0f),
    FGameplayTag::RequestGameplayTag(TEXT("Soundscape.ColorPoint.Bird"))
);

// 手动生成并播放一个 Color
UActiveSoundscapeColor* ActiveColor = nullptr;
USoundscapeBPFunctionLibrary::SpawnSoundscapeColor(World, MySoundscapeColorAsset, ActiveColor);
if (ActiveColor)
{
    ActiveColor->Play(1.0f, 1.0f, 2.0f); // Volume, Pitch, FadeIn
}
```

## Demo 示例

一个完整的最小示例：在 BeginPlay 时设置 Soundscape 状态。

**MyGameMode.h**:

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "MyGameMode.generated.h"

UCLASS()
class AMyGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    virtual void StartPlay() override;
};
```

**MyGameMode.cpp**:

```cpp
#include "MyGameMode.h"
#include "SoundscapeSubsystem.h"
#include "GameplayTagContainer.h"

void AMyGameMode::StartPlay()
{
    Super::StartPlay();

    if (UGameInstance* GameInstance = GetGameInstance())
    {
        if (USoundscapeSubsystem* SoundscapeSubsystem = GameInstance->GetSubsystem<USoundscapeSubsystem>())
        {
            // 设置森林声景状态
            SoundscapeSubsystem->SetState(
                FGameplayTag::RequestGameplayTag(TEXT("Soundscape.Biome.Forest"))
            );
        }
    }
}
```

**Build.cs 依赖**:

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "Soundscape",
    "GameplayTags"
});
```

## 模块依赖

### Runtime 模块（Soundscape）

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、容器、数学库 |
| `CoreUObject` | UObject 系统、反射、序列化 |
| `DeveloperSettings` | `USoundscapeSettings` 的基类，Project Settings 集成 |
| `GameplayTags` | GameplayTag 状态系统，用于 Palette 播放条件和 Color Point 标识 |
| `Engine` | (Private) AudioComponent、World、TimerManager、AssetManager |

### Editor 模块（SoundscapeEditor）

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型 |
| `AssetTools` | 自定义资产类型注册 |
| `Soundscape` | 运行时模块 |
| `AudioMixer` | 音频预览 |
| `UnrealEd` | (Private) 编辑器集成 |
| `Slate` / `SlateCore` | (Private) 编辑器 UI |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-10-01 | `d1f7b3f` | 修复 BeginPlay 时 Palette 更新失败的问题；修复 Color Point 密度计算 + Move By Trace 组合时的问题；修复 debug 绘制框尺寸偏大两倍的问题；修复多个 tooltip 拼写错误 |
| 2024-11-22 | `36771d7` | 统一 uplugin 标记：Experimental 和 Beta 标记共存时，Runtime/Editor 目录下标记为 Beta |
| 2024-08-05 | `fd4a6bf` | 为 Soundscape Palette 添加异步加载功能，避免同步加载导致的帧卡顿 |

### 维护评价

- **创建时间**：2022 年 5 月，约 4 年历史
- **维护状态**：**活跃维护中** — 最近一次更新在 2025 年 10 月，修复了多个实际使用中的 bug
- **Beta 标记**：插件仍标记为 `IsBetaVersion = true`，且 `EnabledByDefault = false`，需要手动启用
- **已知限制**：
  - 不支持分屏（代码中有 `TODO: Handle Split Screen` 注释）
  - Color Point 系统的哈希表有 200 万单位的最大网格宽度限制
  - 没有官方测试用例
- **推荐程度**：**推荐在项目中使用**，但需注意 Beta 状态意味着 API 可能在未来版本发生变化。对于需要程序化环境声的项目，这是 UE5 唯一的内置方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Soundscape)
- 官方文档：无（.uplugin 的 DocsURL 为空）
