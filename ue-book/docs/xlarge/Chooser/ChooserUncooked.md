# Chooser

> Use Chooser and Proxy Tables to build dynamic asset selection logic.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具） |
| 模块 | `Chooser` (Runtime), `ChooserEditor` (Editor), `ChooserUncooked` (UncookedOnly), `ProxyTable` (Runtime), `ProxyTableEditor` (Editor), `ProxyTableUncooked` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2022-05-16 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Chooser) | |

## 用途

Chooser 插件提供了一套数据驱动的资产选择系统，核心目标是让设计师能够在不编写代码的情况下，构建复杂的、基于上下文的动态资产选择逻辑。它主要解决动画系统中根据游戏状态（如角色属性、游戏标签、输入等）动态选择不同动画蒙太奇（AnimMontage）、动画序列（AnimSequence）或其他资产的问题。

该插件包含两个核心概念：
1.  **Chooser**：一个类似数据表的资产，其中每一行代表一个可能的“结果”（如一个动画蒙太奇），每一列代表一个“输入条件”（如一个 GameplayTag、一个布尔值、一个浮点数范围）。运行时，系统会根据提供的上下文数据，匹配 Chooser 表中的条件，返回符合条件的结果。
2.  **Proxy Table**：提供了一层抽象。它允许你引用一个“代理”资产（如一个抽象的动画接口），而不是直接引用具体的资产。在运行时，系统会根据上下文，通过 Chooser 或其他逻辑，将这个代理解析为一个具体的资产。这增强了系统的模块化和可扩展性。

## 使用场景

-   **动态动画选择**：在角色动画蓝图中，根据角色是否在战斗、是否受伤、装备的武器类型等条件，从一组候选动画蒙太奇中动态选择一个播放。
-   **技能系统**：根据技能等级、角色属性或目标状态，选择不同的技能特效、音效或动画。
-   **模块化资产引用**：在大型项目中，使用 Proxy Table 来定义资产接口（如“近战攻击动画”），具体的资产实现可以由不同的 Chooser 表或子系统提供，便于团队协作和资产替换。
-   **数据驱动的配置**：将复杂的 if-else 选择逻辑外置为数据表（Chooser 资产），方便策划调整和迭代，无需修改代码或蓝图。

## 蓝图用法

Chooser 的核心蓝图功能是通过动画蓝图节点和专门的评估函数暴露的。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Chooser Player` | 动画蓝图节点。将 Chooser 资产的评估结果作为动画输入，驱动动画混合栈。 | `UAnimGraphNode_ChooserPlayer` |
| `Evaluate Chooser` | （推断）蓝图函数节点，用于在任意蓝图中评估一个 Chooser 资产并获取结果。 | `UChooserTable` (推测) |
| `Evaluate Proxy` | （推断）蓝图函数节点，用于评估一个 Proxy Table 资产，解析出具体的资产引用。 | `UProxyTable` (推测) |

### 使用示例（蓝图描述）

1.  **在动画蓝图中使用 Chooser Player**：
    *   打开角色的动画蓝图。
    *   在 AnimGraph 中，右键搜索并添加 `Chooser Player` 节点。
    *   在节点的细节面板中，指定一个 `Chooser` 资产（例如 `CT_CharacterActions`）。
    *   将该节点的输出姿势连接到最终的动画输出节点。
    *   在事件图表中，通过 `Update Context` 等函数（具体函数名需查证）将当前的游戏状态（如 `GameplayTag`、`bIsInCombat`）设置到 Chooser 的上下文中，节点会自动根据上下文选择正确的动画。

2.  **在普通蓝图中评估 Chooser**：
    *   获取一个 Chooser 资产的引用。
    *   调用 `Evaluate Chooser` 节点，传入 Chooser 资产和所需的上下文数据（通常是一个结构体或一系列参数）。
    *   节点会返回匹配的结果（例如一个 `UAnimMontage*` 或 `TSoftObjectPtr`）。

## C++ 用法

### 头文件引入

```cpp
#include "ChooserTable.h"
#include "ProxyTable.h"
#include "AnimNode_ChooserPlayer.h"
```

### 基本用法

以下示例展示了如何在 C++ 中评估一个 Chooser 表。此用法基于插件核心逻辑推断。

```cpp
// 假设你已经有一个 UChooserTable* ChooserAsset 和一个 FChooserEvaluationContext Context
// Context 中包含了当前的游戏状态数据

