# UAF Anim Node

> Nodes system for UAF.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画节点蓝图资产） |
| 模块 | `UAFAnimNode` (Runtime), `UAFAnimNodeEditor` (Runtime), `UAFAnimNodeUncookedOnly` (Runtime), `UAFAnimNodeTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-14 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFAnimNode) | |

## 用途

UAFAnimNode 是 UE5 统一动画框架（Unified Animation Framework, UAF）的**动画节点运行时系统**。它为 UAF 提供了一套完整的动画图节点基础设施，包括：

1. **动画节点实例化框架**：定义了 `FUAFAnimNode`（节点实例）和 `FUAFAnimNodeData`（节点共享数据）的分离架构——数据是可序列化的配置，实例是运行时对象
2. **动画操作（AnimOp）系统**：基于栈的求值管线，AnimOp 负责产生和操纵动画值、通知和同步贡献者
3. **混合与过渡系统**：提供 `FUAFBlendStack`、`FUAFTimedTransition`、`FUAFSimpleTransition` 等混合/过渡基础设施
4. **修改器节点**：通过 `FUAFModifierAnimNode` 实现对子节点的包装和修改（如播放速率缩放、根骨骼偏移、转向控制）
5. **具体动画节点**：序列播放器、布尔混合、动态叠加生成、叠加应用、输入值节点等
6. **工厂模式**：通过 `FUAFAnimNodeFactory` 和 `FUAFGraphFactoryAssetAnimNodeFactory` 支持从 UObject 或结构体创建节点实例
7. **GC 集成**：自定义引用收集器确保动画节点中的 UObject 引用被垃圾回收正确追踪

这个插件解决的核心问题是：在 AnimNext 图系统中提供一套高性能、可组合、支持过渡混合的动画节点运行时，作为 UAF 生态系统的动画执行层。

## 使用场景

- 你在使用 UAF 框架构建动画系统 → 用 UAFAnimNode 提供的节点类型和基础设施
- 你需要在 AnimNext 图中播放动画序列并支持混合过渡 → 使用 `FUAFSequencePlayer` + `FUAFSimpleTransition`
- 你需要根据布尔变量在两个动画状态间切换 → 使用 `FUAFBlendByBoolNode`
- 你需要对动画应用叠加效果（如瞄准叠加、受伤叠加）→ 使用 `FUAFApplyAdditive` 或 `FUAFMakeDynamicAdditive`
- 你需要程序化控制根骨骼偏移以减少脚滑 → 使用 `FUAFOffsetRootBoneNode`
- 你需要缩放动画播放速率 → 使用 `FUAFScalePlayRate`
- 你需要实现角色转向控制 → 使用 `FUAFSteeringNode`
- 你需要从图变量读取动画输入值 → 使用 `FUAFInputValueAnimNode`

## 蓝图用法

本插件主要面向 C++ 开发者，蓝图暴露有限。核心的 `FRigUnit_RunAnimNode_v2` 节点可在 AnimNext 图编辑器中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Run Anim Node` | 在 AnimNext 图中执行一个 UAF 动画节点，输出值包 | `FRigUnit_RunAnimNode_v2` |
| `Run Anim Node (Deprecated)` | 旧版执行节点，输出 LOD 姿态（已废弃） | `FRigUnit_RunAnimNode_v1` |

### AnimNext 图中的使用

在 AnimNext RigVM 图中，你可以：

1. 添加 **Run Anim Node** 节点
2. 通过 `AnimNode` 引脚配置要执行的动画节点（支持基础节点 + 修改器组合）
3. 通过 `AttributeSet` 指定要执行的属性集（留空则执行全部）
4. `Result` 输出引脚提供 `FUAFValueBundle` 结果
5. 通过 `ExecuteContext` 引脚连接执行流

## C++ 用法

### 头文件引入

```cpp
#include "UAF/AnimNodeCore/UAFAnimNode.h"
#include "UAF/AnimNodeCore/UAFAnimNodeData.h"
#include "UAF/AnimNodeCore/UAFAnimNodeFactory.h"
#include "UAF/AnimNodes/UAFSequencePlayer.h"
```

### 基本用法：创建和使用动画节点

动画节点采用**数据/实例分离**模式。数据（`FUAFAnimNodeData` 子类）是可序列化的配置，实例（`FUAFAnimNode` 子类）是运行时对象。

