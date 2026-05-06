# UAF State Tree

> StateTree integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF 状态树集成 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFStateTree` (Runtime), `UAFStateTreeEditor` (Runtime), `UAFStateTreeUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-07-30 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFStateTree) | |

## 用途

`UAFStateTree` 插件将 **StateTree**（状态树）系统集成到 **UAF**（Unreal Animation Framework）中。  
UAF 使用 `RigVM` 与 `AnimNext` 构建动画逻辑，而 StateTree 提供灵活的决策树与状态管理。  
该插件的作用是让开发者能够在 UAF 动画图中直接使用 StateTree 驱动动画状态切换、条件判断和行为选择，  
从而替代手写的动画蓝图逻辑或复杂的脚本，实现更模块化、可维护的动画控制。

## 使用场景

- 制作一个具有多段连击、闪避、受击等复杂状态的近战战斗动画系统 → 利用 StateTree 状态机组织状态切换逻辑，通过 UAF 输出动画参数
- 需要根据玩家输入、环境感知（如距离、朝向）动态选择攻击或移动动画 → 将决策逻辑放在 StateTree 中，动画混合交给 UAF
- 希望将动画状态逻辑与角色蓝图解耦，便于美术/策划调整 → StateTree 资产可被非程序员编辑

## 总体规划

插件包含三个模块：
- **UAFStateTree**：运行时核心模块，可能包含资产类型、运行时上下文等（头文件未提供）
- **UAFStateTreeEditor**：编辑器模块，提供自定义编辑器和细节面板（头文件未提供）
- **UAFStateTreeUncookedOnly**（本文档重点）：负责编辑器数据、编译管线、工作区导出等“未烘焙”（Uncooked）阶段的逻辑

## 蓝图用法

此模块主要提供编辑器工具与内部数据结构，**没有公开的蓝图可调用节点**。  
蓝图开发者应使用父级 StateTree 和 UAF 的常规节点，无需直接调用本模块的类。

## C++ 用法

### 头文件引入

```cpp
#include "AnimNextStateTreeEditorData.h"          // 编辑器数据类
#include "AnimNextStateTreeFunctionLibraryHelper.h" // 函数库辅助
#include "AnimNextStateTreeWorkspaceAssetUserData.h" // 工作区资产数据
#include "AnimNextStateTreeWorkspaceExports.h"    // 导出数据结构
```

### 基本用法

**1. 编辑器数据注册（通过 UAnimNextStateTree_EditorData）**  
该类是 UAF 动画图数据的子类，处理 StateTree 所需的特定编译和变量构建。  
通常由工厂类自动创建，但开发者可以继承它自定义编译行为。

```cpp
// 来自 Engine/Plugins/Experimental/UAF/UAFStateTree/Source/UAFStateTreeUncookedOnly/Internal/AnimNextStateTree_EditorData.h
// 在工厂中创建新的 StateTree 编辑器数据：
UAnimNextStateTree_EditorData* EditorData = NewObject<UAnimNextStateTree_EditorData>(Outer);
// 之后可以通过 EditorData 设置变量、触发编译等
```

**2. 使用工作区导出数据**  
当需要在内容浏览器大纲视图中显示 StateTree 结构时，可以填充 `FAnimNextStateTreeStateOutlinerData` 结构。

```cpp
// 来自 Engine/Plugins/Experimental/UAF/UAFStateTree/Source/UAFStateTreeUncookedOnly/Public/AnimNextStateTreeWorkspaceExports.h
FAnimNextStateTreeStateOutlinerData StateData;
StateData.StateName = TEXT("Idle");
StateData.bIsLeafState = false;
StateData.SelectionBehavior = EStateTreeStateSelectionBehavior::TrySelect;
// 然后将 StateData 添加到 FAnimNextStateTreeOutlinerData 的列表中
```

**3. 获取所有暴露的 AnimNext 函数名（编译时辅助）**

