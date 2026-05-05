# Automation Driver Tests

> AutomationDriver 框架的官方集成测试套件，用于验证 UI 自动化驱动器的各项功能。

| 属性 | 值 |
|---|---|
| 分类 | Testing |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 是 |
| 模块 | AutomationDriverTests (UncookedOnly) |
| 创建时间 | 2020-11-09 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/AutomationDriverTests) | |

## 用途

这个 plugin 是 [AutomationDriver](../AutomationDriverTests/../../AutomationDriver/) 框架的**集成测试**。它不是提供给开发者使用的功能库，而是验证 AutomationDriver 的元素定位、交互操作、序列执行等核心能力是否正确工作的测试套件。

测试内容涵盖：
- 通过 `By::Id` 和 `By::Path` 定位 Slate Widget
- `By::TextFilter::Equals` 和 `By::TextFilter::Contains` 文本过滤定位
- 鼠标交互：Hover、Click、DoubleClick
- 键盘交互：Type、Press、Release、TypeChord、Focus
- 滚动操作：ScrollBy、ScrollToBeginning、ScrollToEnd 及其 Until 变体
- 元素状态查询：Exists、IsVisible、IsInteractable、IsFocused、CanFocus、IsHovered、GetText、GetAbsolutePosition、GetSize
- 动作序列（Sequence）：组合多个操作、跨窗口操作、Wait 等待条件

## 使用场景

- 你正在**开发或调试 AutomationDriver 框架本身** → 启用此 plugin 运行测试
- 你想**学习 AutomationDriver 的 API 用法** → 阅读此 plugin 的测试代码作为参考示例
- 你在**编写基于 AutomationDriver 的 UI 自动化测试** → 参考测试中的模式编写自己的测试

## 蓝图用法

此 plugin 无公开的蓝图接口。它是一个纯测试模块，不暴露 `BlueprintCallable` 函数。

## C++ 用法

### 如何启用

此 plugin 默认禁用。在 Editor 的 **Edit → Plugins** 中搜索 "Automation Driver Tests" 并启用，或在 `.uproject` 中添加：

```json
{
    "Plugins": [
        {
            "Name": "AutomationDriverTests",
            "Enabled": true
        }
    ]
}
```

### 头文件引入

```cpp
#include "Misc/AutomationTest.h"
#include "IAutomationDriver.h"
#include "IAutomationDriverModule.h"
#include "IDriverElement.h"
#include "IDriverSequence.h"
#include "LocateBy.h"
#include "DriverConfiguration.h"
```

### 基本用法 — 元素定位

```cpp
// 启用 AutomationDriver 模块
IAutomationDriverModule::Get().Enable();

// 创建 Driver 实例
FAutomationDriverPtr Driver = IAutomationDriverModule::Get().CreateDriver();

// 按 Id 定位（通过 FDriverMetaData::Id 设置）
FDriverElementRef Element = Driver->FindElement(By::Id("MyButton"));
bool bExists = Element->Exists();

// 按 Path 定位（支持 Tag、Id、Type 及层级组合）
FDriverElementRef ByTag = Driver->FindElement(By::Path("Keyboard"));
FDriverElementRef ById = Driver->FindElement(By::Path("#MyPanel"));
FDriverElementRef ByType = Driver->FindElement(By::Path("<SButton>"));
FDriverElementRef ByHierarchy = Driver->FindElement(By::Path("#Suite//#Piano//#KeyA"));
FDriverElementRef MixedHierarchy = Driver->FindElement(By::Path("Form//Rows//#A1//<SEditableText>"));
```

> 来源：`AutomationDriver.spec.cpp` — FindElement / FindElements 测试

### 基本用法 — 鼠标与键盘交互

```cpp
// 点击元素（自动移动光标到元素位置）
Driver->FindElement(By::Id("KeyA"))->Click();

// 双击
Driver->FindElement(By::Id("KeyB"))->DoubleClick();

// Hover
Driver->FindElement(By::Id("KeyC"))->Hover();

// 文本输入（聚焦元素并输入字符串）
FDriverElementRef TextBox = Driver->FindElement(By::Id("A1"));
TextBox->Type(TEXT("Hello World"));

// 按 Tab 跳转到下一个字段并继续输入
TextBox->Type(TEXT("Field1\tField2\tField3"));

// 按下/释放修饰键
TextBox->Press(EKeys::LeftShift);
TextBox->Type(EKeys::A);  // 输入大写 A
TextBox->Release(EKeys::LeftShift);

// 组合键（如 Ctrl+X）
TextBox->TypeChord(EKeys::LeftControl, EKeys::X);
```

> 来源：`AutomationDriver.spec.cpp` — Element.Click / Element.Type / Element.Press 测试

### 进阶用法 — 动作序列（Sequence）

