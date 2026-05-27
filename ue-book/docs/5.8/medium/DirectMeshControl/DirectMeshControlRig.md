# Direct Mesh Control

> Animate using click & drag and surface selection.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `DirectMeshControl` (Runtime), `DirectMeshControlRig` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-14 |
| 年龄标签 | 🆕（约 -1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/DirectMeshControl) | |

## 用途

Direct Mesh Control 插件提供了一套在骨骼网格体（Skeletal Mesh）表面进行交互式选择和操作的底层工具。其核心思想是将网格体表面划分为逻辑区域（通过“多边形组” Polygroup），并允许用户通过点击、拖拽这些表面区域来直接驱动动画或控制 Rig 元素。它解决了传统动画制作流程中需要预先设置大量控制点（Control Points）或骨骼（Bones）才能进行精细表面操作的问题，为动画师提供了一种更直观、基于表面的交互方式。

## 使用场景

-   **角色动画调整**：动画师希望直接拖拽角色模型的肩膀、肘部或面部特定区域来快速调整姿势，而不是通过操作抽象的控制器。
-   **交互式动画原型**：在游戏开发早期，需要快速创建基于玩家输入（如鼠标点击拖拽）的角色表面变形或动画效果。
-   **自定义控制 Rig**：为 Control Rig 系统创建基于网格体表面多边形组的自定义形状库（Shape Library），用于更精确的动画控制。

## 蓝图用法

该插件主要通过 Control Rig 单元（Rig Unit）暴露功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Shape Library from Layer` | 从骨骼网格体的指定多边形组层（Polygroup Layer）读取数据，为每个多边形组生成子网格体，并注册为一个 `UControlRigShapeLibrary`。 | `FRigUnit_SetupShapeLibraryFromLayer` |

### 使用示例（蓝图描述）

1.  在 Control Rig 蓝图中，添加一个 `Set Shape Library from Layer` 节点。
2.  将 `LayerName` 输入引脚连接到一个包含多边形组信息的层名称（例如默认的 `"dmc-polygroup"`）。
3.  该节点执行后，会输出一个 `GroupNames` 数组，包含所有提取出的多边形组名称。
4.  生成的形状库可以被 Control Rig 的其他节点（如 `Set Shape`）使用，从而将控制柄（Handle）与网格体表面的特定区域关联起来。

## C++ 用法

### 头文件引入

```cpp
#include "Units/RigUnit_DirectMeshControl.h"
```

### 基本用法

该插件的核心是定义了一个自定义的 Control Rig 单元。以下是如何在 C++ 中引用和使用该单元的示例。

```cpp
// 假设你正在编写一个自定义的 RigUnit
#include "Units/RigUnit_DirectMeshControl.h"

// 在你的 RigUnit 执行函数中，可以创建并使用 FRigUnit_SetupShapeLibraryFromLayer
// 注意：通常 RigUnit 是通过蓝图或 Control Rig 图表实例化的，直接 C++ 调用较少见。
// 以下为概念性示例。
void FMyCustomRigUnit::Execute()
{
    // ... 其他逻辑
    FRigUnit_SetupShapeLibraryFromLayer SetupUnit;
    SetupUnit.LayerName = FName("my-custom-layer");
    SetupUnit.Execute(); // 执行单元逻辑
    TArray<FName> ExtractedGroups = SetupUnit.GroupNames;
    // ... 使用提取的组名
}
```

### 进阶用法

结合 `DirectMeshControl` 模块提供的其他功能（如表面选择代理），可以实现更复杂的交互。例如，监听用户在网格体表面的点击事件，获取点击位置所在的多边形组，然后通过上述 RigUnit 动态更新控制柄。

## Demo 示例

以下是一个最小化的自定义 RigUnit 示例，它继承自 `FRigUnit_SetupShapeLibraryFromLayer` 并添加了额外的输出。

```cpp
// MyCustomSetupUnit.h
#pragma once
#include "Units/RigUnit_DirectMeshControl.h"
#include "MyCustomSetupUnit.generated.h"

USTRUCT(meta=(DisplayName="My Custom Setup", Keywords="Custom, Direct Mesh"))
struct FMyCustomSetupUnit : public FRigUnit_SetupShapeLibraryFromLayer
{
    GENERATED_BODY()

    // 额外输出：第一个组的名称
    UPROPERTY(meta = (Output))
    FName FirstGroupName;

    RIGVM_METHOD()
    virtual void Execute() override;
};
```

```cpp
// MyCustomSetupUnit.cpp
#include "MyCustomSetupUnit.h"

void FMyCustomSetupUnit::Execute()
{
    // 先调用父类的执行逻辑来填充 GroupNames
    FRigUnit_SetupShapeLibraryFromLayer::Execute();

    // 自定义逻辑：获取第一个组名
    if (GroupNames.Num() > 0)
    {
        FirstGroupName = GroupNames[0];
    }
    else
    {
        FirstGroupName = NAME_None;
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ControlRig` | 提供 RigUnit 基础框架和动画控制核心。 |
| `GeometryProcessing` | 用于处理网格体几何数据，如多边形组操作。 |

## 维护状态

### 近期更新

- 2026-04-24 `7faab2ed` Direct Mesh Control: fixed library and proxies being GCd
- 2026-04-16 `090ee041` Animation Mode: support for hovered state and colors for gizmo libraries
- 2026-04-15 `f5734c77` Direct Mesh Control: documentation pass
- 2026-04-14 `da21a789` Direct Mesh Control: remove useless logs
- 2026-04-14 `331f0ab8` Direct Mesh Control: force DMC components animation updates in editor

### 维护评价

-   **创建时间**：2026-04-14（未来日期，数据可能为模拟或占位符）。
-   **维护状态**：**实验性插件**。根据 `.uplugin` 标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，表明此插件处于早期开发阶段，API 和功能可能不稳定，不建议在生产环境中使用。
-   **推荐度**：仅推荐用于学习、研究或早期原型开发。使用前需做好功能可能变更或移除的心理准备。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/DirectMeshControl)
-   [官方文档]()（暂无）
-   [测试用例]()（暂未发现）