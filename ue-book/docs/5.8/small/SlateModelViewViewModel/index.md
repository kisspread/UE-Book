# Slate Model View Viewmodel

> Implementation of the Model View Viewmodel pattern for Slate

| 属性 | 值 |
|---|---|
| 中文名 | Slate视图模型绑定 |
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SlateMVVM` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-26 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SlateModelViewViewModel) | |

## 用途

该插件为 **Slate**（UE 的底层 UI 框架）提供了一套实现**模型-视图-视图模型（MVVM）** 数据绑定的基础设施。其核心目标是将 Slate UI 控件（视图）与业务逻辑和数据状态（模型/视图模型）解耦，类似于 UMG（可视化 UI）中现有的 MVVM 功能，但专门针对纯 C++ 的 Slate 用户。

它允许开发者将实现了 `INotifyFieldValueChanged` 接口的对象（通常是视图模型）注册为数据源，并将特定的字段更改事件（`FFieldId`）与 Slate 控件或逻辑函数进行绑定。当数据源中的字段值发生变化时，预设的绑定逻辑（如更新文本、颜色）会自动执行，从而避免了手动轮询或冗长的回调代码，简化了 Slate UI 的状态管理。

## 使用场景

-   你正在使用 **Slate** 构建复杂的编辑器工具、自定义资产编辑器或 Unreal Editor 的扩展，并希望管理大量随数据变化而动态更新的 UI 状态。
-   你已经在使用 UMG 的 MVVM 模式，现在需要将类似的数据绑定逻辑应用到纯 Slate 的组件中，以保持架构一致性。
-   你需要一种声明式、可维护的方式来连接数据层与 Slate 视图层，减少 `SNew()` 和 `SAssignNew()` 宏中手动设置属性和委托的样板代码。

## 蓝图用法

该插件主要面向 C++ 开发者，提供的核心类 `FViewModelBindings` 是纯 C++ API，**不包含任何暴露给蓝图（BlueprintCallable/BlueprintReadWrite）的函数**。在 Slate 中进行数据绑定的逻辑应通过 C++ 代码实现。

## C++ 用法

### 头文件引入

```cpp
#include "SlateViewModelBindings.h"
```
命名空间： `UE::Slate::MVVM`

### 基本用法

核心类是 `FViewModelBindings`。你需要创建一个它的实例来管理你的绑定和源。
**绑定流程**：
1.  创建一个 `FViewModelBindings` 实例。
2.  向其中添加实现了 `INotifyFieldValueChanged` 接口的对象作为**数据源**。
3.  将数据源的特定字段（`FFieldId`）与一个委托进行绑定。当该字段值变化时，委托将被调用。
4.  （可选）定义源之间的**依赖关系**，当一个源变化时，自动触发依赖于它的其他源进行更新。

```cpp
// 假设你有一个视图模型类
UCLASS()
class UMyViewModel : public UObject, public INotifyFieldValueChanged
{
    GENERATED_BODY()
public:
    // 定义一个可通知的字段
    UPROPERTY(BlueprintReadWrite, FieldNotify)
    FString UserName;

    // ... 实现 INotifyFieldValueChanged 接口 ...
};

// 在你的 Slate Widget 或拥有管理职责的类中
class SMyWidget : public SCompoundWidget
{
    // ...
    UE::Slate::MVVM::FViewModelBindings ViewModelBindings;
    TScriptInterface<INotifyFieldValueChanged> MyViewModelInstance;

