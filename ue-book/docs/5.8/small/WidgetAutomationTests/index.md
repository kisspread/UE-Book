# WidgetAutomationTests

> （空描述）

| 属性 | 值 |
|---|---|
| 中文名 | 控件自动化测试 |
| 分类 | Testing |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资产） |
| 模块 | `WidgetAutomationTests` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2023-03-30 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/WidgetAutomationTests) | |

## 用途

`WidgetAutomationTests` 是一个**测试框架插件**，旨在为 Unreal Engine 的 Slate UI 控件（`SWidget`）提供自动化集成测试和单元测试的基础设施。它解决的核心问题是：当开发者创建或修改 Slate 控件时，如何高效、可靠地验证其行为（如属性设置、布局计算、绘制、焦点事件）是否符合预期。插件通过提供 Mock 控件基类、测试基类以及 JSON 基线对比机制，简化了编写和维护这类复杂 UI 控件测试的过程。

## 使用场景

-   **Slate 控件开发与维护**：当你正在开发一个自定义的 Slate 控件（例如一个复杂的列表、图表或自定义按钮），并希望确保其核心功能（如尺寸计算、绘制、交互）在代码更改后依然正确时。
-   **回归测试**：在修改底层 Slate 框架或相关模块后，需要验证现有控件是否受到影响。
-   **标准化测试流程**：团队希望建立一套标准化的方法来为 Slate 控件编写自动化测试，以提高代码质量和开发信心。

## 蓝图用法

本插件提供的功能主要面向 C++ 自动化测试，不包含可直接在蓝图中使用的 `BlueprintCallable` 节点。

## C++ 用法

### 头文件引入

```cpp
#include "WidgetAutomationTests.h"
#include "SlateTestBase.h"
#include "SWidgetMock.h"
```

### 基本用法

要使用此框架为你的 `SWidget` 编写测试，通常需要创建一个继承自 `FSlateTestBase<YourWidget>` 的测试类。

**示例**：为一个名为 `SMyButton` 的控件编写测试。

*来源: 根据 `FSlateTestBase` 模板使用方法推导。*

```cpp
// MyButtonAutomationTest.h
#pragma once

#include "SlateTestBase.h"
#include "SMyButton.h" // 你的控件头文件

class FMyButtonAutomationTest : public UE::SlateWidgetAutomationTest::FSlateTestBase<SMyButton>
{
public:
    FMyButtonAutomationTest() : FSlateTestBase(TEXT("MyButtonTest")) {} // 传入唯一的测试名称

    // 设置测试环境，例如调用 FindOrCreateTestJSONFile
    virtual void Setup(FAutomationTestBase* TestObj) override;

    // 执行测试操作，例如设置属性、模拟交互
    virtual void Run(FAutomationTestBase* TestObj) override;

    // 验证结果，通常会调用 ValidatePropertyChange
    virtual void Validate(FAutomationTestBase* TestObj) override;

    // 清理测试环境
    virtual void TearDown(FAutomationTestBase* TestObj) override;
};
```

### 进阶用法

框架的核心方法是 `ValidatePropertyChange`，它封装了一个完整的测试流程：设置属性 -> 验证属性值 -> 等待下一帧 -> 验证是否触发了预期的失效（`EInvalidateWidgetReason`）以及布局/绘制是否正确。

*来源: `FSlateTestBase::ValidatePropertyChange` 函数。*

```cpp
// 在 Run 函数中设置要测试的属性值
void FMyButtonAutomationTest::Run(FAutomationTestBase* TestObj)
{
    // 假设 SMyButton 有 SetText 方法
    GetSubjectWidget()->SetText(FText::FromString(TEXT("New Text")));
}

// 在 Validate 函数中验证
void FMyButtonAutomationTest::Validate(FAutomationTestBase* TestObj)
{
    // 测试 Text 属性更改是否触发了布局和绘制失效
    // SMyButton 需要有一个获取文本的函数 GetText()
    ValidatePropertyChange(
        TestObj,
        &SMyButton::GetText, // Getter 成员函数指针
        TEXT("Text"), // 属性名，用于错误信息
        FText::FromString(TEXT("New Text")), // 期望的值
        EInvalidateWidgetReason::Layout | EInvalidateWidgetReason::Paint // 预期的失效原因
    );
}
```

