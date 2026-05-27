# Blend Stack

> Blend Stack API（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 混合栈 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BlendStack` (Runtime), `BlendStackEditor` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2024-01-30 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/BlendStack) | |

## 用途

Blend Stack 插件提供了一套**多动画混合栈**系统，用于在同一动画图表节点中同时管理多个动画播放器的混合过渡。

传统动画蓝图中，状态机或混合节点通常只处理两个动画之间的过渡。当需要快速连续切换多个动画时（例如角色连续受到攻击、快速执行多个动作），传统方案容易出现动画跳变或过渡被打断。Blend Stack 通过维护一个固定大小的**动画播放器栈**来解决这个问题：

- 新动画加入时，自动与栈中所有活跃动画进行混合
- 当栈满时，最旧/权重最低的动画会被移除或合并到存储姿态中
- 每个栈中的动画播放器支持独立的混合时间、播放速率、镜像、混合空间参数等配置
- 支持基于骨骼的逐骨骼混合权重（通过 Blend Profile）

核心解决的问题是：**在有限的混合资源预算下，实现多个动画之间的平滑、优先级可控的连续过渡**。

## 使用场景

- **动作游戏**：角色快速连续执行轻攻击→重攻击→闪避，每个动作有不同混合时间和优先级
- **物理驱动的动画**：基于 Pose Search（姿态搜索）找到最佳匹配动画后，通过 BlendTo 平滑过渡
- **动画拼接（Animation Stitching）**：利用实验性的 StitchDatabase 在动画之间寻找最佳拼接点进行混合
- **复杂角色状态**：需要同时播放待机→行走→受伤→换弹等多个动画层的混合
- **同步组动画**：多个角色需要同步动画播放节奏（如协作者动画），支持 Leader/Follower 角色

## 蓝图用法

Blend Stack 提供两个蓝图函数库类，分别用于操作主混合栈节点和输入节点。

### 核心节点

#### 节点转换

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Convert To Blend Stack Node` | 将 AnimNodeReference 转换为 BlendStack 节点引用 | `UBlendStackAnimNodeLibrary` |
| `Convert To Blend Stack Node (Pure)` | 同上，纯函数版本，返回 bool 表示是否成功 | `UBlendStackAnimNodeLibrary` |
| `Convert To Blend Stack Input Node` | 将 AnimNodeReference 转换为 BlendStackInput 节点引用 | `UBlendStackInputAnimNodeLibrary` |

#### 混合控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Blend To` | 触发向指定动画资产的混合过渡 | `UBlendStackAnimNodeLibrary` |
| `Blend To (With Settings)` | 带完整设置的混合过渡（可指定 BlendProfile、BlendOption、惯性混合） | `UBlendStackAnimNodeLibrary` |
| `Force Blend On Next Update` | 强制在下一帧执行混合（即使动画未变化） | `UBlendStackAnimNodeLibrary` |

#### 状态查询

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Current Blend Stack Anim Asset` | 获取 BlendStack Input 当前播放的动画资产 | `UBlendStackAnimNodeLibrary` |
| `Get Current Blend Stack Anim Asset Time` | 获取 BlendStack Input 当前动画时间 | `UBlendStackAnimNodeLibrary` |
| `Get Current Blend Stack Anim Is Active` | 判断当前动画是否处于活跃状态 | `UBlendStackAnimNodeLibrary` |
| `Get Current Blend Stack Anim Asset Mirrored` | 判断当前动画是否为镜像状态 | `UBlendStackAnimNodeLibrary` |
| `Get Current Blend Stack Anim Asset Mirror Table` | 获取当前镜像数据表 | `UBlendStackAnimNodeLibrary` |
| `Get Current Asset` | 获取主混合栈节点的当前动画资产 | `UBlendStackAnimNodeLibrary` |
| `Get Current Asset Time` | 获取主混合栈节点的当前动画时间 | `UBlendStackAnimNodeLibrary` |
| `Get Current Asset Time Remaining` | 获取主混合栈节点当前动画剩余时间 | `UBlendStackAnimNodeLibrary` |
| `Is Current Asset Looping` | 判断当前动画是否循环播放 | `UBlendStackAnimNodeLibrary` |

#### BlendStack Input 节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Properties` | 获取输入节点的动画资产和已累积时间 | `UBlendStackInputAnimNodeLibrary` |

