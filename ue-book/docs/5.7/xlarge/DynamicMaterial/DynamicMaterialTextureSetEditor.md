# Material Designer

> Compact dynamic material creator and editor, similar in style to other DDCs.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质资产） |
| 模块 | `DynamicMaterial` (RuntimeAndProgram), `DynamicMaterialTextureSet` (RuntimeAndProgram), `DynamicMaterialEditor` (Editor), `DynamicMaterialTextureSetEditor` (Editor), `DynamicMaterialShaders` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DynamicMaterial) | |

## 用途

Material Designer (DynamicMaterial) 是一个用于创建和编辑动态材质的可视化工具。它提供了一个类似其他数据驱动内容（DDC）的紧凑界面，允许用户通过组合、调整和预览材质属性来快速构建复杂的材质，而无需深入编写材质蓝图或着色器代码。该插件旨在简化材质创建流程，提高虚拟制片和实时内容创作中的迭代效率。

## 使用场景

-   **虚拟制片材质快速迭代**：在虚拟制片现场，美术师需要快速调整场景中物体的材质（如金属度、粗糙度、纹理），以匹配灯光和导演要求。使用 Material Designer 可以通过直观的滑块和节点实时预览更改。
-   **程序化材质生成**：需要根据游戏逻辑或数据（如角色生命值、环境湿度）动态改变材质外观时，可以通过该插件创建参数化的材质模板，并在运行时通过蓝图或 C++ 控制。
-   **材质原型设计**：在项目早期，快速实验不同的材质组合和效果，无需创建大量独立的材质资产。
-   **纹理集管理**：将一组相关的纹理（如基础颜色、法线、粗糙度）打包成一个“纹理集”，并统一管理它们的参数和应用。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Texture Set From Assets` | 根据提供的纹理资产数组，使用预设的过滤器规则创建一个新的纹理集资产。 | `UDMTextureSetBlueprintFunctionLibrary` |

### 使用示例（蓝图描述）

1.  **创建纹理集**：
    *   在蓝图中，使用 `Make Array` 节点收集你想要打包的纹理资产（例如，`T_Rock_BaseColor`, `T_Rock_Normal`, `T_Rock_ORM`）。
    *   将这个数组连接到 `Create Texture Set From Assets` 节点的 `In Assets` 输入引脚。
    *   节点的输出引脚将返回一个新创建的 `UDMTextureSet` 对象，你可以将其保存为资产或直接用于材质参数。

## C++ 用法

### 头文件引入

```cpp
#include "DMTextureSetBlueprintFunctionLibrary.h"
```

### 基本用法

从蓝图函数库的接口推断，C++ 中也可以调用相同的静态函数来创建纹理集。

```cpp
// 假设你已经有一个包含纹理资产数据的数组
TArray<FAssetData> TextureAssets;
// ... 填充 TextureAssets ...

// 创建纹理集
UDMTextureSet* NewTextureSet = UDMTextureSetBlueprintFunctionLibrary::CreateTextureSetFromAssets(TextureAssets);
if (NewTextureSet)
{
    // 使用新创建的纹理集，例如将其设置为某个材质实例的参数
    // ...
}
```

### 进阶用法

该插件的核心是运行时模块 `DynamicMaterial`，它提供了材质实例的动态创建和参数控制。虽然具体的 API 需要查看 `DynamicMaterial` 模块的头文件，但典型的用法模式可能如下：

```cpp
// 伪代码示例，展示可能的用法模式
#include "DynamicMaterialModule.h" // 假设的头文件

// 1. 获取材质设计器的运行时实例
IDynamicMaterialModule& DMModule = FModuleManager::GetModuleChecked<IDynamicMaterialModule>("DynamicMaterial");

// 2. 创建一个动态材质实例（可能基于一个模板）
UMaterialInstanceDynamic* DynamicMat = DMModule.CreateDynamicMaterialInstance(/* 参数 */);

// 3. 设置材质参数
DynamicMat->SetScalarParameterValue(FName("Metallic"), 0.8f);
DynamicMat->SetVectorParameterValue(FName("BaseColor"), FLinearColor::Red);
// 设置纹理参数，可能使用之前创建的纹理集
DynamicMat->SetTextureParameterValue(FName("BaseColorMap"), TextureFromSet);

