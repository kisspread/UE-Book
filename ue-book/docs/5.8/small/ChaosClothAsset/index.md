# Chaos Cloth Asset

> Pattern based cloth asset using the Chaos Cloth simulation.

| 属性 | 值 |
|---|---|
| 中文名 | 基于样片的布料资产 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（布料资产、网格数据、预设） |
| 模块 | `ChaosClothAsset` (Runtime), `ChaosClothAssetEngine` (Runtime), `ChaosClothAssetTools` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset) | |

## 用途

**ChaosClothAsset** 插件在 **Chaos 布料模拟**系统之上，提供了一套**基于样片（Pattern-based）的布料资产化工作流**。它解决了传统布料模拟工作流复杂、与角色动画耦合困难的问题，允许开发者以更直观、模块化的方式设计、创建、编辑和优化布料资产，特别适用于虚拟服装、角色布料动画及需要精细控制的布料模拟场景。

## 使用场景

-   **虚拟服装设计**：为游戏角色或数字人创建和迭代基于真实样片结构的服装，进行动态模拟。
-   **角色布料动画**：在角色动画（如行走、跑动）中，为披风、裙子、头发等附加物添加逼真的物理动画。
-   **布料模拟优化**：通过基于资产的独立编辑与测试，调整布料参数（刚度、阻尼、碰撞等），并预览模拟效果，无需反复运行整个角色动画。
-   **程序化布料生成**：利用 Dataflow 节点或 C++ 接口，程序化地创建或修改布料资产。

## 模块概览

| 模块 | 类型 | 职责简介 |
|---|---|---|
| `ChaosClothAsset` | Runtime | **核心资产定义与数据模块**。定义布料资产 (`UChaosClothAsset`)、组件及用于构建资产的数据流节点。 |
| `ChaosClothAssetEngine` | Runtime | **引擎集成与运行时模块**。负责将布料资产转换为可运行的模拟代理，处理与动画系统、物理系统的集成。 |
| `ChaosClothAssetTools` | Runtime | **编辑器与工具链模块**。提供在编辑器中创建、编辑、预览布料资产的用户界面和工具，如资产编辑器和样片工具。 |

## 蓝图用法

（注：具体节点需结合模块文档 `ChaosClothAsset.md` 和 `ChaosClothAssetEngine.md` 查阅。此处基于核心资产模块 `ChaosClothAsset` 概述主要功能方向。）

### 核心功能节点

| 功能类别 | 说明 | 涉及类（推测） |
|---|---|---|
| 资产操作 | 创建、加载、保存、复制布料资产 | `UChaosClothAsset` |
| 组件交互 | 将布料资产附加到网格体组件，启动/停止模拟 | `UChaosClothComponent` (或类似组件) |
| 参数调整 | 在蓝图中动态读取或设置布料模拟参数（如重力、风速） | `UChaosClothSimulationConfig` |

### 使用示例（蓝图描述）
1.  **创建布料组件**：在角色蓝图中，添加一个“Chaos Cloth Component”（或从 `ChaosClothAsset` 模块派生的组件）。
2.  **赋值资产**：将编辑器中创建好的 `ChaosClothAsset` 资产拖拽到该组件的“Cloth Asset”属性上。
3.  **配置附加**：指定该布料应附加到角色的哪个骨骼（如“spine_02”）。
4.  **触发模拟**：在角色的 `Event BeginPlay` 中，调用组件上类似 `Start Simulation` 的函数，即可在游戏运行时看到布料随角色运动而模拟。

## C++ 用法

### 头文件引入
```cpp
// 核心资产模块
#include "ChaosClothAsset/ChaosClothAsset.h"
// 引擎集成模块
#include "ChaosClothAssetEngine/ChaosClothAssetEngine.h"
// 如需使用数据流节点
#include "ChaosClothAsset/ChaosClothAssetDataflowNodes.h"
```

### 基本用法
```cpp
// 加载一个已存在的布料资产（假设路径已知）
UChaosClothAsset* ClothAsset = LoadObject<UChaosClothAsset>(nullptr, TEXT("/Game/Path/To/MyClothAsset"));

// 假设有一个 SKinnedMeshComponent 指针 (CharacterMesh)
// 创建并附加一个布料组件（具体类名需查证，此处为示例）
UChaosClothComponent* ClothComp = NewObject<UChaosClothComponent>(CharacterMesh->GetOwner());
ClothComp->SetupAttachment(CharacterMesh);
ClothComp->SetClothAsset(ClothAsset);
ClothComp->SetAttachmentPoint(TEXT("spine_02")); // 设置附加骨骼
ClothComp->RegisterComponent();
```

