# Property Access Editor

> Editor support for copying properties from one object to another. Required for Animation and UMG systems to function correctly

| 属性 | 值 |
|---|---|
| 分类 | Runtime |
| 默认启用 | ✅ Yes |
| 包含内容 | ❌ No |
| 模块 | PropertyAccessEditor (UncookedOnly, PreDefault) |
| 创建时间 | 2020-09-09 |
| 年龄标签 | 👴 老古董 (>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/PropertyAccess) | |

## 用途

PropertyAccessEditor 为 UE 的**属性访问（Property Access）系统**提供编辑器侧支持。属性访问系统是 UE 内部一套通用的「属性路径解析 → 属性值拷贝」管线，被 **AnimBP（动画蓝图）** 和 **UMG（UI 框架）** 等子系统广泛使用。

这个 plugin 的核心工作是：

1. **解析属性路径**：将形如 `"Transform.Rotation"` 或 `"ArrayProperty[2].Name"` 的字符串路径解析为引擎内部的 `FProperty` 引用，支持跨越结构体、对象引用、函数调用等多级导航。
2. **属性兼容性检查**：判断两个属性类型之间是否可以直接拷贝、需要类型提升（promotion），还是完全不兼容。
3. **编译属性访问库**：将一组 source→dest 属性拷贝规则编译为 `FPropertyAccessLibrary`，供运行时高效执行。
4. **属性绑定 UI 控件**：提供 `SPropertyBinding` Slate 控件，让编辑器用户可以通过下拉菜单可视化地选择要绑定的属性路径。

## 使用场景

- 你在做动画蓝图，需要将一个变量绑定到 AnimGraph 节点的某个参数上 → PropertyAccessEditor 提供了属性路径解析和绑定 UI
- 你在做 UMG 控件，需要将数据模型的某个字段绑定到 UI 属性上 → 同样使用属性访问系统
- 你需要在编辑器工具中判断两个 `FProperty` 是否兼容、能否自动转换 → 使用 `GetPropertyCompatibility`
- 你正在开发 StateTree 或自定义 K2 节点，需要编译一组属性拷贝规则 → 使用 `FPropertyAccessLibraryCompiler`

## 蓝图用法

此 plugin 不提供蓝图节点。它是一个**编辑器基础设施模块**，提供 Slate UI 控件和 C++ API 供其他编辑器模块（如动画蓝图编辑器、UMG 编辑器）调用。用户在编辑器中通过属性绑定下拉菜单间接使用它。

## C++ 用法

### 头文件引入

```cpp
#include "IPropertyAccessEditor.h"
```

接口头文件位于 `Engine/Source/Editor/UnrealEd/Public/IPropertyAccessEditor.h`。

### 获取模块实例

通过 `IModularFeatures` 获取 singleton 实例：

```cpp
#include "Features/IModularFeatures.h"

IPropertyAccessEditor& PropertyAccessEditor = 
    FModuleManager::GetModuleChecked<IPropertyAccessEditor>("PropertyAccessEditor");
```

### 解析属性路径

将字符串路径解析为属性和数组索引：

```cpp
// 解析 "Transform.Scale.X" 到 FProperty*
const UStruct* Struct = MyObject->GetClass();
TArray<FString> Path = { TEXT("Transform"), TEXT("Scale"), TEXT("X") };

FProperty* Property = nullptr;
int32 ArrayIndex = INDEX_NONE;

FPropertyAccessResolveResult Result = PropertyAccessEditor.ResolvePropertyAccess(
    Struct, Path, Property, ArrayIndex);

if (Result.Result != EPropertyAccessResolveResult::Failed)
{
    // Property 指向最终叶子属性, ArrayIndex 可用
    UE_LOG(LogTemp, Log, TEXT("Resolved to: %s (thread safe: %d)"),
        *Property->GetName(), Result.bIsThreadSafe);
}
```

### 带回调的属性路径解析

在解析过程中逐段回调，适用于需要构建 UI 显示名称等场景：

```cpp
IPropertyAccessEditor::FResolvePropertyAccessArgs ResolveArgs;

ResolveArgs.PropertyFunction = [](int32 SegmentIndex, FProperty* Property, int32 ArrayIndex)
{
    UE_LOG(LogTemp, Log, TEXT("Segment %d: Property '%s'"),
        SegmentIndex, *Property->GetName());
};

ResolveArgs.FunctionFunction = [](int32 SegmentIndex, UFunction* Function, FProperty* ReturnProperty)
{
    UE_LOG(LogTemp, Log, TEXT("Segment %d: Function '%s'"),
        SegmentIndex, *Function->GetName());
};

ResolveArgs.ArrayFunction = [](int32 SegmentIndex, FArrayProperty* Property, int32 ArrayIndex)
{
    UE_LOG(LogTemp, Log, TEXT("Segment %d: Array '%s'[%d]"),
        SegmentIndex, *Property->GetName(), ArrayIndex);
};

PropertyAccessEditor.ResolvePropertyAccess(Struct, Path, ResolveArgs);
```

