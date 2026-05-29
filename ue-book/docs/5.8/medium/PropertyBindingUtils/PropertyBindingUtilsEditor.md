# PropertyBindingUtils

> Utility code for implementing property bindings（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 属性绑定工具集 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产/编辑器UI） |
| 模块 | `PropertyBindingUtils` (Runtime), `PropertyBindingUtilsEditor` (Editor), `PropertyBindingUtilsTestSuite` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-15 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/PropertyBindingUtils) | |

## 用途

PropertyBindingUtils 插件是从 Unreal Engine 的 StateTree 插件中提取、重构并独立出来的**属性绑定系统核心工具库**。它解决的核心问题是：为游戏逻辑系统（如 StateTree、自定义技能或对话系统）提供一套标准化、可复用的基础设施，用于实现数据在不同结构体（Struct）或对象（Object）属性之间的连接、查询和编辑器展示。

简单来说，这个插件是“属性绑定”功能的**后端引擎和编辑器UI工具包**，其他系统可以基于它快速搭建自己的属性绑定功能，而无需从零开始实现复杂的属性路径解析、类型兼容性检查和编辑器扩展逻辑。

## 使用场景

-   **当你正在开发一个需要数据绑定的自定义游戏系统时**：例如，你制作了一个技能系统，希望将技能的“伤害值”属性绑定到角色的“攻击力”属性上。你可以复用此插件的工具，专注于定义你的技能结构体和绑定规则，而无需关心底层的属性路径表示和编辑器UI。
-   **当你需要扩展或定制 Unreal 编辑器中某个属性（例如在细节面板中）的绑定行为时**：`FPropertyBindingExtension` 类正是为此设计，允许你覆盖默认的绑定逻辑。
-   **当你在研究或维护 StateTree 的属性绑定功能时**：理解此插件是理解 StateTree 属性绑定实现的基础。

## 蓝图用法

此插件主要为 C++ 和编辑器扩展设计，不直接暴露蓝图可调用节点。其核心价值体现在编辑器细节面板（Details Panel）中为特定属性自动添加的绑定UI控件。以下节点供在编辑器UI控件（Slate Widget）中使用：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SBindingView` | 一个列表视图控件，用于显示和管理 `IPropertyBindingBindingCollectionOwner` 中的所有绑定。 | `UE::PropertyBinding::SBindingView` |

### 使用示例（蓝图描述）

此插件的典型使用场景是在编辑器C++扩展中，而非在蓝图图表中。你需要通过子类化 `FPropertyBindingExtension` 来为你的自定义属性注入绑定UI。在编辑器中，用户通过一个下拉菜单或选择器来添加、移除或查看属性之间的绑定关系。

## C++ 用法

### 头文件引入

```cpp
#include "PropertyBindingExtension.h" // 包含 FPropertyBindingExtension 和 FCachedBindingData
```

### 基本用法：创建一个属性绑定扩展

从 `FPropertyBindingExtension` 派生一个类，并重写 `IsPropertyExtendable` 和 `ExtendWidgetRow` 方法来为你的属性添加绑定能力。
（来源: `Public/PropertyBindingExtension.h`）

```cpp
// MyBindingExtension.h
#pragma once
#include "PropertyBindingExtension.h"

class FMyBindingExtension : public FPropertyBindingExtension
{
public:
    // 判断哪个属性需要显示绑定UI
    virtual bool IsPropertyExtendable(const UClass* InObjectClass, const IPropertyHandle& InPropertyHandle) const override
    {
        // 假设我们只给标记了“Bindable”的属性添加绑定UI
        return InPropertyHandle.GetBoolMetaData(FName("Bindable"));
    }

    // 为属性行扩展UI
    virtual void ExtendWidgetRow(FDetailWidgetRow& InWidgetRow, const IDetailLayoutBuilder& InDetailBuilder, const UClass* InObjectClass, TSharedPtr<IPropertyHandle> InPropertyHandle) override
    {
        // 调用基类方法，它会利用 CreateCachedBindingData 和 CustomizeDetailWidgetRow 来构建UI
        FPropertyBindingExtension::ExtendWidgetRow(InWidgetRow, InDetailBuilder, InObjectClass, InPropertyHandle);
    }

protected:
    // 创建缓存的绑定数据，你可以在这里定制绑定数据的初始化逻辑
    virtual TSharedPtr<UE::PropertyBinding::FCachedBindingData> CreateCachedBindingData(...) const override
    {
        // 示例：创建基类的缓存数据
        return MakeShareable(new UE::PropertyBinding::FCachedBindingData(InBindingsOwner, InTargetPath, InPropertyHandle, InAccessibleStructs));
    }
};
```

### 进阶用法：使用 FCachedBindingData 管理绑定状态

`FCachedBindingData` 是核心状态管理类，封装了与特定属性关联的绑定数据。它负责检查兼容性、添加/移除绑定，并提供用于UI显示的信息（文本、图标、颜色）。
（来源: `Public/PropertyBindingExtension.h`）

```cpp
// 假设你已经有一个指向 IPropertyBindingBindingCollectionOwner 和属性句柄的指针
IPropertyBindingBindingCollectionOwner* BindingCollectionOwner = ...;
TSharedPtr<IPropertyHandle> PropertyHandle = ...;
TConstArrayView<TInstancedStruct<FPropertyBindingBindableStructDescriptor>> AccessibleStructs = ...;
FPropertyBindingPath TargetPath = ...; // 目标属性的路径

// 1. 创建缓存的绑定数据
TSharedPtr<UE::PropertyBinding::FCachedBindingData> CachedData = MakeShareable(
    new UE::PropertyBinding::FCachedBindingData(BindingCollectionOwner, TargetPath, PropertyHandle, AccessibleStructs)
);

