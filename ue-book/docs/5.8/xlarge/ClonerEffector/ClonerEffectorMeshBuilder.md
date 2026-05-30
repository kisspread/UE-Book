# Cloners and Effectors

> Niagara based cloner system with various layouts and effector affecting each clone instances

| 属性 | 值 |
|---|---|
| 中文名 | 克隆器与效果器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（模板资产、示例场景） |
| 模块 | `ClonerEffector` (Runtime), `ClonerEffectorEditor` (Runtime), `ClonerEffectorMeshBuilder` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ClonerEffector) | |

## 用途

该插件基于 Niagara 粒子系统构建，提供了一个强大的“克隆器”（Cloner）和“效果器”（Effector）框架，用于虚拟制片中的动态视觉效果。它解决了在场景中高效创建和管理大量重复实例，并对这些实例进行复杂、动态的属性控制（如位置、旋转、缩放、颜色、材质等）的需求。与手动摆放或简单的实例化静态网格相比，它允许通过“布局”规则程序化生成克隆体，并使用“效果器”基于各种输入（如时间、音频、空间位置、其他Actor）来实时影响每一个克隆实例，从而实现电影级的动态视觉效果。

## 使用场景

-   **虚拟制片中的动态背景**：需要创建随音乐节奏变化的粒子群、观众席或建筑立面效果时，使用克隆器布局生成基础实例，用音频效果器驱动。
-   **产品展示与广告**：需要创建围绕产品旋转或以特定图案飞散的大量物体时，用克隆器布局并配合旋转/环绕效果器。
-   **交互式艺术装置**：玩家移动或触发事件时，周围环境（如粒子、灯光、模型）产生连锁反应，通过玩家位置效果器触发。
-   **复杂动画**：模拟群体运动（如鸟群、鱼群）、粒子流或几何形变，而无需手动设置关键帧。
-   **动态场景装饰**：在演出中实时控制场景内数千个元素的动画，如灯光、道具、屏幕墙。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Cloner` | 创建并返回一个新的克隆器组件。 | `UClonerComponent` |
| `Create Effector` | 创建并返回一个新的效果器组件。 | `UEffectorComponent` |
| `Set Cloner Layout` | 为克隆器设置一个布局资产（如网格、环形、网格等），决定克隆体的初始排列。 | `UClonerComponent` |
| `Set Effector Domain` | 为效果器设置影响域（如从中心向外衰减、沿某个轴衰减），控制效果的空间影响范围。 | `UEffectorComponent` |
| `Set Effector Field` | 为效果器设置一个具体的属性影响字段（如缩放、旋转、颜色），并配置响应曲线和强度。 | `UEffectorComponent` |

### 使用示例（蓝图描述）

1.  **创建基础克隆**：
    *   在 Actor 的蓝图中，添加一个 `ClonerComponent`。
    *   调用 `Set Cloner Layout` 节点，选择一个布局资产（如 `Grid` 或 `Radial`），这将决定克隆体在场景中的初始排列方式。
    *   克隆器会自动使用该 Actor 的静态网格组件作为原型进行复制。

2.  **添加动态效果**：
    *   在同一 Actor 或另一个 Actor 上，添加一个 `EffectorComponent`。
    *   调用 `Set Effector Domain` 节点，设置效果的空间范围，例如 `Sphere Domain`，并设置半径。
    *   调用 `Set Effector Field` 节点，添加一个 `Scale Field`，并为其指定一条响应曲线，使得靠近效果器中心的克隆体缩放更大。
    *   将该效果器组件的引用设置到克隆器组件的 `Effectors` 数组属性中。克隆器会自动将效果器的影响应用到其所有克隆实例上。

## C++ 用法

### 头文件引入

```cpp
#include "ClonerEffector.h"
```

### 基本用法

从测试用例中可以看到，`FClonerUtilities` 是一个核心工具类，用于查询和操作克隆系统。
（来源：`Engine/Plugins/VirtualProduction/ClonerEffector/Source/ClonerEffector/Private/Tests/ClonerEffectorTest.cpp`）

```cpp
// 检查克隆系统是否可用
if (FClonerUtilities::IsAvailable())
{
    // 获取场景中所有克隆组件的列表
    TArray<UClonerComponent*> ClonerComponents;
    FClonerUtilities::GetAllCloners(GetWorld(), ClonerComponents);

    for (UClonerComponent* Cloner : ClonerComponents)
    {
        // 获取当前克隆体的数量
        int32 InstanceCount = Cloner->GetInstanceCount();
        UE_LOG(LogTemp, Log, TEXT("Cloner has %d instances."), InstanceCount);
    }
}
```

### 进阶用法

结合创建和查询，程序化控制克隆器和效果器。
（综合自多个测试用例逻辑）

```cpp
// 创建一个克隆器组件并附加到Actor上
UClonerComponent* NewCloner = NewObject<UClonerComponent>(MyActor);
NewCloner->RegisterComponent();
NewCloner->AttachToComponent(MyActor->GetRootComponent(), FAttachmentTransformRules::KeepRelativeTransform);

