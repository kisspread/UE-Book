# UMG Viewmodel

> A plugin to support the Model-View-Viewmodel pattern in UMG.

| 属性 | 值 |
|---|---|
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ModelViewViewModel` (Runtime), `ModelViewViewModelAssetSearch` (Runtime), `ModelViewViewModelBlueprint` (Runtime), `ModelViewViewModelDebugger` (Runtime), `ModelViewViewModelDebuggerEditor` (Runtime), `ModelViewViewModelEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-04-01 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ModelViewViewModel) | |

## 用途

本插件为 UMG（Unreal Motion Graphics）实现了完整的 **Model-View-ViewModel (MVVM)** 架构模式。它解决的核心问题是：在传统 UMG 开发中，UI 逻辑（View）和数据/业务逻辑（Model）高度耦合，导致代码难以维护、测试和复用。

通过 MVVM 插件，开发者可以：

- **声明式数据绑定**：在蓝图编辑器中可视化地将 ViewModel 属性绑定到 Widget 属性，无需编写大量事件驱动代码
- **自动双向同步**：ViewModel 属性变化自动反映到 UI，UI 交互自动回写到 ViewModel
- **类型转换函数**：在绑定路径上插入转换函数，处理数据类型不匹配的场景（如 `float` → `FText`）
- **事件绑定**：将 Widget 事件（如按钮点击）绑定到 ViewModel 方法
- **条件绑定**：基于条件表达式控制绑定行为（如可见性、启用状态）
- **面板/列表支持**：专门的扩展支持 `UPanelWidget` 和 `UListViewBase` 的动态子项管理
- **蓝图 ViewModel**：无需编写 C++，直接在蓝图中定义 ViewModel 属性
- **运行时调试**：内置调试器支持，可在运行时检查绑定状态和数据流

**为什么需要这个插件？** 传统 UMG 开发中，当一个界面有 20+ 个数据字段需要显示和交互时，蓝图会变得极其复杂。MVVM 模式将"数据是什么"和"数据怎么显示"分离开来，使得 UI 逻辑清晰、可测试、可复用。

## 使用场景

- 你在做一个 RPG 游戏的角色面板，需要显示 HP、MP、等级、装备等大量数据 → 用 MVVM 绑定 ViewModel 到各个 Widget
- 你在做一个设置界面，需要双向同步滑块/开关状态到配置对象 → 用 MVVM 双向绑定
- 你有一个背包系统，需要动态生成物品列表 → 用 `PanelWidget` 或 `ListViewBase` 扩展
- 你需要在绑定路径上做数据转换（如将枚举值映射为颜色） → 用转换函数
- 你想在蓝图中定义 ViewModel 而不写 C++ → 用 `UMVVMBlueprintInstancedViewModel_PropertyBag`
- 你需要根据条件动态控制 Widget 的可见性或启用状态 → 用条件绑定

## 蓝图用法

### 核心概念

MVVM 插件的核心工作流程：