### 使用示例（蓝图描述）

**基本 BlendTo 用法**：

在 Anim Graph 的"Anim Function"或"Anim Instance"事件图中：

1. 使用 `Convert To Blend Stack Node` 将节点引用转换为 `FBlendStackAnimNodeReference`
2. 调用 `Blend To` 节点，传入目标 `AnimationAsset`、`BlendTime`（如 0.3）、是否 `bLoop`、`bMirrored` 等参数
3. 可通过 `WantedPlayRate` 控制播放速率，`ActivationDelay` 延迟激活

**高级混合设置**：

使用 `Blend To (With Settings)` 节点可额外指定：
- `BlendProfile`：逐骨骼混合权重
- `BlendOption`：混合曲线类型（Linear、HermiteCubic 等）
- `bInertialBlend`：启用惯性混合，配合 `InertialBlendNodeTag` 指定处理节点

**带输入节点的用法**：

在每个 Blend Stack 的样本图（Sample Graph）中放置 `FAnimNode_BlendStackInput` 节点，然后在 Anim Function 中：
1. `Convert To Blend Stack Input Node` 获取输入引用
2. `Get Properties` 获取当前正在播放的动画资产和时间
3. 可在输入节点上设置 `bOverridePlayRate` 和 `PlayRate` 来控制特定样本的播放速率

## C++ 用法

### 头文件引入

```cpp
#include "BlendStack/AnimNode_BlendStack.h"
#include "BlendStack/BlendStackAnimNodeLibrary.h"
#include "BlendStack/AnimNode_BlendStackInput.h"
```

### 基本用法

`FAnimNode_BlendStack` 是一个动画图表节点结构体，通常在自定义动画实例中直接使用其 `BlendTo` 方法来驱动动画混合：

```cpp
// 来源: AnimNode_BlendStack.h - FAnimNode_BlendStack_Standalone::BlendTo
// 在自定义 AnimInstance 或 AnimNode 函数中触发混合
void UMyAnimInstance::PlayAction(UAnimationAsset* NewAction)
{
    // 获取动画蓝图中的 BlendStack 节点（通常通过 Pin 或缓存引用）
    FAnimNode_BlendStack* BlendStackNode = GetBlendStackNode();
    if (!BlendStackNode)
    {
        return;
    }

    // 触发向新动画的混合过渡
    // 参数: Context, AnimationAsset, AccumulatedTime, bLoop, bMirrored,
    //        MirrorDataTable, BlendTime, BlendProfile, BlendOption,
    //        bUseInertialBlend, InertialBlendNodeTag, BlendParameters, PlayRate, ActivationDelay
    FAnimationUpdateContext Context = /* ... 获取当前动画上下文 */;
    BlendStackNode->BlendTo(
        Context,
        NewAction,          // 目标动画资产
        0.f,                // 从头开始
        false,              // 不循环
        false,              // 不镜像
        nullptr,            // 无镜像数据表
        0.3f,               // 0.3 秒混合时间
        nullptr,            // 无自定义混合配置
        EAlphaBlendOption::HermiteCubic,  // Hermite 混合曲线
        false,              // 不使用惯性混合
        NAME_None,          // 无惯性混合节点标签
        FVector::Zero(),    // 混合空间参数
        1.0f,               // 播放速率
        0.f                 // 无激活延迟
    );
}
```

### 蓝图可调用属性配置

通过编辑器中 `FAnimNode_BlendStack` 暴露的属性来配置节点行为：

