# ControlRigPhysics

> Support for physics simulation in control rig

| 属性 | 值 |
|---|---|
| 中文名 | ControlRig 物理模拟 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、调试工具） |
| 模块 | `ControlRigPhysics` (Runtime), `ControlRigPhysicsEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-20 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ControlRigPhysics) | |

## 用途

该插件将物理模拟能力集成到 ControlRig 框架中。它允许动画师和开发者在 ControlRig 蓝图内直接设置和控制物理模拟，例如刚体动力学、碰撞检测等，从而将程序化动画与基于物理的交互无缝结合。该插件从 PhysicsControl 插件中独立出来，专注于为 ControlRig 提供物理模拟支持。

## 使用场景

- **角色物理动画**：在角色动画蓝图中，使用 ControlRig 节点驱动带有物理模拟的部件（如头发、飘带、饰品），实现动画与物理的混合。
- **布娃娃与主动布娃娃**：在角色动画图中集成物理模拟，实现从动画到布娃娃的平滑过渡，或创建受动画驱动的主动布娃娃系统。
- **可破坏环境**：在场景动画序列中，使用 ControlRig 控制物体的物理属性和约束，实现结构倒塌、链条反应等效果。
- **复杂的机械装置**：在 ControlRig 中模拟齿轮、连杆、弹簧等机械结构的物理运动。

## 蓝图用法

本插件的核心蓝图功能（物理节点）位于 `ControlRigPhysics` 运行时模块中。从其 `ControlRigPhysicsEditor` 模块的调试工具中，可以推断出一些可配置的物理模拟参数。

### 核心节点（基于 Editor 模块调试参数推断）

| 节点 | 说明 | 所在类 |
|---|---|---|
| 启用/禁用步进求解器 | 控制物理模拟的求解器是否启用 | `ControlRig` |
| 设置固定时间步长 | 覆盖物理模拟的固定时间步长 | `ControlRig` |
| 设置最大子步数 | 覆盖物理模拟每帧的最大子步数 | `ControlRig` |
| 设置最大增量时间 | 覆盖每帧物理模拟允许的最大增量时间 | `ControlRig` |
| 启用/禁用可视化 | 控制是否在视口中显示物理模拟的调试可视化（如刚体、关节、碰撞体） | `ControlRig` |

**注意**：具体的蓝图节点名称和用法需要查阅 `ControlRigPhysics` 运行时模块的头文件。上表是基于其编辑器调试工具暴露的 CVar 参数推断的常见功能方向。

## C++ 用法

本插件的 C++ API 主要面向需要扩展 ControlRig 物理功能的开发者。

### 头文件引入

由于缺少运行时模块的详细头文件，无法提供具体的引入示例。通常，要使用 ControlRig 的物理功能，需要引入 `ControlRigPhysics` 模块的头文件。

### 基本用法

以下是一个基于插件结构推断的伪代码示例，展示了如何在代码中集成物理模拟：

```cpp
// 假设在你的自定义 ControlRig 节点或动画蓝图逻辑中
#include "ControlRigPhysics.h" // 需要实际验证的头文件

void UMyControlRigNode::Execute(const FControlRigExecuteContext& Context)
{
    // 在 ControlRig 执行上下文中，可能通过特定接口访问或启用物理模拟
    // 具体 API 需要查看 ControlRigPhysics 模块的公开接口
    // 例如，可能有一个 FControlRigPhysicsContext 或类似的结构
}
```

### 进阶用法

编辑器模块 (`ControlRigPhysicsEditor`) 提供了强大的调试工具。如果需要在编辑器中扩展或自定义物理模拟的调试界面，可以参考其代码结构。

**调试小部件 (`SControlRigPhysicsDebugWidget`)**：
该类通过一系列 `Binding` 对象（如 `FCVarOverrideNumericBinding`）将控制台变量 (`CVar`) 与 Slate UI 控件绑定，实现实时调整物理模拟参数。这是扩展编辑器调试功能的典型模式。

```cpp
// 伪代码：展示如何绑定一个自定义的 CVar 到调试 UI
class SMyPhysicsDebugWidget : public SCompoundWidget
{
    // ... Slate 宏定义 ...

    void Construct(const FArguments& InArgs)
    {
        // 创建一个数值型覆盖绑定，用于控制“刚体阻尼”参数
        DampingBinding = MakeShared<ControlRigPhysicsEditor::FCVarOverrideNumericBinding<float>>(
            TEXT("ControlRig.Physics.RigidBodyDamping"),
            FText::FromString("覆盖刚体线性阻尼系数"),
            0.1f, // 默认值
            0.0f  // 最小允许值
        );

        // 在 ChildSlot 中使用这个绑定来创建UI
        ChildSlot
        [
            SNew(SHorizontalBox)
            + SHorizontalBox::Slot()
            [
                DampingBinding->BuildOverrideCell() // 启用/禁用覆盖的复选框
            ]
            + SHorizontalBox::Slot()
            [
                DampingBinding->BuildValueCell() // 数值输入框
            ]
        ];
    }

    // ... 其他成员 ...
};
```

## Demo 示例

以下是一个最小化示例，展示如何在代码中注册一个简单的 ControlRig 物理调试选项（基于编辑器模块的模式）。

### MyPhysicsDebugMenu.h
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyPhysicsDebugMenuModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void RegisterPhysicsDebugMenu();
    void UnregisterPhysicsDebugMenu();
    void ToggleMyDebugOption();
    bool IsMyDebugOptionEnabled() const;

    FDelegateHandle OnDebugMenuExtensionHandle;
    static const FName DebugMenuName;
};
```

