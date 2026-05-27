# Variant Manager

> Manages scene actor variants

| 属性 | 值 |
|---|---|
| 中文名 | 变体管理器 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `VariantManager` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/VariantManager) | |

## 用途

Variant Manager 插件用于创建和管理场景中演员（Actor）的“变体”（Variant）。一个变体代表了场景内一组特定演员及其特定属性（如位置、旋转、缩放、材质、可见性等）的预设状态。通过 Variant Manager，用户可以在一个场景内定义多个变体集（VariantSet），每个变体集包含多个变体，从而实现一个场景内的多个“状态”之间的快速切换。

**核心价值**：解决在单一场景中，需要展示、比较或交互式切换多个预设配置状态的需求。例如，建筑可视化中展示不同家具布局，产品配置器中切换不同材质和颜色，或设计迭代中比较不同灯光设置等。它提供了一个结构化的、可在编辑器和运行时操作的数据模型，来替代复杂的蓝图逻辑或多个独立场景。

## 使用场景

- **建筑/室内可视化**：为一个房间创建“现代风格”、“古典风格”、“空置”等多个变体集，在演示中一键切换。
- **产品配置器**：创建包含不同颜色、材质、附加组件的产品变体，让用户在运行时进行自定义选择。
- **设计迭代**：捕获不同版本的灯光设置、相机角度或环境雾效，方便设计师快速对比。
- **交互式故事/游戏**：根据玩家选择或剧情进度，切换场景中的关键物体状态（如门开/关、灯亮/灭、道具摆放）。
- **自动化测试与批处理**：通过蓝图或Python脚本，系统化地记录和应用场景配置，用于自动化视觉测试或批量渲染。

## 蓝图用法

大部分蓝图功能通过 `UVariantManagerBlueprintLibrary` 静态库暴露。按功能分组如下：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateLevelVariantSetsAsset` | 在指定路径创建一个 `ULevelVariantSets` 资产 | `UVariantManagerBlueprintLibrary` |
| `CreateLevelVariantSetsActor` | 在当前关卡创建一个 `ALevelVariantSetsActor` 并关联资产 | `UVariantManagerBlueprintLibrary` |
| `AddVariantSet` | 向一个 `ULevelVariantSets` 添加新的变体集 | `UVariantManagerBlueprintLibrary` |
| `AddVariant` | 向一个 `UVariantSet` 添加新的变体 | `UVariantManagerBlueprintLibrary` |
| `AddActorBinding` | 将一个演员绑定到指定变体（为其创建捕获） | `UVariantManagerBlueprintLibrary` |
| `CaptureProperty` | 捕获指定演员的指定属性到其绑定的变体中 | `UVariantManagerBlueprintLibrary` |
| `Record` | 从演员当前状态更新捕获属性的记录值 | `UVariantManagerBlueprintLibrary` |
| `Apply` | 将捕获的属性记录值应用回演员 | `UVariantManagerBlueprintLibrary` |
| `GetCapturableProperties` | 获取演员或类上所有可捕获的属性路径 | `UVariantManagerBlueprintLibrary` |
| `Set/Get Value (Bool, Int, Float, Vector, Color...)` | 直接设置/获取 `UPropertyValue` 中记录的具体类型数值 | `UVariantManagerBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **创建基础结构**：
    *   拖拽一个 `CreateLevelVariantSetsAsset` 节点到图表，设置资产名称和路径（如 `/Game/MyConfigurations`）。
    *   接着，拖拽 `CreateLevelVariantSetsActor` 节点，并将上一步的返回值作为输入。这样就在场景中生成了一个可交互的变体管理器Actor。
    *   使用 `AddVariantSet` 和 `AddVariant` 节点，为这个资产创建基础的变体集和变体（例如，变体集“灯光方案”，变体“白天”、“夜晚”）。

2.  **捕获演员状态**：
    *   获取你想要控制的演员（例如，场景中的一个灯光或一个StaticMesh Actor）。
    *   使用 `AddActorBinding` 节点，将该演员绑定到一个具体的变体（例如“白天”变体）。
    *   （可选）使用 `GetCapturableProperties` 节点查询该演员上可捕获的属性列表，例如 `LightComponent->Intensity`。
    *   使用 `CaptureProperty` 节点，输入演员、变体和属性路径（如 `LightComponent.Intensity`），完成属性捕获。

