# Niagara

> Niagara effect systems.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 尼亚加拉粒子系统 |
| 分类 | FX |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、编辑器工具、测试资源） |
| 模块 | `Niagara` (Runtime), `NiagaraAnimNotifies` (Runtime), `NiagaraBlueprintNodes` (Runtime), `NiagaraCore` (Runtime), `NiagaraEditor` (Runtime), `NiagaraEditorWidgets` (Runtime), `NiagaraShader` (Runtime), `NiagaraVertexFactories` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-08-28 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/Niagara) | |

## 用途

Niagara 是 UE5 官方的新一代视觉特效（VFX）系统，用于替代 UE4 时代的 Cascade 粒子系统。它提供了基于节点的可视化脚本环境，允许开发者通过模块化的方式创建、编辑和调试粒子效果。

Niagara 解决了 Cascade 系统的多个核心限制：
- **数据驱动架构**：粒子数据存储在 GPU/ CPU 数据接口中，支持自定义数据通道
- **可扩展性**：通过 Module、Function、Emitter、System 的分层架构，支持从简单到极其复杂的特效需求
- **多发射器交互**：Emitter 可以读取同一 System 内其他 Emitter 的数据
- **事件驱动**：支持基于事件的粒子生成和行为触发
- **GPU 计算**：原生 GPU 粒子模拟支持，利用 Compute Shader 实现大规模粒子效果
- **数据接口**：可读取场景中的网格体、碰撞体、音频波形、流体模拟等外部数据

Niagara 是 UE5 默认推荐的粒子系统，Cascade 已进入维护模式。

## 使用场景

- 你需要创建火焰、烟雾、爆炸等环境特效 → 使用 Niagara 的标准 Emitter 配置
- 你需要大量粒子（数万到数百万）的 GPU 粒子模拟 → 使用 Niagara 的 GPU Compute 功能
- 你需要粒子与场景网格体交互（如沿表面流动） → 使用 Niagara 的 Mesh Data Interface
- 你需要在动画通知中触发粒子效果 → 使用 NiagaraAnimNotifies 模块
- 你需要通过蓝图或 C++ 动态控制粒子参数 → 使用 NiagaraComponent API
- 你需要自定义粒子行为逻辑 → 在 Niagara 编辑器中创建自定义 Module

## 蓝图用法

### NiagaraAnimNotifies 模块核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSpawnedEffect` | 获取由动画通知生成的 FX 组件 | `UAnimNotify_PlayNiagaraEffect` |
| `GetSpawnedEffect` | 获取由定时通知状态生成的 FX 组件 | `UAnimNotifyState_TimedNiagaraEffect` |
| `GetNotifyProgress` | 获取当前通知的播放进度（0~1） | `UAnimNotifyState_TimedNiagaraEffectAdvanced` |

### 动画通知 - 播放 Niagara 效果

`UAnimNotify_PlayNiagaraEffect` 在动画的特定时间点触发一次 Niagara 特效：

1. 在动画序列或蒙太奇中添加通知，选择 "Play Niagara Particle Effect"
2. 设置 **Niagara System**：指定要播放的 Niagara 系统模板
3. 设置 **Socket Name**：指定附加到的骨骼/插槽名称
4. 设置 **Location Offset / Rotation Offset**：偏移位置和旋转
5. 设置 **Scale**：缩放
6. 勾选 **Attached**：粒子是否跟随骨骼移动
7. 蓝图中可通过 `GetSpawnedEffect` 获取生成的组件引用进行后续操作

### 动画通知状态 - 定时 Niagara 效果

`UAnimNotifyState_TimedNiagaraEffect` 在通知的开始和结束之间持续播放 Niagara 特效：

1. 在动画中添加通知状态，选择 "Timed Niagara Effect"
2. 设置 **Niagara System**、**Socket Name**、偏移和缩放
3. 设置 **Destroy Immediately**：通知结束时是否立即销毁（否则等待粒子自然结束）
4. 设置 **Apply Rate Scale As Time Dilation**：是否将动画速率作为特效的时间膨胀

### 高级定时 Niagara 效果

`UAnimNotifyState_TimedNiagaraEffectAdvanced` 在基础版之上增加了进度通知和动画曲线映射：

1. 设置 **Notify Progress Type**：`Forward`（0→1）/ `Reverse`（1→0）/ `None`
2. 设置 **Notify Progress User Parameter**：接收进度值的 Niagara 用户变量名
3. 设置 **Anim Curve Parameters**：将动画曲线名称映射到 Niagara 用户浮点变量
4. 蓝图中通过 `GetNotifyProgress` 读取当前进度值

