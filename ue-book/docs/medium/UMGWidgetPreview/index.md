# UMG Widget Preview

> Quickly preview and debug UMG widgets without running PIE.

| 属性 | 值 |
|---|---|
| 分类 | UI |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（资产定义、编辑器集成） |
| 模块 | `UMGWidgetPreview` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-05-30 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/UMGWidgetPreview) | |

## 用途

UMG Widget Preview 是一个编辑器专用插件，解决了 UMG Widget 蓝图开发中的一个核心痛点：**无需进入 Play-in-Editor (PIE) 即可预览和调试 Widget**。

传统 UMG 开发流程中，要查看 Widget 的最终效果必须运行游戏。这个插件提供了一个独立的预览编辑器，内含：
- **独立预览视口**（Advanced Preview Scene），在编辑器中直接渲染 Widget
- **状态机管理**，自动处理 Widget 的暂停、后台、不支持等状态
- **Named Slot 支持**，可以为 Widget 的每个 Named Slot 分配子 Widget 进行组合预览
- **Widget 尺寸覆盖**，可自定义预览尺寸或遵循 UMG 设计器中的尺寸设置
- **DataValidation 集成**，检测并修复不支持预览的 Widget（缺少 `bCanCallInitializedWithoutPlayerContext`）
- **MVVM 扩展点**，通过公开 API 允许 MVVM 插件扩展预览功能

插件还支持通过 `IUMGWidgetPreviewModule::OnRegisterTabsForEditor` 事件为预览编辑器注册自定义 Tab 页。

## 使用场景

- 你在开发复杂的 UMG Widget 蓝图，想快速查看布局效果 → 在 Content Browser 右键 Widget Blueprint → 选择 "Preview"
- 你的 Widget 使用了 Named Slot，想测试不同子 Widget 的组合效果 → 在预览编辑器的 Details 面板中配置 Slot Widgets
- 你想测试 Widget 在不同尺寸下的表现 → 启用 "Override Widget Size" 并设置自定义尺寸
- 你的 Widget 需要 Player Context 才能初始化 → 插件会提示不支持，并提供一键修复按钮

## 蓝图用法

此插件不直接暴露蓝图节点给游戏逻辑使用，它是纯编辑器工具。但在编辑器中，UWidgetPreview 资产的 Details 面板提供了以下可编辑属性：

### 核心属性

| 属性 | 说明 | 所在类 |
|---|---|---|
| `WidgetType` | 要预览的 Widget Blueprint 或另一个 Widget Preview 资产 | `UWidgetPreview` |
| `SlotWidgetTypes` | 为 Named Slot 分配子 Widget（TMap） | `UWidgetPreview` |
| `bShouldOverrideWidgetSize` | 是否覆盖预览尺寸 | `UWidgetPreview` |
| `OverriddenWidgetSize` | 自定义预览尺寸 (FVector2D) | `UWidgetPreview` |

### 使用示例（操作描述）

1. 在 Content Browser 中找到一个 Widget Blueprint，右键选择 **"Preview"**
2. 插件自动创建一个临时的 `UWidgetPreview` 资产并打开预览编辑器
3. 左侧是预览视口，实时渲染 Widget
4. 右侧 Details 面板显示 Widget 配置：
   - 选择要预览的 Widget 类型
   - 如果 Widget 有 Named Slot，可以为每个 Slot 指定子 Widget
   - 可选启用尺寸覆盖
5. 如果 Widget 不支持无 Player Context 初始化，会在视口中央显示错误消息，并提供 "Fix" 按钮一键修复
6. 预览编辑器顶部工具栏有 "Reset" 按钮可重建预览

## C++ 用法

### 头文件引入

```cpp
#include "WidgetPreview.h"
#include "IUMGWidgetPreviewModule.h"
#include "IWidgetPreviewToolkit.h"
```

### 基本用法 — 创建和管理预览

