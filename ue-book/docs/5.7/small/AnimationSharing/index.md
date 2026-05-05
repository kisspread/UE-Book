# Animation Sharing

> Plugin to create Shared Animation systems using the Leader-Follower pose functionality

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | true |
| 包含内容 | true（含 AnimSharingBase、AnimSharingRed 资产） |
| 模块 | AnimationSharing (Runtime, PreDefault), AnimationSharingEd (Editor, Default) |
| 创建时间 | 2019-01-08 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/AnimationSharing) | |

## 用途

AnimationSharing 是一个动画性能优化插件，核心思想是 **Leader-Follower（主-从）动画驱动**。

在大型场景中（如数百个同类型 NPC），每个角色独立播放动画会消耗大量 CPU 和骨骼求值资源。AnimationSharing 的做法是：将同类型角色分组，每组只由一个 "Leader" 组件实际驱动骨骼动画，其余 "Follower" 组件直接复用 Leader 的骨骼姿态（通过 `LeaderPoseComponent` 机制）。这样可以大幅减少实际运行的动画蓝图实例数量。

插件还支持：
- **按状态分组**：根据用户定义的枚举值（如 Idle、Walk、Run 等）将角色分配到不同的动画组件池
- **状态间混合过渡**：当角色从一个状态切换到另一个状态时，自动创建混合 Actor 来平滑过渡
- **On-Demand 动画**：对不常播放的状态（如死亡、受击），按需创建动画实例而非常驻
- **叠加动画（Additive）**：支持在基础状态上叠加播放额外的动画
- **Significance 集成**：与 SignificanceManager 联动，根据角色重要性动态调整混合质量和 tick 行为
- **平台级可伸缩性设置**：每个平台可独立配置最大并发混合数、混合开关等

## 使用场景

- 你有一个开放世界游戏，场景中有数百个同类型的 NPC（如市民、士兵），需要优化动画性能 → 用 AnimationSharing
- 你正在做一个大规模战斗场景，大量敌人使用相同的骨骼和动画 → 用 AnimationSharing
- 你需要根据角色重要性（距离、屏幕占比）动态降低远处角色的动画质量 → 用 AnimationSharing + SignificanceManager

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Animation Sharing Manager` | 使用指定 Setup 资产创建并初始化共享管理器 | `UAnimationSharingManager` |
| `Get Animation Sharing Manager` | 获取当前世界的 AnimationSharingManager 实例 | `UAnimationSharingManager` |
| `Register Actor` | 将一个 Actor 注册到动画共享系统（按指定 Skeleton 匹配） | `UAnimationSharingManager` |
| `Animation Sharing Enabled` | 查询动画共享是否当前处于启用状态 | `UAnimationSharingManager` |

### 状态处理器（蓝图子类化）

`UAnimationSharingStateProcessor` 是一个 **Blueprintable** 类，你需要创建它的蓝图子类来定义角色状态判定逻辑：

- `ProcessActorState`：每帧为每个注册的 Actor 确定当前动画状态枚举值
- `GetAnimationStateEnum`：返回你定义的状态枚举类（如 `EAnimSharingState::Idle`）

### 使用示例（蓝图描述）

1. **创建 Setup 资产**：在 Content Browser 右键 → Animation → Animation Sharing Setup
2. **配置 Setup 资产**：
   - 在 `SkeletonSetups` 数组中添加条目，指定目标 Skeleton 和 SkeletalMesh
   - 为每个条目配置 `AnimationStates`，每个状态指定枚举值、动画序列、是否 On-Demand 等
   - 指定 `StateProcessorClass` 为你的蓝图状态处理器
   - 指定 `BlendAnimBlueprint` 和 `AdditiveAnimBlueprint`
3. **初始化**：在 GameMode 或 GameState 的 BeginPlay 中，调用 `Create Animation Sharing Manager` 节点，传入 Setup 资产
4. **注册角色**：在每个需要共享动画的 Actor 的 BeginPlay 中，调用 `Register Actor` 节点

## C++ 用法

### 头文件引入

```cpp
#include "AnimationSharingManager.h"
#include "AnimationSharingSetup.h"
#include "AnimationSharingModule.h"
```

### 基本用法

创建管理器并注册 Actor（基于 `AnimationSharingManager.h` 中的公共 API）：

```cpp
// 1. 创建 AnimationSharingManager（通常在 GameMode/GameState 中）
const UAnimationSharingSetup* Setup = LoadObject<UAnimationSharingSetup>(nullptr, TEXT("/Game/MyAnimSharingSetup"));
UAnimationSharingManager* Manager = UAnimationSharingManager::CreateAnimationSharingManager(GetWorld(), Setup);

// 2. 在 Actor 中注册
UAnimationSharingManager* Manager = UAnimationSharingManager::GetAnimationSharingManager(this);
if (Manager)
{
    Manager->RegisterActorWithSkeletonBP(this, MySkeleton);
}

// 3. 查询是否启用
bool bEnabled = UAnimationSharingManager::AnimationSharingEnabled();
```

### 自定义状态处理器（C++）

```cpp
#include "AnimationSharingTypes.h"

