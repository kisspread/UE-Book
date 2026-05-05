# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质、动画、配置等） |
| 模块 | `MetaHumanCore` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanToolkit` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanPlatform` (Runtime), `MeshTrackerInterface` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 数字人动画制作工具包。它并非一个简单的组件，而是一个完整的、端到端的动画制作管线，旨在将真实世界的面部表演数据（如 iPhone 深度摄像头视频、专业头盔相机数据或音频）转化为驱动 MetaHuman 角色的高质量面部动画。

该插件解决的核心问题是：**如何高效、准确地将演员的面部表演“转移”到数字人角色上**。它通过一系列模块化的处理步骤（捕获、追踪、求解、拟合）来实现这一目标，涵盖了从原始数据导入到最终动画输出的全流程。其存在是为了简化和自动化复杂的数字人动画制作工作流，降低技术门槛，使开发者能够专注于创意而非底层技术实现。

## 使用场景

- **影视与虚拟制片**：你需要为电影或电视节目中的数字替身生成逼真的面部动画，使用 iPhone 或专业设备拍摄演员表演。
- **游戏开发**：你的游戏包含大量需要高质量面部动画的对话或过场动画，希望从演员表演视频快速生成动画数据。
- **虚拟主播/VTuber**：你希望基于实时或录制的摄像头画面，驱动一个 MetaHuman 虚拟形象进行直播或内容创作。
- **快速原型与迭代**：在项目早期，你需要快速测试角色对话和表情，而不想手动制作每一帧动画。
- **批量处理**：你有大量的表演捕获数据需要统一处理并转换为动画。

## 蓝图用法

由于插件规模庞大（xlarge），蓝图节点分散在多个模块中。以下按核心功能流程列出关键节点类别。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create MetaHuman Identity` | 从捕获数据创建一个新的 MetaHuman 身份资产。 | `UMetaHumanIdentity` |
| `Add Capture Data` | 向身份资产添加视频或深度捕获数据。 | `UMetaHumanIdentity` |
| `Start Face Tracking` | 启动面部追踪过程，从视频中提取面部特征点。 | `UMetaHumanFaceContourTracker` |
| `Solve Face Animation` | 使用追踪数据求解面部动画曲线。 | `UMetaHumanFaceAnimationSolver` |
| `Fit to MetaHuman` | 将求解出的动画拟合到特定的 MetaHuman 骨骼和网格体上。 | `UMetaHumanFaceFittingSolver` |
| `Export Animation Sequence` | 将最终的动画导出为 Unreal 的动画序列资产。 | `UMetaHumanPerformance` |
| `Process Batch` | 对一组捕获数据执行批处理动画生成流程。 | `UMetaHumanBatchProcessor` |

### 使用示例（蓝图描述）

1.  **创建身份与导入数据**：
    - 使用 `Create MetaHuman Identity` 节点创建一个新的身份资产。
    - 将 `Add Capture Data` 节点的输出连接到身份资产，输入你的视频文件路径。
2.  **执行动画管线**：
    - 将身份资产连接到 `Start Face Tracking` 节点，开始追踪。
    - 追踪完成后，将结果传递给 `Solve Face Animation` 节点。
    - 最后，将求解结果连接到 `Fit to MetaHuman` 节点，并指定目标 MetaHuman 角色。
3.  **导出与使用**：
    - 使用 `Export Animation Sequence` 节点将拟合后的动画保存为资产。
    - 在 Sequencer 或动画蓝图中使用该动画序列。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanIdentity.h"
#include "MetaHumanFaceAnimationSolver.h"
#include "MetaHumanPerformance.h"
```

### 基本用法

以下示例展示了如何在 C++ 中程序化地创建一个身份并启动面部追踪流程。

```cpp
// 来源：基于 MetaHumanIdentity 模块的典型用法推断
#include "MetaHumanIdentity.h"

void CreateAndTrackIdentity()
{
    // 1. 创建一个新的 MetaHuman 身份资产
    UMetaHumanIdentity* NewIdentity = NewObject<UMetaHumanIdentity>();
    NewIdentity->InitializeNewIdentity();

    // 2. 添加捕获数据（假设已有文件路径）
    FString VideoPath = TEXT("/Game/Captures/MyPerformance.mp4");
    UMetaHumanCaptureData* CaptureData = NewIdentity->AddCaptureDataFromPath(VideoPath);

    // 3. 配置并启动面部追踪
    if (CaptureData)
    {
        // 获取追踪器并配置参数
        UMetaHumanFaceContourTracker* Tracker = NewIdentity->GetFaceContourTracker();
        Tracker->SetTrackingQuality(EMetaHumanTrackingQuality::High);
        
        // 开始异步追踪
        Tracker->StartTracking(CaptureData, FOnTrackingComplete::CreateLambda(
            [](bool bSuccess)
            {
                if (bSuccess)
                {
                    UE_LOG(LogTemp, Log, TEXT("面部追踪完成！"));
                }
            }
        ));
    }
}
```

