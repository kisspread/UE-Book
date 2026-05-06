# MutablePopulation

> Extend the Mutable plugin to support Population assets.

| 属性 | 值 |
|---|---|
| 中文名 | 群体人口编辑器 |
| 分类 | CustomizableObjects |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `CustomizableObjectPopulation` (Runtime), `CustomizableObjectPopulationEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-13 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MutablePopulation) | |

## 用途

MutablePopulation 插件基于 Mutable（可变角色系统）扩展，用于创建和管理“群体（Population）”资源。它允许开发者定义一套规则，通过组合不同的身体部分、材质、颜色等参数，自动生成大量外观各异的角色实例。通常用于大规模NPC生成、随机角色创建等场景。

该插件提供两类核心资产：
- **CustomizablePopulationClass**（群体类别）：定义一组可变的参数和约束规则，描述一个“类型”的人群。
- **CustomizablePopulation**（群体配置）：引用多个群体类别，设置每个类别下的实例数量，最终生成一批具体的角色。

编辑器模块（CustomizableObjectPopulationEditor）提供了完整的资产编辑器，包括3D视口预览、标签管理、约束范围编辑等功能。

## 使用场景

- **开放世界NPC填充**：为城市、营地、村庄等场景生成几十到上百个外貌各异的NPC。
- **随机角色创建**：在角色创建界面中，根据预设规则随机组合外观。
- **游戏内动态生成**：运行时根据玩家参数或事件生成特定类型的人群体。
- **性能测试**：快速生成大量高差异角色以测试渲染和动画性能。

## 蓝图用法

该插件主要面向编辑器和工作流，没有直接暴露给蓝图的可调用函数（UFUNCTION(BlueprintCallable)）。所有核心操作通过**资产编辑器**和**自定义类**完成。

在运行时，可以使用C++创建和操作 `UCustomizableObjectPopulation` 和 `UCustomizableObjectPopulationClass` 实例，但这些类目前未标记为Blueprint可见。因此，蓝图用户只能通过C++扩展或使用编辑器内已生成的资源来间接使用。

## C++ 用法

### 头文件引入

```cpp
#include "MuCOP/CustomizableObjectPopulation.h"        // UCustomizableObjectPopulation
#include "MuCOP/CustomizableObjectPopulationClass.h"    // UCustomizableObjectPopulationClass
#include "MuCOPE/CustomizableObjectPopulationEditorModule.h" // 编辑器模块接口
```

### 基本用法

以下示例展示了如何创建和生成群体实例（基于 `Engine/Plugins/Experimental/MutablePopulation/Source/CustomizableObjectPopulation/Private/CustomizableObjectPopulation.cpp` 中的简化逻辑）：

```cpp
// 创建一个群体类别资产（通常通过编辑器创建，这里演示运行时动态构建）
UCustomizableObjectPopulationClass* PopClass = NewObject<UCustomizableObjectPopulationClass>();
PopClass->CustomizableObjectPath = FSoftObjectPath(TEXT("/Game/MyCustomizableObject.MyCustomizableObject")); // 指向一个可变对象
PopClass->Tags.Add(FText::FromString(TEXT("NPC")));
PopClass->MaxInstances = 10;

// 创建群体配置资产
UCustomizableObjectPopulation* Population = NewObject<UCustomizableObjectPopulation>();
Population->PopulationClassAssets.Add(PopClass);
Population->PopulationClassCounts.Add(5); // 生成5个实例

// 生成全部实例
TArray<UCustomizableObjectInstance*> GeneratedInstances;
Population->GeneratePopulation(GeneratedInstances); // 返回一组完整的可变实例（已随机化）
```

### 进阶用法

编辑器工具支持保存和加载群体资产，并提供了视口预览。通过模块接口可以打开编辑器：

```cpp
// 必须包含编辑器模块（仅在 Editor 模式下可用）
#include "MuCOPE/CustomizableObjectPopulationEditorModule.h"

