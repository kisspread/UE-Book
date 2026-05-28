# Contextual Animation

> 

| 属性 | 值 |
|---|---|
| 中文名 | 上下文动画 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画数据资产、调试资源） |
| 模块 | `ContextualAnimation` (Runtime), `ContextualAnimationEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-01-25 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/ContextualAnimation) | |

## 用途

**Contextual Animation** 是一个用于管理角色间上下文动画交互的实验性系统。它解决的核心问题是：如何让多个角色（通常是玩家角色与AI/NPC）播放需要精确空间对齐和时间同步的动画（如近战攻击、处决动作、合作互动等）。该插件提供了一个数据驱动的框架，允许开发者在一个`UContextualAnimAsset`中定义一组相互关联的动画轨道，并通过组件在运行时查询、选择并播放最合适的一组动画，确保角色之间的相对位置、朝向和动画时机完美匹配。

## 使用场景

- 你正在开发一个动作游戏，需要实现主角对敌人施展多种处决动画，每种动画都有不同的起始位置和朝向要求。
- 你需要让玩家角色与NPC进行复杂的交互动作（如搀扶、协同开锁），并确保两者动作无缝衔接。
- 你在制作格斗游戏，其中连招和反击动画需要根据对手的相对位置和状态动态选择。
- 你需要在编辑器中快速预览和测试多人动画交互的效果，而不必每次都进入运行时。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `QueryAndPlay` | 查询指定`ContextualAnimAsset`中与目标Actor相对位置最匹配的动画并播放 | `UContextualAnimComponent` |
| `GetAnimData` | 获取动画数据资产的引用 | `AContextualAnimActor` |
| `DrawDebug` | 在世界中绘制调试图形，可视化动画的入场点和容差范围 | `UContextualAnimComponent` |

### 使用示例（蓝图描述）

1.  **准备阶段**：在`UContextualAnimAsset`编辑器中，为处决动画创建两个轨道：一个用于玩家角色（执行者），一个用于敌人（目标）。设置每组动画的入场点位置、朝向和容差。
2.  **运行时调用**：
    - 在玩家角色的蓝图中，添加`UContextualAnimComponent`组件。
    - 当满足触发条件（如敌人血量低于阈值且在近战距离内）时，获取敌人的引用。
    - 调用`QueryAndPlay`节点，传入准备好的`ContextualAnimAsset`和目标敌人Actor。
    - 系统会自动计算最合适的动画组，并控制两个角色开始播放对齐后的动画。
3.  **调试**：在游戏运行时，通过`DrawDebug`节点可以可视化当前选定的动画入场点（小球）和容差范围（圆柱），帮助调整资产设置。

## C++ 用法

### 头文件引入

```cpp
#include "ContextualAnimComponent.h"
#include "ContextualAnimAsset.h"
#include "ContextualAnimActor.h"
```

### 基本用法

通过组件播放上下文动画。通常在一个Actor（如玩家角色）上创建`UContextualAnimComponent`。

```cpp
// 在 Actor 的 BeginPlay 或需要触发的地方
UContextualAnimComponent* AnimComponent = FindComponentByClass<UContextualAnimComponent>();
if (AnimComponent && ContextualAnimAsset && TargetActor)
{
    // 查询并播放与目标Actor最匹配的动画
    AnimComponent->QueryAndPlay(ContextualAnimAsset, TargetActor);
}
```
*来源：基于模块文档中对`UContextualAnimComponent`核心接口的描述。*

### 进阶用法

处理动画播放完成后的回调，以及自定义Actor在动画期间的行为。

```cpp
// 假设我们有一个自定义的 AContextualAnimActor
void AMyContextualAnimActor::OnContextualAnimEnded(UAnimMontage* Montage, bool bInterrupted)
{
    // 动画播放结束（或中断）后的清理逻辑
    // 例如：销毁自身，或恢复AI控制
    if (!bInterrupted)
    {
        Destroy();
    }
}

