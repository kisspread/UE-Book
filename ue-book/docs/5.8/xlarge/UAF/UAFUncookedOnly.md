# Unreal Animation Framework (UAF)

> Framework for defining functional data flow for animation systems（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 虚幻动画框架 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `UAF` (Runtime), `UAFEditor` (Runtime), `UAFTestData` (Runtime), `UAFUncookedOnly` (Runtime), `UAFTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-26 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF) | |

## 用途

UAF（Unreal Animation Framework）是 Epic Games 为 Unreal Engine 5 打造的**下一代动画系统框架**，其前身为 AnimNext 插件。该框架的核心设计理念是通过**数据流图（RigVM Graph）**来定义动画逻辑，取代传统的 C++ 继承树或蓝图事件链。

具体来说，UAF 解决了以下问题：

1. **动画逻辑的数据驱动化**：将动画状态机、参数绑定、事件处理等全部抽象为可编辑的图（Graph），通过 RigVM 虚拟机执行
2. **变量的统一管理**：提供共享变量（SharedVariables）机制，支持跨资产、跨 C++ 结构体的变量共享与绑定
3. **可编程的编译管线**：通过多阶段编译上下文（FunctionHeader → Variable → Graph → Process），允许子资产在编译过程中动态注入函数头、变量和图
4. **绑定系统**：通过 Universal Object Locator（UOL）将图变量绑定到游戏世界中的实际对象属性/函数，实现运行时数据驱动

该框架主要面向**动画工程师和工具程序员**，让他们能够构建复杂、可复用、可组合的动画系统，而非编写一次性 C++ 代码。

## 使用场景

- 你需要构建一个复杂的动画状态机系统，且希望用可视化编辑器而非纯代码管理 → 用 UAF System
- 你需要在多个动画模块之间共享参数（如移动速度、瞄准方向）→ 用 UAF SharedVariables
- 你需要将动画变量绑定到游戏对象的实际属性（通过 UOL）→ 用变量绑定系统
- 你需要自定义动画编译流程，在编译阶段动态注入图或变量 → 用编译上下文 API
- 你在开发需要运行时数据驱动的动画系统，且希望图中的变量能自动反映游戏状态 → 用 UAF 组件

## 蓝图用法

UAF 的蓝图 API 主要集中在 **UAF 资产管理库** 和 **组件输入/输出节点**。

### 核心节点

#### 资产条目管理（UUAFRigVMAssetLibrary）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FindEntry` | 在 UAF 资产中按名称查找条目 | `UUAFRigVMAssetLibrary` |
| `AddVariable` | 向 UAF 资产添加一个变量条目 | `UUAFRigVMAssetLibrary` |
| `AddEventGraph` | 向 UAF 资产添加一个事件图条目 | `UUAFRigVMAssetLibrary` |
| `AddSharedVariables` | 向 UAF 资产添加共享变量引用 | `UUAFRigVMAssetLibrary` |
| `AddSharedVariablesStruct` | 向 UAF 资产添加基于 C++ 结构体的共享变量 | `UUAFRigVMAssetLibrary` |
| `AddFunction` | 向 UAF 资产添加一个函数图 | `UUAFRigVMAssetLibrary` |
| `AddCategory` | 向 UAF 资产添加一个分类 | `UUAFRigVMAssetLibrary` |
| `RenameCategory` | 重命名 UAF 资产中的分类 | `UUAFRigVMAssetLibrary` |
| `RemoveCategory` | 移除 UAF 资产中的分类 | `UUAFRigVMAssetLibrary` |
| `RemoveEntry` | 从 UAF 资产移除单个条目 | `UUAFRigVMAssetLibrary` |
| `RemoveEntries` | 从 UAF 资产移除多个条目 | `UUAFRigVMAssetLibrary` |
| `RemoveAllEntries` | 移除 UAF 资产中的所有条目 | `UUAFRigVMAssetLibrary` |
| `RenameVariable` | 重命名变量并更新项目中所有引用 | `UUAFRigVMAssetLibrary` |

