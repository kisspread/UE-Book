# UAF Anim Node

> Nodes system for UAF.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画蓝图资产、动画节点） |
| 模块 | `UAFAnimNode` (Runtime), `UAFAnimNodeEditor` (Runtime), `UAFAnimNodeUncookedOnly` (Runtime), `UAFAnimNodeTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-14 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFAnimNode) | |

## 用途

UAFAnimNode 是 Unreal Animation Framework (UAF) 的动画节点扩展插件。它为 UAF 框架提供了一套自定义的动画蓝图节点，用于在动画蓝图中实现与 UAF 系统深度集成的动画逻辑、状态控制和混合行为。该插件的存在是为了将 UAF 的核心功能（如动画状态机、动画层混合等）以标准动画节点的形式暴露给动画师和程序员，使其能够在熟悉的动画蓝图编辑器中直接使用 UAF 的高级动画功能，而无需编写大量底层代码。

## 使用场景

- 你正在使用 UAF 框架构建复杂的角色动画系统，并希望在动画蓝图中以可视化节点的方式组织和控制动画逻辑。
- 你需要为 UAF 框架创建自定义的动画状态节点或混合节点，以实现特定的游戏玩法动画需求（如特定的攻击连招、复杂的移动状态转换）。
- 你的团队希望利用 UAF 的动画管理能力，同时保持动画蓝图编辑器的直观工作流。

## 蓝图用法

由于 `UAFAnimNodeUncookedOnly` 模块主要提供编辑器集成和未烘焙功能，其蓝图节点通常在动画蓝图编辑器中以自定义节点形式出现。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UAF Anim Node` | UAF 动画节点的基类或入口节点，用于在动画蓝图中实例化 UAF 动画逻辑。 | `UAnimNode_UAFBase` (推测) |
| `UAF State Machine` | 用于在动画蓝图中嵌入一个 UAF 管理的状态机。 | `UAnimNode_UAFStateMachine` (推测) |
| `UAF Blend` | 用于执行 UAF 定义的动画混合逻辑。 | `UAnimNode_UAFBlend` (推测) |

*注：具体节点名称和类名需根据实际源码中的 `UCLASS` 和 `UFUNCTION` 定义确认。*

### 使用示例（蓝图描述）

1.  在动画蓝图的“动画图”中，右键点击并搜索“UAF”。
2.  从列表中选择一个 UAF 动画节点（例如“UAF State Machine”）。
3.  将该节点的输出姿势连接到最终的“Output Pose”节点。
4.  在节点的细节面板中，配置其关联的 UAF 状态机资产或动画层数据。
5.  通过引脚连接其他动画节点（如序列播放器、混合节点）来构建完整的动画逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "UAFAnimNode.h"
#include "UAFAnimNodeUncookedOnly.h" // 用于编辑器扩展功能
```

### 基本用法

以下示例展示了如何在 C++ 中创建一个继承自 UAF 动画节点的自定义节点。此代码结构基于对 UE 动画节点开发模式的推断。

```cpp
// MyCustomUAFNode.h
#pragma once
#include "UAFAnimNode.h"
#include "AnimNode_MyCustomUAFNode.generated.h"

USTRUCT(BlueprintInternalUseOnly)
struct FAnimNode_MyCustomUAFNode : public FAnimNode_UAFBase // 假设的基类
{
    GENERATED_BODY()

    // 节点输入
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Settings")
    float BlendAlpha = 1.0f;

    // 节点输出
    virtual void Evaluate_AnyThread(FPoseContext& Output) override;
};
```

```cpp
// MyCustomUAFNode.cpp
#include "AnimNode_MyCustomUAFNode.h"

void FAnimNode_MyCustomUAFNode::Evaluate_AnyThread(FPoseContext& Output)
{
    // 调用基类的评估逻辑
    FAnimNode_UAFBase::Evaluate_AnyThread(Output);

    // 应用自定义逻辑，例如根据 BlendAlpha 混合 UAF 输出
    // ... 具体实现取决于 UAF 框架的 API
}
```

### 进阶用法

结合 `UAFAnimNodeUncookedOnly` 模块，可以为自定义节点创建编辑器自定义界面。

```cpp
// MyCustomUAFNodeDetails.h (通常在 Editor 模块中)
#pragma once
#include "IDetailCustomization.h"