### 进阶用法

结合多个模块，完成从追踪到动画导出的完整流程。

```cpp
// 来源：综合 MetaHumanIdentity, MetaHumanFaceAnimationSolver, MetaHumanPerformance 模块
#include "MetaHumanIdentity.h"
#include "MetaHumanFaceAnimationSolver.h"
#include "MetaHumanPerformance.h"

void FullAnimationPipeline(UMetaHumanIdentity* Identity)
{
    // 假设 Identity 已经完成追踪
    
    // 1. 求解面部动画
    UMetaHumanFaceAnimationSolver* Solver = Identity->GetFaceAnimationSolver();
    FMetaHumanAnimationSolution Solution = Solver->SolveAnimation(Identity->GetTrackingData());

    // 2. 拟合到 MetaHuman
    UMetaHumanFaceFittingSolver* FittingSolver = Identity->GetFaceFittingSolver();
    USkeletalMesh* TargetMetaHumanMesh = LoadObject<USkeletalMesh>(nullptr, TEXT("/Game/MetaHumans/MyCharacter/MyCharacter_SkelMesh"));
    FittingSolver->FitAnimationToMesh(Solution, TargetMetaHumanMesh);

    // 3. 导出动画序列
    UMetaHumanPerformance* Performance = NewObject<UMetaHumanPerformance>();
    UAnimSequence* ExportedAnim = Performance->ExportToAnimSequence(
        FittingSolver->GetFittedAnimation(),
        TargetMetaHumanMesh,
        TEXT("/Game/Animations/ExportedPerformance")
    );

    if (ExportedAnim)
    {
        UE_LOG(LogTemp, Log, TEXT("动画序列已成功导出至: %s"), *ExportedAnim->GetPathName());
    }
}
```

## Demo 示例

一个最小化的示例，展示如何初始化 MetaHuman Animator 核心并创建一个身份对象。

**MetaHumanAnimatorDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MetaHumanAnimatorDemo.generated.h"

class UMetaHumanIdentity;

UCLASS()
class MYPROJECT_API AMetaHumanAnimatorDemo : public AActor
{
    GENERATED_BODY()

public:
    AMetaHumanAnimatorDemo();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    TObjectPtr<UMetaHumanIdentity> DemoIdentity;
};
```

**MetaHumanAnimatorDemo.cpp**
```cpp
#include "MetaHumanAnimatorDemo.h"
#include "MetaHumanIdentity.h"