// 在初始化时绑定回调
AnimComponent->OnContextualAnimEnded.AddDynamic(this, &AMyContextualAnimActor::OnContextualAnimEnded);
```
*来源：基于`UContextualAnimComponent`的委托声明和`AContextualAnimActor`的典型用法推断。*

## Demo 示例

一个最小的可编译示例，展示如何设置一个可交互的上下文动画Actor。

```cpp
// MyContextualAnimActor.h
#pragma once
#include "CoreMinimal.h"
#include "ContextualAnimActor.h"
#include "MyContextualAnimActor.generated.h"

UCLASS()
class AMyContextualAnimActor : public AContextualAnimActor
{
    GENERATED_BODY()
public:
    AMyContextualAnimActor();
    virtual void BeginPlay() override;

private:
    UFUNCTION()
    void OnAnimEnded(UAnimMontage* Montage, bool bInterrupted);
};
```

```cpp
// MyContextualAnimActor.cpp
#include "MyContextualAnimActor.h"
#include "ContextualAnimComponent.h"

AMyContextualAnimActor::AMyContextualAnimActor()
{
    // 构造函数中设置默认动画数据资产（可在蓝图或编辑器中覆盖）
    // AnimDataAsset = LoadObject<UContextualAnimAsset>(nullptr, TEXT("/Game/Path/To/Your/Asset"));
}

void AMyContextualAnimActor::BeginPlay()
{
    Super::BeginPlay();

    // 确保有动画组件并绑定结束回调
    if (UContextualAnimComponent* Comp = FindComponentByClass<UContextualAnimComponent>())
    {
        Comp->OnContextualAnimEnded.AddDynamic(this, &AMyContextualAnimActor::OnAnimEnded);
    }
}

void AMyContextualAnimActor::OnAnimEnded(UAnimMontage* Montage, bool bInterrupted)
{
    // 简单逻辑：动画播放完毕后销毁自己
    if (!bInterrupted)
    {
        Destroy();
    }
}
```

## 模块依赖

根据`.uplugin`文件，使用本插件需要以下**插件级**依赖：

| 模块 | 用途 |
|---|---|
| `MotionWarping` | 为上下文动画提供动态调整角色位置（“扭曲”）的能力，是实现精确对齐的关键。 |
| `IKRig` | 可能在动画混合或最终姿态调整中用于反向动力学（IK）求解，确保肢体末端（如脚）在动画期间贴合地面。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏更新为新的函数式日志宏，代码现代化。 |
| 2026-04-06 | `76545631` | [CAS] Override Support for CAS Actors | 为上下文动画系统(CAS)的Actor添加了覆盖支持，增强了灵活性。 |
| 2026-03-27 | `5c7c61e7` | Contextual Anim Editor: | 编辑器模块的更新，具体改动未在摘要中说明。 |
| 2026-03-11 | `4f7e0527` | Contextual Anim Editor - Added warning message to validate that a preview actor class has a Contextu | 编辑器中增加了验证警告，确保预览Actor类具备必要的上下文动画组件。 |
| 2026-03-11 | `9d29e89e` | Contextual Anim - Added option to let the system find ideal start time for the interaction based on | 核心功能更新：新增选项，允许系统根据目标位置自动寻找交互的理想开始时间。 |

### 维护评价

该插件**仍处于活跃维护状态**。尽管标记为实验性且默认未启用，但自2021年创建以来持续有更新，最近的提交集中在2026年3月和4月，主要增加了新功能（如覆盖支持、智能开始时间）并优化了编辑器工作流。其依赖的`MotionWarping`和`IKRig`插件也都是Epic重点维护的项目。

**建议**：这是一个功能强大但复杂的系统，适用于需要制作高保真角色交互的游戏项目。由于其**实验性**标签，不建议在追求绝对稳定性的正式项目中作为核心依赖，但在原型开发或中小型项目中，它是实现高级动画交互的绝佳工具。使用前建议详细阅读模块文档并测试Demo。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/ContextualAnimation)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/ContextualAnimation/Tests)