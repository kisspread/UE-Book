# Soundscape Plugin

> A Dynamic Ambient Sound System（照抄）

| 属性 | 值 |
|---|---|
| 中文名 | 动态环境声景 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `Soundscape` (Runtime), `SoundscapeEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-05-27 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Soundscape) | |

## 用途

Soundscape 是一个基于状态驱动和空间感知的动态环境音系统。它解决的核心问题是：**如何根据游戏状态（GameplayTag）和玩家在世界中的位置，自动、动态地混合和播放环境音效层**。

与传统的环境音方案（手动放置 Ambient Sound Actor 或编写大量脚本控制音效切换）不同，Soundscape 提供了一套数据驱动的管线：

1. **调色板（Palette）**：定义一组声音"颜色"，并通过 GameplayTagQuery 条件控制何时播放。例如"森林白天"调色板包含鸟鸣、风声、树叶沙沙声。
2. **颜色（Color）**：单个声音的完整定义，包含空间化生成规则（距离、角度、高度限制）、调制行为（音量/音高随机化）、播放行为（淡入淡出、循环限制）。
3. **色彩点（ColorPoint）**：放置在世界中的空间标记点，带有 GameplayTag，用于构建空间密度热力图，影响声音的生成位置和密度过滤。
4. **子系统（Subsystem）**：作为 GameInstance 子系统管理整个生命周期，支持动态切换调色板集合和色彩点集合。

本质上，Soundscape 将环境音设计从"放在哪里播什么"提升到"在什么状态下、周围有什么特征时，自动在合理位置生成合适的声音"。

## 使用场景

- 你在做一个开放世界游戏，需要在森林、沙漠、城镇等不同区域自动切换环境音层 → 用 Soundscape Palette + State 条件
- 你需要鸟叫声、虫鸣声在玩家周围随机位置自然地响起，而不是固定点循环播放 → 用 Soundscape Color 的 SpawnBehavior
- 你希望声音只在特定密度区域生成（例如鸟叫声只在树木密集的地方出现）→ 用 ColorPoint 系统做密度过滤
- 你需要环境音在不同天气/时间状态下平滑过渡 → 用 SetState/ClearState 切换调色板
- 你希望声音有自然的随机变化（音高微调、音量波动、位置偏移）→ 用 ColorModulationSettings

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetState` | 设置 Soundscape 状态标签，触发匹配调色板的加载和播放 | `USoundscapeSubsystem` |
| `ClearState` | 清除指定状态标签 | `USoundscapeSubsystem` |
| `RestartSoundscape` | 重启整个 Soundscape 系统 | `USoundscapeSubsystem` |
| `AddPaletteCollection` | 添加一组调色板资源到子系统 | `USoundscapeSubsystem` |
| `RemovePaletteCollection` | 移除调色板集合 | `USoundscapeSubsystem` |
| `AddColorPointCollection` | 添加色彩点集合（空间密度数据） | `USoundscapeSubsystem` |
| `RemoveColorPointCollection` | 移除色彩点集合 | `USoundscapeSubsystem` |
| `CheckColorPointDensity` | 查询指定位置的色彩点密度 | `USoundscapeSubsystem` |
| `SpawnSoundscapeColor` | 生成一个 Color 播放代理（不自动播放） | `USoundscapeBPFunctionLibrary` |
| `SpawnSoundscapePalette` | 生成一个完整的 Palette 播放代理 | `USoundscapeBPFunctionLibrary` |
| `Play` | 播放一个已激活的 Soundscape Color | `UActiveSoundscapeColor` |
| `Stop` | 停止播放一个已激活的 Soundscape Color | `UActiveSoundscapeColor` |
| `IsPlaying` | 检查是否正在播放 | `UActiveSoundscapeColor` |

### 使用示例

**场景：基于游戏状态切换环境音**

1. 创建 `SoundscapePalette` 资产，设置 `SoundscapePalettePlaybackConditions`（如 `State.Day AND Zone.Forest`），添加多个 `SoundscapePaletteColor` 条目引用不同的 `SoundscapeColor` 资产。
2. 创建 `SoundscapeColor` 资产，配置 Sound 引用、SpawnBehavior（距离范围、角度范围、最大并发数）、ModulationBehavior（音量/音高随机化）。
3. 在 Project Settings → Soundscape 中将 Palette 添加到 `SoundscapePaletteCollection`。
4. 在游戏蓝图中，调用 `Get Game Instance Subsystem → Soundscape Subsystem → Set State` 传入 GameplayTag（如 `State.Night`），系统自动加载匹配条件的 Palette 并开始播放环境音。

**场景：手动控制单个声音**

1. 调用 `SpawnSoundscapeColor` 传入 `SoundscapeColor` 资产，获得 `ActiveSoundscapeColor` 引用。
2. 调用 `ActiveSoundscapeColor → Play` 开始播放，支持自定义音量、音高、淡入时间。
3. 调用 `ActiveSoundscapeColor → Stop` 停止播放，支持自定义淡出时间。

