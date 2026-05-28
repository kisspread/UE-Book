# Color Grading

> Adds a panel with detailed color grading controls

| 属性 | 值 |
|---|---|
| 中文名 | 调色面板 |
| 分类 | Misc |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ColorGradingEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-06-19 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ColorGrading) | |

## 用途

Color Grading 插件为 UE5 编辑器提供了一个独立的**专业调色面板**，最初从 DisplayCluster（nDisplay）插件中分离出来，使其成为通用的编辑器工具。

该插件的核心功能是将 UObject 上的颜色分级属性以**色轮 + 滑块**的可视化方式呈现，支持对 Saturation（饱和度）、Contrast（对比度）、Gamma、Gain（增益）、Offset（偏移）五个维度分别调节，并按 Shadows（暗部）、Midtones（中间调）、Highlights（亮部）等颜色分级元素分组。

关键设计：
- **数据模型抽象层**（`FColorGradingEditorDataModel`）：通过注册自定义 DataModelGenerator，可以将任意 UObject 的颜色属性映射到统一的色轮界面，无需所有对象共享相同的属性结构
- **对象层级混合器**（基于 ObjectMixer）：左侧提供可扩展的对象树，支持 Actor 及其子对象的颜色分级编辑
- **隐藏插件**（`Hidden: true`）：不在插件浏览器中显示，由编辑器内部自动加载

## 使用场景

- 你需要对场景中的 **PostProcessVolume**、**CameraActor** 等对象进行精细的颜色分级调整 → 使用调色面板
- 你正在开发 **nDisplay** 虚拟制片场景，需要直观地调节多个视口的色温/色彩 → 调色面板原生支持 DisplayCluster
- 你有**自定义的 Actor** 需要颜色分级功能 → 通过 `RegisterColorGradingDataModelGenerator` 注册自定义数据模型生成器
- 你需要为 **Composure** 合成通道调节颜色 → 插件已集成 Composure 颜色分级通道支持

## 蓝图用法

该插件是纯 Editor 模块，不暴露 BlueprintCallable 节点。所有操作通过编辑器 UI 或 C++ API 进行。

## C++ 用法

### 头文件引入

```cpp
#include "IColorGradingEditor.h"
#include "ColorGradingEditorDataModel.h"
#include "ColorGradingMixerObjectFilterRegistry.h"
#include "ColorGradingEditorUtil.h"
```

### 基本用法：打开调色面板

通过模块接口获取面板 Tab ID，或使用工具函数创建启动按钮。

```cpp
// 获取模块实例
IColorGradingEditor& ColorGradingEditor = IColorGradingEditor::Get();

// 获取面板 Tab 的 SpawnerId，用于程序化打开面板
FName TabId = ColorGradingEditor.GetColorGradingTabSpawnerId();
FGlobalTabmanager::Get()->TryInvokeTab(TabId);

// 或在 Details 面板中嵌入一个启动按钮
TSharedRef<SWidget> LaunchButton = ColorGradingEditorUtil::MakeColorGradingLaunchButton(true);
```

### 注册自定义对象到调色面板

```cpp
// 注册一个 Actor 类到调色面板的对象列表中（可在面板中创建该 Actor）
FColorGradingMixerObjectFilterRegistry::RegisterActorClassToPlace(APostProcessVolume::StaticClass());

// 注册一个对象类到调色面板的过滤列表中（可在面板中看到该对象的颜色分级属性）
FColorGradingMixerObjectFilterRegistry::RegisterObjectClassToFilter(
    AMyColorGradableObject::StaticClass(),
    // 可选：提供自定义层级配置
    FGetObjectHierarchyConfig::CreateLambda([]() -> TSharedRef<IColorGradingMixerObjectHierarchyConfig>
    {
        return MakeShared<FMyHierarchyConfig>();
    })
);
```

### 进阶用法：注册自定义数据模型生成器

为自定义 Actor 创建颜色分级数据模型，使其属性在色轮面板中可编辑。参见 `ColorGradingDataModelGenerator_PostProcessVolume` 的实现模式：