### 检查属性兼容性

```cpp
FProperty* PropA = ...; // 源属性
FProperty* PropB = ...; // 目标属性

EPropertyAccessCompatibility Compat = 
    PropertyAccessEditor.GetPropertyCompatibility(PropA, PropB);

switch (Compat)
{
case EPropertyAccessCompatibility::Compatible:
    // 可以直接拷贝
    break;
case EPropertyAccessCompatibility::Promotable:
    // 需要类型提升 (如 float → double, bool → int)
    break;
case EPropertyAccessCompatibility::Incompatible:
    // 不兼容，无法拷贝
    break;
}
```

### 创建属性绑定控件

```cpp
// 基于 Blueprint 的绑定控件
FPropertyBindingWidgetArgs Args;
Args.bAllowPropertyBindings = true;
Args.bAllowFunctionBindings = true;
Args.bAllowArrayElementBindings = true;
Args.MaxDepth = 8;

Args.OnAddBinding = FOnAddBinding::CreateLambda(
    [this](FName PropertyName, const TArray<FBindingChainElement>& Chain)
    {
        // 处理绑定添加
    });

Args.OnCanBindProperty = FOnCanBindProperty::CreateLambda(
    [this](FProperty* Property) -> bool
    {
        // 过滤可绑定的属性
        return true;
    });

TSharedRef<SWidget> Widget = PropertyAccessEditor.MakePropertyBindingWidget(
    MyBlueprint, Args);

// 基于 BindingContextStruct 的绑定控件 (无 Blueprint 依赖)
TArray<FBindingContextStruct> ContextStructs;
ContextStructs.Add(FBindingContextStruct(MyUStruct, nullptr, 
    NSLOCTEXT("MyContext", "MyStruct", "My Struct")));

TSharedRef<SWidget> Widget2 = PropertyAccessEditor.MakePropertyBindingWidget(
    ContextStructs, Args);
```

### 编译属性访问库

```cpp
FPropertyAccessLibrary Library;
const UClass* MyClass = MyObject->GetClass();

FPropertyAccessLibraryCompilerArgs CompilerArgs(Library, MyClass);
// 可选：设置 batch ID 回调用于分批执行
CompilerArgs.OnDetermineBatchId = FOnPropertyAccessDetermineBatchId::CreateLambda(
    [](const FPropertyAccessCopyContext& Context) -> int32
    {
        return 0; // 所有拷贝放在 batch 0
    });

TUniquePtr<IPropertyAccessLibraryCompiler> Compiler = 
    PropertyAccessEditor.MakePropertyAccessCompiler(CompilerArgs);

Compiler->BeginCompilation();

// 添加 source→dest 拷贝规则
TArray<FString> SrcPath = { TEXT("MyFloatVar") };
TArray<FString> DestPath = { TEXT("TargetProperty") };
FPropertyAccessHandle Handle = Compiler->AddCopy(SrcPath, DestPath, NAME_None, MyNode);

// 添加单独的属性访问（只读取）
TArray<FString> AccessPath = { TEXT("Transform"), TEXT("Translation") };
FPropertyAccessHandle AccessHandle = Compiler->AddAccess(AccessPath, MyNode);

if (Compiler->FinishCompilation())
{
    // 编译成功，Library 中包含了编译后的路径段和拷贝规则
    FCompiledPropertyAccessHandle CompiledHandle = Compiler->GetCompiledHandle(Handle);
}

// 检查编译错误
Compiler->IterateErrors([](const FText& Error, UObject* Object)
{
    UE_LOG(LogTemp, Error, TEXT("Property access error: %s"), *Error.ToString());
});
```

### 生成路径文本表示

```cpp
// 从绑定链生成字符串路径
TArray<FBindingChainElement> Chain;
Chain.Add(FBindingChainElement(SomeProperty));
Chain.Add(FBindingChainElement(InnerProperty, 2)); // 带数组索引

TArray<FString> StringPath;
PropertyAccessEditor.MakeStringPath(Chain, StringPath);
// StringPath = { "SomeProperty", "InnerProperty[2]" }

// 从字符串路径生成可读文本
TArray<FString> Path = { TEXT("Transform"), TEXT("Rotation") };
FText TextPath = PropertyAccessEditor.MakeTextPath(Path, MyStruct);
// TextPath = "Transform.Rotation" (如果提供 Struct，会使用显示名称)
```