**场景：空间密度影响声音生成**

1. 在世界中放置带有 `SoundscapeColorPointComponent` 的 Actor，设置 `ColorPoint` 标签（如 `Vegetation.Dense`）。
2. 在 Color 资产的 SpawnBehavior 中启用 `bFilterByColorPointDensity`，设置 `ColorPoint` 和 `MinColorPointNumber`。
3. 声音只会在色彩点密度满足阈值的位置生成。

## C++ 用法

### 头文件引入

```cpp
#include "SoundscapeSubsystem.h"
#include "SoundscapeColor.h"
#include "SoundScapePalette.h"
#include "SoundscapeColorPoint.h"
#include "SoundScape.h"
```

### 基本用法：通过子系统管理环境音状态

```cpp
// 获取 Soundscape 子系统
USoundscapeSubsystem* SoundscapeSubsystem = GetGameInstance()->GetSubsystem<USoundscapeSubsystem>();

// 添加调色板集合（从 Settings 中配置的软引用）
FSoundscapePaletteCollection PaletteCollection;
PaletteCollection.SoundscapePaletteCollection.Add(FSoftObjectPath("/Game/Audio/Soundscape/BP_ForestPalette.BP_ForestPalette"));
PaletteCollection.SoundscapePaletteCollection.Add(FSoftObjectPath("/Game/Audio/Soundscape/BP_CityPalette.BP_CityPalette"));
SoundscapeSubsystem->AddPaletteCollection(FName("DefaultPalettes"), PaletteCollection);

// 设置状态，触发匹配的 Palette 加载和播放
FGameplayTag ForestTag = FGameplayTag::RequestGameplayTag(FName("Zone.Forest"));
SoundscapeSubsystem->SetState(ForestTag);

// 清除状态
SoundscapeSubsystem->ClearState(ForestTag);

// 重启系统
SoundscapeSubsystem->RestartSoundscape();
```

### 基本用法：手动生成和控制 Color

```cpp
#include "SoundScape.h"

// 生成一个 ActiveSoundscapeColor 代理
USoundscapeColor* MyColor = LoadObject<USoundscapeColor>(nullptr, TEXT("/Game/Audio/Soundscape/BP_BirdChirp.BP_BirdChirp"));
UActiveSoundscapeColor* ActiveColor = nullptr;
bool bSuccess = USoundscapeBPFunctionLibrary::SpawnSoundscapeColor(GetWorld(), MyColor, ActiveColor);

if (bSuccess && ActiveColor)
{
    // 开始播放：自定义音量 0.8、音高 1.0、淡入 2 秒
    ActiveColor->Play(0.8f, 1.0f, 2.0f);
    
    // 检查播放状态
    if (ActiveColor->IsPlaying())
    {
        // 停止播放，淡出 3 秒
        ActiveColor->Stop(3.0f);
    }
}
```

### 进阶用法：色彩点空间密度系统

```cpp
// 添加色彩点集合
FSoundscapeColorPointCollection PointCollection;

FSoundscapeColorPointVectorArray TreePoints;
TreePoints.ColorPoint = FGameplayTag::RequestGameplayTag(FName("Vegetation.Trees"));
TreePoints.Locations = { FVector(1000, 2000, 0), FVector(1200, 2100, 0), FVector(800, 1900, 0) };
PointCollection.ColorPointCollection.Add(TreePoints);

SoundscapeSubsystem->AddColorPointCollection(FName("ForestVegetation"), PointCollection);

// 查询某位置的色彩点密度
FGameplayTag TreeTag = FGameplayTag::RequestGameplayTag(FName("Vegetation.Trees"));
FVector PlayerLocation = GetPawn()->GetActorLocation();
int32 Density = SoundscapeSubsystem->CheckColorPointDensity(PlayerLocation, TreeTag);

if (Density > 0)
{
    UE_LOG(LogTemp, Log, TEXT("Player is in a dense tree area, density: %d"), Density);
}
```

## Demo 示例

### 头文件

```cpp
// SoundscapeDemoComponent.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "GameplayTagContainer.h"
#include "SoundscapeDemoComponent.generated.h"

class USoundscapeSubsystem;
class UActiveSoundscapeColor;
class USoundscapeColor;

UCLASS(ClassGroup = (Audio), meta = (BlueprintSpawnableComponent))
class YOURPROJECT_API USoundscapeDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    USoundscapeDemoComponent();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    // 在蓝图中设置要使用的 SoundscapeColor 资产
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Soundscape Demo")
    TObjectPtr<USoundscapeColor> DemoColor;

    // 状态标签
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Soundscape Demo")
    FGameplayTag DemoStateTag;

    // 手动播放/停止
    UFUNCTION(BlueprintCallable, Category = "Soundscape Demo")
    void StartDemoSound();

    UFUNCTION(BlueprintCallable, Category = "Soundscape Demo")
    void StopDemoSound();

    UFUNCTION(BlueprintCallable, Category = "Soundscape Demo")
    void ActivateSoundscapeState();

    UFUNCTION(BlueprintCallable, Category = "Soundscape Demo")
    void DeactivateSoundscapeState();

private:
    UPROPERTY()
    TObjectPtr<UActiveSoundscapeColor> ActiveDemoColor;
};
```

