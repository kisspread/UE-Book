# UAF Anim Node

> Nodes system for UAF.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资产、调试工具） |
| 模块 | `UAFAnimNode` (Runtime), `UAFAnimNodeEditor` (Runtime), `UAFAnimNodeUncookedOnly` (Runtime), `UAFAnimNodeTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-14 |
| 年龄标签 | 🆕（约 -1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFAnimNode) | |

## 用途

UAFAnimNode 是 Unreal Animation Framework (UAF) 的扩展插件，主要提供两个核心功能：
1.  **自定义动画节点**：为 UAF 动画系统提供可扩展的动画节点（AnimNode）框架，允许开发者创建和集成自定义的动画逻辑。
2.  **动画调试与分析**：深度集成 Unreal 的 **Rewind Debugger** 系统，为 UAF 动画图（AnimGraph）提供强大的录制、回放和可视化调试能力。它能够追踪动画节点的更新、权重变化以及内部状态值，帮助开发者诊断复杂的动画问题。

简而言之，这个插件解决了在使用 UAF 动画系统时，如何高效地创建自定义动画逻辑以及如何调试这些复杂动画行为的问题。

## 使用场景

-   你正在使用 UAF 动画系统构建角色动画，并且需要实现一个标准动画蓝图节点无法满足的特殊动画效果（如程序化 IK、复杂的混合逻辑）→ 使用此插件提供的框架创建自定义动画节点。
-   你的 UAF 动画逻辑出现异常（如动画抖动、权重错误），需要查看动画图运行时每个节点的实时权重和内部数据 → 使用此插件集成的 Rewind Debugger 功能进行录制和分析。
-   你需要为动画师或技术美术提供一个可视化的调试工具，以便他们理解动画状态机的运行流程和节点间的依赖关系。

## 蓝图用法

当前提供的 `UAFAnimNodeEditor` 模块主要包含编辑器集成和调试工具，其核心功能（如动画节点定义）通常在 `UAFAnimNode` 运行时模块中。基于现有头文件，主要的蓝图交互点集中在编辑器工具和数据工厂上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateUAFAnimNodeDataFromObject` | 从一个 UObject（如动画序列资产）创建对应的 UAF 动画节点数据结构。这是一个编辑器工具函数，用于支持拖放操作。 | `FUAFAnimNodeDataFactory` |

### 使用示例（蓝图描述）

在编辑器中，当你将一个支持的资产（例如 `UAnimSequence`）拖拽到 UAF 动画节点图的某个数据插槽上时，系统内部会调用 `FUAFAnimNodeDataFactory::CreateUAFAnimNodeDataFromObject` 来将资产转换为节点可理解的数据格式。这个过程对用户透明，但开发者可以通过注册自定义的工厂来扩展支持的资产类型。

## C++ 用法

### 头文件引入

```cpp
// 用于创建动画节点数据
#include "UAFAnimNodeDataFactory.h"

// 用于集成 Rewind Debugger 调试轨道
#include "RewindDebugger/UAFAnimNodeTrack.h"
#include "RewindDebugger/UAFAnimOpTrack.h"
```

### 基本用法

**1. 注册自定义的动画节点数据工厂**

这是扩展 UAF 动画系统支持新资产类型的核心方法。你需要定义一个从 `UObject` 到 `FUAFAnimNodeData` 派生结构的转换函数。

```cpp
// MyCustomAnimNodeData.h
#pragma once
#include "UAF/AnimNodeCore/UAFAnimNode.h"

USTRUCT()
struct FMyCustomAnimNodeData : public FUAFAnimNodeData
{
    GENERATED_BODY()
    // 自定义数据字段
    UPROPERTY()
    float CustomParam;
};

// MyModule.cpp
#include "UAFAnimNodeDataFactory.h"
#include "MyCustomAnimNodeData.h"
#include "MyCustomAsset.h" // 假设你有一个自定义资产类

void RegisterMyCustomFactory()
{
    // 注册工厂：当用户将 UMyCustomAsset 拖放到节点时，创建 FMyCustomAnimNodeData
    FTopLevelAssetPath RegistrationHandle = FUAFAnimNodeDataFactory::RegisterAsset<FMyCustomAnimNodeData, UMyCustomAsset>(
        [](UMyCustomAsset* Asset) -> FMyCustomAnimNodeData
        {
            FMyCustomAnimNodeData Data;
            Data.CustomParam = Asset->SomeValue; // 从资产提取数据
            return Data;
        }
    );
    // 保存 RegistrationHandle 以便在模块关闭时调用 UnregisterAsset
}

void UnregisterMyCustomFactory(FTopLevelAssetPath Handle)
{
    FUAFAnimNodeDataFactory::UnregisterAsset(Handle);
}
```
*来源：基于 `Public/UAFAnimNodeDataFactory.h` 中的模板函数推断。*

### 进阶用法

**2. 为自定义动画系统创建 Rewind Debugger 调试轨道**

如果你的动画系统需要深度调试，可以参考 `UAFAnimNodeEditor` 模块中的实现，创建自己的分析器（Analyzer）、提供者（Provider）和轨道（Track）。

