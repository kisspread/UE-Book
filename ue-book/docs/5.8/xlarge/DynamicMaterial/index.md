# Material Designer

> Compact dynamic material creator and editor, similar in style to other DDCs.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 材质设计器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `DynamicMaterial` (Runtime), `DynamicMaterialTextureSet` (Runtime), `DynamicMaterialEditor` (Editor), `DynamicMaterialTextureSetEditor` (Editor), `DynamicMaterialShaders` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DynamicMaterial) | |

## 用途
这是一个用于在运行时和编辑器内动态创建、编辑和管理材质（Material）的插件系统。它解决了在蓝图中通过大量参数和复杂逻辑来构建材质实例的痛点，为设计师和开发者提供了一个类似节点式、可视化编程（DDC风格）的界面来组合材质属性。其核心是提供一套轻量级、高性能的材质模型，可以替代传统的、基于蓝图图（Blueprint Graph）或材质实例参数集合（MIC）的动态材质创建方式。

## 使用场景
- 你在 **Motion Design** 或其他 **Virtual Production** 项目中需要快速原型设计并动态调整材质效果。
- 你需要在运行时（Runtime）根据用户交互或数据流，**动态生成**复杂的材质外观，而不想依赖大量的材质实例或繁重的蓝图逻辑。
- 你希望将材质的创建逻辑从厚重的材质蓝图中**解耦**出来，用更直观、数据驱动的方式进行管理。
- 你需要管理一套**纹理集合（Texture Set）**，并能够动态地将其映射到不同的材质参数上。

## 蓝图用法
此插件主要通过一个专用的 **Actor 组件** 来暴露核心的蓝图功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Dynamic Material` | 从一个材质模型（`UMaterialInterface`）创建一个动态材质实例（`UMaterialInstanceDynamic`）。 | `UDMMaterialDesignerComponent` |
| `Set Material Parameter` | 动态设置材质的标量、向量或纹理参数。 | `UDMMaterialDesignerComponent` |
| `Get Dynamic Material` | 获取由该组件管理的当前动态材质实例。 | `UDMMaterialDesignerComponent` |

### 使用示例（蓝图描述）
1.  在你的 Actor 上添加 `Material Designer Component`。
2.  在“细节”面板中指定一个**材质模型（Material Model）** 资产（`.dmm` 格式，由插件编辑器创建）。
3.  调用 `Create Dynamic Material` 节点，并将返回的 `Dynamic Material` 赋给目标组件（如 `Static Mesh Component`）的材质。
4.  使用 `Set Material Parameter` 节点，传入参数名称和值，即可实时修改材质效果。

## C++ 用法
### 头文件引入
```cpp
#include "DMBlueprintLibrary.h"
#include "DMDefs.h"
```

### 基本用法
可以通过蓝图库或直接操作组件来创建和管理动态材质。
```cpp
// 在 Actor 组件中，获取或创建一个 Dynamic Material Designer Component
UDMMaterialDesignerComponent* DMComp = FindComponentByClass<UDMMaterialDesignerComponent>();
if (!DMComp)
{
    DMComp = NewObject<UDMMaterialDesignerComponent>(this);
    DMComp->RegisterComponent();
}

// 设置材质模型资产 (UObject*)
// DMComp->SetMaterialModel(MyDMMaterialModel);

// 创建动态材质并应用到某个 Mesh Component 上
UMaterialInstanceDynamic* MID = DMComp->CreateDynamicMaterial();
UMeshComponent* Mesh = FindComponentByClass<UMeshComponent>();
if (Mesh && MID)
{
    Mesh->SetMaterial(0, MID);
}
```

### 进阶用法
使用 `UDynamicMaterialSubsystem` 进行全局管理。
```cpp
// 获取子系统
UDynamicMaterialSubsystem* DMSubsystem = GEngine->GetEngineSubsystem<UDynamicMaterialSubsystem>();

// 可以利用子系统进行批量材质实例的管理、查询或统计
```

## Demo 示例
一个简单的组件，用于在运行时基于配置创建并应用动态材质。
```cpp
// MyDMMaterialComponent.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MyDMMaterialComponent.generated.h"

class UDMMaterialDesignerComponent;
class UMaterialInterface;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyDMMaterialComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyDMMaterialComponent();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="DM")
    TObjectPtr<UMaterialInterface> MaterialModel; // 这里实际应为 .dmm 资产，为演示简化

    UPROPERTY(BlueprintReadWrite, Category="DM")
    TObjectPtr<UDMMaterialDesignerComponent> DMComponent;

    UFUNCTION(BlueprintCallable, Category="DM")
    void ApplyDynamicMaterial();
};

// MyDMMaterialComponent.cpp
#include "MyDMMaterialComponent.h"
#include "Components/DMMaterialDesignerComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Components/StaticMeshComponent.h"

UMyDMMaterialComponent::UMyDMMaterialComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMyDMMaterialComponent::ApplyDynamicMaterial()
{
    if (!DMComponent)
    {
        DMComponent = NewObject<UDMMaterialDesignerComponent>(GetOwner());
        DMComponent->RegisterComponent();
    }

    // 设置模型并创建材质
    DMComponent->SetMaterialModel(MaterialModel);
    UMaterialInstanceDynamic* MID = DMComponent->CreateDynamicMaterial();

    // 应用到所有兄弟 Mesh 组件
    if (AActor* Owner = GetOwner())
    {
        TArray<UStaticMeshComponent*> MeshComps;
        Owner->GetComponents<UStaticMeshComponent>(MeshComps);
        for (UStaticMeshComponent* Mesh : MeshComps)
        {
            if (Mesh)
            {
                Mesh->SetMaterial(0, MID);
            }
        }
    }
}
```

## 模块依赖
此插件拥有多个模块，使用者主要依赖其运行时模块。

| 模块 | 用途 |
|---|---|
| `DynamicMaterial` | 核心运行时模块，包含材质模型、组件和子系统。 |
| `DynamicMaterialTextureSet` | 提供纹理集合的运行时支持。 |
| `DynamicMaterialShaders` | 包含材质系统所需的特定着色器（Shader）。 |
| `CustomDetailsView` | **编辑器依赖**。用于在属性面板中实现插件的自定义细节视图。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner)  in level editor to their own gro | 将Motion Design的编辑器面板标签页独立分组，提升界面组织性。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联/解除关联的通知机制，优化代码结构。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退了一次提交（CL53913857），可能是为了解决引入的问题。 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 与cfb610df相同的重构提交，可能是分支合并前的重复。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下，双精度常量截断到单精度浮点数引发的编译警告。 |

### 维护评价
该插件于 **2025年5月** 从 Experimental 目录迁移至 Virtual Production 目录，标志着其重要性和稳定性的提升。从 **2026年5月** 的密集提交记录来看，它正处于 **活跃开发和维护** 中，更新频率高，且涉及功能整合和代码优化。作为 Virtual Production 工作流（特别是 Motion Design）的核心组件之一，推荐在相关项目中使用。目前无明显废弃迹象。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DynamicMaterial)
- [官方文档]()（暂无）
- [测试用例]()（可在 `Engine/Tests/` 相关目录中查找）