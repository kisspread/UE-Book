# Motion Design

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、编辑器工具等） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Avalanche（动态设计）插件是一套专为虚拟制片（Virtual Production）和实时广播设计的综合性工具集。它提供了一套完整的解决方案，用于在虚幻引擎内创建、合成和控制动态视觉效果。其核心目标是将传统后期合成、动态图形设计和实时广播流程集成到引擎中，允许设计师和广播工程师在熟悉的3D环境中直接完成从设计到最终输出的全流程工作。该插件由众多子模块构成，涵盖了场景构建、材质设计、动画控制、媒体合成、远程控制、特效生成等各个方面。

`AvalancheTagEditor` 模块是 Motion Design 插件中**标签系统（Tag System）** 的**编辑器侧实现**。它为 `AvalancheTag` 模块中定义的标签数据结构（如 `FAvaTagHandle`, `UAvaTagCollection`）提供了完整的编辑器集成，包括标签资产的创建工厂、属性面板（Details Panel）的自定义界面、以及用于选取和管理标签的专用UI控件。它的存在使得设计师可以在编辑器中方便地创建、编辑和引用标签，从而为场景中的元素（如模型、材质、动画）打上逻辑分类标签，用于实现批量控制、条件触发等功能。

## 使用场景

- **你需要为场景中的多个物体分组控制属性**：例如，为所有“霓虹灯”物体打上标签，然后通过标签统一调整其亮度或颜色动画。
- **你在设计一个交互式灯光秀**：使用标签系统为不同的灯光组命名，并在Sequencer或远程控制协议中引用这些标签来触发特定的灯光序列。
- **你正在创建需要条件触发的特效**：给不同的粒子系统打上标签，在蓝图或脚本中检查特定标签是否存在来决定是否播放特效。
- **你需要一套灵活的资产管理系统**：利用标签对静态网格、材质等资产进行分类和筛选，超越传统的文件夹管理方式。

## 蓝图用法

`AvalancheTagEditor` 模块本身主要提供编辑器功能，其核心数据结构和基础操作接口（如 `FAvaTagHandle`）定义在 `AvalancheTag` 运行时模块中，并可在蓝图中使用。本模块的关键贡献是提供了这些数据类型的**编辑器属性自定义**。

### 核心接口 (来自 `AvalancheTag` 运行时模块，在蓝图中可用)

| 接口/类 | 说明 | 所在模块 |
|---|---|---|
| `FAvaTagHandle` | 标签句柄结构体，是引用一个具体标签的主要方式。 | `AvalancheTag` |
| `UAvaTagCollection` | 标签集合资产，用于定义和存储一组标签。 | `AvalancheTag` |
| `IAvaTagHandleCustomizer` | 标签句柄自定义器接口，用于在编辑器中处理不同类型的标签句柄（单选、多选、别名等）。 | `AvalancheTagEditor` |

### 编辑器自定义实现 (C++)

`AvalancheTagEditor` 模块实现了多种 `IAvaTagHandleCustomizer` 的派生类，用于为不同的标签属性类型提供定制的编辑器UI：
- `FAvaTagHandleCustomizer`: 用于单选的 `FAvaTagHandle` 属性。
- `FAvaTagHandleContainerCustomizer`: 用于多选的标签容器。
- `FAvaTagSoftHandleCustomizer`: 用于软引用（`TSoftObjectPtr`）的标签句柄。
- `FAvaTagAliasCustomizer`: 用于标签别名系统。

### 使用示例（属性面板）

当一个 `UObject` 包含一个类型为 `FAvaTagHandle` 的 `UPROPERTY` 时，`AvalancheTagEditor` 模块会自动将其在细节面板中的显示替换为一个可交互的标签选取器（`SAvaTagPicker`）。开发者无需编写额外代码，只需正确声明属性类型即可享受完整的编辑器集成体验。

## C++ 用法

本模块的用法主要集中在**编辑器扩展**和**自定义标签处理器**的实现上。

### 头文件引入

```cpp
#include "AvalancheTagEditor.h"
```

### 基本用法：实现自定义标签处理器

你可以通过实现 `IAvaTagHandleCustomizer` 接口来创建自定义的标签选取行为。以下是一个简化示例，来源于 `AvaTagHandleCustomizer.h` 和 `AvaTagAliasCustomizer.h`。

