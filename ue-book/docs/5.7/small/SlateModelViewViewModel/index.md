# Slate Model View Viewmodel

> Implementation of the Model View Viewmodel pattern for Slate

| 属性 | 值 |
|---|---|
| 中文名 | Slate MVVM |
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SlateMVVM` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-26 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SlateModelViewViewModel) | |

## 用途

该插件将 UMG 中成熟的 Model-View-ViewModel（MVVM）数据绑定模式引入到纯 Slate（非 UMG）环境中。它允许你在自定义 Slate 控件中通过声明式的绑定语法将视图（Widget）与视图模型（ViewModel）连接起来，并自动响应模型数据变化更新 UI。

在标准的 Slate 编程中，控件状态的更新需要手动监听回调并调用 `Invalidate` 等方法。此插件提供了一套轻量级的 `FViewModelBindings` 系统，支持基于字段通知（`INotifyFieldValueChanged`）的自动刷新，使 Slate 控件可以像 UMG 那样使用集合（ViewModel）来驱动呈现。

## 使用场景

- 你正在开发一个纯 Slate 编辑器工具或自定义控件（例如：图表面板、属性编辑器），希望用数据驱动 UI 更新。
- 你已经在 UMG 中使用了 MVVM 模式，现在需要将相同的 ViewModel 逻辑复用到 Slate 下。
- 你需要构建一个多源依赖的 Slate 控件，当多个 ViewModel 的属性变化时自动重绘。

由于是实验性插件，推荐在非生产环境或原型阶段使用。

## 蓝图用法

该插件目前**不提供**蓝图可调用节点。所有功能均通过 C++ 类 `UE::Slate::MVVM::FViewModelBindings` 暴露，仅适用于 C++ 开发。

## C++ 用法

### 头文件引入

```cpp
#include "SlateViewModelBindings.h"
```

### 基本用法

下例展示如何在自定义 Slate 控件中创建一个 ViewModel 绑定系统，监听一个字段变化并执行更新。

```cpp
// MyCustomWidget.cpp

#include "SlateViewModelBindings.h"
#include "INotifyFieldValueChanged.h"

class FMyViewModel : public UObject, public INotifyFieldValueChanged
{
    // 实现 INotifyFieldValueChanged，通常通过继承 UMVVMViewModelBase 或手动实现
    // ...
};

void UMySlateWidget::CreateBindings()
{
    using namespace UE::Slate::MVVM;

    // 1. 创建绑定系统
    FViewModelBindings Bindings;

    // 2. 注册一个 ViewModel 源，获取唯一 ID
    UObject* ViewModelInstance = ...; // 你的 ViewModel 对象
    FSourceInstanceId ViewModelId = FSourceInstanceId::Create(ViewModelInstance);

    // 3. 开始构建绑定
    FViewModelBindings::FBuilder Builder = Bindings.AddSource(ViewModelId);

    // 4. 定义字段 ID（通常是你 ViewModel 中声明的 FFieldNotification）
    UE::FieldNotification::FFieldId FieldId = FFieldNotification::Create("MyProperty");

    // 5. 添加绑定：当字段变化时执行自定义 Lambda
    Builder.AddBinding(FieldId, FSimpleDelegate::CreateLambda([this]()
    {
        // 更新 Slate 控件的内容
        Invalidate(EInvalidateWidgetReason::Paint);
    }));
}
```

> **来源**: [Engine/Plugins/Experimental/SlateModelViewViewModel/Source/SlateMVVM/Public/SlateViewModelBindings.h](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/SlateModelViewViewModel/Source/SlateMVVM/Public/SlateViewModelBindings.h)

### 进阶用法

当需要从多个 ViewModel 源中获取值以决定 UI 状态时，可以使用 `AddDependency` 建立依赖关系，并通过求值委托（`FEvaluateSourceDelegate`）拉取最新值。

```cpp
void UMyComplexWidget::CreateComplexBindings()
{
    using namespace UE::Slate::MVVM;

    FViewModelBindings Bindings;

    // 注册两个源
    UObject* ViewModelA = ...;
    UObject* ViewModelB = ...;
    FSourceInstanceId IdA = FSourceInstanceId::Create(ViewModelA);
    FSourceInstanceId IdB = FSourceInstanceId::Create(ViewModelB);

    // 添加源并获取 Builder
    FViewModelBindings::FBuilder BuilderA = Bindings.AddSource(IdA);

    // 添加依赖：当 IdA 的字段 "Status" 变化时，从 ViewModelB 中获取值并处理
    BuilderA.AddDependency(
        IdB,
        FFieldId("Status"),
        FViewModelBindings::FEvaluateSourceDelegate::CreateLambda([]() -> UObject*
        {
            // 返回应当被评估的源对象（可以是另一个 ViewModel 或中间计算对象）
            return ViewModelB;
        })
    );

    // 字段变化时的回调
    BuilderA.AddBinding(
        FFieldId("Status"),
        FSimpleDelegate::CreateLambda([this]()
        {
            // 重新计算 UI 状态
            Invalidate(EInvalidateWidgetReason::Layout);
        })
    );
}
```

利用 `FBuilder` 的链式调用可以一次性完成多个绑定和依赖设置。注意 `FViewModelBindings` 在当前线程生命周期内有效，通常在 `SWidget::Construct` 或控件的初始化函数中创建并持有。

## Demo 示例

以下是一个可编译的最小 Slate 控件，展示了如何使用 `FViewModelBindings` 在其 `Construct` 中设置绑定。假设你已有一个实现了 `INotifyFieldValueChanged` 的 ViewModel 类。

### MyViewModel.h

```cpp
#pragma once

