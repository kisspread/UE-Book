# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 元人类动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质、资产、配置等） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一个完整的工具链，用于将真实世界的面部表演数据（通常来自 iPhone 或其他深度摄像头）驱动数字 MetaHuman 角色。它解决了一个核心问题：如何将视频/深度捕获数据转化为高质量的面部动画序列，并将其与 MetaHuman 角色的骨骼绑定系统相匹配。
该插件不仅提供了从数据捕获、跟踪、求解到最终动画生成的全流程管线，还包含了在编辑器中管理捕获数据、创建和配置“身份资产”（MetaHuman Identity）以及批量处理动画性能的工具。

## 使用场景

- **数字人/虚拟偶像制作**：将真人演员的表演实时或离线地应用于 MetaHuman 角色，用于虚拟直播、电影或游戏过场动画。
- **游戏开发**：为游戏中的 NPC 或主角快速生成基于表演捕捉的对话动画，取代手工关键帧动画。
- **内容创作**：短视频创作者希望用自己的面部表情驱动一个高质量的 3D 角色，制作创意内容。

## 蓝图用法

**MetaHumanFaceFittingSolverEditor** 模块主要提供编辑器扩展功能（资产工厂、细节面板定制等），不包含面向运行时的 `BlueprintCallable` 节点。其核心功能通过编辑器内的资产操作和UI交互暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FactoryCreateNew` | 在编辑器中创建新的 `UMetaHumanFaceFittingSolver` 资产实例。 | `UMetaHumanFaceFittingSolverFactoryNew` |
| `CustomizeDetails` | 自定义 `UMetaHumanFaceFittingSolver` 资产在细节面板中的属性布局和UI。 | `FMetaHumanFaceFittingSolverCustomization` |

### 使用示例（蓝图描述）
此模块主要通过编辑器用户界面使用，不涉及蓝图图表的连接：
1.  在内容浏览器中右键点击，选择 `Animation` -> `MetaHuman` -> `Face Fitting Solver` 来创建一个新的资产。
2.  在资产编辑器中打开该资产，细节面板会显示由 `FMetaHumanFaceFittingSolverCustomization` 定制的UI，用于配置面部拟合的关键参数。

## C++ 用法

该模块的C++用法主要涉及扩展编辑器功能，如创建新的资产类型或自定义属性面板。

### 头文件引入

```cpp
#include "MetaHumanFaceFittingSolver.h"
```

### 基本用法
**创建自定义资产工厂** (来源: `Private/MetaHumanFaceFittingSolverFactoryNew.h`)
```cpp
// 自定义资产工厂，用于在编辑器中创建 MetaHumanFaceFittingSolver 资产
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
**为资产添加细节面板定制** (来源: `Private/Customizations/MetaHumanFaceFittingSolverCustomizations.h`)
```cpp
// 为 UMetaHumanFaceFittingSolver 资产提供自定义的细节面板UI
class FMetaHumanFaceFittingSolverCustomization : public IDetailCustomization
{
public:
    static TSharedRef<IDetailCustomization> MakeInstance();
    virtual void CustomizeDetails(IDetailLayoutBuilder& InDetailBuilder) override;
};
```

## Demo 示例

一个最小化的自定义资产定义和细节定制示例。

```cpp
// MyFaceFittingSolverAsset.h
#pragma once
#include "Engine/DataAsset.h"
#include "MyFaceFittingSolverAsset.generated.h"

UCLASS(BlueprintType)
class UMyFaceFittingSolverAsset : public UDataAsset
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Solver")
    float SolverStrength = 1.0f;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Solver")
    bool bUseAdvancedConstraints = false;
};

// MyFaceFittingSolverAssetCustomization.h
#pragma once
#include "IDetailCustomization.h"

class FMyFaceFittingSolverAssetCustomization : public IDetailCustomization
{
public:
    static TSharedRef<IDetailCustomization> MakeInstance();
    virtual void CustomizeDetails(IDetailLayoutBuilder& InDetailBuilder) override;
};

// MyFaceFittingSolverAssetCustomization.cpp
#include "MyFaceFittingSolverAssetCustomization.h"
#include "DetailLayoutBuilder.h"
#include "DetailCategoryBuilder.h"
#include "DetailWidgetRow.h"
#include "MyFaceFittingSolverAsset.h"

TSharedRef<IDetailCustomization> FMyFaceFittingSolverAssetCustomization::MakeInstance()
{
    return MakeShareable(new FMyFaceFittingSolverAssetCustomization());
}

void FMyFaceFittingSolverAssetCustomization::CustomizeDetails(IDetailLayoutBuilder& InDetailBuilder)
{
    IDetailCategoryBuilder& SolverCategory = InDetailBuilder.EditCategory("Solver");
    
    // 添加一个自定义行，当 bUseAdvancedConstraints 为 true 时显示额外信息
    TSharedRef<IPropertyHandle> AdvancedHandle = InDetailBuilder.GetProperty(GET_MEMBER_NAME_CHECKED(UMyFaceFittingSolverAsset, bUseAdvancedConstraints));
    
    SolverCategory.AddCustomRow(LOCTEXT("AdvancedInfoRow", "Advanced Info"))
    .NameContent()
    [
        SNew(STextBlock)
        .Text(LOCTEXT("InfoLabel", "Solver Info"))
    ]
    .ValueContent()
    [
        SNew(STextBlock)
        .Text_Lambda([AdvancedHandle]()
        {
            bool bValue = false;
            AdvancedHandle->GetValue(bValue);
            return bValue ? LOCTEXT("AdvancedEnabled", "Advanced constraints are active.") : LOCTEXT("AdvancedDisabled", "Using standard constraints.");
        })
    ];
}
```

## 模块依赖

从 Build.cs 文件中提取的独特依赖。

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心技术算法库，提供面部拟合、跟踪等底层功能 |
| `MetaHumanCaptureDataEditor` | 提供捕获数据的编辑器集成和查看功能 |
| `MetaHumanSDKEditor` | MetaHuman SDK 的编辑器组件 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为已有网格导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复序列器缓存问题 |

### 维护评价

- **活跃维护**：最近一次更新在 2026 年 5 月，且更新内容涉及功能增强和Bug修复，表明该模块处于 **活跃维护** 状态。
- **功能集成**：作为 MetaHuman 官方工具包的核心组件，它与 Unreal Engine 的渲染、动画系统深度集成，更新通常伴随着引擎版本的发布。
- **推荐使用**：如果你正在使用 MetaHuman 并需要基于捕获数据制作面部动画，这是官方推荐且持续维护的解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceFittingSolverEditor)
- [官方文档](https://docs.unrealengine.com/en-US/metahuman-animator/)