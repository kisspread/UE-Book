# UAF Layering

> Framework to define a layering setup in UAF

| 属性 | 值 |
|---|---|
| 中文名 | UAF 动画分层框架 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `UAFLayering` (Runtime), `UAFLayeringEditor` (Runtime), `UAFLayeringUncookedOnly` (Runtime), `UAFLayeringTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-13 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering) | |

## 用途

UAF Layering 插件提供了一个用于在 Unreal Animation Framework (UAF) 中定义、管理和运行时混合动画分层的框架。它解决了在复杂动画系统中需要精细化控制不同动画层（例如基础运动、上层动作、面部表情等）如何混合与交互的问题。该插件允许动画师和技术美术通过一个专门的资产（Layer Stack）来配置分层逻辑，并在编辑器中进行可视化调试，而无需在运行时蓝图或代码中硬编码复杂的混合逻辑。

## 使用场景

-   你需要为你的角色创建一个高度可定制的动画系统，其中包含多个独立的动画层（如走路、跑步、射击、受伤），并且需要精确控制它们之间的混合权重和优先级。
-   你正在使用 UAF 系统，并且希望将分层动画的配置从蓝图中解耦出来，变成一个可资产化、可复用、易于团队协作的 `UAFLayerStack` 资产。
-   你的项目需要一个统一的编辑器界面来预览和调试复杂动画分层的效果，而不是在运行时反复试错。

## 蓝图用法

### 核心节点

*注意：根据提供的模块（UAFLayeringEditor）和头文件分析，主要的运行时蓝图节点可能位于 `UAFLayering` 运行时模块中。以下是从当前编辑器模块代码推断或常见的相关操作：*

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Layer Stack Asset` | 在工作区编辑器中打开指定的 `UAFLayerStack` 资产进行编辑 | `UAssetDefinition_UAFLayerStack` (通过资产定义触发) |
| *(推断)* `Create New Layer Stack` | 创建一个新的 `UAFLayerStack` 资产 | `UUAFLayerStackFactory` (通过内容浏览器触发) |

### 使用示例（蓝图描述）

1.  **创建资产**：在内容浏览器中右键，通过“动画”类别下的“UAF Layer Stack”创建新资产。这会调用 `UUAFLayerStackFactory` 来创建一个 `UAFLayerStack` 对象。
2.  **编辑资产**：双击创建好的 `UAFLayerStack` 资产，或右键选择“编辑”。这会触发 `UAssetDefinition_UAFLayerStack::OpenAssets`，从而在 UAF 工作区编辑器中打开一个专门的图层堆栈编辑器。该编辑器由 `FUAFLayeringEditorModule` 负责创建文档小部件。
3.  **运行时集成**：在角色蓝图或动画蓝图中，获取并使用 `UAFLayerStack` 资产来驱动动画更新。具体节点（如 `Evaluate Layer Stack`）需要在运行时模块 (`UAFLayering`) 的头文件中查找。

## C++ 用法

### 头文件引入

```cpp
#include "UAFLayeringEditorModule.h"
#include "Workspace/LayerStackViewportController.h"
#include "UAFLayerStackAssetDefinition.h"
```

### 基本用法

创建和打开一个 `UAFLayerStack` 资产进行编辑。此示例展示了如何通过资产定义系统集成。

```cpp
// 来源: Private/UAFLayerStackAssetDefinition.h, Private/UAFLayeringEditorModule.h
// 当在内容浏览器中双击一个 UAFLayerStack 资产时，此函数会被引擎调用。
EAssetCommandResult UAssetDefinition_UAFLayerStack::OpenAssets(const FAssetOpenArgs& OpenArgs) const
{
    // 简化的示意逻辑：通知 UAF 工作区模块打开此资产进行编辑
    for (UAFLayerStack* Asset : OpenArgs.LoadObjects<UAFLayerStack>())
    {
        UE::Workspace::FWorkspaceEditorContext Context(Asset, OpenArgs);
        // FUAFLayeringEditorModule 会响应此请求，创建 LayerStack 编辑器界面
        // 具体的打开逻辑封装在工作区系统中
        UE::Workspace::OpenWorkspaceEditor(Context);
    }
    return EAssetCommandResult::Handled;
}
```

### 进阶用法

为 Layer Stack 编辑器提供自定义的视口预览控制器。`FLayerStackViewportController` 负责在编辑器中预览角色网格体与当前分层动画设置的效果。

