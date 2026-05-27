# Media Profile

> This plugin contains the Media Profile asset and related entities, which help manage media sources and outputs

| 属性 | 值 |
|---|---|
| 中文名 | 媒体配置 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（媒体资产） |
| 模块 | `MediaProfile` (Runtime), `MediaProfileEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaProfile) | |

## 用途
该插件提供了 `UMediaProfile` 资产及相关的管理和代理类，其核心目的是将媒体配置（媒体源、输出等）从 `OpenCVDistortion` 等插件中解耦并独立出来。它允许开发者集中管理和复用复杂的媒体输入/输出设置，而无需在每个使用媒体的模块中重复定义，简化了媒体工作流的配置与维护。

## 使用场景
- 当你需要为虚拟制片、广播或录制项目统一管理多个摄像机源（如 AJA, Blackmagic）和输出目标时。
- 当你在项目中频繁使用媒体框架，且需要在不同场景或关卡间共享和切换相同的媒体配置时。
- 当你希望避免 `MediaProfile` 功能与其他特定媒体处理插件（如计算机视觉）产生不必要的模块依赖时。

## 蓝图用法

### 核心节点
| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateMediaProfileAsset` | 创建一个媒体配置资产 | `UMediaProfileSubsystem` |
| `GetMediaProfile` | 获取当前的媒体配置资产 | `UMediaProfileSubsystem` |
| `ApplyMediaProfile` | 应用指定的媒体配置 | `UMediaProfileSubsystem` |
| `GetMediaSourceProxy` | 根据配置获取对应的媒体源代理 | `UMediaProfile` |
| `GetMediaOutputProxy` | 根据配置获取对应的媒体输出代理 | `UMediaProfile` |

### 使用示例（蓝图描述）
1.  在关卡蓝图或任意 Actor 中，使用 “Get Game Instance” 节点获取游戏实例，再调用 “Get Subsystem” 获取 `UMediaProfileSubsystem`。
2.  调用 `CreateMediaProfileAsset` 节点，可指定资产名称和路径，创建一个新的配置资产。
3.  或者，使用 `GetMediaProfile` 节点加载一个已存在的媒体配置资产。
4.  调用 `ApplyMediaProfile` 节点，将选中的媒体配置应用到当前场景，所有引用该配置的媒体播放器/捕获器将自动使用其关联的源和输出设置。

## C++ 用法

### 头文件引入
```cpp
#include "MediaProfileSubsystem.h"
#include "MediaProfile.h"
```

### 基本用法
```cpp
// 来自 MediaProfileSubsystem.h
UMediaProfileSubsystem* MediaProfileSubsystem = GetWorld()->GetGameInstance()->GetSubsystem<UMediaProfileSubsystem>();
if (MediaProfileSubsystem)
{
    // 创建一个新的媒体配置资产
    UMediaProfile* NewProfile = MediaProfileSubsystem->CreateMediaProfileAsset(TEXT("MyNewProfile"), TEXT("/Game/Media/Profiles"));
    
    // 应用该配置
    MediaProfileSubsystem->ApplyMediaProfile(NewProfile);
    
    // 或者获取当前活动的配置
    UMediaProfile* CurrentProfile = MediaProfileSubsystem->GetMediaProfile();
}
```

### 进阶用法
```cpp
// 来自 MediaProfile.h
UMediaProfile* Profile = ...; // 获取或创建的媒体配置资产

// 遍历并获取配置中的媒体源代理
for (const FMediaProfileMediaSourceProxy& SourceProxy : Profile->GetMediaSourceProxies())
{
    // SourceProxy.SourceName, SourceProxy.MediaSource 是主要数据
    UE_LOG(LogTemp, Log, TEXT("配置中的媒体源: %s"), *SourceProxy.SourceName.ToString());
}

// 获取特定输出代理
FMediaProfileMediaOutputProxy* OutputProxy = Profile->GetMediaOutputProxy(FName(TEXT("LiveOutput")));
if (OutputProxy)
{
    // 使用 OutputProxy->MediaOutput 进行进一步配置
}
```

## Demo 示例

**MediaProfileDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaProfileDemo.generated.h"

UCLASS()
class AMyMediaProfileActor : public AActor
{
    GENERATED_BODY()
public:
    AMyMediaProfileActor();
    
    UFUNCTION(BlueprintCallable)
    void SetupAndApplyMediaProfile();
};
```

**MediaProfileDemo.cpp**
```cpp
#include "MediaProfileDemo.h"
#include "MediaProfileSubsystem.h"
#include "MediaProfile.h"

AMyMediaProfileActor::AMyMediaProfileActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMediaProfileActor::SetupAndApplyMediaProfile()
{
    UGameInstance* GI = GetGameInstance();
    if (!GI) return;

    UMediaProfileSubsystem* Subsystem = GI->GetSubsystem<UMediaProfileSubsystem>();
    if (!Subsystem) return;

    // 创建一个临时的媒体配置资产
    UMediaProfile* TempProfile = Subsystem->CreateMediaProfileAsset(TEXT("TempDemoProfile"), TEXT("/Game/Transient"));
    if (TempProfile)
    {
        // 在这里可以进一步编辑 TempProfile，例如添加源代理和输出代理
        
        // 应用该配置
        Subsystem->ApplyMediaProfile(TempProfile);
        
        UE_LOG(LogTemp, Log, TEXT("已应用临时媒体配置: %s"), *TempProfile->GetName());
    }
}
```

## 模块依赖
无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `ff9996e8` | Media Profile: Fixed issue where ElectraProtron issue would not play a new video after it had alread | 修复了 ElectraProtron 在已播放后无法播放新视频的问题 |
| 2026-05-20 | `54cbb9f8` | Ensure a transient MediaProfile always exists from startup | 确保启动时始终存在一个临时的媒体配置 |
| 2026-05-20 | `de6434f1` | Composure: Add final new icons for composite actors, layers, and passes, and minor tweaks to menu co | （Composure插件更新，与本插件无关） |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | （Viewport插件重构，与本插件无关） |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回滚了某个更改 |

### 维护评价
该插件**非常新**，创建于近期，并且**仍在活跃维护**中。最近几周内有多次实质性提交，主要聚焦于功能完善（如保证临时配置存在）和关键bug修复（如播放问题）。尽管被标记为实验性且默认未启用，但其近期的更新频率和内容表明它是一个正在积极开发和完善的组件。推荐在需要集中管理媒体配置的项目中尝试使用，但需注意其“实验性”状态可能意味着未来API或功能存在变动。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaProfile)
- 测试用例：未在插件目录内发现独立的测试文件。