### 进阶用法（程序化创建资产）
可通过代码驱动 `Dataflow` 图或直接操作资产对象来程序化生成布料资产。此部分需要参考 `ChaosClothAsset` 模块文档中关于 `UChaosClothAsset` 和相关 `Dataflow` 节点的详细说明。

## Demo 示例

一个最小化的 C++ 示例，展示如何创建一个布料组件并赋值资产。

**MyCharacter.h**
```cpp
#pragma once
#include "GameFramework/Character.h"
// 前置声明
class UChaosClothComponent;
class UChaosClothAsset;
#include "MyCharacter.generated.h"

UCLASS()
class AMyCharacter : public ACharacter
{
    GENERATED_BODY()
public:
    AMyCharacter();
    virtual void BeginPlay() override;
private:
    UPROPERTY(VisibleAnywhere)
    UChaosClothComponent* ClothComponent;
};
```

**MyCharacter.cpp**
```cpp
#include "MyCharacter.h"
#include "ChaosClothAsset/ChaosClothAssetComponent.h" // 头文件名需查证

AMyCharacter::AMyCharacter()
{
    // 假设 ChaosClothComponent 类名为 UChaosClothComponent
    ClothComponent = CreateDefaultSubobject<UChaosClothComponent>(TEXT("ChaosCloth"));
    ClothComponent->SetupAttachment(GetMesh());
}

void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();
    // 加载资产并设置（硬编码路径仅为示例）
    UChaosClothAsset* MyAsset = LoadObject<UChaosClothAsset>(nullptr, TEXT("/Game/ClothAssets/MyDress"));
    if (ClothComponent && MyAsset)
    {
        ClothComponent->SetClothAsset(MyAsset);
        ClothComponent->SetAttachmentPoint(TEXT("pelvis")); // 设置到骨盆
        ClothComponent->SetSimulatePhysics(true); // 通常在组件细节面板设置
    }
}
```

## 模块依赖

（注：以下依赖关系基于插件名称和 `Chaos`、`GeometryCache`、`Dataflow` 等插件依赖推断，具体以 `Build.cs` 文件为准。）

| 模块 | 用途 |
|---|---|
| `Chaos` | Chaos 物理框架核心 |
| `ChaosCloth` | Chaos 布料模拟器实现 |
| `GeometryCache` | 用于存储和回放预计算的几何数据（如模拟缓存） |
| `Dataflow` | 提供节点化、可视化的数据流编辑框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `89e20f15` | [ChaosClothAsset] Preserve the Cloth Component bSimulateInEditor and Asset properties across Bluepri | 修复蓝图中布料组件的模拟开关和资产属性在复制/粘贴时丢失的问题。 |
| 2026-05-26 | `8953a713` | [Cloth] Move parallel cloth simulation wait from EOF to TG_LastDemotable. | 优化并行布料模拟的线程等待时机，提升性能。 |
| 2026-05-25 | `1db5232a` | [ChaosCloth] Implement RefershBoneMapping for ClothAssetSKMClothingAsset. | 为特定类型的布料资产实现了骨骼映射刷新功能。 |
| 2026-05-22 | `e98c5896` | [Chaos Cloth Asset] Refresh the editor-only Asset alias after a duplicate or paste of an actor. | 修复在编辑器中复制/粘贴Actor后，布料资产别名不更新的问题。 |
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理布料资产转换器代码。 |

### 维护评价

-   **状态**: **活跃开发中**
-   **分析**:
    1.  **创建时间**: 创建于 2024 年 3 月，距今约 2 年，是较新的插件。
    2.  **版本**: 版本号为 `0.1`，且从首次提交信息可知，刚从 Experimental 文件夹移出并标记为 **Beta**。
    3.  **近期活跃度**: 在 **2026 年 5 月**内有多次密集提交，内容涉及功能增强（属性保持、骨骼映射刷新）、性能优化和 Bug 修复，表明该插件正处于积极的开发和迭代期。
    4.  **依赖关系**: 依赖于 Chaos、Dataflow 等核心系统，这些系统本身也在持续演进。
-   **推荐度**: **推荐关注与评估使用**。虽然是 Beta 版本，但功能完整且维护活跃，适用于对布料模拟有较高要求且愿意跟进 Beta 功能和潜在变更的项目。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset)
-   [官方文档]() (暂无)
-   [测试用例]() (路径未提供，通常位于 `Engine/Plugins/ChaosClothAsset/` 下的 `Tests` 或类似目录)