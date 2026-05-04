# Blend Stack

> Blend Stack API

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BlendStack` (Runtime), `BlendStackEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-30 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/BlendStack) | |

## 用途

Blend Stack 是 UE5 动画系统中的**动画混合栈**插件，用于在运行时动态地将多个动画资产（AnimSequence、BlendSpace）以栈的方式层叠混合。

与传统的 State Machine 或 BlendNode 不同，Blend Stack 采用**栈式管理**：每次通过 `BlendTo` 请求新动画时，新动画被压入栈顶并与当前动画混合。栈的最大深度由 `MaxActiveBlends` 控制（默认 4 层）。当栈满时，最底部的动画会被合并到一个存储姿态（stored pose）中，从而在有限内存下支持任意数量的动画过渡。

核心解决的问题：
- **程序化动画驱动**：代码（而非状态机图表）控制动画切换，适合 locomotion、motion matching 等需要高频动态切动画的场景
- **多动画并行混合**：支持同时混合多个动画，每个 player 有独立的混合时间、延迟激活、镜像、blend profile 等
- **与 Pose Search / Motion Matching 配合**：作为 pose search 结果的播放容器，支持 stitch animation（实验性）

## 使用场景

- 你在做 Motion Matching / Pose Search 系统，需要一个能动态接收搜索结果并平滑混合的动画播放器 → 用 BlendStack
- 你需要从 C++ 代码中频繁切换动画（如根据速度/方向连续切换 locomotion），但不想受 State Machine 的拓扑限制 → 用 BlendStack
- 你需要支持动画镜像（mirror）、BlendSpace 输入、延迟激活等高级混合控制 → 用 BlendStack
- 你需要在蓝图中通过 Anim Node Functions 动态控制动画切换 → 用 BlendStack 的 Blueprint Library

## 蓝图用法

Blend Stack 通过两个 Blueprint Function Library 暴露蓝图接口：`UBlendStackAnimNodeLibrary`（操作 BlendStack 节点）和 `UBlendStackInputAnimNodeLibrary`（查询 BlendStack Input 节点）。这些函数需要在 Anim Graph 的 **Anim Node Functions**（如 On Update、On Become Relevant）中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Convert To Blend Stack Node` | 将 AnimNodeReference 转换为 BlendStack 节点引用（带 exec pin） | `UBlendStackAnimNodeLibrary` |
| `Convert To Blend Stack Node (Pure)` | 同上，纯函数版本 | `UBlendStackAnimNodeLibrary` |
| `Blend To` | 请求混合到指定动画资产（AnimationAsset、时间、循环、镜像、混合时间等） | `UBlendStackAnimNodeLibrary` |
| `Blend To (With Settings)` | 同上但支持更多参数：BlendProfile、BlendOption、InertialBlend（实验性） | `UBlendStackAnimNodeLibrary` |
| `Force Blend On Next Update` | 强制下一次更新时重新混合（即使动画未变化） | `UBlendStackAnimNodeLibrary` |
| `Get Current Blend Stack Anim Asset` | 从 BlendStack Input 节点获取当前播放的动画资产 | `UBlendStackAnimNodeLibrary` |
| `Get Current Blend Stack Anim Asset Time` | 获取当前动画的已播放时间 | `UBlendStackAnimNodeLibrary` |
| `Get Current Blend Stack Anim Is Active` | 获取当前 player 是否处于活跃状态（未在 blend out） | `UBlendStackAnimNodeLibrary` |
| `Get Current Blend Stack Anim Asset Mirrored` | 获取当前动画是否为镜像状态 | `UBlendStackAnimNodeLibrary` |
| `Get Current Asset` | 获取 BlendStack 节点当前播放的动画资产 | `UBlendStackAnimNodeLibrary` |
| `Get Current Asset Time` | 获取当前动画已播放时间 | `UBlendStackAnimNodeLibrary` |
| `Get Current Asset Time Remaining` | 获取当前动画剩余播放时间 | `UBlendStackAnimNodeLibrary` |
| `Is Current Asset Looping` | 当前动画是否循环播放 | `UBlendStackAnimNodeLibrary` |
| `Convert To Blend Stack Input Node` | 将 AnimNodeReference 转换为 BlendStackInput 节点引用 | `UBlendStackInputAnimNodeLibrary` |
| `Get Properties` | 获取 BlendStackInput 节点的 AnimationAsset 和 AccumulatedTime | `UBlendStackInputAnimNodeLibrary` |

### 使用示例（蓝图描述）

1. 在 AnimGraph 中放置 **Blend Stack** 节点（Anim Graph 菜单 → BlendStack 分类）
2. Blend Stack 节点内嵌一个子图（BoundGraph），子图中包含 **Blend Stack Input** 节点和 **Blend Stack Result** 节点
3. 在子图中，将 BlendStackInput 连接到你的混合逻辑，最终输出到 BlendStackResult
4. 在 AnimGraph 的 **On Update** 函数中：
   - 添加 "Convert To Blend Stack Node" 节点，将 Self 引用转为 BlendStack 引用
   - 连接 "Blend To" 节点，指定目标 AnimationAsset、BlendTime、bLoop 等参数
   - 将 Update Context 和 BlendStack 引用传入

## C++ 用法

### 头文件引入

```cpp
#include "BlendStack/AnimNode_BlendStack.h"
#include "BlendStack/BlendStackAnimNodeLibrary.h"
```

### 基本用法

Blend Stack 主要通过 `FAnimNode_BlendStack` 或 `FAnimNode_BlendStack_Standalone` 使用。前者是带 pin 的可配置版本，后者是纯 C++ 驱动版本。

```cpp
// 在自定义 AnimInstance 或 AnimNode 中获取 BlendStack 节点并调用 BlendTo
// 来源: Source/Runtime/Public/BlendStack/AnimNode_BlendStack.h

