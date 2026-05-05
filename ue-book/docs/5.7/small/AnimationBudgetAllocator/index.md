# Animation Budget Allocator

> Constrains the time taken for animation to run by dynamically throttling skeletal mesh component ticking.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | AnimationBudgetAllocator (Runtime, LoadingPhase=PreDefault) |
| 创建时间 | 2018-11-14 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AnimationBudgetAllocator) | |

## 用途

AnimationBudgetAllocator 是一个全局动画性能预算系统。它的核心思路是：**给骨骼动画分配一个固定的时间预算（毫秒），当场景中骨骼网格体组件过多导致动画 tick 超出预算时，自动降低低重要性组件的更新频率，甚至跳过 tick、启用插值或切换到"减少工作量"模式**。

这个 plugin 解决的核心问题是：在有大量角色/NPC 的场景中（如大逃杀、MMO、开放世界），骨骼动画的 tick 开销可能严重拖慢帧率。AnimationBudgetAllocator 通过 importance-based 的动态降级策略，在保持高重要性角色（如玩家）动画质量的同时，大幅降低远处/不重要角色的动画开销。

与 URO（Update Rate Optimization）不同，AnimationBudgetAllocator 是**全局协调**的——它在每帧总预算内统一调度所有已注册组件的 tick，而不是每个组件独立决策。

## 使用场景

- 你的游戏有大量同屏角色（50+ 骨骼网格体），动画 tick 成为瓶颈 → 用 AnimationBudgetAllocator
- 你希望玩家角色始终以最高频率更新动画，远处 NPC 降频 → 配合 `SetComponentSignificance` 使用
- 你需要全局控制动画性能预算，而不是逐个组件调 URO → 用这个 plugin
- Fortnite、大逃杀类游戏是此 plugin 的主要用户

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EnableAnimationBudget` | 启用/禁用动画预算系统 | `UAnimationBudgetBlueprintLibrary` |
| `SetAnimationBudgetParameters` | 设置预算参数（预算时间、降级策略等） | `UAnimationBudgetBlueprintLibrary` |
| `SetComponentSignificance` | 设置组件重要性（0~1），决定降级优先级 | `USkeletalMeshComponentBudgeted` |
| `SetAutoRegisterWithBudgetAllocator` | 设置是否自动注册到预算系统 | `USkeletalMeshComponentBudgeted` |

### 使用示例（蓝图描述）

**1. 在 GameMode 或 GameState 中初始化预算系统：**

- BeginPlay → 调用 `EnableAnimationBudget`（WorldContext = self, bEnabled = true）
- 接着调用 `SetAnimationBudgetParameters`，构造一个 `FAnimationBudgetAllocatorParameters` 结构体，设置 `BudgetInMs = 2.0`（分配 2ms 给动画）

**2. 使用预算化的骨骼组件：**

- 将角色的 SkeletalMeshComponent 替换为 `SkeletalMeshComponentBudgeted`
- 在 Details 面板中勾选 `bAutoRegisterWithBudgetAllocator = true`（自动注册）
- 勾选 `bAutoCalculateSignificance = true`（自动按距离计算重要性）

**3. 手动设置重要性（高级用法）：**

- 对每个 Budgeted 组件调用 `SetComponentSignificance(Significance=1.0, bNeverSkip=true)` → 玩家角色永不跳过
- 对远处 NPC 调用 `SetComponentSignificance(Significance=0.3)` → 低优先级降频

## C++ 用法

### 头文件引入

```cpp
#include "IAnimationBudgetAllocator.h"
#include "SkeletalMeshComponentBudgeted.h"
#include "AnimationBudgetAllocatorParameters.h"
```

### 基本用法：启用预算系统并设置参数

```cpp
// 在 GameMode 或合适的地方启用预算系统
#include "AnimationBudgetBlueprintLibrary.h"

void AMyGameMode::BeginPlay()
{
    Super::BeginPlay();

    // 启用动画预算
    UAnimationBudgetBlueprintLibrary::EnableAnimationBudget(this, true);

    // 配置参数
    FAnimationBudgetAllocatorParameters Params;
    Params.BudgetInMs = 2.0f;              // 总预算 2ms
    Params.MaxTickRate = 10;               // 最低每 10 帧 tick 一次
    Params.MinQuality = 0.0f;              // 允许完全跳过低重要性组件
    Params.AutoCalculatedSignificanceMaxDistance = 50000.0f; // 500 米外重要性为 0

    UAnimationBudgetBlueprintLibrary::SetAnimationBudgetParameters(this, Params);
}
```

### 进阶用法：通过 C++ 接口直接操作

```cpp
// 获取当前世界的预算分配器
IAnimationBudgetAllocator* Budgeter = IAnimationBudgetAllocator::Get(GetWorld());
if (Budgeter)
{
    // 手动注册组件（如果未自动注册）
    Budgeter->RegisterComponent(MyBudgetedComponent);

    // 设置重要性：高重要性、永不跳过、即使不在屏幕内也 tick
    Budgeter->SetComponentSignificance(
        MyBudgetedComponent,
        1.0f,    // Significance: 1.0 = 最高
        true,    // bNeverSkip: 永不跳过
        true,    // bTickEvenIfNotRendered: 不可见也 tick
        true,    // bAllowReducedWork: 允许减少工作量
        false    // bForceInterpolate: 不强制插值
    );

    // 强制下一帧 tick（忽略预算调度）
    Budgeter->ForceNextTickThisFrame(MyBudgetedComponent);
}
```

### 自定义重要性计算

```cpp
// 绑定全局重要性计算委托（在 bAutoCalculateSignificance=true 时生效）
USkeletalMeshComponentBudgeted::OnCalculateSignificance().BindLambda(
    [](USkeletalMeshComponentBudgeted* Component) -> float
    {
        // 自定义：基于到玩家的距离计算重要性
        APlayerController* PC = Component->GetWorld()->GetFirstPlayerController();
        if (!PC || !PC->GetPawn()) return 0.0f;

        float Distance = FVector::Dist(
            Component->GetComponentLocation(),
            PC->GetPawn()->GetActorLocation()
        );

        // 1000cm 内 = 1.0，10000cm 外 = 0.0
        return FMath::Clamp(1.0f - (Distance - 1000.0f) / 9000.0f, 0.0f, 1.0f);
    }
);
```

## Demo 示例

### 最小可运行示例

**MyGameMode.h:**
```cpp
#pragma once
#include "GameFramework/GameModeBase.h"
#include "MyGameMode.generated.h"

