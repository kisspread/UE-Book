# Floating Properties

> Show floating properties from the details panel directly on the active viewport.

| 属性 | 值 |
|---|---|
| 中文名 | 浮动属性 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例资产） |
| 模块 | `FloatingProperties` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-26 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FloatingProperties) | |

## 用途

这个插件解决了在 Unreal Engine 中频繁在细节面板和视口之间切换的痛点。它允许开发者将细节面板中选中 Actor 或组件的特定属性直接以浮动小部件的形式显示在编辑器视口上方，从而实时查看和编辑这些属性，无需在面板间来回导航。它尤其适用于需要频繁调整多个对象特定属性（如颜色、位置、数值参数）的场景。

## 使用场景

- **快速调整材质颜色**：在场景中同时查看和编辑多个材质实例的主颜色属性。
- **精确放置物体**：在视口中实时查看并微调物体的位置、旋转或缩放数值，而无需反复打开属性面板。
- **动画调试**：快速查看动画蓝图或骨骼网格体的特定变量值。
- **关卡设计**：同时监控并调整场景中多个灯光或环境音效的参数。

## 蓝图用法

此插件主要是编辑器扩展，提供设置和数据接口。核心设置类 `UFloatingPropertiesSettings` 可在项目设置中配置。

### 核心节点

由于是编辑器插件，直接蓝图节点较少。主要通过 `UFloatingPropertiesSettings` 类进行配置。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get FloatingProperties Settings` | 获取插件设置实例（通常在项目设置中编辑） | `UFloatingPropertiesSettings` |

### 使用示例（蓝图描述）

1. **在项目设置中配置**：
   - 在编辑器偏好设置中找到 "Floating Properties" 分类。
   - 勾选 `bEnabled` 来启用插件。
   - 在 `SavedValues` 中添加属性预设，可以保存常用的属性值组合。
   - 在 `PropertyPositions` 中自定义每个属性在视口中的锚点和偏移位置。
   - 在 `PropertyAnchors` 中设置属性之间的父子锚定关系，使它们堆叠显示。

2. **运行时（编辑器内）**：
   - 启用后，在关卡编辑器视口中选中任意 Actor 或组件。
   - 根据插件设置，选中的对象的指定属性会自动以浮动小部件形式出现在视口中。
   - 可以通过拖拽小部件来重新排列它们，也可以直接在小部件上编辑属性值。

## C++ 用法

### 头文件引入

```cpp
#include "FloatingPropertiesModule.h"
#include "FloatingPropertiesSettings.h"
```

### 基本用法

**注册自定义属性控件（来自 FloatingPropertiesModule.h）**
```cpp
#include "FloatingPropertiesModule.h"
#include "YourStruct.h"

// 假设你有一个自定义结构体 FMyVector，想要为其创建一个特殊的浮动属性控件
void RegisterMyVectorWidgetDelegate()
{
    FFloatingPropertiesModule& Module = FFloatingPropertiesModule::Get();
    
    // 创建一个委托，当需要为 FMyVector 类型的属性创建控件时被调用
    FFloatingPropertiesModule::FCreateStructPropertyValueWidgetDelegate MyDelegate;
    MyDelegate.BindLambda([](TSharedRef<IPropertyHandle> PropertyHandle) -> TSharedPtr<SWidget>
    {
        // 创建并返回一个自定义的 Slate 控件，用于编辑 FMyVector
        // 例如：return SNew(SMyVectorPropertyEditor, PropertyHandle);
        return nullptr; // 返回 null 则使用默认控件
    });
    
    // 注册委托
    Module.RegiserStructPropertyValueWidgetDelegate(FMyVector::StaticStruct(), MyDelegate);
}
```

**访问插件设置（来自 FloatingPropertiesSettings.h）**
```cpp
#include "FloatingPropertiesSettings.h"