```cpp
// 来自 Engine/Plugins/Experimental/UAF/UAFStateTree/Source/UAFStateTreeUncookedOnly/Public/AnimNextStateTreeFunctionLibraryHelper.h
const TArray<FName>& FunctionNames = UAnimNextStateTreeFunctionLibraryHelper::GetExposedAnimNextFunctionNames();
// 可以用于动态填充下拉列表或自动补全
```

### 进阶用法

**自定义编译管线**：  
通过重写 `UAnimNextStateTree_EditorData` 中的 `RecompileVM`、`BuildFunctionHeadersContext`、`OnPreCompileGetProgrammaticGraphs` 等方法，可以注入自定义的 RigVM 字节码或变量。

```cpp
// 继承 UAnimNextStateTree_EditorData
UCLASS()
class MYCUSTOMEDITOR_API UMyStateTreeEditorData : public UAnimNextStateTree_EditorData
{
    GENERATED_BODY()
protected:
    virtual void RecompileVM() override
    {
        // 自定义编译前处理
        // 调用基类
        Super::RecompileVM();
        // 后续处理
    }
};
```

## Demo 示例

以下示例创建一个简单的 StateTree 资产关联的数据类，用于编辑器扩展（概念性代码，不可直接编译）。

```cpp
// MyStateTreeEditorData.h
#pragma once
#include "AnimNextStateTree_EditorData.h"
#include "MyStateTreeEditorData.generated.h"

UCLASS()
class UMyStateTreeEditorData : public UAnimNextStateTree_EditorData
{
    GENERATED_BODY()
public:
    // 额外编辑器变量（例如自定义参数）
    UPROPERTY(EditAnywhere, Category = "My StateTree")
    float MyCustomParameter = 0.0f;
};
```

```cpp
// MyStateTreeEditorData.cpp
#include "MyStateTreeEditorData.h"
// 无需额外逻辑，继承已提供默认实现
```

该数据类可以在 UAF 资产编辑器中被识别，并且其 `MyCustomParameter` 会显示在细节面板中。

## 模块依赖

以下模块是本模块所依赖的独特模块（不包含 Core/Engine/Slate 等常见项）。

| 模块 | 用途 |
|---|---|
| `StateTree` | 核心 StateTree 运行时与编辑器数据 |
| `AnimNext` | UAF 动画框架运行时 |
| `AnimNextAnimGraph` | 动画图编辑器数据基类 (`UAnimNextAnimationGraph_EditorData`) |
| `AnimNextRigVM` | RigVM 编译与变量管理 |
| `RigVM` | RigVM 通用支持 |

**注意**：实际使用本模块时，还需要依赖 `AnimNext` 和 `StateTree` 原生插件。

## 维护状态

插件创建于 2025 年 7 月，尚处于实验阶段，但开发活跃。

### 近期更新

- 2025-09-23 `9a934fb4` — Fix UAF leaking callbacks causing UAF state tree selction to be cleared.
- 2025-08-28 `9273c535` — Add missing IUpdate propagation to StateTree
- 2025-08-15 `031b08ff` — UAF StateTree autocomplete on graph timeline complete
- 2025-08-01 `7aace74a` — Downgrade check to ensure on statetree failure
- 2025-07-30 `3ac8187c` — UAF Read / Write Variable in Function Fixes

### 维护评价

- **创建时间**：2025-07-30，极新插件。
- **近期更新频率**：每月均有提交，截止 2025-09-23 仍活跃。
- **维护状态**：**活跃维护**。修复和功能更新持续进行。
- **已知问题**：存在 UAF 回调泄漏相关 bug（已于最新 commit 修复），可能还有边缘情况。
- **实验性**：该插件标记为实验性，API 可能变化，不建议用于正式产品。

综合评价：作为实验性插件，维护积极，可用于原型或学习研究，但生产环境需谨慎。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFStateTree)
- [官方文档](https://dev.epicgames.com/documentation/)（暂无专用文档）