```cpp
// 创建可复用的动作序列
FDriverSequenceRef Sequence = Driver->CreateSequence();
Sequence->Actions()
    .Click(By::Id("KeyA"))
    .Click(By::Id("KeyB"))
    .Click(By::Id("KeyC"));

// 执行序列（可多次执行）
Sequence->Perform();

// 混合多种操作
FDriverElementRef TextBox = Driver->FindElement(By::Id("C2"));
FDriverSequenceRef MixedSequence = Driver->CreateSequence();
MixedSequence->Actions()
    .Focus(TextBox)
    .Type(TEXT("1234567890"))
    .Click(By::Id("KeyA"))
    .Focus(TextBox)
    .Type(EKeys::Home)
    .Press(EKeys::LeftShift)
    .Type(EKeys::Right)
    .Type(EKeys::Right)
    .Type(EKeys::Right)
    .Release(EKeys::LeftShift)
    .Type(EKeys::Delete);

MixedSequence->Perform();
```

> 来源：`AutomationDriver.spec.cpp` — Sequence 测试

### 进阶用法 — 等待条件

```cpp
// 配置隐式等待时间
Driver->GetConfiguration()->ImplicitWait = FTimespan::FromSeconds(0.5);

// 等待元素出现
Driver->Wait(Until::ElementExists(Element, FWaitTimeout::InSeconds(3)));

// 等待元素可见
Driver->Wait(Until::ElementIsVisible(By::Id("Piano"), FWaitTimeout::InSeconds(1)));

// 等待元素隐藏
Driver->Wait(Until::ElementIsHidden(By::Id("Piano"), FWaitTimeout::InSeconds(1)));

// 等待元素可交互
Driver->Wait(Until::ElementIsInteractable(Element, FWaitTimeout::InSeconds(3)));

// 在序列中使用 Wait
FDriverSequenceRef Sequence = Driver->CreateSequence();
Sequence->Actions()
    .Wait(Until::ElementExists(Element, FWaitTimeout::InSeconds(3)))
    .Focus(Element);
Sequence->Perform();

// 带自定义轮询间隔的 Wait（超时后取消后续操作）
Sequence->Actions()
    .Wait(Until::ElementIsVisible(Element, FWaitInterval::InSeconds(0.25), FWaitTimeout::InSeconds(1)))
    .Focus(Element);
bool bSuccess = Sequence->Perform();  // 超时返回 false
```

> 来源：`AutomationDriver.spec.cpp` — Sequence.Wait / Until::Element* 测试

### 进阶用法 — 文本过滤定位

```cpp
// 精确匹配（默认区分大小写）
FDriverElementRef Match = Driver->FindElement(
    By::TextFilter::Equals(By::Path("#Piano//<SButton>"), TEXT("Bb/A#")));

// 不区分大小写
FDriverElementRef MatchIgnoreCase = Driver->FindElement(
    By::TextFilter::Equals(By::Path("#Piano//<SButton>"), TEXT("bb/a#"), ESearchCase::IgnoreCase));

// 子字符串匹配（默认不区分大小写）
FDriverElementRef Contains = Driver->FindElement(
    By::TextFilter::Contains(By::Path("#Piano//<SButton>"), TEXT("b/a")));

// 子字符串匹配 — 区分大小写
FDriverElementRef ContainsCase = Driver->FindElement(
    By::TextFilter::Contains(By::Path("#Piano//<SButton>"), TEXT("Bb"), ESearchCase::CaseSensitive));

// 查找多个匹配元素
TArray<FDriverElementRef> Elements = Driver->FindElements(
    By::TextFilter::Equals(By::Path("Documents//<SButton>"), TEXT("Document 1"), ESearchCase::CaseSensitive))
    ->GetElements();
```

> 来源：`AutomationDriver.spec.cpp` — By::TextFilter 测试

### 进阶用法 — 滚动操作

```cpp
FDriverElementRef ScrollBox = Driver->FindElement(By::Path("#Documents//<SScrollBox>"));

// 基本滚动
Element->ScrollBy(-1);   // 向下滚动
Element->ScrollBy(1);    // 向上滚动

// 滚动到首/尾
Element->ScrollToBeginning();
Element->ScrollToEnd();

// 滚动直到子元素可见
FDriverElementRef Target = Driver->FindElement(By::Path("#Documents//List//#Document50"));
Element->ScrollToEndUntil(Target);  // 滚动直到 Document50 可见

// 在序列中滚动
FDriverSequenceRef Sequence = Driver->CreateSequence();
Sequence->Actions()
    .ScrollToBeginning(Element)
    .ScrollToEnd(Element, 1)
    .ScrollToEndUntil(Element, Target);
```

> 来源：`AutomationDriver.spec.cpp` — Element.ScrollBy / ScrollToEnd / ScrollToBeginning 测试

