# UMG View Model

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

## 用途

ModelViewViewModel 插件为 UMG 蓝图系统实现了 **MVVM（Model-View-ViewModel）** 架构模式。它解决的核心问题是：**在复杂 UI 项目中，将数据逻辑（ViewModel）与界面表现（View）解耦**。

传统 UMG 蓝图中，数据获取、转换、绑定逻辑全部混在 Widget 蓝图里，导致：
- UI 蓝图臃肿，难以维护
- 数据逻辑无法复用
- 难以进行单元测试
- 无法灵活切换数据源

MVVM 插件通过以下机制解决这些问题：
1. **声明式绑定**：在专用编辑器中配置源路径（ViewModel 属性）到目标路径（Widget 属性）的绑定关系，而非手动拖线
2. **自动响应更新**：基于 `FieldNotification` 系统，ViewModel 属性变化时自动刷新绑定的 UI
3. **转换函数**：支持自定义函数在源和目标之间转换值类型
4. **多绑定模式**：支持 OneTime、OneWay（双向）、事件监听、条件绑定等多种模式
5. **编译时验证**：在蓝图编译阶段检查绑定路径合法性，提前暴露错误

## 使用场景

- 你在做一个 RPG 游戏的背包系统 → ViewModel 存储物品数据，View 自动显示物品列表、名称、图标
- 你有一个复杂的设置界面，数据来自配置文件 → 用 MVVM 绑定配置项到各控件，配置变更时 UI 自动更新
- 你需要多个界面共享同一份数据（如玩家状态栏、详情面板）→ 多个 Widget 绑定同一个 ViewModel
- 你想实现列表型 UI（邮件列表、排行榜）→ 配合 ListViewBase 扩展自动绑定条目数据
- 你需要在值转换时执行复杂逻辑（如字符串格式化、数值缩放）→ 使用转换函数

## 子模块概览

本插件包含 6 个模块，本文档聚焦 `ModelViewViewModelBlueprint` 模块的编译器与蓝图扩展部分。

| 模块 | 类型 | 职责 |
|---|---|---|
| `ModelViewViewModel` | Runtime | 核心运行时：视图类、绑定库、字段通知、ViewModel 基类 |
| `ModelViewViewModelBlueprint` | Runtime | 蓝图层：编译器、蓝图视图定义、属性路径、转换函数、事件/条件 |
| `ModelViewViewModelAssetSearch` | Runtime | 资产搜索索引支持 |
| `ModelViewViewModelDebugger` | Runtime | 运行时调试器 |
| `ModelViewViewModelEditor` | Runtime | 编辑器扩展（面板、详情、工具栏） |
| `ModelViewViewModelDebuggerEditor` | Runtime | 调试器的编辑器 UI |

## 蓝图用法

MVVM 的核心交互通过 **View Editor**（蓝图编辑器中的 MVVM 面板）完成，而非直接放置节点。

### 核心概念

| 概念 | 说明 | 关键类 |
|---|---|---|
| ViewModel 上下文 | 定义蓝图使用的 ViewModel 及其实例化方式 | `FMVVMBlueprintViewModelContext` |
| 绑定（Binding） | 源路径到目标路径的数据映射关系 | `FMVVMBlueprintViewBinding` |
| 事件（Event） | 监听 Widget 或 ViewModel 的委托事件 | `UMVVMBlueprintViewEvent` |
| 条件（Condition） | 根据条件值控制 UI 显示/隐藏 | `UMVVMBlueprintViewCondition` |
| 转换函数 | 在绑定源和目标之间转换值 | `UMVVMBlueprintViewConversionFunction` |
| 属性路径 | 描述属性的读写路径 | `FMVVMBlueprintPropertyPath` |

### View 设置

`UMVVMBlueprintViewSettings` 控制视图的初始化行为：

