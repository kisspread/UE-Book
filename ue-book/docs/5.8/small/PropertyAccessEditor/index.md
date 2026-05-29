# Property Access Editor

> Editor support for copying properties from one object to another. Required for Animation and UMG systems to function correctly

| 属性 | 值 |
|---|---|
| 中文名 | 属性访问编辑器 |
| 分类 | Runtime |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `PropertyAccessEditor` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2020-09-01 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/PropertyAccess) | |

## 用途

这个插件的核心用途是**提供一种可视化、类型安全且高性能的机制，用于在蓝图编辑器中配置和编译“属性绑定”**。它解决的是“如何在编辑器中方便地建立从源对象到目标对象的属性复制关系，并在运行时高效执行”的问题。

具体来说，它实现了两个层面的功能：
1.  **编辑器 UI (SPropertyBinding)**: 为动画蓝图、UMG 等需要属性绑定的编辑器面板提供标准的下拉菜单和交互逻辑，用于选择和配置属性路径。
2.  **访问编译器 (FPropertyAccessLibraryCompiler)**: 将用户配置的字符串形式的属性路径（如 `Actor.Location.X`）编译成底层高效的、可缓存的访问句柄（`FCompiledPropertyAccessHandle`）和复制指令（如 `FloatToInt`、`VectorCopy` 等），供运行时动画和 UMG 系统使用。

没有这个插件，动画状态机、UMG 控件的数据绑定等关键功能将无法正常工作。

## 使用场景

-   **动画蓝图开发者**：在动画蓝图的事件图表或状态机中，为变量或节点设置“绑定”，将其他对象（如角色、组件）的属性直接映射过来。
-   **UMG 界面设计师**：在 UMG 控件的“细节”面板中，使用“绑定”功能将控件属性（如文本、颜色）与游戏数据源（如玩家生命值、物品名称）动态关联。
-   **任何需要跨对象属性复制的系统**：需要在编辑器中配置复杂属性访问路径，并希望运行时有高性能解决方案的场景。

## 蓝图用法

此插件主要提供编辑器内的 UI 和逻辑，不直接暴露为蓝图节点给游戏逻辑使用。其核心交互（选择属性路径的下拉菜单）是通过 `SPropertyBinding` 控件在特定编辑器面板（如动画蓝图、UMG 设计器）中隐式呈现的。

### 核心节点

此插件没有 `UFUNCTION(BlueprintCallable)` 节点。其蓝图用法体现在其他系统（动画、UMG）提供的“绑定”属性上。开发者通过这些属性的编辑器 UI（由本插件驱动）来配置绑定。

**相关底层结构 (C++)：**
| 结构/类 | 说明 |
|---|---|
| `FPropertyBindingWidgetArgs` | 用于配置 `SPropertyBinding` 控件外观和行为的参数集 |
| `FBindingChainElement` | 表示属性路径中的一个片段（如一个属性名、一个函数名） |
| `IPropertyAccessLibraryCompiler` | 属性访问编译器的接口 |

### 使用示例（蓝图描述）

1.  打开一个**动画蓝图**，在事件图表中右键，选择 `Set (Variable) ...`。
2.  在变量的 `Details` 面板中，找到要设置的属性（如 `Location`），点击旁边的下拉菜单（链状图标）。
3.  这个下拉菜单就是由 `SPropertyBinding` 控件生成的。菜单中会列出当前蓝图可访问的上下文结构（如 `Pawn`、`PlayerController`）及其属性。
4.  选择一条路径，如 `Pawn > Get Movement Component > Velocity`，即完成绑定配置。运行时，系统会使用编译后的指令高效复制该路径的值。

## C++ 用法

### 头文件引入

```cpp
#include "PropertyAccessEditor.h" // 包含访问编译器和辅助函数
#include "SPropertyBinding.h"     // 如果需要创建自定义的属性绑定控件
```

### 基本用法