3.  **记录与切换**：
    *   调整好演员的某个状态（例如，将灯光强度调高作为“白天”效果）。
    *   在蓝图中，先获取对应变体中该演员绑定的 `UPropertyValue` 对象（通常通过遍历 `ULevelVariantSets` -> `UVariantSet` -> `UVariant` -> `UVariantObjectBinding` -> `UPropertyValue` 获得）。
    *   拖拽 `Record` 节点，并将该 `UPropertyValue` 传入。这会将当前演员的灯光强度数值保存到变体中。
    *   之后，无论演员被如何修改，只要调用 `Apply` 节点，就能将灯光强度恢复为记录的“白天”数值。
    *   切换到另一个变体（例如“夜晚”），对同一个演员执行相同的 `Record` 步骤，记录一个较低的强度值。之后通过切换不同的 `Apply` 调用，就能实现灯光状态的一键切换。

## C++ 用法

### 头文件引入

```cpp
#include "VariantManager.h"
#include "VariantManagerBlueprintLibrary.h" // 用于蓝图库静态函数
```

### 基本用法

通过模块接口和蓝图库进行操作。以下示例展示如何以编程方式创建一个变体并应用。

```cpp
// 假设在编辑器工具或某个管理器类中
#include "VariantManagerModule.h"
#include "VariantManagerBlueprintLibrary.h"
#include "LevelVariantSets.h"
#include "Variant.h"
#include "VariantObjectBinding.h"
#include "PropertyValue.h"

void SetupVariantProgrammatically()
{
    // 1. 获取或创建 Variant Manager 模块实例
    IVariantManagerModule& VariantManagerModule = IVariantManagerModule::Get();
    ULevelVariantSets* MyLevelVariantSets = UVariantManagerBlueprintLibrary::CreateLevelVariantSetsAsset(TEXT("MyConfig"), TEXT("/Game/"));

    if (MyLevelVariantSets)
    {
        // 2. 使用 FVariantManager 来执行核心操作
        TSharedRef<FVariantManager> VariantManager = VariantManagerModule.CreateVariantManager(MyLevelVariantSets);

        // 3. 创建变体集和变体
        UVariantSet* NewVariantSet = VariantManager->CreateVariantSet(MyLevelVariantSets);
        UVariant* NewVariant = VariantManager->CreateVariant(NewVariantSet);

        // 4. 获取目标演员并创建绑定
        AActor* TargetActor = /* 从世界中获取或 Spawn */;
        TArray<AActor*> Actors = { TargetActor };
        TArray<UVariant*> Variants = { NewVariant };
        // 创建绑定（自动捕获一些基本属性如Transform）
        TArray<UVariantObjectBinding*> Bindings = VariantManager->CreateObjectBindingsAndCaptures(Actors, Variants);

        // 5. 记录当前状态 (更常用的是通过蓝图库的静态方法)
        // UVariantManagerBlueprintLibrary::Record(SpecificPropertyValue);
        // 6. 修改演员状态后，应用记录的值
        // UVariantManagerBlueprintLibrary::Apply(SpecificPropertyValue);
    }
}
```
*注：实际应用中，更多操作是通过 `UVariantManagerBlueprintLibrary` 的静态函数完成，因为它们封装了 `FVariantManager` 的实例化和获取逻辑。*

### 进阶用法

**捕获自定义属性**：除了自动捕获的Transform，可以捕获演员的任意属性。
```cpp
// 获取可捕获属性
TArray<FString> PropertyPaths = UVariantManagerBlueprintLibrary::GetCapturableProperties(MyActor);
// 查找特定属性路径，例如 “StaticMeshComponent.bVisible”
FString TargetPropertyPath = TEXT(“StaticMeshComponent.bVisible”);

// 假设已有绑定 (MyActorBinding)
UPropertyValue* CapturedProp = UVariantManagerBlueprintLibrary::CaptureProperty(MyVariant, MyActor, TargetPropertyPath);
if (CapturedProp)
{
    // 记录可见性为 false
    UVariantManagerBlueprintLibrary::SetValueBool(CapturedProp, false);
    UVariantManagerBlueprintLibrary::Record(CapturedProp);
}
```

**依赖管理**：变体之间可以设置依赖关系，实现激活一个变体时自动激活另一个。
```cpp
FVariantDependency Dependency;
Dependency.bEnabled = true;
Dependency.VariantSet = SomeOtherVariantSet;
Dependency.Variant = SomeOtherVariant;

UVariantManagerBlueprintLibrary::AddDependency(MyVariant, Dependency);
```

## Demo 示例

一个最小化的C++类，用于在编辑器工具中创建一个简单的变体配置。