## Demo 示例

以下是一个最小的编辑器模块示例，演示如何使用 PropertyAccessEditor 解析属性路径并创建绑定控件：

```cpp
// MyEditorModule.Build.cs
using UnrealBuildTool;

public class MyEditorModule : ModuleRules
{
    public MyEditorModule(ReadOnlyTargetRules Target) : base(Target)
    {
        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "UnrealEd",          // IPropertyAccessEditor 在此模块
        });
    }
}
```

```cpp
// MyEditorModule.h
#pragma once

#include "Modules/ModuleManager.h"

class FMyEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// MyEditorModule.cpp
#include "MyEditorModule.h"
#include "IPropertyAccessEditor.h"
#include "Features/IModularFeatures.h"

void FMyEditorModule::StartupModule()
{
    // 检查 PropertyAccessEditor 是否可用
    if (FModuleManager::Get().IsModuleLoaded("PropertyAccessEditor"))
    {
        IPropertyAccessEditor& PAEditor = 
            FModuleManager::GetModuleChecked<IPropertyAccessEditor>("PropertyAccessEditor");

        // 解析一个属性路径
        USomeClass* CDO = GetDefault<USomeClass>();
        TArray<FString> Path = { TEXT("MyFloatProperty") };
        FProperty* Property = nullptr;
        int32 ArrayIndex = INDEX_NONE;

        auto Result = PAEditor.ResolvePropertyAccess(
            CDO->GetClass(), Path, Property, ArrayIndex);
        
        if (Result.Result == EPropertyAccessResolveResult::Succeeded)
        {
            UE_LOG(LogTemp, Log, TEXT("Resolved: %s"), *Property->GetName());
        }
    }
}

void FMyEditorModule::ShutdownModule()
{
}

IMPLEMENT_MODULE(FMyEditorModule, MyEditorModule)
```

## 模块依赖

从 `PropertyAccessEditor.Build.cs` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | 引擎核心基础库 |
| `CoreUObject` | UObject 系统、反射、属性系统 |
| `Slate` | Slate UI 框架 |
| `GraphEditor` | 蓝图编辑器图节点支持 (Private) |
| `BlueprintGraph` | 蓝图图系统 (Private) |
| `Engine` | 引擎核心运行时 (Private) |
| `UnrealEd` | 编辑器框架，包含 `IPropertyAccessEditor` 接口 (Private) |
| `SlateCore` | Slate 核心样式和类型 (Private) |
| `InputCore` | 输入系统 (Private) |
| `KismetWidgets` | K2 蓝图相关控件 (Private) |
| `PropertyPath` | 属性路径解析辅助工具 (Private) |
| `AnimGraph` | 动画图系统支持 (Private) |

> **注意**：此模块类型为 `UncookedOnly`，仅在编辑器和未打包构建中加载。如果你的模块需要使用 `IPropertyAccessEditor` 接口，依赖 `UnrealEd` 即可。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-10-15 | `d096fc80` | Fix display name of conversion functions in details panel, small padding tweak | UI 修复：属性绑定控件中转换函数的显示名称从内部名改为友好名，并调整了控件内边距 |
| 2025-09-23 | `c56b11d4` | Quick binding support for UEFN | 为 UEFN 添加快速绑定功能：点击链接图标时直接显示属性选择器菜单，仅显示兼容类型 |
| 2025-05-15 | `bc444b6e` | StateTree: Support binding on array element | 为 StateTree 添加数组元素绑定支持，修复 UE-259498 |

### 维护评价

- **年龄**：创建于 2020 年 9 月，约 5.6 年历史
- **活跃度**：**活跃维护** — 最近一次更新在 2025 年 10 月，且近 3 次提交都是功能性更新
- **更新趋势**：持续增加新的绑定场景支持（UEFN、StateTree 数组元素绑定），UI 体验持续改进
- **重要性**：作为 AnimBP 和 UMG 的底层基础设施，属于「不会废弃」的核心模块
- **是否推荐使用**：✅ 推荐。这是 UE 属性绑定系统的标准编辑器实现，如果你正在开发需要属性路径解析或绑定 UI 的编辑器工具，这是唯一的选择

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/PropertyAccess)
- [IPropertyAccessEditor 接口头文件](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Editor/UnrealEd/Public/IPropertyAccessEditor.h)
- 测试用例：未发现独立测试文件
