# Niagara AnimNotifies

> Niagara effect systems.

| 属性 | 值 |
|---|---|
| 中文名 | Niagara 动画通知 |
| 分类 | FX |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `NiagaraAnimNotifies` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-10-16 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/Niagara/Source/NiagaraAnimNotifies) | |

## 用途

Niagara AnimNotifies 是 Niagara VFX 系统与动画引擎之间的桥梁。它提供了两个预制的动画通知类：

- **`UAnimNotify_PlayNiagaraEffect`**：在动画序列的特定帧触发一次性的 Niagara 粒子效果（类似“蒙太奇粒子发射”）。
- **`UAnimNotifyState_TimedNiagaraEffect`**：在动画通知持续期间循环播放 Niagara 系统，开始播放、结束停止（类似“持续粒子光环”）。

这些通知完全在动画编辑器中配置，**无需任何 C++ 代码或蓝图逻辑**即可将复杂的 Niagara 特效与骨骼动画绑定，极大简化了美术/策划的工作流。

## 使用场景

- 你正在制作一个动作游戏，需要让角色挥剑时在剑刃上产生轨迹特效 → 使用 **Play Niagara Particle Effect** 通知，每秒触发一次剑气粒子。
- 你需要角色在奔跑时脚底持续产生尘土/火焰特效 → 使用 **Timed Niagara Effect** 通知，覆盖整个奔跑动画片段。
- 你希望在动画蓝图中动态控制特效的某个用户参数（例如粒子大小） → 使用带的 `GetSpawnedEffect` 节点获取 FX 组件，然后通过蓝图设置参数。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSpawnedEffect` | 返回由该通知生成的 Niagara FX 组件，可用于后续设置参数、控制生命周期 | `UAnimNotify_PlayNiagaraEffect` / `UAnimNotifyState_TimedNiagaraEffect` |

### 使用示例

1. 在动画序列中添加一个 **Timed Niagara Effect** 通知（设置持续时间为 1 秒）。
2. 在通知的细节面板中：
   - **Niagara System**：选择你的 `UNiagaraSystem` 资产。
   - **Socket Name**：指定绑定的骨骼/插槽名称（如 `weapon_tip`）。
   - **Destroy Immediately**：设为 false 时，通知结束时系统允许粒子自然消亡（而不是立即销毁）。
3. 如果你需要在通知期间调节参数，可以在动画蓝图的事件图表中：
   - 从 `AnimNotifyState` 节点的 Out 引脚拖出 `Get Spawned Effect`。
   - 调用 `Set Float Parameter` 等接口传入曲线值。

## C++ 用法

### 头文件引入

```cpp
#include "AnimNotify_PlayNiagaraEffect.h"
#include "AnimNotifyState_TimedNiagaraEffect.h"
```

### 基本用法：继承并自定义生成逻辑

你可以在 C++ 中继承这两个通知类，重写 `SpawnEffect` 方法来自定义特效的附加方式、条件判断或资源加载。

**示例（继承 `UAnimNotifyState_TimedNiagaraEffect`）**：

```cpp
// MyCustomNiagaraNotify.h
#pragma once

#include "AnimNotifyState_TimedNiagaraEffect.h"
#include "MyCustomNiagaraNotify.generated.h"

UCLASS()
class MYGAME_API UMyCustomNiagaraNotify : public UAnimNotifyState_TimedNiagaraEffect
{
    GENERATED_BODY()

protected:
    virtual UFXSystemComponent* SpawnEffect(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation) const override;
};

// MyCustomNiagaraNotify.cpp
#include "MyCustomNiagaraNotify.h"
#include "NiagaraFunctionLibrary.h"
#include "NiagaraComponent.h"

