# WidgetAutomationTests

> 无描述（.uplugin Description 为空）

| 属性 | 值 |
|---|---|
| 分类 | Testing |
| 默认启用 | false |
| 包含内容 | true |
| 模块 | WidgetAutomationTests (Editor) |
| 创建时间 | 2023-03-30 |
| 年龄标签 | 🆕（~3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/WidgetAutomationTests) | |

## 用途

WidgetAutomationTests 是 Epic 为 Slate/UMG Widget 提供的**自动化测试框架**，用于验证 Widget 属性变更后是否正确触发了失效（Invalidation）、重绘（OnPaint）和重布局（ComputeDesiredSize）。

它解决的核心问题是：当开发者修改一个 Slate Widget 的某个属性（如颜色、文字、对齐方式）时，如何自动验证该属性变更确实导致了正确的视觉更新？传统做法需要人眼检查，而本框架通过 Mock Widget + JSON 基线文件实现了自动化回归测试。

框架的设计思路：
1. 用 `SWidgetMock<T>` 包装被测 Widget，拦截 `OnPaint`、`ComputeDesiredSize`、焦点回调等关键函数的调用
2. 首次运行时将实际渲染参数写入 JSON 基线文件
3. 后续运行时对比实际参数与 JSON 基线，验证一致性
4. 通过 `FSlateTestBase<T>` 提供 Setup → Run → Validate → TearDown 的标准测试生命周期

## 使用场景

- 你正在开发自定义 Slate Widget，需要确保属性变更正确触发重绘 → 用本框架编写自动化测试
- 你在修改引擎内置 Widget（如 STextBlock、SButton）的行为，需要回归测试 → 继承 `FSlateTestBase<T>` 编写测试
- 你需要验证 Widget 的焦点系统回调（OnFocusReceived/OnFocusLost/OnFocusChanging）是否按预期触发 → 使用 FocusTest 模式

## 蓝图用法

本插件**不提供任何蓝图接口**。它是一个纯 C++ 的编辑器测试框架，所有代码均在 `#if WITH_DEV_AUTOMATION_TESTS` 条件编译保护下，仅在开发构建中可用。

## C++ 用法

### 头文件引入

```cpp
#include "SlateTestBase.h"
#include "SWidgetMock.h"
#include "SlateTestHelper.h"
```

### 核心类关系

```
FSlateTestBase<T>          ← 你的测试继承这个（T 必须是 SWidget 子类）
  ├── SWidgetMock<T>       ← 自动创建的 Mock Widget，拦截函数调用
  │     ├── T              ← 被测的真实 Widget 类型
  │     └── FWidgetMockNonTemplate  ← 函数调用计数、JSON 数据验证
  └── SWindow              ← 自动创建的测试窗口
```

### 基本用法：编写属性变更测试

参考 `STextBlockTest.cpp` 的模式，测试一个 Widget 属性变更是否正确触发重绘：