void OpenPopulationEditor(UCustomizableObjectPopulation* PopulationAsset)
{
    ICustomizableObjectPopulationEditorModule& EditorModule = ICustomizableObjectPopulationEditorModule::Get();
    TSharedRef<ICustomizableObjectPopulationEditor> Editor = EditorModule.CreateCustomizableObjectPopulationEditor(
        EToolkitMode::WorldCentric,
        nullptr, // ToolkitHost
        PopulationAsset
    );
}
```

## Demo 示例

以下是一个最小示例，演示如何在运行时通过C++生成群体实例并应用到角色骨骼网格组件：

**PopulationHelper.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MuCOP/CustomizableObjectPopulation.h"
#include "PopulationHelper.generated.h"

UCLASS()
class APopulationHelper : public AActor
{
    GENERATED_BODY()

public:
    // 生成并生成指定数量的随机角色
    UFUNCTION(BlueprintCallable, Category = "Population")
    void SpawnRandomNPCs(int32 Count);

private:
    UPROPERTY()
    UCustomizableObjectPopulation* Population;
};
```

**PopulationHelper.cpp**
```cpp
#include "PopulationHelper.h"
#include "MuCOP/CustomizableObjectPopulation.h"
#include "Components/SkeletalMeshComponent.h"

void APopulationHelper::SpawnRandomNPCs(int32 Count)
{
    // 加载已编辑好的群体资产
    static ConstructorHelpers::FObjectFinder<UCustomizableObjectPopulation> PopAsset(
        TEXT("/Game/MyPopulations/NPCPopulation.NPCPopulation"));
    if (!PopAsset.Succeeded()) return;

    UCustomizableObjectPopulation* Pop = PopAsset.Object;
    
    // 生成实例
    TArray<UCustomizableObjectInstance*> Instances;
    Pop->GeneratePopulation(Instances, Count); // 根据Count生成指定数量
    
    // 为每个实例创建骨骼网格组件并附加到世界
    for (int32 i = 0; i < Instances.Num(); ++i)
    {
        UCustomizableObjectInstance* COInstance = Instances[i];
        if (!COInstance) continue;

        USkeletalMeshComponent* SMC = NewObject<USkeletalMeshComponent>(this);
        SMC->SetSkeletalMesh(COInstance->GetSkeletalMesh());
        SMC->RegisterComponent();
        SMC->AttachToComponent(GetRootComponent(), FAttachmentTransformRules::KeepRelativeTransform);
        
        // 随机放置位置（简化处理）
        SMC->SetWorldLocation(FVector(i * 100.0f, 0.0f, 0.0f));
    }
}
```

## 模块依赖

由于 `CustomizableObjectPopulationEditor` 是编辑器模块，以下是非标准依赖（已排除 Core、Engine、Slate、UnrealEd 等极常见模块）：

| 模块 | 用途 |
|---|---|
| `DerivedDataCache` | 提供缓存支持，加速可变对象的编译和生成 |
| `MessageLog` | 提供日志和消息面板，用于编辑器内错误反馈 |
| `EditorStyle` | 提供 Slate 样式资源，用于编辑器 UI 主题 |

> 运行时模块 `CustomizableObjectPopulation` 无特殊非标准依赖（仅 `CoreUObject`, `Engine`, `Mutable`）。

## 维护状态

### 近期更新

- 2025-06-10 `bb3758b4` — `SEditorViewport::MakeViewportToolbar()` 已被弃用，更新代码。
- 2025-05-29 `f5ac91eb` — 移除`U`宏在会被跳过的位置上的无效出现。
- 2025-04-29 `13d19592` — [mutable population] 修复在3个或更多群体类别同时使用时随机崩溃的问题。
- 2025-03-26 `634dfda6` — [mutable] 所有CustomizableObject编辑器标签改为只显示资产名称，去除文件路径。
- 2025-03-13 `b059f7b4` — 修复琐碎的不可达代码警告。

### 维护评价

- **创建时间**：2025年03月，距今约3个月。
- **近期更新频率**：每月都有实质性提交，修复崩溃、API弃用更新等。
- **活跃程度**：活跃维护中，属于引擎开发团队持续更新的插件。
- **已知问题/限制**：
  - 仍为“实验性”插件，默认不启用，API可能发生变化。
  - 当前未暴露蓝图接口，仅C++可用。
  - 依赖于 Mutable 插件，需要同时启用。
- **推荐使用**：如果你的项目需要使用 Mutable 系统进行大规模角色生成，此插件提供了必备的编辑器和运行时支持。但由于是实验性，建议预留一定迁移成本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MutablePopulation)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MutablePopulation/Source/CustomizableObjectPopulation/Tests)（如有）
- [官方文档](https://docs.unrealengine.com/5.x/en-US/)（暂未提供专门文档）