### 实现文件

```cpp
// SoundscapeDemoComponent.cpp
#include "SoundscapeDemoComponent.h"
#include "SoundscapeSubsystem.h"
#include "SoundScape.h"
#include "SoundScapePalette.h"
#include "Engine/GameInstance.h"

USoundscapeDemoComponent::USoundscapeDemoComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void USoundscapeDemoComponent::BeginPlay()
{
    Super::BeginPlay();
}

void USoundscapeDemoComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (ActiveDemoColor)
    {
        ActiveDemoColor->Stop(0.0f);
    }
    Super::EndPlay(EndPlayReason);
}

void USoundscapeDemoComponent::StartDemoSound()
{
    if (!DemoColor)
    {
        UE_LOG(LogTemp, Warning, TEXT("SoundscapeDemo: No DemoColor asset assigned."));
        return;
    }

    // 使用蓝图函数库生成代理
    bool bSuccess = USoundscapeBPFunctionLibrary::SpawnSoundscapeColor(
        GetWorld(), DemoColor, ActiveDemoColor);

    if (bSuccess && ActiveDemoColor)
    {
        ActiveDemoColor->Play(1.0f, 1.0f, 1.0f);
    }
}

void USoundscapeDemoComponent::StopDemoSound()
{
    if (ActiveDemoColor && ActiveDemoColor->IsPlaying())
    {
        ActiveDemoColor->Stop(2.0f);
    }
}

void USoundscapeDemoComponent::ActivateSoundscapeState()
{
    USoundscapeSubsystem* Subsystem = GetWorld()->GetGameInstance()->GetSubsystem<USoundscapeSubsystem>();
    if (Subsystem && DemoStateTag.IsValid())
    {
        Subsystem->SetState(DemoStateTag);
    }
}

void USoundscapeDemoComponent::DeactivateSoundscapeState()
{
    USoundscapeSubsystem* Subsystem = GetWorld()->GetGameInstance()->GetSubsystem<USoundscapeSubsystem>();
    if (Subsystem && DemoStateTag.IsValid())
    {
        Subsystem->ClearState(DemoStateTag);
    }
}
```

## 模块依赖

从 `Soundscape.Build.cs` 分析，使用者需要注意以下独特依赖：

| 模块 | 用途 |
|---|---|
| `GameplayTags` | 整个系统的核心标识机制，Palette 条件、ColorPoint 标签均基于此 |
| `GameplayAbilities` | Palette 播放条件使用 GameplayTagQuery，依赖此模块的查询功能 |

无其他特殊依赖（仅标准 Core/Engine/AudioMixer 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 内容浏览器新增音频菜单项，与 Soundscape 间接相关 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF | 将 UE_LOG 迁移到 UE_LOGF 宏，日志系统更新 |
| 2025-10-01 | `714456fa` | [Soundscape] Fixes | Soundscape 相关的 Bug 修复 |
| 2024-11-22 | `36771d79` | Updated uplugin descriptor files marked as both Experimental and Beta. Plugins with both flags in uplugin descriptor files... | 更新同时标记为 Experimental 和 Beta 的插件描述文件 |
| 2024-08-05 | `fd4a6bf8` | [Soundscape] Adding Asynchronous Loading to Soundscape Palettes | 为 Soundscape Palette 添加异步加载支持，减少加载卡顿 |

### 维护评价

Soundscape 插件于 2022 年由 Epic Games 创建，距今约 3 年。核心功能在创建初期已基本完成，后续更新以修复和优化为主。值得注意的是：

- **仍处于 Beta 阶段**（`IsBetaVersion=true`），且默认未启用（`EnabledByDefault=false`），API 可能在未来版本发生变化
- 最近的实质性功能更新是 2024-08-05 的异步加载支持，2025-10-01 有修复提交
- 近期更新（2026-04）属于工具链层面的间接改动，非功能增强
- 空间密度系统（ColorPoint + Hash Map）设计较为完善，支持 LOD 分级查询
- 作为 Epic 官方维护的插件，质量有保障，适合在需要动态环境音的项目中试用

**建议**：可用于原型和实验性项目，生产环境使用需注意 Beta 标签意味着未来可能有 Breaking Changes。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Soundscape)
- 官方文档：无（DocsURL 为空）