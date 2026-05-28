# Chooser

> Use Chooser and Proxy Tables to build dynamic asset selection logic.

| 属性 | 值 |
|---|---|
| 中文名 | 条件选择器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `Chooser` (Runtime), `ChooserEditor` (Runtime), `ChooserUncooked` (Runtime), `ProxyTable` (Runtime), `ProxyTableEditor` (Runtime), `ProxyTableUncooked` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-16 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Chooser) | |

## 用途

**Chooser** 插件解决的是传统 `DataTable` 在复杂、动态逻辑下的选择与映射问题。它提供了一套**可视化的、条件驱动的数据表编辑器**（`ChooserTable` 资产），允许开发者定义一系列的“列”（条件检查器）和“行”（选择规则）。当需要从多个候选项中根据当前游戏上下文（如角色状态、距离、属性等）动态选择一个资产、类或其它数据时，`ChooserTable` 会按行顺序评估每个条件列，第一个所有条件都满足的行即为选中结果。

它与 **ProxyTable** 协同工作，`ProxyTable` 用于定义对象类型（如动画蓝图类），而 `ChooserTable` 则基于 `ProxyTable` 提供的上下文信息来进行评估和选择。这本质上是一个**强大的运行时决策表系统**，将原本散落在蓝图或 C++ 中的复杂 `if-else` 或 `switch-case` 逻辑，转化为一个易于编辑、可视化和复用的数据资产。

## 使用场景

- **动画系统**：根据角色移动速度、是否在空中、持有武器类型等条件，动态选择播放的动画蒙太奇或动画序列。例如，使用 `ChooserPlayer` 动画图节点。
- **游戏逻辑**：在对话系统中，根据玩家的声望、已完成的任务、当前区域等条件，选择不同的对话选项或 NPC 行为。
- **UI 系统**：根据当前平台、游戏进度或玩家设置，选择不同的 UI 模板、图标或背景。
- **随机生成**：结合“随机化”列，实现可控的随机选择（如从一堆宝箱中随机选一个，但稀有物品有更高权重）。
- **类选择**：根据上下文（如游戏模式、玩家技能）动态选择要实例化的 `UClass`。

## 蓝图用法

### 核心资产与节点

Chooser 系统在蓝图中主要通过两种资产工作：
1.  **ChooserTable**：核心的条件选择表。
2.  **ChooserSignature** / **ProxyTable**：定义评估所需的上下文（参数）类型。

| 节点 / 操作 | 说明 | 所在类/资产 |
|---|---|---|
| **创建 ChooserTable 资产** | 在内容浏览器中右键创建。创建时需要选择一种“初始化器”（`ChooserInitializer`），如“Generic Chooser”（通用）或“Animation Chooser”（动画专用）。 | `UChooserTableFactory` |
| **配置初始化器** | 在 ChooserTable 资产编辑器中，根节点属性决定了表的输入（参数）和输出（结果）类型。例如 `FGenericChooserInitializer` 可以指定返回 `Object` 或 `Class`，以及可接受的参数类型。 | `FGenericChooserInitializer` |
| **“Chooser Player” 动画图节点** | 在动画蓝图中使用，其输入是一个 `ChooserTable` 资产（类型需为 `FChooserPlayerInitializer`）。节点会基于当前动画实例等上下文评估 Chooser，输出选中的动画资产。 | `UChooserPlayer` (动画图节点) |
| **蓝图中的动态评估** | 在蓝图中，可以通过创建 `UChooserEvaluator` 对象，并设置其参数上下文（`ContextData`）来动态评估一个 `ChooserTable`。 | `UChooserEvaluator` |
| **获取评估结果** | 评估后，可以从评估器中获取主要结果（`PrimaryResult`，通常是资产或类引用）或从输出参数获取写入的值（如浮点数、字符串）。 | `UChooserEvaluator` |

