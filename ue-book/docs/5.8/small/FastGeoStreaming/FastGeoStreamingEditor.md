# Fast Geo Streaming

> A system that extracts and converts a partitioned world's geometry to optimize world streaming performance.

| 属性 | 值 |
|---|---|
| 中文名 | 快速几何流送 |
| 分类 | World Building |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（运行时代码） |
| 模块 | `FastGeoStreaming` (Runtime), `FastGeoStreamingEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-20 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FastGeoStreaming) | |

## 用途

该插件旨在优化大型开放世界中静态几何体的流送性能。其核心思想是将世界分区（World Partition）中不可变的静态几何体（StaticMeshes 和 InstanceStaticMeshes，包括带/不带碰撞的）从常规的UObject资产中“提取”出来，并转换为一种极其轻量级的非UObject数据结构。

在运行时，系统会异步地管理这些几何体数据的加载（Streaming-in）和卸载（Streaming-out），大部分计算工作不在游戏线程（GameThread）上执行。这使得它成为UE5标准关卡流送（Level Streaming）流程的一部分，并兼容数据层（Data Layers）和HLOD等世界分区功能。

**存在原因**：为了解决在超大规模世界中，频繁地创建和销毁大量StaticMesh组件及其关联UObject所带来的性能瓶颈（如内存、CPU开销和线程阻塞）。它将几何体数据与对象生命周期解耦，以实现更高效的流送。

## 使用场景

- **大型开放世界游戏开发**：当玩家在广袤的地图中移动时，需要快速加载和卸载地形、建筑物等静态场景元素，以维持流畅的帧率和内存使用。
- **复杂HLOD环境**：与HLOD系统结合，在极远距离提供优化的几何体表示。
- **需要快速流送性能的原型或技术验证**：用于测试和验证在海量静态几何体场景下的世界流送性能优化方案。

**注意**：该插件需要启用 `p.Chaos.EnableAsyncInitBody` 控制台变量才能正常工作。

## 蓝图用法

根据提供的源码分析，`FastGeoStreaming` 和 `FastGeoStreamingEditor` 模块中主要包含运行时核心逻辑和编辑器集成工具（如资产工厂、属性自定义），并未发现标记为 `BlueprintCallable` 或 `BlueprintReadWrite` 的公共蓝图API。其工作流程可能主要集成在引擎的关卡流送和世界分区管理管线内部。

## C++ 用法

该插件的使用涉及编辑器资产创建和运行时配置，但其核心流送逻辑对使用者通常是透明的。

### 头文件引入

若需与插件提供的编辑器类型交互（如创建设置资产），需包含相应头文件。
```cpp
#include "FastGeoTransformerSettings.h"
```

### 基本用法

主要的C++交互点在于创建和配置 `UFastGeoTransformerSettings` 资产，该资产控制几何体提取和转换的行为。
（来源：`FastGeoFactory.h` 及资产定义）

```cpp
// 创建 FastGeoTransformerSettings 资产的实例 (通常在编辑器扩展或工具代码中)
UFastGeoTransformerSettings* Settings = NewObject<UFastGeoTransformerSettings>(GetTransientPackage(), UFastGeoTransformerSettings::StaticClass());
// 根据需要配置 Settings 的属性...
```

### 进阶用法

该插件的核心高级功能（异步几何体提取、流送、渲染）由引擎在关卡流送时自动调用。开发者主要通过以下方式与之交互：
1.  **配置转换器设置**：通过编辑器中的 `UFastGeoTransformerSettings` 资产。
2.  **确保环境兼容性**：启用 `p.Chaos.EnableAsyncInitBody`。
3.  **与世界分区系统协作**：正常使用世界分区、数据层和HLOD功能，插件会在后台自动优化相关几何体的流送。

## Demo 示例

一个最小的示例，展示如何通过C++创建 `UFastGeoTransformerSettings` 资产。

**FastGeoDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "FastGeoDemo.generated.h"

class UFastGeoTransformerSettings;

UCLASS()
class AFastGeoDemoActor : public AActor
{
	GENERATED_BODY()

public:
	AFastGeoDemoActor();

	UPROPERTY(EditAnywhere, Category = "FastGeo Demo")
	TObjectPtr<UFastGeoTransformerSettings> TransformerSettings;

	virtual void BeginPlay() override;

private:
	void CreateDefaultSettingsIfNeeded();
};
```