### MyPhysicsDebugMenu.cpp
```cpp
#include "MyPhysicsDebugMenu.h"

#include "ToolMenus.h"
#include "ControlRigPhysicsCVars.h" // 假设存在一个定义 CVar 的头文件

const FName FMyPhysicsDebugMenuModule::DebugMenuName = TEXT("ControlRig.Physics.Debug");

void FMyPhysicsDebugMenuModule::StartupModule()
{
    // 延迟注册，确保 ToolMenus 已初始化
    UToolMenus::RegisterStartupCallback(FSimpleMulticastDelegate::FDelegate::CreateRaw(
        this, &FMyPhysicsDebugMenuModule::RegisterPhysicsDebugMenu));
}

void FMyPhysicsDebugMenuModule::ShutdownModule()
{
    UToolMenus::UnRegisterStartupCallback(this);
    UToolMenus::UnregisterOwner(this);
}

void FMyPhysicsDebugMenuModule::RegisterPhysicsDebugMenu()
{
    UToolMenu* Menu = UToolMenus::Get()->ExtendMenu(
        TEXT("LevelEditor.MainMenu.Tools")); // 菜单路径需根据实际情况调整
    if (Menu)
    {
        FToolMenuSection& Section = Menu->FindOrAddSection(TEXT("PhysicsDebug"));
        Section.AddMenuEntry(
            TEXT("ToggleMyOption"),
            FText::FromString(TEXT("切换自定义物理调试选项")),
            FText::FromString(TEXT("启用/禁用一个自定义的物理模拟调试可视化")),
            FSlateIcon(),
            FUIAction(
                FExecuteAction::CreateRaw(this, &FMyPhysicsDebugMenuModule::ToggleMyDebugOption),
                FCanExecuteAction(),
                FIsActionChecked::CreateRaw(this, &FMyPhysicsDebugMenuModule::IsMyDebugOptionEnabled)
            ),
            EUserInterfaceActionType::Check
        );
    }
}

void FMyPhysicsDebugMenuModule::UnregisterPhysicsDebugMenu()
{
    UToolMenus::UnregisterOwner(this);
}

void FMyPhysicsDebugMenuModule::ToggleMyDebugOption()
{
    // 切换相关的 CVar
    IConsoleVariable* CVar = IConsoleManager::Get().FindConsoleVariable(TEXT("ControlRig.Physics.ShowCustomDebug"));
    if (CVar)
    {
        CVar->Set(CVar->GetInt() == 0 ? TEXT("1") : TEXT("0"), ECVF_SetByConsole);
    }
}

bool FMyPhysicsDebugMenuModule::IsMyDebugOptionEnabled() const
{
    const IConsoleVariable* CVar = IConsoleManager::Get().FindConsoleVariable(TEXT("ControlRig.Physics.ShowCustomDebug"));
    return CVar ? CVar->GetInt() != 0 : false;
}

IMPLEMENT_MODULE(FMyPhysicsDebugMenuModule, MyPhysicsDebugMenu)
```

## 模块依赖

从插件的依赖关系（`ControlRig`, `PhysicsControl`）和模块性质推断，你的项目模块需要依赖以下独特模块：

| 模块 | 用途 |
|---|---|
| `ControlRigPhysics` | 核心运行时模块，提供 ControlRig 中的物理模拟功能和节点。 |
| `ControlRigPhysicsEditor` | 编辑器模块，提供物理模拟的调试工具和UI（如调试面板）。 |

**注意**：使用本插件还需要确保 `ControlRig` 和 `PhysicsControl` 插件已启用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `0fc3e074` | Anim In Engine: Run CR physics collisions on game thread, if we are currently on the game thread. Th | 优化碰撞检测，使其在游戏线程上运行，可能提升特定场景下的性能或稳定性。 |
| 2026-05-26 | `81eec0eb` | Fix for missing control rig physics version - fixes assert on loading older control rigs that don't  | 修复加载旧版控制 rig 时因缺少物理版本信息导致的断言错误，增强了向后兼容性。 |
| 2026-05-14 | `c6a1ed72` | Control rig physics - Remove SolverSettings.WorldCollisionExpiryFrames as a value of 1 is the only  | 移除了 `WorldCollisionExpiryFrames` 设置，因为始终为1是唯一有效值，简化了设置。 |
| 2026-05-14 | `15fdc3a0` | Control rig physics - more uses of the cached components | 增加了缓存组件的使用，旨在减少重复查找，提升运行时性能。 |
| 2026-05-14 | `c48042d4` | Control rig physics - use caching. Very simple change mirroring what we do in Control Rig Dynamics,  | 引入缓存机制以优化性能，此改动借鉴了 ControlRig Dynamics 模块的现有做法。 |

### 维护评价

该插件是一个相对较新的实验性功能（创建于2025年6月）。从近期的提交历史（截至2026年5月）来看，它正处在**活跃的开发与维护阶段**。更新内容包括性能优化（缓存、线程模型调整）、Bug修复（向后兼容性）和设置简化，表明其功能正在快速迭代和稳定化。

**主要优势**：
- 开发活跃，Epic 工程师正在积极改进。
- 专注于 ControlRig 生态，与现有动画工具链集成紧密。

**注意事项**：
- **实验性/Beta状态**：功能、API 和行为在未来版本中可能发生重大变更。
- 由于处于早期阶段，社区文档和资源可能有限。

**推荐**：如果你正在使用 ControlRig 并且需要集成物理模拟，该插件是官方提供的方案，值得在**非生产项目或原型开发中**尝试和评估。不建议在需要长期稳定性的正式项目中依赖其当前状态。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ControlRigPhysics)