**使用示例（蓝图描述）**：
1.  在动画蓝图的 `EventGraph` 中，添加一个 `Chooser Player` 节点。
2.  将你的动画 `ChooserTable` 资产（已配置好移动速度、是否空中等列）拖拽到该节点的 `Chooser` 引脚。
3.  将 `Animation Update` 事件连接到 `Chooser Player` 的执行引脚。
4.  `Chooser Player` 的输出引脚 `Animation` 即为当前上下文选中的动画资产，将其连接到动画状态机或 `Montage Play` 节点。
5.  当角色移动时，`Chooser Player` 节点会根据 `AnimInstance` 提供的速度、是否在地面等信息，自动更新 `Animation` 输出。

## C++ 用法

### 头文件引入

```cpp
#include "ChooserTable.h"
#include "ChooserEvaluator.h"
#include "ProxyTable.h"
```

### 基本用法

评估一个 ChooserTable 并获取结果。

```cpp
// 来源: 基于 ChooserRuntime 模块公共 API 推断
void EvaluateMyChooserTable(UChooserTable* MyChooserTable, UObject* ContextObject)
{
    // 1. 创建一个评估器
    UChooserEvaluator* Evaluator = NewObject<UChooserEvaluator>();

    // 2. 设置评估所需的上下文（参数）。这必须与 ChooserTable 的初始化器中定义的参数匹配。
    // 假设 ChooserTable 需要一个 AnimInstance 和一个 float 作为参数。
    FInstancedStruct AnimInstanceParam;
    AnimInstanceParam.InitializeAs(FContextObjectType_AnimInstance::StaticStruct());
    AnimInstanceParam.GetMutable<FContextObjectType_AnimInstance>().Object = Cast<UAnimInstance>(ContextObject);
    Evaluator->AddContextData(MoveTemp(AnimInstanceParam));

    FInstancedStruct FloatParam;
    FloatParam.InitializeAs(FContextObjectType_Float::StaticStruct());
    FloatParam.GetMutable<FContextObjectType_Float>().Value = 15.0f; // 例如速度
    Evaluator->AddContextData(MoveTemp(FloatParam));

    // 3. 执行评估
    Evaluator->Evaluate(MyChooserTable);

    // 4. 获取主要结果（例如，一个动画资产）
    FObjectChooserResult PrimaryResult = Evaluator->GetPrimaryResult();
    if (PrimaryResult.ResultType == EObjectChooserResultType::ObjectResult)
    {
        UObject* ResultAsset = PrimaryResult.Object;
        if (ResultAsset)
        {
            // 使用选中的资产...
        }
    }
}
```

### 进阶用法

使用 `ChooserEvaluator` 写入输出参数（当 ChooserTable 包含“写入”类型的列时）。

```cpp
// 在上面的评估器设置完成后...
// 5. 获取输出参数（假设 ChooserTable 会向一个名为 “OutBlendTime” 的参数写入浮点值）
const FInstancedStruct* OutputParam = Evaluator->FindOutputParameter(TEXT("OutBlendTime"));
if (OutputParam)
{
    const FContextObjectType_Float* OutFloat = OutputParam->GetPtr<FContextObjectType_Float>();
    if (OutFloat)
    {
        float BlendTime = OutFloat->Value; // 这个值是 ChooserTable 选中行所设定的
        // 使用 BlendTime...
    }
}
```

## Demo 示例

一个最小示例，展示如何在 C++ 中评估一个配置好的 ChooserTable。