## C++ 用法

### 头文件引入

```cpp
// 动画通知相关
#include "AnimNotify_PlayNiagaraEffect.h"
#include "AnimNotifyState_TimedNiagaraEffect.h"

// Niagara 核心
#include "NiagaraComponent.h"
#include "NiagaraSystem.h"
#include "NiagaraFunctionLibrary.h"
```

### 基本用法 - 创建自定义播放 Niagara 动画通知

从 `AnimNotify_PlayNiagaraEffect` 源码中可以看到其核心模式——在 `Notify` 中调用 `SpawnEffect` 生成组件：

```cpp
// 自定义继承自 AnimNotify_PlayNiagaraEffect 的通知
// 来源: Engine/Plugins/FX/Niagara/Source/NiagaraAnimNotifies/Public/AnimNotify_PlayNiagaraEffect.h
UCLASS(meta = (DisplayName = "My Custom Niagara Notify"))
class UMyAnimNotify_Niagara : public UAnimNotify_PlayNiagaraEffect
{
    GENERATED_BODY()

public:
    // 获取生成的特效组件引用
    UFUNCTION(BlueprintCallable, Category = "AnimNotify")
    UFXSystemComponent* GetSpawnedComponent()
    {
        return GetSpawnedEffect();
    }
};
```

### 基本用法 - 创建定时 Niagara 通知状态

```cpp
// 从 AnimNotifyState_TimedNiagaraEffect 派生自定义通知状态
// 来源: Engine/Plugins/FX/Niagara/Source/NiagaraAnimNotifies/Public/AnimNotifyState_TimedNiagaraEffect.h
UCLASS(meta = (DisplayName = "My Timed Niagara State"))
class UMyAnimNotifyState_Niagara : public UAnimNotifyState_TimedNiagaraEffect
{
    GENERATED_BODY()

public:
    // 可以覆盖 NotifyBegin 进行自定义逻辑
    virtual void NotifyBegin(
        USkeletalMeshComponent* MeshComp,
        UAnimSequenceBase* Animation,
        float TotalDuration,
        const FAnimNotifyEventReference& EventReference) override
    {
        Super::NotifyBegin(MeshComp, Animation, TotalDuration, EventReference);
        // 自定义开始逻辑
    }

    virtual void NotifyEnd(
        USkeletalMeshComponent* MeshComp,
        UAnimSequenceBase* Animation,
        const FAnimNotifyEventReference& EventReference) override
    {
        Super::NotifyEnd(MeshComp, Animation, EventReference);
        // 自定义结束逻辑，例如获取生成的特效
        UFXSystemComponent* Effect = GetSpawnedEffect(MeshComp);
        if (Effect)
        {
            // 对特效组件进行自定义操作
        }
    }
};
```

### 进阶用法 - 高级定时通知与进度追踪

```cpp
// 使用高级定时通知实现动画曲线到 Niagara 参数的映射
// 来源: Engine/Plugins/FX/Niagara/Source/NiagaraAnimNotifies/Public/AnimNotifyState_TimedNiagaraEffect.h
UCLASS(meta = (DisplayName = "Advanced Niagara Notify With Progress"))
class UMyAnimNotifyState_AdvancedNiagara : public UAnimNotifyState_TimedNiagaraEffectAdvanced
{
    GENERATED_BODY()

public:
    UMyAnimNotifyState_AdvancedNiagara()
    {
        // 设置进度类型为正向（0→1）
        NotifyProgressType = ENiagaraAnimNotifyProgressType::Forward;

        // 设置接收进度的 Niagara 用户参数名
        NotifyProgressUserParameter = FName("NotifyProgress");

        // 将动画曲线 "MyAnimCurve" 映射到 Niagara 用户浮点 "NiagaraCurveValue"
        FCurveParameterPair CurveMapping;
        CurveMapping.AnimCurveName = FName("MyAnimCurve");
        CurveMapping.UserVariableName = FName("NiagaraCurveValue");
        AnimCurves.Add(CurveMapping);
    }

    virtual void NotifyTick(
        USkeletalMeshComponent* MeshComp,
        UAnimSequenceBase* Animation,
        float FrameDeltaTime,
        const FAnimNotifyEventReference& EventReference) override
    {
        Super::NotifyTick(MeshComp, Animation, FrameDeltaTime, EventReference);

        // 读取当前通知进度
        float Progress = GetNotifyProgress(MeshComp);
        // 自定义逻辑...
    }
};
```

