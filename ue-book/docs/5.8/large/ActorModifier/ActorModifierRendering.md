# Actor Modifier

> Actual implementation of modifiers for actors based on ActorModifierCore plugin

| 属性 | 值 |
|---|---|
| 中文名 | Actor 修改器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（修改器蓝图资产） |
| 模块 | `ActorModifier` (Runtime), `ActorModifierEditor` (Runtime), `ActorModifierLayout` (Runtime), `ActorModifierRendering` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ActorModifier) | |

## 用途

ActorModifier 是基于 ActorModifierCore 框架的实际修改器实现集合，专为 Motion Design（运动设计）/ 虚拟制片工作流设计。它提供了一系列可堆叠的 Actor 修改器，能够在运行时动态改变 Actor 的渲染、布局和附加行为，而无需直接修改 Actor 本身。

核心价值在于：将复杂的效果逻辑（如 Holdout 合成、子 Actor 追踪、渲染状态管理）封装为可复用的修改器组件，与 Unreal 的虚拟制片工具链（Motion Design、ClonerEffector 等）深度集成。

## 使用场景

- 你需要在虚拟制片场景中对 Actor 施加非破坏性的修改效果 → 使用 ActorModifier
- 你需要将多个 Actor 渲染为 holdout mask 并在合成通道中回混 → 使用 Holdout Composite Modifier
- 你需要让修改器自动追踪子 Actor 的变化并响应场景树更新 → 使用内置的场景树追踪扩展
- 你正在构建 Motion Design 工作流并需要可配置的 Actor 效果管线 → 使用此插件配合 ActorModifierCore

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetIncludeChildren` | 设置修改器是否应用于子 Actor | `UActorModifierHoldoutCompositeModifier` |
| `GetIncludeChildren` | 获取是否包含子 Actor 的状态 | `UActorModifierHoldoutCompositeModifier` |

所有修改器节点分类在 `Motion Design|Modifiers|Holdout` 蓝图类别下。

### 使用示例（蓝图描述）

1. 在 Actor 上添加 `Holdout Composite Modifier` 组件
2. 在 Details 面板中设置 `bIncludeChildren` 为 `true`，使修改器同时作用于所有子 Actor
3. 修改器会自动注册追踪相关的 `UPrimitiveComponent`，在渲染管线中执行 holdout 合成
4. 当场景树中的子 Actor 发生变化时（添加/移除），修改器会自动响应并重新注册组件

## C++ 用法

### 头文件引入

```cpp
#include "Modifiers/ActorModifierHoldoutCompositeModifier.h"
```

### 基本用法

创建自定义修改器的模式（基于源码中的生命周期方法）：

```cpp
// 自定义修改器需要继承 UActorModifierAttachmentBaseModifier 或 UActorModifierCoreBase
// 以下展示核心生命周期方法的实现模式

// 1. 设置修改器元数据
void UMyCustomModifier::OnModifierCDOSetup(FActorModifierCoreMetadata& InMetadata)
{
    Super::OnModifierCDOSetup(InMetadata);
    // 在此配置修改器的元数据信息
}

// 2. 修改器被添加时的初始化
void UMyCustomModifier::OnModifierAdded(EActorModifierCoreEnableReason InReason)
{
    Super::OnModifierAdded(InReason);
    // 注册组件、建立追踪关系等
}

// 3. 恢复到修改前的状态
void UMyCustomModifier::RestorePreState()
{
    Super::RestorePreState();
    // 清理已注册的组件，恢复原始渲染状态
    UnregisterPrimitiveComponents();
}

