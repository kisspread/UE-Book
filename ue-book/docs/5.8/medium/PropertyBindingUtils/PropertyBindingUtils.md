# Property Binding Utils

> Utility code for implementing property bindings

| 属性 | 值 |
|---|---|
| 中文名 | 属性绑定工具 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资产、编辑器工具） |
| 模块 | `PropertyBindingUtils` (Runtime), `PropertyBindingUtilsEditor` (Editor), `PropertyBindingUtilsTestSuite` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-15 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/PropertyBindingUtils) | |

## 用途

PropertyBindingUtils 是一个用于实现**属性绑定**基础设施的共享插件。它从 StateTree 插件中提取并泛化，旨在为引擎中的多个系统（如 StateTree、Gameplay Ability System 或任何需要动态属性连接的自定义系统）提供一套统一、可复用的属性绑定框架。

**核心解决的问题**：在不同对象（或数据结构）之间建立动态的属性读写连接，而不是硬编码的直接访问。它通过**属性路径**（`FPropertyBindingPath`）描述连接关系，并通过**绑定集合**（`FPropertyBindingBindingCollection`）管理这些连接，最终将它们解析为高效的内存偏移量，以实现高性能的属性数据复制。

**为什么存在**：避免为每个需要类似功能的系统（状态树、技能系统、动画蓝图、UI 数据绑定等）重复开发属性访问和复制的底层代码。它提供了路径解析、验证、类型提升、重定向处理等通用能力。

## 使用场景

-   **你需要为你的自定义状态机或行为树节点实现“属性绑定”**：例如，让一个节点的输出值（如 `Health`）能动态地设置到另一个节点的输入属性上。你可以继承 `FPropertyBindingBindingCollection` 来管理这些绑定。
-   **你的游戏系统需要在编辑器中可视化地配置数据流**：例如，用户需要在编辑器里将“玩家速度”拖拽连接到“冲刺粒子效果的速度参数”上。此插件提供了底层支持，可用于构建这样的可视化编辑器。
-   **你在开发一个需要读取或写入来自不同数据源（其他对象、结构体实例）属性的运行时系统**：`FPropertyBindingDataView` 提供了一种统一的方式来安全地访问 UObject 或任意 UStruct 的内存。
-   **你需要处理属性重命名、结构体类型变化等兼容性问题**：`FPropertyBindingPath` 的解析和更新机制内置了对 Core Redirect、蓝图类和用户自定义结构体属性重定向的支持。

## 蓝图用法

本插件的核心模块 (`PropertyBindingUtils`) 是 Runtime 类型，主要提供 C++ 接口，用于构建上层系统。直接可供蓝图使用的节点较少，其价值在于被其他插件或系统（如 StateTree 编辑器）集成后，在编辑器中暴露出可视化操作。蓝图开发者通常通过继承 `IPropertyBindingBindingCollectionOwner` 接口的 UObject 来参与绑定过程。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetBindableStructs` | (Editor-only) 获取对某个目标结构体可见的、可用于绑定的结构体描述符列表。 | `IPropertyBindingBindingCollectionOwner` |
| `GetEditorPropertyBindings` | (Editor-only) 获取该拥有者的编辑器属性绑定集合。 | `IPropertyBindingBindingCollectionOwner` |

**重要说明**：`FPropertyBindingBindingCollection`、`FPropertyBindingPath` 等核心类型是 `USTRUCT`，可以在蓝图中作为变量使用，但它们的复杂操作（如路径解析）需要通过 C++ 调用。

### 使用示例（蓝图描述）

1.  **实现拥有者接口**：创建一个从 `UObject` 派生的蓝图类，添加 `IPropertyBindingBindingCollectionOwner` 接口。在 C++ 中实现其 `GetBindableStructs` 等虚函数，以便编辑器知道从哪里获取可绑定的数据。
2.  **在编辑器中使用**：当其他系统（如 StateTree 编辑器）检测到你的对象实现了此接口时，它会调用你的接口方法来获取可绑定的数据列表，并在 UI 中展示，允许用户创建 `FPropertyBindingBinding` 条目。

## C++ 用法

### 头文件引入

```cpp
#include "PropertyBindingUtils/PropertyBindingPath.h"
#include "PropertyBindingUtils/PropertyBindingBindingCollection.h"
#include "PropertyBindingUtils/PropertyBindingBindingCollectionOwner.h"
#include "PropertyBindingUtils/PropertyBindingDataView.h"
```

### 基本用法

以下示例展示如何定义和使用一个简单的绑定集合。

```cpp
// MyBindingCollection.h
#pragma once
#include "PropertyBindingUtils/PropertyBindingBindingCollection.h"
#include "MyBindingCollection.generated.h"