// BlendTo 是核心方法，将新动画压入栈并开始混合
BlendStackNode->BlendTo(
    Context,
    AnimationAsset,        // UAnimationAsset* - AnimSequence 或 BlendSpace
    0.f,                   // AccumulatedTime - 起始时间
    true,                  // bLoop - 是否循环
    false,                 // bMirrored - 是否镜像
    nullptr,               // MirrorDataTable - 镜像数据表
    0.2f,                  // BlendTime - 混合时长(秒)
    nullptr,               // BlendProfile - 按骨骼混合配置
    EAlphaBlendOption::Linear,  // BlendOption - 混合曲线类型
    false,                 // bUseInertialBlend - 是否使用惯性混合
    NAME_None,             // InertialBlendNodeTag - 惯性混合节点标签
    FVector::Zero(),       // BlendParameters - BlendSpace 的 XY 参数
    1.f,                   // PlayRate - 播放速率
    0.f,                   // ActivationDelay - 激活延迟(秒)
    NAME_None,             // GroupName - 同步组名
    EAnimGroupRole::CanBeLeader,  // GroupRole
    EAnimSyncMethod::DoNotSync,   // Method
    false                  // bOverridePositionWhenJoiningSyncGroupAsLeader
);
```

### 进阶用法

```cpp
// 查询当前栈中播放的动画信息
// 来源: Source/Runtime/Private/BlendStackAnimNodeLibrary.cpp

UAnimationAsset* CurrentAsset = BlendStackNode->GetAnimAsset();
float CurrentTime = BlendStackNode->GetCurrentAssetTime();
float CurrentLength = BlendStackNode->GetCurrentAssetLength();
float AccumulatedTime = BlendStackNode->GetAccumulatedTime();
bool bLooping = BlendStackNode->IsLooping();
bool bMirrored = BlendStackNode->GetMirror();
FVector BlendParams = BlendStackNode->GetBlendParameters();

// 更新播放速率
BlendStackNode->UpdatePlayRate(2.0f);

// 强制下次更新时重新混合
BlendStackNode->ForceBlendNextUpdate();

// 重置整个 blend stack
BlendStackNode->Reset();
```

```cpp
// FBlendStackAnimPlayer 提供单个 player 的详细信息
// 来源: Source/Runtime/Public/BlendStack/AnimNode_BlendStack.h