// 评估 Chooser 表
FChooserSelectedRow SelectedRow = ChooserAsset->Evaluate(Context);

if (SelectedRow.IsValid())
{
    // 获取结果。结果类型取决于 Chooser 表的配置，可能是 UObject*, FInstancedStruct 等。
    // 例如，如果结果列是动画蒙太奇：
    UAnimMontage* ResultMontage = Cast<UAnimMontage>(SelectedRow.Value.Get<UObject*>());
    if (ResultMontage)
    {
        // 播放动画蒙太奇
        // ...
    }
}
```

### 进阶用法

结合 Proxy Table 实现抽象资产引用。

```cpp
// 1. 定义一个代理表资产 (UProxyTable*) ProxyTableAsset
// 2. 在代码中，通过代理表获取实际资产
FChooserEvaluationContext Context; // 填充上下文
UObject* ResolvedAsset = ProxyTableAsset->Resolve(Context);

// 3. 使用解析后的资产
UAnimMontage* Montage = Cast<UAnimMontage>(ResolvedAsset);
if (Montage)
{
    // 使用具体的蒙太奇
}
```

## Demo 示例

以下是一个自定义 Chooser 评估器的最小示例，用于在 C++ 中扩展 Chooser 的功能。

**MyChooserFunction.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "ChooserFunction.h"
#include "MyChooserFunction.generated.h"

// 自定义一个 Chooser 函数，用于在评估时计算一个自定义值
UCLASS()
class UMyChooserFunction : public UChooserFunction
{
    GENERATED_BODY()

public:
    // 在 Chooser 表的列中作为可选函数暴露
    virtual FInstancedStruct Evaluate(const FChooserEvaluationContext& Context) const override;

    // 函数的输入参数定义（在编辑器中配置）
    UPROPERTY(EditAnywhere, Category = "Parameters")
    float Multiplier = 1.0f;
};
```

**MyChooserFunction.cpp**
```cpp
#include "MyChooserFunction.h"

FInstancedStruct UMyChooserFunction::Evaluate(const FChooserEvaluationContext& Context) const
{
    // 从上下文中获取一个浮点值（假设上下文中有名为 “BaseValue” 的属性）
    float BaseValue = Context.GetValue<float>(FName("BaseValue"));

    // 计算结果
    float Result = BaseValue * Multiplier;

    // 将结果包装成 FInstancedStruct 返回
    FInstancedStruct ResultStruct;
    ResultStruct.InitializeAs<float>();
    ResultStruct.GetMutable<float>() = Result;
    return ResultStruct;
}
```

## 模块依赖

从模块名称和常见模式推断，使用此插件可能需要以下依赖（需在项目的 `.Build.cs` 中添加）：

| 模块 | 用途 |
|---|---|
| `Chooser` | Chooser 和 ProxyTable 的核心运行时逻辑。 |
| `GameplayTags` | Chooser 的条件列广泛使用 GameplayTags 进行匹配。 |
| `AnimGraphRuntime` | 与动画蓝图节点（如 Chooser Player）交互所需。 |
| `PropertyAccess` | 用于在 Chooser 中访问对象属性作为输入条件。 |

## 维护状态

### 近期更新

```
- 87bed3a038da Fix for BP compile errors with EvaluateChooser and EvaluateProxy when using Class outputs, and "All Results" Array output mode
- e12378c050fe Support for accessing any context member from PoseSearchFeatureChannel_Distance blueprint subclasses, rather than only the AnimInstance
- ec25460b543e Update title of Chooser Player nodes to contain the asset name, which also allows find in blueprints to find those nodes when searching for a chooser or proxy asset name
```

*   最近的提交修复了蓝图编译错误，增强了上下文访问能力，并改进了编辑器中的节点标题显示，表明插件仍在积极维护和改进中。

### 维护评价

-   **创建时间**：约3年前（2022年），属于较新的插件。
-   **更新频率**：近期有实质性功能更新和错误修复，表明处于**活跃维护**状态。
-   **功能状态**：作为 Epic 官方提供的动画系统增强工具，功能相对完整和稳定。
-   **推荐度**：**推荐使用**。对于需要复杂、数据驱动动画选择逻辑的项目，这是一个强大且官方支持的解决方案。由于默认未启用，需要在项目设置中手动开启。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Chooser)