| 属性 | 说明 |
|---|---|
| `bInitializeSourcesOnConstruct` | 构造时自动初始化 ViewModel 源 |
| `bInitializeBindingsOnConstruct` | 构造时自动执行所有绑定 |
| `bInitializeEventsOnConstruct` | 构造时自动初始化事件监听 |
| `bCreateViewWithoutBindings` | 即使没有绑定也创建视图（用于纯 ViewModel 访问） |

### ViewModel 创建类型

`EMVVMBlueprintViewModelContextCreationType` 枚举定义了 ViewModel 的获取方式：

| 类型 | 说明 |
|---|---|
| `Manual` | 手动赋值（通过生成的 Setter 函数） |
| `CreateInstance` | Widget 创建时自动实例化 |
| `GlobalViewModelCollection` | 从全局 ViewModel 注册表获取 |
| `PropertyPath` | 通过属性路径计算获取 |
| `Resolver` | 通过解析器对象获取 |
| `Context` | 从本地上下文提供者获取 |

### 绑定模式

`EMVVMBindingMode` 控制绑定的同步方向和时机，支持：
- **OneTime**：仅初始化时执行一次
- **OneWayToDestination**：源→目标（最常用）
- **OneWayToSource**：目标→源
- **TwoWay**：双向同步

### 使用流程（文字描述）

1. 打开 Widget 蓝图 → 在 MVVM 面板中添加 ViewModel 上下文（选择类、命名）
2. 添加绑定 → 选择源（ViewModel 属性）→ 选择目标（Widget 属性）
3. 可选：添加转换函数处理值映射
4. 可选：添加事件监听（如按钮点击触发数据更新）
5. 可选：添加条件控制 UI 显示状态
6. 编译蓝图 → 编译器自动生成绑定代码
7. 运行时自动执行绑定

## C++ 用法

### 核心类关系

```
UMVVMWidgetBlueprintExtension_View   ← Widget 蓝图扩展入口
    └── UMVVMBlueprintView           ← 蓝图中所有绑定/事件/条件的容器
            ├── FMVVMBlueprintViewModelContext[]  ← ViewModel 定义
            ├── FMVVMBlueprintViewBinding[]       ← 绑定列表
            ├── UMVVMBlueprintViewEvent[]         ← 事件列表
            └── UMVVMBlueprintViewCondition[]     ← 条件列表

UMVVMBlueprintViewConversionFunction  ← 转换函数封装（含包装图生成）
FMVVMBlueprintPropertyPath            ← 属性路径描述
FCompiledBindingLibraryCompiler       ← 绑定库编译器
FMVVMViewBlueprintCompiler            ← 蓝图编译器主逻辑
```

### 基本用法：属性路径

属性路径 `FMVVMBlueprintPropertyPath` 是 MVVM 系统的基础数据结构，描述从 ViewModel/Widget 到具体属性的访问路径。

```cpp
#include "MVVMPropertyPath.h"

// 创建一个从 ViewModel 到属性的路径
FMVVMBlueprintPropertyPath PropertyPath;
PropertyPath.SetViewModelId(MyViewModelId);
PropertyPath.AppendPropertyPath(WidgetBlueprint, FirstField);
PropertyPath.AppendPropertyPath(WidgetBlueprint, SecondField);

// 获取路径信息
TArray<FName> FieldNames = PropertyPath.GetFieldNames(WidgetClass);
TArray<FMVVMConstFieldVariant> Fields = PropertyPath.GetFields(WidgetClass);
```

来源：`Public/MVVMPropertyPath.h`

### 基本用法：ViewModel 上下文

```cpp
#include "MVVMBlueprintViewModelContext.h"

// 创建 ViewModel 上下文
FMVVMBlueprintViewModelContext ViewModelContext;
ViewModelContext.NotifyFieldValueClass = UMyViewModel::StaticClass();
ViewModelContext.ViewModelName = TEXT("PlayerViewModel");
ViewModelContext.CreationType = EMVVMBlueprintViewModelContextCreationType::CreateInstance;

// 也可以使用构造函数
FMVVMBlueprintViewModelContext Context(UMyViewModel::StaticClass(), TEXT("PlayerViewModel"));

// 获取属性
FGuid Id = Context.GetViewModelId();
FName Name = Context.GetViewModelName();
UClass* Class = Context.GetViewModelClass();
```