void CheckAndEnablePlugin()
{
    // 获取插件设置对象
    UFloatingPropertiesSettings* Settings = GetMutableDefault<UFloatingPropertiesSettings>();
    
    if (Settings && !Settings->bEnabled)
    {
        // 通过设置对象启用插件
        Settings->bEnabled = true;
        Settings->PostEditChange(); // 触发保存和通知
    }
    
    // 监听设置变化
    UFloatingPropertiesSettings::OnChange.AddLambda([](const UFloatingPropertiesSettings* InSettings, FName InSettingName)
    {
        if (InSettingName == GET_MEMBER_NAME_CHECKED(UFloatingPropertiesSettings, bEnabled))
        {
            // 处理启用状态变化
        }
    });
}
```

### 进阶用法

**编程方式管理浮动属性预设（来自 FloatingPropertiesSettings.h）**
```cpp
void SaveCustomPropertyPreset()
{
    UFloatingPropertiesSettings* Settings = GetMutableDefault<UFloatingPropertiesSettings>();
    
    // 定义要保存的属性：某个类的特定属性路径
    FFloatingPropertiesClassProperty PropertyKey;
    PropertyKey.Class = AStaticMeshActor::StaticClass();
    PropertyKey.PropertyPath = TEXT("StaticMeshComponent.RelativeLocation.X");
    
    // 定义该属性的保存值
    FFloatingPropertiesClassProperties PropertyValues;
    PropertyValues.Properties.Add(TEXT("Value1"), TEXT("100.0"));
    PropertyValues.Properties.Add(TEXT("Value2"), TEXT("200.0"));
    
    // 保存到设置中
    Settings->SavedValues.Add(PropertyKey, PropertyValues);
    
    // 设置该属性在视口中的位置
    FFloatingPropertiesClassPropertyPosition Position;
    Position.HorizontalAnchor = HAlign_Left;
    Position.VerticalAnchor = VAlign_Top;
    Position.Offset = FIntPoint(10, 10);
    Settings->PropertyPositions.Add(PropertyKey, Position);
    
    Settings->PostEditChange();
}
```

## Demo 示例

以下示例演示如何创建一个简单的编辑器工具按钮，一键启用/禁用浮动属性功能。

**FloatingPropertiesDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "EdGraph/EdGraphNode.h"

class FFloatingPropertiesDemo
{
public:
    /** 在编辑器工具栏中注册一个切换按钮 */
    static void RegisterToolbarButton();
    
    /** 切换浮动属性的启用状态 */
    static void ToggleFloatingProperties();
};
```

**FloatingPropertiesDemo.cpp**
```cpp
#include "FloatingPropertiesDemo.h"
#include "FloatingPropertiesSettings.h"
#include "Framework/MultiBox/MultiBoxBuilder.h"
#include "Styling/AppStyle.h"

#define LOCTEXT_NAMESPACE "FloatingPropertiesDemo"

void FFloatingPropertiesDemo::RegisterToolbarButton()
{
    // 此函数通常在插件 StartupModule 中通过 FExtender 调用，这里仅为演示
    // 实际注册需要在合适的时机通过 LevelEditor 或其他工具栏扩展器完成
}

void FFloatingPropertiesDemo::ToggleFloatingProperties()
{
    UFloatingPropertiesSettings* Settings = GetMutableDefault<UFloatingPropertiesSettings>();
    if (Settings)
    {
        Settings->bEnabled = !Settings->bEnabled;
        Settings->PostEditChange();
        
        FMessageDialog::Open(EAppMsgType::Ok, 
            Settings->bEnabled ? 
            LOCTEXT("EnabledMsg", "Floating Properties have been ENABLED.") :
            LOCTEXT("DisabledMsg", "Floating Properties have been DISABLED."));
    }
}

#undef LOCTEXT_NAMESPACE
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PropertyEditor` | 用于创建和管理属性编辑器界面 |
| `EditorStyle` | 提供编辑器风格的 Slate 控件样式 |
| `ToolMenus` | 用于扩展编辑器菜单和工具栏 |
| `UnrealEd` | 核心编辑器功能，如关卡编辑器、选择集管理 |
| `LevelEditor` | 提供关卡编辑器视口和相关接口 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG宏迁移到新的UE_LOGF格式，提升日志系统一致性。 |
| 2025-09-12 | `fd5c41be` | Addressing instances "ignoring return value of function declared with 'nodiscard' attribute" issue f | 修复了忽略`nodiscard`函数返回值的警告问题。 |
| 2025-03-13 | `b059f7b4` | Fix trivial unreachable code warnings. | 修复了简单的无法到达代码警告，提升代码质量。 |
| 2024-11-06 | `3b134e14` | Floating Properties: Properties attached to other properties will no longer mistakenly appear at the | 修复了属性附着到其他属性时位置显示错误的bug。 |
| 2024-09-23 | `7f438692` | Floating Properties | 修复了浮动属性的基础功能问题（具体信息被截断）。 |

### 维护评价

**活跃维护**。该插件创建于 2024 年初，虽然标记为实验性（`IsExperimentalVersion: true`），但维护活跃：
- **近期有实质性更新**：最近一次功能性更新在 2024 年 11 月，修复了属性附着位置的错误。
- **持续维护**：2025 年和 2026 年仍有维护性更新，主要是代码质量改进和警告修复。
- **实验性状态**：由于仍在实验阶段，可能还有功能上的限制或接口变化，但核心功能已可用。

**建议**：适合在开发环境中用于提升工作流效率，尤其是在频繁调整属性值的场景。由于是实验性插件，在生产环境中使用需谨慎，并关注后续版本更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FloatingProperties)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/FloatingProperties/Tests)（如果存在）