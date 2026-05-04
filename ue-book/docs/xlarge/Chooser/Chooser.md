# Chooser

> Use Chooser and Proxy Tables to build dynamic asset selection logic.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、Chooser 表资产） |
| 模块 | `Chooser` (Runtime), `ChooserEditor` (Runtime), `ChooserUncooked` (Runtime), `ProxyTable` (Runtime), `ProxyTableEditor` (Runtime), `ProxyTableUncooked` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-05-16 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Chooser) | |

## 用途

Chooser 是一个**数据驱动的动态资产选择系统**，用于在运行时根据输入参数从预定义的表中选择最匹配的结果。它解决的核心问题是：**如何用可视化、可配置的方式替代硬编码的 if/else 链或 switch 语句来选择资产**。

典型场景：根据角色状态、GameplayTag、枚举值等条件，动态选择要播放的动画、要生成的 Actor 类、要使用的材质等。Chooser Table 类似于数据表，但每一列都是一个**过滤条件或输出参数**，每一行是一个候选结果。评估时，系统逐列过滤，最终选出匹配的行并返回其关联的资产。

与 ProxyTable 配合使用时，可以实现**间接资产引用**——通过代理键查找实际资产，支持运行时替换和热重载。

## 使用场景

- 你有大量动画需要根据角色状态（移动方向、速度、装备类型等）动态选择 → 用 Chooser Table
- 你需要根据 GameplayTag 组合选择不同的资产 → 用 Chooser 的 GameplayTag 列
- 你需要一个可配置的"随机选择"系统，且要避免连续重复 → 用 Randomize 列
- 你需要根据浮点值（如速度、角度）选择最接近的动画 → 用 FloatDistance 评分列
- 你需要在运行时动态替换资产引用（如 DLC 替换）→ 用 ProxyTable
- 你需要在动画蓝图中根据条件选择动画资产 → 用 ChooserPlayer 动画节点

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EvaluateChooser` | 评估 Chooser Table 并返回选中的 UObject | `UChooserFunctionLibrary` |
| `EvaluateChooserMulti` | 评估 Chooser Table 并返回所有匹配的 UObject 列表 | `UChooserFunctionLibrary` |
| `EvaluateObjectChooserBase` | 评估任意 ObjectChooser 实现并返回选中的 UObject | `UChooserFunctionLibrary` |
| `EvaluateObjectChooserBaseMulti` | 评估任意 ObjectChooser 实现并返回所有匹配结果 | `UChooserFunctionLibrary` |
| `EvaluateObjectChooserBaseSoft` | 评估并返回软引用结果 | `UChooserFunctionLibrary` |
| `AddChooserObjectInput` | 向评估上下文添加 UObject 参数 | `UChooserFunctionLibrary` |
| `AddChooserStructInput` | 向评估上下文添加 Struct 参数 | `UChooserFunctionLibrary` |
| `GetChooserObjectInput` | 从评估上下文获取指定索引的 UObject | `UChooserFunctionLibrary` |

### 使用示例（蓝图描述）

**基本用法 - 评估 Chooser Table：**

1. 创建一个 `ChooserTable` 资产（右键 → Animation → Chooser Table）
2. 在 Chooser Table 编辑器中配置列（过滤条件）和行（候选结果）
3. 在蓝图中：
   - 使用 `EvaluateChooser` 节点
   - 连接 Context Object（通常是 Self，即当前 Actor）
   - 连接 ChooserTable 资产引用
   - 指定期望的结果类型（ObjectClass）
   - 输出即为选中的资产对象

**带上下文的用法：**

1. 创建 `FChooserEvaluationContext` 结构体
2. 使用 `AddChooserObjectInput` 添加上下文对象
3. 使用 `EvaluateObjectChooserBase` 进行评估
4. 可以添加多个上下文对象，Chooser 会从中读取属性进行匹配

## C++ 用法

### 头文件引入

```cpp
#include "ChooserFunctionLibrary.h"
#include "Chooser.h"
#include "IObjectChooser.h"
```

### 基本用法

```cpp
// 评估 Chooser Table 并获取结果
// 来源: ChooserFunctionLibrary.h

// 创建评估上下文
FChooserEvaluationContext Context;
Context.AddObjectParam(MyActor);  // 添加上下文对象

// 评估 Chooser Table
UObject* Result = UChooserFunctionLibrary::EvaluateChooser(
    MyActor,           // 上下文对象
    MyChooserTable,    // UChooserTable* 资产
    UAnimSequence::StaticClass()  // 期望的结果类型
);

if (Result)
{
    UAnimSequence* AnimSequence = Cast<UAnimSequence>(Result);
    // 使用选中的动画
}
```

### 进阶用法

```cpp
// 使用 InstancedStruct 进行通用 Chooser 评估
// 来源: ChooserFunctionLibrary.h, IObjectChooser.h

// 创建评估上下文，支持多个参数
FChooserEvaluationContext Context;
Context.AddObjectParam(CharacterActor);
Context.AddObjectParam(WeaponActor);

// 添加结构体参数（如自定义数据）
FMyCustomData CustomData;
CustomData.Speed = 500.0f;
Context.AddStructParam(CustomData);