```cpp
// 声明数据模型生成器
class FColorGradingDataModelGenerator_MyActor : public IColorGradingEditorDataModelGenerator
{
public:
    static TSharedRef<IColorGradingEditorDataModelGenerator> MakeInstance()
    {
        return MakeShared<FColorGradingDataModelGenerator_MyActor>();
    }

    virtual void Initialize(
        const TSharedRef<FColorGradingEditorDataModel>& ColorGradingDataModel,
        const TSharedRef<IPropertyRowGenerator>& PropertyRowGenerator) override
    {
        // 初始化时的准备工作
    }

    virtual void Destroy(
        const TSharedRef<FColorGradingEditorDataModel>& ColorGradingDataModel,
        const TSharedRef<IPropertyRowGenerator>& PropertyRowGenerator) override
    {
        // 清理工作
    }

    virtual void GenerateDataModel(
        IPropertyRowGenerator& PropertyRowGenerator,
        FColorGradingEditorDataModel& OutColorGradingDataModel) override
    {
        // 从属性行生成器中提取颜色分级属性
        // 将属性句柄分配到 FColorGradingElement 的对应字段（SaturationPropertyHandle 等）
        // 构建 FColorGradingGroup 并添加到 OutColorGradingDataModel.ColorGradingGroups
    }
};

// 在模块启动时注册（通常在 IModuleInterface::StartupModule 中）
FColorGradingEditorDataModel::RegisterColorGradingDataModelGenerator<AMyColorGradableActor>(
    FGetDetailsDataModelGenerator::CreateStatic(&FColorGradingDataModelGenerator_MyActor::MakeInstance)
);
```

## Demo 示例

以下展示如何为自定义 Actor 注册完整的颜色分级支持：

**MyColorGradableActor.h**
```cpp
#pragma once

#include "GameFramework/Actor.h"
#include "MyColorGradableActor.generated.h"

UCLASS()
class AMyColorGradableActor : public AActor
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "Color Grading")
    FLinearColor Saturation = FLinearColor::White;

    UPROPERTY(EditAnywhere, Category = "Color Grading")
    FLinearColor Contrast = FLinearColor::White;
};
```

**MyColorGradingDataModelGenerator.h**
```cpp
#pragma once

#include "ColorGradingEditorDataModel.h"

class FMyColorGradingDataModelGenerator : public IColorGradingEditorDataModelGenerator
{
public:
    static TSharedRef<IColorGradingEditorDataModelGenerator> MakeInstance();

    virtual void Initialize(
        const TSharedRef<FColorGradingEditorDataModel>& ColorGradingDataModel,
        const TSharedRef<IPropertyRowGenerator>& PropertyRowGenerator) override;
    virtual void Destroy(
        const TSharedRef<FColorGradingEditorDataModel>& ColorGradingDataModel,
        const TSharedRef<IPropertyRowGenerator>& PropertyRowGenerator) override;
    virtual void GenerateDataModel(
        IPropertyRowGenerator& PropertyRowGenerator,
        FColorGradingEditorDataModel& OutColorGradingDataModel) override;
};
```