    void Construct(const FArguments& InArgs)
    {
        // 1. 初始化视图模型实例
        MyViewModelInstance = NewObject<UMyViewModel>();

        // 2. 添加数据源，并获取一个标识符 (SourceId)
        auto SourceBuilder = ViewModelBindings.AddSource(MyViewModelInstance);
        auto SourceId = SourceBuilder.GetId();

        // 3. 绑定字段变化事件
        // 当 UserName 字段变化时，执行一个 Lambda 来更新 UI
        SourceBuilder.AddBinding(
            UMyViewModel::FFieldNotificationClassDescriptor::UserName,
            FSimpleDelegate::CreateLambda([this]()
            {
                // 更新 Slate TextBlock 的文本
                if (NameTextBlock.IsValid())
                {
                    NameTextBlock->SetText(FText::FromString(Cast<UMyViewModel>(MyViewModelInstance.Get())->UserName));
                }
            })
        );

        // 4. 将构建好的绑定存储起来（SourceBuilder 生命周期结束）

        // ... 构建 Slate 树 ...
        ChildSlot
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("初始文本")))
            // 初始文本应通过其他方式设置，或在绑定执行后更新
        ];
    }
};
```

### 进阶用法

**源之间的依赖关系**：你可以定义一个源依赖于另一个源的变化。当被依赖的源发生变化时，依赖源的绑定会自动执行。
这在视图模型依赖另一个服务或模型的状态时非常有用。

```cpp
// 假设有两个数据源：一个模型 (Model) 和一个视图模型 (ViewModel)
// ViewModel 的显示内容依赖于 Model 的数据

TScriptInterface<INotifyFieldValueChanged> ModelSource;
TScriptInterface<INotifyFieldValueChanged> ViewModelSource;

auto ModelSourceBuilder = ViewModelBindings.AddSource(ModelSource);
auto ModelSourceId = ModelSourceBuilder.GetId();

auto ViewModelSourceBuilder = ViewModelBindings.AddSource(ViewModelSource);
auto ViewModelSourceId = ViewModelSourceBuilder.GetId();

// 绑定 ViewModel 自身字段的变化
ViewModelSourceBuilder.AddBinding(
    /* Some FieldId */,
    FSimpleDelegate::CreateSP(this, &SMyWidget::OnViewModelFieldChanged)
);

// 设置依赖：当 ModelSource 的某个字段变化时，重新评估 ViewModelSource。
// EvaluateDelegate 用于从 Model 获取最新数据并更新 ViewModel。
ViewModelSourceBuilder.AddDependency(
    ModelSourceId,
    UMyModel::FFieldNotificationClassDescriptor::SomeDataField, // 当 Model 的此字段变化时
    UE::Slate::MVVM::FViewModelBindings::FEvaluateSourceDelegate::CreateLambda(
        [ViewModelSource, ModelSource]() -> UObject*
        {
            // 在此 Lambda 中，根据最新的 Model 数据更新 ViewModel 的属性。
            auto* Model = Cast<UMyModel>(ModelSource.Get());
            auto* VM = Cast<UMyViewModel>(ViewModelSource.Get());
            if (Model && VM)
            {
                VM->UpdateFromModel(Model); // 假设的更新函数
            }
            return ViewModelSource.Get(); // 返回需要被评估的源
        }
    )
);
```

## Demo 示例

以下是一个最小化示例，展示如何在 Slate Widget 中使用 `FViewModelBindings` 来自动更新一个文本块。

**MyViewModel.h**
```cpp
#pragma once

#include "UObject/Interface.h"
#include "FieldNotification/FieldNotificationDeclaration.h"
#include "MyViewModel.generated.h"

UINTERFACE()
class UMyViewModel : public UInterface
{
    GENERATED_BODY()
};

class IMyViewModel
{
    GENERATED_BODY()
public:
    // 声明一个可通知的字段
    UPROPERTY(BlueprintReadWrite, FieldNotify)
    FString UserMessage;
};

// 一个简单的实现类
UCLASS()
class UMyViewModelImpl : public UObject, public IMyViewModel
{
    GENERATED_BODY()
public:
    // 确保字段通知宏正确展开（通常在.cpp中使用实现宏，此处简化）
    FFieldNotificationId GetUserMessageFieldId() const { return GET_MEMBER_NAME_CHECKED(UMyViewModelImpl, UserMessage); }
};
```

**SMyWidget.h**
```cpp
#pragma once