// 评估通用 ObjectChooser（支持 ChooserTable 和 ProxyTable）
FInstancedStruct ObjectChooser;
// ... 设置 ObjectChooser 实现

UObject* Result = UChooserFunctionLibrary::EvaluateObjectChooserBase(
    Context,
    ObjectChooser,
    UAnimationAsset::StaticClass(),
    false  // bResultIsClass = false，返回对象实例
);

// 获取多个结果
TArray<UObject*> AllResults = UChooserFunctionLibrary::EvaluateObjectChooserBaseMulti(
    Context,
    ObjectChooser,
    UAnimationAsset::StaticClass(),
    false
);
```

```cpp
// 在动画节点中使用 Chooser
// 来源: AnimNode_ChooserPlayer.h

// FAnimNode_ChooserPlayer 是一个动画节点，可在动画蓝图中使用
// 它会根据 Chooser 的评估结果动态选择动画资产
// 支持以下评估频率：
// - OnInitialUpdate: 仅在初始化时评估
// - OnBecomeRelevant: 在变为相关时评估
// - OnLoop: 在动画循环时重新评估
// - OnUpdate: 每帧评估
```

## Demo 示例

```cpp
// MyChooserComponent.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Chooser.h"
#include "MyChooserComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYGAME_API UMyChooserComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyChooserComponent();

    // Chooser Table 资产引用
    UPROPERTY(EditAnywhere, Category = "Chooser")
    TObjectPtr<UChooserTable> AnimationChooser;

    // 根据当前状态选择动画
    UFUNCTION(BlueprintCallable, Category = "Chooser")
    UAnimationAsset* SelectAnimation();

protected:
    virtual void BeginPlay() override;
};
```

```cpp
// MyChooserComponent.cpp
#include "MyChooserComponent.h"
#include "ChooserFunctionLibrary.h"
#include "Animation/AnimationAsset.h"

UMyChooserComponent::UMyChooserComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMyChooserComponent::BeginPlay()
{
    Super::BeginPlay();
}

UAnimationAsset* UMyChooserComponent::SelectAnimation()
{
    if (!AnimationChooser)
    {
        return nullptr;
    }

    // 评估 Chooser Table，传入 Owner Actor 作为上下文
    UObject* Result = UChooserFunctionLibrary::EvaluateChooser(
        GetOwner(),
        AnimationChooser,
        UAnimationAsset::StaticClass()
    );

    return Cast<UAnimationAsset>(Result);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `StructUtils` | InstancedStruct 支持，用于灵活的类型擦除参数传递 |
| `GameplayTags` | GameplayTag 列和 GameplayTagQuery 列的过滤支持 |
| `BlendStack` | ChooserPlayer 动画节点的混合栈支持 |
| `PoseSearch` | 可选，用于 ChooserPlayer 的姿态匹配功能 |

## 维护状态

### 近期更新

```
- 7733aee6ea57 Add AnimInstance threading sync to blueprint chooser evaluations
- accbcce541ed Fixup API macros
- 7ff009b49aca Chooser - PoseSearchColumn initial support for fallback row
```

- 第一条：修复了蓝图 Chooser 评估中的 AnimInstance 线程同步问题，表明插件在持续优化线程安全性
- 第二条：API 宏修复，属于维护性更新
- 第三条：为 PoseSearch 列添加了回退行支持，是功能性增强

### 维护评价

Chooser 插件创建于 2022 年，至今约 3 年，属于较新的插件。从近期提交记录看，仍在**活跃维护**中，有功能增强（PoseSearch 集成）和 bug 修复（线程同步）。该插件默认未启用（`EnabledByDefault=false`），需要手动在项目设置中启用。

**推荐使用**：对于需要数据驱动资产选择逻辑的项目，Chooser 提供了比硬编码更灵活、更易维护的解决方案。特别是动画选择场景，配合 ChooserPlayer 动画节点可以大幅简化动画蓝图的复杂度。

**注意事项**：
- 插件默认未启用，需手动启用
- 部分功能标记为实验性（如 ScratchArea、ForceBlendTo）
- 需要理解 Chooser Table 的列/行概念和评估流程

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Chooser)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Chooser/Tests)

---

# Chooser 模块文档

## 概述

Chooser 模块是插件的核心运行时模块，包含 Chooser Table 的评估逻辑、列类型定义、参数绑定系统和动画节点集成。

## 核心概念

### Chooser Table（UChooserTable）

Chooser Table 是一个类似数据表的资产，由**行（Rows）**和**列（Columns）**组成：
- **行**：每个行代表一个候选结果（如一个动画资产、一个 Actor 类）
- **列**：每列定义一个过滤条件或输出参数

评估流程：
1. 从所有行开始
2. 逐列应用过滤条件，排除不匹配的行
3. 如果有评分列，计算每行的总成本
4. 选择成本最低的行（或通过 Randomize 列随机选择）
5. 返回该行关联的结果对象，并执行输出列的写入操作

### 列类型

#### 过滤列（Filter Columns）

