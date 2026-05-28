# Remote Control Actor Modifier Bridge

> Interface between the Remote Control, Actor Modifier and Property Animator plugins.

| 属性 | 值 |
|---|---|
| 中文名 | 远程控制与修改器桥接 |
| 分类 | Messaging |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `RemoteControlActorModifierBridge` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2025-07-28 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RemoteControlActorModifierBridge) | |

## 用途

此插件作为 `RemoteControl`、`ActorModifierCore` 和 `PropertyAnimatorCore` 插件之间的桥接器。它的核心目的是确保当通过远程控制面板（Remote Control Panel）选择属性的“源（Source）”时，与 `ActorModifier` 或 `PropertyAnimator` 关联的 Actor 也能被正确地同步选中。简单来说，它解决了在远程控制中操作被修改器或动画器影响的 Actor 属性时，源对象识别不一致的问题。

## 使用场景

- 当你在使用 `Remote Control` 面板远程修改一个 Actor 的属性，同时这个 Actor 正被 `Actor Modifier` 或 `Property Animator` 动态修改时，使用此插件可以确保两者的行为和选择状态保持一致。

## 蓝图用法

此插件主要通过模块启动时的内部注册实现其功能，没有暴露公开的蓝图节点。用户无需直接操作蓝图，其作用在启用插件后对其他插件的交互自动生效。

## C++ 用法

此插件不提供公开的 C++ API，其功能通过模块启动时向 `RemoteControl` 的属性解析系统注册自定义解析器来实现。开发者通常无需直接调用其代码。

### 核心实现逻辑

该插件的核心是向 `RemoteControl` 注册一个属性解析委托，用于在解析 `ActorModifier` 或 `PropertyAnimator` 相关属性时，将最终目标对象（`BoundObjects`）正确地设置为关联的 Actor。

**来源**: `Engine/Plugins/Experimental/RemoteControlActorModifierBridge/Source/Private/RemoteControlActorModifierBridgeModule.h`

```cpp
// 在模块启动时注册解析器
void FRemoteControlActorModifierBridgeModule::StartupModule()
{
    // 假设这里注册了 ResolverActorModifierProperty 到 RemoteControl 的解析流程
    // ...
}

// 解析函数示例（概念）
bool FRemoteControlActorModifierBridgeModule::ResolverActorModifierProperty(
    const TSharedRef<FRemoteControlProperty>& InProperty,
    TArray<UObject*>& InOutBoundObjects,
    TSharedPtr<FPropertyPath>& OutPropertyPath)
{
    // 核心逻辑：检查属性路径是否指向 ActorModifier 或 PropertyAnimator
    // 如果是，则从这些组件向上查找到其所属的 Actor，并将 Actor 添加到 InOutBoundObjects
    // 这样远程控制最终会作用到正确的 Actor 上。
    // ...
    return true; // 表示成功处理
}
```

## Demo 示例

此插件为内部桥接，没有独立的运行时功能示例。其效果体现在 `RemoteControl` 与 `ActorModifier`/`PropertyAnimator` 插件的协同工作中。

## 模块依赖

从 `Build.cs` 及插件依赖分析得出，要使用此插件，你的模块（如果直接依赖）或至少以下插件需要启用：

| 模块 | 用途 |
|---|---|
| `ActorModifierCore` | 提供 Actor 修改器核心功能 |
| `OperatorStack` | （根据插件依赖推测）可能用于处理算子栈 |
| `RemoteControl` | 提供远程控制核心功能 |
| `PropertyAnimatorCore` | 提供属性动画器核心功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-07-28 | `558e1e82` | Remote Control / Actor Modifier / Property Animator: Bridge plugin | 插件首次创建，建立三个插件间的桥接，实现在远程控制中选择源时同步选中关联 Actor。 |

### 维护评价

该插件非常新（创建于 2025 年 7 月），且处于实验性阶段（`IsBetaVersion=true`）。目前仅有一次初始提交，内容稳定，但尚无后续的功能迭代或错误修复记录。作为一个功能性的桥接插件，其存在解决了特定插件间的交互问题。由于其依赖的插件（如 `RemoteControl`、`ActorModifierCore`）仍在活跃维护中，该桥接插件可能会随着这些插件的更新而进行必要的适配。

**建议**：可以谨慎使用，但需注意其“实验性”状态。在依赖此插件构建核心功能时，应考虑其未来可能发生的 API 变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RemoteControlActorModifierBridge)