UCLASS()
class UMyAnimStateProcessor : public UAnimationSharingStateProcessor
{
    GENERATED_BODY()
public:
    // 重写状态判定逻辑
    virtual void ProcessActorState_Internal(int32& OutState, AActor* InActor, uint8 CurrentState, uint8 OnDemandState, bool& bShouldProcess) override
    {
        // 根据角色的移动速度等判断当前动画状态
        // OutState = (int32)EMyAnimState::Run;
        // bShouldProcess = true;
    }
};
```

### 进阶用法

通过模块事件监听管理器生命周期：

```cpp
#include "AnimationSharingModule.h"

// 监听管理器创建事件
FAnimSharingModule::GetOnAnimationSharingManagerCreated().AddLambda(
    [](UAnimationSharingManager* Manager, const UWorld* World)
    {
        // 在管理器创建后执行额外逻辑
    });

// C++ 端直接注册（带 Handle 更新回调）
Manager->RegisterActor(MyActor, FUpdateActorHandle::CreateLambda(
    [](int32 NewHandle)
    {
        // Actor 被重新分配时更新 handle
    }));
```

## Demo 示例

### 最小可运行示例

**MyAnimSharingGameState.h**
```cpp
#pragma once
#include "GameFramework/GameStateBase.h"
#include "MyAnimSharingGameState.generated.h"

UCLASS()
class AMyAnimSharingGameState : public AGameStateBase
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;

    UPROPERTY(EditDefaultsOnly, Category = "Animation")
    TObjectPtr<UAnimationSharingSetup> SharingSetup;
};
```

**MyAnimSharingGameState.cpp**
```cpp
#include "MyAnimSharingGameState.h"
#include "AnimationSharingManager.h"

void AMyAnimSharingGameState::BeginPlay()
{
    Super::BeginPlay();

    if (SharingSetup)
    {
        UAnimationSharingManager::CreateAnimationSharingManager(GetWorld(), SharingSetup);
    }
}
```

**Build.cs 依赖**：
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "AnimationSharing"  // 需要添加此依赖
});
```

> 注意：AnimationSharing 的 Build.cs 中所有依赖均为 `PrivateDependencyModuleNames`，但使用者仍需在自己的 Build.cs 中显式添加 `AnimationSharing` 模块依赖。

## 模块依赖

### AnimationSharing（Runtime）

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（SkeletalMeshComponent、World 等） |
| `SignificanceManager` | 角色重要性评估，决定混合质量和 tick 策略 |

### AnimationSharingEd（Editor）

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库 |
| `CoreUObject` | UObject 系统 |
| `UnrealEd` | 编辑器框架 |
| `AssetTools` | 自定义资产类型注册 |
| `AnimationSharing` | Runtime 模块依赖 |
| `Slate` / `SlateCore` | 自定义 Details 面板 |
| `PropertyEditor` | 属性编辑器自定义 |

### Plugin 依赖

| Plugin | 用途 |
|---|---|
| `SignificanceManager` | 必须启用，提供角色重要性评估 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-09-24 | `4332746b` | PermutationTimeOffset requiring InitAnim for AnimSharing instances | Bug 修复：在 AnimSharing 实例初始化后调用 InitAnim，确保属性值正确更新（UE-298244） |
| 2025-09-12 | `5636743b` | Fix for incorrect use of skeletonIndex rather than skeletonID in UnregisterActor | Bug 修复：修复注销 Actor 时 skeletonIndex 和 skeletonID 混淆的问题 |
| 2025-09-11 | `168408af` | AnimationSharingManager can now create sharing instances from multiple AnimationSharingSetups | 功能更新：支持多个 AnimationSharingSetup、运行时动态添加/移除 Setup、异步加载支持（从 37.50 分支合并） |

### 维护评价

- **创建时间**：2019 年 1 月，已运行超过 7 年
- **最近活跃度**：2025 年 9 月有密集的功能更新和 bug 修复（3 次提交），表明仍在活跃维护
- **维护状态**：**活跃维护** — 最近有实质性功能更新（多 Setup 支持、运行时动态管理）
- **已知限制**：
  - 所有共享同一状态的角色必须使用相同 Skeleton
  - On-Demand 状态的并发实例数有限制，超出时使用 "Wiggle" 机制复用
  - 没有官方测试用例（Engine/Tests/ 下未找到相关测试）
- **是否推荐使用**：**推荐** — 这是 Epic 官方的大规模动画优化方案，在 Fortnite 等大型项目中已验证（commit 中提到 FortGameStateAthena）。如果你的场景有大量同骨骼角色，这是首选方案。

## 调试命令

| 控制台命令 | 说明 |
|---|---|
| `a.Sharing.DebugStates 1` | 开启调试可视化：Leader 组件材质着色、角色状态文字 |
| `a.Sharing.DebugStates 2` | 额外显示动画状态信息、Follower→Leader 连线 |
| `a.Sharing.DebugStates 3` | 显示当前播放动画的详细信息 |
| `a.Sharing.DisableDebugMaterials 1` | 关闭调试材质着色 |
| `a.Sharing.DebugFontScale <float>` | 调试文字缩放 |
| `a.Sharing.Enabled 0/1` | 运行时开关动画共享 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/AnimationSharing)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- 测试用例：无（未找到官方测试用例）