UCLASS()
class AMyGameMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;
};
```

**MyGameMode.cpp:**
```cpp
#include "MyGameMode.h"
#include "AnimationBudgetBlueprintLibrary.h"
#include "AnimationBudgetAllocatorParameters.h"

void AMyGameMode::BeginPlay()
{
    Super::BeginPlay();

    // 启用动画预算
    UAnimationBudgetBlueprintLibrary::EnableAnimationBudget(this, true);

    // 设置预算参数
    FAnimationBudgetAllocatorParameters Params;
    Params.BudgetInMs = 2.0f;
    Params.MaxTickRate = 10;
    Params.AutoCalculatedSignificanceMaxDistance = 30000.0f;
    UAnimationBudgetBlueprintLibrary::SetAnimationBudgetParameters(this, Params);
}
```

**Build.cs 依赖：**
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "AnimationBudgetAllocator"
});
```

## CVar 控制台变量

通过控制台变量可以实时调整预算系统参数，适合运行时调试和可扩展性（Scalability）配置。

| CVar | 默认值 | 说明 |
|---|---|---|
| `a.Budget.Enabled` | 0 | 全局启用/禁用（可被 Scalability 覆盖） |
| `a.Budget.BudgetMs` | 1.0 | 动画 tick 时间预算（毫秒） |
| `a.Budget.MinQuality` | 0.0 | 最低质量指标 [0.0, 1.0] |
| `a.Budget.MaxTickRate` | 10 | 最大 tick 间隔（帧数） |
| `a.Budget.WorkUnitSmoothingSpeed` | 5.0 | 工作单元时间平滑速度 |
| `a.Budget.AlwaysTickFalloffAggression` | 0.8 | "始终 tick"组件的降级激进度 [0.1, 0.9] |
| `a.Budget.InterpolationFalloffAggression` | 0.4 | 插值组件的降级激进度 [0.1, 0.9] |
| `a.Budget.InterpolationMaxRate` | 6 | 插值模式最大 tick 间隔 |
| `a.Budget.MaxInterpolatedComponents` | 16 | 最大插值组件数 |
| `a.Budget.MaxTickedOffsreen` | 4 | 最大屏幕外 tick 组件数 |
| `a.Budget.StateChangeThrottleInFrames` | 30 | 状态变更节流（帧） |
| `a.Budget.BudgetFactorBeforeReducedWork` | 1.5 | 触发"减少工作量"的预算压力阈值 |
| `a.Budget.BudgetFactorBeforeAggressiveReducedWork` | 2.0 | 触发激进减少工作量的阈值 |
| `a.Budget.GBudgetPressureBeforeEmergencyReducedWork` | 2.5 | 紧急减少工作量的阈值 |
| `a.Budget.AutoCalculatedSignificanceMaxDistance` | 30000.0 | 自动重要性计算的最大距离（cm） |

**调试 CVar（非 Shipping/Test 构建）：**

| CVar | 说明 |
|---|---|
| `a.Budget.Debug.Enabled` | 启用调试渲染 |
| `a.Budget.Debug.ShowAddresses` | 显示组件数据地址 |
| `a.Budget.Debug.Force` | 强制覆盖预算调度 |
| `a.Budget.Debug.Force.Rate` | 强制 tick 速率 |
| `a.Budget.Debug.Force.Interp` | 强制插值 |
| `a.Budget.Debug.Force.Reduced` | 强制减少工作量 |

## 模块依赖

AnimationBudgetAllocator.Build.cs 中声明的依赖：

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、容器、数学库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（World、Components 等） |

> 注意：这些都是 PrivateDependency，使用者只需在自己的 Build.cs 中添加 `AnimationBudgetAllocator` 即可。

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-06-16 | `7450ee1` | Replace some usages of FORCEINLINE with inline in Animation modules | 代码规范化，将 `FORCEINLINE` 替换为 `inline`，无功能变更 |
| 2025-05-08 | `8e62bc8` | Animation Budget Allocator: Enable component tick when unregistering | **Bug 修复**：取消注册组件时重新启用 tick，修复了组件从预算系统移除后可能停止动画的问题 |
| 2025-04-23 | `939cc6e` | Used FortniteClient build target to find and convert all files to have dllstorage | DLL 导出符号规范化，支持 Fortnite 构建目标 |

### 维护评价

- **年龄**：2018 年 11 月创建，约 7 年历史
- **活跃度**：2025 年仍有实质性更新（bug 修复），属于**活跃维护**
- **稳定性**：非实验性（`IsExperimentalVersion=false`，`IsBetaVersion=false`），但默认未启用（`EnabledByDefault=false`）
- **使用者**：Fortnite 是主要用户，说明经过大规模生产验证
- **推荐**：如果你的游戏有大量骨骼网格体需要优化，**推荐使用**。这是一个成熟、经过实战验证的性能优化方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AnimationBudgetAllocator)
- [官方文档]()（无官方文档页面）
