# Automation Driver Tests

> 

| 属性 | 值 |
|---|---|
| 中文名 | 自动化驱动测试 |
| 分类 | Testing |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源、Slate UI 模板） |
| 模块 | `AutomationDriverTests` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2020-11-09 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/AutomationDriverTests) | |

## 用途

这是 **AutomationDriver** 框架的配套测试插件，提供了一个用于验证自动化驱动功能的交互式测试场景——"钢琴键盘"UI。

AutomationDriver 是 UE5 中用于 UI 自动化测试的框架，能够以编程方式模拟用户交互（点击、输入、悬停等）。本插件不提供可复用的库代码，而是提供一套精心设计的 Slate UI 测试页面，包含：

- **钢琴键盘**：一组可点击的琴键按钮，记录点击和悬停序列，用于验证按钮定位、点击、悬停等自动化驱动能力
- **表单元素**：多个文本输入框，用于验证文本输入、提交、变更等交互
- **文档列表**：可滚动的按钮列表，用于验证滚动、定位等功能

插件从主引擎的 AutomationDriver 测试中独立出来，方便用户单独启用并运行自动化驱动的测试示例。

## 使用场景

- 你正在开发或调试 **AutomationDriver** 框架 → 启用本插件运行自动化测试验证驱动行为
- 你需要一个标准的交互式 UI 页面来测试 UI 自动化框架的定位器（Locator）功能
- 你在编写 UI 自动化测试用例时，需要一个包含按钮、输入框、列表等多种控件的测试沙盒
- 你需要验证 `By::TextFilter::Contains`、`By::TextFilter::Equals` 等文本定位器的正确性

## 蓝图用法

本插件无 BlueprintCallable API。它是一个纯测试插件，所有功能通过 C++ 自动化测试框架运行。

## C++ 用法

本插件不对外暴露可复用的 C++ API。其内部结构可作为编写类似自动化测试的参考。

### 头文件引入

```cpp
#include "AutomationDriverTests.h"
```

### 测试用例结构参考

测试用例通过 UE 的自动化测试框架（`IMPLEMENT_SIMPLE_AUTOMATION_TEST`）编写，使用 BDD 风格的 `GIVEN/WHEN/THEN` 宏组织测试逻辑。

典型的测试流程：

1. 创建 `IAutomationDriverSpecSuiteViewModel` 实例（包含钢琴键、表单、文档列表的完整数据模型）
2. 构建 `SAutomationDriverSpecSuite` Slate UI 并绑定 ViewModel
3. 使用 AutomationDriver API 模拟用户交互
4. 验证交互结果

## Demo 示例

本插件本身即为完整示例。核心组件如下：

### ViewModel 接口（Private）

```cpp
// 私有头文件，仅供内部测试使用
// Source/AutomationDriverTests/Private/AutomationDriverSpecSuiteViewModel.h

// 琴键枚举：覆盖所有钢琴音符（含升降号）
enum class EPianoKey : uint8
{
    AFlat, A, ASharp,
    BFlat, B, BSharp,
    CFlat, C, CSharp,
    DFlat, D, DSharp,
    EFlat, E, ESharp,
    FFlat, F, FSharp,
    GFlat, G, GSharp,
};

// 表单元素枚举
enum class EFormElement : uint8
{
    A1, A2, B1, B2, C1, C2, D1,
};

// ViewModel 接口：提供钢琴键交互、表单输入、文档列表操作
class IAutomationDriverSpecSuiteViewModel
{
public:
    virtual ~IAutomationDriverSpecSuiteViewModel() {}

    // 表单文本操作
    virtual FText GetFormText(EFormElement Element) const = 0;
    virtual void OnFormTextCommitted(const FText& InText, ETextCommit::Type InCommitType, EFormElement Element) = 0;
    virtual void OnFormTextChanged(const FText& InText, EFormElement Element) = 0;

    // 钢琴键交互
    virtual bool IsKeyEnabled(EPianoKey Key) const = 0;
    virtual FReply KeyClicked(EPianoKey Key) = 0;
    virtual void KeyHovered(EPianoKey Key) = 0;
    virtual FString GetKeySequence() const = 0;

    // 文档列表
    virtual TArray<TSharedRef<FDocumentInfo>>& GetDocuments() = 0;
    virtual FReply DocumentButtonClicked(TSharedRef<FDocumentInfo> Document) = 0;

    // 重置状态
    virtual void Reset() = 0;
};
```

### Slate UI 组件（Private）

```cpp
// Source/AutomationDriverTests/Private/SAutomationDriverSpecSuite.h

class SAutomationDriverSpecSuite : public SUserWidget
{
public:
    SLATE_USER_ARGS(SAutomationDriverSpecSuite) {}
    SLATE_END_ARGS()

    virtual void Construct(const FArguments& InArgs,
                           const TSharedRef<IAutomationDriverSpecSuiteViewModel>& InViewModel) = 0;

    // 获取琴键控件引用，用于自动化驱动定位
    virtual TSharedPtr<SWidget> GetKeyWidget(EPianoKey Key) const = 0;

    // 内容控制（用于测试动态添加/移除控件）
    virtual void RestoreContents() = 0;
    virtual void RemoveContents() = 0;

    // 滚动控制（用于测试滚动定位）
    virtual void ScrollDocumentsToTop() = 0;
    virtual void ScrollDocumentsToBottom() = 0;
};
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。具体依赖在 Build.cs 中定义，本插件作为测试插件仅依赖引擎基础模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-20 | `c154bfb5` | Fix test string expectation for Unix based system | 修复 Unix 系统下的测试字符串期望值 |
| 2026-01-26 | `b18aebbb` | PR #14018: Automation Driver in Lyra | 在 Lyra 示例项目中集成 AutomationDriver 支持 |
| 2024-11-11 | `6120f38e` | Fix scrolling of elements with duplicated ScrollBar in AutomationDriver | 修复 AutomationDriver 中重复 ScrollBar 元素的滚动问题 |
| 2024-10-10 | `2dc759b4` | Add By::TextFilter::Contains and By::TextFilter::Equals locators to AutomationDriver | 为 AutomationDriver 新增 Contains 和 Equals 文本过滤定位器 |
| 2024-06-12 | `e521f5d7` | Replaced EAutomationTestFlags::ApplicationContextMask with EAutomationTestFlags_ApplicationContextMa | 替换已废弃的自动化测试标志宏 |

### 维护评价

- **创建于 2020 年**，约 5 年历史，属于较年轻的测试插件
- **持续活跃维护**：2024-2026 年有多次功能性更新，包括新增定位器、平台兼容性修复、Lyra 集成等
- **紧跟上游变化**：随 AutomationDriver 框架的功能演进而同步更新测试
- **默认未启用**：`EnabledByDefault=false`，需要在项目设置中手动启用才能使用
- **仅限开发环境**：模块类型为 `UncookedOnly`，不会被打包到最终产品中
- **推荐使用**：如果你正在使用或开发 AutomationDriver 相关功能，本插件提供了标准的参考测试场景

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/AutomationDriverTests)
- [AutomationDriver 源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Source/Developer/AutomationDriver)