```cpp
// 创建一个 Widget Preview 实例
UWidgetPreview* Preview = NewObject<UWidgetPreview>();

// 设置要预览的 Widget 类型
FPreviewableWidgetVariant Variant(MyUserWidgetClass);
Preview->SetWidgetType(Variant);

// 创建 Widget 实例用于预览
UWorld* World = /* 获取预览用的 World */;
UUserWidget* Instance = Preview->GetOrCreateWidgetInstance(World, true);

// 获取底层 Slate Widget 用于渲染
TSharedPtr<SWidget> SlateWidget = Preview->GetSlateWidgetInstance();
```

> 来源: `WidgetPreview.h`, `WidgetPreview.cpp`

### 进阶用法 — 检查 Widget 兼容性

```cpp
// 检查 Widget 及其子 Widget 是否支持无 Player Context 初始化
TArray<const UUserWidget*> FailedWidgets;
bool bSupported = Preview->CanCallInitializedWithoutPlayerContext(
    true,  // bInRecursive — 递归检查 Named Slot 中的子 Widget
    FailedWidgets
);

if (!bSupported)
{
    // FailedWidgets 包含所有不支持的 Widget CDO
    for (const UUserWidget* FailedWidget : FailedWidgets)
    {
        UE_LOG(LogTemp, Warning, TEXT("Widget %s 不支持预览"), *FailedWidget->GetName());
    }
}
```

> 来源: `WidgetPreview.cpp` (L265-335)

### 进阶用法 — 配置 Named Slot 子 Widget

```cpp
// 为 Named Slot 分配子 Widget
TMap<FName, FPreviewableWidgetVariant> SlotWidgets;
SlotWidgets.Add(FName("Content"), FPreviewableWidgetVariant(MyContentWidgetClass));
SlotWidgets.Add(FName("Header"), FPreviewableWidgetVariant(MyHeaderWidgetClass));
Preview->SetSlotWidgetTypes(SlotWidgets);
```

> 来源: `WidgetPreview.cpp` (L362-377)

### 进阶用法 — 监听 Widget 变化

```cpp
// 监听预览 Widget 的各种变化事件
Preview->OnWidgetChanged().AddLambda([](const EWidgetPreviewWidgetChangeType ChangeType)
{
    switch (ChangeType)
    {
    case EWidgetPreviewWidgetChangeType::Assignment:   // Widget 类型被重新赋值
    case EWidgetPreviewWidgetChangeType::Reinstanced:  // Widget 实例被重建
    case EWidgetPreviewWidgetChangeType::Structure:    // Widget 蓝图结构变化（编译等）
    case EWidgetPreviewWidgetChangeType::Resized:      // 预览尺寸变化
    case EWidgetPreviewWidgetChangeType::Destroyed:    // Widget 即将销毁
        break;
    }
});
```

> 来源: `WidgetPreview.h` (L19-27, L89)

### 进阶用法 — 扩展预览编辑器 Tab

```cpp
// 通过模块接口为预览编辑器注册自定义 Tab
IUMGWidgetPreviewModule& Module = FModuleManager::LoadModuleChecked<IUMGWidgetPreviewModule>("UMGWidgetPreview");
Module.OnRegisterTabsForEditor().AddLambda(
    [](const TSharedPtr<UE::UMGWidgetPreview::IWidgetPreviewToolkit>& Toolkit, const TSharedRef<FTabManager>& TabManager)
    {
        // 注册自定义 Tab...
    });
```

> 来源: `IUMGWidgetPreviewModule.h`

## Demo 示例

### 最小预览创建示例

**WidgetPreviewDemo.Build.cs:**
```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "UMG",
    "UMGWidgetPreview"
});
```

**WidgetPreviewDemo.h:**
```cpp
#pragma once

#include "CoreMinimal.h"

class FWidgetPreviewDemo
{
public:
    static void CreatePreview(UUserWidget* InUserWidgetCDO, UWorld* InWorld);

private:
    static void OnWidgetChanged(const EWidgetPreviewWidgetChangeType InType);
};
```

