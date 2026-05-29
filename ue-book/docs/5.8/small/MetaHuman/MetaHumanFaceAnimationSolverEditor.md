# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | unknown |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一套将真实世界人脸表演转换为 MetaHuman 角色动画的完整工具链。它不仅仅是一个动画工具，而是覆盖了从**捕获**（通过手机或专业设备录制表演）、**处理**（跟踪面部特征点、求解动画曲线）到**应用**（驱动 MetaHuman 角色）的端到端工作流。其核心目的是让创作者能够高效地将演员的表演“移植”到数字角色上，实现逼真的面部动画。

## 使用场景

- **影视与游戏过场动画制作**：使用 iPhone 或专业设备录制演员面部表演，快速生成高保真度的 MetaHuman 角色动画序列。
- **实时虚拟直播或会议**：将演员的实时面部表情和口型同步驱动到虚拟 MetaHuman 主播或数字分身上。
- **历史影像资料数字化**：处理已有的影像素材（如电影片段），为其中的真人角色生成对应的 MetaHuman 动画，用于重制或分析。
- **批量动画生产**：对于有大量对话或表演需求的项目，使用批处理功能批量处理录制素材，提高生产效率。

## 蓝图用法

由于 MetaHuman Animator 是一个大型工具链插件，其运行时蓝图功能通常在其他关联模块（如 `MetaHumanPerformance` 或 `MetaHumanPipeline`）中。当前分析的 `MetaHumanFaceAnimationSolverEditor` 模块主要为编辑器提供资产创建和自定义界面，不直接暴露运行时蓝图节点。

编辑器相关的功能（如创建求解器资产）通常在编辑器工具或通过 `UMetaHumanFaceAnimationSolverFactoryNew` 工厂类在“内容浏览器”中通过右键菜单使用。

## C++ 用法

### 基本用法

以下示例展示了如何在编辑器插件中自定义 `MetaHumanFaceAnimationSolver` 资产的细节面板。

**头文件引入**
```cpp
#include "IDetailCustomization.h"
#include "IDetailLayoutBuilder.h"
```

**自定义细节面板**
```cpp
// 继承 IDetailCustomization 来自定义资产的属性面板
class FMyCustomFaceSolverCustomization : public IDetailCustomization
{
public:
    static TSharedRef<IDetailCustomization> MakeInstance()
    {
        return MakeShareable(new FMyCustomFaceSolverCustomization);
    }

    // 重写 CustomizeDetails 来布局和编辑属性
    virtual void CustomizeDetails(IDetailLayoutBuilder& InDetailBuilder) override
    {
        // 获取所有选中的资产对象
        TArray<TWeakObjectPtr<UObject>> Objects;
        InDetailBuilder.GetObjectsBeingCustomized(Objects);

        // 根据资产状态自定义属性显示，例如隐藏或分类某些属性
        InDetailBuilder.EditCategory("CategoryName", FText::GetEmpty(), ECategoryPriority::Important)
            .AddProperty(InDetailBuilder.GetProperty(GET_MEMBER_NAME_CHECKED(UMyMetaHumanFaceAnimationSolver, SomeProperty)));
    }
};

// 在编辑器启动时注册自定义（例如在IModuleInterface的StartupModule中）
FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
PropertyModule.RegisterCustomClassLayout(
    UMetaHumanFaceAnimationSolver::StaticClass()->GetFName(),
    FOnGetDetailCustomizationInstance::CreateStatic(&FMyCustomFaceSolverCustomization::MakeInstance)
);
```
*(示例逻辑基于 `MetaHumanFaceAnimationSolverCustomizations.h` 的结构推断)*

### 进阶用法

结合 `UFactory` 创建自定义资产。
```cpp
#include "Factories/Factory.h"
#include "MetaHumanFaceAnimationSolver.h"

UCLASS()
class UMyCustomSolverFactory : public UFactory
{
    GENERATED_BODY()

public:
    UMyCustomSolverFactory()
    {
        SupportedClass = UMetaHumanFaceAnimationSolver::StaticClass();
        bCreateNew = true;
        bEditAfterNew = true;
    }

    virtual UObject* FactoryCreateNew(UClass* InClass, UObject* InParent, FName InName, EObjectFlags InFlags, UObject* Context, FFeedbackContext* Warn) override
    {
        UMetaHumanFaceAnimationSolver* NewSolver = NewObject<UMetaHumanFaceAnimationSolver>(InParent, InClass, InName, InFlags);
        // 在此处对新创建的求解器对象进行初始化设置
        // NewSolver->InitializeDefaultSettings();
        return NewSolver;
    }
};
```
*(示例逻辑基于 `MetaHumanFaceAnimationSolverFactoryNew.h` 的结构推断)*

## Demo 示例

一个最小化的自定义细节面板注册示例（.h + .cpp）。

**MyFaceSolverCustomization.h**
```cpp
#pragma once
#include "IDetailCustomization.h"

class FMyFaceSolverCustomization : public IDetailCustomization
{
public:
    static TSharedRef<IDetailCustomization> MakeInstance();
    virtual void CustomizeDetails(IDetailLayoutBuilder& DetailLayout) override;
};
```

**MyFaceSolverCustomization.cpp**
```cpp
#include "MyFaceSolverCustomization.h"
#include "DetailLayoutBuilder.h"
#include "DetailCategoryBuilder.h"
#include "DetailWidgetRow.h"
#include "MetaHumanFaceAnimationSolver.h"

TSharedRef<IDetailCustomization> FMyFaceSolverCustomization::MakeInstance()
{
    return MakeShareable(new FMyFaceSolverCustomization());
}

void FMyFaceSolverCustomization::CustomizeDetails(IDetailLayoutBuilder& DetailLayout)
{
    // 隐藏 “Advanced” 分类
    DetailLayout.HideCategory(FName("Advanced"));

    // 获取并编辑 “Settings” 分类
    IDetailCategoryBuilder& SettingsCategory = DetailLayout.EditCategory(
        FName("Settings"),
        LOCTEXT("MyCategory", "My Custom Settings"),
        ECategoryPriority::Important
    );

    // 添加一个自定义行
    SettingsCategory.AddCustomRow(LOCTEXT("MyRow", "My Row"))
    .NameContent()
    [
        SNew(STextBlock)
        .Text(LOCTEXT("MyRowLabel", "Enable Special Mode"))
    ]
    .ValueContent()
    [
        SNew(SCheckBox)
        .IsChecked(ECheckBoxState::Checked) // 示例状态
    ];
}
```

## 模块依赖

当前模块 `MetaHumanFaceAnimationSolverEditor` 无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能，避免冲突 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色上的渲染瑕疵（artifact） |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪模式下过滤可视化对象，优化显示 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为现有网格体导出动画序列，增强功能 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer（定序器）的缓存问题，提升稳定性 |

### 维护评价

MetaHuman Animator 插件正处于**积极维护**状态。从 git 日志可见，过去一周内有多次实质性更新，内容涵盖**新功能开发**（如为现有网格导出动画）、**关键Bug修复**（渲染瑕疵、缓存问题）以及**功能优化**（身体追踪模式下的过滤）。作为 Epic Games 官方推出的 MetaHuman 核心工具链，它与 Unreal Engine 的集成紧密，且开发活跃，是实现高质量数字人动画的推荐方案。当前模块 `MetaHumanFaceAnimationSolverEditor` 作为其编辑器支持的一部分，也随着主插件一同更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/meta-human-animator-in-unreal-engine/)（MetaHuman Animator 官方文档链接）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceAnimationSolverEditor) (编辑器模块源码)