1. **定义 ViewModel**：创建一个继承自 `UMVVMViewModelBase` 的类（C++ 或蓝图），声明带 `FieldNotify` 标记的属性
2. **配置 View**：在 Widget Blueprint 的 MVVM 面板中，添加 ViewModel 上下文并创建绑定
3. **运行时**：`UMVVMView` 自动管理绑定的生命周期和数据同步

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddViewModel` | 向 View 添加一个 ViewModel 上下文 | `UMVVMBlueprintView` |
| `RemoveViewModel` | 从 View 移除一个 ViewModel | `UMVVMBlueprintView` |
| `FindViewModel` | 按 ID 或名称查找 ViewModel 上下文 | `UMVVMBlueprintView` |
| `AddBinding` | 添加一个源到目标的绑定 | `UMVVMBlueprintView` |
| `RemoveBinding` | 移除一个绑定 | `UMVVMBlueprintView` |
| `AddEvent` | 添加一个事件绑定（如按钮点击） | `UMVVMBlueprintView` |
| `AddCondition` | 添加一个条件绑定 | `UMVVMBlueprintView` |
| `GetConversionFunction` | 获取绑定的转换函数（源→目标或反向） | `FMVVMBlueprintViewBinding` |
| `IsValid` | 检查转换函数是否有效 | `UMVVMBlueprintViewConversionFunction` |
| `NeedsWrapperGraph` | 检查转换函数是否需要包装图 | `UMVVMBlueprintViewConversionFunction` |

### ViewModel 上下文创建类型

| 类型 | 说明 |
|---|---|
| `Manual` | 手动赋值，ViewModel 稍后通过蓝图设置 |
| `CreateInstance` | Widget 创建时自动实例化 ViewModel |
| `GlobalViewModelCollection` | 从全局 MVVM 子系统获取已注册的 ViewModel |
| `PropertyPath` | 通过属性路径或函数获取 ViewModel |
| `Resolver` | 通过自定义 Resolver 对象获取 ViewModel |

### 使用示例（蓝图描述）

**场景：创建一个简单的 HP 显示**

1. 创建一个 C++ ViewModel 类 `UMyCharacterViewModel`，继承 `UMVVMViewModelBase`
2. 添加属性 `UPROPERTY(BlueprintReadWrite, FieldNotify) float HealthPercent`
3. 创建 Widget Blueprint `WBP_HealthBar`
4. 在 WBP 编辑器的 MVVM 面板中：
   - 添加 ViewModel 上下文，选择 `UMyCharacterViewModel`，创建类型设为 `CreateInstance`
   - 添加绑定：Source 选择 `HealthPercent`，Destination 选择 ProgressBar 的 `Percent`
5. 运行时，当 ViewModel 的 `HealthPercent` 变化时，ProgressBar 自动更新

**场景：双向绑定设置滑块**

1. ViewModel 属性标记为 `FieldNotify`
2. 绑定模式设为 `TwoWay`
3. 添加转换函数处理 `float` ↔ `FText` 的显示格式化

## C++ 用法

### 头文件引入

```cpp
// 核心运行时
#include "MVVMViewModelBase.h"
#include "MVVMSubsystem.h"
#include "View/MVVMView.h"

// 蓝图相关（编辑器/蓝图模块）
#include "MVVMBlueprintView.h"
#include "MVVMBlueprintViewBinding.h"
#include "MVVMBlueprintViewModelContext.h"
```

### 基本用法：定义 ViewModel

```cpp
// MyCharacterViewModel.h
#pragma once

#include "MVVMViewModelBase.h"
#include "FieldNotification/FieldNotificationDeclaration.h"
#include "MyCharacterViewModel.generated.h"

UCLASS(BlueprintType)
class UMyCharacterViewModel : public UMVVMViewModelBase
{
    GENERATED_BODY()

public:
    // 使用 FieldNotify 宏声明可绑定属性
    UE_FIELD_NOTIFICATION_DECLARE_CLASS_DESCRIPTOR_BEGIN(UMyCharacterViewModel)
    UE_FIELD_NOTIFICATION_DECLARE_FIELD(HealthPercent)
    UE_FIELD_NOTIFICATION_DECLARE_FIELD(PlayerName)
    UE_FIELD_NOTIFICATION_DECLARE_CLASS_DESCRIPTOR_END()

    UPROPERTY(BlueprintReadWrite, FieldNotify, Category = "Stats")
    float HealthPercent = 1.0f;

    UPROPERTY(BlueprintReadWrite, FieldNotify, Category = "Stats")
    FText PlayerName;

    // 设置器会自动触发通知
    UFUNCTION(BlueprintCallable, Category = "Stats")
    void SetHealthPercent(float NewValue)
    {
        UE_MVVM_SET_PROPERTY_VALUE(HealthPercent, NewValue);
    }

    UFUNCTION(BlueprintCallable, Category = "Stats")
    void SetPlayerName(const FText& NewValue)
    {
        UE_MVVM_SET_PROPERTY_VALUE(PlayerName, NewValue);
    }
};
```

> 来源：基于 `UMVVMViewModelBase` 的标准用法，参考 `MVVMViewModelBase.h`

### 基本用法：在 Widget 中使用 View

```cpp
// MyUserWidget.h
#pragma once

#include "Blueprint/UserWidget.h"
#include "MyUserWidget.generated.h"