来源：`Public/MVVMBlueprintViewModelContext.h`

### 基本用法：绑定定义

```cpp
#include "MVVMBlueprintViewBinding.h"

// 创建绑定
FMVVMBlueprintViewBinding Binding;
Binding.SourcePath.SetViewModelId(ViewModelId);
Binding.SourcePath.AppendPropertyPath(Blueprint, HealthField);
Binding.DestinationPath.SetWidgetName(TEXT("HealthBar"));
Binding.DestinationPath.AppendPropertyPath(Blueprint, PercentField);
Binding.BindingType = EMVVMBindingMode::OneWayToDestination;
Binding.bEnabled = true;
Binding.bCompile = true;

// 获取显示名称
FString DisplayName = Binding.GetDisplayNameString(WidgetBlueprint);
```

来源：`Public/MVVMBlueprintViewBinding.h`

### 进阶用法：编译器扩展接口

编译器提供两个阶段的接口，允许扩展注入自定义行为：

```cpp
#include "MVVMBlueprintViewCompilerInterface.h"

// 预编译阶段：添加字段路径、验证绑定
class FMyViewExtension : public UMVVMBlueprintViewExtension
{
    virtual void Precompile(UE::MVVM::Compiler::IMVVMBlueprintViewPrecompile* Compiler,
                            UWidgetBlueprintGeneratedClass* Class) override
    {
        // 获取所有绑定
        TArray<Compiler::FCompilerBindingHandle> Bindings = Compiler->GetAllBindings();
        
        // 获取绑定的读字段路径
        for (auto& Handle : Bindings)
        {
            auto ReadFields = Compiler->GetBindingReadFields(Handle);
            auto WriteFields = Compiler->GetBindingWriteFields(Handle);
        }
        
        // 添加自定义字段路径
        auto Result = Compiler->AddFieldPath(MyFieldPath, /*bRead=*/true);
        if (Result.HasError())
        {
            Compiler->AddMessage(Result.GetError(), Compiler::EMessageType::Error);
        }
        
        // 添加消息（警告会导致编译警告，错误会导致编译失败）
        Compiler->AddMessageForBinding(Handle, 
            FText::FromString(TEXT("Binding has side effects")),
            Compiler::EMessageType::Warning);
    }
    
    // 编译阶段：创建运行时扩展、获取编译后的字段路径
    virtual void Compile(UE::MVVM::Compiler::IMVVMBlueprintViewCompile* Compiler,
                         UWidgetBlueprintGeneratedClass* Class,
                         UMVVMViewClass* ViewExtension) override
    {
        // 获取预编译阶段添加的字段路径的编译结果
        FMVVMVCompiledFieldPath CompiledPath = Compiler->GetFieldPath(MyHandle).GetValue();
        
        // 创建运行时视图类扩展
        UMVVMViewClassExtension* Ext = Compiler->CreateViewClassExtension(
            UMyViewClassExtension::StaticClass());
    }
};
```

来源：`Public/MVVMBlueprintViewCompilerInterface.h`

### 进阶用法：绑定库编译器

`FCompiledBindingLibraryCompiler` 是底层编译器，负责将字段路径和绑定关系编译为运行时数据。