```cpp
// 来源: Private/Workspace/LayerStackViewportController.h
void FLayerStackViewportController::OnEnter(const FViewportContext& InViewportContext)
{
    // 当进入预览模式时，根据当前的 UAFSystem 和 LayerStack 配置，
    // 将一个带有正确动画图的角色 Actor 添加到预览场景中。
    const UUAFSystem* System = InViewportContext.GetSystem();
    const UUAFLayerStack* LayerStack = InViewportContext.GetAsset<UUAFLayerStack>();
    if (System && LayerStack)
    {
        USkeletalMesh* SkeletalMesh = System->GetSkeletalMesh(); // 示例：从系统获取网格体
        AddMeshToPreview(InViewportContext.GetPreviewScene(), System, LayerStack, SkeletalMesh);
    }
}

void FLayerStackViewportController::AddMeshToPreview(FAdvancedPreviewScene* PreviewScene, const TObjectPtr<const UUAFSystem> System, const TObjectPtr<const UUAFLayerStack> LayerStack, USkeletalMesh* InSkeletalMesh)
{
    // 具体的实现会创建一个 AActor，应用 SkeletalMeshComponent，
    // 并为其设置一个由 LayerStack 配置驱动的动画蓝图或动画实例。
    // 此处省略了具体的 Actor 创建和动画蓝图赋值逻辑。
    AActor* PreviewActor = /* ... */;
    PreviewActors.Add(PreviewActor);
    PreviewScene->AddActor(PreviewActor);
}
```

## Demo 示例

以下是一个简化的自定义 `UAFLayerStack` 使用示例，假设在运行时模块中已经存在相关的求值函数。

**MyAnimLayerStackUser.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
// 假设 UAFLayerStack 和相关运行时类在 “UAFLayering” 模块中
// #include "UAFLayerStack.h" 
#include "MyAnimLayerStackUser.generated.h"

UCLASS()
class AMyAnimLayerStackUser : public AActor
{
    GENERATED_BODY()

public:
    AMyAnimLayerStackUser();

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

private:
    // 指向分层资产的指针，可在蓝图或编辑器中设置
    UPROPERTY(EditAnywhere, Category = "Animation")
    TObjectPtr<UAFLayerStack> LayerStackAsset;

    // 骨骼网格体组件
    UPROPERTY(VisibleAnywhere)
    TObjectPtr<USkeletalMeshComponent> MeshComponent;
};
```

**MyAnimLayerStackUser.cpp**
```cpp
#include "MyAnimLayerStackUser.h"
// 包含运行时求值所需的头文件
// #include "UAFLayerStackEvaluator.h" // 假设存在

AMyAnimLayerStackUser::AMyAnimLayerStackUser()
{
    PrimaryActorTick.bCanEverTick = true;
    MeshComponent = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("Mesh"));
    RootComponent = MeshComponent;
}

void AMyAnimLayerStackUser::BeginPlay()
{
    Super::BeginPlay();
    // 如果资产有效，在开始时初始化或重置评估器状态
    if (LayerStackAsset)
    {
        // 假设存在一个函数来初始化分层评估上下文
        // InitializeLayerStackEvaluator(LayerStackAsset);
    }
}

void AMyAnimLayerStackUser::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (LayerStackAsset && MeshComponent)
    {
        // 在 Tick 中求值分层堆栈，更新动画状态。
        // 具体的 API 调用（如 Evaluate、Blend）需要在 UAFLayering 模块的公共头文件中查找。
        // 伪代码示例：
        // FAnimationLayerStackResult Result = EvaluateLayerStack(LayerStackAsset, DeltaTime, CurrentState);
        // ApplyAnimationResult(MeshComponent, Result);
    }
}
```

## 模块依赖

从 `UAFLayeringEditor` 模块（编辑器侧）的代码推断，该插件与 UAF 核心和工作区系统紧密集成。

| 模块 | 用途 |
|---|---|
| `Workspace` | 为 Layer Stack 资产提供编辑器工作区框架、大纲视图细节和视口控制器接口 |
| `AnimationCore` | (推断) UAF 核心动画功能模块，提供动画评估和混合的基础框架 |
| `AnimationBlueprintLibrary` | (推断) 动画蓝图相关功能，可能用于集成运行时动画逻辑 |

**注意**：要使用此插件，你的项目可能还需要依赖 UAF 插件本身（如 `UAF` 或 `UAFCore`）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的日志框架，属代码现代化维护。 |
| 2026-04-10 | `797a6da6` | Rename GetComponent to GetOrAddComponent to match functionality | 重命名函数以更准确地反映其“获取或添加”的行为，是接口澄清。 |
| 2026-03-05 | `dd5531fb` | UAF Layering: | （信息不完整，推断为功能或修复提交）。 |
| 2026-03-04 | `d9a06590` | Update UAF blend profiles | 更新 UAF 的混合配置文件，可能涉及分层混合行为的调整。 |
| 2026-03-04 | `95766f52` | UAF Layering: Expand outliner items per default | 默认展开工作区大纲中的图层项，改善编辑器用户体验。 |

### 维护评价

-   **创建时间**：该插件创建于2026年初，非常新。
-   **更新频率**：最近一个月（截至2026-04-14）有多次提交，最近一次提交是代码维护性改进，之前有功能优化和UX改进。
-   **活跃度**：处于**活跃开发**阶段。
-   **状态**：插件被标记为 **Experimental**（`IsExperimentalVersion=true`）且 **默认禁用**（`EnabledByDefault=false`）。这表明它仍处于早期开发或测试阶段，API 和功能可能不稳定，不建议直接用于生产项目。
-   **推荐度**：目前仅推荐用于**实验性项目、技术预研或参与引擎早期开发**。对于稳定项目，建议等待其成为正式功能或密切关注其成熟度。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering/Tests)