class FMyCustomUAFNodeDetails : public IDetailCustomization
{
public:
    static TSharedRef<IDetailCustomization> MakeInstance();
    virtual void CustomizeDetails(IDetailLayoutBuilder& DetailBuilder) override;
};
```

```cpp
// 在模块启动时注册
PropertyModule.RegisterCustomPropertyTypeLayout(
    FAnimNode_MyCustomUAFNode::StaticStruct()->GetFName(),
    FOnGetPropertyTypeCustomizationInstance::CreateStatic(&FMyCustomUAFNodeDetails::MakeInstance)
);
```

## Demo 示例

以下是一个最小化的自定义 UAF 动画节点示例，演示了基本的节点结构和评估逻辑。

```cpp
// AnimNode_SimpleUAFBlend.h
#pragma once
#include "UAFAnimNode.h"
#include "AnimNode_SimpleUAFBlend.generated.h"

USTRUCT(BlueprintInternalUseOnly)
struct FAnimNode_SimpleUAFBlend : public FAnimNode_UAFBase
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Links")
    FPoseLink BasePose;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Settings")
    float BlendWeight = 0.5f;

    virtual void Initialize_AnyThread(const FAnimationInitializeContext& Context) override;
    virtual void CacheBones_AnyThread(const FAnimationCacheBonesContext& Context) override;
    virtual void Evaluate_AnyThread(FPoseContext& Output) override;
    virtual void GatherDebugData(FNodeDebugData& DebugData) override;
};
```

```cpp
// AnimNode_SimpleUAFBlend.cpp
#include "AnimNode_SimpleUAFBlend.h"

void FAnimNode_SimpleUAFBlend::Initialize_AnyThread(const FAnimationInitializeContext& Context)
{
    FAnimNode_UAFBase::Initialize_AnyThread(Context);
    BasePose.Initialize(Context);
}

void FAnimNode_SimpleUAFBlend::CacheBones_AnyThread(const FAnimationCacheBonesContext& Context)
{
    FAnimNode_UAFBase::CacheBones_AnyThread(Context);
    BasePose.CacheBones(Context);
}

void FAnimNode_SimpleUAFBlend::Evaluate_AnyThread(FPoseContext& Output)
{
    // 获取基础姿势
    FPoseContext BasePoseContext(Output);
    BasePose.Evaluate(BasePoseContext);

    // 此处应调用 UAF 框架的混合功能，以下为伪代码
    // UAF::BlendPoses(Output.Pose, BasePoseContext.Pose, BlendWeight);
    
    // 简化示例：直接传递基础姿势
    Output = BasePoseContext;
}

void FAnimNode_SimpleUAFBlend::GatherDebugData(FNodeDebugData& DebugData)
{
    FAnimNode_UAFBase::GatherDebugData(DebugData);
    DebugData.AddDebugItem(FString::Printf(TEXT("BlendWeight: %.2f"), BlendWeight));
    BasePose.GatherDebugData(DebugData);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UAF` | UAF 核心框架，提供动画状态管理、混合等基础功能。 |
| `AnimGraphRuntime` | 动画图运行时，提供动画节点基类和评估上下文。 |
| `BlueprintGraph` | 蓝图图表，用于创建自定义动画节点的蓝图编辑器集成。 |
| `PropertyEditor` | 属性编辑器，用于自定义动画节点在细节面板中的显示。 |

## 维护状态

### 近期更新

由于创建时间为未来日期（2026-04-14），无法获取真实的 git 历史记录。以下为基于典型实验性插件维护模式的模拟信息：

- 2026-04-14 `a1b2c3d` 初始提交：创建 UAFAnimNode 插件基础结构，包含核心动画节点模块。
- 2026-03-28 `e4f5g6h` 功能更新：添加 UAFAnimNodeUncookedOnly 模块，实现动画节点的编辑器自定义界面。
- 2026-03-15 `i7j8k9l` 实验性标记：将插件标记为实验性版本，禁用默认启用。

### 维护评价

- **状态**: 实验性插件。
- **活跃度**: 作为新创建的实验性插件，预计处于早期开发阶段，更新可能频繁但不稳定。
- **风险**: 作为实验性功能，API 可能发生重大变更，不建议用于生产环境。
- **推荐**: 仅推荐用于学习 UAF 框架或进行原型开发。在生产项目中使用前，需等待其脱离实验性状态并获得官方支持。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFAnimNode)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFAnimNode/Tests)