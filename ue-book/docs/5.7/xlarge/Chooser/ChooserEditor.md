# Chooser

> Use Chooser and Proxy Tables to build dynamic asset selection logic.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `Chooser` (Runtime), `ChooserEditor` (Runtime), `ChooserUncooked` (Runtime), `ProxyTable` (Runtime), `ProxyTableEditor` (Runtime), `ProxyTableUncooked` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-05-16 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Chooser) | |

## 用途

Chooser 插件提供了一个**数据驱动的、可视化的资产选择系统**。它解决的核心问题是：如何在运行时，根据一组复杂的、动态的输入条件（如角色状态、游戏进度、玩家选择等），从一个预定义的集合中选择出正确的资产（如动画、材质、声音、蓝图类等）。

传统的做法可能需要编写大量的 `if-else` 或 `switch-case` 逻辑，或者使用数据表（DataTable）进行简单的键值查找。Chooser 将这种选择逻辑提升为一个**可编辑、可调试、可复用的资产**（`UChooserTable`）。开发者可以在编辑器中通过一个类似电子表格的界面，直观地配置输入条件（列）和对应的输出结果（行），从而将复杂的逻辑从代码中剥离出来，极大地提高了灵活性和可维护性。

## 使用场景

- **动画状态机**：根据角色的移动速度、是否在空中、装备的武器类型等多个条件，动态选择播放哪个动画蒙太奇或动画序列。
- **游戏逻辑**：根据玩家等级、已完成的任务、拥有的物品等条件，动态决定下一个任务目标、对话选项或奖励。
- **资产变体管理**：为同一个角色或物体准备多种材质、模型或特效变体，并根据游戏内事件（如天气、时间、状态）动态切换。
- **需要可视化配置复杂选择逻辑**：当选择逻辑的条件和结果组合非常复杂，用纯代码难以维护和理解时，使用 Chooser 表格可以一目了然。
- **需要运行时动态评估**：选择逻辑不是固定的，可能需要根据实时变化的游戏状态进行评估。

## 蓝图用法

Chooser 插件的核心蓝图交互围绕 `UChooserTable` 资产和其评估结果展开。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Evaluate Chooser` | 对一个 ChooserTable 进行评估，根据传入的上下文对象返回选择结果。这是最核心的运行时节点。 | `UChooserTable` |
| `Get Chooser Result` | 从评估结果中提取具体的资产（Object）或类（Class）。 | `FObjectChooserResult` |
| `Create Chooser Table` | 在蓝图中动态创建一个新的 ChooserTable 实例（通常用于测试或程序化生成）。 | `UChooserTable` |

### 使用示例（蓝图描述）

1.  **准备上下文**：在蓝图中，你需要有一个或多个“上下文对象”（Context Object），这些对象包含了 Chooser 表格进行决策所需的信息。例如，一个 `Character` 对象，它可能有 `Speed`、`IsInAir` 等属性。
2.  **评估 Chooser**：使用 `Evaluate Chooser` 节点，将你的 `UChooserTable` 资产和上下文对象连接起来。
3.  **处理结果**：`Evaluate Chooser` 节点会输出一个 `FObjectChooserResult` 结构体。使用 `Get Chooser Result` 节点可以从中获取最终选择的资产（如一个 `UAnimMontage`）或类（如一个 `UClass`）。
4.  **应用结果**：将获取到的资产或类用于后续逻辑，例如播放动画、生成物体等。

## C++ 用法

在 C++ 中，主要通过 `UChooserTable` 的 API 来评估选择逻辑，并通过 `FObjectChooserResult` 来获取结果。

### 头文件引入

```cpp
#include "Chooser.h"
#include "ChooserPropertyAccess.h" // 如果需要处理属性绑定
```

### 基本用法

以下示例展示了如何在 C++ 中评估一个 ChooserTable 并获取结果。

```cpp
// 假设你已经有一个 UChooserTable* 指针 ChooserTableAsset
// 以及一个作为上下文的 UObject* ContextObject (例如你的角色)