```cpp
// 1. 定义测试类，继承 FSlateTestBase<被测Widget类型>
class FSlateTestMyWidget : public FSlateTestBase<SMyWidget>
{
public:
    FSlateTestMyWidget(FString InTestName)
        : FSlateTestBase<SMyWidget>(MoveTemp(InTestName)) {}

    // Setup: 创建布局、初始化 Widget、加载 JSON 基线
    void Setup(FAutomationTestBase* TestObj) override
    {
        // 将被测 Widget 添加到窗口
        TSharedRef<SVerticalBox> Panel = SNew(SVerticalBox);
        Panel->AddSlot()[GetSubjectWidget()];
        GetMainWindow()->SetContent(Panel);

        // 初始化属性
        GetSubjectWidget()->SetSomeProperty(InitialValue);

        // 启用快速更新（Global Invalidation 所需）
        GetMainWindow()->SetAllowFastUpdate(true);

        // 下一帧清除副作用并加载 JSON 基线
        TestObj->AddCommand(new FDelayedFunctionLatentCommand(
            [this, TestObj]()
            {
                GetSubjectWidget()->ClearFunctionRecords();
                GetSubjectWidget()->FindOrCreateTestJSONFile(GetTestName());
            }, 0.1f));
    }

    // Run: 修改被测属性
    void Run(FAutomationTestBase* TestObj) override
    {
        GetSubjectWidget()->SetSomeProperty(NewValue);
    }

    // Validate: 验证属性已设置、回调被触发、JSON 基线匹配
    void Validate(FAutomationTestBase* TestObj) override
    {
        if (!JSONValidation(TestObj, "SomeProperty"))
            return;

        // 通用验证：getter 返回正确值 + OnPaint/ComputeDesiredSize 被调用
        ValidatePropertyChange<FSomeType>(
            TestObj,
            &SMyWidget::GetSomeProperty,
            "SomeProperty",
            NewValue,
            EInvalidateWidgetReason::Paint | EInvalidateWidgetReason::Layout);
    }

    // TearDown: 写入 JSON 基线文件、销毁窗口
    void TearDown(FAutomationTestBase* TestObj) override
    {
        if (GetSubjectWidget()->GetTestJSONObjectToWrite().IsValid())
        {
            FSlateTestHelper::WriteJSONToTxt(
                GetSubjectWidget()->GetTestJSONObjectToWrite().ToSharedRef(),
                GetTestName());
        }
        FSlateApplication::Get().RequestDestroyWindow(GetMainWindow());
    }
};

// 2. 注册自动化测试
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FMyWidgetTest,
    "Slate.MyWidgetTest",
    EAutomationTestFlags_ApplicationContextMask | EAutomationTestFlags::EngineFilter)

// 3. 实现 RunTest
bool FMyWidgetTest::RunTest(const FString& Parameters)
{
    auto MyTest = MakeShared<FSlateTestMyWidget>(TEXT("SlateTestMyWidget_SomeProperty"));

    MyTest->Setup(this);

    AddCommand(new FDelayedFunctionLatentCommand([this, MyTest]()
    {
        MyTest->Run(this);
        MyTest->Validate(this);

        this->AddCommand(new FDelayedFunctionLatentCommand([this, MyTest]()
        {
            MyTest->TearDown(this);
        }, 0.1f));
    }, 0.1f));

    return true;
}
```

### 进阶用法：测试焦点系统

参考 `FocusTest.cpp`，测试焦点转移时回调的触发顺序：

```cpp
template<class T>
class FSlateTestFocus : public FSlateTestBase<T>
{
    TSharedPtr<SWidgetMock<T>> SiblingWidget;
    TSharedPtr<SWidgetMock<SVerticalBox>> PanelWidget;

    void Setup(FAutomationTestBase* TestObj) override
    {
        // 创建两个同类型 Widget：SubjectWidget 和 SiblingWidget
        PanelWidget = SNew(SWidgetMock<SVerticalBox>);
        SiblingWidget = CreateWidget();

        PanelWidget->AddSlot()[GetSubjectWidget()];
        PanelWidget->AddSlot()[SiblingWidget.ToSharedRef()];
        GetMainWindow()->SetContent(PanelWidget.ToSharedRef());

        // 初始焦点在 SiblingWidget 上
        FSlateApplication::Get().SetUserFocus(0, SiblingWidget);

        GetSubjectWidget()->ClearFunctionRecords();
        SiblingWidget->ClearFunctionRecords();
    }

    void Run(FAutomationTestBase* TestObj) override
    {
        // 将焦点转移到 SubjectWidget
        FSlateApplication::Get().SetUserFocus(0, GetSubjectWidget());
    }

    void Validate(FAutomationTestBase* TestObj) override
    {
        // 验证 SubjectWidget 收到了 OnFocusReceived 和 OnFocusChanging
        TestObj->AddErrorIfFalse(
            GetSubjectWidget()->GetValueInFunctionCalls(FTestFunctionNames::NAME_OnFocusReceived) == 1,
            TEXT("OnFocusReceived was not called on the widget receiving focus."));
        TestObj->AddErrorIfFalse(
            GetSubjectWidget()->GetValueInFunctionCalls(FTestFunctionNames::NAME_OnFocusChanging) == 1,
            TEXT("OnFocusChanging was not called on the widget receiving focus."));

        // 验证 SiblingWidget 收到了 OnFocusLost 和 OnFocusChanging
        TestObj->AddErrorIfFalse(
            SiblingWidget->GetValueInFunctionCalls(FTestFunctionNames::NAME_OnFocusLost) == 1,
            TEXT("OnFocusLost was not called on the widget losing focus."));

        // 验证不会出现错误的回调
        TestObj->AddErrorIfFalse(
            GetSubjectWidget()->GetValueInFunctionCalls(FTestFunctionNames::NAME_OnFocusLost) == 0,
            TEXT("OnFocusLost should not be called on the widget receiving focus."));
    }

    void TearDown(FAutomationTestBase* TestObj) override
    {
        FSlateApplication::Get().RequestDestroyWindow(GetMainWindow());
    }
};
```

