# UMG Viewmodel

> A plugin to support the Model-View-Viewmodel pattern in UMG.

| 属性 | 值 |
|---|---|
| 中文名 | UMG 视图模型 |
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ModelViewViewModel` (Runtime), `ModelViewViewModelAssetSearch` (Runtime), `ModelViewViewModelBlueprint` (Runtime), `ModelViewViewModelDebugger` (Runtime), `ModelViewViewModelDebuggerEditor` (Runtime), `ModelViewViewModelEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-04-01 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ModelViewViewModel) | |

> **注意**：此插件默认未启用（`EnabledByDefault=false`），且处于 Beta 状态（`IsBetaVersion=true`）。需要在项目设置中手动启用。

## 用途

本插件为 Unreal Engine 的 UMG（Unreal Motion Graphics）UI 系统实现了 **Model-View-ViewModel（MVVM）** 架构模式。它解决的核心问题是：**在构建复杂 UI 时，UI 控件（View）与游戏数据（Model）之间的紧耦合**。

通过 MVVM 模式，开发者可以：
- 将 UI 展示逻辑与业务数据分离，定义独立的 **ViewModel** 类来持有和暴露 UI 所需的数据
- 在编辑器中通过可视化面板配置 **Binding（绑定）**，将 ViewModel 属性自动同步到 Widget 属性
- 支持 **双向绑定**（TwoWay）、**单向绑定**（OneWayToDestination/OneWayToSource）等多种绑定模式
- 配置 **转换函数（Conversion Function）** 在源和目标之间进行类型转换
- 使用 **事件（Event）** 和 **条件（Condition）** 系统实现更复杂的交互逻辑
- 为 ListView/Panel 等列表类控件提供专门的 ViewModel 绑定支持

该插件包含 6 个模块，涵盖核心运行时、蓝图支持、调试器和编辑器扩展，是一个完整的 MVVM 工具链。

## 使用场景

- 你正在构建一个数据驱动的 RPG 游戏 UI（背包、技能树、状态面板）→ 使用 MVVM 绑定将玩家数据自动同步到 UI
- 你需要 UI 能响应多个数据源的变化（血量变化更新血条、金币变化更新商店）→ 定义多个 ViewModel 并分别绑定
- 你使用 ListView 显示动态列表数据（排行榜、邮件列表）→ 为 ListView 配置 Entry ViewModel
- 你的 UI 需要双向数据绑定（输入框 ↔ 数据模型）→ 使用 TwoWay 绑定模式
- 你需要在数据变化时有条件地更新 UI → 使用 Condition 系统
- 你希望在蓝图编辑器中可视化管理所有数据绑定关系 → 启用此插件获取 MVVM 面板

## 蓝图用法

本插件主要通过 **编辑器子系统** `UMVVMEditorSubsystem` 提供蓝图可调用的 API，用于在蓝图编辑器中管理 MVVM 绑定配置。

### 核心节点 — ViewModel 管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RequestView` | 为指定 WidgetBlueprint 请求/创建 MVVM 视图 | `UMVVMEditorSubsystem` |
| `GetView` | 获取 WidgetBlueprint 已有的 MVVM 视图 | `UMVVMEditorSubsystem` |
| `AddViewModel` | 向 WidgetBlueprint 添加一个 ViewModel 类 | `UMVVMEditorSubsystem` |
| `AddInstancedViewModel` | 添加一个实例化 ViewModel（运行时创建实例） | `UMVVMEditorSubsystem` |
| `RemoveViewModel` | 从 WidgetBlueprint 移除指定 ViewModel | `UMVVMEditorSubsystem` |
| `RenameViewModel` | 重命名 ViewModel，自动更新所有引用 | `UMVVMEditorSubsystem` |
| `ReparentViewModel` | 变更 ViewModel 的父类 | `UMVVMEditorSubsystem` |
| `VerifyViewModelRename` | 验证 ViewModel 重命名是否合法 | `UMVVMEditorSubsystem` |