if (ChooserTableAsset && ContextObject)
{
    // 创建评估上下文，将上下文对象添加进去
    FChooserEvaluationContext Context;
    Context.AddObjectParam(ContextObject);

    // 评估 Chooser 表格
    FObjectChooserResult Result = ChooserTableAsset->Evaluate(Context);

    // 检查结果类型并获取资产
    if (Result.ResultType == EObjectChooserResultType::ObjectResult)
    {
        UObject* SelectedAsset = Result.Object.Get();
        if (SelectedAsset)
        {
            // 使用选中的资产，例如转换为动画资产
            UAnimMontage* SelectedMontage = Cast<UAnimMontage>(SelectedAsset);
            if (SelectedMontage)
            {
                // 播放动画...
            }
        }
    }
    else if (Result.ResultType == EObjectChooserResultType::ClassResult)
    {
        UClass* SelectedClass = Result.Class;
        if (SelectedClass)
        {
            // 使用选中的类，例如生成一个该类的实例
            // GetWorld()->SpawnActor<AActor>(SelectedClass, ...);
        }
    }
}
```
*（基于 `UChooserTable::Evaluate` 和 `FObjectChooserResult` 的典型用法推断）*

### 进阶用法

Chooser 的强大之处在于其列（Column）系统，每一列代表一个决策条件。在 C++ 中，你可以通过 `FChooserColumnBase` 的派生类来定义自定义的决策逻辑。这通常涉及到实现 `Evaluate` 方法，并访问通过 `FChooserPropertyBinding` 绑定的属性。

```cpp
// 自定义一个 Chooser 列，用于检查角色的生命值
UCLASS()
class UChooserColumn_HealthCheck : public UChooserColumnBase
{
    GENERATED_BODY()

public:
    // 绑定到上下文对象上的一个浮点属性 (例如 CurrentHealth)
    UPROPERTY(EditAnywhere, Category = "Binding")
    FChooserPropertyBinding HealthProperty;

    // 评估逻辑：检查生命值是否大于阈值
    virtual bool Evaluate(FChooserEvaluationContext& Context, int32 RowIndex) const override
    {
        // 通过绑定的属性获取当前生命值
        float CurrentHealth = 0.f;
        if (HealthProperty.GetValue(Context, CurrentHealth))
        {
            // 假设表格中该行的值是一个阈值，存储在 FChooserColumnData 中
            // 这里简化逻辑，实际需要从行数据中读取阈值
            const float Threshold = 50.f; // 示例阈值
            return CurrentHealth > Threshold;
        }
        return false;
    }
};
```
*（基于 `FChooserColumnBase` 和 `FChooserPropertyBinding` 的结构推断）*

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何创建并评估一个简单的 ChooserTable。

**MyGameMode.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "MyGameMode.generated.h"

class UChooserTable;

UCLASS()
class AMyGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    // 在编辑器中指定一个 ChooserTable 资产
    UPROPERTY(EditAnywhere, Category = "Chooser")
    TObjectPtr<UChooserTable> AssetChooser;

    virtual void StartPlay() override;
};
```

**MyGameMode.cpp**
```cpp
#include "MyGameMode.h"
#include "Chooser.h"

void AMyGameMode::StartPlay()
{
    Super::StartPlay();

    if (AssetChooser)
    {
        // 创建一个评估上下文（此示例没有上下文对象，Chooser 可能返回默认/第一行结果）
        FChooserEvaluationContext Context;

        // 评估 Chooser
        FObjectChooserResult Result = AssetChooser->Evaluate(Context);

        if (Result.ResultType == EObjectChooserResultType::ObjectResult && Result.Object.IsValid())
        {
            UE_LOG(LogTemp, Log, TEXT("Chooser selected asset: %s"), *Result.Object->GetName());
            // 在这里使用选中的资产
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AnimationCore` | 提供动画系统核心功能，Chooser 与动画深度集成。 |
| `PropertyEditor` | 用于在编辑器中创建自定义属性编辑器（如 `SPropertyAccessChainWidget`）。 |
| `GameplayTagsEditor` | 用于在编辑器中提供 GameplayTag 选择器。 |
| `StructViewer` | 用于在编辑器中提供结构体选择器（`FStructFilter`）。 |
| `ClassViewer` | 用于在编辑器中提供类选择器（`FInterfaceClassFilter`）。 |

## 维护状态

### 近期更新

- c105bb26a3b8 Fix for nested choosers not respecting root chooser Result Type
  *修复了嵌套 Chooser 不遵循根 Chooser 结果类型的问题。*
- 7762fe096295 Chooser - fix for crash when changing column type from Pose Match to a different column and then back to PoseMatch
  *修复了将列类型从 PoseMatch 切换到其他类型再切回时导致的崩溃。*
- a25fd38da594 Fix chooser parameter search incorrectly reporting that unindexed assets need to be loaded
  *修复了 Chooser 参数搜索错误地报告未索引资产需要加载的问题。*

### 维护评价

**活跃维护**。该插件创建于 2022 年，属于较新的功能。从最近的提交记录看，维护团队仍在积极修复 bug 和改进功能（最近一次提交在 2025 年）。提交信息表明插件仍在迭代中，解决了嵌套评估、编辑器稳定性和资产加载等实际问题。作为 Epic Games 官方维护的插件，其稳定性和未来支持有保障。**推荐使用**，特别是对于需要复杂、可配置资产选择逻辑的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Chooser)
- [官方文档]() （暂无）
- [测试用例]() （需在源码仓库中搜索 `Chooser` 相关测试文件）