USTRUCT()
struct FMyBindingCollection : public FPropertyBindingBindingCollection
{
    GENERATED_BODY()

    // 必须实现的纯虚函数
    virtual int32 GetNumBindableStructDescriptors() const override { /* ... */ }
    virtual const FPropertyBindingBindableStructDescriptor* GetBindableStructDescriptorFromHandle(FConstStructView InSourceHandleView) const override { /* ... */ }
    virtual int32 GetNumBindings() const override { /* ... */ }
    virtual void ForEachBinding(TFunctionRef<void(const FPropertyBindingBinding& Binding)> InFunction) const override { /* ... */ }
    virtual void ForEachMutableBinding(TFunctionRef<void(FPropertyBindingBinding& Binding)> InFunction) override { /* ... */ }
    // ... 其他纯虚函数实现

protected:
    // 实现具体的绑定存储逻辑
    virtual FPropertyBindingBinding* AddBindingInternal(const FPropertyBindingPath& InSourcePath, const FPropertyBindingPath& InTargetPath) override;
    virtual void RemoveBindingsInternal(TFunctionRef<bool(FPropertyBindingBinding&)> InPredicate) override;
    virtual bool HasBindingInternal(TFunctionRef<bool(const FPropertyBindingBinding&)> InPredicate) const override;
    virtual const FPropertyBindingBinding* FindBindingInternal(TFunctionRef<bool(const FPropertyBindingBinding&)> InPredicate) const override;
};
```

```cpp
// MyBindingUsage.cpp
void UMyClass::SetupBindings()
{
    FMyBindingCollection MyBindings;

    // 1. 设置拥有者（用于路径验证）
    MyBindings.SetBindingsOwner(this); // `this` 需实现 IPropertyBindingBindingCollectionOwner

    // 2. 添加绑定
    FPropertyBindingPath SourcePath(FGuid(), FName("Health"));
    FPropertyBindingPath TargetPath(FGuid(), FName("CurrentHealth"));
    MyBindings.AddBinding(SourcePath, TargetPath);

    // 3. 解析所有绑定的路径，将其转换为高效的内存偏移（`FPropertyBindingCopyInfo`）
    bool bResolved = MyBindings.ResolvePaths();
    if (bResolved)
    {
        // 4. 在运行时复制属性值
        FPropertyBindingDataView SourceView(SourceStruct, SourceMemory);
        FPropertyBindingDataView TargetView(TargetStruct, TargetMemory);
        const auto& Batch = MyBindings.GetBatch(FPropertyBindingIndex16(0));
        for (const auto& CopyInfo : MyBindings.GetBatchCopies(Batch))
        {
            MyBindings.CopyProperty(CopyInfo, SourceView, TargetView);
        }
    }
}
```

### 进阶用法：实现 IPropertyBindingBindingCollectionOwner

这是将你的类接入属性绑定编辑器功能的关键。

```cpp
// MyBindableObject.h
UCLASS()
class UMyBindableObject : public UObject, public IPropertyBindingBindingCollectionOwner
{
    GENERATED_BODY()

public:
    // 运行时接口
    virtual bool GetBindingDataView(const FPropertyBindingBinding& InBinding, EBindingSide InSide, FPropertyBindingDataView& OutDataView) override;

#if WITH_EDITOR
    // 编辑器接口
    virtual void GetBindableStructs(const FGuid InTargetStructID, TArray<TInstancedStruct<FPropertyBindingBindableStructDescriptor>>& OutStructDescs) const override;
    virtual bool GetBindableStructByID(const FGuid InStructID, TInstancedStruct<FPropertyBindingBindableStructDescriptor>& OutStructDesc) const override;
    virtual bool GetBindingDataViewByID(const FGuid InStructID, FPropertyBindingDataView& OutDataView) const override;
    virtual FPropertyBindingBindingCollection* GetEditorPropertyBindings() override;
    // ... 实现其他编辑器虚函数
#endif

private:
    UPROPERTY()
    FMyBindingCollection EditorBindings; // 包含绑定集合
};
```

## Demo 示例

一个最小的、展示 `FPropertyBindingDataView` 用法的控制台程序片段。

```cpp
// MinimalBindingDemo.h
#pragma once
#include "PropertyBindingUtils/PropertyBindingDataView.h"