#### RigVM 控制器扩展（UAnimNextControllerBase）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddAssetSharedVariableNode` | 从资产添加共享变量节点到图中 | `UAnimNextControllerBase` |
| `AddStructSharedVariableNode` | 从 C++ 结构体添加共享变量节点到图中 | `UAnimNextControllerBase` |
| `AddSharedVariableNode` | 从源对象路径添加共享变量节点 | `UAnimNextControllerBase` |
| `RefreshSharedVariableNode` | 刷新共享变量节点的数据 | `UAnimNextControllerBase` |
| `AddUnitNodeOfClass` | 向图添加函数/结构体节点 | `UAnimNextControllerBase` |

#### 组件变量访问（蓝图 K2 节点）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetVariable` | 从 UAF 组件获取变量值 | `UK2Node_UAFComponentGetVariable` |
| `SetVariable` | 向 UAF 组件设置变量值 | `UK2Node_AnimNextComponentSetVariable` |
| `SetInputBinding` | 设置 UAF 组件的动态输入绑定 | `UK2Node_UAFComponentSetInputBinding` |

### 使用示例（蓝图描述）

**在蓝图中向 UAF 资产添加变量并设置默认值：**

1. 获取一个 `UUAFRigVMAsset` 对象引用
2. 调用 `UUAFRigVMAssetLibrary::AddVariable` 节点，传入资产引用、变量名、值类型（如 `Float`）、默认值字符串
3. 返回值为 `UAnimNextVariableEntry*`，可进一步配置其绑定或分类

**在蓝图中从 UAF 组件读取/写入变量：**

1. 拥有一个 `UAFComponent`（动画组件）引用
2. 使用 `UK2Node_UAFComponentGetVariable` 节点，连接组件引脚，选择目标变量名，输出即为变量当前值
3. 使用 `UK2Node_AnimNextComponentSetVariable` 节点连接组件和值引脚来设置变量

## C++ 用法

### 头文件引入

```cpp
// 模块接口
#include "IAnimNextUncookedOnlyModule.h"

// 资产编辑数据
#include "AnimNextRigVMAssetEditorData.h"

// 控制器扩展
#include "AnimNextControllerBase.h"

// 变量接口
#include "Variables/IAnimNextRigVMVariableInterface.h"

// 编译作用域
#include "UAFCompilationScope.h"

// 导出数据
#include "AnimNextExports.h"
```

### 基本用法

**获取模块实例并注册变量绑定类型：**

```cpp
// 来源: Internal/AnimNextUncookedOnlyModule.h
#include "IAnimNextUncookedOnlyModule.h"

using namespace UE::UAF::UncookedOnly;

// 获取 UncookedOnly 模块
IAnimNextUncookedOnlyModule& Module = IAnimNextUncookedOnlyModule::Get();

// 注册自定义变量绑定类型
// InStructName 必须是 FAnimNextVariableBindingData 的子结构体
Module.RegisterVariableBindingType(MyBindingStruct->GetFName(), MakeShared<FMyBindingType>());
```

**向 UAF 资产添加变量和事件图（通过库函数）：**

```cpp
// 来源: Internal/AnimNextRigVMAssetEditorData.h
#include "AnimNextRigVMAssetEditorData.h"

UUAFRigVMAsset* Asset = ...;

// 添加一个浮点变量
UAnimNextVariableEntry* VarEntry = UUAFRigVMAssetLibrary::AddVariable(
    Asset,
    FName("MoveSpeed"),            // 变量名
    EPropertyBagPropertyType::Float, // 值类型
    EPropertyBagContainerType::None, // 容器类型
    nullptr,                         // 值类型对象
    TEXT("600.0"),                   // 默认值
    true                             // 支持撤销
);

// 添加一个事件图
UScriptStruct* EventStruct = FMyAnimEvent::StaticStruct();
UAnimNextEventGraphEntry* EventGraph = UUAFRigVMAssetLibrary::AddEventGraph(
    Asset,
    FName("OnHitReact"),
    EventStruct
);

// 添加共享变量引用
UUAFSharedVariables* SharedVars = ...;
UUAFSharedVariablesEntry* SharedEntry = UUAFRigVMAssetLibrary::AddSharedVariables(
    Asset,
    SharedVars
);
```

**通过控制器扩展向图中添加共享变量节点：**

```cpp
// 来源: Internal/AnimNextControllerBase.h
UAnimNextControllerBase* Controller = ...;
const UUAFSharedVariables* SharedVarsAsset = ...;

// 从资产添加共享变量 getter 节点
UUAFSharedVariableNode* Node = Controller->AddAssetSharedVariableNode(
    SharedVarsAsset,
    FName("Health"),              // 变量名
    TEXT("float"),                // CPP 类型
    nullptr,                      // CPP 类型对象
    true,                         // bIsGetter
    TEXT("100.0"),                // 默认值
    FVector2D(100, 200)           // 位置
);
```