```cpp
#include "Bindings/MVVMCompiledBindingLibraryCompiler.h"

// 创建编译器
FCompiledBindingLibraryCompiler Compiler(Blueprint);

// 添加字段 ID
auto FieldIdResult = Compiler.AddFieldId(UMyViewModel::StaticClass(), TEXT("Health"));

// 添加读字段路径
auto ReadPathResult = Compiler.AddFieldPath(ReadFieldPath, /*bRead=*/true);

// 添加写字段路径
auto WritePathResult = Compiler.AddFieldPath(WriteFieldPath, /*bRead=*/false);

// 添加绑定
auto BindingResult = Compiler.AddBinding(ReadPathResult.GetValue(), WritePathResult.GetValue());

// 添加带转换函数的绑定
auto ConvPathResult = Compiler.AddConversionFunctionFieldPath(
    UObject::StaticClass(), ConversionFunction);
auto ComplexBinding = Compiler.AddBinding(
    ReadPathResult.GetValue(), WritePathResult.GetValue(), ConvPathResult.GetValue());

// 编译
auto CompileResult = Compiler.Compile(LibraryId);
if (CompileResult.HasValue())
{
    FMVVMCompiledBindingLibrary& Library = CompileResult.GetValue().Library;
    auto& FieldPaths = CompileResult.GetValue().FieldPaths;
    auto& Bindings = CompileResult.GetValue().Bindings;
    auto& FieldIds = CompileResult.GetValue().FieldIds;
}
```

来源：`Public/Bindings/MVVMCompiledBindingLibraryCompiler.h`

### 进阶用法：转换函数

转换函数在绑定的源和目标之间进行值转换，支持简单的 UFunction 和复杂的 K2Node。

```cpp
#include "MVVMBlueprintViewConversionFunction.h"
#include "Bindings/MVVMConversionFunctionHelper.h"

// 创建转换函数对象
UMVVMBlueprintViewConversionFunction* ConvFunc = NewObject<UMVVMBlueprintViewConversionFunction>();

// 初始化为一个 UFunction
ConvFunc->InitializeFromFunction(WidgetBlueprint, TEXT("ConvertHealthToColor"), HealthToColorFunction);

// 初始化为一个 K2Node
FMVVMBlueprintFunctionReference FuncRef(MyK2NodeClass);
ConvFunc->Initialize(WidgetBlueprint, TEXT("ConvertNode"), FuncRef);

// 检查是否需要包装图（多参数函数或 K2Node 需要）
bool bNeedsWrapper = ConvFunc->NeedsWrapperGraph(WidgetClass);

// 获取或创建包装图
UEdGraph* WrapperGraph = ConvFunc->GetOrCreateWrapperGraph(WidgetBlueprint);

// 保存/更新引脚值
ConvFunc->SavePinValues(WidgetBlueprint);
ConvFunc->UpdatePinValues(WidgetBlueprint);
```

来源：`Public/MVVMBlueprintViewConversionFunction.h`

## Demo 示例

以下示例展示如何在 C++ 中通过蓝图扩展自定义 MVVM 编译行为：

```cpp
// MyMVVMExtension.h
#pragma once

#include "Extensions/MVVMBlueprintViewExtension.h"
#include "MVVMBlueprintViewCompilerInterface.h"

UCLASS()
class UMyMVVMExtension : public UMVVMBlueprintViewExtension
{
    GENERATED_BODY()

public:
    virtual TArray<UE::MVVM::Compiler::FBlueprintViewUserWidgetProperty> AddProperties() override;
    virtual void Precompile(UE::MVVM::Compiler::IMVVMBlueprintViewPrecompile* Compiler,
                            UWidgetBlueprintGeneratedClass* Class) override;
    virtual void Compile(UE::MVVM::Compiler::IMVVMBlueprintViewCompile* Compiler,
                         UWidgetBlueprintGeneratedClass* Class,
                         UMVVMViewClass* ViewExtension) override;

private:
    UE::MVVM::FCompiledBindingLibraryCompiler::FFieldPathHandle CustomFieldHandle;
};
```