```cpp
// 来源: AnimNode_BlendStack.h - FAnimNode_BlendStack 属性
// 在动画蓝图编辑器中设置以下属性：

// 最大同时活跃混合数（超过此数量时旧动画被丢弃或合并）
BlendStackNode->SetMaxActiveBlends(4);

// 混合时间
// BlendTime = 0.2f;

// 是否启用惯性混合（配合 InertialBlendNodeTag 使用）
// bUseInertialBlend = true;
// InertialBlendNodeTag = FName("InertializationNode");

// 当栈满时是否存储混合姿态（true=合并到存储姿态，false=丢弃动画以节省内存）
// bStoreBlendedPose = true;

// 混合空间参数更新模式
// BlendspaceUpdateMode = EBlendStack_BlendspaceUpdateMode::UpdateActiveOnly;
```

### 蓝图库函数调用

```cpp
// 来源: BlendStackAnimNodeLibrary.h - UBlendStackAnimNodeLibrary
// 在 AnimInstance 的 AnimNode 函数中使用

// 1. 转换节点引用
FBlendStackAnimNodeReference BlendStackRef;
EAnimNodeReferenceConversionResult Result;
BlendStackRef = UBlendStackAnimNodeLibrary::ConvertToBlendStackNode(NodeRef, Result);

if (Result == EAnimNodeReferenceConversionResult::Succeeded)
{
    // 2. 查询当前状态
    UAnimationAsset* CurrentAsset = UBlendStackAnimNodeLibrary::GetCurrentAsset(BlendStackRef);
    float CurrentTime = UBlendStackAnimNodeLibrary::GetCurrentAssetTime(BlendStackRef);
    float TimeRemaining = UBlendStackAnimNodeLibrary::GetCurrentAssetTimeRemaining(BlendStackRef);
    bool bLooping = UBlendStackAnimNodeLibrary::IsCurrentAssetLooping(BlendStackRef);
}
```

### 进阶用法

**使用同步组（Sync Group）实现多角色动画同步**：

```cpp
// 来源: AnimNode_BlendStack.h - FAnimNode_BlendStack 的 Sync 属性
// FAnimNode_BlendStack 支持动画同步组，可将多个 BlendStack 节点加入同一组进行同步

// 在动画蓝图编辑器中配置（WITH_EDITORONLY_DATA 区域的属性）：
// GroupName = FName("WalkSync");        // 同步组名称
// GroupRole = EAnimGroupRole::CanBeLeader;  // 角色：Leader 或 Follower
// Method = EAnimSyncMethod::Sync;       // 同步方法

// Follower 的前一个动画同步配置
// PrevGroupName = FName("WalkSync");
// PrevGroupRole = EAnimGroupRole::CanBeLeader;
// PrevMethod = EAnimSyncMethod::Sync;
```

**通过输入节点控制特定样本的播放速率**：

```cpp
// 来源: AnimNode_BlendStackInput.h - FAnimNode_BlendStackInput
// 在 BlendStack 的 Sample Graph 中，BlendStackInput 节点可以单独控制播放速率

// 在动画蓝图编辑器中设置输入节点属性：
// bOverridePlayRate = true;  // 启用播放速率覆盖
// PlayRate = 0.5f;           // 以半速播放此样本

// 此设置会覆盖 BlendStack 中 SequencePlayer 或 BlendSpacePlayer 的播放速率
```

## Demo 示例

以下示例展示了一个自定义动画节点，它包装了 `FAnimNode_BlendStack` 并暴露了两个输出姿态链接：

```cpp
// MyBlendStackNode.h
#pragma once

#include "Animation/AnimNodeBase.h"
#include "BlendStack/AnimNode_BlendStack.h"

USTRUCT(BlueprintInternalUseOnly)
struct FAnimNode_MyBlendStack : public FAnimNode_Base
{
    GENERATED_BODY()

public:
    // 目标动画资产（蓝图可配置）
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = Settings, meta = (PinHiddenByDefault))
    TObjectPtr<UAnimationAsset> AnimationAsset;

    // 混合时间
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = Settings, meta = (PinHiddenByDefault, ClampMin = "0"))
    float BlendTime = 0.2f;

    // 最大同时活跃混合数
    UPROPERTY(EditAnywhere, Category = Settings, meta = (ClampMin = "0"))
    int32 MaxActiveBlends = 4;

    // FAnimNode_Base 接口
    virtual void Initialize_AnyThread(const FAnimationInitializeContext& Context) override;
    virtual void CacheBones_AnyThread(const FAnimationCacheBonesContext& Context) override;
    virtual void Update_AnyThread(const FAnimationUpdateContext& Context) override;
    virtual void Evaluate_AnyThread(FPoseContext& Output) override;
    virtual void GatherDebugData(FNodeDebugData& DebugData) override;

private:
    // 内部的 BlendStack 节点
    UPROPERTY()
    FAnimNode_BlendStack_Standalone InternalBlendStack;
};
```