struct FMyActorData
{
    float Speed = 0.f;
    int32 Ammo = 100;
};

class FMinimalBindingDemo
{
public:
    void Run();
};

// MinimalBindingDemo.cpp
#include "MinimalBindingDemo.h"
#include "UObject/UObjectGlobals.h"

void FMinimalBindingDemo::Run()
{
    // 模拟一个 UObject
    UObject* DummyObject = NewObject<UObject>();
    // 模拟一个自定义结构体实例
    FMyActorData ActorData{ 350.f, 30 };

    // 创建数据视图
    FPropertyBindingDataView ObjectView(DummyObject);
    FPropertyBindingDataView StructView(FMyActorData::StaticStruct(), &ActorData);

    // 安全访问
    if (ObjectView.IsValid())
    {
        UObject& ObjRef = ObjectView.Get<UObject>();
        UE_LOG(LogTemp, Log, TEXT("Accessed valid UObject"));
    }

    if (StructView.IsValid())
    {
        FMyActorData& DataRef = StructView.GetMutable<FMyActorData>();
        UE_LOG(LogTemp, Log, TEXT("Actor Speed: %f, Ammo: %d"), DataRef.Speed, DataRef.Ammo);
    }
}
```

## 模块依赖

使用核心 `PropertyBindingUtils` 模块**无需特殊依赖**。它设计为底层工具，仅依赖引擎核心模块。

如果要使用**编辑器**功能 (`PropertyBindingUtilsEditor`) 或**测试**功能 (`PropertyBindingUtilsTestSuite`)，则需要依赖对应的模块。

| 模块 | 用途 |
|---|---|
| `PropertyBindingUtilsEditor` | 提供属性绑定的编辑器集成工具（如自定义资产编辑器扩展、路径选择器 UI）。 |
| `PropertyBindingUtilsTestSuite` | 包含该插件的自动化测试用例，用于开发和验证。 |

**重要**：当你的模块（或插件）需要使用 `FPropertyBindingBindingCollection` 等类型时，请在你的 `Build.cs` 中添加对 `PropertyBindingUtils` 模块的依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-22 | `bd1b81a6` | [StateTree] Implement task completion binding support for StateTree property bindings. | 为状态树的任务完成事件添加了属性绑定支持。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏统一迁移到新的 `UE_LOGF` 格式。 |
| 2026-03-31 | `55512aa0` | PropertyBindings: Provide a detailed error message when promoting a parameter ensures due to failed | 优化了参数提升失败时的错误信息，使其更详细。 |
| 2026-03-26 | `7113aa71` | [StateTree] Centralize FStateTreeEditorNode initialization via InitializeAs() | 集中了状态树编辑器节点的初始化逻辑。 |
| 2026-03-13 | `86c9c6c7` | [StateTree] Add the output binding batch index info to the compilation output log. | 在编译日志中添加了输出绑定批次索引信息，便于调试。 |

### 维护评价

-   **状态**：**活跃维护中**。插件创建于 2024 年初，非常年轻。近期（2026 年 3-4 月）的更新记录显示它仍在被频繁修改和增强，主要与 **StateTree** 系统的深度集成有关。
-   **风险提示**：插件标记为 `IsBetaVersion=true` 且 `EnabledByDefault=false`，表明 API 和功能可能还不稳定，可能会在未来的引擎版本中发生变更。
-   **推荐度**：如果你正在开发需要复杂、动态属性连接的系统（尤其是与状态树协同工作），**强烈建议研究并使用此插件**，它能为你节省大量底层开发时间。但请准备好应对可能的 API 调整，并始终关注其与主仓库 StateTree 插件的同步更新。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/PropertyBindingUtils)
-   [官方文档]：暂无
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/PropertyBindingUtils/Source/PropertyBindingUtilsTestSuite)