```cpp
// 来源：Private/Customization/TagCustomizers/AvaTagHandleCustomizer.h
// 以及 IAvaTagHandleCustomizer.h
#include "IAvaTagHandleCustomizer.h"

class FMyCustomTagCustomizer : public IAvaTagHandleCustomizer
{
public:
    // 获取标签集合的属性句柄，用于在UI中选择集合源
    virtual TSharedPtr<IPropertyHandle> GetTagCollectionHandle(const TSharedRef<IPropertyHandle>& InStructHandle) const override
    {
        // 返回指向结构体中“TagCollection”成员的属性句柄
        return InStructHandle->GetChildHandle(GET_MEMBER_NAME_CHECKED(FMyTagStruct, TagCollection));
    }

    // 从原始数据中获取或加载标签集合对象
    virtual const UAvaTagCollection* GetOrLoadTagCollection(const void* InStructRawData) const override
    {
        const FMyTagStruct* TagStruct = static_cast<const FMyTagStruct*>(InStructRawData);
        return TagStruct->TagCollection.LoadSynchronous(); // 对于软引用
        // 或者直接返回 TagStruct->TagCollection; // 对于硬引用
    }

    // 设置标签是否被选中
    virtual void SetTagHandleAdded(const TSharedRef<IPropertyHandle>& InStructHandle, const FAvaTagHandle& InTagHandle, bool bInAdd) const override
    {
        if (bInAdd)
        {
            // 将 InTagHandle 设置到属性中
            InStructHandle->SetValue(InTagHandle);
        }
        else
        {
            // 清除或重置属性
            // InStructHandle->SetValue(FMyDefaultTagHandle);
        }
    }

    // 检查当前数据是否包含指定标签
    virtual bool ContainsTagHandle(const void* InStructRawData, const FAvaTagHandle& InTagHandle) const override
    {
        const FMyTagStruct* TagStruct = static_cast<const FMyTagStruct*>(InStructRawData);
        return TagStruct->CurrentTagHandle == InTagHandle;
    }

    // 获取用于UI显示的标签值名称
    virtual FName GetDisplayValueName(const void* InStructRawData) const override
    {
        const FMyTagStruct* TagStruct = static_cast<const FMyTagStruct*>(InStructRawData);
        return TagStruct->CurrentTagHandle.GetTagName(); // 假设 FAvaTagHandle 有 GetTagName 方法
    }

    // 可选：允许选择多个标签
    // virtual bool AllowMultipleTags() const override { return false; }
};
```

### 进阶用法：注册自定义标签类型

要使你的自定义类型在编辑器中获得标签选取器支持，需要在模块启动时注册一个自定义化（Customization）。

```cpp
// 来源：Private/AvaTagEditorModule.h
void FAvalancheTagEditorModule::RegisterCustomizations()
{
    FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>(“PropertyEditor”);
    
    // 为你的结构体类型注册自定义化
    PropertyModule.RegisterCustomPropertyTypeLayout(
        FMyTagStruct::StaticStruct()->GetFName(),
        FOnGetPropertyTypeCustomizationInstance::CreateLambda([]() -> TSharedRef<IPropertyTypeCustomization>
        {
            return MakeShareable(new FAvaTagHandleCustomization(
                MakeShareable(new FMyCustomTagCustomizer()) // 传入你的自定义处理器
            ));
        })
    );
    CustomizedTypes.Add(FMyTagStruct::StaticStruct()->GetFName());
}

void FAvalancheTagEditorModule::UnregisterCustomizations()
{
    if (FModuleManager::Get().IsModuleLoaded(“PropertyEditor”))
    {
        FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>(“PropertyEditor”);
        for (const FName& TypeName : CustomizedTypes)
        {
            PropertyModule.UnregisterCustomPropertyTypeLayout(TypeName);
        }
    }
    CustomizedTypes.Empty();
}
```

## Demo 示例

一个完整的自定义标签处理器及注册示例。

### MyCustomTagStruct.h
```cpp
#pragma once

#include “CoreMinimal.h”
#include “AvalancheTag.h”
#include “MyCustomTagStruct.generated.h”

USTRUCT(BlueprintType)
struct FMyCustomTagStruct
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category = “Tags”)
    FAvaTagHandle TagHandle;

    UPROPERTY(EditAnywhere, Category = “Tags”)
    TSoftObjectPtr<UAvaTagCollection> TagCollection;
};
```