**1. 解析属性路径**
此功能常用于编辑器工具中验证用户输入的路径是否有效。
```cpp
// 来源: PropertyAccessEditor.h
#include "PropertyAccessEditor.h"

void MyFunction()
{
    UStruct* MyStruct = AMyActor::StaticClass(); // 或某个 UObject 的类
    TArray<FString> Path = {TEXT("bIsAlive")};

    FProperty* FoundProperty = nullptr;
    int32 ArrayIndex = INDEX_NONE;
    FPropertyAccessResolveResult Result = PropertyAccess::ResolvePropertyAccess(MyStruct, Path, FoundProperty, ArrayIndex);

    if (Result == EPropertyAccessResolveResult::Success)
    {
        // FoundProperty 指向了 AMyActor::bIsAlive 属性
        UE_LOG(LogTemp, Log, TEXT("成功解析属性: %s"), *FoundProperty->GetName());
    }
}
```

**2. 获取属性兼容性**
在实现自定义绑定逻辑时，判断两个属性类型是否可以互相赋值。
```cpp
// 来源: PropertyAccessEditor.h
FProperty* FloatProp = FFloatProperty::StaticClass(); // 假设
FProperty* DoubleProp = FDoubleProperty::StaticClass(); // 假设

EPropertyAccessCompatibility Compat = PropertyAccess::GetPropertyCompatibility(FloatProp, DoubleProp);
// Compat 将是 EPropertyAccessCompatibility::Compatible
```

### 进阶用法

**使用 `FPropertyAccessLibraryCompiler` 编译绑定**
这是插件的核心，用于将一整套属性复制规则编译成高效的运行时表示。
```cpp
// 来源: PropertyAccessEditor.h
#include "PropertyAccessEditor.h"

// 假设我们有一个 FPropertyAccessLibrary* Library， 一个 UClass* OwnerClass
FPropertyAccessLibraryCompiler Compiler(Library, OwnerClass, /* InOnDetermineBatchId */ FOnPropertyAccessDetermineBatchId());

// 1. 开始编译
Compiler.BeginCompilation();

// 2. 添加一个复制规则：从 `Pawn.Location` 复制到 `CachedLocation`
TArray<FString> SourcePath = {TEXT("Pawn"), TEXT("GetActorLocation")};
TArray<FString> DestPath = {TEXT("CachedLocation")};
FPropertyAccessHandle CopyHandle = Compiler.AddCopy(SourcePath, DestPath, NAME_None);

// 3. 添加一个只读访问规则：获取 `Pawn.Health`
TArray<FString> AccessPath = {TEXT("Pawn"), TEXT("GetHealth")};
FPropertyAccessHandle AccessHandle = Compiler.AddAccess(AccessPath);

// 4. 结束编译，生成最终的高效指令集
bool bSuccess = Compiler.FinishCompilation();

if (bSuccess)
{
    // 获取编译后的句柄，用于运行时访问
    FCompiledPropertyAccessHandle CompiledCopy = Compiler.GetCompiledHandle(CopyHandle);
    FCompiledPropertyAccessHandle CompiledAccess = Compiler.GetCompiledHandle(AccessHandle);

    // 运行时系统可以使用这些 Compiled 句柄快速获取或设置属性值
}
else
{
    // 编译失败，迭代错误信息
    Compiler.IterateErrors([](const FText& Error, UObject* AssociatedObject)
    {
        UE_LOG(LogTemp, Error, TEXT("属性访问编译错误: %s - 关联对象: %s"), *Error.ToString(), *GetNameSafe(AssociatedObject));
    });
}
```

## Demo 示例

以下示例展示如何在一个自定义编辑器工具中，使用插件提供的 API 解析属性路径并编译一个简单的绑定。

```cpp
// MyPropertyAccessTool.h
#pragma once
#include "CoreMinimal.h"
#include "PropertyAccessEditor.h" // 引入插件头文件

class UMyPropertyAccessTool
{
public:
    void RunDemo(UBlueprint* InBlueprint);

private:
    FPropertyAccessLibrary DemoLibrary;
};
```