### 核心节点 — 绑定管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddBinding` | 添加一条新的绑定关系，返回绑定引用 | `UMVVMEditorSubsystem` |
| `RemoveBinding` | 移除指定绑定 | `UMVVMEditorSubsystem` |
| `SetSourcePathForBinding` | 设置绑定的源路径（ViewModel 属性或 Widget 属性） | `UMVVMEditorSubsystem` |
| `SetDestinationPathForBinding` | 设置绑定的目标路径 | `UMVVMEditorSubsystem` |
| `SetBindingTypeForBinding` | 设置绑定模式（OneWay/TwoWay 等） | `UMVVMEditorSubsystem` |
| `SetEnabledForBinding` | 启用/禁用绑定 | `UMVVMEditorSubsystem` |
| `SetCompileForBinding` | 设置绑定是否参与编译 | `UMVVMEditorSubsystem` |
| `OverrideExecutionModeForBinding` | 覆盖绑定的执行模式（即时/延迟） | `UMVVMEditorSubsystem` |
| `SetSourceToDestinationConversionFunction` | 设置源→目标的转换函数 | `UMVVMEditorSubsystem` |
| `SetDestinationToSourceConversionFunction` | 设置目标→源的转换函数 | `UMVVMEditorSubsystem` |

### 核心节点 — 事件与条件

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddEvent` / `RemoveEvent` | 添加/移除事件 | `UMVVMEditorSubsystem` |
| `AddCondition` / `RemoveCondition` | 添加/移除条件 | `UMVVMEditorSubsystem` |
| `SetEventPath` | 设置事件的触发路径 | `UMVVMEditorSubsystem` |
| `SetEventDestinationPath` | 设置事件的目标路径 | `UMVVMEditorSubsystem` |
| `SetConditionPath` | 设置条件的检查路径 | `UMVVMEditorSubsystem` |
| `SetConditionOperation` | 设置条件操作类型（大于/小于/等于等） | `UMVVMEditorSubsystem` |

### 核心节点 — 查询

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetBindableWidgets` | 获取当前 WidgetBlueprint 中可绑定的 Widget 列表 | `UMVVMEditorSubsystem` |
| `GetAllViewModels` | 获取当前 WidgetBlueprint 中所有 ViewModel | `UMVVMEditorSubsystem` |
| `GetChildViewModels` | 获取指定类的所有子 ViewModel 属性 | `UMVVMEditorSubsystem` |
| `GetAvailableConversionFunctions` | 获取可用的类型转换函数列表（已废弃） | `UMVVMEditorSubsystem` |
| `IsValidConversionFunction` | 验证转换函数是否对指定源/目标类型有效 | `UMVVMEditorSubsystem` |
| `IsSimpleConversionFunction` | 判断是否为简单转换函数 | `UMVVMEditorSubsystem` |
| `GetConversionFunctionGraph` | 获取绑定的转换函数图表 | `UMVVMEditorSubsystem` |

### 使用示例（蓝图描述）

**添加 ViewModel 并创建绑定**：
1. 从 `UMVVMEditorSubsystem` 调用 `AddViewModel`，传入 WidgetBlueprint 引用和你的 ViewModel 类（如 `UInventoryViewModel`）
2. 调用 `AddBinding` 创建一条新绑定，获取返回的 `FMVVMBlueprintViewBinding` 引用
3. 调用 `SetSourcePathForBinding`，将源路径指向 ViewModel 的属性（如 `GoldAmount`）
4. 调用 `SetDestinationPathForBinding`，将目标路径指向 Widget 属性（如 TextBlock 的 `Text`）
5. 调用 `SetBindingTypeForBinding` 设置为 `OneWayToDestination`

**为 ListView 配置 Entry ViewModel**：
1. 在 WidgetBlueprint 编辑器中选择 ListView 控件
2. 在 Details 面板中找到 MVVM 扩展区域，点击 "+" 按钮添加 Panel/ListView 扩展
3. 在弹出的 ViewModel 选择器中选择 Entry 类对应的 ViewModel

## C++ 用法

本插件主要面向编辑器扩展开发，核心 API 通过 `IModelViewViewModelEditorModule` 接口和 `UMVVMEditorSubsystem` 子系统暴露。

### 头文件引入

```cpp
#include "MVVMEditorSubsystem.h"
#include "IModelViewViewModelEditorModule.h"
#include "MVVMConversionFunctionValue.h"
#include "MVVMLinkedPinValue.h"
```

### 基本用法 — 通过 Editor Subsystem 管理绑定