## Demo 示例

一个完整的最小测试类示例。

*来源: `FSlateTestBase` 和 `SWidgetMock` 的使用模式。*

```cpp
// SMinimalWidget.h
#pragma once
#include "Widgets/SLeafWidget.h"

class SMinimalWidget : public SLeafWidget
{
public:
    SLATE_BEGIN_ARGS(SMinimalWidget) {}
        SLATE_ATTRIBUTE(FString, TestString)
    SLATE_END_ARGS()
    void Construct(const FArguments& InArgs);
    virtual FVector2D ComputeDesiredSize(float) const override;
    virtual int32 OnPaint(const FPaintArgs&, const FGeometry&, const FSlateRect&, FSlateWindowElementList&, int32, const FWidgetStyle&, bool bParentEnabled) const override;
    void SetTestString(const FString& NewString);
    FString GetTestString() const;
private:
    TAttribute<FString> TestString;
};
```

```cpp
// MinimalWidgetAutomationTest.h
#pragma once
#include "SlateTestBase.h"
#include "SMinimalWidget.h"

// 1. 声明测试类，模板参数为被测控件
class FMinimalWidgetAutomationTest : public UE::SlateWidgetAutomationTest::FSlateTestBase<SMinimalWidget>
{
public:
    FMinimalWidgetAutomationTest() : FSlateTestBase(TEXT("MinimalWidgetTest")) {}

    virtual void Setup(FAutomationTestBase* TestObj) override
    {
        // 2. 在 Setup 中调用 FindOrCreateTestJSONFile 来初始化 JSON 基线文件
        GetSubjectWidget()->FindOrCreateTestJSONFile(GetTestName());
    }

    virtual void Run(FAutomationTestBase* TestObj) override
    {
        // 3. 在 Run 中操作被测控件
        GetSubjectWidget()->SetTestString(TEXT("Automation"));
    }

    virtual void Validate(FAutomationTestBase* TestObj) override
    {
        // 4. 在 Validate 中验证属性更改是否按预期工作
        ValidatePropertyChange(
            TestObj,
            &SMinimalWidget::GetTestString,
            TEXT("TestString"),
            TEXT("Automation"),
            EInvalidateWidgetReason::Layout | EInvalidateWidgetReason::Paint
        );
    }

    virtual void TearDown(FAutomationTestBase* TestObj) override
    {
        // 5. 清理工作（如果有）
    }
};
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下 double 常量截断为 float 的警告。 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以支持 FString 和 UE::FSharedString。 |
| 2026-02-04 | `80b637db` | Fixed printf format specifiers. | 修复了 printf 格式说明符问题。 |
| 2024-09-23 | `3ac66072` | [misc] fix lots of FString::Printf format errors | 修复了大量 FString::Printf 格式错误。 |
| 2024-06-12 | `e521f5d7` | Replaced EAutomationTestFlags::ApplicationContextMask with EAutomationTestFlags_ApplicationContextMa | 替换了过时的 EAutomationTestFlags 枚举。 |

### 维护评价

`WidgetAutomationTests` 是一个专用的**测试框架**插件。从提交历史看，它仍在维护中，但更新频率不高，主要以代码格式修复、编译警告消除和 API 适配为主，表明其核心功能已趋于稳定。该插件在 Epic Games 的内部开发中持续使用，对于有需要的开发者来说是一个可靠的选择。**注意**：它标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，表明其 API 可能会在未来版本中发生变化，使用时需要留意引擎更新日志。推荐在开发自定义 Slate 控件并需要系统化测试时使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/WidgetAutomationTests)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/WidgetAutomationTests/Tests)