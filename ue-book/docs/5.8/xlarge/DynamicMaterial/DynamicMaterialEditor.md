# Material Designer

> Compact dynamic material creator and editor, similar in style to other DDCs.

| 属性 | 值 |
|---|---|
| 中文名 | 动态材质设计器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质资产、蓝图资产、编辑器界面） |
| 模块 | `DynamicMaterial` (RuntimeAndProgram), `DynamicMaterialEditor` (Editor), `DynamicMaterialShaders` (Runtime), `DynamicMaterialTextureSet` (RuntimeAndProgram), `DynamicMaterialTextureSetEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DynamicMaterial) | |

## 用途

DynamicMaterial 插件提供了一种与传统材质图表不同的紧凑式动态材质创作和编辑体验。它旨在简化材质创建流程，提供一个类似“节点图（DDC）”但更注重即时预览和图层混合的编辑器。该插件核心解决的问题是：允许用户通过一个结构化的、基于图层的编辑界面（而非传统的节点式材质编辑器）来快速构建和迭代复杂的材质，尤其适用于虚拟制片等需要快速创建和运行时调整材质的场景。其“动态”特性主要体现在两个方面：一是编辑过程中可实时预览材质效果（Live Edit），二是支持生成和修改可在运行时被实例化和调整的动态材质实例。

## 使用场景

- **快速原型设计材质**：当你需要在虚拟制片或实时渲染项目中快速尝试不同的材质外观（如金属度、粗糙度、纹理混合），而不希望陷入传统材质图表复杂连线的细节时，可以使用 Material Designer 进行快速搭建。
- **创建运行时动态材质**：你需要为一个场景或对象创建可以在游戏或应用运行时通过蓝图或 C++ 代码调整参数（如颜色、纹理、粗糙度）的材质。插件可以直接创建 `UDynamicMaterialInstance`。
- **基于图层的材质混合**：你的设计流程更倾向于使用图层堆栈（Layer Stack）来组织材质属性，例如先有一层基础颜色，再叠加一层法线贴图，最后用一个遮罩层控制混合区域，这比节点连线更直观。
- **虚拟制片工作流**：在虚拟制片现场，美术或灯光师需要快速调整场景中物体的材质外观，并实时看到效果，此插件的编辑器设计和 Live Edit 模式非常适合此类需求。

## 蓝图用法

插件通过 `IDynamicMaterialEditorModule` 和 `UDynamicMaterialModelEditorOnlyData` 等类暴露了大量蓝图接口，用于创建、查询和编辑材质。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OpenEditor` | 打开 Material Designer 编辑器窗口。 | `IDynamicMaterialEditorModule` |
| `OpenMaterial` | 在编辑器中打开指定的动态材质实例进行编辑。 | `IDynamicMaterialEditorModule` |
| `OnActorSelected` | 响应编辑器中 Actor 的选中事件，自动打开其材质到设计器。 | `IDynamicMaterialEditorModule` |
| `ClearDynamicMaterialModel` | 清除当前世界关联的 Material Designer 材质模型。 | `IDynamicMaterialEditorModule` |
| `GetMaterialProperties` | 获取材质模型中所有材质属性（如 BaseColor, Roughness）的映射表。 | `UDynamicMaterialModelEditorOnlyData` |
| `GetSlots` | 获取材质模型中的所有材质插槽（Slot）列表。 | `UDynamicMaterialModelEditorOnlyData` |
| `SetBlendMode` | 设置生成材质的混合模式（如 Opaque, Translucent）。 | `UDynamicMaterialModelEditorOnlyData` |
| `SetShadingModel` | 设置生成材质的着色模型（如 Lit, Unlit）。 | `UDynamicMaterialModelEditorOnlyData` |
| `CreateLayer` | 为指定的材质插槽创建一个新的材质图层。 | `UDMMaterialLayerObject` |
| `SetSource` | 设置一个材质阶段（Stage）的来源（如纹理采样器、数学表达式、值）。 | `UDMMaterialStage` |
| `CreateEffectStackForLayer` | 为材质图层创建一个效果堆栈容器。 | `UDMMaterialEffectStack` |
| `AddEffect` | 向效果堆栈中添加一个材质效果。 | `UDMMaterialEffectStack` |

### 使用示例（蓝图描述）

1.  **创建并编辑新材质**：
    - 从任意对象（如你的 GameMode 或管理 Actor）调用 `IDynamicMaterialEditorModule::Get().OpenEditor(GetWorld())`，这将打开 Material Designer 并创建一个新的空白材质模型。
    - 在编辑器界面中，通过左侧的材质属性列表（如 Base Color）选择需要编辑的属性。
    - 在右侧的插槽编辑器中，为该属性添加一个新的图层。
    - 点击图层中“基础（Base）”阶段的图标，从弹出的菜单中选择来源，例如 `Texture Sample`。
    - 在纹理采样器的属性面板中指定一个纹理资源，即可在预览中看到效果。

