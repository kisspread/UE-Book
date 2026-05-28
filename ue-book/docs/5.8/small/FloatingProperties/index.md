# Floating Properties

> Show floating properties from the details panel directly on the active viewport.

| 属性 | 值 |
|---|---|
| 中文名 | 浮窗属性 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产） |
| 模块 | `FloatingProperties` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-26 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FloatingProperties) | |

## 用途

**Floating Properties** 是一个**编辑器工具**，旨在提高关卡设计和属性调试的工作流效率。它解决了在复杂场景中频繁在“细节”面板和视口之间切换的痛点。

该插件的核心功能是**将所选 Actor 或 ActorComponent 的属性直接以浮动控件的形式覆盖显示在活动的编辑器视口上**。开发者或设计师可以在不离开视口、不失去对场景对象视觉关注的情况下，实时查看和调整关键属性（如 Transform、材质参数、自定义属性等）。它本质上是一个 **“可配置的实时属性悬浮面板”**。

## 使用场景

- **关卡设计**：在摆放 Actor 时，需要实时微调其位置（X/Y/Z）或旋转，而不希望每次都去侧边栏的“细节”面板寻找对应条目。
- **材质与参数调试**：在调试材质或参数化蓝图时，需要将关键的 Scalar、Vector 或 Color 参数固定显示在视口旁，便于快速滑动调整并观察实时反馈。
- **自定义属性快速访问**：对于频繁修改的自定义属性（如 AI 巡逻点、触发器大小、效果强度等），可以将其“钉”在视口上，实现一键式访问。
- **多对象属性对比**：虽然主要针对单对象，但其堆栈和锚定机制允许将相关属性分组，便于理解复杂组件的配置。

## 蓝图用法

该插件主要通过编辑器内的 UI 交互进行配置，提供的蓝图接口较少，主要集中在设置层面。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Is Enabled` | 获取/设置插件是否全局启用 | `UFloatingPropertiesSettings` |
| `Save Config` | 保存当前显示的属性配置 | `SFloatingPropertiesPropertyWidget` |

### 使用示例（蓝图描述）

由于是编辑器工具，主要使用场景在编辑器 UI 中：

1.  **启用插件**：在“编辑” -> “编辑器偏好设置” -> “Floating Properties”中，勾选 `bEnabled` 以激活功能。
2.  **选择对象**：在关卡编辑器中选择一个 Actor 或 Component。
3.  **激活属性浮窗**：通常通过视口右上角或上下文菜单（插件会添加菜单扩展）激活。选中的对象的属性将以可拖拽的控件形式出现在视口上。
4.  **自定义显示**：在“细节”面板中找到你想固定的属性，点击旁边的按钮（插件添加），选择“添加到浮动视图”。该属性即可独立出现在视口。
5.  **排列与锚定**：可以直接在视口上拖拽这些属性控件。松开时，它们可以自动吸附（Snap）并形成父子堆栈关系，便于组织。
6.  **保存配置**：对于某个类（如 `BP_MyActor`），你可以将其多个属性（如 “Health”, “Speed”）及其在视口上的相对位置保存。下次选择同类型对象时，会自动应用此布局。

## C++ 用法

该插件的主要扩展点在于**注册自定义结构体的属性值控件**。

### 头文件引入

```cpp
#include "FloatingPropertiesModule.h"
```

### 基本用法

此示例展示如何为一个自定义结构体 `FMyStruct` 注册一个简单的文本控件。**来源**：基于 `FFloatingPropertiesModule` 的公共接口和模块模式推断。

```cpp
// 在你的编辑器模块启动时 (StartupModule)
void FMyEditorModule::StartupModule()
{
    // 获取 FloatingProperties 模块实例
    FFloatingPropertiesModule& FloatingPropsModule = FFloatingPropertiesModule::Get();

    // 定义一个委托，该委托负责为我们的结构体创建控件
    FFloatingPropertiesModule::FCreateStructPropertyValueWidgetDelegate MyDelegate;
    MyDelegate.BindLambda([](TSharedRef<IPropertyHandle> InPropertyHandle) -> TSharedPtr<SWidget>
    {
        // 创建一个最简单的文本块来显示属性名
        return SNew(STextBlock)
            .Text(InPropertyHandle->GetPropertyDisplayName());
        // 在实际场景中，这里可以创建更复杂的交互控件
    });

    // 为结构体 `FMyStruct` 注册这个委托
    // 当 FloatingProperties 需要显示一个类型为 FMyStruct 的属性时，会调用此委托来获取控件
    FloatingPropsModule.RegiserStructPropertyValueWidgetDelegate(FMyStruct::StaticStruct(), MyDelegate);
}