| 列类型 | 说明 | 输入类型 |
|---|---|---|
| `FBoolColumn` | 布尔值过滤 | bool |
| `FEnumColumn` | 枚举值过滤（等于/不等于/任意） | uint8 (enum) |
| `FMultiEnumColumn` | 多选枚举过滤（位掩码匹配） | uint8 (enum) |
| `FObjectColumn` | 对象引用过滤 | UObject* |
| `FObjectClassColumn` | 对象类过滤（子类检查） | UClass* |
| `FGameplayTagColumn` | GameplayTag 匹配过滤 | FGameplayTagContainer |
| `FGameplayTagQueryColumn` | GameplayTag 查询过滤 | FGameplayTagContainer |
| `FFloatRangeColumn` | 浮点范围过滤 | double |

#### 评分列（Scoring Columns）

| 列类型 | 说明 | 输入类型 |
|---|---|---|
| `FFloatDistanceColumn` | 浮点距离评分（选择最接近的值） | double |

#### 随机列（Random Columns）

| 列类型 | 说明 |
|---|---|
| `FRandomizeColumn` | 随机选择，支持权重和避免重复 |

#### 输出列（Output Columns）

| 列类型 | 说明 | 输出类型 |
|---|---|---|
| `FOutputBoolColumn` | 写入布尔值 | bool |
| `FOutputFloatColumn` | 写入浮点值 | double |
| `FOutputEnumColumn` | 写入枚举值 | uint8 |
| `FOutputObjectColumn` | 写入对象引用 | UObject* |
| `FOutputStructColumn` | 写入结构体 | FInstancedStruct |
| `FOutputGameplayTagQueryColumn` | 写入 GameplayTag 查询 | FGameplayTagQuery |

### 参数绑定系统

Chooser 使用属性绑定（Property Binding）系统从上下文对象读取/写入属性：

- `FChooserPropertyBinding`：通用属性绑定，支持链式属性访问
- `FChooserObjectPropertyBinding`：对象属性绑定
- `FChooserEnumPropertyBinding`：枚举属性绑定
- `FChooserStructPropertyBinding`：结构体属性绑定

绑定通过 `FChooserEvaluationContext` 传递上下文对象，支持多层属性链访问。

### Object Chooser 接口

`FObjectChooserBase` 是所有对象选择器的基类：

| 实现 | 说明 |
|---|---|
| `FAssetChooser` | 硬引用特定资产 |
| `FSoftAssetChooser` | 软引用特定资产 |
| `FClassChooser` | 返回一个类（用于 ClassResult 模式） |

### ChooserPlayer 动画节点

`FAnimNode_ChooserPlayer` 是一个动画节点，集成 Chooser 评估到动画蓝图中：
- 支持混合空间参数（BlendSpaceX/Y）
- 支持镜像动画（MirrorDataTable）
- 支持自定义播放设置（播放速率、起始时间、循环等）
- 支持惯性混合（Inertial Blend）
- 支持姿态匹配（PoseSearch，实验性）

## 关键类

| 类 | 说明 |
|---|---|
| `UChooserTable` | Chooser Table 资产，核心数据容器 |
| `UChooserSignature` | Chooser 的签名定义（结果类型、上下文数据） |
| `FChooserEvaluationContext` | 评估上下文，携带输入参数 |
| `FChooserIndexArray` | 索引数组，用于过滤过程中的行索引传递 |
| `FChooserPlayerSettings` | ChooserPlayer 的播放设置 |
| `UChooserFunctionLibrary` | 蓝图函数库，提供评估接口 |

## 调试支持

Chooser 内置了调试支持（`CHOOSER_DEBUGGING_ENABLED`）：
- 支持 Unreal Insights 追踪（`CHOOSER_TRACE_ENABLED`）
- 编辑器中可设置调试目标对象
- 可查看每列的测试值和过滤结果
- 支持高亮显示选中的行

---

# ProxyTable 模块文档

## 概述

ProxyTable 模块提供代理表功能，允许通过间接键查找资产，支持运行时替换。

## 核心概念

ProxyTable 将逻辑键映射到实际资产，使得：
- 可以在不修改 Chooser Table 的情况下替换底层资产
- 支持 DLC 和模组场景下的资产热替换
- 提供一层抽象，解耦选择逻辑和具体资产

## 使用方式

ProxyTable 作为 ObjectChooser 的一种实现，可以与 Chooser Table 配合使用。在 Chooser Table 的结果列中，可以选择使用 ProxyTable 查找而非直接引用资产。

---

# 编辑器模块文档

## ChooserEditor

ChooserEditor 模块提供 Chooser Table 的编辑器界面：
- 可视化表格编辑器
- 列类型配置面板
- 行数据编辑
- 调试测试功能
- 资产浏览器集成

## ProxyTableEditor

ProxyTableEditor 模块提供 ProxyTable 的编辑器界面：
- 键值对映射编辑
- 资产引用管理

## ChooserUncooked / ProxyTableUncooked

这些模块处理未打包（Uncooked）状态下的特殊逻辑，如：
- 资产预处理
- 编辑器专用数据的序列化
- Cook 时的数据优化