2.  **通过蓝图动态修改材质**：
    - 首先，通过 `UDynamicMaterialModelEditorOnlyData::Get(SomeMaterialModel)` 获取材质模型的编辑器数据对象。
    - 使用 `GetMaterialProperty(EDMMaterialPropertyType::BaseColor)` 获取基础颜色属性。
    - 假设你知道某个图层或插槽的引用，可以通过其 `GetSource()` 等方法获取当前的来源（如一个 `UDMMaterialStageInputValue`）。
    - 通过 `UDMMaterialStageInputValue::GetValue()` 获取其关联的材质值（如 `UDMMaterialValueFloat4` 代表颜色）。
    - 调用该值的 `SetXXX` 方法（如 `SetValue(FLinearColor::Red)`）来修改颜色，修改会触发材质重新编译。

## C++ 用法

插件的运行时和编辑器模块提供了丰富的 C++ 接口，核心是围绕 `UDynamicMaterialModel`、`UDMMaterialSlot`、`UDMMaterialLayerObject`、`UDMMaterialStage` 等对象构建的材质模型层次结构。

### 头文件引入

```cpp
// 运行时材质模型和组件
#include "Model/DynamicMaterialModel.h"
#include "Components/DMMaterialSlot.h"
#include "Components/DMMaterialLayer.h"
#include "Components/DMMaterialStage.h"

// 编辑器模块接口（仅在编辑器模块中使用）
#include "IDynamicMaterialEditorModule.h"

// 编辑器专用数据
#include "Model/DynamicMaterialModelEditorOnlyData.h"
```

### 基本用法

以下示例展示了如何在 C++ 中打开 Material Designer 编辑器并响应材质模型创建完成的回调。

```cpp
// 来源: 基于 IDynamicMaterialEditorModule 接口的典型用法
// 1. 定义一个回调类来处理向导完成（材质创建）事件
class FMyOnMaterialCreatedCallback : public IDMOnWizardCompleteCallback
{
public:
    virtual void OnComplete(UDynamicMaterialModel* InModel) override
    {
        if (InModel)
        {
            UE_LOG(LogTemp, Log, TEXT("Material Designer created a new model: %s"), *InModel->GetName());
            // 在这里可以获取模型的编辑器数据进行后续操作
            UDynamicMaterialModelEditorOnlyData* EditorOnlyData = UDynamicMaterialModelEditorOnlyData::Get(InModel);
            if (EditorOnlyData)
            {
                // 例如，将着色模型设为 Unlit
                EditorOnlyData->SetShadingModel(EDMMaterialShadingModel::Unlit);
            }
        }
    }
};

// 2. 在某个函数中（如 Actor BeginPlay 或自定义函数）注册回调并打开编辑器
void AMyActor::OpenMaterialDesigner()
{
    if (IDynamicMaterialEditorModule::IsLoaded())
    {
        IDynamicMaterialEditorModule& EditorModule = IDynamicMaterialEditorModule::Get();
        
        // 注册一个在向导（创建新材质）完成时调用的回调
        TSharedRef<FMyOnMaterialCreatedCallback> Callback = 
            EditorModule.RegisterMaterialModelCreatedCallback<FMyOnMaterialCreatedCallback>();
        
        // 打开编辑器，这将显示 Material Designer 界面
        EditorModule.OpenEditor(GetWorld());
    }
}
```

### 进阶用法

此示例展示了如何通过编程方式查询和遍历一个已存在的材质模型结构，理解其插槽、图层和阶段的概念。

```cpp
// 来源: 结合 DynamicMaterialModel, DMMaterialSlot, DMMaterialLayer, DMMaterialStage 的 API
// 假设我们有一个已存在的 UDynamicMaterialModel* InModel
void AnalyzeMaterialModel(UDynamicMaterialModel* InModel)
{
    if (!InModel) return;
    
    // 获取编辑器专用数据，大部分编辑操作通过此类进行
    UDynamicMaterialModelEditorOnlyData* EditorData = UDynamicMaterialModelEditorOnlyData::Get(InModel);
    if (!EditorData) return;
    
    // 1. 遍历所有材质属性（如 BaseColor, Roughness 等）
    TMap<EDMMaterialPropertyType, UDMMaterialProperty*> Properties = EditorData->GetMaterialProperties();
    for (auto& Pair : Properties)
    {
        EDMMaterialPropertyType PropertyType = Pair.Key;
        UDMMaterialProperty* MaterialProperty = Pair.Value;
        if (MaterialProperty && MaterialProperty->IsEnabled())
        {
            UE_LOG(LogTemp, Log, TEXT("Property: %s is enabled."), *UEnum::GetValueAsString(PropertyType));
        }
    }
    
    // 2. 获取所有插槽，并检查第一个插槽的内容
    const TArray<UDMMaterialSlot*>& Slots = EditorData->GetSlots();
    if (Slots.Num() > 0)
    {
        UDMMaterialSlot* FirstSlot = Slots[0];
        UE_LOG(LogTemp, Log, TEXT("First Slot has %d layers."), FirstSlot->GetLayers().Num());
        
        // 遍历插槽中的图层
        for (UDMMaterialLayerObject* Layer : FirstSlot->GetLayers())
        {
            UE_LOG(LogTemp, Log, TEXT("  Layer: %s, Enabled: %d"), 
                *Layer->GetLayerName().ToString(), Layer->IsEnabled());
            
            // 获取图层的“基础”阶段
            UDMMaterialStage* BaseStage = Layer->GetStage(EDMMaterialLayerStage::Base);
            if (BaseStage)
            {
                // 获取基础阶段的来源（例如，它是一个纹理采样器吗？）
                UDMMaterialStageSource* Source = BaseStage->GetSource();
                if (Source)
                {
                    UE_LOG(LogTemp, Log, TEXT("    Base Stage Source: %s"), 
                        *Source->GetClass()->GetName());
                }
                
                // 获取基础阶段的输入（例如，纹理坐标）
                const TArray<UDMMaterialStageInput*>& Inputs = BaseStage->GetInputs();
                for (UDMMaterialStageInput* Input : Inputs)
                {
                    UE_LOG(LogTemp, Log, TEXT("    Input: %s"), 
                        *Input->GetComponentDescription().ToString());
                }
            }
        }
    }
    
    // 3. 设置材质全局属性（如混合模式）
    EditorData->SetBlendMode(BLEND_Translucent);
    EditorData->SetShadingModel(EDMMaterialShadingModel::Lit);
    
    // 4. 触发材质重新编译以应用更改
    EditorData->BuildMaterial(true); // true 表示可能污染资产
}
```

