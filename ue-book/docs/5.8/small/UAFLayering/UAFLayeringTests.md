# UAF Layering

> Framework to define a layering setup in UAF

| 属性 | 值 |
|---|---|
| 中文名 | UAF 分层框架 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `UAFLayering` (Runtime), `UAFLayeringEditor` (Runtime), `UAFLayeringUncookedOnly` (Runtime), `UAFLayeringTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/main/Engine/Plugins/Experimental/UAF/UAFLayering) | |

## 用途

UAFLayering 插件为 Unreal Animation Framework (UAF) 提供了一套动画分层系统。它允许动画师和程序员定义复杂的动画混合逻辑，将多个动画“层”堆叠并混合在一起，类似于动画蓝图中的状态机和混合节点，但以一种更资产化、更易复用的方式进行管理。它解决的核心问题是：如何以标准化的资产形式，管理和组合复杂的、多层级的动画混合流程，从而提升动画工作流的可维护性和复用性。

## 使用场景

- 你需要在角色上组合多个动画源（如基础移动、上半身动作、面部表情、武器持握）并精确控制它们的混合权重和影响区域 → 使用 UAF Layer Stack 资产定义混合规则。
- 你希望建立一套标准化的、可版本控制的动画混合模板，供项目中多个角色共享 → 将 Layer Stack 作为资产在内容浏览器中管理和分配。
- 你需要一个可视化的编辑器来调试和预览复杂的动画分层效果 → 使用该插件提供的 Layer Stack 编辑器。

## 蓝图用法

此插件的测试模块 (`UAFLayeringTests`) 主要用于自动化测试验证，未包含暴露给蓝图的 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)` 公共接口。其核心功能（资产创建、编辑器交互）主要通过其 Editor 模块实现，运行时逻辑通过 C++ 模块提供。

### 核心节点

当前模块 (`UAFLayeringTests`) 未提供蓝图可调用节点。蓝图交互可能通过其运行时模块 (`UAFLayering`) 暴露，需查阅其公开头文件。

## C++ 用法

以下示例基于插件测试用例及代码结构推断。

### 头文件引入

```cpp
#include "UAF/UAFLayering/Public/LayerStack.h"
// 可能还需引入 UAF 核心头文件
```

### 基本用法

创建和使用一个 Layer Stack 资产。
*(来源: 根据插件功能描述及 `LayerStack.h` 文件路径推断)*
```cpp
// 假设你已经通过编辑器创建了一个 ULayerStack 资产并保存在“/Game/Animation/LayerStacks”下
ULayerStack* MyLayerStack = LoadObject<ULayerStack>(nullptr, TEXT("/Game/Animation/LayerStacks/LS_PlayerLocomotion"));
if (MyLayerStack)
{
    // 将 Layer Stack 应用到某个动画实例或组件中（具体函数需查阅 UAF 核心及本插件运行时接口）
    // 例如: AnimInstance->ApplyLayerStack(MyLayerStack);
}
```

### 进阶用法

通过代码动态构建或修改 Layer Stack 的定义。
*(来源: 根据 `LayerStack` 可能支持动态编辑的插件设计模式推断)*
```cpp
ULayerStack* DynamicStack = NewObject<ULayerStack>();
// 假设有一个方法来向堆栈添加层
FAnimationLayerDefinition BaseLocoLayer;
// 配置 BaseLocoLayer ... 
DynamicStack->AddLayer(BaseLocoLayer);

FAnimationLayerDefinition UpperBodyLayer;
// 配置 UpperBodyLayer ...
DynamicStack->AddLayer(UpperBodyLayer);

// 然后将此动态创建的堆栈用于运行时
```

## Demo 示例

一个演示如何创建和应用 Layer Stack 的最小 C++ 示例。
*(示例结构基于 UAF 及 UE 动画框架常见模式，具体类名和函数需参考实际插件 API)*

### LayerStackExample.h
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LayerStackExample.generated.h"

class ULayerStack;
class USkeletalMeshComponent;

UCLASS()
class ALayerStackExample : public AActor
{
    GENERATED_BODY()

public:
    ALayerStackExample();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere)
    USkeletalMeshComponent* MeshComp;

    // 指向内容浏览器中 Layer Stack 资产的引用
    UPROPERTY(EditAnywhere, Category = "Animation")
    ULayerStack* LayerStackAsset;
};
```

### LayerStackExample.cpp
```cpp
#include "LayerStackExample.h"
#include "Components/SkeletalMeshComponent.h"
#include "UAF/UAFLayering/Public/LayerStack.h" // 根据实际路径调整

ALayerStackExample::ALayerStackExample()
{
    PrimaryActorTick.bCanEverTick = false;

    MeshComp = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("Mesh"));
    RootComponent = MeshComp;
}

void ALayerStackExample::BeginPlay()
{
    Super::BeginPlay();

    if (MeshComp && LayerStackAsset)
    {
        // 此处为示意。实际应用需要获取动画实例并调用相关方法。
        // 例如：UAnimInstance* AnimInstance = MeshComp->GetAnimInstance();
        // if (AnimInstance)
        // {
        //     AnimInstance->SetLayerStack(LayerStackAsset); // 假设的API
        // }
        UE_LOG(LogTemp, Log, TEXT("Layer Stack Asset '%s' has been assigned to %s"), *LayerStackAsset->GetName(), *GetName());
    }
}
```

## 模块依赖

你的项目模块若想使用 UAFLayering，通常需要依赖以下模块（具体请检查插件 `Build.cs` 文件）：

| 模块 | 用途 |
|---|---|
| `UAFCore` | UAF 框架核心模块，提供动画系统基础 |
| `UAFWorkspace` | UAF 工作区模块，插件通过它集成到 UAF 的资产和编辑环境中 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移至新的 UE_LOGF 格式，属于代码现代化更新。 |
| 2026-04-10 | `797a6da6` | Rename GetComponent to GetOrAddComponent to match functionality | 将函数重命名为更准确的名称，表明其具备“获取或创建”的逻辑。 |
| 2026-03-05 | `dd5531fb` | UAF Layering: | 可能为一次功能提交，具体改动需查看子提交或代码。 |
| 2026-03-04 | `d9a06590` | Update UAF blend profiles | 更新了混合配置，可能影响分层混合效果。 |
| 2026-03-04 | `95766f52` | UAF Layering: Expand outliner items per default | 改进了编辑器大纲视图的默认显示行为。 |

### 维护评价

- **创建时间**：约 1 年前创建。
- **近期更新**：最近 2 个月内有多次功能更新和代码优化，频率较高。
- **活跃程度**：处于**活跃开发**阶段，作为实验性功能正在快速迭代。
- **已知限制**：标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，表明这是一个早期原型，API 和功能可能不稳定。
- **推荐使用**：**可以实验性使用和学习**，适合跟进 UAF 框架的最新发展。**不建议**将其用于需要高度稳定的生产环境。建议持续关注其更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/main/Engine/Plugins/Experimental/UAF/UAFLayering)
- 官方文档：暂无
- 测试用例：位于插件目录内的 `Tests/` 子目录中，路径为 [Tests/UAFLayeringTests](https://github.com/EpicGames/UnrealEngine/tree/main/Engine/Plugins/Experimental/UAF/UAFLayering/Tests)