UFXSystemComponent* UMyCustomNiagaraNotify::SpawnEffect(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation) const
{
    // 根据骨骼数量动态选择 Niagara 系统
    UNiagaraSystem* SystemToSpawn = (MeshComp && MeshComp->GetNumBones() > 50) ? AlternateTemplate : Template;

    // 使用 NiagaraFunctionLibrary 生成特效（自动处理 Socket 附加）
    return UNiagaraFunctionLibrary::SpawnSystemAttached(
        SystemToSpawn,
        MeshComp,
        SocketName,
        LocationOffset,
        RotationOffset,
        Scale,
        EAttachLocation::SnapToTarget,
        true, // bAutoDestroy
        ENCPoolMethod::None,
        true, // bAutoActivate
        true  // bPreCullCheck
    );
}
```

### 进阶用法：获取生成的特效并控制

```cpp
// 在 AnimNotifyState 的 NotifyBegin 中，你已经获得了 SpawnedEffect 指针
// 如果需要更精细的控制，可以在蓝图中调用 GetSpawnedEffect 取得 UFXSystemComponent*
// 然后通过 NiagaraComponent 的 SetVariable* 方法设置用户参数
// 示例（基于 UAnimNotify_PlayNiagaraEffect）：
UFXSystemComponent* EffectComp = MyNotifyObject->GetSpawnedEffect();
if (UNiagaraComponent* NiagaraComp = Cast<UNiagaraComponent>(EffectComp))
{
    NiagaraComp->SetVariableFloat(TEXT("User.Strength"), 2.0f);
}
```

## Demo 示例

以下是一个最小 C++ 示例，展示如何创建一个自定义的“一次性” Niagara 通知（类似 `UAnimNotify_PlayNiagaraEffect` 但附加了声音播放）。

```cpp
// MyCustomPlayNiagaraNotify.h
#pragma once

#include "AnimNotify_PlayNiagaraEffect.h"
#include "MyCustomPlayNiagaraNotify.generated.h"

UCLASS()
class UMyCustomPlayNiagaraNotify : public UAnimNotify_PlayNiagaraEffect
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sound")
    USoundBase* SoundToPlay;

protected:
    virtual UFXSystemComponent* SpawnEffect(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation) override;
};

// MyCustomPlayNiagaraNotify.cpp
#include "MyCustomPlayNiagaraNotify.h"
#include "Kismet/GameplayStatics.h"

UFXSystemComponent* UMyCustomPlayNiagaraNotify::SpawnEffect(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation)
{
    // 先播放声音
    if (SoundToPlay && MeshComp)
    {
        UGameplayStatics::PlaySoundAtLocation(this, SoundToPlay, MeshComp->GetComponentLocation());
    }
    // 调用父类生成特效
    return Super::SpawnEffect(MeshComp, Animation);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Niagara` (Runtime) | Niagara 粒子系统的核心运行时模块，提供 `UNiagaraSystem`、`UNiagaraComponent` 和 `UNiagaraFunctionLibrary` |

> 其他标准依赖（Core, CoreUObject, Engine, Slate 等）此处省略。

## 维护状态

### 近期更新

- 2025-10-22 `5d0cd83c` 修复了清理过程中访问已释放 Niagara 组件的问题。
- 2025-10-22 `3f549682` 修复了 CPU 端无数据更新时残留 NDC 数据的问题。
- 2025-10-21 `6ac05a79` 添加了一个默认关闭的 workaround，用于修复内部测试中遇到的 Niagara 崩溃。
- 2025-10-17 `f6546371` 修复了 GT 和 RT 的 tick 不匹配导致 NDC 数据丢失的问题。
- 2025-10-16 `566219ca` [Backout] 撤回 CL47013072。

### 维护评价

- **创建时间**：2025-10-16（模块首次记录），推测该模块在 UE5.0 之前已存在，但近期已有活跃更新。
- **近期更新**：连续 5 次 commit 均为修复性更新（内存访问、数据同步、崩溃），频率高，说明该模块已进入稳定维护期。
- **活跃度**：距离现在不足 2 个月，修复及时，属于活跃维护。
- **推荐使用**：✅ 推荐。Niagara 动画通知是官方方案，与动画蓝图深度集成，性能稳定。如有特殊需求（如条件判断、自定义附加逻辑），建议从 `SpawnEffect` 重写，而非修改通知生命周期。已知限制：只支持骨骼网格体，无法直接用于 Morph Target 或静态网格体的动画。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/Niagara/Source/NiagaraAnimNotifies)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/Niagara/Tests)（Niagara 全局测试）