### 进阶用法

**使用编译作用域批量编译 UAF 资产：**

```cpp
// 来源: Public/UAFCompilationScope.h
#include "UAFCompilationScope.h"

using namespace UE::UAF::UncookedOnly;

// 方式1: 带名称的编译范围
{
    FCompilationScope Scope(FText::FromString(TEXT("CompileAll")));
    // 在此范围内编译的资产会在 scope 退出时统一重新分配
    Compilation::RequestAssetCompilation(MyAsset);
}

// 方式2: 直接传入资产
{
    FCompilationScope Scope(MyAsset);
    // 资产在 scope 析构时自动完成重分配
}

// 方式3: 批量编译
TArray<UUAFRigVMAsset*> Assets = { Asset1, Asset2, Asset3 };
{
    FCompilationScope Scope(FText::FromString(TEXT("BatchCompile")), Assets);
    for (UUAFRigVMAsset* Asset : Assets)
    {
        Compilation::RequestAssetCompilation(Asset);
    }
}
```

**在自定义资产的编译阶段注入程序化图和变量：**

```cpp
// 来源: Internal/Compilation/AnimNextGetVariableCompileContext.h, AnimNextGetGraphCompileContext.h
// 这是子类化 UUAFRigVMAssetEditorData 时重写的编译钩子

void UMyCustomAsset_EditorData::OnPreCompileGetProgrammaticVariables(
    const FRigVMCompileSettings& InSettings,
    FAnimNextGetVariableCompileContext& OutCompileContext)
{
    // 动态注入一个程序化变量
    FAnimNextProgrammaticVariable ProgVar;
    ProgVar.Name = FName("InjectedParam");
    ProgVar.SetType(FAnimNextParamType::GetType<float>());
    ProgVar.SetDefaultValueFromString(TEXT("1.0"));
    
    OutCompileContext.GetMutableProgrammaticVariables().Add(ProgVar);
}

void UMyCustomAsset_EditorData::OnPreCompileGetProgrammaticGraphs(
    const FRigVMCompileSettings& InSettings,
    FAnimNextGetGraphCompileContext& OutCompileContext)
{
    // 通过 FUtils 辅助创建事件图
    URigVMController* Controller = ...;
    UE::UAF::UncookedOnly::FUtils::SetupEventGraph(
        Controller,
        FMyEvent::StaticStruct(),
        FName("OnMyEvent")
    );
    OutCompileContext.GetMutableProgrammaticGraphs().Add(Controller->GetGraph());
}
```

**通过 UOL 将变量绑定到游戏对象：**

```cpp
// 来源: Internal/Variables/AnimNextUniversalObjectLocatorBindingData.h
// 设置一个 UOL 绑定数据，将变量绑定到目标对象的属性
FAnimNextUniversalObjectLocatorBindingData BindingData;
BindingData.Type = FAnimNextUniversalObjectLocatorBindingType::Property;
BindingData.Property = TFieldPath<FProperty>(SomeProperty);
BindingData.Locator = FUniversalObjectLocator(...); // 设置定位器

// 将绑定应用到变量条目
FAnimNextVariableBinding Binding;
Binding.BindingData.InitializeAs<FAnimNextUniversalObjectLocatorBindingData>(BindingData);
VariableEntry->SetBinding(MoveTemp(Binding));
```

## Demo 示例

**最小示例：创建一个自定义 UAF 编辑数据类，注入编译阶段变量**

```cpp
// MyCustomAsset_EditorData.h
#pragma once

#include "AnimNextRigVMAssetEditorData.h"
#include "AnimNextGetVariableCompileContext.h"
#include "AnimNextGetGraphCompileContext.h"
#include "MyCustomAsset_EditorData.generated.h"

UCLASS(MinimalAPI)
class UMyCustomAsset_EditorData : public UUAFRigVMAssetEditorData
{
    GENERATED_BODY()

protected:
    // 指定使用的执行上下文结构体
    virtual UScriptStruct* GetExecuteContextStruct() const override
    {
        return FAnimNextExecuteContext::StaticStruct();
    }

    // 指定允许的条目类型
    virtual TConstArrayView<TSubclassOf<UUAFRigVMAssetEntry>> GetEntryClasses() const override;

    // 在编译阶段注入程序化变量
    virtual void OnPreCompileGetProgrammaticVariables(
        const FRigVMCompileSettings& InSettings,
        FAnimNextGetVariableCompileContext& OutCompileContext) override;
    
    // 在编译阶段注入程序化图
    virtual void OnPreCompileGetProgrammaticGraphs(
        const FRigVMCompileSettings& InSettings,
        FAnimNextGetGraphCompileContext& OutCompileContext) override;
};
```