**WidgetPreviewDemo.cpp:**
```cpp
#include "WidgetPreviewDemo.h"
#include "WidgetPreview.h"

void FWidgetPreviewDemo::CreatePreview(UUserWidget* InUserWidgetCDO, UWorld* InWorld)
{
    // 创建预览资产
    UWidgetPreview* Preview = NewObject<UWidgetPreview>();

    // 设置要预览的 Widget
    Preview->SetWidgetType(FPreviewableWidgetVariant(InUserWidgetCDO->GetClass()));

    // 监听变化
    Preview->OnWidgetChanged().AddStatic(&FWidgetPreviewDemo::OnWidgetChanged);

    // 生成预览实例
    UUserWidget* Instance = Preview->GetOrCreateWidgetInstance(InWorld, true);
    if (Instance)
    {
        TSharedPtr<SWidget> SlateWidget = Preview->GetSlateWidgetInstance();
        // 将 SlateWidget 添加到 Slate 面板中渲染...
    }
}

void FWidgetPreviewDemo::OnWidgetChanged(const EWidgetPreviewWidgetChangeType InType)
{
    UE_LOG(LogTemp, Log, TEXT("Widget Preview changed: %d"), (int32)InType);
}
```

## 模块依赖

从 `UMGWidgetPreview.Build.cs` 的 `PrivateDependencyModuleNames` 提取：

| 模块 | 用途 |
|---|---|
| `AdvancedPreviewScene` | 提供 3D 预览场景基础设施 |
| `AssetDefinition` | 资产类型定义（Content Browser 集成） |
| `BlueprintGraph` | 蓝图编译相关 |
| `ContentBrowser` | Content Browser 右键菜单集成 |
| `Core` | 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `DataValidation` | 数据验证（Widget 兼容性检查和修复） |
| `EditorSubsystem` | 编辑器子系统访问 |
| `Engine` | 引擎核心 |
| `FieldNotification` | MVVM 字段通知支持 |
| `InputCore` | 输入处理 |
| `MessageLog` | 消息日志面板 |
| `Projects` | 插件/项目信息 |
| `PropertyEditor` | Details 面板自定义布局 |
| `Slate` | Slate UI 框架 |
| `SlateCore` | Slate 核心 |
| `ToolMenus` | 工具菜单和工具栏扩展 |
| `UMG` | UMG Widget 系统 |
| `UMGEditor` | UMG 编辑器（WidgetBlueprint 等） |
| `UnrealEd` | 编辑器基础设施 |

插件依赖: `DataValidation`（在 .uplugin 中声明）

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-08-28 | `e6f47d7` | Minor fix to a potential nullptr access in UMG Widget Preview Editor Plugin | Bug 修复：修复了预览编辑器中的空指针问题 |
| 2025-06-26 | `a2e7518` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files | 代码质量：添加了 UE_INLINE_GENERATED_CPP_BY_NAME 宏优化编译 |
| 2025-05-30 | `8396b18` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars | 代码质量：修正 DLL 导出标记位置 |

更早的重要更新：
- 2025-02-24 (`21473a3b`): **重要功能更新** — 预览现在尊重 UMG 设计器中指定的预览尺寸（Desired, Fill 等），并在角落显示当前预览尺寸，新增 Widget Size 覆盖属性
- 2024-08-05 (`a0b4cd7`): 模块销毁修复
- 2024-07-31 (`1e9af4e`): **重要功能更新** — 添加公开 API 支持可扩展性（主要为 MVVM 集成）

### 维护评价

- **创建时间**: 2024-05-30（约 2 年前）
- **最近更新**: 2025-08-28（约 8 个月前有 Bug 修复）
- **更新频率**: 中等，2025 年有多次更新但多为代码质量改进而非新功能
- **实验性状态**: ⚠️ `IsExperimentalVersion=true`，仍标记为实验性
- **活跃度**: 仍在维护中，有持续的 bug 修复和编译兼容性更新
- **限制**: 
  - 仅限编辑器使用（Editor 模块）
  - 需要 Widget 设置 `bCanCallInitializedWithoutPlayerContext = true` 才能预览
  - 依赖 DataValidation 插件
- **推荐度**: 适合在编辑器中快速预览 UMG Widget，但需注意实验性标记。对于 MVVM 项目特别有用，因为有专门的扩展点

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/UMGWidgetPreview)
- 官方文档：无（.uplugin 中 DocsURL 为空）
