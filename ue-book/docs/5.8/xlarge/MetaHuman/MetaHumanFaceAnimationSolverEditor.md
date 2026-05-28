# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 数字人动画工具 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画资产、配置、蓝图资产） |
| 模块 | `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanIdentity` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 未知 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 提供的官方 MetaHuman 动画制作工具包。它不仅仅是一个简单的插件，而是一个**端到端的解决方案**，用于将真实的表演捕获数据（如视频、深度信息）转换为高保真的、可直接用于 Unreal Engine 的 MetaHuman 角色面部动画。

这个插件解决了数字人制作流程中的核心难题：如何高效、精准地将演员的面部表情和动作数据映射到复杂的 MetaHuman 角色面部骨骼和绑定上。它包含了一系列相互协作的模块，负责从捕获数据导入、面部特征点追踪、动画求解、姿态调整到最终序列输出的完整流水线。其存在是为了大幅降低创建电影级数字人动画的门槛和时间成本，使开发者无需深入了解复杂的计算机视觉和图形学算法，即可生成逼真的面部动画。

## 使用场景

-   **虚拟制片 (Virtual Production)**：在影视或广告拍摄中，需要快速将演员的表演实时或离线转换为 MetaHuman 角色的动画。
-   **游戏开发**：为游戏中的 MetaHuman NPC 或主角制作高质量的过场动画和面部表情。
-   **实时数字人**：构建需要实时驱动数字人面部表情的交互式应用，如虚拟主播、在线会议助手。
-   **角色动画预览**：在动画师手动精修前，快速生成基于真实表演的动画草稿。

## 蓝图用法

当前提供的源码片段主要集中在 `MetaHumanFaceAnimationSolverEditor` 模块，这是一个**编辑器扩展模块**，主要用于资产工厂和细节面板自定义化。它不直接暴露面向运行时游戏逻辑的蓝图节点。

该插件的主要蓝图接口（如 `UPerformance`，`UFaceAnimationSolver`）需要在更底层的运行时模块（如 `MetaHumanPerformance`， `MetaHumanFaceAnimationSolver`）中查找。

**编辑器内资产操作**：
-   在内容浏览器中右键创建新的 `MetaHuman Face Animation Solver` 资产。
-   选中一个求解器资产，在“细节”面板中查看和编辑其属性（通过 `FMetaHumanFaceAnimationSolverCustomization` 实现自定义化）。

## C++ 用法

基于提供的编辑器模块头文件，用法主要涉及资产创建和编辑器界面定制。

### 头文件引入

```cpp
// 用于创建新的动画求解器资产
#include "MetaHumanFaceAnimationSolverFactoryNew.h"

// 用于自定义求解器资产的细节面板显示
#include "AssetDefinitions/AssetDefinition_MetaHumanFaceAnimationSolver.h"
#include "Customizations/MetaHumanFaceAnimationSolverCustomizations.h"
```

### 基本用法（编辑器扩展）

此代码示例展示了如何通过 C++ 工厂模式创建自定义资产，以及如何注册细节面板自定义化。

**1. 自定义资产工厂 (创建资产)**
```cpp
// MetaHumanFaceAnimationSolverFactoryNew.h (示例)
UCLASS(hidecategories=Object)
class UMetaHumanFaceAnimationSolverFactoryNew : public UFactory
{
    GENERATED_BODY()
public:
    UMetaHumanFaceAnimationSolverFactoryNew();
    
    virtual UObject* FactoryCreateNew(UClass* InClass, UObject* InParent, FName InName, EObjectFlags InFlags, UObject* Context, FFeedbackContext* Warn) override;
    virtual FText GetToolTip() const override;
};
```

**2. 资产定义 (定义在编辑器中的显示)**
```cpp
// AssetDefinition_MetaHumanFaceAnimationSolver.h (示例)
UCLASS()
class UAssetDefinition_MetaHumanFaceAnimationSolver : public UAssetDefinitionDefault
{
    GENERATED_BODY()
public:
    virtual FText GetAssetDisplayName() const override; // 返回资产在UI中的名称
    virtual FLinearColor GetAssetColor() const override; // 返回资产图标颜色
    virtual TSoftClassPtr<UObject> GetAssetClass() const override; // 返回此资产定义对应的 UObject 类
    virtual TConstArrayView<FAssetCategoryPath> GetAssetCategories() const override; // 返回资产在内容浏览器中的分类路径
};
```

### 进阶用法

在插件的其他运行时模块中，会存在用于驱动动画求解和处理捕获数据的 API。典型的用法可能涉及：
1.  初始化一个 `UMetaHumanFaceAnimationSolver` 实例。
2.  将其配置与一个 `UPerformance`（表演捕获数据）资产关联。
3.  调用求解函数，生成一个包含面部骨骼动画数据的 `UAnimSequence`。
4.  通过 `MetaHumanSequencer` 模块将动画输出到关卡序列中。

