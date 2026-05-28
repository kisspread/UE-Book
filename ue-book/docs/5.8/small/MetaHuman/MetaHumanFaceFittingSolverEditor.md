# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、工具资产） |
| 模块 | `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanAnimator` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanToolkit` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanPlatform` (Runtime), `MeshTrackerInterface` (Runtime), `MetaHumanCaptureSource` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-04-26 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 提供的官方工具包，用于将面部捕捉数据（如视频、设备数据）转换为应用于 MetaHuman 角色的动画。它提供了一个完整的流水线，从数据导入、面部特征追踪、动画求解到最终输出动画序列。该插件解决了从现实世界捕捉数据生成高保真数字人面部动画的核心问题，使得创建逼真、个性化的 MetaHuman 角色动画变得高效且可控。

## 使用场景

- **影视与游戏制作**：需要为数字人角色制作细腻面部表演时。
- **快速原型制作**：使用手机视频快速为 MetaHuman 角色生成对话或情绪动画。
- **专业动捕流程**：整合专业面部捕捉设备的数据，并将其烘焙到 UE5 中的 MetaHuman 骨骼网格体上。
- **批量处理**：对大量捕捉素材进行自动化处理，生成动画序列。

## 蓝图用法

由于 `MetaHumanFaceFittingSolverEditor` 是一个编辑器扩展模块，其主要功能（如资产创建、细节面板自定义）集成在编辑器界面中，而非直接提供运行时蓝图节点。

### 核心节点

本模块主要为编辑器提供扩展功能，不直接暴露蓝图节点。

### 使用示例（蓝图描述）

在内容浏览器中，通过右键菜单 `Create Advanced Asset > Animation > MetaHuman Face Fitting Solver` 创建求解器资产。在资产的“细节”面板中，可以根据提供的自定义界面配置面部拟合参数。

## C++ 用法

本模块主要用于扩展编辑器功能，为 MetaHuman 面部拟合求解器资产提供工厂和细节自定义。

### 头文件引入

由于是编辑器模块，通常在编辑器模块或插件内部使用。

```cpp
#include "MetaHumanFaceFittingSolverFactoryNew.h"
#include "AssetDefinitions/AssetDefinition_MetaHumanFaceFittingSolver.h"
#include "Customizations/MetaHumanFaceFittingSolverCustomizations.h"
```

### 基本用法

通过工厂类在编辑器中程序化地创建 `UMetaHumanFaceFittingSolver` 资产。

```cpp
// 创建 MetaHuman 面部拟合求解器资产的工厂 (用于编辑器)
// 来源：Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceFittingSolverEditor/Private/MetaHumanFaceFittingSolverFactoryNew.h
UCLASS(hidecategories=Object)
class UMetaHumanFaceFittingSolverFactoryNew : public UFactory
{
    GENERATED_BODY()
public:
    UMetaHumanFaceFittingSolverFactoryNew();
    virtual UObject* FactoryCreateNew(UClass* InClass, UObject* InParent, FName InName, EObjectFlags InFlags, UObject* Context, FFeedbackContext* Warn) override;
    virtual FText GetToolTip() const override;
};
```

### 进阶用法

为资产定义自定义外观和在内容浏览器中的分类。

```cpp
// 定义资产在编辑器中的显示名称、颜色、图标和分类
// 来源：Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceFittingSolverEditor/Private/AssetDefinitions/AssetDefinition_MetaHumanFaceFittingSolver.h
UCLASS()
class UAssetDefinition_MetaHumanFaceFittingSolver : public UAssetDefinitionDefault
{
    GENERATED_BODY()
public:
    virtual FText GetAssetDisplayName() const override;
    virtual FLinearColor GetAssetColor() const override;
    virtual TSoftClassPtr<UObject> GetAssetClass() const override;
    virtual TConstArrayView<FAssetCategoryPath> GetAssetCategories() const override;
};
```

自定义资产的细节面板。

```cpp
// 自定义求解器资产在“细节”面板中的布局
// 来源：Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceFittingSolverEditor/Private/Customizations/MetaHumanFaceFittingSolverCustomizations.h
class FMetaHumanFaceFittingSolverCustomization : public IDetailCustomization
{
public:
    static TSharedRef<IDetailCustomization> MakeInstance();
    virtual void CustomizeDetails(IDetailLayoutBuilder& InDetailBuilder) override;
};
```

## Demo 示例

一个简单的编辑器模块示例，展示如何注册资产定义和细节自定义。

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
#include "AssetDefinitions/AssetDefinition_MetaHumanFaceFittingSolver.h"
#include "Customizations/MetaHumanFaceFittingSolverCustomizations.h"
#include "PropertyEditorModule.h"

void FMyEditorModule::StartupModule()
{
    // 注册细节面板自定义
    FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
    PropertyModule.RegisterCustomClassLayout(
        UMetaHumanFaceFittingSolver::StaticClass()->GetFName(),
        FOnGetDetailCustomizationInstance::CreateStatic(&FMetaHumanFaceFittingSolverCustomization::MakeInstance)
    );
    PropertyModule.NotifyCustomizationModuleChanged();
}

void FMyEditorModule::ShutdownModule()
{
    if (FModuleManager::Get().IsModuleLoaded("PropertyEditor"))
    {
        FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
        PropertyModule.UnregisterCustomClassLayout(UMetaHumanFaceFittingSolver::StaticClass()->GetFName());
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库，提供基础算法和工具 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 身体追踪启用时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复MetaHuman上的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MHA] 为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复序列缓存问题 |

### 维护评价

MetaHuman Animator 是 Epic Games 的官方前沿产品，自2023年4月创建以来，处于**极度活跃**的维护状态。从最近的提交记录来看（截至2026年5月），几乎每天都有更新，主要集中在功能增强（如动画序列导出）、问题修复（渲染瑕疵、缓存问题）和与身体追踪系统的整合优化上。该插件是 MetaHuman 工作流的核心组件，其代码质量和维护频率都处于顶级水平，**强烈推荐**在需要创建高保真 MetaHuman 动画的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档]()（请查阅 Epic Games 官方 MetaHuman 文档）