class UMyCharacterViewModel;

UCLASS()
class UMyUserWidget : public UUserWidget
{
    GENERATED_BODY()

protected:
    virtual void NativeConstruct() override
    {
        Super::NativeConstruct();
        
        // 获取 MVVM View（由插件自动生成）
        UMVVMView* MVVMView = UMVVMView::GetView(this);
        if (MVVMView)
        {
            // 初始化 ViewModel 上下文
            MVVMView->Initialize();
        }
    }
};
```

### 进阶用法：自定义 View Extension

```cpp
// 通过继承 UMVVMBlueprintViewExtension 来注入自定义编译行为
// 参考 MVVMBlueprintViewExtension.h

class UMyCustomViewExtension : public UMVVMBlueprintViewExtension
{
    GENERATED_BODY()

public:
    // 添加自定义属性到 Widget
    virtual TArray<UE::MVVM::Compiler::FBlueprintViewUserWidgetProperty> AddProperties() override
    {
        TArray<UE::MVVM::Compiler::FBlueprintViewUserWidgetProperty> Result;
        // ... 添加属性定义
        return Result;
    }

    // 在编译阶段注入自定义逻辑
    virtual void Compile(UE::MVVM::Compiler::IMVVMBlueprintViewCompile* Compiler,
                         UWidgetBlueprintGeneratedClass* Class,
                         UMVVMViewClass* ViewExtension) override
    {
        // 自定义编译逻辑
    }

    // 处理 Widget 重命名
    virtual bool WidgetRenamed(FName OldName, FName NewName) override
    {
        // 返回 true 表示已处理
        return false;
    }
};
```

> 来源：`Engine/Plugins/Runtime/ModelViewViewModel/Source/ModelViewViewModelBlueprint/Public/Extensions/MVVMBlueprintViewExtension.h`

### 进阶用法：转换函数

```cpp
// 转换函数用于在绑定路径上转换数据类型
// 参考 MVVMConversionFunctionHelper.h

#include "Bindings/MVVMConversionFunctionHelper.h"

// 检查一个 UFunction 是否需要包装器
bool bNeedsWrapper = UE::MVVM::ConversionFunctionHelper::RequiresWrapper(MyFunction);

// 创建一个 setter 图用于事件绑定
auto Result = UE::MVVM::ConversionFunctionHelper::CreateSetterGraph(
    WidgetBlueprint,
    FName("MyWrapperGraph"),
    SignatureFunction,
    PropertyPath,
    UE::MVVM::ConversionFunctionHelper::FCreateGraphParams{
        .bIsConst = false,
        .bTransient = true,
        .bIsForEvent = true
    }
);

if (Result.HasValue())
{
    UEdGraph* NewGraph = Result.GetValue().NewGraph;
    UK2Node* WrappedNode = Result.GetValue().WrappedNode;
}
```

> 来源：`Engine/Plugins/Runtime/ModelViewViewModel/Source/ModelViewViewModelBlueprint/Public/Bindings/MVVMConversionFunctionHelper.h`

### 进阶用法：属性路径

```cpp
// FMVVMBlueprintPropertyPath 表示绑定中的属性路径
// 参考 MVVMPropertyPath.h

#include "MVVMPropertyPath.h"

// 从 Blueprint 上下文和字段创建属性路径项
FMVVMBlueprintFieldPath FieldPath(MyBlueprint, MyFieldVariant);

// 获取字段名称
FName FieldName = FieldPath.GetFieldName(MyClass);

// 获取字段（解析后）
UE::MVVM::FMVVMConstFieldVariant Field = FieldPath.GetField(MyClass);