// 2. 检查是否有绑定
if (CachedData->HasBinding(FPropertyBindingBindingCollection::ESearchMode::All))
{
    UE_LOG(LogTemp, Log, TEXT("属性 '%s' 已绑定。"), *TargetPath.ToString());
    // 3. 获取绑定信息，用于更新UI
    FText DisplayText = CachedData->GetText();
    FLinearColor Color = CachedData->GetColor();
    // ... 将 DisplayText 和 Color 应用到你的 Slate 控件
}

// 4. 模拟添加一个绑定（通常由UI触发）
TArray<FBindingChainElement> BindingChain; // 填充源路径信息
CachedData->AddBinding(BindingChain);

// 5. 模拟移除绑定
CachedData->RemoveBinding(FPropertyBindingBindingCollection::ESearchMode::User);
```

## Demo 示例

一个最小的属性绑定扩展实现示例。

**MyPropertyBindingExtension.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "PropertyBindingExtension.h"

// 一个简单的绑定扩展，为所有带 “BindMe” 元数据的属性添加绑定UI
class FMyPropertyBindingExtension : public FPropertyBindingExtension
{
public:
    virtual bool IsPropertyExtendable(const UClass* InObjectClass, const IPropertyHandle& InPropertyHandle) const override
    {
        // 检查属性是否有 "BindMe" 元数据
        return InPropertyHandle.HasMetaData(FName("BindMe"));
    }
    
protected:
    // 可以选择性地重写此方法来自定义绑定UI的外观或行为
    virtual void CustomizeDetailWidgetRow(
        FDetailWidgetRow& InWidgetRow, 
        const IDetailLayoutBuilder& InDetailBuilder,
        IPropertyBindingBindingCollectionOwner* InBindingsOwner,
        TSharedPtr<IPropertyHandle> InPropertyHandle,
        const FPropertyBindingPath& InTargetPath,
        TSharedPtr<UE::PropertyBinding::FCachedBindingData> InCachedBindingData
    ) const override
    {
        // 在这里，你可以完全控制绑定UI的构建，或者在调用基类实现前/后添加额外的控件。
        // 调用基类实现来获取默认的绑定UI。
        FPropertyBindingExtension::CustomizeDetailWidgetRow(
            InWidgetRow, InDetailBuilder, InBindingsOwner, InPropertyHandle, InTargetPath, InCachedBindingData
        );
        
        // 示例：在默认的绑定UI后面添加一个“解绑”按钮
        if (InCachedBindingData->HasBinding(FPropertyBindingBindingCollection::ESearchMode::User))
        {
            InWidgetRow.ExtensionContent()
            [
                SNew(SButton)
                .Text(LOCTEXT("UnbindButton", "Unbind"))
                .OnClicked(FOnClicked::CreateLambda([InCachedBindingData]() -> FReply
                {
                    InCachedBindingData->RemoveBinding(FPropertyBindingBindingCollection::ESearchMode::User);
                    return FReply::Handled();
                }))
            ];
        }
    }
};
```

**MyPropertyBindingExtension.cpp**
```cpp
#include "MyPropertyBindingExtension.h"

// 注册此扩展。通常在你的模块 StartupModule 中调用。
// FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
// PropertyModule.RegisterPropertyTypeCustomization(...); // 或者使用其他注册机制
// PropertyModule.RegisterCustomClassLayout(...); // 针对类自定义
```

## 模块依赖

编辑器模块 `PropertyBindingUtilsEditor` 是主要的对外接口，其依赖关系体现了插件的核心功能所需。

| 模块 | 用途 |
|---|---|
| `PropertyBindingUtils` | 核心运行时库，包含属性绑定数据结构和逻辑。 |
| `PropertyAccess` | 提供底层的属性访问和路径解析功能。 |
| `StateTreeModule` | 与StateTree深度集成，用于StateTree特定的绑定逻辑。 |

*注：编辑器模块（`PropertyBindingUtilsEditor`）还隐式依赖 UnrealEd、Slate/UMG 等标准编辑器模块，此处已省略。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-22 | `bd1b81a6` | [StateTree] Implement task completion binding support for StateTree property bindings. | 为 StateTree 的任务完成事件添加了属性绑定支持。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF。 |
| 2026-03-31 | `55512aa0` | PropertyBindings: Provide a detailed error message when promoting a parameter ensures due to failed | 当参数提升因失败而中止时，提供更详细的错误消息。 |
| 2026-03-26 | `7113aa71` | [StateTree] Centralize FStateTreeEditorNode initialization via InitializeAs() | 通过 InitializeAs() 函数集中初始化 StateTree 编辑器节点。 |
| 2026-03-13 | `86c9c6c7` | [StateTree] Add the output binding batch index info to the compilation output log. | 在编译输出日志中添加输出绑定批处理索引信息。 |

### 维护评价

- **创建时间**: 2024-01-15，距今约 1 年，是一个相对较新的插件。
- **活跃维护**: 最近更新频繁（2026年4月），且内容均为功能性增强或集成改进（主要围绕StateTree），表明该插件处于**活跃开发和维护**中。
- **实验性插件**: `.uplugin` 文件中 `IsBetaVersion: true` 且 `EnabledByDefault: false`，这明确表明它仍处于实验阶段，API 和功能可能在不通知的情况下发生变化。
- **推荐状态**: **谨慎推荐**。对于需要深度定制 StateTree 属性绑定或构建类似高级属性绑定系统的开发者，这是一个重要的参考和工具库。但由于其**实验性质**，在生产环境中使用需自行承担稳定性风险，并密切关注其更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/PropertyBindingUtils)
- [官方文档]() （无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/PropertyBindingUtils/Source/PropertyBindingUtilsTestSuite)