// 在你的编辑器模块关闭时 (ShutdownModule)
void FMyEditorModule::ShutdownModule()
{
    FFloatingPropertiesModule& FloatingPropsModule = FFloatingPropertiesModule::Get();
    // 注销委托，避免悬空引用
    FloatingPropsModule.UnregiserStructPropertyValueWidgetDelegate(FMyStruct::StaticStruct());
}
```

### 进阶用法

插件本身通过 `FloatingPropertiesPropertyNode` 和 `FloatingPropertiesSnapMetrics` 等内部类实现了复杂的**属性控件堆栈管理和吸附逻辑**。用户通常不直接调用这些，但理解其模型有助于定制行为：
- **Node (节点)**：每个浮动属性控件对应一个 `FFloatingPropertiesPropertyNode`，节点之间可以建立父子（Parent-Child）关系，形成一个**栈 (Stack)**。
- **Position (位置)**：每个节点的位置由 `FFloatingPropertiesClassPropertyPosition` 定义，包含相对于视口可拖拽区域的锚点（Anchor）和偏移（Offset）。
- **Snap (吸附)**：当拖拽一个控件接近另一个控件时（距离小于 `SnapDistance`），系统会计算 `FFloatingPropertiesSnapMetrics`，决定是作为父节点还是子节点吸附上去，形成垂直堆栈。

## Demo 示例

一个最小示例：为一个自定义颜色结构体注册一个颜色选择器控件。

**MyCustomColorStruct.h**
```cpp
USTRUCT(BlueprintType)
struct FMyCustomColorStruct
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FLinearColor Color = FLinearColor::White;
};
```

**MyEditorModule.h**
```cpp
#pragma once
#include "Modules/ModuleManager.h"

class FMyEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**MyEditorModule.cpp**
```cpp
#include "MyEditorModule.h"
#include "FloatingPropertiesModule.h"
#include "MyCustomColorStruct.h"
#include "Widgets/Colors/SColorPicker.h"
#include "PropertyHandle.h"

void FMyEditorModule::StartupModule()
{
    FFloatingPropertiesModule& FloatingPropsModule = FFloatingPropertiesModule::Get();

    // 创建一个能打开颜色选择器的控件委托
    FFloatingPropertiesModule::FCreateStructPropertyValueWidgetDelegate ColorPickerDelegate;
    ColorPickerDelegate.BindLambda([](TSharedRef<IPropertyHandle> InPropertyHandle) -> TSharedPtr<SWidget>
    {
        // 使用插件内置的通用颜色属性编辑器基类
        // 注意：这里简化了，实际插件提供了 SFloatingPropertiesLinearColorPropertyEditor 等封装类
        return SNew(STextBlock)
            .Text(FText::FromString(TEXT("[Color Swatch]")))
            .ColorAndOpacity(FSlateColor(FLinearColor::Red));
        // 真实实现会更复杂，需要处理属性读取和写入
    });

    FloatingPropsModule.RegiserStructPropertyValueWidgetDelegate(FMyCustomColorStruct::StaticStruct(), ColorPickerDelegate);
}

void FMyEditorModule::ShutdownModule()
{
    if (FFloatingPropertiesModule::IsAvailable())
    {
        FFloatingPropertiesModule::Get().UnregiserStructPropertyValueWidgetDelegate(FMyCustomColorStruct::StaticStruct());
    }
}

IMPLEMENT_MODULE(FMyEditorModule, MyEditor)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DetailsCustomizations` | 用于细节面板的自定义展示（插件内部可能用于生成属性控件） |
| `PropertyEditor` | 提供 `IPropertyHandle`, `IPropertyRowGenerator` 等核心属性编辑和生成接口 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏 `UE_LOG` 迁移为新的 `UE_LOGF` 形式，属于代码现代化维护。 |
| 2025-09-12 | `fd5c41be` | Addressing instances "ignoring return value of function declared with 'nodiscard' attribute" issue f | 修复了忽略带有 `nodiscard` 属性函数返回值的编译警告。 |
| 2025-03-13 | `b059f7b4` | Fix trivial unreachable code warnings. | 修复了琐碎的“不可达代码”编译警告。 |
| 2024-11-06 | `3b134e14` | Floating Properties: Properties attached to other properties will no longer mistakenly appear at the | 修复了一个 Bug：附着在其他属性上的属性不再会错误地出现在视口上（可能指位置计算错误）。 |
| 2024-09-23 | `7f438692` | Floating Properties | 功能性更新，具体内容未详述，但标记为针对插件本身的改动。 |

### 维护评价

**综合评价：谨慎使用**

- **状态**：该插件仍处于 **实验性 (Experimental)** 阶段，且默认未启用 (`Installed: false`)。这意味着其 API 和功能在未来版本中可能发生重大变更。
- **活跃度**：维护节奏较慢，最近一次功能性更新在2024年9月。后续的提交主要是**编译警告修复和代码清理**，而非新功能或重大 Bug 修复。这表明插件功能已趋于稳定，但可能也意味着 Epic 没有投入大量资源进行持续开发。
- **推荐度**：对于希望尝试新工作流、提升特定场景效率的资深开发者或团队，可以**在实验性项目中评估使用**。但不建议将其作为核心生产管线的关键依赖。在升级引擎版本时，需要特别关注此插件的兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FloatingProperties)
- [官方文档]( )
- [测试用例]( )（插件目录内未发现标准测试文件）