AMetaHumanAnimatorDemo::AMetaHumanAnimatorDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMetaHumanAnimatorDemo::BeginPlay()
{
    Super::BeginPlay();

    // 创建一个 MetaHuman 身份对象用于演示
    DemoIdentity = NewObject<UMetaHumanIdentity>(this);
    if (DemoIdentity)
    {
        DemoIdentity->InitializeNewIdentity();
        UE_LOG(LogTemp, Log, TEXT("MetaHuman Animator Demo: 身份对象已创建。"));
        
        // 在此可以继续添加捕获数据、启动追踪等操作
        // DemoIdentity->AddCaptureDataFromPath(TEXT("..."));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("MetaHuman Animator Demo: 创建身份对象失败！"));
    }
}
```

## 模块依赖

该插件的模块间依赖关系复杂，且许多模块依赖于 Epic 的内部库（如 `MetaHumanCoreTechLib`）。对于使用者而言，主要需要关注以下外部依赖：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心算法库，提供底层的面部追踪、求解和拟合算法。 |
| `ControlRig` | 用于驱动 MetaHuman 角色的动画控制系统。 |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格体相关的通用工具。 |
| `MetaHumanSDKEditor` | MetaHuman SDK 的编辑器部分，可能用于资产管理和集成。 |

**注意**：由于插件包含大量编辑器专用模块（后缀为 `Editor`），在打包（Shipping）构建中，这些模块将被自动排除。运行时功能主要由不带 `Editor` 后缀的模块提供。

## 维护状态

### 近期更新

```
- 9803c443cfab Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
- 99e36a1ffc6a [UEMHC] Content Browser-Add Button-Metahuman: Unloc'd Tooltips Require Gather
- 2a7f797f2bdd [MH-Plugin] Migrate the animator plugin from restricted #rb Jane.Haslam [REVIEW] thanasis.vogiannou
```

### 维护评价

- **创建时间**：插件于 2024 年 2 月创建，相对年轻。
- **最近更新**：最近的提交集中在代码质量优化（添加 `UE_INLINE_GENERATED_CPP_BY_NAME`）、本地化修复（Tooltip 翻译）以及重要的架构调整（从受限仓库迁移）。这表明插件正在积极维护和迭代。
- **活跃度**：作为 Epic 官方支持的 MetaHuman 工具链核心部分，预计将持续获得更新和支持，以适配新的引擎版本和 MetaHuman 技术。
- **已知限制**：插件默认未启用（`Installed: false`），需要用户手动在插件管理器中启用。部分高级功能可能依赖于特定的硬件（如 iPhone 的 TrueDepth 摄像头）或 Epic 的云服务。
- **推荐使用**：**强烈推荐**。对于任何需要高质量 MetaHuman 面部动画的项目，这是官方且功能最完整的解决方案。尽管学习曲线可能较陡，但其提供的端到端工作流能极大提升生产效率。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/metahuman-animator-in-unreal-engine/) (Epic 官方文档站点)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest) (包含一个专门的测试模块)

---

# MetaHuman Face Animation Solver Editor

> （此模块为 MetaHuman Animator 插件的一部分，无独立描述）

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MetaHumanFaceAnimationSolverEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceAnimationSolverEditor) | |

## 用途

`MetaHumanFaceAnimationSolverEditor` 模块是 `MetaHumanFaceAnimationSolver` 核心模块的编辑器扩展。它的主要作用是为面部动画求解器提供编辑器内的用户界面、资产自定义和调试工具。

该模块解决的问题是：**如何让美术师和技术美术在 Unreal Editor 中直观地配置、预览和调试面部动画求解过程**。它可能提供了自定义求解器参数的编辑器面板、动画曲线的可视化工具、以及将求解结果与 Sequencer 集成的功能。

## 使用场景

- **调整求解参数**：作为技术美术，你需要在编辑器中微调面部动画求解器的权重、平滑度或约束，以获得更理想的动画效果。
- **预览与调试**：在将动画应用到最终角色前，你需要在编辑器中实时预览求解结果，并检查特定面部区域的动画是否正确。
- **资产配置**：你需要为不同的表演风格或角色创建不同的求解器预设，并在编辑器中管理这些配置资产。

## 蓝图用法

此模块主要提供编辑器工具，其蓝图节点通常在编辑器工具蓝图（Editor Utility Blueprint）或编辑器模块中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Solver Configuration` | 打开面部动画求解器的配置编辑器窗口。 | `UMetaHumanFaceAnimationSolverEditorModule` |
| `Get Solver Presets` | 获取所有可用的求解器预设资产列表。 | `UMetaHumanFaceAnimationSolverEditorUtils` |
| `Apply Preset to Identity` | 将选定的求解器预设应用到指定的 MetaHuman 身份上。 | `UMetaHumanFaceAnimationSolverEditorUtils` |

### 使用示例（蓝图描述）

在编辑器工具蓝图中：
1.  使用 `Get Solver Presets` 节点获取预设列表，并填充到一个下拉菜单中。
2.  当用户选择一个预设后，调用 `Apply Preset to Identity` 节点，将预设参数应用到当前正在编辑的 MetaHuman 身份资产上。
3.  提供一个按钮，调用 `Open Solver Configuration` 节点，让用户进行更高级的手动调整。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanFaceAnimationSolverEditor.h"
```

### 基本用法

此模块通常不直接在游戏运行时代码中使用，而是在编辑器工具或自定义编辑器面板中使用。

```cpp
// 来源：基于编辑器模块的典型用法推断
#include "MetaHumanFaceAnimationSolverEditor.h"
#include "MetaHumanFaceAnimationSolver.h"

void ConfigureSolverInEditor(UMetaHumanIdentity* Identity)
{
    // 获取编辑器模块实例
    FMetaHumanFaceAnimationSolverEditorModule& SolverEditorModule = 
        FModuleManager::GetModuleChecked<FMetaHumanFaceAnimationSolverEditorModule>("MetaHumanFaceAnimationSolverEditor");

    // 通过编辑器模块访问求解器配置工具
    TSharedPtr<IMetaHumanFaceAnimationSolverEditor> SolverEditor = SolverEditorModule.GetSolverEditor();
    if (SolverEditor.IsValid())
    {
        // 打开配置窗口
        SolverEditor->OpenConfigurationWindow(Identity);
        
        // 或者直接应用一个预设
        // SolverEditor->ApplyPreset(Identity, TEXT("Cinematic_HighDetail"));
    }
}
```

### 进阶用法

创建自定义的编辑器扩展，集成求解器配置功能。

```cpp
// 来源：创建自定义编辑器面板的示例
#include "MetaHumanFaceAnimationSolverEditor.h"
#include "Toolkits/AssetEditorManager.h"

