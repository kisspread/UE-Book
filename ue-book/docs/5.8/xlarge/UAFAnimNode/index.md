# UAF Anim Node

> Nodes system for UAF.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画蓝图资产、测试资产） |
| 模块 | `UAFAnimNode` (Runtime), `UAFAnimNodeEditor` (Runtime), `UAFAnimNodeUncookedOnly` (Runtime), `UAFAnimNodeTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-14 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFAnimNode) | |

## 用途

UAFAnimNode 是 UAF (Universal Animation Framework) 插件的动画节点扩展。它为动画师和开发者提供了一套可在动画蓝图中使用的自定义动画节点，用于在动画图中集成和驱动 UAF 系统的功能。该插件解决了将 UAF 的高级动画逻辑（如状态机、混合、IK 等）以可视化节点形式暴露给动画蓝图的问题，使得复杂的动画控制流程能够通过蓝图直观地构建和调试。

## 使用场景

- 你需要在动画蓝图中使用 UAF 框架提供的特定动画逻辑或状态控制。
- 你希望将 UAF 系统的复杂动画功能封装成可复用的动画节点，供动画师在编辑器中拖放使用。
- 你正在开发一个基于 UAF 的角色动画系统，并需要自定义动画节点来满足特定项目需求。

## 模块列表与总结

本插件包含以下四个模块，详细 API 请参阅各模块文档：

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| [`UAFAnimNode`](UAFAnimNode.md) | Runtime | 核心运行时模块，定义了所有可在动画蓝图中使用的 UAF 动画节点类及其逻辑。 |
| [`UAFAnimNodeEditor`](UAFAnimNodeEditor.md) | Runtime | 编辑器模块，提供动画节点的自定义外观、引脚配置、上下文菜单等编辑器集成。 |
| [`UAFAnimNodeUncookedOnly`](UAFAnimNodeUncookedOnly.md) | Runtime | 仅未打包模块，包含仅在编辑器或开发环境中使用的工具、验证和资产处理逻辑。 |
| [`UAFAnimNodeTests`](UAFAnimNodeTests.md) | Runtime | 测试模块，包含针对动画节点功能的自动化测试用例。 |

## 蓝图用法

本插件的核心功能是提供动画蓝图节点。在动画蓝图的“动画图”中，你可以通过右键菜单或拖放方式添加由 `UAFAnimNode` 模块提供的自定义节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UAFAnimNode_*` | 一系列以 `UAFAnimNode_` 为前缀的动画节点，具体功能取决于 UAF 系统。例如，可能包含状态驱动节点、混合节点、IK 节点等。 | `UAnimNode_*` (具体类名见模块文档) |

### 使用示例（蓝图描述）

1.  打开一个动画蓝图，进入“动画图”。
2.  在图表空白处右键，搜索 “UAF”。
3.  从搜索结果中选择一个你需要的 UAF 动画节点（例如 `UAFAnimNode_StateMachine`）。
4.  将该节点的输入/输出引脚与其他动画节点（如 `State Machine`、`Blend Poses by bool` 等）连接起来，构建你的动画逻辑。
5.  在节点的细节面板中配置其特有属性。

## C++ 用法

在 C++ 中，你通常不会直接实例化这些动画节点，而是在动画蓝图中使用它们。但如果你需要创建自定义的动画节点并继承 UAF 的功能，可以参考 `UAFAnimNode` 模块中的基类。

### 头文件引入

```cpp
#include "UAFAnimNode.h" // 引入核心动画节点基类
```

### 基本用法

创建一个自定义动画节点，继承自 UAF 提供的基类。
```cpp
// MyCustomUAFNode.h
#pragma once
#include "UAFAnimNode.h"
#include "MyCustomUAFNode.generated.h"

UCLASS()
class UMyCustomUAFNode : public UUAFAnimNode_Base // 假设基类名为 UUAFAnimNode_Base
{
    GENERATED_BODY()

public:
    // 重写动画节点的评估函数
    virtual void Evaluate_AnyThread(FPoseContext& Output) override;
};
```

## 模块依赖

本插件依赖于 **UAF** 插件。你的项目或模块如果需要使用或扩展此插件的功能，需要在 `.Build.cs` 文件中添加对 `UAF` 模块的依赖。

| 模块 | 用途 |
|---|---|
| `UAF` | UAF 核心框架，提供本插件动画节点所依赖的基础动画系统和功能。 |

## 维护状态

### 近期更新

由于创建时间为未来日期（2026-04-14），无法获取有效的 Git 历史记录。此信息可能为测试数据。

### 维护评价

- **实验性插件**：该插件在 `.uplugin` 中明确标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`。这意味着它处于早期开发阶段，API 和功能可能不稳定，不建议在生产项目中直接使用。
- **依赖关系**：作为 UAF 插件的扩展，其维护状态与 UAF 主插件紧密相关。
- **推荐**：仅建议用于学习、研究或对 UAF 框架进行原型开发。在生产环境中使用前，需密切关注 Epic 官方的更新公告和稳定性声明。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFAnimNode)
- [官方文档]() (暂无)