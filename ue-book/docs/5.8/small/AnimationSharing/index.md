# Animation Sharing

> Plugin to create Shared Animation systems using the Leader-Follower pose functionality

| 属性 | 值 |
|---|---|
| 中文名 | 动画共享 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产，材质） |
| 模块 | `AnimationSharing` (Runtime), `AnimationSharingEd` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-01-08 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/AnimationSharing) | |

## 用途
AnimationSharing 插件旨在优化大量具有相似动画需求的 Actor 的性能。其核心思想是“领导者-跟随者”（Leader-Follower）机制：从一组需要播放相同或相似动画的 Actor 中，选出一个“领导者”角色执行完整的动画蓝图计算和骨骼网格体更新。组内其他“跟随者”角色则直接共享“领导者”的动画结果（骨骼姿势），从而避免了大量重复的动画蓝图评估、物理模拟等开销。这对于大型人群、军团、背景NPC等场景的性能提升至关重要。

## 使用场景
- 你的游戏有成百上千个士兵、市民或怪物，它们播放着几乎相同的待机、行走或战斗动画。
- 你正在实现一个大型开放世界的人群模拟系统，需要渲染大量背景角色。
- 你希望在远距离或视野内存在大量相似动画对象时，维持稳定的帧率。

## 蓝图用法
动画共享系统的管理主要通过蓝图暴露的类和函数进行。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsAnimationSharingEnabled` | 检查动画共享系统是否已启用 | `UAnimationSharingManager` |
| `GetAnimationSharingManager` | 获取全局的动画共享管理器实例 | `UAnimationSharingManager` |
| `InitializeAnimationSharing` | 根据提供的设置数据初始化动画共享系统 | `UAnimationSharingManager` |
| `RegisterActor` | 将一个 Actor 注册到动画共享系统中，由系统自动管理其动画 | `UAnimationSharingManager` |
| `UnregisterActor` | 从动画共享系统中注销一个 Actor | `UAnimationSharingManager` |
| `GetWorld` | 获取管理器关联的世界对象 | `UAnimationSharingManager` |

### 使用示例（蓝图描述）
1.  **系统初始化**：在游戏模式（GameMode）的初始化事件中，通过 `GetAnimationSharingManager` 节点获取管理器实例，然后调用 `InitializeAnimationSharing` 并传入一个 `UAnimationSharingSetup` 资产（需提前创建）来配置共享规则（例如，哪些骨骼网格体共享动画、分组距离等）。
2.  **角色注册**：在需要参与动画共享的角色蓝图中，可以在 `BeginPlay` 事件里调用 `RegisterActor` 节点，将自身注册到系统中。系统会根据配置和角色位置，自动将其划入某个动画组。
3.  **状态查询**：在调试或需要知道角色当前是否为动画“领导者”时，可以调用 `IsAnimationSharingEnabled` 并结合其他状态查询节点。

## C++ 用法

### 头文件引入
```cpp
#include "AnimationSharingManager.h"
#include "AnimationSharingSetup.h"
```

### 基本用法
从测试用例中提取的初始化和状态查询代码。
```cpp
// 假设在某个 Actor 或 GameMode 中
#include "AnimationSharingManager.h"

void AMyGameMode::InitAnimationSharing()
{
    // 检查系统是否已启用
    UAnimationSharingManager* Manager = UAnimationSharingManager::GetAnimationSharingManager(GetWorld());
    if (Manager && Manager->IsAnimationSharingEnabled())
    {
        UE_LOG(LogTemp, Log, TEXT("Animation Sharing is active."));
    }
}
```
*(来源：基于 Engine/Tests/Runtime/AnimationSharing/ 中的测试用例模式)*

### 进阶用法
更复杂的用法涉及在 C++ 中直接注册和管理 Actor，以及监听动画共享状态变化。
```cpp
// 在 Actor 的初始化或 BeginPlay 中注册
void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();
    UAnimationSharingManager* Manager = UAnimationSharingManager::GetAnimationSharingManager(GetWorld());
    if (Manager)
    {
        Manager->RegisterActor(this, FOnAnimationSharingRegisteredDelegate::CreateUObject(this, &AMyCharacter::OnAnimationSharingRegistered));
    }
}

void AMyCharacter::OnAnimationSharingRegistered(bool bSuccess)
{
    // 注册成功后的回调，可以在此处理一些初始化逻辑
    if (bSuccess)
    {
        // ...
    }
}
```
*(来源：综合 AnimationSharingManager 的公共接口和测试用例逻辑)*

## Demo 示例
一个演示如何在 C++ Actor 中初始化和查询动画共享系统状态的最小示例。

```cpp
// AnimationSharingDemoActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AnimationSharingDemoActor.generated.h"

UCLASS()
class MYPROJECT_API AAnimationSharingDemoActor : public AActor
{
    GENERATED_BODY()
    
public:
    AAnimationSharingDemoActor();

protected:
    virtual void BeginPlay() override;

public:
    virtual void Tick(float DeltaTime) override;

private:
    // 检查并打印动画共享状态
    void CheckAnimationSharingStatus() const;
};
```

```cpp
// AnimationSharingDemoActor.cpp
#include "AnimationSharingDemoActor.h"
#include "AnimationSharingManager.h"

AAnimationSharingDemoActor::AAnimationSharingDemoActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AAnimationSharingDemoActor::BeginPlay()
{
    Super::BeginPlay();
    CheckAnimationSharingStatus();
}

void AAnimationSharingDemoActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
}

void AAnimationSharingDemoActor::CheckAnimationSharingStatus() const
{
    UAnimationSharingManager* Manager = UAnimationSharingManager::GetAnimationSharingManager(GetWorld());
    if (Manager)
    {
        if (Manager->IsAnimationSharingEnabled())
        {
            UE_LOG(LogTemp, Log, TEXT("[%s]: Animation Sharing is ENABLED."), *GetName());
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("[%s]: Animation Sharing is DISABLED."), *GetName());
        }
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("[%s]: Failed to get Animation Sharing Manager."), *GetName());
    }
}
```

## 模块依赖
要使用此插件，你的模块需要依赖：

| 模块 | 用途 |
|---|---|
| `AnimationSharing` | 提供核心的动画共享运行时功能、管理器和蓝图类。 |
| `SignificanceManager` | 用于根据重要性（如距离屏幕中心、距离玩家等）来优化动画更新的调度。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的UE_LOGF格式，不影响功能。 |
| 2025-11-11 | `ca342f27` | Ensure that Additive and Blend components have their LOD forced to 0, otherwise it will be impacted | 修复了加法动画和混合组件的LOD问题，确保动画共享不受影响。 |
| 2025-11-06 | `c51e7614` | Fixed issue with additive instances not taking into account actor running an on-demand state or bein | 修复了当Actor运行按需动画状态时，加法动画实例计算不正确的问题。 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 代码规范修改，将析构函数体改写为=default，不改变功能。 |
| 2025-10-27 | `e5a984c3` | Add per platform option in animsharing for sending curves during blends. | 新增了按平台配置动画共享期间曲线发送的选项，增强了灵活性。 |

### 维护评价
AnimationSharing 插件创建于 2019 年，是一个相对成熟的工具。从近期的 Git 记录来看，它**仍在被 Epic Games 积极维护**，更新内容包括修复 bug（如加法动画、LOD问题）、添加新功能（平台特定曲线选项）以及代码现代化。虽然创建已有约 7 年，但其核心功能对于优化大规模动画角色性能的场景仍然非常有效且必要。**推荐在需要处理大量重复动画角色的项目中使用**。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/AnimationSharing)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Runtime/AnimationSharing)