class FMyCustomSolverPanel
{
public:
    void Initialize()
    {
        // 监听身份资产被打开的事件
        FAssetEditorManager::Get().OnAssetEditorOpened().AddRaw(this, &FMyCustomSolverPanel::OnAssetEditorOpened);
    }

    void OnAssetEditorOpened(UObject* Asset)
    {
        if (UMetaHumanIdentity* Identity = Cast<UMetaHumanIdentity>(Asset))
        {
            // 在身份资产编辑器打开时，注入我们的自定义求解器配置UI
            FMetaHumanFaceAnimationSolverEditorModule& Module = 
                FModuleManager::GetModuleChecked<FMetaHumanFaceAnimationSolverEditorModule>("MetaHumanFaceAnimationSolverEditor");
            
            // 假设模块提供了扩展点
            Module.RegisterCustomSolverPanel(Identity, CreateMyPanel());
        }
    }

    TSharedRef<SWidget> CreateMyPanel()
    {
        // 创建自定义的 Slate UI 用于配置求解器
        return SNew(SVerticalBox)
            + SVerticalBox::Slot()
            [
                SNew(STextBlock).Text(FText::FromString(TEXT("自定义求解器配置面板")))
            ];
        // ... 更多UI控件
    }
};
```

## Demo 示例

一个最小化的示例，展示如何在编辑器工具中访问求解器编辑器模块。

**MyEditorTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "EditorUtilityWidget.h"
#include "MyEditorTool.generated.h"

class UMetaHumanIdentity;

UCLASS()
class UMyEditorTool : public UEditorUtilityWidget
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    void OpenFaceAnimationSolverConfig(UMetaHumanIdentity* Identity);
};
```

**MyEditorTool.cpp**
```cpp
#include "MyEditorTool.h"
#include "MetaHumanFaceAnimationSolverEditor.h"
#include "MetaHumanIdentity.h"

void UMyEditorTool::OpenFaceAnimationSolverConfig(UMetaHumanIdentity* Identity)
{
    if (!Identity)
    {
        UE_LOG(LogTemp, Warning, TEXT("OpenFaceAnimationSolverConfig: 提供的身份对象无效。"));
        return;
    }

    // 检查求解器编辑器模块是否已加载
    if (FModuleManager::Get().IsModuleLoaded("MetaHumanFaceAnimationSolverEditor"))
    {
        FMetaHumanFaceAnimationSolverEditorModule& SolverEditorModule = 
            FModuleManager::GetModuleChecked<FMetaHumanFaceAnimationSolverEditorModule>("MetaHumanFaceAnimationSolverEditor");
        
        // 使用模块功能打开配置窗口
        SolverEditorModule.OpenSolverConfigurationForIdentity(Identity);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("OpenFaceAnimationSolverConfig: MetaHumanFaceAnimationSolverEditor 模块未加载。"));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetaHumanFaceAnimationSolver` | 核心求解器模块，提供被编辑和配置的底层算法和数据结构。 |
| `UnrealEd` | Unreal 编辑器核心框架，用于创建编辑器UI、工具和资产编辑器。 |
| `PropertyEditor` | 用于在编辑器中显示和编辑 UObject 属性。 |
| `Slate`, `SlateCore` | 用于构建编辑器用户界面。 |

## 维护状态

### 近期更新

（与主插件 MetaHuman Animator 的更新历史一致）

```
- 9803c443cfab Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
- 99e36a1ffc6a [UEMHC] Content Browser-Add Button-Metahuman: Unloc'd Tooltips Require Gather
- 2a7f797f2bdd [MH-Plugin] Migrate the animator plugin from restricted #rb Jane.Haslam [REVIEW] thanasis.vogiannou
```

### 维护评价

- **创建时间**：作为 MetaHuman Animator 插件的一部分，创建于 2024 年 2 月。
- **维护状态**：该模块随主插件一起维护。最近的提交表明其代码正在被优化和本地化，处于活跃开发中。
- **功能定位**：这是一个编辑器支持模块，其稳定性和功能完整性依赖于核心的 `MetaHumanFaceAnimationSolver` 模块。只要主插件在维护，此模块也会得到相应更新。
- **推荐使用**：如果你需要在编辑器中深度定制或调试面部动画求解过程，此模块是必需的。对于仅使用默认设置的用户，可能不会直接与之交互，但它在后台为编辑器集成提供了关键支持。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceAnimationSolverEditor)
- [所属插件文档](#meta-human-animator)