#include "Widgets/SCompoundWidget.h"
#include "SlateViewModelBindings.h"

class SMyWidget : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyWidget) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    void OnUserMessageChanged();

    TSharedPtr<STextBlock> MessageTextBlock;
    UE::Slate::MVVM::FViewModelBindings ViewModelBindings;
    TScriptInterface<INotifyFieldValueChanged> MyViewModel;
};
```

**SMyWidget.cpp**
```cpp
#include "SMyWidget.h"
#include "MyViewModel.h"

void SMyWidget::Construct(const FArguments& InArgs)
{
    // 创建视图模型实例
    MyViewModel = NewObject<UMyViewModelImpl>();

    // 添加到绑定系统
    auto SourceBuilder = ViewModelBindings.AddSource(MyViewModel);

    // 绑定 UserMessage 字段的变化到一个成员函数
    SourceBuilder.AddBinding(
        UMyViewModelImpl::FFieldNotificationClassDescriptor::UserMessage,
        FSimpleDelegate::CreateSP(this, &SMyWidget::OnUserMessageChanged)
    );

    // 构建 Slate 树
    ChildSlot
    [
        SNew(STextBlock)
        .Text(FText::FromString(TEXT("等待数据...")))
        .Text_Lambda([this]() -> FText
        {
            // 初始文本，也可以在 OnUserMessageChanged 中设置
            if (MyViewModel)
            {
                return FText::FromString(Cast<IMyViewModel>(MyViewModel.Get())->UserMessage);
            }
            return FText::GetEmpty();
        })
    ];
    // 注意：在实际使用中，可能需要立即执行一次绑定以设置初始文本。
    // ViewModelBindings.Execute(); // 可根据需要调用
}

void SMyWidget::OnUserMessageChanged()
{
    // 当视图模型的 UserMessage 字段改变时，此函数被调用
    if (MessageTextBlock.IsValid() && MyViewModel)
    {
        const FString& NewMsg = Cast<IMyViewModel>(MyViewModel.Get())->UserMessage;
        MessageTextBlock->SetText(FText::FromString(NewMsg));
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。该插件的模块 `SlateMVVM` 依赖于引擎的核心模块，如 `FieldNotification`、`Slate` 和 `SlateCore`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-01-26 | `025d4fa3` | Add experimental plugin to use MVVM in Slate the same way it is used in UMG. #rb editor-ui-systems [CL 30932073 by patrick boutot in ue5-main branch] | 初始提交，添加实验性插件，为 Slate 实现与 UMG 类似的 MVVM 模式。 |

### 维护评价

**创建时间**：该插件于 2024 年初创建，属于较新的实验性功能。

**最近更新**：整个插件仅有一次初始提交记录（2024-01-26）。自创建以来，在主分支上**没有后续的功能更新或错误修复**记录。

**活跃度**：**不活跃**。作为“Experimental”插件，它可能处于设计验证阶段。缺乏持续更新表明其 API 和功能可能尚未稳定，也未被 Epic 官方广泛采用或推广。

**已知问题或限制**：
1.  **实验性**：官方明确标记为实验性，API 未来可能会有较大改动。
2.  **无蓝图支持**：纯 C++ API，对需要蓝图可视化脚本的用户不友好。
3.  **文档与示例缺失**：除初始提交说明外，没有官方文档或示例项目，上手难度较高。

**推荐使用**：
*   **不推荐在生产环境或关键项目中直接使用**。
*   可作为**学习参考**或**概念验证**，了解如何在 Slate 中构建数据绑定系统。
*   如果你在开发内部工具或原型，并愿意承担 API 变化的风险，可以谨慎试用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SlateModelViewViewModel)
-   [官方文档]( ) （无）
-   [测试用例]( ) （在提供的信息中未发现独立的测试文件）