### MyCustomTagCustomizer.h
```cpp
#pragma once

#include “IAvaTagHandleCustomizer.h”

class FMyCustomTagCustomizer : public IAvaTagHandleCustomizer
{
public:
    // 此处实现上面提到的所有纯虚函数...
    // (省略具体实现，参考上文)
    virtual TSharedPtr<IPropertyHandle> GetTagCollectionHandle(const TSharedRef<IPropertyHandle>& InStructHandle) const override;
    virtual const UAvaTagCollection* GetOrLoadTagCollection(const void* InStructRawData) const override;
    virtual void SetTagHandleAdded(const TSharedRef<IPropertyHandle>& InStructHandle, const FAvaTagHandle& InTagHandle, bool bInAdd) const override;
    virtual bool ContainsTagHandle(const void* InStructRawData, const FAvaTagHandle& InTagHandle) const override;
    virtual FName GetDisplayValueName(const void* InStructRawData) const override;
};
```

### MyTagEditorModule.cpp
```cpp
#include “Modules/ModuleManager.h”
#include “PropertyEditorModule.h”
#include “AvalancheTagEditor.h”
#include “MyCustomTagStruct.h”
#include “MyCustomTagCustomizer.h”
#include “Customization/AvaTagHandleCustomization.h”

class FMyTagEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override
    {
        if (GIsEditor && !IsRunningCommandlet())
        {
            RegisterCustomizations();
        }
    }

    virtual void ShutdownModule() override
    {
        UnregisterCustomizations();
    }

private:
    void RegisterCustomizations()
    {
        FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>(“PropertyEditor”);
        PropertyModule.RegisterCustomPropertyTypeLayout(
            FMyCustomTagStruct::StaticStruct()->GetFName(),
            FOnGetPropertyTypeCustomizationInstance::CreateLambda([]() -> TSharedRef<IPropertyTypeCustomization>
            {
                return MakeShareable(new FAvaTagHandleCustomization(
                    MakeShareable(new FMyCustomTagCustomizer())
                ));
            })
        );
        CustomizedTypes.Add(FMyCustomTagStruct::StaticStruct()->GetFName());
    }

    void UnregisterCustomizations()
    {
        if (FModuleManager::Get().IsModuleLoaded(“PropertyEditor”))
        {
            FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>(“PropertyEditor”);
            for (const FName& TypeName : CustomizedTypes)
            {
                PropertyModule.UnregisterCustomPropertyTypeLayout(TypeName);
            }
        }
        CustomizedTypes.Empty();
    }

    TArray<FName> CustomizedTypes;
};

IMPLEMENT_MODULE(FMyTagEditorModule, MyTagEditor)
```

## 模块依赖

从模块功能和命名推断，`AvalancheTagEditor` 模块主要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `AvalancheTag` | 提供核心的标签数据结构（`FAvaTagHandle`， `UAvaTagCollection`）和运行时逻辑。 |
| `Slate`, `SlateCore` | 构建编辑器UI控件（`SAvaTagPicker`等）的基础框架。 |
| `PropertyEditor` | 用于注册和实现细节面板（Details Panel）的属性类型自定义化。 |
| `ToolMenus` | 用于创建上下文菜单（如`FAvaTagCollectionPickerContextMenu`）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将动态设计的相关编辑器选项卡（场景设置、大纲视图）移至独立的功能组。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 在使用“节目单页面”设置时，为电影渲染队列添加了分析功能。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在播出控制工具栏中添加了页面加载选项（全部、下一个、已选），并添加了相关功能。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加了一个项目设置，用于强制禁用Text3D和形状的碰撞。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口：通过通知客户端关联或断开关联来规范必要的代码复制粘贴行为。 |

### 维护评价

`Motion Design`（包括 `AvalancheTagEditor` 模块）是一个**活跃维护中**的新模块。
- **创建时间**：2025年5月，从实验性插件迁移到正式插件目录。
- **更新频率**：最近提交集中在2025年5月，表明其在开发初期是核心关注点，功能仍在快速迭代和完善中。
- **状态**：作为 Epic Games 官方为虚拟制片推出的主要工具之一，预计会长期投入维护。当前为**实验性**状态（`⚠️ 是`），意味着其API和功能可能会在未来的引擎版本中发生变化。
- **推荐度**：对于虚拟制片、动态图形和广播工作流，这是官方推荐的工具。建议关注其更新日志以跟进API变更。由于模块较新，在生产环境中使用时需进行充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/virtual-production-in-unreal-engine/) (暂无专门文档，但属于虚拟制片工具集一部分)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheFunctionalTest) (包含在主插件的测试模块中)