// 查询 blend in 进度
float BlendPercentage = Player.GetBlendInPercentage();
float BlendInWeight = Player.GetBlendInWeight();

// 查询 player 状态
bool bActive = Player.IsActive();       // 是否正在活跃播放(未 blend out)
bool bPostponed = Player.IsPostponed(); // 是否在延迟激活中
float TimeToActivation = Player.GetTimeToActivation();

// 获取混合权重(按骨骼)
TArray<float> Weights;
Weights.SetNum(Player.GetBlendInWeightsNum());
Player.GetBlendInWeights(Weights);
```

## Demo 示例

### 最小 C++ 集成示例

```cpp
// MyBlendStackAnimInstance.h
#pragma once
#include "Animation/AnimInstance.h"
#include "MyBlendStackAnimInstance.generated.h"

UCLASS()
class UMyBlendStackAnimInstance : public UAnimInstance
{
    GENERATED_BODY()
public:
    // 要播放的动画资产，蓝图可配置
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Animation")
    UAnimationAsset* TargetAnimation = nullptr;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Animation")
    float BlendTime = 0.2f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Animation")
    bool bLoop = true;
};
```

在 AnimGraph 中使用：
1. 添加 **Blend Stack** 节点
2. 在 Blend Stack 子图中放置 **Blend Stack Input** → 你的混合逻辑 → **Blend Stack Result**
3. 在 AnimGraph 的 **On Update** Anim Node Function 中，使用 `Blend To` 蓝图节点驱动切换

### Build.cs 依赖

```csharp
// 你的模块 Build.cs
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject", 
    "Engine",
    "AnimationCore",
    "AnimGraphRuntime",
    "BlendStack",        // 添加此依赖
});
```

## 模块依赖

### BlendStack (Runtime)

| 模块 | 用途 |
|---|---|
| `Core` | 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `AnimationCore` | 动画核心数据结构 |
| `AnimGraphRuntime` | 动画图运行时（AnimNode 基类、SequencePlayer、BlendSpacePlayer 等） |

### BlendStackEditor (UncookedOnly)

| 模块 | 用途 |
|---|---|
| `AnimGraph` | AnimGraph 编辑器图节点基类 |
| `AnimGraphRuntime` | 运行时动画图类型 |
| `AnimationCore` | 动画核心数据结构 |
| `BlendStack` | 运行时模块（依赖自身） |
| `BlueprintGraph` (Private) | 蓝图图表支持 |
| `SlateCore` (Private) | UI 框架 |
| `UnrealEd` (Private) | 编辑器基础 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-08-27 | `74386d312d0f` | Fixup API macro usage | 编译宏修正，非功能性改动 |
| 2025-08-26 | `9a77cb5a8f74` | Fix for Blend Stack Input IsActive not working as expected | 修复 `IsActive` 在 BlendStackInput 上的行为 bug（UE-296821） |
| 2025-08-01 | `0c2b3551454e` | SlateCore several changes for code size | 非本插件功能性改动，SlateCore 重构波及 |

### 维护评价

- **创建时间**：2024-01-30，约 2 年前，属于较新的插件
- **维护状态**：**活跃维护中**。最近一次功能性更新在 2025 年 8 月（修复 IsActive bug），且该插件与 Pose Search / Motion Matching 等 Epic 重点推进的系统紧密关联
- **实验性标记**：插件 `EnabledByDefault=false`，且蓝图库类标记为 `Experimental`，API 可能随版本变化
- **已知限制**：
  - 不支持 AnimMontage（代码中有显式检查并报错）
  - BlendSpace 参数默认仅在首次 BlendTo 时更新（`InitialOnly` 模式），需手动设置 `BlendspaceUpdateMode` 来持续更新
  - Stitch 功能（用于 motion matching 的动画拼接过渡）标记为实验性
- **推荐使用**：如果你在构建程序化动画系统（特别是 motion matching 方向），推荐使用。如果只是简单的状态机动画切换，传统 State Machine 更合适

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/BlendStack)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- 测试用例：本插件目录内无独立测试文件，测试可能位于 Engine 测试目录中
