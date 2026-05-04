# Material Designer

> Compact dynamic material creator and editor, similar in style to other DDCs.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质资产、材质函数、纹理集） |
| 模块 | `DynamicMaterial` (Runtime), `DynamicMaterialTextureSet` (Runtime), `DynamicMaterialEditor` (Editor), `DynamicMaterialTextureSetEditor` (Editor), `DynamicMaterialShaders` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-28 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DynamicMaterial) | |

---

## 用途

Material Designer 是一个**基于图层的动态材质可视化编辑系统**，类似于 Photoshop 的图层混合模式工作流，用于在运行时和编辑器中创建、编辑和组合材质。

它解决的核心问题是：传统材质编辑器（Material Editor 蓝图节点图）过于复杂且不适合快速迭代，而 Material Designer 提供了一种**紧凑的、数据驱动的**材质创作方式，通过以下机制工作：

- **图层混合（Blend Stages）**：提供 20+ 种 Photoshop 风格的混合模式（Add、Multiply、Screen、Overlay、Color Dodge、Color Burn、Hard Light、Soft Light 等），每个混合模式底层对应一个材质函数（Material Function）
- **渐变生成器（Gradients）**：内置线性渐变和径向渐变，支持平铺和镜像
- **表达式节点（Expressions）**：如纹理坐标等材质表达式节点
- **纹理集（Texture Set）**：将一组相关纹理（Base Color、Normal、ORM 等）打包为一个资产，快速应用到材质模型
- **效果栈预设（Effect Stack Presets）**：保存和加载材质效果组合
- **运行时材质实例**：通过 `UDynamicMaterialInstance` 在运行时动态创建和修改材质实例

该插件属于 **Virtual Production** 分类，主要面向虚拟制片场景中需要快速迭代材质外观的工作流。

> ⚠️ 该插件默认未启用（`Installed: false`），需要在项目设置中手动启用。

---

## 使用场景

- 你在做虚拟制片，需要快速调整场景中物体的材质外观 → 用 Material Designer 的图层混合系统
- 你需要在运行时根据游戏状态动态改变材质（如天气效果、损坏程度）→ 用 `UDynamicMaterialInstance`
- 你有一组 PBR 纹理（Base Color + Normal + ORM），想快速应用到材质 → 用 Texture Set 功能
- 你想保存一组材质效果组合以便复用 → 用 Effect Stack Preset 子系统
- 你需要 Photoshop 风格的混合模式来组合多个材质层 → 用内置的 20+ 种 Blend 模式

---

## 模块架构

本插件包含 5 个模块，按职责划分：

| 模块 | 类型 | 职责 |
|---|---|---|
| `DynamicMaterial` | Runtime | 核心运行时：材质模型、材质实例、值类型、阶段、槽位等基础数据结构 |
| `DynamicMaterialTextureSet` | Runtime | 纹理集运行时：纹理集资产定义和管理 |
| `DynamicMaterialEditor` | Editor | 编辑器：Material Designer UI、混合模式、渐变、表达式、蓝图函数库 |
| `DynamicMaterialTextureSetEditor` | Editor | 纹理集编辑器：纹理集的编辑器集成 |
| `DynamicMaterialShaders` | Runtime | 着色器：自定义着色器代码（PostConfigInit 加载） |

---

## 蓝图用法

### 核心节点 — 效果栈预设管理

来自 `UDMMaterialEffectStackPresetSubsystem`（编辑器子系统）：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SavePreset` | 将效果栈配置保存为命名预设 | `UDMMaterialEffectStackPresetSubsystem` |
| `LoadPreset` | 按名称加载效果栈预设 | `UDMMaterialEffectStackPresetSubsystem` |
| `RemovePreset` | 删除指定预设 | `UDMMaterialEffectStackPresetSubsystem` |
| `GetPresetNames` | 获取所有已保存预设的名称列表 | `UDMMaterialEffectStackPresetSubsystem` |

### 核心节点 — 纹理集集成

来自 `UDMTextureSetFunctionLibrary`：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddTextureSetToModel` | 将纹理集集成到材质模型的编辑器数据中，可选择替换或追加槽位 | `UDMTextureSetFunctionLibrary` |

