# Floating Properties

> Show floating properties from the details panel directly on the active viewport.

| 属性 | 值 |
|---|---|
| 中文名 | 浮动属性 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `FloatingProperties` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-05-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/FloatingProperties) | |

## 用途

该插件将细节面板中的属性直接浮现在活动视口上方，允许用户在无需切换面板的情况下快速查看和编辑常用属性。

它解决了两个核心问题：
1. **减少上下文切换**：编辑角色或组件时不必频繁在视口和细节面板间移动鼠标。
2. **直观编辑**：属性直接浮现在物体附近，所见即所得，尤其适合变换、材质颜色等频繁调整的属性。

插件通过监听视口选择变化，自动提取选中 Actor 或组件的属性，并将其以浮窗形式显示在视口内。支持拖拽排列、自动吸附到视口边界，并允许保存每类属性的预设位置。

## 使用场景

- **关卡编辑**：频繁调整 Actor 的位置、旋转、缩放时，浮动属性面板可减少切换。
- **材质调试**：快速修改材质的颜色、粗糙度等参数，实时查看效果。
- **组件属性微调**：如灯光强度、碰撞半径等，无需展开组件层级。
- **多视口工作流**：每个视口独立显示浮动属性，适合多显示器布局。

## 蓝图用法

该插件为纯编辑器工具，**无公开蓝图 API**。所有功能通过编辑器界面和项目设置配置。

### 项目设置

在 **Project Settings > Plugins > Floating Properties** 中可配置：

- **默认显示属性**：通过 `FloatingPropertiesClassProperty` 数组，按类指定要显示在浮动面板上的属性路径。
- **位置预设**：每个属性可保存水平/垂直锚点、偏移量，实现自定义排列。
- **结构体属性值控件**：可通过 C++ 注册自定义结构体的值编辑控件，如颜色、旋转角等。

## C++ 用法

### 头文件引入

```cpp
#include "FloatingPropertiesModule.h"
#include "FloatingPropertiesSettings.h"
```

### 基本用法

#### 检查插件是否启用

```cpp
if (FFloatingPropertiesModule* Module = FModuleManager::GetModulePtr<FFloatingPropertiesModule>("FloatingProperties"))
{
    // 模块已加载
}
```

#### 注册自定义结构体属性值控件

插件允许为特定的 `UScriptStruct` 注册自定义的 `SWidget` 工厂，替代默认的数值输入框。例如为 `FColor` 类型注册颜色选择器（内置已支持 `FColor` 和 `FLinearColor`）。

```cpp
// 在模块 Startup 或插件加载后注册
FFloatingPropertiesModule::Get().RegiserStructPropertyValueWidgetDelegate(
    TBaseStructure<FMyCustomStruct>::Get(),
    FCreateStructPropertyValueWidgetDelegate::CreateLambda(
        [](TSharedRef<IPropertyHandle> InPropertyHandle) -> TSharedPtr<SWidget>
        {
            return SNew(SMyCustomStructWidget, InPropertyHandle);
        }
    )
);
```

#### 访问插件设置

```cpp
const UFloatingPropertiesSettings* Settings = GetDefault<UFloatingPropertiesSettings>();
if (Settings)
{
    // 读取配置的类属性列表
    for (const auto& Pair : Settings->ClassProperties)
    {
        // Pair.Key: TSoftClassPtr<UObject>
        // Pair.Value: FFloatingPropertiesClassProperties (属性路径到默认值映射)
    }
}
```

### 进阶用法

#### 自定义视口数据提供者

插件通过 `IFloatingPropertiesDataProvider` 接口获取视口和选择信息。默认实现针对 `ILevelEditor`，但可扩展至其他 `IToolkitHost`。

```cpp
class FMyDataProvider : public IFloatingPropertiesDataProvider
{
public:
    virtual TArray<TSharedRef<IFloatingPropertiesWidgetContainer>> GetWidgetContainers() override
    {
        // 返回所有需要显示浮动属性的容器（如视口）
    }

    virtual USelection* GetActorSelection() const override { /*...*/ }
    virtual USelection* GetComponentSelection() const override { /*...*/ }
    virtual UWorld* GetWorld() const override { /*...*/ }
    virtual bool IsWidgetVisibleInContainer(TSharedRef<IFloatingPropertiesWidgetContainer> InContainer) const override
    {
        return true; // 自定义可见性逻辑
    }
};
```