```cpp
// MyVariantSetupTool.h
#pragma once
#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "MyVariantSetupTool.generated.h"

class ULevelVariantSets;

UCLASS(BlueprintType)
class UMyVariantSetupTool : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "Demo")
    void SetupTwoLightVariants(ULevelVariantSets* InLevelVariantSets, AActor* LightActor);
};

// MyVariantSetupTool.cpp
#include "MyVariantSetupTool.h"
#include "VariantManagerBlueprintLibrary.h"
#include "PropertyValue.h"
#include "Variant.h"
#include "VariantSet.h"

void UMyVariantSetupTool::SetupTwoLightVariants(ULevelVariantSets* InLevelVariantSets, AActor* LightActor)
{
    if (!InLevelVariantSets || !LightActor) return;

    // 1. 创建“照明”变体集
    UVariantSet* LightingVariantSet = UVariantManagerBlueprintLibrary::CreateVariantSetAsset(InLevelVariantSets, TEXT(“Lighting”));

    // 2. 创建“亮”变体
    UVariant* BrightVariant = UVariantManagerBlueprintLibrary::CreateVariantAsset(LightingVariantSet, TEXT(“Bright”));
    UVariantManagerBlueprintLibrary::AddActorBinding(BrightVariant, LightActor);
    // 捕获灯光强度属性 (路径需要根据实际演员调整，如 “PointLightComponent.Intensity”)
    UPropertyValue* BrightIntensityProp = UVariantManagerBlueprintLibrary::CaptureProperty(BrightVariant, LightActor, TEXT(“PointLightComponent.Intensity”));
    if (BrightIntensityProp)
    {
        UVariantManagerBlueprintLibrary::SetValueFloat(BrightIntensityProp, 10000.0f);
        UVariantManagerBlueprintLibrary::Record(BrightIntensityProp);
    }

    // 3. 创建“暗”变体
    UVariant* DimVariant = UVariantManagerBlueprintLibrary::CreateVariantAsset(LightingVariantSet, TEXT(“Dim”));
    UVariantManagerBlueprintLibrary::AddActorBinding(DimVariant, LightActor);
    UPropertyValue* DimIntensityProp = UVariantManagerBlueprintLibrary::CaptureProperty(DimVariant, LightActor, TEXT(“PointLightComponent.Intensity”));
    if (DimIntensityProp)
    {
        UVariantManagerBlueprintLibrary::SetValueFloat(DimIntensityProp, 1000.0f);
        UVariantManagerBlueprintLibrary::Record(DimIntensityProp);
    }

    UE_LOG(LogTemp, Log, TEXT(“Created ‘Lighting’ variant set with ‘Bright’ and ‘Dim’ variants for actor %s.”), *LightActor->GetName());
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `VariantManagerContent` | Variant Manager 所需的特定内容资产（如蓝图、材质等） |
| `DatasmithContent` | 与 Datasmith 导入/导出集成相关的内容 |

*（无其他特殊运行时依赖）*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到 UE_LOGF。 |
| 2026-03-20 | `c5bb9adf` | [AutoViz] Minor updates to Variant Manager | [自动可视化] 对变体管理器进行次要更新。 |
| 2025-10-30 | `0990a715` | Ran UnrealCodeFixup on Fortnite to change all ~Type() {} to instead be ~Type() = default | 在 Fortnite 项目中运行代码修复，将析构函数体改为 = default。 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 在引擎项目中运行代码修复，将析构函数体改为 = default。 |

### 维护评价

- **创建时间**：插件于2019年10月创建，属于 Epic Games 的 Enterprise 工具线。
- **更新频率**：从提交历史看，插件仍**处于维护中**。但近期（过去两年）的更新主要是**编译器警告修复、代码规范化（如析构函数、日志宏）和少量针对特定集成（AutoViz）的调整**，没有大的新功能迭代。
- **实验性状态**：`.uplugin` 中 `IsBetaVersion: true`，表明其仍被视为实验性功能，API和稳定性可能不如正式版插件。
- **已知限制**：作为编辑器插件，其 UI 比较基础。复杂数据类型（如容器类）的捕获支持有限。依赖关系管理相对简单。
- **推荐使用**：对于明确的场景状态切换需求（如产品配置器、建筑可视化演示），它是一个**稳定且实用的解决方案**，尤其适合通过蓝图和Python脚本进行自动化。但对于追求最新UI/UX或需要极端复杂逻辑的用户，可能需要评估其“实验性”状态。整体推荐用于生产，但需注意其 Beta 标签。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/VariantManager)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/) (主要关联 Datasmith 工作流)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/VariantManager/Tests)