```cpp
// MyPropertyAccessTool.cpp
#include "MyPropertyAccessTool.h"
#include "Kismet2/BlueprintEditorUtils.h"

void UMyPropertyAccessTool::RunDemo(UBlueprint* InBlueprint)
{
    if (!InBlueprint) return;

    UClass* BlueprintClass = InBlueprint->GeneratedClass;
    if (!BlueprintClass) return;

    // 1. 创建编译器
    FPropertyAccessLibraryCompiler Compiler(&DemoLibrary, BlueprintClass, FOnPropertyAccessDetermineBatchId());

    // 2. 开始编译
    Compiler.BeginCompilation();

    // 3. 定义并添加一个从蓝图自身变量 `PlayerName` 到 `DisplayText` 的复制
    TArray<FString> Source = {TEXT("PlayerName")};
    TArray<FString> Dest = {TEXT("DisplayText")};
    FPropertyAccessHandle CopyHandle = Compiler.AddCopy(Source, Dest, NAME_None);

    // 4. 完成编译
    if (Compiler.FinishCompilation())
    {
        UE_LOG(LogTemp, Display, TEXT("Demo: 属性访问库编译成功。"));

        // 获取编译句柄，可保存或传递给运行时组件
        FCompiledPropertyAccessHandle CompiledHandle = Compiler.GetCompiledHandle(CopyHandle);
        if (CompiledHandle.IsValid())
        {
            UE_LOG(LogTemp, Display, TEXT("Demo: 已获得编译句柄，类型: %s"),
                LexToString(Compiler.GetCompiledHandleAccessType(CopyHandle)));
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Demo: 编译失败，错误信息:"));
        Compiler.IterateErrors([](const FText& Error, UObject* Obj)
        {
            UE_LOG(LogTemp, Warning, TEXT("  - %s"), *Error.ToString());
        });
    }
}
```

## 模块依赖

根据 `PropertyAccessEditor.Build.cs` 以及代码分析，使用此插件时，你的模块需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `AnimationCore` | 提供动画系统核心类型，是绑定动画属性的基础 |
| `PropertyAccess` | 提供运行时属性访问库（`FPropertyAccessLibrary`），是本插件编辑器功能的运行时对应物 |
| `AnimationBlueprintLibrary` | （可选）用于与动画蓝图交互的实用功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-10-15 | `92ec7c47` | - Fix display name of conversion functions in the details panel, in order to display a friendly name | 修复详情面板中转换函数的显示名称，使其更友好 |
| 2025-10-15 | `2b3b0a79` | Fix PropertyName captured by reference | 修复属性名被引用捕获的潜在问题 |
| 2025-10-14 | `4c55c01b` | Expose function for generating property access menus to property access editor | 将生成属性访问菜单的函数暴露给属性访问编辑器 |
| 2025-09-18 | `55e74f4b` | Quick binding support, for UEFN: | 为 UEFN（堡垒之夜编辑器）添加快速绑定支持 |
| 2025-05-15 | `bc444b6e` | StateTree: Support binding on array element. | StateTree（状态树）支持在数组元素上进行绑定 |

### 维护评价

-   **维护状态**: **活跃维护中**。插件自 2020 年创建以来持续有更新，尤其在 2025 年下半年仍有频繁的功能性提交，表明 Epic 官方在持续维护并扩展其能力（如支持 UEFN、StateTree）。
-   **功能重要性**: 属于 **核心基础设施**。动画蓝图、UMG 和 StateTree 等主要系统的属性绑定功能都依赖于此插件。
-   **推荐使用**: **强烈推荐**。任何涉及到在蓝图编辑器中配置跨对象属性传递的场景，都会直接或间接用到此插件提供的功能。它稳定且是官方实现。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/PropertyAccess)
-   [运行时对应物 `PropertyAccess` 插件源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/PropertyAccess/Source/PropertyAccess) (提供 `FPropertyAccessLibrary` 等运行时类)
-   **测试用例**: 未在插件目录内发现专用测试文件。相关测试逻辑可能位于 `Engine/Tests/` 或依赖此插件的其他系统（如 Animation、UMG）的测试中。