**MyColorGradingDataModelGenerator.cpp**
```cpp
#include "MyColorGradingDataModelGenerator.h"
#include "MyColorGradableActor.h"
#include "PropertyHandle.h"

TSharedRef<IColorGradingEditorDataModelGenerator> FMyColorGradingDataModelGenerator::MakeInstance()
{
    return MakeShared<FMyColorGradingDataModelGenerator>();
}

void FMyColorGradingDataModelGenerator::Initialize(
    const TSharedRef<FColorGradingEditorDataModel>& ColorGradingDataModel,
    const TSharedRef<IPropertyRowGenerator>& PropertyRowGenerator)
{
}

void FMyColorGradingDataModelGenerator::Destroy(
    const TSharedRef<FColorGradingEditorDataModel>& ColorGradingDataModel,
    const TSharedRef<IPropertyRowGenerator>& PropertyRowGenerator)
{
}

void FMyColorGradingDataModelGenerator::GenerateDataModel(
    IPropertyRowGenerator& PropertyRowGenerator,
    FColorGradingEditorDataModel& OutColorGradingDataModel)
{
    // 创建一个颜色分级组
    FColorGradingEditorDataModel::FColorGradingGroup Group;
    Group.DisplayName = FText::FromString(TEXT("My Actor Grading"));

    // 创建一个颜色分级元素（如 Global）
    FColorGradingEditorDataModel::FColorGradingElement Element;
    Element.DisplayName = FText::FromString(TEXT("Global"));

    // 从 PropertyRowGenerator 获取属性句柄
    const TArray<TSharedRef<IDetailTreeNode>>& RootNodes = PropertyRowGenerator.GetRootTreeNodes();
    for (const TSharedRef<IDetailTreeNode>& RootNode : RootNodes)
    {
        TArray<TSharedRef<IDetailTreeNode>> Children;
        RootNode->GetChildren(Children);
        for (const TSharedRef<IDetailTreeNode>& Child : Children)
        {
            TSharedPtr<IPropertyHandle> PropertyHandle = Child->CreatePropertyHandle();
            if (!PropertyHandle.IsValid()) continue;

            FName PropertyName = PropertyHandle->GetProperty()->GetFName();
            if (PropertyName == GET_MEMBER_NAME_CHECKED(AMyColorGradableActor, Saturation))
            {
                Element.SaturationPropertyHandle = PropertyHandle;
            }
            else if (PropertyName == GET_MEMBER_NAME_CHECKED(AMyColorGradableActor, Contrast))
            {
                Element.ContrastPropertyHandle = PropertyHandle;
            }
        }
    }

    Group.ColorGradingElements.Add(Element);
    OutColorGradingDataModel.ColorGradingGroups.Add(Group);
}

// 在编辑器模块启动时注册
static struct FAutoRegisterMyGenerator
{
    FAutoRegisterMyGenerator()
    {
        FColorGradingEditorDataModel::RegisterColorGradingDataModelGenerator<AMyColorGradableActor>(
            FGetDetailsDataModelGenerator::CreateStatic(
                &FMyColorGradingDataModelGenerator::MakeInstance));
    }
} AutoRegisterMyGenerator;
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ObjectMixer` | 对象混合器框架，提供可扩展的对象层级列表和属性面板 |
| `SceneOutliner` | 场景大纲组件，用于构建树形结构和拖放操作 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `708628fd` | nDisplay: Fixed issue in Color Grading drawer where deleting the currently selected color grading gr | 修复删除当前选中的调色分组时的面板异常 |
| 2026-05-01 | `c2ff6527` | [ColorGradingEditor] Fixed crash on group selection | 修复切换调色分组时的崩溃问题 |
| 2025-12-10 | `f38d4a19` | Composure: Added integration with color grading drawer for composure color grading passes. Now, any | 新增 Composure 合成通道的颜色分级面板集成支持 |
| 2025-12-10 | `7a2449bb` | [Backout] - CL49123081 | 回滚了之前的提交 |
| 2025-12-10 | `c44b6434` | Composure: Added integration with color grading drawer for composure color grading passes. Now, any | Composure 集成的原始提交（后被回滚后重新提交） |

### 维护评价

**活跃维护**。该插件创建于 2024 年 6 月（约 2 年前），近期仍有实质性更新：
- 2026 年 5 月连续修复了两个 Bug（崩溃和 UI 状态异常）
- 2025 年 12 月新增了 Composure 集成功能
- 作为隐藏的编辑器核心组件，与 nDisplay/virtual production 工作流紧密绑定

⚠️ 注意：该插件标记为 `Hidden: true`，不在插件浏览器中显示，属于编辑器内部基础设施。默认自动启用，无需手动操作。

**推荐使用**：如果你需要对 PostProcessVolume 或 CameraActor 进行可视化颜色分级，该插件已内置支持。如需为自定义对象扩展颜色分级能力，可参照 DataModelGenerator 模式注册。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ColorGrading)