### Demo 示例

一个最小的 AutomationDriver 测试用例：

```cpp
// MyAutomationDriverTest.cpp
#include "Misc/AutomationTest.h"
#include "IAutomationDriver.h"
#include "IAutomationDriverModule.h"
#include "IDriverElement.h"
#include "LocateBy.h"

BEGIN_DEFINE_SPEC(FMyDriverTest, "MyProject.DriverTests",
    EAutomationTestFlags::ProductFilter | EAutomationTestFlags_ApplicationContextMask)
    FAutomationDriverPtr Driver;
END_DEFINE_SPEC(FMyDriverTest)

void FMyDriverTest::Define()
{
    BeforeEach([this]() {
        IAutomationDriverModule::Get().Enable();
        Driver = IAutomationDriverModule::Get().CreateDriver();
    });

    It("should click a button and verify text changes", EAsyncExecution::ThreadPool, [this]() {
        // 定位并点击按钮
        FDriverElementRef Button = Driver->FindElement(By::Id("MySubmitButton"));
        Button->Click();

        // 验证结果文本
        FDriverElementRef ResultLabel = Driver->FindElement(By::Id("ResultLabel"));
        TestEqual(TEXT("Result text"), ResultLabel->GetText().ToString(), TEXT("Submitted"));
    });

    AfterEach([this]() {
        Driver.Reset();
        IAutomationDriverModule::Get().Disable();
    });
}
```

**Build.cs 依赖：**

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "Slate",
    "SlateCore",
    "AutomationDriver"   // 核心依赖
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型与工具 |
| `InputCore` | 输入系统（FKey 定义） |
| `AutomationDriver` | UI 自动化驱动框架（核心依赖） |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `Slate` | Slate UI 框架 |
| `SlateCore` | Slate 核心类型 |
| `ApplicationCore` | 应用程序核心 |
| `Json` | JSON 支持 |

## 测试套件架构

此 plugin 内部构建了一个测试用的 Slate UI 界面（`SAutomationDriverSpecSuite`），模拟真实应用场景：

```
SWindow ("Automation Driver Spec Suite")
└── SAutomationDriverSpecSuite (Id: "Suite")
    ├── STextBlock (Id: "KeySequence", Tag: "Duplicate") — 显示按键序列
    ├── SVerticalBox (Id: "UserForm", Tag: "Form")
    │   ├── RowA: SEditableTextBox x2 (Id: "A1", "A2")
    │   ├── RowB: SEditableTextBox x2 (Id: "B1", "B2")
    │   ├── RowC: SEditableTextBox x2 (Id: "C1", "C2")
    │   └── SMultiLineEditableTextBox (Id: "D1")
    ├── Documents (Tag: "Documents")
    │   ├── SListView (Tag: "List") — 200 个文档按钮
    │   ├── STileView (Tag: "Tiles")
    │   └── SScrollBox — 200 个滚动按钮
    └── SOverlay (Id: "Piano", Tag: "Keyboard")
        ├── 白键: A, B, C, D, E, F, G (Tag: "Key")
        └── 黑键: A#/Bb, B#/Cb, C#/Db, D#/Eb, E#/Fb, F#/Gb, G#/Ab (Tag: "KeyModifier")
```

- **钢琴键盘**：7 个白键 + 6 个黑键（通过 SMenuAnchor 弹出），测试点击、Hover、可见性等
- **表单区域**：7 个文本输入框，测试 Type、Tab 跳转、文本提交等
- **文档列表**：200 个文档，分布在 ListView、TileView 和 ScrollBox 中，测试滚动与大量元素定位

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2024-11-11 | `6120f38` | 修复具有重复 ScrollBar 的元素在 AutomationDriver 中的滚动问题 |
| 2024-10-10 | `2dc759b` | 新增 `By::TextFilter::Contains` 和 `By::TextFilter::Equals` 定位器 |
| 2024-06-12 | `e521f5d` | 将 `EAutomationTestFlags::ApplicationContextMask` 替换为 `EAutomationTestFlags_ApplicationContextMask` |

### 维护评价

- **活跃维护** — 近 6 个月内有功能性更新（新增 TextFilter 定位器 + 滚动修复）
- 作为测试 plugin，它随着 AutomationDriver 框架的演进持续更新
- 测试覆盖全面，包含正向/反向测试用例和边界条件
- `EnabledByDefault: false`，仅在需要运行自动化驱动测试时启用
- **推荐**：如果你在使用 AutomationDriver 框架，此 plugin 是学习 API 和验证环境的绝佳参考

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/AutomationDriverTests)
- [AutomationDriver 框架](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AutomationDriver)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Tests/AutomationDriverTests/Source/AutomationDriverTests/Private/AutomationDriver.spec.cpp)