### 关键 API 速查

#### FSlateTestBase\<T\>

| 方法 | 说明 |
|---|---|
| `GetSubjectWidget()` | 获取被测 Mock Widget（`TSharedRef<SWidgetMock<T>>`） |
| `GetMainWindow()` | 获取测试窗口（`TSharedRef<SWindow>`） |
| `CreateWidget()` | 创建新的同类型 Mock Widget（用于多 Widget 测试） |
| `ValidatePropertyChange<T>(...)` | 通用属性变更验证：检查 getter + 失效回调 + JSON 基线 |
| `JSONValidation(TestObj, PropertyName)` | 检查 JSON 基线文件是否加载成功 |

#### SWidgetMock\<T\>（继承自 FWidgetMockNonTemplate）

| 方法 | 说明 |
|---|---|
| `ClearFunctionRecords()` | 清除所有函数调用计数和数据验证记录 |
| `FindOrCreateTestJSONFile(TestName)` | 加载或创建 JSON 基线文件 |
| `GetValueInFunctionCalls(FuncName)` | 获取某函数被调用的次数 |
| `GetValueInDataValidations(FuncName)` | 获取某函数的数据验证结果（bool） |
| `GetTestJSONObject()` | 获取已加载的 JSON 基线对象 |
| `GetTestJSONObjectToWrite()` | 获取待写入的 JSON 对象（首次运行时有值） |

#### FSlateTestHelper

| 方法 | 说明 |
|---|---|
| `WriteJSONToTxt(JsonObj, TestName)` | 将 JSON 对象写入基线文件 |
| `LoadJSONFromTxt(TestName)` | 从基线文件加载 JSON 对象 |
| `GetFullPath(TestName)` | 获取基线文件的完整路径 |

#### 内置函数名常量（FTestFunctionNames）

| 常量 | 对应函数 |
|---|---|
| `NAME_OnPaint` | `SWidget::OnPaint` |
| `NAME_ComputeDesiredSize` | `SWidget::ComputeDesiredSize` |
| `NAME_OnFocusReceived` | `SWidget::OnFocusReceived` |
| `NAME_OnFocusLost` | `SWidget::OnFocusLost` |
| `NAME_OnFocusChanging` | `SWidget::OnFocusChanging` |

## Demo 示例

一个完整的最小测试示例，验证 STextBlock 的 ColorAndOpacity 属性变更（来自 `STextBlockTest.cpp`）：

**Build.cs 依赖**：
```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core", "CoreUObject", "Slate", "SlateCore", "Json"
});
```

**STextBlockColorTest.cpp**：
```cpp
#include "CoreMinimal.h"
#include "Misc/AutomationTest.h"
#include "SlateTestBase.h"
#include "SWidgetMock.h"
#include "Widgets/Text/STextBlock.h"
#include "Widgets/SWindow.h"
#include "Framework/Application/SlateApplication.h"

#if WITH_DEV_AUTOMATION_TESTS

namespace UE::SlateWidgetAutomationTest
{

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FTextBlockColorTest,
    "Slate.STextBlockColorTest",
    EAutomationTestFlags_ApplicationContextMask | EAutomationTestFlags::EngineFilter)

class FSlateTestTextBlockColor : public FSlateTestBase<STextBlock>
{
public:
    FSlateTestTextBlockColor(FString InTestName)
        : FSlateTestBase<STextBlock>(MoveTemp(InTestName)) {}

    void Setup(FAutomationTestBase* TestObj) override
    {
        TSharedRef<SVerticalBox> VerticalBox = SNew(SVerticalBox);
        VerticalBox->AddSlot()[GetSubjectWidget()];
        GetMainWindow()->SetContent(VerticalBox);

        GetSubjectWidget()->SetText(FText::FromString(TEXT("Hello")));
        GetMainWindow()->SetAllowFastUpdate(true);

        TestObj->AddCommand(new FDelayedFunctionLatentCommand([this, TestObj]()
        {
            GetSubjectWidget()->ClearFunctionRecords();
            GetSubjectWidget()->FindOrCreateTestJSONFile(GetTestName());
        }, 0.1f));
    }

    void Run(FAutomationTestBase* TestObj) override
    {
        GetSubjectWidget()->SetColorAndOpacity(
            FSlateColor(FLinearColor(0.5f, 0.4f, 0.3f, 0.9f)));
    }

    void Validate(FAutomationTestBase* TestObj) override
    {
        if (!JSONValidation(TestObj, "ColorAndOpacity")) return;

        ValidatePropertyChange<FSlateColor>(
            TestObj,
            &STextBlock::GetColorAndOpacity,
            "ColorAndOpacity",
            FSlateColor(FLinearColor(0.5f, 0.4f, 0.3f, 0.9f)),
            EInvalidateWidgetReason::Layout | EInvalidateWidgetReason::Paint);
    }

    void TearDown(FAutomationTestBase* TestObj) override
    {
        if (GetSubjectWidget()->GetTestJSONObjectToWrite().IsValid())
        {
            FSlateTestHelper::WriteJSONToTxt(
                GetSubjectWidget()->GetTestJSONObjectToWrite().ToSharedRef(),
                GetTestName());
        }
        FSlateApplication::Get().RequestDestroyWindow(GetMainWindow());
    }
};

bool FTextBlockColorTest::RunTest(const FString& Parameters)
{
    auto MyTest = MakeShared<FSlateTestTextBlockColor>(
        TEXT("SlateTestTextBlock_ColorAndOpacity"));

    MyTest->Setup(this);

    AddCommand(new FDelayedFunctionLatentCommand([this, MyTest]()
    {
        MyTest->Run(this);
        MyTest->Validate(this);

        this->AddCommand(new FDelayedFunctionLatentCommand([this, MyTest]()
        {
            MyTest->TearDown(this);
        }, 0.1f));
    }, 0.1f));

    return true;
}

} // namespace
#endif
```