#include "UObject/Object.h"
#include "INotifyFieldValueChanged.h"
#include "FieldNotificationId.h"
#include "MyViewModel.generated.h"

UCLASS(BlueprintType)
class UMyViewModel : public UObject, public INotifyFieldValueChanged
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ViewModel")
    int32 Counter;

    // 用于通知字段变化
    void SetCounter(int32 NewCounter)
    {
        if (Counter != NewCounter)
        {
            Counter = NewCounter;
            UE::FieldNotification::FFieldId FieldId = UE::FieldNotification::FFieldId::Create("Counter");
            BroadcastFieldValueChanged(FieldId);
        }
    }
};
```

### MySlateWidget.h

```cpp
#pragma once

#include "Widgets/SCompoundWidget.h"
#include "SlateViewModelBindings.h"

class SMySlateWidget : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMySlateWidget) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    UE::Slate::MVVM::FViewModelBindings ViewModelBindings;
    TStrongObjectPtr<UMyViewModel> ViewModel;
};
```

### MySlateWidget.cpp

```cpp
#include "MySlateWidget.h"
#include "MyViewModel.h"
#include "SlateCore/Widgets/Images/SImage.h"
#include "SlateCore/Widgets/Text/STextBlock.h"
#include "SlateCore/Widgets/Layout/SBorder.h"

void SMySlateWidget::Construct(const FArguments& InArgs)
{
    // 创建 ViewModel
    ViewModel = TStrongObjectPtr<UMyViewModel>(NewObject<UMyViewModel>());

    // 构建 Slate 控件树
    ChildSlot
    [
        SNew(SBorder)
        .BorderImage(FCoreStyle::Get().GetBrush("WhiteTexture"))
        .Content()
        [
            SNew(STextBlock)
            .Text_Raw(this, &SMySlateWidget::GetCurrentText)
        ]
    ];

    // 设置 MVVM 绑定
    using namespace UE::Slate::MVVM;
    FSourceInstanceId ViewModelId = FSourceInstanceId::Create(ViewModel.Get());
    FViewModelBindings::FBuilder Builder = ViewModelBindings.AddSource(ViewModelId);
    Builder.AddBinding(
        UE::FieldNotification::FFieldId::Create("Counter"),
        FSimpleDelegate::CreateLambda([this]()
        {
            Invalidate(EInvalidateWidgetReason::Paint);
        })
    );
}

FText SMySlateWidget::GetCurrentText() const
{
    if (ViewModel.IsValid())
    {
        return FText::AsNumber(ViewModel->Counter);
    }
    return FText::GetEmpty();
}
```

使用时，在某个地方调用 `ViewModel->SetCounter(42)` ，Slate 控件会自动刷新显示。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `FieldNotification` | 提供字段通知机制 (`FFieldId`, `INotifyFieldValueChanged`) |

无其他特殊依赖（标准 Core/Engine/Slate 等已隐含）。

## 维护状态

### 近期更新

- 2024-01-26 `025d4fa3` 添加实验性插件以在 Slate 中使用 MVVM，方式与 UMG 中的 MVVM 相同（初始提交）。

### 维护评价

该插件创建于 2024 年 1 月，目前仅有一个提交，处于**实验性早期阶段**。由于没有任何后续更新，尚不清楚 Epic 是否会继续维护或将其纳入稳定。已知限制：缺少蓝图支持，无官方示例文档，且 API 可能在未来版本变更。如果你需要稳定的 Slate 数据绑定方案，建议等待官方进一步迭代或考虑其他成熟实现（如基于 Delegate 的手动绑定）。

**推荐谨慎使用**，适合在非关键原型或评估项目中探索。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SlateModelViewViewModel)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/model-view-viewmodel-in-unreal-engine/)（UMG MVVM 文档，Slate MVVM 尚无独立文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SlateModelViewViewModel/Source/SlateMVVM)（目前无测试用例）