### 核心节点 — 渐变控制

来自 `UDMMaterialStageGradientLinear`：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetTilingType` | 获取线性渐变的平铺类型（不平铺/平铺/平铺并镜像） | `UDMMaterialStageGradientLinear` |
| `SetTilingType` | 设置线性渐变的平铺类型 | `UDMMaterialStageGradientLinear` |

### 使用示例（蓝图描述）

**保存和加载材质效果预设：**

1. 获取 `UDMMaterialEffectStackPresetSubsystem` 实例（通过 `Get Editor Subsystem` 节点）
2. 构造 `FDMMaterialEffectStackJson` 数据结构
3. 调用 `SavePreset`，传入预设名称和数据
4. 之后可通过 `GetPresetNames` 列出所有预设，`LoadPreset` 恢复

**将纹理集应用到材质模型：**

1. 获取目标 Actor 的 `UDynamicMaterialModelEditorOnlyData`
2. 准备一个 `UDMTextureSet` 资产引用
3. 调用 `AddTextureSetToModel`，设置 `bInReplaceSlots` 为 true（完全替换）或 false（追加）

---

## C++ 用法

### 头文件引入

```cpp
// 核心运行时
#include "DynamicMaterialModule.h"

// 编辑器功能（仅在编辑器模块中使用）
#include "Components/DMMaterialStageBlendFunction.h"
#include "Components/DMMaterialStageGradient.h"
#include "Utils/DMMaterialInstanceFunctionLibrary.h"
#include "Utils/DMMaterialEffectStackPresetSubsystem.h"
#include "Utils/DMTextureSetFunctionLibrary.h"
```

### 基本用法 — 获取 Actor 的材质属性

从 `UDMMaterialInstanceFunctionLibrary` 提取：

```cpp
// 获取 Actor 上所有可设置的材质属性
TArray<FDMObjectMaterialProperty> MaterialProperties = 
    UDMMaterialInstanceFunctionLibrary::GetActorMaterialProperties(MyActor);

// 在某个材质属性上创建新的动态材质模型
UDynamicMaterialModel* MaterialModel = 
    UDMMaterialInstanceFunctionLibrary::CreateMaterialInObject(MaterialProperties[0]);

// 将已有的材质实例设置到对象上
UDMMaterialInstanceFunctionLibrary::SetMaterialInObject(MaterialProperties[0], MyMaterialInstance);
```

### 基本用法 — 纹理集集成

```cpp
// 将纹理集集成到材质模型
UDynamicMaterialModelEditorOnlyData* EditorOnlyData = /* 获取编辑器数据 */;
UDMTextureSet* TextureSet = /* 加载纹理集资产 */;

bool bSuccess = UDMTextureSetFunctionLibrary::AddTextureSetToModel(
    EditorOnlyData, 
    TextureSet, 
    true  // bInReplaceSlots: true=替换, false=追加
);
```

### 进阶用法 — 效果栈预设管理

```cpp
// 获取编辑器子系统
UDMMaterialEffectStackPresetSubsystem* PresetSubsystem = 
    UDMMaterialEffectStackPresetSubsystem::Get();

// 保存预设
FDMMaterialEffectStackJson PresetData;
// ... 填充预设数据 ...
PresetSubsystem->SavePreset(TEXT("MyPreset"), PresetData);

// 列出所有预设
TArray<FString> PresetNames = PresetSubsystem->GetPresetNames();