// 加载并设置布局
UClonerLayout* GridLayout = LoadObject<UClonerLayout>(nullptr, TEXT("/ClonerEffector/Layouts/DefaultGrid"));
NewCloner->SetLayout(GridLayout);

// 创建一个效果器组件
UEffectorComponent* AudioEffector = NewObject<UEffectorComponent>(MyActor);
AudioEffector->RegisterComponent();
AudioEffector->AttachToComponent(MyActor->GetRootComponent(), FAttachmentTransformRules::KeepRelativeTransform);

// 配置效果器域和字段（伪代码，具体类名需查阅头文件）
// AudioEffector->SetDomain(...);
// AudioEffector->AddField(ECEFieldAttribute::Scale, ...);

// 将效果器关联到克隆器
NewCloner->Effectors.Add(AudioEffector);
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何在运行时动态创建并配置克隆器和效果器。

**ClonerEffectorDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ClonerEffectorDemo.generated.h"

class UClonerComponent;
class UEffectorComponent;
class UClonerLayout;

UCLASS()
class AClonerEffectorDemo : public AActor
{
	GENERATED_BODY()

public:
	AClonerEffectorDemo();

protected:
	virtual void BeginPlay() override;

private:
	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UStaticMeshComponent> MeshComp;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UClonerComponent> ClonerComp;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UEffectorComponent> EffectorComp;
};
```

**ClonerEffectorDemo.cpp**
```cpp
#include "ClonerEffectorDemo.h"
#include "ClonerComponent.h"
#include "EffectorComponent.h"

AClonerEffectorDemo::AClonerEffectorDemo()
{
	// 创建根网格组件
	MeshComp = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
	RootComponent = MeshComp;

	// 创建克隆器组件
	ClonerComp = CreateDefaultSubobject<UClonerComponent>(TEXT("Cloner"));

	// 创建效果器组件
	EffectorComp = CreateDefaultSubobject<UEffectorComponent>(TEXT("Effector"));
}

void AClonerEffectorDemo::BeginPlay()
{
	Super::BeginPlay();

	// 在运行时设置布局资产（路径需根据项目实际资产调整）
	if (UClonerLayout* Layout = LoadObject<UClonerLayout>(this, TEXT("/Game/Meshes/MyGridLayout")))
	{
		ClonerComp->SetLayout(Layout);
	}

	// 将效果器添加到克隆器的影响器列表
	ClonerComp->Effectors.Add(EffectorComp);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Niagara` | 核心依赖，克隆器系统基于 Niagara 粒子系统实现 |
| `GeometryCore` | `ClonerEffectorMeshBuilder` 模块依赖，用于动态网格操作和构建 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量被截断为浮点数导致的警告代码。 |
| 2026-05-12 | `6a7d961a` | Motion Design: fix cloner MIDs getting gc‘d on save, causing the mesh renderer to have an array of d | 修复克隆器MID在保存时被垃圾回收，导致网格渲染器材质数组损坏的问题。 |
| 2026-05-12 | `9d568373` | Motion Design: fixed warning logs when cloner asset isn‘t generated yet and failing to find a data i | 修复当克隆器资产未生成且找不到数据接口时产生的警告日志。 |
| 2026-05-12 | `adfb4114` | Motion Design: fixed cloners spawning default actors while in async loading thread. Instead, these a | 修复克隆器在异步加载线程中生成默认Actor的问题，改为延迟生成。 |
| 2026-05-12 | `ae187efa` | Motion Design: fixed motion design scene tree returning potentially null actors. Also added null che | 修复Motion Design场景树可能返回空Actor的问题，并添加了空指针检查。 |

### 维护评价

**活跃维护**。该插件虽然创建时间不长（约1年），但近期（2026年5月）有多次密集的提交，内容集中在**Bug修复**和**稳定性提升**上，例如修复内存管理、异步加载、日志警告等问题。这表明插件正处于活跃的迭代和维护阶段，开发者正在积极处理已知问题。考虑到它属于 Virtual Production 工具链的一部分，预计会持续获得支持。可以放心在项目中使用，但建议关注后续版本更新以获取最新的稳定性改进。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ClonerEffector)
- [官方文档]( )（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ClonerEffector/Source/ClonerEffector/Private/Tests)