```cpp
#include "UAF/AnimNodeCore/UAFAnimNodeData.h"
#include "UAF/AnimNodes/UAFSequencePlayer.h"

using namespace UE::UAF;

// 创建序列播放器数据
FUAFSequencePlayerData SequenceData;
SequenceData.Sequence = MyAnimSequence;
SequenceData.LoopMode = EAnimAssetLoopMode::Auto;
SequenceData.StartTime = 0.0f;

// 从数据创建实例（需要更新上下文）
FUAFAnimNodePtr NodeInstance = SequenceData.CreateInstance(UpdateContext);
```

### 基本用法：使用修改器包装节点

```cpp
#include "UAF/AnimNodeCore/UAFAnimNodeDataEx.h"
#include "UAF/AnimNodes/UAFScalePlayRate.h"

using namespace UE::UAF;

// 创建基础序列播放器
FUAFSequencePlayerData BaseData;
BaseData.Sequence = MyAnimSequence;

// 创建播放速率修改器
FUAFScalePlayRateData ScaleData;
ScaleData.PlayRateMultiplier = 1.5f;

// 使用 FUAFAnimNodeDataEx 组合基础节点和修改器
TInstancedStruct<FUAFAnimNodeData> Base = TInstancedStruct<FUAFAnimNodeData>::Make(BaseData);
TArray<TInstancedStruct<FUAFModifierAnimNodeData>> Modifiers;
Modifiers.Add(TInstancedStruct<FUAFModifierAnimNodeData>::Make(ScaleData));

FUAFAnimNodeDataEx AnimNodeEx = FUAFAnimNodeDataEx::Make(Base, Modifiers);
```

### 进阶用法：注册自定义资产类型到工厂

```cpp
#include "UAF/AnimNodeCore/UAFAnimNodeFactory.h"

using namespace UE::UAF;

// 注册自定义 UObject 类型到 UAF 动画节点工厂
FTopLevelAssetPath AssetPath = FUAFAnimNodeFactory::RegisterAsset(
    UMyAnimAsset::StaticClass(),
    [](UObject* Object, FUAFAnimGraphUpdateContext& Context) -> FUAFAnimNodePtr
    {
        UMyAnimAsset* Asset = Cast<UMyAnimAsset>(Object);
        // 根据资产创建对应的动画节点实例
        return MakeRefCount<FUMyAnimNode>(Context, Asset);
    }
);

// 取消注册
FUAFAnimNodeFactory::UnregisterAsset(AssetPath);
```

### 进阶用法：实现自定义动画节点接口

```cpp
#include "UAF/AnimNodeCore/UAFAnimNodeInterfaceId.h"

using namespace UE::UAF;

// 定义自定义接口
struct IMyCustomInterface
{
    static constexpr FUAFAnimNodeInterfaceId InterfaceId = 
        FUAFAnimNodeInterfaceId::MakeFromString(TEXT("IMyCustomInterface"));
    
    virtual ~IMyCustomInterface() = default;
    virtual void MyCustomMethod() = 0;
};

// 在节点中实现接口
class FMyAnimNode : public FUAFAnimNode, public IMyCustomInterface
{
public:
    virtual void* GetInterface(FUAFAnimNodeInterfaceId Id) override
    {
        if (Id == IMyCustomInterface::InterfaceId)
            return static_cast<IMyCustomInterface*>(this);
        return nullptr;
    }
    
    virtual void MyCustomMethod() override { /* ... */ }
};

// 使用接口查询
FUAFAnimNodePtr Node = /* ... */;
if (IMyCustomInterface* Custom = Node->GetInterface<IMyCustomInterface>())
{
    Custom->MyCustomMethod();
}
```

## Demo 示例

### 自定义动画节点实现