// 加载预设
FDMMaterialEffectStackJson LoadedPreset;
if (PresetSubsystem->LoadPreset(TEXT("MyPreset"), LoadedPreset))
{
    // 使用加载的预设数据
}
```

### 进阶用法 — 自定义混合模式

所有混合模式都继承自 `UDMMaterialStageBlendFunction`，该基类通过材质函数实现混合逻辑：

```cpp
// 混合模式类层次结构
// UDMMaterialStageBlend (抽象基类)
//   └── UDMMaterialStageBlendFunction (基于材质函数的混合基类)
//         ├── UDMMaterialStageBlendAdd          (线性减淡/加法)
//         ├── UDMMaterialStageBlendMultiply      (正片叠底)
//         ├── UDMMaterialStageBlendScreen        (滤色)
//         ├── UDMMaterialStageBlendOverlay       (叠加)
//         ├── UDMMaterialStageBlendColorDodge    (颜色减淡)
//         ├── UDMMaterialStageBlendColorBurn     (颜色加深)
//         ├── UDMMaterialStageBlendHardLight     (强光)
//         ├── UDMMaterialStageBlendSoftLight     (柔光)
//         ├── UDMMaterialStageBlendDifference    (差值)
//         ├── UDMMaterialStageBlendExclusion     (排除)
//         ├── UDMMaterialStageBlendHue           (色相)
//         ├── UDMMaterialStageBlendSaturation    (饱和度)
//         ├── UDMMaterialStageBlendColor         (颜色)
//         ├── UDMMaterialStageBlendLuminosity    (明度)
//         └── ... 更多混合模式
//   └── UDMMaterialStageBlendContrastBase (对比度相关混合基类)
```

---

## 内置混合模式一览

Material Designer 提供了完整的 Photoshop 风格混合模式集合：

| 混合模式 | 类名 | 说明 |
|---|---|---|
| Add (Linear Dodge) | `UDMMaterialStageBlendAdd` | 加法混合，与线性减淡相同 |
| Subtract | `UDMMaterialStageBlendSubtract` | 减法混合 |
| Multiply | `UDMMaterialStageBlendMultiply` | 正片叠底 |
| Divide | `UDMMaterialStageBlendDivide` | 划分混合 |
| Screen | `UDMMaterialStageBlendScreen` | 滤色 |
| Overlay | `UDMMaterialStageBlendOverlay` | 叠加 |
| Darken | `UDMMaterialStageBlendDarken` | 变暗 |
| Lighten | `UDMMaterialStageBlendLighten` | 变亮 |
| Darken Color | `UDMMaterialStageBlendDarkenColor` | 颜色变暗 |
| Lighten Color | `UDMMaterialStageBlendLightenColor` | 颜色变亮 |
| Color Dodge | `UDMMaterialStageBlendColorDodge` | 颜色减淡 |
| Color Burn | `UDMMaterialStageBlendColorBurn` | 颜色加深 |
| Linear Dodge | `UDMMaterialStageBlendLinearDodge` | 线性减淡 |
| Linear Burn | `UDMMaterialStageBlendLinearBurn` | 线性加深 |
| Hard Light | `UDMMaterialStageBlendHardLight` | 强光 |
| Soft Light | `UDMMaterialStageBlendSoftLight` | 柔光 |
| Vivid Light | `UDMMaterialStageBlendVividLight` | 亮光 |
| Linear Light | `UDMMaterialStageBlendLinearLight` | 线性光 |
| Pin Light | `UDMMaterialStageBlendPinLight` | 点光 |
| Hard Mix | `UDMMaterialStageBlendHardMix` | 实色混合 |
| Difference | `UDMMaterialStageBlendDifference` | 差值 |
| Exclusion | `UDMMaterialStageBlendExclusion` | 排除 |
| Hue | `UDMMaterialStageBlendHue` | 色相 |
| Saturation | `UDMMaterialStageBlendSaturation` | 饱和度 |
| Color | `UDMMaterialStageBlendColor` | 颜色 |
| Luminosity | `UDMMaterialStageBlendLuminosity` | 明度 |

---

## 内置渐变类型

| 渐变类型 | 类名 | 说明 |
|---|---|---|
| 线性渐变 | `UDMMaterialStageGradientLinear` | 支持三种平铺模式：NoTile、Tile、TileAndMirror |
| 径向渐变 | `UDMMaterialStageGradientRadial` | 从中心向外辐射的圆形渐变 |

---

## Demo 示例

### 动态创建材质并应用到 Actor

```cpp
// MyMaterialActor.h
#pragma once

#include "GameFramework/Actor.h"
#include "MyMaterialActor.generated.h"

class UDynamicMaterialModel;
class UDynamicMaterialInstance;
class UDynamicMaterialModelEditorOnlyData;
class UDMTextureSet;

UCLASS()
class AMyMaterialActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMaterialActor();

    /** 创建动态材质并应用纹理集 */
    UFUNCTION(BlueprintCallable)
    void ApplyTextureSet(UDMTextureSet* InTextureSet);

    /** 获取当前的动态材质模型 */
    UFUNCTION(BlueprintPure)
    UDynamicMaterialModel* GetMaterialModel() const { return MaterialModel; }

protected:
    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UDynamicMaterialModel> MaterialModel;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UDynamicMaterialInstance> MaterialInstance;
};
```

```cpp
// MyMaterialActor.cpp
#include "MyMaterialActor.h"

#include "Components/StaticMeshComponent.h"
#include "DynamicMaterialInstance.h"
#include "DynamicMaterialModel.h"
#include "DynamicMaterialModelEditorOnlyData.h"
#include "DMTextureSet.h"
#include "Utils/DMMaterialInstanceFunctionLibrary.h"
#include "Utils/DMTextureSetFunctionLibrary.h"

AMyMaterialActor::AMyMaterialActor()
{
    PrimaryActorTick.bCanEverTick = false;

    USceneComponent* Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    SetRootComponent(Root);

    UStaticMeshComponent* Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    Mesh->SetupAttachment(Root);
}

void AMyMaterialActor::ApplyTextureSet(UDMTextureSet* InTextureSet)
{
    if (!InTextureSet)
    {
        return;
    }

    // 获取此 Actor 的材质属性
    TArray<FDMObjectMaterialProperty> MaterialProperties = 
        UDMMaterialInstanceFunctionLibrary::GetActorMaterialProperties(this);

    if (MaterialProperties.Num() == 0)
    {
        return;
    }

    // 在第一个材质属性上创建动态材质模型
    MaterialModel = UDMMaterialInstanceFunctionLibrary::CreateMaterialInObject(
        MaterialProperties[0]
    );

    if (!MaterialModel)
    {
        return;
    }

    // 获取编辑器数据并集成纹理集
    UDynamicMaterialModelEditorOnlyData* EditorOnlyData = MaterialModel->GetEditorOnlyData();
    if (EditorOnlyData)
    {
        UDMTextureSetFunctionLibrary::AddTextureSetToModel(
            EditorOnlyData, 
            InTextureSet, 
            true  // 替换现有槽位
        );
    }
}
```

---

## 模块依赖

从 Build.cs 分析，该插件依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `CustomDetailsView` | 自定义详情面板视图（插件级依赖，用于 Material Designer 的属性编辑 UI） |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

---

## 维护状态

### 近期更新

```
- 669cf6efd8dd Material Designer: Disabled substrate material support.
- 1bc0c17b95df Material Designer: Now checks if properties are keyable when displaying keyframe buttons.
- f992976238f7 Material Designer: The "Material Settings" and "Material Type" categories are now localized.
```

### 维护评价

- **创建时间**：2024 年 1 月，属于较新的插件
- **更新频率**：持续有功能性更新（禁用 Substrate 支持、关键帧按钮改进、本地化）
- **维护状态**：**活跃维护中** — 由 Epic Games 官方维护，属于 Virtual Production 工具链的一部分
- **已知限制**：Substrate 材质系统支持已被禁用（commit 669cf6e），说明该功能尚不稳定
- **推荐程度**：✅ 推荐用于虚拟制片场景中的快速材质迭代工作流。该插件规模庞大（1148 个源文件），功能完善，且由 Epic 官方持续维护

> ⚠️ 注意：该插件默认未启用（`Installed: false`），需要在项目的 `.uproject` 文件或插件设置中手动启用。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DynamicMaterial)
- [DynamicMaterial 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DynamicMaterial/Source/DynamicMaterial)
- [DynamicMaterialEditor 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DynamicMaterial/Source/DynamicMaterialEditor)
- [DynamicMaterialTextureSet 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DynamicMaterial/Source/DynamicMaterialTextureSet)
- [DynamicMaterialShaders 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DynamicMaterial/Source/DynamicMaterialShaders)