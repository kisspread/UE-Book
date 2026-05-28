# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 元人类动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质模板、蓝图资产、配置文件） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 约 2022 年 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman) | |

## 用途

MetaHuman Animator 是一套用于创建、管理和驱动 MetaHuman 角色面部动画的完整工具链。其核心解决的问题是：如何将来自真实世界的面部捕捉数据（如 iPhone 深度相机数据、专业动捕设备数据）高效、精确地转换为高质量的 MetaHuman 虚拟角色面部动画。它不仅包含数据采集和追踪的后端处理，还提供了编辑器内用于资产创建、配置求解器、预览和最终导出的全套工具，旨在实现“捕捉到屏幕”的一体化工作流。

## 使用场景

- **游戏开发**：为游戏中的主要角色（NPC/主角）快速生成基于真人表演的细腻面部动画，大幅提升角色表演的真实感。
- **虚拟制片/影视**：在电影或广告制作中，使用动捕设备录制演员表演，然后将其应用到虚拟 MetaHuman 角色上，进行实时预览或最终渲染。
- **数字人直播/虚拟主播**：将面部捕捉数据实时驱动虚拟 MetaHuman 角色，用于直播或虚拟发布会。
- **快速原型制作**：利用 iPhone 的 FaceID 摄像头等消费级设备快速录制面部表演，并生成可用于原型或测试的动画。

## 蓝图用法

该插件的模块以 C++ 运行时库和编辑器工具为主，大部分核心功能通过编辑器资产（如 `UAnimSequence`）和编辑器工具（如专用资产编辑器）暴露，纯蓝图可调用函数较少。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CanProcess` | 检查求解器当前配置是否满足处理条件 | `UMetaHumanFaceAnimationSolver` |
| `GetSolverTemplateData` | 获取求解器模板数据（JSON格式） | `UMetaHumanFaceAnimationSolver` |
| `GetSolverConfigData` | 获取当前求解器配置数据（JSON格式） | `UMetaHumanFaceAnimationSolver` |

### 使用示例（蓝图描述）

1.  **创建与配置求解器**：在内容浏览器中创建 `MetaHuman Face Animation Solver` 资产。在属性面板中，你可以覆盖默认的深度图影响（`DepthMapInfluence`）、眼睛平滑度（`EyeSolveSmoothness`）和牙齿模式（`TeethMode`）。
2.  **在性能资产中使用**：创建一个 `MetaHuman Performance` 资产。在其属性面板中，将上一步创建的 `MetaHuman Face Animation Solver` 资产指定给 `Face Solver` 属性。之后，当处理性能数据时，该求解器将被使用。

## C++ 用法

### 头文件引入

```cpp
#include “MetaHumanFaceAnimationSolver/MetaHumanFaceAnimationSolver.h”
```

### 基本用法

创建并配置一个面部动画求解器对象。这个对象通常用于定义面部动画处理过程中的各种参数。

```cpp
// 来源: 模块 API 分析
// 创建一个求解器实例
UMetaHumanFaceAnimationSolver* FaceSolver = NewObject<UMetaHumanFaceAnimationSolver>();

// 覆盖默认设置并进行配置
FaceSolver->bOverrideDepthMapInfluence = true;
FaceSolver->DepthMapInfluence = EDepthMapInfluenceValue::Low; // 使用较低的深度图影响
FaceSolver->bOverrideEyeSolveSmoothness = true;
FaceSolver->EyeSolveSmoothness = 0.3f; // 设置眼睛平滑度

// 检查配置是否可用于处理
if (FaceSolver->CanProcess())
{
    // 获取用于某个特定捕捉数据的求解器配置
    FString SolverConfigJson = FaceSolver->GetSolverConfigData(MyCaptureData);
    // SolverConfigJson 可以被传递给底层的求解管线
}
```

### 进阶用法

监听求解器配置的改变，并在外部做出响应。

```cpp
// 来源: 模块 API 分析
UMetaHumanFaceAnimationSolver* FaceSolver = /* ... */;

// 绑定一个回调函数到配置变更委托
FDelegateHandle Handle = FaceSolver->OnInternalsChanged().AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT(“Face animation solver config has been changed.”));
    // 在这里更新依赖此配置的其他系统或UI
});

// 当你不再需要监听时，解绑
FaceSolver->OnInternalsChanged().Remove(Handle);
```

## Demo 示例

一个最小化的 C++ 示例，展示如何创建和配置一个 `UMetaHumanFaceAnimationSolver`。

```cpp
// MyFaceSolverDemo.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include “MetaHumanFaceAnimationSolver/MetaHumanFaceAnimationSolver.h”
#include "MyFaceSolverDemo.generated.h"

UCLASS()
class MYPROJECT_API AMyFaceSolverDemo : public AActor
{
    GENERATED_BODY()
public:
    AMyFaceSolverDemo();

    UPROPERTY(VisibleAnywhere, Category = “MetaHuman”)
    TObjectPtr<UMetaHumanFaceAnimationSolver> FaceAnimationSolver;

    UFUNCTION(BlueprintCallable, Category = “MetaHuman”)
    void PrintSolverConfig();
};
```

```cpp
// MyFaceSolverDemo.cpp
#include "MyFaceSolverDemo.h"

AMyFaceSolverDemo::AMyFaceSolverDemo()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建求解器实例作为子对象
    FaceAnimationSolver = CreateDefaultSubobject<UMetaHumanFaceAnimationSolver>(TEXT("FaceSolver"));
}

void AMyFaceSolverDemo::PrintSolverConfig()
{
    if (FaceAnimationSolver && FaceAnimationSolver->CanProcess())
    {
        FString ConfigJson = FaceAnimationSolver->GetSolverConfigData();
        UE_LOG(LogTemp, Log, TEXT(“Current Solver Config:\n%s”), *ConfigJson);
    }
}
```

## 模块依赖

`MetaHumanFaceAnimationSolver` 模块本身无特殊依赖（仅标准 Core/Engine/Slate 等）。但请注意，要完整使用 MetaHuman Animator 的功能，整个插件依赖以下不常见的模块（已从各子模块的 Build.cs 中提取）：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 底层核心算法库 |
| `MetaHumanSDKEditor` | MetaHuman SDK 编辑器集成 |
| `ControlRigDeveloper` | 用于与 Control Rig 蓝图编辑器交互 |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格体处理工具 |
| `MetaHumanImageViewerEditor` | 图像查看器编辑器集成 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色上的渲染伪影问题 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 为已存在的网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 的缓存问题 |

### 维护评价

MetaHuman Animator 插件处于**活跃维护**状态。
- **近期更新**：最近的提交（2026年5月）表明开发团队仍在积极修复问题、优化功能（如身体追踪集成、导出流程、渲染问题），并且在进行功能增强。
- **功能状态**：作为 Epic Games 官方维护的 MetaHuman 核心工具链，它是一个成熟且持续发展的产品，旨在为 MetaHuman 生态系统提供全面支持。
- **推荐**：对于任何需要高质量、高保真 MetaHuman 角色面部动画的项目，此插件是官方推荐且功能完备的解决方案，**推荐使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/metahuman-animator-in-unreal-engine/) （MetaHuman Animator 文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/Tests) （插件目录下的Tests文件夹）