```cpp
// MyCustomAnimNode.h
#pragma once

#include "UAF/AnimNodeCore/UAFAnimNode.h"
#include "UAF/AnimNodeCore/UAFAnimNodeData.h"
#include "UAF/AnimOpCore/UAFAnimOp.h"

namespace UE::UAF
{
    // 自定义 AnimOp：执行实际的动画操作
    USTRUCT()
    struct FMyCustomAnimOp : public FUAFAnimOp
    {
        GENERATED_BODY()
        UAF_DECLARE_ANIMOP(FMyCustomAnimOp)
        
        FMyCustomAnimOp() : FUAFAnimOp(1) // 1 个输入
        {
            InitializeAs<FMyCustomAnimOp>();
        }
        
        virtual void EvaluateValues(FUAFAnimOpValueEvaluator& Evaluator) override;
    };
    
    // 节点共享数据（可序列化配置）
    USTRUCT(DisplayName = "My Custom Node")
    struct FMyCustomAnimNodeData : public FUAFAnimNodeData
    {
        GENERATED_BODY()
        
        UPROPERTY(EditAnywhere, Category = "Data")
        float Speed = 1.0f;
        
        virtual FUAFAnimNodePtr CreateInstance(FUAFAnimGraphUpdateContext& Context) const override;
    };
    
    // 节点运行时实例
    class FMyCustomAnimNode : public FUAFAnimNode
    {
    public:
        explicit FMyCustomAnimNode(FUAFAnimGraphUpdateContext& Context, const FMyCustomAnimNodeData& InData);
        
        virtual void PreUpdate(FUAFAnimGraphUpdateContext& GraphContext) override;
        virtual void* GetInterface(FUAFAnimNodeInterfaceId Id) override { return nullptr; }
        
    private:
        const FMyCustomAnimNodeData& Data;
        FMyCustomAnimOp CustomOp;
    };
}
```

```cpp
// MyCustomAnimNode.cpp
#include "MyCustomAnimNode.h"

namespace UE::UAF
{
    FUAFAnimNodePtr FMyCustomAnimNodeData::CreateInstance(FUAFAnimGraphUpdateContext& Context) const
    {
        return MakeRefCount<FMyCustomAnimNode>(Context, *this);
    }
    
    FMyCustomAnimNode::FMyCustomAnimNode(FUAFAnimGraphUpdateContext& Context, const FMyCustomAnimNodeData& InData)
        : FUAFAnimNode(Context)
        , Data(InData)
    {
        // 将 AnimOp 注册到节点的 Pre-AnimOp
        SetPreAnimOp(&CustomOp);
    }
    
    void FMyCustomAnimNode::PreUpdate(FUAFAnimGraphUpdateContext& GraphContext)
    {
        // 在更新阶段执行自定义逻辑
        // ...
    }
    
    void FMyCustomAnimOp::EvaluateValues(FUAFAnimOpValueEvaluator& Evaluator)
    {
        // 在求值阶段操作动画值栈
        // ...
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UAF` | UAF 核心框架，提供动画资产、变量系统、值运行时等基础设施 |
| `AnimNext` | AnimNext 图系统，提供 RigUnit 基类、LOD 姿态、执行上下文等 |
| `StructUtils` | 结构体工具，提供 `TInstancedStruct` 等 |
| `RigVM` | RigVM 虚拟机，用于 AnimNext 图执行 |
| `AnimationCore` | 动画核心库，提供混合、姿态等基础类型 |
| `RewindDebugger` | 回放调试器，用于 UAF 追踪系统 |

## 维护状态

### 近期更新

- 2026-04-15 `8d8f8b4b` Implement blend overwrite and accumulate AnimOps
- 2026-04-14 `64a20049` Add newly relevant hint to allow nodes to be re-used
- 2026-04-14 `36403a6d` Add accessor to set the play rate
- 2026-04-14 `afb293fa` Add construction variants to AnimOp ArrayView
- 2026-04-14 `d1af965e` Add InputValue anim node/op

> 注：该插件创建于 2026-04-14，属于实验性新增插件，暂无更多 git 历史记录。

### 维护评价

- **创建时间**：2026-04-14，非常新的实验性插件
- **维护状态**：🆕 新创建，作为 UAF 生态系统的动画节点层
- **实验性标记**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，需要手动启用
- **代码规模**：118 个源文件，属于大型插件，架构成熟
- **已知限制**：
  - 实验性 API，可能在后续版本中发生重大变更
  - `FRigUnit_RunAnimNode_v1` 已标记为废弃，应使用 v2
  - 依赖 UAF 核心插件，不可独立使用
- **推荐**：仅推荐在 UAF 框架内部或实验性项目中使用，不建议在生产环境中依赖

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFAnimNode)
- [UAF 核心插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAF)