# Motion Design Data Link Integration

> （描述字段为空，已从源码分析）

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计数据链接 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AvalancheDataLink` (Runtime), `AvalancheDataLinkEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/AvalancheDataLink) | |

## 用途

此插件是 **Avalanche (Motion Design)** 系统与 **Data Link** 系统之间的桥梁。它的核心目的是将数据链接（DataLink）功能集成到 Motion Design 工作流中，允许设计师将外部或动态的数据源（DataLink）连接到 Motion Design 的元素和属性上，实现数据驱动的动态图形设计。由于其 `IsBetaVersion: true`，该功能尚在测试阶段。

## 使用场景

- 你正在使用 **Motion Design** 工具创建广播或动态图形设计，并希望元素的属性（如位置、颜色、文本）能由实时数据（如来自数据表格、蓝图或外部 API）自动更新。
- 你需要在 Motion Design Actor 上配置和管理与数据源的映射关系，并希望有一个统一的编辑器界面来操作。

## 蓝图用法

根据源码分析，该插件主要提供**编辑器扩展**和**交互式工具**，其运行时核心功能通常通过编辑器中的属性面板进行配置，而非直接通过蓝图节点暴露大量可调用函数。主要的用户交互发生在 Unreal Editor 的“细节”面板中。

### 核心功能（通过编辑器）

| 功能 | 说明 | 相关类 |
|---|---|---|
| 交互式放置 Actor | 提供一个编辑器工具，用于在场景中快速创建和放置 Avalanche Data Link Actor。 | `UAvaDataLinkActorTool` |
| 自定义细节面板 | 对 Data Link Actor 的实例进行深度定制，优化其属性在“细节”面板中的显示和交互。 | `FAvaDataLinkInstanceCustomization` |
| 控制器映射 UI | 在细节面板中构建一个自定义的、可交互的数组（映射）管理控件，用于配置数据链接控制器。 | `FAvaDataLinkControllerMappingsBuilder` |

### 使用示例（编辑器操作）

1.  确保 `AvalancheDataLink` 插件已启用。
2.  在编辑器主工具栏中，找到并点击由 `FAvaDataLinkEditorCommands` 注册的专用工具按钮（通常标记为“Data Link Actor”）。
3.  在视口内点击或拖拽，即可创建一个 `AvaDataLinkActor`（或其子类）。
4.  选中该 Actor，在“细节”面板中，你将看到经过 `FAvaDataLinkInstanceCustomization` 定制的界面。
5.  在相关属性区域，你将看到由 `FAvaDataLinkControllerMappingsBuilder` 生成的映射配置列表，你可以在此添加、编辑数据源到 Actor 属性的映射关系。

## C++ 用法

该插件的运行时模块 (`AvalancheDataLink`) 主要提供底层数据链接的集成逻辑，而编辑器模块 (`AvalancheDataLinkEditor`) 提供了所有用户界面和交互扩展。对于插件开发者或需要深度定制编辑器的用户，可能会关注编辑器模块。

### 头文件引入

```cpp
// 主要引入编辑器模块的头文件以进行编辑器扩展
#include "AvaDataLinkEditorModule.h"
// 或具体的定制化头文件
#include "AvaDataLinkInstanceCustomization.h"
#include "AvaDataLinkControllerMappingsBuilder.h"
```

### 基本用法：注册细节面板定制

以下代码展示了如何为一个特定的 UObject 类注册自定义的细节面板定制（类似于 `FAvaDataLinkInstanceCustomization` 的工作原理）。

```cpp
// 假设在某个 Editor 模块启动时 (e.g., FAvaDataLinkEditorModule::StartupModule)
// 注册对 UMyDataLinkObject 类的细节定制
FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
PropertyModule.RegisterCustomClassLayout(
    TEXT("MyDataLinkObject"), // 要定制的类名
    FOnGetDetailCustomizationInstance::CreateStatic(&FMyCustomization::MakeInstance)
);
```

### 进阶用法：创建自定义细节构建器

类似于 `FAvaDataLinkControllerMappingsBuilder`，你可以创建一个 `IDetailCustomNodeBuilder` 来在细节面板中插入完全自定义的 UI 行或区域。

```cpp
// 1. 定义一个继承自 IDetailCustomNodeBuilder 的类
class FMyDataCustomBuilder : public IDetailCustomNodeBuilder
{
public:
    // ... 实现所有纯虚函数，如 GenerateHeaderRowContent, GenerateChildContent
    // 在 GenerateChildContent 中构建你的 Slate UI
    virtual void GenerateChildContent(IDetailChildrenBuilder& InChildrenBuilder) override
    {
        // 示例：添加一个自定义的 SWidget
        InChildrenBuilder.AddCustomRow(FText::FromString(TEXT("MyCustomRow")))
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("这是自定义的映射管理区域")))
        ];
    }
    // ... 其他实现
};

// 2. 在 IDetailCustomization::CustomizeDetails 中使用它
void FMyObjectCustomization::CustomizeDetails(IDetailLayoutBuilder& InDetailBuilder)
{
    // 获取一个属性句柄
    TSharedRef<IPropertyHandle> MappingsProperty = InDetailBuilder.GetProperty(GET_MEMBER_NAME_CHECKED(UMyObject, Mappings));

    // 创建自定义构建器实例
    TSharedRef<FMyDataCustomBuilder> CustomBuilder = MakeShared<FMyDataCustomBuilder>(MappingsProperty);

    // 将自定义构建器添加到详情布局中
    IDetailCategoryBuilder& Category = InDetailBuilder.EditCategory(TEXT("Data Link"));
    Category.AddCustomBuilder(CustomBuilder);
}
```

## Demo 示例

以下示例展示了一个最小的数据链接 Actor 的 C++ 类结构，该 Actor 可以使用 `AvalancheDataLink` 插件提供的功能。

### MyDataLinkActor.h
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AvaDataLinkActor.h" // 假设基类来自AvalancheDataLink运行时模块
#include "MyDataLinkActor.generated.h"

UCLASS()
class MYPROJECT_API AMyDataLinkActor : public AAvaDataLinkActor
{
    GENERATED_BODY()

public:
    AMyDataLinkActor();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "My Custom Data")
    FString MyDynamicText;

    // 其他数据驱动属性...
protected:
    virtual void BeginPlay() override;

public:
    virtual void Tick(float DeltaTime) override;

    // 重写以处理来自数据链接的更新
    virtual void OnDataLinkUpdate(const FName& ControllerName, const FInstancedStruct& Payload) override;
};
```

### MyDataLinkActor.cpp
```cpp
#include "MyDataLinkActor.h"

AMyDataLinkActor::AMyDataLinkActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyDataLinkActor::BeginPlay()
{
    Super::BeginPlay();
    // 在编辑器中配置数据链接映射后，BeginPlay 时链接将自动建立
}

void AMyDataLinkActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    // Tick 通常用于视觉更新或依赖于其他逻辑的属性
}

void AMyDataLinkActor::OnDataLinkUpdate(const FName& ControllerName, const FInstancedStruct& Payload)
{
    // 当数据链接源发送新数据时，此函数被调用
    if (ControllerName == TEXT("MyTextController"))
    {
        // 从 Payload 中提取新文本并更新属性
        if (const FMyTextPayload* TextPayload = Payload.GetPtr<FMyTextPayload>())
        {
            MyDynamicText = TextPayload->NewText;
            // 触发 UI 更新或其他逻辑
        }
    }

    // 调用父类实现以确保任何基础功能正常工作
    Super::OnDataLinkUpdate(ControllerName, Payload);
}
```

## 模块依赖

该插件依赖于 `Avalanche` 和 `DataLink` 核心插件。因此，使用此插件的项目模块需要声明对以下模块的依赖：

| 模块 | 用途 |
|---|---|
| `Avalanche` | Motion Design 核心系统 |
| `AvalancheCore` | Motion Design 核心功能 |
| `DataLink` | 数据链接系统 |
| `DataLinkCore` | 数据链接核心功能 |
| `SlateCore` | 编辑器 UI 框架（编辑器模块） |
| `PropertyEditor` | 细节面板定制化（编辑器模块） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-08-27 | `f25e96ca` | Motion Design: set the scene state and data link plugins to beta | 将插件状态正式标记为 Beta 测试阶段。 |
| 2025-08-27 | `94f96138` | Motion Design: Moved scene state and data link plugins out of experimental into virtualproduction | 将插件从实验区正式迁移到虚拟生产插件目录，标志其成为正式功能的一部分。 |

### 维护评价

该插件非常新（创建于 2025 年 8 月），是从实验区迁移出来的正式功能。首次提交就将其标记为 Beta 版本，表明其 API 和功能可能还不稳定，存在变更的风险。由于其依赖于 `Avalanche` 和 `DataLink` 两个大型系统，其维护状态将跟随这两个主插件。目前看来处于**活跃维护**的初期阶段。**鉴于其 Beta 状态，建议在生产环境中谨慎使用，并关注后续版本更新。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/AvalancheDataLink)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/AvalancheDataLink/Tests) (如果存在)