### 进阶用法 - 通过代码生成通知并关联曲线参数

```cpp
// 配置 FCurveParameterPair 将多个动画曲线映射到 Niagara 参数
// 来源: Engine/Plugins/FX/Niagara/Source/NiagaraAnimNotifies/Public/AnimNotifyState_TimedNiagaraEffect.h
void SetupAdvancedNiagaraNotify(UAnimNotifyState_TimedNiagaraEffectAdvanced* Notify)
{
    // 正向进度
    Notify->NotifyProgressType = ENiagaraAnimNotifyProgressType::Forward;
    Notify->NotifyProgressUserParameter = FName("AnimProgress");
    Notify->bApplyRateScaleToProgress = true;

    // 批量添加曲线映射
    TArray<FName> AnimCurveNames = { FName("Alpha"), FName("Intensity"), FName("Scale") };
    TArray<FName> NiagaraUserVars = { FName("EmitterAlpha"), FName("EmitIntensity"), FName("EmitterScale") };

    for (int32 i = 0; i < AnimCurveNames.Num(); ++i)
    {
        FCurveParameterPair Pair;
        Pair.AnimCurveName = AnimCurveNames[i];
        Pair.UserVariableName = NiagaraUserVars[i];
        Notify->AnimCurves.Add(Pair);
    }
}
```

## Demo 示例

以下示例展示如何在 C++ 中创建一个自定义的高级定时 Niagara 动画通知：

**MyNiagaraAnimNotify.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "AnimNotifyState_TimedNiagaraEffect.h"
#include "MyNiagaraAnimNotify.generated.h"

UCLASS(meta = (DisplayName = "Weapon Trail Niagara Effect"))
class MYGAME_API UAnimNotifyState_WeaponTrail : public UAnimNotifyState_TimedNiagaraEffectAdvanced
{
    GENERATED_BODY()

public:
    UAnimNotifyState_WeaponTrail();

    virtual void NotifyBegin(
        USkeletalMeshComponent* MeshComp,
        UAnimSequenceBase* Animation,
        float TotalDuration,
        const FAnimNotifyEventReference& EventReference) override;

    virtual void NotifyTick(
        USkeletalMeshComponent* MeshComp,
        UAnimSequenceBase* Animation,
        float FrameDeltaTime,
        const FAnimNotifyEventReference& EventReference) override;

    virtual void NotifyEnd(
        USkeletalMeshComponent* MeshComp,
        UAnimSequenceBase* Animation,
        const FAnimNotifyEventReference& EventReference) override;

    // 自定义：攻击强度参数名
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Weapon")
    FName AttackIntensityParameter = FName("AttackIntensity");

    // 自定义：当前攻击强度
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Weapon")
    float CurrentAttackIntensity = 1.0f;
};
```

**MyNiagaraAnimNotify.cpp**
```cpp
#include "MyNiagaraAnimNotify.h"
#include "NiagaraComponent.h"
#include "NiagaraFunctionLibrary.h"

UAnimNotifyState_WeaponTrail::UAnimNotifyState_WeaponTrail()
{
    // 使用基础版本的配置
    NotifyProgressType = ENiagaraAnimNotifyProgressType::Forward;
    NotifyProgressUserParameter = FName("TrailProgress");
    bApplyRateScaleToProgress = true;

    // 将动画曲线映射到 Niagara 参数
    FCurveParameterPair WidthCurve;
    WidthCurve.AnimCurveName = FName("TrailWidth");
    WidthCurve.UserVariableName = FName("EmitterWidth");
    AnimCurves.Add(WidthCurve);

    // 不要在通知结束时立即销毁，让拖尾效果自然消失
    bDestroyAtEnd = false;
}

void UAnimNotifyState_WeaponTrail::NotifyBegin(
    USkeletalMeshComponent* MeshComp,
    UAnimSequenceBase* Animation,
    float TotalDuration,
    const FAnimNotifyEventReference& EventReference)
{
    Super::NotifyBegin(MeshComp, Animation, TotalDuration, EventReference);

    // 获取生成的 Niagara 组件并设置攻击强度参数
    UFXSystemComponent* FXComponent = GetSpawnedEffect(MeshComp);
    if (UNiagaraComponent* NiagaraComp = Cast<UNiagaraComponent>(FXComponent))
    {
        NiagaraComp->SetVariableFloat(AttackIntensityParameter, CurrentAttackIntensity);
    }
}

