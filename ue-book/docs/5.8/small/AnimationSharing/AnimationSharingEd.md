# Animation Sharing

> Plugin to create Shared Animation systems using the Leader-Follower pose functionality

| 属性 | 值 |
|---|---|
| 中文名 | 动画共享 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（资产类型、材质模板） |
| 模块 | `AnimationSharing` (Runtime), `AnimationSharingEd` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-01-08 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/AnimationSharing) | |

## 用途

该插件旨在优化大量角色（如群体、NPC大军）的动画性能。其核心思想是“Leader-Follower”（领导-跟随）模式：在一个角色组中，只选择一个或几个角色（Leader）执行完整的、昂贵的骨骼动画计算。组内其他角色（Follower）则通过复制 Leader 计算出的最终骨骼姿态（Pose）来更新自身，避免了重复的动画蓝图、状态机、物理等计算。这种方法能显著降低CPU开销，尤其适用于角色外观相似且动画需求一致的场景。

## 使用场景

- **游戏中的大规模群体**：例如僵尸群、士兵方阵、观众席人群，这些角色通常播放相同的行走、待机动画，但不需要独立的动画控制逻辑。
- **优化动画蓝图复杂角色的性能**：当动画蓝图逻辑（如复杂的状态机、IK、物理）非常耗性能时，可以将大部分角色设置为Follower，共享少数Leader的计算结果。
- **制作过场动画中庞大的角色队列**：确保队列中角色的动画同步且高效。

## 蓝图用法

插件的核心逻辑通过 `UAnimationSharingManager` 管理，并暴露了蓝图功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddActorsToGroup` | 将一组Actor添加到指定的动画共享组中，开始参与动画共享。 | `UAnimationSharingManager` |
| `RemoveActorsFromGroup` | 将一组Actor从其所在的动画共享组中移除。 | `UAnimationSharingManager` |
| `GetAnimationSharingManager` | 获取当前世界的动画共享管理器单例。 | `UAnimationSharingSubsystem` |
| `SetAnimationSharingEnabled` | 启用或禁用整个动画共享系统。 | `UAnimationSharingManager` |
| `IsAnimationSharingEnabled` | 查询动画共享系统是否启用。 | `UAnimationSharingManager` |
| `GetAnimationStateForGroup` | 查询特定组当前的动画状态索引。 | `UAnimationSharingManager` |

### 使用示例（蓝图描述）

1.  **配置阶段**：在项目设置或世界中放置一个 `UAnimationSharingSetup` 资产，配置好骨骼、动画状态和每个状态的处理器（例如，指定哪些动画用于Leader，哪些角色被选为Leader的概率）。
2.  **初始化**：游戏开始时，通过 `GetAnimationSharingManager` 获取管理器，通常由子系统自动初始化。
3.  **运行时添加角色**：在生成大量需要共享动画的角色（如敌人）后，调用 `AddActorsToGroup` 节点，将这些角色的Actor引用数组传入，并指定它们所属的组（基于 `UAnimationSharingSetup` 中的配置）。
4.  **（可选）移除角色**：当某个角色被销毁或需要独立动画时，调用 `RemoveActorsFromGroup` 将其移除。

## C++ 用法

### 头文件引入

```cpp
#include "AnimationSharingManager.h"
```

### 基本用法

获取管理器并添加角色到组。

```cpp
// 获取动画共享管理器
UAnimationSharingManager* AnimSharingManager = UAnimationSharingManager::GetAnimSharingManager(GetWorld());

if (AnimSharingManager)
{
    // 创建一个包含要共享动画的Actor的数组
    TArray<AActor*> ActorsToAdd;
    ActorsToAdd.Add(MyCharacter1);
    ActorsToAdd.Add(MyCharacter2);
    // ... 更多角色

    // 将它们添加到基于UAnimationSharingSetup配置的组中
    // 组索引通常根据角色的骨骼、动画状态等自动确定或通过配置指定
    AnimSharingManager->AddActorsToGroup(ActorsToAdd);
}
```

### 进阶用法

动态移除角色并查询状态。

```cpp
// 移除单个角色
if (AnimSharingManager)
{
    TArray<AActor*> ActorsToRemove;
    ActorsToRemove.Add(MyCharacter1);
    AnimSharingManager->RemoveActorsFromGroup(ActorsToRemove);
}