```cpp
// 获取 MVVM 编辑器子系统
UMVVMEditorSubsystem* MVVMEditor = GEditor->GetEditorSubsystem<UMVVMEditorSubsystem>();
if (!MVVMEditor) return;

// 为 WidgetBlueprint 获取或创建 MVVM 视图
UMVVMBlueprintView* View = MVVMEditor->RequestView(WidgetBlueprint);
if (!View) return;

// 添加一个 ViewModel
FGuid ViewModelId = MVVMEditor->AddViewModel(WidgetBlueprint, MyViewModelClass);

// 创建绑定并设置源/目标
FMVVMBlueprintViewBinding& Binding = MVVMEditor->AddBinding(WidgetBlueprint);
MVVMEditor->SetSourcePathForBinding(WidgetBlueprint, Binding, SourcePropertyPath);
MVVMEditor->SetDestinationPathForBinding(WidgetBlueprint, Binding, DestPropertyPath, true);

// 设置绑定类型为双向
MVVMEditor->SetBindingTypeForBinding(WidgetBlueprint, Binding, EMVVMBindingMode::TwoWay);
```

### 基本用法 — 打开独立编辑器窗口

```cpp
// 通过模块接口打开弹出式编辑器
IModelViewViewModelEditorModule& MVVMModule = 
    FModuleManager::GetModuleChecked<IModelViewViewModelEditorModule>("ModelViewViewModelEditor");
MVVMModule.OpenPopoutEditor(MyViewModelObject, false); // false = 编辑模式
```

### 进阶用法 — 查询可绑定的属性和转换函数

```cpp
UMVVMEditorSubsystem* MVVMEditor = GEditor->GetEditorSubsystem<UMVVMEditorSubsystem>();

// 获取所有可绑定的 Widget
TArray<UE::MVVM::FBindingSource> BindableWidgets = MVVMEditor->GetBindableWidgets(WidgetBlueprint);

// 获取所有 ViewModel
TArray<UE::MVVM::FBindingSource> AllViewModels = MVVMEditor->GetAllViewModels(WidgetBlueprint);

// 获取子 ViewModel 属性
TArray<FMVVMAvailableBinding> ChildVMs = MVVMEditor->GetChildViewModels(SourceClass, AccessorClass);

// 查询可用的转换函数（用于类型不匹配时的自动转换）
TArray<UE::MVVM::FConversionFunctionValue> Conversions = 
    MVVMEditor->GetConversionFunctions(WidgetBlueprint, ExpectedArgumentType, ExpectedReturnType);
```

## Demo 示例

以下示例展示如何在编辑器工具中通过 C++ 与 MVVM 系统交互。

```cpp
// MVVMHelper.h
#pragma once

#include "CoreMinimal.h"

class UWidgetBlueprint;
class UClass;

class FMVVMHelper
{
public:
    /** 为 WidgetBlueprint 设置基本的 MVVM 绑定 */
    static bool SetupBasicBinding(UWidgetBlueprint* WidgetBlueprint, 
                                   const UClass* ViewModelClass,
                                   FName SourcePropertyName,
                                   FName TargetWidgetName,
                                   FName TargetPropertyName);

    /** 获取 WidgetBlueprint 中所有可用的 ViewModel 列表 */
    static TArray<FString> GetViewModelNames(UWidgetBlueprint* WidgetBlueprint);
};
```

