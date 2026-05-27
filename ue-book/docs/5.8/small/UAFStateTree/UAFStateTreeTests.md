# UAF State Tree

> StateTree integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF 状态树 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画资产、状态树配置） |
| 模块 | `UAFStateTree` (Runtime), `UAFStateTreeEditor` (Runtime), `UAFStateTreeUncookedOnly` (Runtime), `UAFStateTreeTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFStateTree) | |

## 用途

UAFStateTree 是 Unreal Animation Framework（UAF）与 StateTree 状态树系统之间的集成插件。UAF 是 UE5 新一代的动画框架，而 StateTree 是一种可视化的层级状态机系统。

**这个插件解决的核心问题**：让动画师和开发者能够使用 StateTree 来管理和驱动 UAF 动画系统的状态转换、混合和决策逻辑。

**实际价值**：
- 通过 StateTree 可视化界面配置复杂的动画状态机，降低动画逻辑的编程门槛
- 利用 StateTree 的层级结构和数据绑定能力，管理 UAF 动画实例的生命周期
- 与 UE5 的动画蓝图工作流无缝集成，提供比传统状态机更灵活的动画控制方案

## 使用场景

- 你正在使用 UE5 新版动画框架 UAF（Unreal Animation Framework）→ 用 UAFStateTree 通过 StateTree 管理动画状态
- 你需要为角色创建复杂的动画状态机，包含条件分支、并行状态和数据驱动逻辑 → 用 StateTree 集成 UAF 动画系统
- 你希望以可视化方式配置动画状态转换，而不是编写大量蓝图逻辑 → 用 UAFStateTree 的编辑器工具
- 你的项目需要将 AI 行为树与动画系统深度整合 → StateTree 同时支持行为和动画驱动

## 蓝图用法

> ⚠️ **注意**：当前文档基于测试模块 `UAFStateTreeTests` 的分析，核心运行时 API 的完整蓝图节点列表需要查阅 `UAFStateTree` 和 `UAFStateTreeEditor` 模块。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| GetOrAddComponent | 获取或添加 UAF 状态树组件 | `UAFStateTreeComponent` |

### 使用示例（蓝图描述）

典型的 UAFStateTree 使用流程：

1. **创建 StateTree Schema**：在动画蓝图中创建一个使用 UAF StateTree Schema 的状态树实例
2. **定义状态节点**：在 StateTree 编辑器中添加动画相关的状态节点（如播放动画片段、混合动画层）
3. **配置转换条件**：设置状态之间的转换条件，可以绑定到 UAF 动画实例的属性
4. **运行时驱动**：通过组件接口驱动状态树的执行，管理动画状态的生命周期

## C++ 用法

> ⚠️ **注意**：由于当前分析的是测试模块，以下信息可能不完整。建议结合 `UAFStateTree` 运行时模块源码使用。

### 头文件引入

```cpp
#include "UAFStateTree/UAFStateTreeModule.h"
```

### 基本用法

从测试用例的组件交互模式推断的典型用法：

```cpp
// 获取或添加 UAF 状态树组件
UAFStateTreeComponent* StateTreeComp = Actor->GetOrAddComponent<UAFStateTreeComponent>();
if (StateTreeComp)
{
    // 组件已就绪，可以通过 StateTree 驱动动画逻辑
    // 具体的状态树实例配置在编辑器中完成
}
```

### 进阶用法

UAFStateTree 通常与 UE5 的 StateTree 系统配合使用，涉及：
- StateTree Schema 自定义（UAFStateTreeEditor 模块提供）
- 动画实例与状态树数据绑定
- 状态树运行时求值和事件触发

## Demo 示例

> ⚠️ 由于 UAFStateTree 是实验性插件，且当前分析基于测试模块，建议参考 Epic Games 官方示例项目了解完整用法。

一个最小化的组件集成示例：

```cpp
// MyAnimCharacter.h
#pragma once
#include "GameFramework/Character.h"
#include "MyAnimCharacter.generated.h"

class UAFStateTreeComponent;

UCLASS()
class AMyAnimCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyAnimCharacter();
    
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    UAFStateTreeComponent* StateTreeComponent;
};

// MyAnimCharacter.cpp
#include "MyAnimCharacter.h"
#include "UAFStateTree/Components/UAFStateTreeComponent.h"

AMyAnimCharacter::AMyAnimCharacter()
{
    // 在构造函数中创建组件
    StateTreeComponent = CreateDefaultSubobject<UAFStateTreeComponent>(TEXT("UAFStateTree"));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `StateTree` | UE5 核心状态树模块，提供状态机运行时和编辑器框架 |
| `UAF` | Unreal Animation Framework 核心模块，提供新动画系统基础设施 |
| `GameplayTags` | 用于状态树中的标签系统和条件匹配 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志系统到新的 UE_LOGF 宏格式 |
| 2026-04-13 | `6f1ea925` | State Tree: Updated state tree reference struct details to show the display name of the struct rathe | 更新状态树引用结构详情显示，展示结构体的显示名称 |
| 2026-04-13 | `5078d880` | Add UAFSharedAssets plugin for content we want to provide that references UAF assets defined in sepa | 新增 UAFSharedAssets 插件，用于提供跨插件共享的 UAF 资产 |
| 2026-04-10 | `797a6da6` | Rename GetComponent to GetOrAddComponent to match functionality | 将 GetComponent 重命名为 GetOrAddComponent 以匹配实际功能 |
| 2026-03-31 | `4e41a45f` | Fix crash attempting to manually create UAF ST by hiding UAF ST Schema | 修复手动创建 UAF 状态树时的崩溃问题，通过隐藏 UAF ST Schema |

### 维护评价

**状态**：🟢 活跃维护

- **创建时间**：2025-06-27，插件年龄约 1 年，是 UE5 新功能的一部分
- **更新频率**：最近 2 周内有 5 次提交，更新非常频繁
- **更新内容**：涵盖 API 优化、bug 修复、依赖插件整合等实质性改进
- **实验性标记**：`IsExperimentalVersion = true`，API 可能发生变化
- **默认启用**：`EnabledByDefault = false`，需要手动启用

**推荐**：如果你的项目需要使用 UAF 动画框架并通过 StateTree 管理动画状态，可以尝试使用。但需注意：
1. 这是实验性功能，API 可能在后续版本中变化
2. 建议关注 Epic Games 的官方文档和示例项目
3. 生产环境使用前需要充分测试

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFStateTree)
- [UAF 核心插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF)（父级 UAF 框架）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFStateTree/Tests)（UAFStateTreeTests 模块）