## Demo 示例

由于当前分析的 `MetaHumanFaceAnimationSolverEditor` 模块是编辑器扩展，其运行时示例需依赖其他模块。以下是一个概念性的、高度简化的“伪代码”示例，展示该插件的整体工作流思路。

```cpp
// MyCharacter.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
// 假设的头文件引用
// #include "MetaHumanPerformance/Performance.h"
// #include "MetaHumanFaceAnimationSolver/FaceAnimationSolver.h"
#include "MyCharacter.generated.h"

UCLASS()
class AMyCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    // 蓝图可读写的捕获数据资产引用
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MetaHuman Animation")
    TObjectPtr<UPerformance> CapturePerformance;

    // 蓝图可调用的函数，用于启动动画生成
    UFUNCTION(BlueprintCallable, Category = "MetaHuman Animation")
    void GenerateFaceAnimation();

private:
    // 内部使用的动画求解器实例
    // TObjectPtr<UMetaHumanFaceAnimationSolver> FaceAnimationSolver;
};
```

```cpp
// MyCharacter.cpp
#include "MyCharacter.h"

void AMyCharacter::GenerateFaceAnimation()
{
    if (CapturePerformance)
    {
        // 以下为概念性代码，实际 API 请参考 MetaHumanAnimator 插件文档
        /*
        // 1. 初始化/获取求解器
        if (!FaceAnimationSolver)
        {
            FaceAnimationSolver = NewObject<UMetaHumanFaceAnimationSolver>();
        }

        // 2. 执行求解
        FaceAnimationSolver->SetPerformanceData(CapturePerformance);
        UAnimSequence* FaceAnimSequence = FaceAnimationSolver->Solve();

        // 3. 应用或导出动画
        if (FaceAnimSequence)
        {
            // 例如：将动画应用到角色的骨骼网格体组件
            // GetMesh()->PlayAnimation(FaceAnimSequence, false);
            // 或者将其保存到内容浏览器
        }
        */
        UE_LOG(LogTemp, Log, TEXT("MetaHuman Face Animation generation started for: %s"), *CapturePerformance->GetName());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("No CapturePerformance asset assigned."));
    }
}
```

## 模块依赖

要使用 MetaHuman Animator 插件的功能，你的项目模块通常需要依赖一些该插件提供的核心运行时模块。常见的依赖如下（已省略 `Core`, `Engine` 等公共依赖）：

| 模块 | 用途 |
|---|---|
| `MetaHumanCaptureUtils` | 处理和解析捕获的原始数据（视频、深度图） |
| `MetaHumanFaceAnimationSolver` | 核心算法模块，将捕获数据转换为面部动画 |
| `MetaHumanPerformance` | 管理“表演”数据资产，作为求解器的输入 |
| `MetaHumanPipeline` | 定义和管理数据处理流水线 |
| `MetaHumanIdentity` | 管理和连接 MetaHuman 角色身份、绑定与求解器配置 |

具体依赖哪些模块，取决于你使用该插件的哪部分功能。例如，如果你只是播放生成的动画，可能不需要直接依赖求解器模块。

## 维护状态

### 近期更新

从提供的 git log 来看，该插件在近期（2026年5月）仍然保持着**活跃的更新**。

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 修复：启用身体追踪时，禁用关卡序列导出功能以避免冲突 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色的渲染伪影问题 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 改进：身体追踪模式下过滤不必要的可视化对象，提升性能 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 新增功能：支持为已有的网格体（非新建）导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer（序列器）中的缓存相关问题 |

### 维护评价

-   **活跃维护**：从提交记录看，最近一次更新距今很近（2026年5月），且包含功能新增、Bug修复和优化，表明 Epic Games 仍在积极维护和迭代此插件。
-   **稳定性**：作为官方核心数字人工具链的一部分，其稳定性和可靠性有较高保障。
-   **实验性**：`.uplugin` 显示 `IsBetaVersion` 和 `IsExperimentalVersion` 均为 `false`，表明它已是一个相对成熟、可正式使用的工具。
-   **推荐使用**：如果你正在使用或计划使用 MetaHuman 角色，并希望实现基于表演捕获的动画制作，**强烈推荐**使用此官方插件。它是目前最直接、最集成化的解决方案。
-   **注意**：该插件的默认启用状态为“否”（`Installed: false`），需要在编辑器的插件菜单中手动启用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
-   官方文档（`.uplugin` 中未提供 `DocsURL`，请参考 Epic Games 官方学习中心关于 MetaHuman 的教程）
-   测试用例：该插件的测试用例可能位于 `Engine/Tests/` 目录下或各模块内部的 `Test` 文件夹中。