```cpp
// MyCustomAsset_EditorData.cpp
#include "MyCustomAsset_EditorData.h"
#include "UncookedOnlyUtils.h"
#include "AnimNextVariableEntry.h"
#include "AnimNextEventGraphEntry.h"

TConstArrayView<TSubclassOf<UUAFRigVMAssetEntry>> UMyCustomAsset_EditorData::GetEntryClasses() const
{
    static const TArray<TSubclassOf<UUAFRigVMAssetEntry>> Classes = {
        UAnimNextVariableEntry::StaticClass(),
        UAnimNextEventGraphEntry::StaticClass(),
        UUAFSharedVariablesEntry::StaticClass(),
    };
    return Classes;
}

void UMyCustomAsset_EditorData::OnPreCompileGetProgrammaticVariables(
    const FRigVMCompileSettings& InSettings,
    FAnimNextGetVariableCompileContext& OutCompileContext)
{
    Super::OnPreCompileGetProgrammaticVariables(InSettings, OutCompileContext);
    
    // 注入一个自动生成的变量，不保存到资产中
    FAnimNextProgrammaticVariable AutoVar;
    AutoVar.Name = FName("AutoGeneratedSpeed");
    AutoVar.SetType(FAnimNextParamType::GetType<float>());
    AutoVar.SetDefaultValueFromString(TEXT("300.0"));
    
    OutCompileContext.GetMutableProgrammaticVariables().Add(AutoVar);
}

void UMyCustomAsset_EditorData::OnPreCompileGetProgrammaticGraphs(
    const FRigVMCompileSettings& InSettings,
    FAnimNextGetGraphCompileContext& OutCompileContext)
{
    Super::OnPreCompileGetProgrammaticGraphs(InSettings, OutCompileContext);
    
    // 可在此动态生成图并注入编译上下文
    // OutCompileContext.GetMutableProgrammaticGraphs().Add(MyGeneratedGraph);
}
```

## 模块依赖

当前分析的 **UAFUncookedOnly** 模块的依赖如下：

| 模块 | 用途 |
|---|---|
| `LiveCoding` | 支持运行时/编辑器代码热重载（Live Coding） |

其他 UAF 子模块（UAF、UAFEditor 等）未在本次分析范围内。

无特殊依赖（仅标准 Core/Engine/Slate 等 + LiveCoding）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `eeaff753` | UAF: Introduce optional tick dependency between the UAF Component targeting a ACharacters mesh compo | 为 UAF 组件添加可选的 tick 依赖，用于 ACharacter 网格组件 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复编译器间的类型转换警告兼容性 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复枚举在格式化函数中导致的垃圾输出问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配问题 |
| 2026-04-24 | `523ac953` | Fix incorrect quaternion attribute type usage | 修复四元数属性类型的错误用法 |

### 维护评价

UAF 插件**活跃维护中**，最近 1 个月内有多次功能性更新和 bug 修复。

- **创建时间**：2025-06-26，约 1 年历史，由原 AnimNext 插件重命名/迁移而来
- **更新频率**：近 1 个月（2026-04 ~ 2026-05）有多次提交，包含新功能（tick 依赖）和编译兼容性修复
- **实验性状态**：`.uplugin` 标记 `IsExperimentalVersion=true`，且 `EnabledByDefault=false`，说明仍在开发中，API 可能变动
- **已知限制**：作为实验性插件，不建议在生产环境中直接使用；部分命名残留了 "AnimNext" 前缀（因从旧插件迁移），后续可能继续重构
- **推荐度**：如果你在探索 UE5 的下一代动画管线架构，值得关注和学习；不建议用于正式项目直到官方移除实验性标记

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF)
- 官方文档：暂无（`.uplugin` 中 DocsURL 为空）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/Tests)