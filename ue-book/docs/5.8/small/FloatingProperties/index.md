# Floating Properties

> Show floating properties from the details panel directly on the active viewport.

| 属性 | 值 |
|---|---|
| 中文名 | 浮窗属性 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（设置资源） |
| 模块 | `FloatingProperties` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-26 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FloatingProperties) | |

## 用途

Floating Properties 插件旨在提升关卡编辑和原型制作的效率。它解决了在编辑器中频繁在细节面板和视口之间切换以查看或修改物体属性的问题。其核心功能是允许用户将物体（Actor 或 Component）的特定属性（如变换、颜色、数值等）以可交互的“浮窗”形式直接显示在 3D 视口上。

用户可以在视口内直接拖动、点击这些浮窗来修改属性值，无需打开细节面板。插件还支持将多个属性“堆叠”在一起，并允许用户自定义哪些属性需要显示以及它们的初始位置。这对于需要快速迭代光照参数、材质属性或物体位置的工作流非常有用。

## 使用场景

- 你正在调整场景中多个灯光的强度和颜色，希望在视口中同时看到并修改这些参数，而不是在细节面板中反复选择。
- 你需要精确地设置一组物体的相对位置（例如对齐多个平台），通过在视口直接拖动其“位置”属性浮窗会更直观。
- 你在进行原型设计时，希望快速调整一个关键对象的某些核心属性（如生命值、速度），并希望这些信息始终在视口可见。
- 你希望自定义一个“工作台”，只显示当前任务最关心的几个属性到视口上。

## 蓝图用法

此插件主要面向编辑器扩展，核心功能通过其设置对象和模块接口进行控制，直接的蓝图可调用节点较少。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Enabled` | 全局开关浮窗属性显示功能。 | `UFloatingPropertiesSettings` |
| `Save Config` / `Load Config` | 保存或加载用户对浮窗位置和自定义值的配置。 | `UFloatingPropertiesSettings` |
| `RegiserStructPropertyValueWidgetDelegate` | 为自定义的 `UScriptStruct` 类型注册用于创建其属性值小部件的委托。 | `FFloatingPropertiesModule` |

### 使用示例（蓝图描述）

在编辑器工具蓝图中，你可以通过 `Get Settings` 节点获取 `UFloatingPropertiesSettings` 实例。使用 `Set Enabled` 节点来控制浮窗功能的开关。要获取插件模块单例，可以使用 `Get` 静态函数。

## C++ 用法

插件通过模块 `FFloatingPropertiesModule` 和设置类 `UFloatingPropertiesSettings` 进行交互和控制。

### 头文件引入

```cpp
#include "FloatingPropertiesModule.h"
#include "FloatingPropertiesSettings.h"
```

### 基本用法

启用/禁用浮窗功能并监听设置变更。

```cpp
// 获取模块单例
FFloatingPropertiesModule& FPModule = FFloatingPropertiesModule::Get();

// 获取设置对象
UFloatingPropertiesSettings* FPSettings = GetMutableDefault<UFloatingPropertiesSettings>();

// 启用浮窗
FPSettings->bEnabled = true;
FPSettings->PostEditChange(); // 触发设置变更通知

// 监听设置变更（例如，自定义工具需要响应浮窗开关）
UFloatingPropertiesSettings::OnChange.AddLambda([](const UFloatingPropertiesSettings* InSettings, FName InSetting) {
    if (InSetting == GET_MEMBER_NAME_CHECKED(UFloatingPropertiesSettings, bEnabled))
    {
        // 根据启用状态执行操作
        bool bIsNowEnabled = InSettings->bEnabled;
        // ...
    }
});
```

### 进阶用法

为自定义的 `FVector` 属性注册一个特殊的浮动编辑器控件。

```cpp
// 假设我们有一个自定义的向量属性希望以特殊方式显示在视口
// 首先，注册一个委托，当遇到 FVector 属性时返回我们的自定义小部件
FPModule.RegiserStructPropertyValueWidgetDelegate(
    TBaseStructure<FVector>::Get(),
    FFloatingPropertiesModule::FCreateStructPropertyValueWidgetDelegate::CreateLambda(
        [](TSharedRef<IPropertyHandle> InPropertyHandle) -> TSharedPtr<SWidget>
        {
            // 这里返回一个自定义的 Slate 控件，例如带有三轴输入的编辑器
            // 具体实现取决于你的需求
            return SNew(STextBlock).Text(FText::FromString(TEXT("Custom Vector Editor")));
        }
    )
);

// 之后，当有物体显示其 FVector 类型的属性浮窗时，将使用我们注册的这个小部件。
```

## Demo 示例

以下是一个最小化的编辑器工具按钮示例，点击后切换浮窗功能的开关状态。

```cpp
// MyEditorTool.h
#pragma once
#include "CoreMinimal.h"

class FMyEditorTool
{
public:
    static void ToggleFloatingProperties();
    static bool IsFloatingPropertiesEnabled();
};
```

```cpp
// MyEditorTool.cpp
#include "MyEditorTool.h"
#include "FloatingPropertiesSettings.h"

void FMyEditorTool::ToggleFloatingProperties()
{
    UFloatingPropertiesSettings* Settings = GetMutableDefault<UFloatingPropertiesSettings>();
    if (Settings)
    {
        Settings->bEnabled = !Settings->bEnabled;
        Settings->PostEditChange();
    }
}

bool FMyEditorTool::IsFloatingPropertiesEnabled()
{
    const UFloatingPropertiesSettings* Settings = GetDefault<UFloatingPropertiesSettings>();
    return Settings ? Settings->bEnabled : false;
}
```

## 模块依赖

从插件的 `FloatingProperties.Build.cs` 分析，除了常见的 Core/Engine/Slate 依赖外，有以下特殊依赖：

| 模块 | 用途 |
|---|---|
| `DataValidation` | 用于插件内部数据验证。 |
| `PropertyEditor` | 用于创建和操作细节面板中的属性句柄和节点，是浮窗功能的核心依赖。 |
| `InputCore` | 提供输入相关的基础类型。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF，属于代码质量更新。 |
| 2025-09-12 | `fd5c41be` | Addressing instances "ignoring return value of function declared with 'nodiscard' attribute" issue f | 修复忽略标记了 `nodiscard` 函数返回值的警告。 |
| 2025-03-13 | `b059f7b4` | Fix trivial unreachable code warnings. | 修复了一些平凡的不可达代码警告。 |
| 2024-11-06 | `3b134e14` | Floating Properties: Properties attached to other properties will no longer mistakenly appear at the | 修复了一个功能 bug：属性附着到其他属性时错误显示的问题。 |
| 2024-09-23 | `7f438692` | Floating Properties | 提交记录信息不完整，推测为插件相关的一次更新。 |

### 维护评价

该插件创建于 **2024年1月**，至今约 **3年**，属于较新的插件。从 Git 历史看，最后一次更新在 **2026年4月**，虽然主要是日志宏的迁移，但表明它仍然跟随主引擎代码库进行维护。2024年末和2025年有实质性的 bug 修复和代码质量改进。作为标记为 `Experimental` 的插件，它正处于实验性阶段，功能可能发生变化，但维护活动显示 Epic 仍在持续关注和改进它。

**结论**：这是一个活跃维护中的实验性插件。非常适合希望在编辑器中获得更高效率的开发者尝试使用，但需注意其实验性状态，未来 API 和功能可能调整。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FloatingProperties)
- [官方文档]() (无)
- [测试用例]() (未提供)