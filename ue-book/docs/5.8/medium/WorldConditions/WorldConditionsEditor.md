# World Conditions Editor

> General purpose cached conditions（照抄）

| 属性 | 值 |
|---|---|
| 中文名 | 世界条件编辑器 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器UI定制、类型细节自定义） |
| 模块 | `WorldConditions` (Runtime), `WorldConditionsEditor` (Editor), `WorldConditionsTestSuite` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-11-16 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WorldConditions) | |

## 用途

**WorldConditionsEditor** 模块是 **WorldConditions** 运行时插件的编辑器配套模块。它的核心用途是为游戏开发者（特别是策划和程序）提供在 Unreal Editor 属性面板中编辑和调试 **World Condition**（世界条件）的友好界面。

WorldConditions 系统本身用于定义和评估游戏世界中的状态或规则（例如：“敌人是否在视野内？”、“玩家生命值是否低于 30%？”、“当前时间是否是夜晚？”），这些条件常用于驱动AI行为树、任务系统或其他游戏逻辑。此编辑器模块将复杂的条件定义、表达式构建、Schema（架构/规则）关联等过程，通过直观的属性细节面板（Details Panel）UI 暴露出来，使得用户可以通过下拉菜单、按钮等控件来配置条件，而无需手动编辑复杂的JSON或结构体文本。它解决了直接编辑 FWorldConditionEditable 等结构体不直观、易出错的问题。

## 使用场景

- 你正在为游戏中的NPC或任务系统编写行为逻辑，并使用 **WorldConditions** 来定义复杂的触发规则 → 安装此插件后，在编辑器中配置这些条件会变得非常直观。
- 你需要为任务目标、AI状态转换或技能释放条件创建可复用、可配置的查询规则 → 通过编辑器UI，你可以方便地选择条件类型、组合逻辑运算符、关联上下文数据。
- 你在调试某个条件为何没有按预期触发 → 编辑器UI提供了清晰的当前配置视图，帮助排查问题。

## 蓝图用法

本模块（WorldConditionsEditor）主要为编辑器属性面板提供UI定制，不直接向游戏运行时或蓝图暴露通用的游戏性节点。与“世界条件”相关的运行时节点（如创建查询、检查状态等）位于 **WorldConditions** 运行时模块中。

### 核心节点

（本模块无公开的 BlueprintCallable 游戏性节点。其功能通过编辑器细节面板隐式体现。）

## C++ 用法

本模块的使用主要体现在如何为你的自定义 `UWorldConditionSchema` 或条件结构体注册编辑器定制。以下示例展示了如何关联。

### 头文件引入

```cpp
// 仅当需要直接访问模块接口时
#include "WorldConditionsEditorModule.h"
```

### 基本用法：为条件结构体注册类型定制

WorldConditionsEditor 模块为内置的 `FWorldConditionEditable` 和 `FWorldConditionContextDataRef` 等结构体提供了细节面板定制。如果你有自定义的结构体需要类似行为，可以参考其 `IPropertyTypeCustomization` 实现模式。

（注意：直接为内置类型注册定制通常由该模块自动完成，无需手动调用。此展示仅为说明其机制。）
```cpp
// 在编辑器模块启动时（例如你的自定义编辑器模块中），注册细节面板定制
// 来源: Private/Customizations/WorldConditionEditableDetails.h
void FMyEditorModule::StartupModule()
{
    FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");

    // 为 FWorldConditionEditable 注册自定义细节面板
    PropertyModule.RegisterCustomPropertyTypeLayout(
        FWorldConditionEditable::StaticStruct()->GetFName(),
        FOnGetPropertyTypeCustomizationInstance::CreateStatic(&FWorldConditionEditableDetails::MakeInstance)
        );

    // 为 FWorldConditionContextDataRef 注册自定义细节面板
    PropertyModule.RegisterCustomPropertyTypeLayout(
        FWorldConditionContextDataRef::StaticStruct()->GetFName(),
        FOnGetPropertyTypeCustomizationInstance::CreateStatic(&FWorldConditionContextDataRefDetails::MakeInstance)
        );
}
```

### 进阶用法：访问编辑器模块接口

可以通过模块接口进行交互，尽管当前接口定义非常简单。
```cpp
// 来源: Public/WorldConditionsEditorModule.h
#include "WorldConditionsEditorModule.h"

void SomeEditorFunction()
{
    if (IWorldConditionsEditorModule::IsAvailable())
    {
        // 获取模块单例，可用于未来可能的扩展API调用
        IWorldConditionsEditorModule& EditorModule = IWorldConditionsEditorModule::Get();
        // ... 目前接口无额外方法，但可进行模块存在性检查
    }
}
```

## Demo 示例