```cpp
// MyCharacter.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "MyCharacter.generated.h"

class UChooserTable;
class UAnimMontage;

UCLASS()
class AMyCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyCharacter();

    // 一个指向 ChooserTable 资产的引用，可在编辑器中设置
    UPROPERTY(EditDefaultsOnly, Category = "Animation")
    TObjectPtr<UChooserTable> AttackChooserTable;

    void PlayAttackMontage();

protected:
    virtual void BeginPlay() override;
};

// MyCharacter.cpp
#include "MyCharacter.h"
#include "ChooserTable.h"
#include "ChooserEvaluator.h"
#include "Animation/AnimMontage.h"

AMyCharacter::AMyCharacter()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();
    // 初始时可选择性地评估一次，或延迟到需要时
}

void AMyCharacter::PlayAttackMontage()
{
    if (!AttackChooserTable) return;

    // 创建评估器
    UChooserEvaluator* Evaluator = NewObject<UChooserEvaluator>();

    // 添加上下文：当前动画实例
    if (UAnimInstance* AnimInst = GetMesh()->GetAnimInstance())
    {
        FInstancedStruct AnimParam;
        AnimParam.InitializeAs(FContextObjectType_AnimInstance::StaticStruct());
        AnimParam.GetMutable<FContextObjectType_AnimInstance>().Object = AnimInst;
        Evaluator->AddContextData(MoveTemp(AnimParam));
    }

    // 执行评估
    Evaluator->Evaluate(AttackChooserTable);

    // 获取结果：一个 AnimMontage
    FObjectChooserResult Result = Evaluator->GetPrimaryResult();
    if (UAnimMontage* AttackMontage = Cast<UAnimMontage>(Result.Object))
    {
        // 播放选中的攻击动画
        PlayAnimMontage(AttackMontage);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Chooser` | 核心运行时逻辑，包含 ChooserTable、Evaluator、Column 类型等 |
| `ChooserEditor` | ChooserTable 和 ChooserSignature 的资产编辑器、自定义 UI、调试工具 |
| `ProxyTable` | ProxyTable 运行时逻辑，用于定义对象/类上下文 |
| `ProxyTableEditor` | ProxyTable 的资产编辑器 |
| `UnrealEd` | 用于资产编辑器基础功能 |
| `PropertyEditor` | 用于细节面板自定义 |
| `AnimationEditor` / `Persona` | 用于动画 Chooser 与动画图编辑器的集成 |
| `TraceServices` | 用于 Chooser 的调试与性能分析追踪 |

**注**：无特殊依赖（仅标准 Core/Engine/Slate 等）之外的依赖已在上表列出。实际使用时，你的 `Build.cs` 可能需要依赖 `Chooser` 和/或 `ProxyTable` 模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `aad6fe75` | Remove build setting making chooser internal headers public, and move most of those internal headers | 清理编译设置，将大部分内部头文件移回私有目录，提高模块封装性。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下 double 常量隐式转换为 float 导致的编译警告。 |
| 2026-05-12 | `333cccbc` | Add profiling tag to chooser property access | 为 Chooser 的属性访问添加性能分析标签，便于性能分析工具识别。 |
| 2026-04-17 | `1eda8a87` | Fix chooser editor null pointer crash after native context type rename | 修复在重命名原生上下文类型后，编辑器发生的空指针崩溃问题。 |
| 2026-04-16 | `0b4d09a4` | [ContentBrowser] New Add Menu Data Menu | 与内容浏览器“新建”菜单的数据表子菜单集成。 |

### 维护评价

**综合评价：活跃维护中**。
- **创建时间**：插件于 2024 年 9 月从 Experimental 迁出，年龄约 2 年，是一个相对较新但已成熟的模块。
- **更新频率**：近期（2026年4-5月）有持续的代码提交，包括 bug 修复、性能优化、编辑器集成改进和内部代码清理，表明开发团队仍在积极维护和优化此插件。
- **稳定性**：提交记录显示修复了编辑器崩溃和编译警告，致力于提升稳定性。
- **推荐度**：**强烈推荐使用**。这是一个功能强大、设计现代、且得到 Epic 官方持续支持的动画和游戏逻辑工具。它填补了传统数据表的空白，是处理复杂动态选择逻辑的首选方案。默认禁用状态主要是为了控制项目大小和避免不需要的依赖，使用前需要手动启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Chooser)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Chooser/Tests)