```cpp
// 假设你有一个自定义的动画提供者
class FMyAnimProvider : public TraceServices::IProvider
{
    // ... 实现数据存储和读取接口
};

// 创建对应的分析器，用于解析 Trace 数据
class FMyAnimAnalyzer : public UE::Trace::IAnalyzer
{
public:
    FMyAnimAnalyzer(TraceServices::IAnalysisSession& InSession, FMyAnimProvider& InProvider);
    virtual void OnAnalysisBegin(const FOnAnalysisContext& Context) override;
    virtual bool OnEvent(uint16 RouteId, EStyle Style, const FOnEventContext& Context) override;
private:
    TraceServices::IAnalysisSession& Session;
    FMyAnimProvider& Provider;
};

// 创建轨道类，用于在 Rewind Debugger UI 中显示
class FMyAnimTrack : public RewindDebugger::FRewindDebuggerTrack
{
public:
    FMyAnimTrack(uint64 InObjectId);
private:
    virtual bool UpdateInternal() override;
    virtual TSharedPtr<SWidget> GetTimelineViewInternal() override;
    virtual TSharedPtr<SWidget> GetDetailsViewInternal() override;
    // ... 其他重写函数
};

// 创建轨道创建器，用于将轨道与特定对象类型关联
class FMyAnimTrackCreator : public RewindDebugger::IRewindDebuggerTrackCreator
{
private:
    virtual FName GetTargetTypeNameInternal() const; // 返回要调试的对象类型名
    virtual TSharedPtr<RewindDebugger::FRewindDebuggerTrack> CreateTrackInternal(const RewindDebugger::FObjectId& InObjectId) const override;
    virtual bool HasDebugInfoInternal(const RewindDebugger::FObjectId& InObjectId) const override;
};
```
*来源：基于 `Private/RewindDebugger/` 目录下的多个头文件（如 `UAFAnimNodeTrack.h`, `UAFAnimOpTrack.h`）的结构和模式。*

## Demo 示例

以下是一个最小化的示例，展示如何注册一个自定义的动画节点数据工厂。

**MyAnimNodeDataFactory.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "UAFAnimNodeDataFactory.h"

class FMyAnimNodeDataFactory
{
public:
    static void Register();
    static void Unregister();

private:
    static FTopLevelAssetPath RegistrationHandle;
};
```

**MyAnimNodeDataFactory.cpp**
```cpp
#include "MyAnimNodeDataFactory.h"
#include "UAF/AnimNodeCore/UAFAnimNode.h" // 假设的基类头文件

// 定义一个简单的自定义数据结构
USTRUCT()
struct FSimpleAnimData : public FUAFAnimNodeData
{
    GENERATED_BODY()
    UPROPERTY()
    float BlendWeight = 1.0f;
};

// 假设的资产类
UCLASS()
class USimpleAnimAsset : public UObject
{
    GENERATED_BODY()
public:
    UPROPERTY()
    float BaseWeight;
};

FTopLevelAssetPath FMyAnimNodeDataFactory::RegistrationHandle;

void FMyAnimNodeDataFactory::Register()
{
    RegistrationHandle = FUAFAnimNodeDataFactory::RegisterAsset<FSimpleAnimData, USimpleAnimAsset>(
        [](USimpleAnimAsset* Asset) -> FSimpleAnimData
        {
            FSimpleAnimData Data;
            Data.BlendWeight = Asset->BaseWeight;
            return Data;
        }
    );
}

void FMyAnimNodeDataFactory::Unregister()
{
    if (!RegistrationHandle.IsNull())
    {
        FUAFAnimNodeDataFactory::UnregisterAsset(RegistrationHandle);
        RegistrationHandle = FTopLevelAssetPath();
    }
}
```

## 模块依赖

从头文件引用和模块结构推断，使用此插件需要以下非标准依赖：

| 模块 | 用途 |
|---|---|
| `UAF` | 核心动画框架，提供基础动画操作和数据结构（如 `UAFInstancedAnimOpList`）。 |
| `RewindDebugger` | 提供动画录制、回放和可视化调试的框架。 |
| `StructUtils` | 提供 `FInstancedStruct`、`FPropertyBag` 等高级结构工具，用于动态数据管理。 |
| `TraceServices` | 提供 Trace 数据的分析会话、提供者和模块接口，是实现自定义调试分析器的基础。 |

## 维护状态

### 近期更新

- 2026-04-15 `8d8f8b4b` Implement blend overwrite and accumulate AnimOps
- 2026-04-14 `64a20049` Add newly relevant hint to allow nodes to be re-used
- 2026-04-14 `36403a6d` Add accessor to set the play rate
- 2026-04-14 `afb293fa` Add construction variants to AnimOp ArrayView
- 2026-04-14 `d1af965e` Add InputValue anim node/op

### 维护评价

-   **实验性**：插件在 `.uplugin` 中明确标记为 `IsExperimentalVersion: true`，且默认未启用 (`EnabledByDefault: false`)。这表明它仍处于早期开发或测试阶段，API 和功能可能会发生重大变化。
-   **功能完整性**：从代码结构看，该插件已经实现了核心的动画节点数据工厂和完整的 Rewind Debugger 集成，具备了基本的可用性。
-   **风险提示**：作为实验性插件，不建议在需要长期稳定性的生产项目中直接依赖。建议用于原型开发、内部工具或学习研究。
-   **推荐**：如果你正在深度使用 UAF 动画系统并需要强大的调试能力，可以尝试在开发环境中启用此插件。否则，建议等待其正式发布或寻找替代方案。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFAnimNode)
-   官方文档：无
-   测试用例：路径为 `Tests/UAFAnimNodeTests`，但未提供具体文件内容。