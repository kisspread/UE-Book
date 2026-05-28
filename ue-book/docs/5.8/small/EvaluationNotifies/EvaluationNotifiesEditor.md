# Evaluation Notifies

> A system for animation notifies which have animation evaluation time code.

| 属性 | 值 |
|---|---|
| 中文名 | 评估通知 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `EvaluationNotifiesRuntime` (Runtime), `EvaluationNotifiesEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-11-23 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EvaluationNotifies) | |

## 用途

EvaluationNotifies 是一个扩展动画评估管线的通知系统，让动画通知（Notify）能够在**动画评估时间码**（evaluation time code）上触发，而不是传统的游戏时间轴上触发。

标准的动画通知基于序列播放进度触发，在游戏帧率不稳定或动画发生缩放/重映射时可能出现时机偏移。EvaluationNotifies 将通知与动画评估管线深度集成，确保通知在正确的动画评估点精确触发，这对以下场景至关重要：

- **MotionWarping**（运动扭曲）：根运动需要在精确的动画时间点进行修改
- **根运动预计算**：运动扭曲的预计算变形需要精确的评估时机
- **UAF 动画框架**：与 Epic 实验性动画框架的状态机/时间线系统协同工作
- **RigVM 驱动的动画**：节点图驱动的动画评估中需要通知回调

## 使用场景

- 你在使用 MotionWarping 做运动匹配/跃迁动画 → 需要在精确的动画评估点触发对齐/变形逻辑
- 你在基于 UAF 构建动画状态机，时间线查询可能失败 → 需要健壮的通知派发机制
- 你正在尝试根运动预计算扭曲 → 需要通知在评估时间码上精确触发

> ⚠️ 此插件为实验性功能，默认未启用。需要在插件设置中手动启用，且依赖 AnimationWarping、RigVM、UAF、UAFAnimGraph 等实验性插件。

## 蓝图用法

此插件提供了一个动画图节点，可在动画蓝图中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Evaluation Notifies` | 动画图节点，将通知与动画评估时间码绑定，支持骨骼控制操作 | `UAnimGraphNode_EvaluationNotifies` |

### 使用示例（蓝图描述）

1. 在动画蓝图的 AnimGraph 中，右键添加 **Evaluation Notifies** 节点
2. 该节点作为骨骼控制基础节点（Skeletal Control Base），具有输入/输出引脚和属性链接
3. 在 Details 面板中配置节点属性（`FAnimNode_EvaluationNotifies`）
4. 节点支持输入/输出链接属性（`GetInputLinkAttributes` / `GetOutputLinkAttributes`），可与其他动画图节点进行属性级联
5. 编译时节点会自动校验骨骼兼容性（`ValidateAnimNodeDuringCompilation`）

## C++ 用法

### 头文件引入

```cpp
#include "AnimGraphNode_EvaluationNotifies.h"      // 编辑器节点
// Runtime 模块头文件（从依赖推断）
#include "AnimNode_EvaluationNotifies.h"           // 运行时动画节点
```

### 基本用法

从 AnimGraph 节点的接口可以推断运行时节点的基本用法：

```cpp
// 创建运行时动画节点
FAnimNode_EvaluationNotifies EvaluationNotifyNode;

// 该节点继承自 FAnimNode_SkeletalControlBase，支持标准的
// EvaluateSkeletalControl_AnyThread / EvaluateComponentSpace_AnyThread 调用
// 通知将在动画评估期间基于时间码触发
```

*（来源：Public/AnimGraph/AnimGraphNode_EvaluationNotifies.h 中的 `FAnimNode_EvaluationNotifies Node` 成员）*

### 进阶用法

基于 git 历史中的功能变更，此系统支持以下进阶场景：

```cpp
// MotionWarping 集成 - 对齐通知实例
// 当没有动画序列播放时，通知派发会优雅地失败（而非崩溃）
// 参见 commit 1be7393a

// 根运动预计算扭曲
// FAlignmentNotifyInstance::GetWeight 支持通知权重查询
// 参见 commit 8ce934ce
```

## Demo 示例

由于此插件为实验性功能，且运行时模块源码未完全公开，以下为最小编辑器节点扩展示例：

```cpp
// MyEvaluationNotifyNode.h
#pragma once

#include "AnimGraphNode_EvaluationNotifies.h"
#include "MyEvaluationNotifyNode.generated.h"

UCLASS()
class UMyEvaluationNotifyNode : public UAnimGraphNode_EvaluationNotifies
{
    GENERATED_BODY()

public:
    // 自定义节点标题
    virtual FText GetNodeTitle(ENodeTitleType::Type TitleType) const override
    {
        return FText::FromString(TEXT("My Custom Evaluation Notify"));
    }
};
```

> 注：实际使用时，直接使用 `UAnimGraphNode_EvaluationNotifies` 节点即可，无需子类化。

## 模块依赖

从插件依赖关系和模块结构推断：

| 模块 | 用途 |
|---|---|
| `AnimationWarping` | 运动扭曲评估支持 |
| `RigVM` | RigVM 动画节点图集成 |
| `UAF` | Unreal Animation Framework 核心 |
| `UAFAnimGraph` | UAF 动画图集成 |

> 注：此插件对 UAF 生态有强依赖，未启用 UAF 系列插件将无法使用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-24 | `42548e51` | Fix non-unity build: forward-declare UAnimationAsset in anim node headers | 修复非统一构建问题，前向声明 UAnimationAsset |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到 UE_LOGF 新日志宏 |
| 2026-04-10 | `8ce934ce` | MotionWarping - fix for FAlignmentNotifyInstance::GetWeight and URootMotionModifier_PrecomputedWarp | 修复 MotionWarping 对齐通知权重和预计算扭曲 |
| 2026-02-09 | `1be7393a` | Gracefully handle notify dispatch failure when no animation sequence is playing | 无动画播放时通知派发失败的优雅处理 |
| 2025-11-24 | `1e8772b6` | UAF: Timelines can now fail state & delta queries | UAF 时间线查询支持失败状态处理 |

### 维护评价

- **实验性插件**：由 Epic Games 维护，处于积极开发阶段
- **活跃维护**：2026 年 4 月仍有功能性更新和修复（MotionWarping 集成修复、构建系统适配）
- **强依赖 UAF 生态**：与 Unreal Animation Framework 紧密耦合，随 UAF 演进而更新
- **使用建议**：适合正在使用 MotionWarping + UAF 技术栈的开发者进行实验性探索，暂不建议用于生产环境。需要关注 UAF 系列插件的整体成熟度。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EvaluationNotifies)
- [AnimationWarping 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/AnimationWarping)