```cpp
// MyBlendStackNode.cpp
#include "MyBlendStackNode.h"

void FAnimNode_MyBlendStack::Initialize_AnyThread(const FAnimationInitializeContext& Context)
{
    // 初始化内部的 BlendStack 节点
    InternalBlendStack.SetMaxActiveBlends(MaxActiveBlends);
    InternalBlendStack.Initialize_AnyThread(Context);
}

void FAnimNode_MyBlendStack::CacheBones_AnyThread(const FAnimationCacheBonesContext& Context)
{
    InternalBlendStack.CacheBones_AnyThread(Context);
}

void FAnimNode_MyBlendStack::Update_AnyThread(const FAnimationUpdateContext& Context)
{
    // 如果设置了动画资产，触发混合
    if (AnimationAsset)
    {
        InternalBlendStack.BlendTo(
            Context,
            AnimationAsset,
            0.f,                // AccumulatedTime
            true,               // bLoop
            false,              // bMirrored
            nullptr,            // MirrorDataTable
            BlendTime
        );
    }

    InternalBlendStack.Update_AnyThread(Context);
}

void FAnimNode_MyBlendStack::Evaluate_AnyThread(FPoseContext& Output)
{
    InternalBlendStack.Evaluate_AnyThread(Output);
}

void FAnimNode_MyBlendStack::GatherDebugData(FNodeDebugData& DebugData)
{
    FString DebugDesc = FString::Printf(TEXT("MyBlendStack: %s"),
        AnimationAsset ? *AnimationAsset->GetName() : TEXT("None"));
    DebugData.AddDebugItem(DebugDesc);

    InternalBlendStack.GatherDebugData(DebugData);
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等基础模块）。BlendStack 模块主要依赖 UE 动画系统基础模块（AnimGraphRuntime、AnimationCore 等），这些是动画相关插件的常见依赖。BlendStackEditor 模块额外依赖 UnrealEd 及 BlendStack 运行时模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移至新的 UE_LOGF 格式 |
| 2026-01-27 | `62ce2078` | BlendStack - logging errors in FAnimNode_BlendStack_Standalone::InternalBlendTo if inconsistent an E | 修复 InternalBlendTo 中不一致动画事件的错误日志 |
| 2026-01-22 | `1d9e2356` | BlendStack - sync group support for follower blendstacks | 新增 Follower 模式的混合栈同步组支持 |
| 2026-01-09 | `520bb55e` | PoseSearch - fix for misspelled words | 修正拼写错误（关联 PoseSearch 重构） |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将插件配置文件重命名为 Default 命名规范 |

### 维护评价

Blend Stack 插件创建于 2024 年 1 月，从 Experimental 文件夹迁出后独立为正式插件。目前处于**活跃维护**状态：

- **更新频率**：近期保持每月/每两月的功能性更新节奏，2026 年初密集增加了同步组支持和错误处理改进
- **代码质量**：头文件注释清晰，UFUNCTION 宏标注了线程安全（BlueprintThreadSafe），属性带有编辑器元数据约束
- **实验性功能**：部分功能（如 StitchDatabase 动画拼接、BlendToWithSettings）标记为 Experimental，API 可能变更
- **EnabledByDefault=false**：该插件默认未启用，需要在项目设置中手动开启

**推荐使用**：对于需要管理复杂动画混合的游戏项目（特别是动作游戏、使用 Pose Search 的项目），Blend Stack 是官方推荐的多动画混合方案，值得启用和使用。注意实验性功能（Stitch、部分 BlendCurve 修复）可能在未来版本中有行为变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/BlendStack)
- [官方文档]()（暂无）