// 4. 应用修改
void UMyCustomModifier::Apply()
{
    Super::Apply();
    // 执行实际的修改逻辑
}
```

### 进阶用法

监听场景树变化（基于 `IAvaSceneTreeUpdateModifierExtension` 接口）：

```cpp
// 当追踪的 Actor 子节点发生变化时自动回调
void UMyModifier::OnSceneTreeTrackedActorChildrenChanged(
    int32 InIdx,
    const TSet<TWeakObjectPtr<AActor>>& InPreviousChildrenActors,
    const TSet<TWeakObjectPtr<AActor>>& InNewChildrenActors)
{
    // 计算新增和移除的 Actor
    // 更新内部追踪的组件集合
    // 触发重新 Apply
}
```

响应属性编辑变化（编辑器内）：

```cpp
#if WITH_EDITOR
void UMyModifier::PostEditChangeProperty(FPropertyChangedEvent& InPropertyChangedEvent)
{
    Super::PostEditChangeProperty(InPropertyChangedEvent);
    
    if (InPropertyChangedEvent.GetPropertyName() == GET_MEMBER_NAME_CHECKED(UMyModifier, bIncludeChildren))
    {
        OnIncludeChildrenChanged(); // 重新注册/注销子 Actor 的组件
    }
}
#endif
```

## Demo 示例

```cpp
// MyHoldoutModifier.h
#pragma once

#include "Modifiers/ActorModifierHoldoutCompositeModifier.h"
#include "MyHoldoutModifier.generated.h"

UCLASS(BlueprintType, MinimalAPI)
class UMyHoldoutModifier : public UActorModifierHoldoutCompositeModifier
{
    GENERATED_BODY()

public:
    UMyHoldoutModifier();

protected:
    virtual void OnModifierCDOSetup(FActorModifierCoreMetadata& InMetadata) override;
    virtual void Apply() override;
};
```

```cpp
// MyHoldoutModifier.cpp
#include "MyHoldoutModifier.h"

UMyHoldoutModifier::UMyHoldoutModifier()
{
    bIncludeChildren = true;
}

void UMyHoldoutModifier::OnModifierCDOSetup(FActorModifierCoreMetadata& InMetadata)
{
    Super::OnModifierCDOSetup(InMetadata);
    // 配置自定义元数据
    InMetadata.SetName(TEXT("MyHoldoutModifier"));
}

void UMyHoldoutModifier::Apply()
{
    // 先执行基类的 holdout 合成逻辑
    Super::Apply();
    
    // 追加自定义渲染逻辑
    for (const TWeakObjectPtr<UPrimitiveComponent>& CompWeak : PrimitiveComponentsWeak)
    {
        if (UPrimitiveComponent* Comp = CompWeak.Get())
        {
            // 对每个追踪的组件施加额外效果
        }
    }
}
```

## 模块依赖

由于此插件是 ActorModifierCore 的实现层，核心依赖如下：

| 模块 | 用途 |
|---|---|
| `ActorModifierCore` | 修改器核心框架（基类、元数据系统） |
| `ActorModifierAttachment` | 附件修改器基类（HoldoutComposite 继承自它） |
| `MotionDesignCommon` / 相关 Motion Design 模块 | 场景树更新接口（IAvaSceneTreeUpdateModifierExtension） |

无特殊依赖（仅标准 Core/Engine/Slate 等）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-09 | `bdd66985` | Motion Design: made render state dirty reason optional + added some fixes to the text3d update causi | 渲染状态脏标记原因改为可选，修复 Text3D 更新相关问题 |
| 2026-04-08 | `5c28c1d0` | Motion Design: added render state dirty reason scope for the modifier system to have a better idea o | 为修改器系统添加渲染状态脏标记作用域，改善状态追踪 |
| 2026-03-13 | `ab2df2c3` | Motion Design: moved usage of core ticker to custom ts ticker instance to better control timing. | 将核心 ticker 迁移为自定义实例以精确控制时序 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 配置文件命名规范化（Base → Default） |
| 2025-09-23 | `cabb6e4f` | MotionDesign : ActorModifier | ActorModifier 初始化提交 |

### 维护评价

- **状态**：活跃维护中
- **年龄**：约 1 年，属于较新插件
- **更新频率**：近 2 个月内有持续的功能性更新（渲染状态管理、时序控制优化）
- **背景**：从 Experimental 迁移到 VirtualProduction，表明已通过内部评估达到生产可用标准
- **注意事项**：`Installed: false`，需手动在插件管理器中启用；作为 Motion Design 工作流的一部分，需配合 ActorModifierCore 使用
- **推荐程度**：✅ 推荐用于 Motion Design / 虚拟制片工作流。活跃维护，Epic 官方维护，适合生产使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ActorModifier)
- [官方文档]()（暂无）
- [测试用例]()（暂未发现独立测试文件）