void UAnimNotifyState_WeaponTrail::NotifyTick(
    USkeletalMeshComponent* MeshComp,
    UAnimSequenceBase* Animation,
    float FrameDeltaTime,
    const FAnimNotifyEventReference& EventReference)
{
    Super::NotifyTick(MeshComp, Animation, FrameDeltaTime, EventReference);

    // 获取当前进度并可用于自定义逻辑
    float Progress = GetNotifyProgress(MeshComp);

    UFXSystemComponent* FXComponent = GetSpawnedEffect(MeshComp);
    if (UNiagaraComponent* NiagaraComp = Cast<UNiagaraComponent>(FXComponent))
    {
        // 根据进度动态调整攻击强度
        float ScaledIntensity = CurrentAttackIntensity * FMath::InterpEaseIn(1.0f, 0.3f, Progress, 2.0f);
        NiagaraComp->SetVariableFloat(AttackIntensityParameter, ScaledIntensity);
    }
}

void UAnimNotifyState_WeaponTrail::NotifyEnd(
    USkeletalMeshComponent* MeshComp,
    UAnimSequenceBase* Animation,
    const FAnimNotifyEventReference& EventReference)
{
    Super::NotifyEnd(MeshComp, Animation, EventReference);

    // bDestroyAtEnd 为 false 时，组件会被停止但不会被立即销毁
    // 拖尾粒子会自然消散
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NiagaraCore` | Niagara 核心类型定义和基础数据接口 |
| `Niagara` | Niagara 运行时引擎，粒子系统模拟与渲染 |
| `NiagaraShader` | Niagara 着色器编译与 GPU 计算支持 |
| `NiagaraVertexFactories` | Niagara 顶点工厂，用于粒子渲染管线 |
| `NiagaraBlueprintNodes` | Niagara 蓝图函数库节点 |
| `NiagaraAnimNotifies` | 动画通知集成，支持在动画中触发粒子效果 |
| `NiagaraEditor` | Niagara 编辑器，节点图可视化编辑环境 |
| `NiagaraEditorWidgets` | Niagara 编辑器自定义 UI 控件 |

> 以上为 Niagara 插件的内部模块依赖关系。外部使用者通常只需依赖 `Niagara` 模块即可访问运行时 API。若需要动画通知功能，还需额外依赖 `NiagaraAnimNotifies`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `da97a493` | Data Hierarchy: guard SyncViewModelsToData against re-entry from OnHierarchyChanged listeners | 修复数据层级同步时监听器重入导致的递归问题 |
| 2026-05-22 | `85c6d110` | Avoid creating an empty RHI buffer for SKM sampling data | 避免为骨骼网格体采样数据创建空的 RHI 缓冲区 |
| 2026-05-20 | `119ee9ac` | [HWRT] Fix FNiagaraRendererMeshes::GetDynamicRayTracingInstances(...) corrupting GPUScene when rendering | 修复网格体渲染器的光线追踪实例获取导致 GPUScene 损坏的问题 |
| 2026-05-19 | `5e68c5a9` | [HWRT] Fix crash due to FNiagaraRendererRibbons requesting multiple updates on the same RayTracingGeometry | 修复带状渲染器在同一光线追踪几何体上请求多次更新导致的崩溃 |
| 2026-05-14 | `4bb8e4f1` | Fix UNiagaraBakerSettings crash when AI toolset or Python writes a null entry into the Outputs array | 修复 AI 工具或 Python 脚本写入空条目时烘焙设置崩溃的问题 |

### 维护评价

**活跃维护** ✅

- **创建时间**：2017 年 8 月，已持续开发约 9 年
- **更新频率**：最近一周内有 5 次提交，更新极为频繁
- **更新内容**：涵盖硬件光线追踪修复、GPU 场景优化、数据层级架构改进、崩溃修复等，属于核心功能持续迭代
- **团队投入**：Epic Games 核心 VFX 团队长期维护，是 UE5 官方推荐的粒子系统
- **成熟度**：作为 Cascade 的替代者，Niagara 已非常成熟且功能完备，是 UE5 中最重要的 VFX 系统
- **已知限制**：硬件光线追踪相关功能仍在持续修复中，GPU 粒子在某些平台上可能有兼容性问题

**推荐使用**：强烈推荐。Niagara 是 UE5 标准粒子系统，新项目应全面使用 Niagara 而非 Cascade。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/Niagara)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/creating-visual-effects-in-niagara-for-unreal-engine/)