以下示例展示如何定义一个使用 WorldConditions 系统的核心运行时类型（Schema 和条件结构），这为编辑器UI（WorldConditionsEditor模块）提供了可编辑的对象。
```cpp
// MyGameTypes.h
#pragma once

#include "WorldConditions/WorldConditionSchema.h"
#include "WorldConditions/WorldConditionQuery.h"
#include "CoreMinimal.h"

// 1. 定义一个Schema，规定哪些类型的数据可以作为上下文，以及哪些条件类型可用
UCLASS()
class UMyTaskConditionSchema : public UWorldConditionSchema
{
    GENERATED_BODY()
public:
    // 构造函数中定义Schema规则
    UMyTaskConditionSchema()
    {
        // 添加允许的上下文数据类型
        AddContextDataStruct<APawn>(TEXT("PlayerPawn"));
        AddContextDataStruct<AActor>(TEXT("TargetActor"));
        
        // 添加可用的条件类型
        AddConditionStruct<FWorldCondition_IsVisible>(TEXT("IsVisible"));
        AddConditionStruct<FWorldCondition_HealthBelow>(TEXT("HealthBelow"));
    }
};

// 2. 定义一个具体的条件结构体
USTRUCT()
struct FWorldCondition_HealthBelow : public FWorldConditionBase
{
    GENERATED_BODY()

    // 评估条件的核心方法
    virtual bool Evaluate(const FWorldConditionContext& Context) const override
    {
        const AActor* Actor = Context.GetContextData<AActor>(TEXT("TargetActor"));
        if (!Actor) return false;
        
        // 简化的健康值检查逻辑
        // const UHealthComponent* HealthComp = Actor->FindComponentByClass<UHealthComponent>();
        // return HealthComp && HealthComp->GetHealthPercent() < Threshold;
        return true; // 示例占位
    }

    // 在编辑器中显示的阈值参数
    UPROPERTY(EditAnywhere, Category = "Condition")
    float Threshold = 0.3f;
};

// 3. 使用示例（通常在任务或AI组件中）
void AMyTask::EvaluateConditions()
{
    // 构建查询上下文
    FWorldConditionContext Context;
    Context.AddData(TEXT("PlayerPawn"), GetPlayerPawn());
    Context.AddData(TEXT("TargetActor"), Target);
    
    // 创建查询状态
    FWorldConditionQueryState QueryState;
    QueryState.SetSchema(UMyTaskConditionSchema::StaticClass());
    
    // 加载一个预定义的条件表达式（可在编辑器中编辑）
    QueryState.Load(/* 从资产或结构体加载条件定义 */);
    
    // 执行查询
    bool bConditionsMet = QueryState.Query(Context);
    
    if (bConditionsMet)
    {
        // 执行任务逻辑...
    }
}
```
**编译注意**：你需要在项目的 `Build.cs` 文件中添加对 `WorldConditions` 模块的依赖。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PropertyBindingUtils` | 用于支持属性绑定相关的UI工具，可能是提供编辑器中数据选择器的基础设施 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `cfaec1a0` | [WorldConditions] Build SharedDefinition before serialize so name harvest matches write | 修复序列化前构建共享定义，确保名称收集与写入一致 |
| 2026-04-23 | `f49c6ff0` | [WorldConditions][Stability] Do not dereference Owner during GC in FWorldConditionQueryState destruc | 提升稳定性，避免在垃圾回收期间在查询状态析构函数中解引用Owner |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏 UE_LOG 迁移至新式 UE_LOGF |
| 2026-03-24 | `2da4cdac` | [AI][WorldConditions] Add WorldConditionsToolset plugin for MCP inspection | 添加 WorldConditionsToolset 插件，用于支持 MCP（任务控制处理器）检查 |
| 2026-03-10 | `ba65d06d` | [WorldCondition] fixed case where world condition queries would not be properly linked when embedded | 修复了世界条件查询在嵌入时未能正确链接的问题 |

### 维护评价

**维护状态：活跃维护**。
- **创建时间**：约 3 年前（2022年11月），仍处于实验性阶段。
- **近期活动**：最近几个月有频繁且实质性的更新，包括稳定性修复（GC安全）、工具链改进（日志迁移、新增MCP检查工具）和核心逻辑修复（序列化、查询链接）。这表明该插件正在被积极开发和集成到更大的AI工具集中。
- **功能成熟度**：作为实验性功能，API可能会发生变化。最近的更新集中在底层稳定性和工具支持上，意味着核心功能正在趋于稳固。
- **推荐使用**：**适合早期采用和原型开发**。对于需要强大条件逻辑系统的项目（特别是AI密集型），可以引入使用，但需注意其实验性状态，并准备好跟随后续的API调整。由于持续活跃，问题发现和修复会比较及时。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WorldConditions)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WorldConditions/Source/WorldConditionsTestSuite)