**FastGeoDemo.cpp**
```cpp
#include "FastGeoDemo.h"
#include "FastGeoTransformerSettings.h" // 需要链接 FastGeoStreamingEditor 模块
#include "UObject/ConstructorHelpers.h"

AFastGeoDemoActor::AFastGeoDemoActor()
{
	PrimaryActorTick.bCanEverTick = false;
	// 在构造函数中尝试通过路径加载或直接创建设置资产
	TransformerSettings = nullptr;
}

void AFastGeoDemoActor::BeginPlay()
{
	Super::BeginPlay();
	CreateDefaultSettingsIfNeeded();
}

void AFastGeoDemoActor::CreateDefaultSettingsIfNeeded()
{
	if (!TransformerSettings)
	{
		// 在运行时创建临时设置对象（通常用于编辑器工具或动态配置）
		TransformerSettings = NewObject<UFastGeoTransformerSettings>(GetTransientPackage(), FName("DefaultFastGeoSettings"));
		UE_LOG(LogTemp, Log, TEXT("Created temporary FastGeo Transformer Settings."));
	}
}
```

**使用说明**：
1.  在编辑器中，`FastGeoStreamingEditor` 模块会注册 `UFastGeoFactory`，允许用户在内容浏览器中通过右键菜单 -> “杂项” -> “Fast Geo Transformer Settings” 来创建 `.FastGeoTransformerSettings` 资产文件。
2.  上述示例代码展示了如何在C++ Actor中引用或动态创建此类设置对象。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `FastGeoStreaming` | 核心运行时模块，提供几何体提取、转换和异步流送的实现。 |
| `FastGeoStreamingEditor` | 编辑器模块，提供 `UFastGeoTransformerSettings` 的工厂、资产定义和属性面板自定义。 |
| `UnrealEd` | `FastGeoStreaming` 模块的依赖，用于访问编辑器特定功能（可能用于世界分区单元转换器）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `d478e533` | [CodeClarity] CVar description and naming cleanup for FastGeo / SSAM / Async Physics | 清理FastGeo、SSAM、异步物理相关的控制台变量描述和命名。 |
| 2026-05-12 | `8b5eabf3` | FastGeo: Support GPU animated instanced skinned meshes. | 新增对GPU动画实例化蒙皮网格的支持。 |
| 2026-05-12 | `10c54c93` | [FastGeo] Harden surrogate component physics queries | 加强代理组件物理查询的稳健性。 |
| 2026-05-12 | `6fa3ba35` | [FastGeo] Fix world transform for unregistered components in runtime cell transformer | 修复运行时单元转换器中未注册组件的世界变换问题。 |
| 2026-05-12 | `8ce6709d` | [FastGeo] Resolve WalkableSlopeOverride from BodySetup when building surrogate descriptor | 在构建代理描述符时，从BodySetup中解析WalkableSlopeOverride。 |

### 维护评价

该插件创建于2025年3月，**非常年轻**，目前处于**活跃维护**状态。从最近的提交记录（2026年5月）可以看出，它仍在持续获得新功能（如支持GPU动画实例）和关键的错误修复（如物理查询、变换问题）。

**注意**：由于该插件标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，它仍处于实验阶段，API和功能可能会发生破坏性更改，不建议在需要长期稳定性的生产项目中直接使用。它更适合于技术预研、性能测试或作为内部工具链的一部分。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FastGeoStreaming)
- [官方文档]（无）
- [测试用例]（无公开测试用例路径）