```cpp
// MyMVVMExtension.cpp
#include "MyMVVMExtension.h"

TArray<UE::MVVM::Compiler::FBlueprintViewUserWidgetProperty> UMyMVVMExtension::AddProperties()
{
    TArray<UE::MVVM::Compiler::FBlueprintViewUserWidgetProperty> Properties;
    
    UE::MVVM::Compiler::FBlueprintViewUserWidgetProperty Prop;
    Prop.AuthoritativeClass = GetOuterUClass();
    Prop.Name = TEXT("MyCustomProperty");
    Prop.DisplayName = FText::FromString(TEXT("My Custom Property"));
    Prop.CategoryName = TEXT("Custom");
    Prop.bReadOnly = false;
    Prop.bPrivate = false;
    Properties.Add(Prop);
    
    return Properties;
}

void UMyMVVMExtension::Precompile(
    UE::MVVM::Compiler::IMVVMBlueprintViewPrecompile* Compiler,
    UWidgetBlueprintGeneratedClass* Class)
{
    // 构建自定义字段路径
    TArray<UE::MVVM::FMVVMConstFieldVariant> FieldPath;
    // ... 填充字段路径 ...
    
    auto Result = Compiler->AddFieldPath(FieldPath, true);
    if (Result.HasValue())
    {
        CustomFieldHandle = Result.GetValue();
    }
    else
    {
        Compiler->MarkPrecompileStepInvalid();
    }
}

void UMyMVVMExtension::Compile(
    UE::MVVM::Compiler::IMVVMBlueprintViewCompile* Compiler,
    UWidgetBlueprintGeneratedClass* Class,
    UMVVMViewClass* ViewExtension)
{
    // 获取编译后的字段路径
    auto FieldPathResult = Compiler->GetFieldPath(CustomFieldHandle);
    if (FieldPathResult.HasValue())
    {
        // 使用编译后的字段路径配置运行时扩展
        // ...
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `FieldNotification` | 字段通知系统（`NotifyFieldValueChanged` 接口） |
| `UMG` | UMG 蓝图编辑器和 Widget 基础设施 |
| `KismetCompiler` | 蓝图编译器框架（生成函数、变量） |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `f172f2b0` | MVVMToolset: Initial MVVM toolset plugin that supports creating and modifying Viewmodel via blueprint | 新增 MVVM 工具集插件，支持通过蓝图创建和修改 ViewModel |
| 2026-05-13 | `825be502` | Listview/Panel Extension: use widget blueprint class directly to get the MVVM view during compilation | ListView/Panel 扩展改用 Widget 蓝图类直接获取 MVVM 视图 |
| 2026-05-12 | `21f108ac` | Cherry-pick UMGToolSet | 合入 UMG 工具集相关改动 |
| 2026-04-23 | `e24ce23f` | MVVM: Remove unused USTRUCT specifiers | 清理未使用的 USTRUCT 说明符 |
| 2026-04-22 | `cd8175a0` | MVVM: Resolve invalid transient outer when importing copied conditions and events | 修复导入复制的条件和事件时 transient outer 无效的问题 |

### 维护评价

- **创建时间**：2022 年 4 月，约 4 年历史
- **活跃度**：非常活跃，2026 年 4-5 月有多次功能性更新，包括新工具集和架构改进
- **状态**：Beta 版本（`IsBetaVersion=true`），默认未启用（`EnabledByDefault=false`）
- **已知限制**：
  - Beta 阶段，API 可能在后续版本发生变更（代码中可见大量 `UE_DEPRECATED` 标记）
  - 5.4 版本有重大重构（`FMVVMBlueprintPropertyPath` 源从 Widget/ViewModel 字段改为枚举）
  - 5.5 版本转换函数包装图从持久化改为瞬态
- **推荐**：推荐用于新项目的 UI 架构设计。虽然是 Beta，但 Epic 持续投入开发，且已有多次大版本迭代。生产项目建议做好 API 变更的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ModelViewViewModel)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Runtime/ModelViewViewModel)（如存在）