#### 显示/隐藏浮动属性

插件自动跟随视口选择变化。若需手动触发刷新，可调用：

```cpp
// 获取模块并强制刷新（不对外公开，仅供内部使用）
FFloatingPropertiesModule::Get().GetLevelEditorWidgetController()->RebuildWidgets(...);
```

注意：此 API 为 `protected`，仅内部使用。外部一般无需手动干预。

## Demo 示例

以下是一个最小 C++ 模块示例，展示如何在其他 Editor 模块中依赖 FloatingProperties 并注册自定义颜色控件。

### MyFloatingPropsDemoModule.h

```cpp
#pragma once

#include "Modules/ModuleInterface.h"

class FMyFloatingPropsDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

### MyFloatingPropsDemoModule.cpp

```cpp
#include "MyFloatingPropsDemoModule.h"
#include "FloatingPropertiesModule.h"
#include "FloatingPropertiesSettings.h"
#include "Widgets/Colors/SColorBlock.h"
#include "IPropertyHandle.h"
#include "UObject/NoExportTypes.h"

// 假设存在一个自定义结构体 FMyColor
USTRUCT(BlueprintType)
struct FMyColor
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category = "MyColor")
    FLinearColor Color;
};

void FMyFloatingPropsDemoModule::StartupModule()
{
    if (FFloatingPropertiesModule* FPM = FModuleManager::GetModulePtr<FFloatingPropertiesModule>("FloatingProperties"))
    {
        // 注册自定义颜色控件
        FPM->RegiserStructPropertyValueWidgetDelegate(
            TBaseStructure<FMyColor>::Get(),
            FCreateStructPropertyValueWidgetDelegate::CreateLambda(
                [](TSharedRef<IPropertyHandle> InPropertyHandle) -> TSharedPtr<SWidget>
                {
                    return SNew(SColorBlock)
                        .Color(this, &HandleColorValue, InPropertyHandle)
                        .OnMouseButtonDown_Lambda([InPropertyHandle](const FGeometry&, const FPointerEvent&) -> FReply
                            {
                                // 处理点击打开颜色选择器
                                return FReply::Handled();
                            });
                }
            )
        );
    }
}

void FMyFloatingPropsDemoModule::ShutdownModule()
{
    // 取消注册（可选）
    if (FFloatingPropertiesModule* FPM = FModuleManager::GetModulePtr<FFloatingPropertiesModule>("FloatingProperties"))
    {
        FPM->UnregiserStructPropertyValueWidgetDelegate(TBaseStructure<FMyColor>::Get());
    }
}

IMPLEMENT_MODULE(FMyFloatingPropsDemoModule, MyFloatingPropsDemo);
```

注意：实际控件实现需完整负责读/写属性值，此处仅为示意。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LevelEditor` | 获取活动视口和选择变化事件 |
| `UnrealEd` | 访问编辑器选择集（USelection）、Actor 管理 |
| `ToolMenus` | 注册视口右键菜单扩展（如启用/禁用浮动属性） |
| `DeveloperSettings` | 插件项目设置 |

无其他特殊依赖。

## 维护状态

### 近期更新

- 2025-09-12 `ce6ff392` — 修复 `nodiscard` 属性忽略返回值警告
- 2025-03-13 `b059f7b4` — 修复不可达代码警告
- 2024-11-06 `3b134e14` — 修复附着属性位置错误显示问题
- 2024-09-23 `7f438692` — 功能更新（未提供详细说明）
- 2024-05-28 `c1a3e0ee` — 移除 `ToolMenus.h` 冗余 include；初始提交

### 维护评价

该插件是实验性功能，创建于 2024 年 5 月，至今约 1.5 年。从提交记录看，近一年有多次更新，包括功能提交（2024-09-23）和持续的小修复（2025-03, 2025-09），说明仍在维护中。但需要注意其 `IsExperimentalVersion=true`，可能未完全稳定。适合希望提升编辑效率的开发者，推荐在非关键项目中使用，并关注官方更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/FloatingProperties)
- 官方文档：无（实验性插件暂无独立文档）
- 测试用例：无专用测试文件（可在 `Engine/Plugins/Experimental/FloatingProperties/Source/FloatingProperties/Private/...` 中找到单元测试，但未公开）