// 查询某个组的动画状态（可用于UI显示或调试）
int32 GroupIndex = 0;
int32 StateIndex = AnimSharingManager->GetAnimationStateForGroup(GroupIndex);
```

## Demo 示例

**AnimationSharingTest.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AnimationSharingTest.generated.h"

UCLASS()
class MYPROJECT_API AAnimationSharingTest : public AActor
{
    GENERATED_BODY()
    
public:    
    AAnimationSharingTest();

    virtual void BeginPlay() override;

    // 用于测试添加和移除的函数
    UFUNCTION(BlueprintCallable, Category = "Animation Sharing Test")
    void AddCharactersToSharing();

    UFUNCTION(BlueprintCallable, Category = "Animation Sharing Test")
    void RemoveCharacterFromSharing();

private:
    UPROPERTY()
    TArray<AActor*> MyCharacters;
};
```

**AnimationSharingTest.cpp**
```cpp
#include "AnimationSharingTest.h"
#include "AnimationSharingManager.h"
#include "Engine/World.h"

AAnimationSharingTest::AAnimationSharingTest()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AAnimationSharingTest::BeginPlay()
{
    Super::BeginPlay();
    // 在BeginPlay中生成一些角色并添加到MyCharacters数组（生成逻辑略）
}

void AAnimationSharingTest::AddCharactersToSharing()
{
    if (UAnimationSharingManager* Manager = UAnimationSharingManager::GetAnimSharingManager(GetWorld()))
    {
        Manager->AddActorsToGroup(MyCharacters);
        UE_LOG(LogTemp, Log, TEXT("Added %d characters to animation sharing."), MyCharacters.Num());
    }
}

void AAnimationSharingTest::RemoveCharacterFromSharing()
{
    if (MyCharacters.Num() > 0 && UAnimationSharingManager::GetAnimSharingManager(GetWorld()))
    {
        TArray<AActor*> RemoveArray;
        RemoveArray.Add(MyCharacters[0]);
        UAnimationSharingManager::GetAnimSharingManager(GetWorld())->RemoveActorsFromGroup(RemoveArray);
        UE_LOG(LogTemp, Log, TEXT("Removed 1 character from animation sharing."));
    }
}
```

## 模块依赖

`AnimationSharing` 模块的 `Build.cs` 中依赖了 `TargetPlatform`，这是一个常见依赖，通常无需特别说明。

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新的UE_LOGF格式。 |
| 2025-11-11 | `ca342f27` | Ensure that Additive and Blend components have their LOD forced to 0, otherwise it will be impacted | 确保加法与混合组件的LOD强制为0，以防止被错误裁剪。 |
| 2025-11-06 | `c51e7614` | Fixed issue with additive instances not taking into account actor running an on-demand state or being | 修复了加法动画实例未考虑Actor运行按需状态或处于…的问题。 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 代码风格修正，将所有析构函数从`~Type() {}`改为`= default`。 |
| 2025-10-27 | `e5a984c3` | Add per platform option in animsharing for sending curves during blends. | 为动画共享添加了平台级选项，以控制在混合期间是否发送曲线数据。 |

### 维护评价

该插件创建于2019年，已有约6年历史。从近期提交记录看（最后几次更新在2025年底至2026年初），**它仍在被维护**，但更新频率较低，主要集中在bug修复、代码风格更新和特定平台的功能微调上。没有迹象表明它已被废弃。考虑到其针对特定优化场景（大规模群体动画）的功能完整性，对于有明确需求的项目来说，它仍然是一个**可推荐使用的稳定工具**。但开发者应意识到，其功能相对单一，且动画共享是一种高级优化手段，使用前需对性能瓶颈有清晰认识。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/AnimationSharing)
- [官方文档]() （.uplugin中未提供DocsURL）
- [测试用例]() （未在常规测试路径中发现专门针对此插件的自动化测试）