// 检查来源类型
FMVVMBlueprintPropertyPath PropertyPath;
// PropertyPath.GetSource() 返回 EMVVMBlueprintFieldPathSource::Widget 或 ViewModel
```

> 来源：`Engine/Plugins/Runtime/ModelViewViewModel/Source/ModelViewViewModelBlueprint/Public/MVVMPropertyPath.h`

## 模块架构

本插件包含 6 个模块，按职责划分：

| 模块 | 类型 | 职责 |
|---|---|---|
| `ModelViewViewModel` | Runtime | 核心运行时：ViewModel 基类、View 管理、绑定执行、子系统 |
| `ModelViewViewModelBlueprint` | Runtime | 蓝图支持：蓝图视图定义、绑定配置、编译器接口、转换函数 |
| `ModelViewViewModelAssetSearch` | Runtime | 资产搜索：支持在编辑器中搜索 MVVM 相关资产 |
| `ModelViewViewModelDebugger` | Runtime | 运行时调试：绑定状态检查、数据流追踪 |
| `ModelViewViewModelDebuggerEditor` | Runtime | 调试器编辑器：调试 UI 面板 |
| `ModelViewViewModelEditor` | Runtime | 编辑器支持：MVVM 面板、属性自定义、蓝图扩展 |

### 核心类关系

```
UMVVMBlueprintView (蓝图视图配置)
├── TArray<FMVVMBlueprintViewModelContext> (ViewModel 上下文列表)
├── TArray<FMVVMBlueprintViewBinding> (绑定列表)
│   ├── FMVVMBlueprintPropertyPath SourcePath
│   ├── FMVVMBlueprintPropertyPath DestinationPath
│   └── FMVVMBlueprintViewConversionPath (转换函数)
│       ├── UMVVMBlueprintViewConversionFunction* SourceToDestination
│       └── UMVVMBlueprintViewConversionFunction* DestinationToSource
├── TArray<UMVVMBlueprintViewEvent*> (事件绑定)
└── TArray<UMVVMBlueprintViewCondition*> (条件绑定)

UMVVMWidgetBlueprintExtension_View (Widget Blueprint 扩展)
└── UMVVMBlueprintView* BlueprintView

UMVVMBlueprintViewExtension (视图扩展基类)
├── UMVVMBlueprintViewExtension_ListViewBase (列表视图扩展)
└── UMVVMBlueprintViewExtension_PanelWidget (面板扩展)
```

## 模块依赖

从各模块的 Build.cs 分析，本插件的依赖关系如下：

| 模块 | 用途 |
|---|---|
| `FieldNotification` | 字段通知系统，MVVM 属性绑定的核心基础设施 |
| `UMG` | UMG Widget 框架，View 层的载体 |
| `KismetCompiler` | 蓝图编译器，用于编译 MVVM 绑定 |
| `Kismet` | 蓝图系统，提供 K2Node 支持 |
| `StructUtils` | 结构体工具，PropertyBag 用于蓝图 ViewModel |
| `DeveloperSettings` | 开发者设置基类 |

> 注：以上仅列出不常见的依赖。标准依赖（Core, CoreUObject, Engine, Slate, SlateCore, UMG, InputCore 等）已省略。

## 维护状态

### 近期更新

```
- da8a9339d794 MVVM: Move property permission validation out of compile
- d73fda75b642 MVVM: Add support for widget as source of condition, as this is necessary for verse fields.
- c27fe66b19f0 MVVM: fix widget renaming breaks component bindings #jira UE-322040 #rb yohann.dossantos
```

### 维护评价

**活跃维护中** ✅

- **创建时间**：2022 年 4 月，约 3 年历史
- **更新频率**：近期有持续的功能更新和 Bug 修复，包括权限验证重构、Verse 字段支持、组件绑定修复等
- **Beta 状态**：插件标记为 `IsBetaVersion=true`，`EnabledByDefault=false`，说明 Epic 仍在迭代中，API 可能发生变化
- **代码规模**：412 个源文件，6 个模块，是一个大型且功能完整的插件
- **已知限制**：
  - Beta 状态意味着 API 不稳定，升级引擎版本时可能需要适配
  - 部分 API 标记为 `UE_DEPRECATED`，说明正在经历重构
  - 需要手动启用（`EnabledByDefault=false`）
- **推荐程度**：**推荐在新项目中使用**。这是 Epic 官方的 MVVM 实现，虽然仍在 Beta，但已经相当成熟。对于复杂的 UMG 界面，MVVM 模式能显著提升代码可维护性。建议关注引擎版本升级时的 API 变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ModelViewViewModel)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/model-view-viewmodel-in-unreal-engine)