```cpp
// MVVMHelper.cpp
#include "MVVMHelper.h"
#include "MVVMEditorSubsystem.h"
#include "MVVMBlueprintView.h"
#include "WidgetBlueprint.h"
#include "MVVMBlueprintPropertyPath.h"
#include "MVVMBlueprintViewBinding.h"

bool FMVVMHelper::SetupBasicBinding(UWidgetBlueprint* WidgetBlueprint,
                                     const UClass* ViewModelClass,
                                     FName SourcePropertyName,
                                     FName TargetWidgetName,
                                     FName TargetPropertyName)
{
    if (!WidgetBlueprint || !ViewModelClass)
    {
        return false;
    }

    UMVVMEditorSubsystem* MVVMEditor = GEditor->GetEditorSubsystem<UMVVMEditorSubsystem>();
    if (!MVVMEditor)
    {
        return false;
    }

    // 1. 创建 MVVM 视图
    UMVVMBlueprintView* View = MVVMEditor->RequestView(WidgetBlueprint);
    if (!View)
    {
        return false;
    }

    // 2. 添加 ViewModel
    FGuid ViewModelId = MVVMEditor->AddViewModel(WidgetBlueprint, ViewModelClass);

    // 3. 创建绑定
    FMVVMBlueprintViewBinding& Binding = MVVMEditor->AddBinding(WidgetBlueprint);

    // 4. 设置源和目标路径
    FMVVMBlueprintPropertyPath SourcePath;
    // SourcePath 由编辑器内部构建，此处为示意
    MVVMEditor->SetSourcePathForBinding(WidgetBlueprint, Binding, SourcePath);

    FMVVMBlueprintPropertyPath DestPath;
    MVVMEditor->SetDestinationPathForBinding(WidgetBlueprint, Binding, DestPath, true);

    // 5. 设置为单向绑定
    MVVMEditor->SetBindingTypeForBinding(WidgetBlueprint, Binding, EMVVMBindingMode::OneWayToDestination);

    return true;
}

TArray<FString> FMVVMHelper::GetViewModelNames(UWidgetBlueprint* WidgetBlueprint)
{
    TArray<FString> Names;
    if (!WidgetBlueprint) return Names;

    UMVVMEditorSubsystem* MVVMEditor = GEditor->GetEditorSubsystem<UMVVMEditorSubsystem>();
    if (!MVVMEditor) return Names;

    TArray<UE::MVVM::FBindingSource> ViewModels = MVVMEditor->GetAllViewModels(WidgetBlueprint);
    for (const UE::MVVM::FBindingSource& VM : ViewModels)
    {
        if (VM.IsValid())
        {
            Names.Add(VM.GetDisplayName().ToString());
        }
    }

    return Names;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PropertyViewer` | 属性树视图控件，用于显示和选择可绑定的属性 |
| `WidgetBlueprint` | Widget 蓝图编辑器核心，提供 FWidgetBlueprintEditor 等基础设施 |
| `BlueprintGraph` | K2 节点系统，用于转换函数节点（UK2Node） |
| `Diff` | 蓝图差异对比，支持 MVVM 绑定的 Diff 视图 |
| `ClassViewer` | 类浏览器，用于选择 ViewModel 类 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `f172f2b0` | MVVMToolset: Initial MVVM toolset plugin that supports creating and modifying Viewmodel via blueprint | 新增 MVVM 工具集插件，支持通过蓝图创建和修改 ViewModel |
| 2026-05-13 | `825be502` | Listview/Panel Extension: use widget blueprint class directly to get the MVVM view during compilation | 修复 ListView/Panel 扩展编译时获取 MVVM 视图的方式 |
| 2026-05-12 | `21f108ac` | Cherry-pick UMGToolSet | 从其他分支合并 UMGToolSet 相关改动 |
| 2026-04-23 | `e24ce23f` | MVVM: Remove unused USTRUCT specifiers | 清理未使用的 USTRUCT 说明符 |
| 2026-04-22 | `cd8175a0` | MVVM: Resolve invalid transient outer when importing copied conditions and events. UMVVMBlueprintView... | 修复复制粘贴条件和事件时无效的 transient outer 引用问题 |

### 维护评价

- **状态**：**活跃维护中** — 最近数月持续有功能更新和 Bug 修复
- **成熟度**：仍处于 Beta 阶段（`IsBetaVersion=true`），API 可能发生变化（从源码中可见多处 `UE_DEPRECATED` 标记在 5.3/5.4/5.5 版本进行了接口调整）
- **代码质量**：架构清晰，包含完整的编辑器 UI（属性选择器、绑定列表、ViewModel 面板）、转换函数库、差异对比支持等
- **注意事项**：
  - 默认未启用，需手动在项目设置中激活
  - 部分 API 已标记废弃（如 `GetConversionFunction`、`GetAvailableConversionFunctions`），建议使用新版替代方法
  - 插件持续演进中，5.5 版本有较大的 API 调整（转换函数返回值类型变更）
- **推荐**：✅ 推荐用于中大型项目的 UI 开发，但注意跟踪 API 变更

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ModelViewViewModel)