运行测试：编辑器中打开 **Session Frontend → Automation**，搜索 `Slate.STextBlockColorTest` 并执行。

### JSON 基线文件

首次运行时，框架会在 `Engine/Plugins/Tests/WidgetAutomationTests/Resources/TestBaselineFiles/` 下自动创建 JSON 文件（如 `UIAutomation_SlateTestTextBlock_ColorAndOpacity.json`），记录渲染参数作为基线。后续运行时对比实际输出与基线是否一致。

## 模块依赖

从 Build.cs 的 `PublicDependencyModuleNames` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、FString、TMap 等 |
| `CoreUObject` | UObject 系统 |
| `EditorTests` | 编辑器自动化测试基础设施（`IMPLEMENT_SIMPLE_AUTOMATION_TEST` 等） |
| `Engine` | 引擎核心 |
| `Slate` | Slate UI 框架（SWidget、SWindow 等） |
| `SlateCore` | Slate 核心类型（FGeometry、FWidgetStyle 等） |
| `Json` | JSON 读写（FJsonObject、FJsonReader） |
| `UnrealEd` | 编辑器功能 |
| `UMG` | UMG Widget 系统 |
| `UMGEditor` | UMG 编辑器支持 |

插件依赖：`EditorTests`（在 .uplugin 中声明）

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2024-09-23 | `3ac6607290a9` | fix lots of FString::Printf format errors | 批量修复格式化字符串错误，编译兼容性维护 |
| 2024-06-12 | `e521f5d700f0` | Replaced EAutomationTestFlags::ApplicationContextMask with EAutomationTestFlags_ApplicationContextMask | API 重命名适配，跟随引擎 API 变更 |
| 2023-10-12 | `ffb133e799d3` | Update FJsonObject to use TCHAR strings instead of ANSI strings | 适配 FJsonObject 的 TCHAR 迁移 |

### 维护评价

- **创建时间**：2023-03-30，约 3 年前
- **更新频率**：最近一次更新在 2024-09-23，约 8 个月前；但三次更新均为编译/API 适配修复，无功能性更新
- **实验性标记**：`.uplugin` 中 `IsExperimentalVersion: true`、`EnabledByDefault: false`
- **现状**：框架本身稳定但处于实验阶段，Epic 尚未将其标记为正式功能。测试覆盖范围有限（目前仅有 STextBlock 属性测试和 SButton 焦点测试两个用例）
- **限制**：JSON 基线验证目前仅支持 `ET_ShapedText` 元素类型，其他绘制元素类型尚在 TODO 中
- **推荐**：适用于需要为自定义 Slate Widget 编写自动化测试的场景，但需注意其实验性状态

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/WidgetAutomationTests)
- 测试用例：
  - [STextBlockTest.cpp](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Tests/WidgetAutomationTests/Source/WidgetAutomationTests/Private/STextBlockTest.cpp)
  - [FocusTest.cpp](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Tests/WidgetAutomationTests/Source/WidgetAutomationTests/Private/FocusTest.cpp)