// 4. 将材质应用到网格体组件
MeshComponent->SetMaterial(0, DynamicMat);
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何通过代码创建一个简单的动态材质并设置其纹理参数。请注意，实际的类名和函数名需要根据 `DynamicMaterial` 模块的源码进行调整。

**MyActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyActor.generated.h"

class UMaterialInstanceDynamic;
class UStaticMeshComponent;

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()

public:
    AMyActor();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere)
    UStaticMeshComponent* MeshComp;

    UPROPERTY()
    UMaterialInstanceDynamic* DynamicMaterial;
};
```

**MyActor.cpp**
```cpp
#include "MyActor.h"
#include "Components/StaticMeshComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Engine/Texture2D.h"

AMyActor::AMyActor()
{
    PrimaryActorTick.bCanEverTick = false;
    MeshComp = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    RootComponent = MeshComp;
}

void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    // 从静态材质创建动态材质实例
    UMaterialInterface* BaseMaterial = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Materials/M_BaseDynamic"));
    if (BaseMaterial)
    {
        DynamicMaterial = UMaterialInstanceDynamic::Create(BaseMaterial, this);
        MeshComp->SetMaterial(0, DynamicMaterial);

        // 设置一个标量参数
        DynamicMaterial->SetScalarParameterValue(FName("Roughness"), 0.4f);

        // 设置一个纹理参数
        UTexture2D* MyTexture = LoadObject<UTexture2D>(nullptr, TEXT("/Game/Textures/T_Default"));
        if (MyTexture)
        {
            DynamicMaterial->SetTextureParameterValue(FName("DiffuseTexture"), MyTexture);
        }
    }
}
```

## 模块依赖

该插件包含多个模块，它们之间存在依赖关系。对于使用者而言，主要需要关注运行时模块。

| 模块 | 用途 |
|---|---|
| `DynamicMaterial` | 核心运行时模块，提供动态材质的创建、管理和参数控制功能。 |
| `DynamicMaterialTextureSet` | 运行时模块，负责纹理集资产的定义和运行时逻辑。 |
| `DynamicMaterialShaders` | 包含插件所需的自定义着色器代码。 |
| `CustomDetailsView` | 插件依赖的另一个编辑器插件，用于提供自定义的细节面板视图。 |

**注意**：`DynamicMaterialEditor` 和 `DynamicMaterialTextureSetEditor` 是编辑器专用模块，在打包后的运行时版本中不可用。

## 维护状态

### 近期更新

-   `04930821cdf6` (2024-10-28) 运行 UnrealCodeFixup 工具，在可能的地方为文件添加 `#include UE_INLINE_GENERATED_CPP_BY_NAME`。
-   `d53ec51b85c0` (2024-10-28) Motion Design: 将以下插件从 `/Plugins/Experimental` 移动到 `/Plugins/VirtualProduction`：ActorModifier, ActorModifierCore, Motion Design, ClonerEffector, CustomDetailsView, Material Designer, GeometryMask, OperatorStack, PropertyAnimator, PropertyAnimatorCore, StormSync, StormSync Motion Design Bridge。

### 维护评价

-   **创建时间**：插件于 2024 年 1 月底创建，非常年轻。
-   **最近更新**：最近的提交（2024年10月）主要是代码整理和插件目录结构的迁移（从 Experimental 移至 VirtualProduction），没有涉及新功能开发或重大 bug 修复。
-   **活跃度**：作为 Epic Games 官方维护的虚拟制片工具链的一部分，预计会持续维护。但近期没有实质性功能更新。
-   **推荐使用**：该插件功能明确，是 Epic 官方虚拟制片工具集的一部分，**推荐在相关项目中使用**。由于其相对年轻，使用时需注意可能存在的 API 变化。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DynamicMaterial)
-   [官方文档]() （.uplugin 中未提供 DocsURL）
-   [测试用例]() （测试文件位置可能位于 `Engine/Tests/` 目录下，具体路径需进一步查找）