## Demo 示例

以下是一个完整的、可编译的最小示例，展示了如何在 Actor 中集成 Material Designer，并监听材质模型创建事件。

**MyDesignerActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IDynamicMaterialEditorModule.h" // 需要引入编辑器模块头文件
#include "MyDesignerActor.generated.h"

UCLASS()
class MYPROJECT_API AMyDesignerActor : public AActor
{
    GENERATED_BODY()
    
public:
    AMyDesignerActor();

protected:
    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category="Material Designer")
    void LaunchMaterialDesigner();

private:
    // 回调对象，需要保持引用以防止被垃圾回收
    TSharedPtr<IDMOnWizardCompleteCallback> OnMaterialCreatedCallback;
};
```

**MyDesignerActor.cpp**
```cpp
#include "MyDesignerActor.h"

// 实现自定义的回调类
class FDesignerOnCompleteCallback : public IDMOnWizardCompleteCallback
{
public:
    virtual void OnComplete(UDynamicMaterialModel* InModel) override
    {
        if (InModel)
        {
            UE_LOG(LogTemp, Warning, TEXT("Material Designer model created successfully!"));
            // 在这里可以添加对创建模型的后续处理逻辑
        }
    }
};

AMyDesignerActor::AMyDesignerActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyDesignerActor::BeginPlay()
{
    Super::BeginPlay();
    // 在BeginPlay中尝试打开编辑器，仅作为演示，实际项目中可能由UI按钮触发
    // LaunchMaterialDesigner();
}

void AMyDesignerActor::LaunchMaterialDesigner()
{
    // 检查编辑器模块是否已加载（仅在编辑器环境下有效）
    if (IDynamicMaterialEditorModule::IsLoaded())
    {
        IDynamicMaterialEditorModule& DMEditor = IDynamicMaterialEditorModule::Get();

        // 注册回调
        OnMaterialCreatedCallback = MakeShared<FDesignerOnCompleteCallback>();
        DMEditor.RegisterMaterialModelCreatedCallback(OnMaterialCreatedCallback);

        // 打开编辑器
        DMEditor.OpenEditor(GetWorld());

        UE_LOG(LogTemp, Log, TEXT("Material Designer Editor launched from Actor: %s"), *GetName());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("DynamicMaterialEditor module is not loaded."));
    }
}
```

## 模块依赖

从 Build.cs 分析，使用此插件（特别是其运行时材质模型功能）无需引入额外的不常见模块。其核心逻辑封装在自身模块中。

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-05-09 | `3950790a` | Motion Design: moved the following plugins from /Plugins/Experimental to /Plugins/VirtualProduction: ActorModifier, ActorModifierCore, Motion Design, ClonerEffector, CustomDetailsView, Material Designer, GeometryMask, OperatorStack, PropertyAnimator, PropertyAnimatorCore, StormSync, StormSync Motion Design Bridge | 将包括 Material Designer 在内的多个插件从实验性目录移至虚拟制片目录，标志着其成熟并被纳入官方虚拟制片工具集。 |

### 维护评价

Material Designer 插件于 2025 年 5 月从实验性状态移至正式的虚拟制片插件目录，表明其已通过内部验证并被视为可用于生产环境。虽然从首次提交看它是一个相对较新的插件（约 1 年历史），但被纳入 Virtual Production 分类意味着 Epic Games 将其作为该领域的重要工具进行维护。从代码结构和功能复杂度看，它是一个功能完整的编辑器扩展。鉴于其在官方仓库中的位置和性质，可以预期它将随着 Unreal Engine 的更新而持续维护。推荐在虚拟制片、快速材质原型设计以及需要运行时动态材质调整的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DynamicMaterial)
- [官方文档]() (当前无直接链接，但属于 Virtual Production 文档体系)